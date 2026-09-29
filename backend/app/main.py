from fastapi import FastAPI

from app.api.routes.system import router as system_router
from app.core.config import settings

# Initialize FastAPI application using configuration settings
app = FastAPI(
    title=settings.app_name,
    version=settings.version,
)

# Include application routers
app.include_router(system_router)


@app.get("/")
def read_root():
    """Root endpoint welcoming API clients."""
    return {"message": "Developer Career Intelligence System API"}
