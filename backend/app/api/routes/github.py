from typing import List
from fastapi import APIRouter, HTTPException, Path, Query, status

from app.schemas.github import GitHubProfileResponse
from app.schemas.github_account import GitHubAccountAnalysisResponse
from app.schemas.github_repository import GitHubRepositoryResponse
from app.schemas.skill_profile import SkillProfileResponse
from app.schemas.technology import TechnologyExtractionResponse
from app.services.github_account_service import github_account_service
from app.services.github_service import (
    GitHubAPIError,
    GitHubUserNotFoundError,
    InvalidGitHubUsernameError,
    github_service,
)
from app.services.skill_profile_service import skill_profile_service
from app.services.technology_service import technology_service

router = APIRouter(prefix="/github", tags=["GitHub"])


@router.get(
    "/analysis",
    response_model=GitHubAccountAnalysisResponse,
    summary="Analyze GitHub Account (Query Param)",
    description=(
        "Analyze a public GitHub account including repository inspection, "
        "evidence-backed technologies and skills, and cross-repository account intelligence. "
        "Accepts username or profile URL via query parameter."
    ),
    include_in_schema=False,
)
async def analyze_github_account_query(
    username: str = Query(
        ...,
        description="The GitHub username or public profile URL to analyze",
    ),
    max_pages: int = Query(
        10,
        ge=1,
        le=50,
        description="Maximum repository pages to discover and inspect",
    ),
) -> GitHubAccountAnalysisResponse:
    """Query parameter variant for GitHub account analysis."""
    return await analyze_github_account(username_or_url=username, max_pages=max_pages)


@router.get(
    "/{username_or_url:path}/analysis",
    response_model=GitHubAccountAnalysisResponse,
    summary="Analyze GitHub Account",
    description=(
        "Analyze a public GitHub account including repository inspection, "
        "evidence-backed technologies and skills, and cross-repository account intelligence."
    ),
)
async def analyze_github_account(
    username_or_url: str = Path(
        ...,
        description="The GitHub username or public profile URL to analyze",
    ),
    max_pages: int = Query(
        10,
        ge=1,
        le=50,
        description="Maximum repository pages to discover and inspect",
    ),
) -> GitHubAccountAnalysisResponse:
    """
    Execute full GitHub account intelligence pipeline (Tasks 3–6):
    1. Normalize username or profile URL input
    2. Discover public profile and repository catalog
    3. Deeply inspect repository architecture and manifests
    4. Extract factual technologies, skills, and evidence signals
    5. Aggregate cross-repository intelligence into an account-level profile

    Args:
        username_or_url: GitHub username, @username, or profile URL.
        max_pages: Maximum repository pages to fetch (default 10).

    Returns:
        GitHubAccountAnalysisResponse: Account metadata, discovered repositories,
        and cross-repository aggregated technical profile.
    """
    try:
        return await github_account_service.aggregate_account(
            username_or_url=username_or_url, max_pages=max_pages
        )
    except (InvalidGitHubUsernameError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        )
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
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while analyzing the GitHub account.",
        )


@router.get(
    "/{username}",
    response_model=GitHubProfileResponse,
    summary="Get GitHub User Profile",
    description="Fetch public profile details for a specified GitHub username.",
)
async def get_github_profile(
    username: str = Path(..., description="The GitHub username to query")
) -> GitHubProfileResponse:
    """
    Retrieve basic public GitHub profile information.

    Args:
        username: GitHub username provided as a path parameter.

    Returns:
        GitHubProfileResponse: Validated structured profile information.
    """
    try:
        profile_data = await github_service.get_user_profile(username=username)
        return GitHubProfileResponse(**profile_data)
    except (InvalidGitHubUsernameError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        )
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
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while processing the request.",
        )


@router.get(
    "/{username}/repos",
    response_model=List[GitHubRepositoryResponse],
    summary="Get GitHub User Repositories",
    description="Fetch public repositories for a specified GitHub username.",
)
async def get_github_repositories(
    username: str = Path(..., description="The GitHub username to query")
) -> List[GitHubRepositoryResponse]:
    """
    Retrieve public repositories for the specified GitHub user.

    Args:
        username: GitHub username provided as a path parameter.

    Returns:
        List[GitHubRepositoryResponse]: Validated list of user repositories.
    """
    try:
        repos_data = await github_service.get_user_repositories(username=username)
        return [GitHubRepositoryResponse(**repo) for repo in repos_data]
    except (InvalidGitHubUsernameError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        )
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
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while processing the request.",
        )


@router.get(
    "/{username}/technologies",
    response_model=TechnologyExtractionResponse,
    summary="Extract Technologies from User Repositories",
    description="Analyze public repositories of a GitHub user to extract normalized technology signals and repository counts.",
)
async def get_github_technologies(
    username: str = Path(..., description="The GitHub username to query")
) -> TechnologyExtractionResponse:
    """
    Extract normalized technologies from the user's public repositories.

    Args:
        username: GitHub username provided as a path parameter.

    Returns:
        TechnologyExtractionResponse: Extracted technologies and repository counts.
    """
    try:
        repos_data = await github_service.get_user_repositories(username=username)
        extraction_data = technology_service.extract_technologies(repositories=repos_data)
        return TechnologyExtractionResponse(**extraction_data)
    except (InvalidGitHubUsernameError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        )
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
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while processing the request.",
        )


@router.get(
    "/{username}/skills",
    response_model=SkillProfileResponse,
    summary="Get Developer Skill Profile",
    description=(
        "Analyze public repositories of a GitHub user and return a structured "
        "developer skill profile with technologies grouped into skill categories."
    ),
)
async def get_github_skills(
    username: str = Path(..., description="The GitHub username to query")
) -> SkillProfileResponse:
    """
    Build a categorized developer skill profile from GitHub repository data.

    The pipeline is:
        GitHubService → TechnologyService → SkillProfileService

    Args:
        username: GitHub username provided as a path parameter.

    Returns:
        SkillProfileResponse: Skill categories with repository counts.
    """
    try:
        repos_data = await github_service.get_user_repositories(username=username)
        extraction_data = technology_service.extract_technologies(repositories=repos_data)
        skill_data = skill_profile_service.build_skill_profile(
            technologies=extraction_data["technologies"],
            total_repositories=extraction_data["total_repositories"],
        )
        return SkillProfileResponse(**skill_data)
    except (InvalidGitHubUsernameError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        )
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
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while processing the request.",
        )
