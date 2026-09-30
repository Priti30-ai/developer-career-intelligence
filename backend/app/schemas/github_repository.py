from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class GitHubRepositoryResponse(BaseModel):
    """Pydantic model representing a GitHub repository."""

    name: str
    full_name: str
    description: Optional[str] = None
    html_url: str
    language: Optional[str] = None
    stargazers_count: int = 0
    forks_count: int = 0
    topics: List[str] = Field(default_factory=list)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    private: bool = False
    fork: bool = False

    model_config = ConfigDict(extra="ignore")
