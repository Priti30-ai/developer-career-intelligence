from typing import List
from fastapi import APIRouter, HTTPException, Path, status

from app.schemas.career_recommendation import (
    CareerRecommendationRequest,
    CareerRecommendationResponse,
)
from app.schemas.skill_gap import CareerRoleSummaryResponse
from app.services.career_recommendation_service import career_recommendation_service
from app.services.career_role_service import (
    CareerRoleNotFoundError,
    career_role_service,
)
from app.services.github_service import (
    GitHubAPIError,
    GitHubUserNotFoundError,
    github_service,
)
from app.services.technology_service import technology_service

router = APIRouter(tags=["Career Recommendations"])


@router.get(
    "/roles",
    response_model=List[CareerRoleSummaryResponse],
    summary="List Roles Available for Career Recommendations",
    description="Retrieve all supported career roles for which learning recommendations and roadmaps can be generated.",
)
def list_recommendation_roles() -> List[CareerRoleSummaryResponse]:
    """Return summary list of available career roles."""
    roles = career_role_service.list_roles()
    return [CareerRoleSummaryResponse(**r) for r in roles]


@router.post(
    "/analyze",
    response_model=CareerRecommendationResponse,
    summary="Generate Career Learning Recommendations and Roadmap",
    description="Analyze developer skill gaps against a target role and generate a prioritized learning roadmap.",
)
def generate_career_recommendations(
    request: CareerRecommendationRequest,
) -> CareerRecommendationResponse:
    """
    Generate prioritized skill recommendations and ordered roadmap stages.

    Args:
        request: CareerRecommendationRequest with target_role and current_skills list.

    Returns:
        CareerRecommendationResponse: Structured recommendations, priorities, projects, and roadmap.
    """
    try:
        result = career_recommendation_service.generate_recommendations(
            target_role=request.target_role,
            current_skills=request.current_skills,
        )
        return CareerRecommendationResponse(**result)
    except CareerRoleNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )


@router.get(
    "/github/{username}/{role_slug}",
    response_model=CareerRecommendationResponse,
    summary="Generate Career Recommendations from GitHub Profile",
    description="Extract skills from a user's GitHub repositories and generate personalized learning recommendations.",
)
async def generate_github_career_recommendations(
    username: str = Path(..., description="GitHub username to evaluate"),
    role_slug: str = Path(..., description="Target career role slug, e.g. 'data-scientist'"),
) -> CareerRecommendationResponse:
    """
    End-to-end career recommendation pipeline from public GitHub profile.

    Pipeline:
        GitHubService → TechnologyService → SkillGapService → CareerRecommendationService
    """
    try:
        repos = await github_service.get_user_repositories(username=username)
        extracted = technology_service.extract_technologies(repositories=repos)
        current_skills = [t["name"] for t in extracted["technologies"]]
        result = career_recommendation_service.generate_recommendations(
            target_role=role_slug,
            current_skills=current_skills,
        )
        return CareerRecommendationResponse(**result)
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
    except CareerRoleNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while generating career recommendations.",
        )
