from fastapi import FastAPI

from app.api.routes.github import router as github_router
from app.api.v1.router import api_router
from app.core.config import settings

# Initialize FastAPI application using configuration settings
app = FastAPI(
    title=settings.app_name,
    version=settings.version,
)

# Include versioned API router under /api/v1
app.include_router(api_router, prefix="/api/v1")

# Include GitHub API router under /api
app.include_router(github_router, prefix="/api")


@app.get("/")
def read_root():
    """Root endpoint welcoming API clients."""
    return {"message": "Developer Career Intelligence System API"}
