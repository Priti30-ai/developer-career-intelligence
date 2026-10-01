from fastapi import APIRouter, HTTPException, status

from app.schemas.job_matching import (
    JobMatchingRequest,
    JobMatchingResponse,
)
from app.services.job_matching_service import job_matching_service

router = APIRouter(tags=["Job Matching"])


@router.post(
    "/analyze",
    response_model=JobMatchingResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyze and Match Job Description against Developer Skills",
    description=(
        "Extract canonical technical skills from a job description, compare against developer skills, "
        "and calculate deterministic match coverage and gap breakdown."
    ),
)
def analyze_job_matching(request: JobMatchingRequest) -> JobMatchingResponse:
    """
    Accepts raw job description text and developer skills, extracts required skills deterministically,
    and returns matched skills, missing skills, and match percentage.
    """
    try:
        result = job_matching_service.match_job_description(
            job_description=request.job_description,
            developer_skills=request.developer_skills,
        )
        return JobMatchingResponse(**result)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during job description matching.",
        )
