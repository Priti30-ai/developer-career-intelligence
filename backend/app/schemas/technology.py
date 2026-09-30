from typing import List
from pydantic import BaseModel, ConfigDict


class TechnologyResponse(BaseModel):
    """Schema representing an extracted technology signal and its repository count."""

    name: str
    repository_count: int

    model_config = ConfigDict(extra="ignore")


class TechnologyExtractionResponse(BaseModel):
    """Schema representing complete technology extraction results for a user."""

    technologies: List[TechnologyResponse]
    total_repositories: int

    model_config = ConfigDict(extra="ignore")
