from fastapi import APIRouter

from app.api.routes.career_recommendation import (
    router as career_recommendation_router,
)
from app.api.routes.developer_profile import (
    router as developer_profile_router,
)
from app.api.routes.evidence import router as evidence_router
from app.api.routes.github import router as github_router
from app.api.routes.job_matching import router as job_matching_router
from app.api.routes.repository_architecture import (
    router as repository_architecture_router,
)
from app.api.routes.resume import router as resume_router
from app.api.routes.skill_gap import router as skill_gap_router
from app.api.routes.system import router as system_router

api_router = APIRouter()

# Include sub-routers under API v1
api_router.include_router(system_router)
api_router.include_router(github_router)
api_router.include_router(skill_gap_router, prefix="/skill-gap")
api_router.include_router(
    career_recommendation_router, prefix="/career-recommendations"
)
api_router.include_router(resume_router, prefix="/resume")
api_router.include_router(evidence_router, prefix="/evidence")
api_router.include_router(job_matching_router, prefix="/job-matching")
api_router.include_router(
    developer_profile_router, prefix="/developer-profile"
)
api_router.include_router(
    repository_architecture_router, prefix="/repository-architecture"
)
