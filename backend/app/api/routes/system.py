from fastapi import APIRouter

from app.schemas.system import HealthResponse

router = APIRouter(tags=["System"])


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    """Health check endpoint to verify backend service status."""
    return HealthResponse(status="healthy")
