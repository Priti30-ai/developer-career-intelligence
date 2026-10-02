from typing import Optional

from fastapi import APIRouter, File, HTTPException, Request, UploadFile, status
from fastapi.encoders import jsonable_encoder
from pydantic import ValidationError

from app.schemas.resume import (
    ResumeAnalysisRequest,
    ResumeAnalysisResponse,
)
from app.services.document_extraction_service import (
    DocumentExtractionError,
    MAX_FILE_SIZE_BYTES,
    document_extraction_service,
)
from app.services.resume_service import resume_service

router = APIRouter(tags=["Resume Analysis"])


@router.post(
    "/analyze",
    response_model=ResumeAnalysisResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyze Resume Document or Text",
    description=(
        "Extract text from an uploaded resume document (PDF, DOCX, TXT) "
        "and parse it into structured sections, normalized skills, education, "
        "experience, and projects. Also accepts JSON payload with resume_text for backward compatibility."
    ),
)
async def analyze_resume(
    request: Request,
    file: Optional[UploadFile] = File(
        None,
        description="Uploaded resume document file (PDF, DOCX, or TXT, max 5 MB)",
    ),
) -> ResumeAnalysisResponse:
    """
    Primary workflow:
    Accepts multipart/form-data containing an uploaded resume file (PDF, DOCX, TXT).
    Validates file format and size, extracts text using DocumentExtractionService,
    and forwards extracted text to the deterministic resume parser.

    Backward compatibility:
    Accepts application/json containing {"resume_text": "..."}.
    """
    content_type = request.headers.get("content-type", "")

    # 1. Backward-compatible JSON path
    if "application/json" in content_type:
        try:
            body = await request.json()
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid JSON payload.",
            ) from exc

        try:
            analysis_request = ResumeAnalysisRequest.model_validate(body)
            resume_text = analysis_request.resume_text
        except ValidationError as val_err:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=jsonable_encoder(val_err.errors()),
            ) from val_err

    # 2. File upload path (multipart/form-data)
    else:
        target_file = file
        if target_file is None:
            # Fallback inspection of form data for files uploaded with alternative field names
            try:
                form = await request.form()
                for key in ("file", "resume", "document", "upload"):
                    candidate = form.get(key)
                    if isinstance(candidate, UploadFile):
                        target_file = candidate
                        break
            except Exception:
                target_file = None

        if target_file is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No resume file was uploaded. Please upload a PDF, DOCX, or TXT file.",
            )

        # Validate metadata (extension & MIME type)
        try:
            document_extraction_service.validate_file_metadata(
                filename=target_file.filename,
                content_type=target_file.content_type,
            )
        except DocumentExtractionError as err:
            raise HTTPException(
                status_code=err.status_code,
                detail=err.message,
            ) from err

        # Read file contents safely with max size boundary
        try:
            contents = await target_file.read(MAX_FILE_SIZE_BYTES + 1)
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to read uploaded file contents.",
            ) from exc

        if len(contents) > MAX_FILE_SIZE_BYTES:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="File size exceeds the 5 MB limit. Please upload a smaller resume document.",
            )

        if len(contents) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded file is empty. Please upload a valid resume document.",
            )

        # Extract text via DocumentExtractionService
        try:
            resume_text = document_extraction_service.extract_text(
                file_bytes=contents,
                filename=target_file.filename,
                content_type=target_file.content_type,
            )
        except DocumentExtractionError as err:
            raise HTTPException(
                status_code=err.status_code,
                detail=err.message,
            ) from err

    # 3. Validate extracted text content
    trimmed = resume_text.strip()
    if not trimmed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Extracted resume text is empty or contains only whitespace.",
        )

    if len(trimmed) > 50_000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Extracted resume text exceeds the maximum allowed limit of 50,000 characters.",
        )

    # 4. Parse deterministically using existing resume_service
    analysis_result = resume_service.analyze_resume(trimmed)
    return ResumeAnalysisResponse(**analysis_result)
