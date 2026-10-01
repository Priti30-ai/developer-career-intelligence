from fastapi import APIRouter, status

from app.schemas.resume import (
    ResumeAnalysisRequest,
    ResumeAnalysisResponse,
)
from app.services.resume_service import resume_service

router = APIRouter(tags=["Resume Analysis"])


@router.post(
    "/analyze",
    response_model=ResumeAnalysisResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyze Plain-Text Resume",
    description="Parse raw plain-text resume into structured sections, normalized skills, education, experience, and projects.",
)
def analyze_resume(request: ResumeAnalysisRequest) -> ResumeAnalysisResponse:
    """
    Accepts raw resume text, parses sections deterministically, extracts
    and normalizes skills, and returns structured candidate profile data.
    """
    analysis_result = resume_service.analyze_resume(request.resume_text)
    return ResumeAnalysisResponse(**analysis_result)
