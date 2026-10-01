"""
job_matching.py
---------------
Pydantic schemas for Job Description Analysis and Matching.
"""

from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator


class JobMatchingRequest(BaseModel):
    """Request payload to extract skills from a Job Description and match against developer skills."""

    job_description: str = Field(
        ...,
        description="Raw plain text of the job description or posting",
        max_length=50_000,
        examples=[
            "Senior Backend Engineer\nRequirements:\n- 3+ years experience with Python and FastAPI\n"
            "- Strong background in PostgreSQL and Docker\n- Experience with React is a plus"
        ],
    )
    developer_skills: List[str] = Field(
        default_factory=list,
        description="List of skills or technologies possessed by the developer",
        examples=[["Python", "FastAPI", "PostgreSQL", "Docker", "Git"]],
    )

    @field_validator("job_description")
    @classmethod
    def validate_not_blank(cls, value: str) -> str:
        """Ensure job_description is not empty or whitespace-only."""
        if not value or not value.strip():
            raise ValueError("job_description must not be empty or whitespace-only")
        return value

    @field_validator("developer_skills")
    @classmethod
    def validate_skills(cls, value: List[str]) -> List[str]:
        """Strip individual skills and ignore blank entries."""
        return [s.strip() for s in value if s and s.strip()]

    model_config = ConfigDict(extra="ignore")


class JobMatchingResponse(BaseModel):
    """Structured response comparing extracted JD skills against developer skills."""

    extracted_skills: List[str] = Field(
        default_factory=list,
        description="Deduplicated, normalized canonical skills detected in the job description",
    )
    developer_skills: List[str] = Field(
        default_factory=list,
        description="Deduplicated, normalized developer skills supplied for comparison",
    )
    matched_skills: List[str] = Field(
        default_factory=list,
        description="Skills present in both the job description and the developer skill set",
    )
    missing_skills: List[str] = Field(
        default_factory=list,
        description="Skills required by the job description but not detected in developer skills",
    )
    total_required_skills: int = Field(
        ...,
        description="Total count of unique skills extracted from the job description",
    )
    matched_skill_count: int = Field(
        ...,
        description="Count of matched skills",
    )
    missing_skill_count: int = Field(
        ...,
        description="Count of missing skills",
    )
    match_percentage: float = Field(
        ...,
        description=(
            "Deterministic match coverage: round((matched_skill_count / total_required_skills) * 100, 2). "
            "Returns 0.0 if total_required_skills is 0."
        ),
    )
    explanation: Optional[str] = Field(
        None,
        description="Deterministic explainability summary describing match breakdown",
    )

    model_config = ConfigDict(extra="ignore")
