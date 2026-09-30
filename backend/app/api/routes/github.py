from typing import List
from fastapi import APIRouter, HTTPException, Path, status

from app.schemas.github import GitHubProfileResponse
from app.schemas.github_repository import GitHubRepositoryResponse
from app.schemas.technology import TechnologyExtractionResponse
from app.services.github_service import (
    GitHubAPIError,
    GitHubUserNotFoundError,
    github_service,
)
from app.services.technology_service import technology_service

router = APIRouter(prefix="/github", tags=["GitHub"])


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
