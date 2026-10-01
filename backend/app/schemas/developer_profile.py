"""
developer_profile.py
--------------------
Pydantic schemas for the Unified Developer Profile Synthesis module.

Combines information from:
1. GitHub repository analysis
2. Technology extraction / normalization
3. Skill profiling
4. Resume analysis
5. Resume <-> GitHub evidence analysis

The unified developer profile acts as the core developer-level representation
for downstream intelligence modules (Job Description Matching, Skill Gap Analysis,
Career Recommendations, Learning Roadmap, and UI consumption).
"""

from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.evidence import SupportingRepository
from app.schemas.resume import (
    ResumeEducation,
    ResumeExperience,
    ResumeProject,
)

SOURCE_GITHUB = "github"
SOURCE_RESUME = "resume"


class GitHubSummary(BaseModel):
    """Aggregated GitHub repository and technology summary."""

    username: str = Field(..., description="Public GitHub username analyzed")
    repositories_analyzed: int = Field(..., description="Total public repositories analyzed")
    technologies_detected: List[str] = Field(
        default_factory=list,
        description="Deduplicated, normalized technologies detected across analyzed repositories",
    )

    model_config = ConfigDict(extra="ignore")


class ResumeSummary(BaseModel):
    """Aggregated resume content summary."""

    summary: Optional[str] = Field(None, description="Summary or objective statement from resume")
    skills: List[str] = Field(
        default_factory=list,
        description="Deduplicated, normalized skills claimed on resume",
    )
    education: List[ResumeEducation] = Field(
        default_factory=list,
        description="Structured education entries",
    )
    experience: List[ResumeExperience] = Field(
        default_factory=list,
        description="Structured experience and internship entries",
    )
    projects: List[ResumeProject] = Field(
        default_factory=list,
        description="Structured project entries with detected technologies",
    )
    certifications: List[str] = Field(
        default_factory=list,
        description="Certifications listed on resume",
    )
    achievements: List[str] = Field(
        default_factory=list,
        description="Academic or professional achievements listed on resume",
    )

    model_config = ConfigDict(extra="ignore")


class DeveloperSkill(BaseModel):
    """
    Unified skill entry combining source tracking and verified GitHub evidence.

    Sources indicate where the skill was identified ('github', 'resume', or both).
    Evidence status classifies verified repository evidence:
    - STRONG: detected across >= 2 analyzed repositories
    - MODERATE: detected in 1 analyzed repository
    - NONE_DETECTED: no evidence detected in analyzed GitHub repositories

    CRITICAL NOTE:
    'NONE_DETECTED' indicates absence of analyzed GitHub repository evidence.
    It does NOT prove or imply that the candidate lacks the skill.
    """

    skill: str = Field(..., description="Canonical normalized skill name")
    sources: List[str] = Field(
        ...,
        description="Origin sources: 'github', 'resume', or both",
        examples=[["github", "resume"], ["github"], ["resume"]],
    )
    evidence_status: str = Field(
        ...,
        description="Evidence classification: 'STRONG', 'MODERATE', or 'NONE_DETECTED'",
        examples=["STRONG", "MODERATE", "NONE_DETECTED"],
    )
    supporting_repositories: List[SupportingRepository] = Field(
        default_factory=list,
        description="Analyzed GitHub repositories demonstrating this skill",
    )

    model_config = ConfigDict(extra="ignore")


class DeveloperProfileSummary(BaseModel):
    """Deterministic aggregate statistics for the unified developer profile."""

    total_skills: int = Field(
        ...,
        description="Total unique canonical skills across all sources",
    )
    github_skill_count: int = Field(
        ...,
        description="Count of unique skills detected across GitHub repositories",
    )
    resume_skill_count: int = Field(
        ...,
        description="Count of unique skills claimed on the resume",
    )
    skills_from_both_sources: int = Field(
        ...,
        description="Count of skills verified both in GitHub repositories and claimed on resume",
    )
    supported_skill_count: int = Field(
        ...,
        description="Count of skills with >= 1 supporting repository in GitHub (STRONG or MODERATE)",
    )
    skills_without_github_evidence: int = Field(
        ...,
        description=(
            "Count of skills with no detected GitHub evidence (NONE_DETECTED). "
            "Note: missing GitHub evidence does NOT imply lack of skill."
        ),
    )

    model_config = ConfigDict(extra="ignore")


class DeveloperProfileRequest(BaseModel):
    """Request payload to synthesize a unified developer profile."""

    github_username: str = Field(
        ...,
        description="Public GitHub username to analyze",
        max_length=100,
        examples=["octocat"],
    )
    resume_text: Optional[str] = Field(
        None,
        description="Optional raw plain text content of the candidate resume",
        max_length=50_000,
    )
    resume_skills: Optional[List[str]] = Field(
        default_factory=list,
        description="Optional pre-extracted skill list if raw resume text is not supplied",
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
    def validate_skills(cls, value: Optional[List[str]]) -> List[str]:
        if value is None:
            return []
        return [s.strip() for s in value if s and s.strip()]

    model_config = ConfigDict(extra="ignore")


class DeveloperProfileResponse(BaseModel):
    """
    Unified Developer Profile representation combining repository, resume,
    and evidence intelligence.
    """

    developer_id: str = Field(..., description="Developer identifier / username")
    github: GitHubSummary = Field(..., description="GitHub repository analysis summary")
    resume: ResumeSummary = Field(..., description="Resume profile summary")
    skills: List[DeveloperSkill] = Field(
        default_factory=list,
        description="Deduplicated canonical skills with source tracking and evidence status",
    )
    summary: DeveloperProfileSummary = Field(
        ...,
        description="Aggregated deterministic profile statistics",
    )

    def get_skill_names(self) -> List[str]:
        """
        Helper method to extract canonical skill names for downstream modules
        such as Job Description Matching and Skill Gap Analysis.
        """
        return [item.skill for item in self.skills]

    model_config = ConfigDict(extra="ignore")
