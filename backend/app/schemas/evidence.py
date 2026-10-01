"""
evidence.py
-----------
Pydantic schemas for Resume vs GitHub Evidence Analysis.
"""

from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator


class SupportingRepository(BaseModel):
    """Representation of an analyzed GitHub repository providing evidence for a skill."""

    name: str = Field(..., description="Repository name")
    full_name: Optional[str] = Field(None, description="Full repository path, e.g. 'octocat/Hello-World'")
    html_url: Optional[str] = Field(None, description="Direct web link to repository on GitHub")
    skills_detected: List[str] = Field(
        default_factory=list,
        description="All normalized technologies and skills detected in this repository",
    )

    model_config = ConfigDict(extra="ignore")


class EvidenceItem(BaseModel):
    """Detailed evidence evaluation for a single skill."""

    skill: str = Field(..., description="Normalized canonical skill name")
    resume_claimed: bool = Field(
        ...,
        description="True if the skill was claimed in the candidate resume",
    )
    github_detected: bool = Field(
        ...,
        description="True if verified evidence for this skill was detected in analyzed GitHub repositories",
    )
    evidence_level: str = Field(
        ...,
        description="Deterministic classification: 'STRONG', 'MODERATE', or 'NONE_DETECTED'",
        examples=["STRONG", "MODERATE", "NONE_DETECTED"],
    )
    supporting_repositories: List[SupportingRepository] = Field(
        default_factory=list,
        description="Analyzed GitHub repositories demonstrating this skill",
    )

    model_config = ConfigDict(extra="ignore")


class EvidenceSummary(BaseModel):
    """Aggregate counts and deterministic coverage metrics for evidence analysis."""

    total_resume_skills: int = Field(
        ...,
        description="Total count of unique normalized skills claimed on resume",
    )
    skills_with_evidence: int = Field(
        ...,
        description="Count of resume skills with detected GitHub repository evidence",
    )
    skills_without_evidence: int = Field(
        ...,
        description="Count of resume skills without detected GitHub repository evidence",
    )
    evidence_coverage_percentage: float = Field(
        ...,
        description=(
            "Deterministic coverage metric: round((skills_with_evidence / total_resume_skills) * 100, 2). "
            "Reflects verified GitHub repository presence only; missing evidence does NOT imply lack of skill."
        ),
    )

    model_config = ConfigDict(extra="ignore")


class EvidenceAnalysisRequest(BaseModel):
    """Request payload to analyze resume skills against GitHub evidence."""

    github_username: str = Field(
        ...,
        description="Public GitHub username to analyze",
        max_length=100,
        examples=["octocat"],
    )
    resume_skills: List[str] = Field(
        default_factory=list,
        description="List of skills claimed on the resume",
        examples=[["Python", "JavaScript", "Docker"]],
    )
    resume_text: Optional[str] = Field(
        None,
        description="Optional raw resume text to extract skills from if resume_skills is omitted",
        max_length=50_000,
    )

    @field_validator("github_username")
    @classmethod
    def validate_username(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("github_username must not be empty or whitespace-only")
        return cleaned

    @field_validator("resume_skills")
    @classmethod
    def validate_skills(cls, value: List[str]) -> List[str]:
        return [s.strip() for s in value if s and s.strip()]

    model_config = ConfigDict(extra="ignore")


class EvidenceAnalysisResponse(BaseModel):
    """Structured response comparing claimed resume skills against GitHub evidence."""

    github_username: str = Field(..., description="Target GitHub username analyzed")
    resume_skills: List[str] = Field(
        default_factory=list,
        description="Deduplicated, normalized list of skills claimed on resume",
    )
    github_skills: List[str] = Field(
        default_factory=list,
        description="Deduplicated, normalized list of all skills detected across analyzed GitHub repositories",
    )
    evidence_items: List[EvidenceItem] = Field(
        default_factory=list,
        description="Per-skill evidence breakdown with supporting repositories and classification level",
    )
    summary: EvidenceSummary = Field(
        ...,
        description="Summary statistics and deterministic evidence coverage percentage",
    )

    model_config = ConfigDict(extra="ignore")
