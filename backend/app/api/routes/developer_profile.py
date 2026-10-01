"""
developer_profile.py
--------------------
FastAPI route for Unified Developer Profile Synthesis.

Endpoint:
    POST /api/v1/developer-profile/analyze
"""

from fastapi import APIRouter, HTTPException, status

from app.schemas.developer_profile import (
    DeveloperProfileRequest,
    DeveloperProfileResponse,
)
from app.services.developer_profile_service import developer_profile_service
from app.services.github_service import (
    GitHubAPIError,
    GitHubUserNotFoundError,
)

router = APIRouter(tags=["Developer Profile"])


@router.post(
    "/analyze",
    response_model=DeveloperProfileResponse,
    status_code=status.HTTP_200_OK,
    summary="Synthesize Unified Developer Profile",
    description=(
        "Synthesize a canonical, unified developer profile combining GitHub repository "
        "evidence, normalized technologies, and resume profile details. Accurately tracks "
        "skill sources ('github', 'resume') and verified evidence levels."
    ),
)
async def analyze_developer_profile(
    request: DeveloperProfileRequest,
) -> DeveloperProfileResponse:
    """
    Synthesize and return a Unified Developer Profile.

    Accepts:
    - github_username: Target public GitHub username.
    - resume_text: Optional plain-text resume content.
    - resume_skills: Optional pre-extracted resume skills list.

    Returns:
    - DeveloperProfileResponse containing github summary, resume summary,
      unified skills with sources and evidence, and aggregate statistics.
    """
    try:
        result = await developer_profile_service.synthesize_profile(
            username=request.github_username,
            resume_text=request.resume_text,
            resume_skills=request.resume_skills,
        )
        return DeveloperProfileResponse(**result)
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
            detail="An unexpected error occurred during developer profile synthesis.",
        )
