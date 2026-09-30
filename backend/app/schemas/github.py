from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class GitHubProfileResponse(BaseModel):
    """Pydantic model representing public GitHub profile details."""

    login: str
    name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    html_url: Optional[str] = None
    public_repos: int = 0
    followers: int = 0
    following: int = 0
    created_at: Optional[datetime] = None

    model_config = ConfigDict(extra="ignore")
