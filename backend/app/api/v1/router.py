from fastapi import APIRouter

from app.api.routes.career_recommendation import (
    router as career_recommendation_router,
)
from app.api.routes.resume import router as resume_router
from app.api.routes.skill_gap import router as skill_gap_router
from app.api.routes.system import router as system_router

api_router = APIRouter()

# Include sub-routers under API v1
api_router.include_router(system_router)
api_router.include_router(skill_gap_router, prefix="/skill-gap")
api_router.include_router(
    career_recommendation_router, prefix="/career-recommendations"
)
api_router.include_router(resume_router, prefix="/resume")
