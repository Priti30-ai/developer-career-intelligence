from fastapi import APIRouter, HTTPException, Path, status

from app.schemas.github import GitHubProfileResponse
from app.services.github_service import (
    GitHubAPIError,
    GitHubUserNotFoundError,
    github_service,
)

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
