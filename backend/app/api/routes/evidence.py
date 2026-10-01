from fastapi import APIRouter, HTTPException, status

from app.schemas.evidence import (
    EvidenceAnalysisRequest,
    EvidenceAnalysisResponse,
)
from app.services.evidence_service import evidence_service
from app.services.github_service import (
    GitHubAPIError,
    GitHubUserNotFoundError,
)

router = APIRouter(tags=["Evidence Analysis"])


@router.post(
    "/analyze",
    response_model=EvidenceAnalysisResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyze Resume Skills vs GitHub Evidence",
    description="Compare claimed resume skills against evidence detected across public GitHub repositories.",
)
async def analyze_evidence(request: EvidenceAnalysisRequest) -> EvidenceAnalysisResponse:
    """
    Accepts a GitHub username and resume skills (or raw resume text).
    Fetches the user's public repositories, extracts repository-level skills,
    and returns a deterministic evidence classification with supporting repositories.
    """
    try:
        result = await evidence_service.analyze_evidence(
            username=request.github_username,
            resume_skills=request.resume_skills,
            resume_text=request.resume_text,
        )
        return EvidenceAnalysisResponse(**result)
    except GitHubUserNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )
    except GitHubAPIError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=str(exc),
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during evidence analysis.",
        )
