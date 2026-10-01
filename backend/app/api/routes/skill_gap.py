from typing import List
from fastapi import APIRouter, HTTPException, Path, status

from app.schemas.skill_gap import (
    CareerRoleDetailResponse,
    CareerRoleSummaryResponse,
    SkillGapRequest,
    SkillGapResponse,
)
from app.services.career_role_service import (
    CareerRoleNotFoundError,
    career_role_service,
)
from app.services.github_service import (
    GitHubAPIError,
    GitHubUserNotFoundError,
    github_service,
)
from app.services.skill_gap_service import skill_gap_service
from app.services.technology_service import technology_service

router = APIRouter(tags=["Skill Gap"])


@router.get(
    "/roles",
    response_model=List[CareerRoleSummaryResponse],
    summary="List Supported Career Roles",
    description="Retrieve all predefined career roles and their required skill counts.",
)
def list_career_roles() -> List[CareerRoleSummaryResponse]:
    """Return summary list of available career roles."""
    roles = career_role_service.list_roles()
    return [CareerRoleSummaryResponse(**r) for r in roles]


@router.get(
    "/roles/{role_slug}",
    response_model=CareerRoleDetailResponse,
    summary="Get Career Role Details",
    description="Retrieve role information and complete required skill set for a specific role slug.",
)
def get_career_role_details(
    role_slug: str = Path(..., description="The role slug to retrieve, e.g., 'data-scientist'"),
) -> CareerRoleDetailResponse:
    """Return detailed information and required skills for a single role."""
    role = career_role_service.get_role(role_slug)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Career role '{role_slug}' not found.",
        )
    return CareerRoleDetailResponse(**role)


@router.post(
    "/analyze",
    response_model=SkillGapResponse,
    summary="Analyze Skill Gap from Provided Skills",
    description="Compare a provided list of current developer skills against the requirements of a target role.",
)
def analyze_skill_gap(request: SkillGapRequest) -> SkillGapResponse:
    """
    Compare developer's current skills against target role requirements.

    Args:
        request: SkillGapRequest with target_role and current_skills list.

    Returns:
        SkillGapResponse: Matched, missing skills, and match percentage.
    """
    try:
        result = skill_gap_service.analyze_gap(
            target_role=request.target_role,
            current_skills=request.current_skills,
        )
        return SkillGapResponse(**result)
    except CareerRoleNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )


@router.get(
    "/github/{username}/{role_slug}",
    response_model=SkillGapResponse,
    summary="Analyze GitHub User Skill Gap for Target Role",
    description="Analyze a GitHub user's public repositories, extract skills, and evaluate the gap for a target career role.",
)
async def analyze_github_user_skill_gap(
    username: str = Path(..., description="GitHub username to evaluate"),
    role_slug: str = Path(..., description="Target career role slug, e.g. 'data-scientist'"),
) -> SkillGapResponse:
    """
    End-to-end skill gap analysis from GitHub profile to career role comparison.

    Pipeline:
        GitHubService (repos) → TechnologyService (extraction) → SkillGapService (comparison)
    """
    try:
        repos = await github_service.get_user_repositories(username=username)
        extracted = technology_service.extract_technologies(repositories=repos)
        current_skills = [t["name"] for t in extracted["technologies"]]
        result = skill_gap_service.analyze_gap(
            target_role=role_slug,
            current_skills=current_skills,
        )
        return SkillGapResponse(**result)
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
            detail="An unexpected error occurred while analyzing the skill gap.",
        )
