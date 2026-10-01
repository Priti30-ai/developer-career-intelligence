"""
repository_architecture.py
--------------------------
FastAPI route for GitHub Repository Architecture Analysis.

Endpoint:
    POST /api/v1/repository-architecture/analyze
"""

from fastapi import APIRouter, HTTPException, status

from app.schemas.repository_architecture import (
    RepositoryArchitectureRequest,
    RepositoryArchitectureResponse,
)
from app.services.github_service import (
    GitHubAPIError,
    GitHubRepositoryNotFoundError,
)
from app.services.repository_architecture_service import (
    repository_architecture_service,
)

router = APIRouter(tags=["Repository Architecture"])


@router.post(
    "/analyze",
    response_model=RepositoryArchitectureResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyze Repository Architecture",
    description=(
        "Analyze the file and directory tree structure of a public GitHub repository. "
        "Produces explainable architecture signals, detected dependency manifests, "
        "and deterministic project classification (e.g. FULL_STACK, FRONTEND, BACKEND)."
    ),
)
async def analyze_repository_architecture(
    request: RepositoryArchitectureRequest,
) -> RepositoryArchitectureResponse:
    """
    Accepts:
    - owner: Repository owner / organization.
    - repo: Repository name.
    - branch: Optional branch or commit SHA (defaults to default branch).

    Returns:
    - RepositoryArchitectureResponse containing repository info, project type,
      languages detected, manifests, architecture signals, and summary metrics.
    """
    try:
        result = await repository_architecture_service.analyze_repository(
            owner=request.owner,
            repo=request.repo,
            branch=request.branch,
        )
        return RepositoryArchitectureResponse(**result)
    except GitHubRepositoryNotFoundError as exc:
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
            detail="An unexpected error occurred during repository architecture analysis.",
        )
