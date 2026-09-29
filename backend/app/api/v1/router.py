from fastapi import APIRouter

from app.api.routes.system import router as system_router

api_router = APIRouter()

# Include sub-routers under API v1
api_router.include_router(system_router)
