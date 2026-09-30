from typing import List
from pydantic import BaseModel, ConfigDict


class SkillResponse(BaseModel):
    """Schema representing a single skill with its repository count."""

    name: str
    repository_count: int

    model_config = ConfigDict(extra="ignore")


class SkillCategoryResponse(BaseModel):
    """Schema representing a skill category and its contained skills."""

    category: str
    skills: List[SkillResponse]

    model_config = ConfigDict(extra="ignore")


class SkillProfileResponse(BaseModel):
    """Schema representing the complete developer skill profile."""

    categories: List[SkillCategoryResponse]
    total_repositories: int
    total_unique_technologies: int

    model_config = ConfigDict(extra="ignore")
