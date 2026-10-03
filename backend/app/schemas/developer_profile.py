"""
developer_profile.py
--------------------
Pydantic schemas for the Unified Developer Profile Synthesis module.

Combines information from:
1. GitHub repository analysis & account intelligence
2. Technology extraction / normalization
3. Skill profiling & taxonomy classification
4. Resume analysis & provenance tracking
5. Resume <-> GitHub evidence synthesis

The unified developer profile acts as the core developer-level representation
for downstream intelligence modules (Job Description Matching, Skill Gap Analysis,
Career Recommendations, Learning Roadmap, and UI consumption).
"""

from typing import Any, List, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.schemas.evidence import SupportingRepository
from app.schemas.github_account import (
    AggregatedLanguage,
    EvidenceSummary,
    RepositoryCoverage,
)
from app.schemas.resume import (
    ResumeEducation,
    ResumeExperience,
    ResumeProject,
    ResumeSkill,
)
from app.schemas.skill_profile import SkillCategoryResponse

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
    repository_coverage: Optional[RepositoryCoverage] = Field(
        None,
        description="Deterministic repository counts (original, forks, archived, active, empty)",
    )
    evidence_summary: Optional[EvidenceSummary] = Field(
        None,
        description="Account-level aggregate evidence classifications (STRONG, MODERATE, WEAK)",
    )
    languages: List[AggregatedLanguage] = Field(
        default_factory=list,
        description="Aggregated programming and markup languages across repositories",
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
    categorized_skills: List[ResumeSkill] = Field(
        default_factory=list,
        description="Resume skills with taxonomy categories and resume section provenance",
    )

    model_config = ConfigDict(extra="ignore")


class DeveloperSkillEvidence(BaseModel):
    """
    Granular evidence signals and section provenance from GitHub and Resume.
    """

    # GitHub evidence provenance
    repository_count: int = Field(0, description="Count of analyzed repositories demonstrating this skill")
    evidence_count: int = Field(0, description="Total concrete evidence signals confirming this skill")
    evidence_strength: Optional[str] = Field(
        None,
        description="Grounded GitHub evidence strength: 'STRONG', 'MODERATE', 'WEAK', or None if no GitHub evidence",
    )
    supporting_repositories: List[str] = Field(
        default_factory=list,
        description="Names of analyzed repositories demonstrating this skill",
    )
    signal_types: List[str] = Field(
        default_factory=list,
        description="Evidence source types detected (e.g. 'DEPENDENCY_MANIFEST', 'SOURCE_LANGUAGE', 'REPOSITORY_TOPIC')",
    )

    # Resume section provenance
    resume_sources: List[str] = Field(
        default_factory=list,
        description="Resume sections where this skill was detected ('skills_section', 'project_text', 'experience_text')",
    )

    model_config = ConfigDict(extra="ignore")


class DeveloperSkill(BaseModel):
    """
    Unified skill entry combining source tracking and verified GitHub evidence.

    Sources indicate where the skill was identified ('github', 'resume', or both).
    Evidence status classifies verified repository evidence:
    - STRONG: detected across >= 2 analyzed repositories or confirmed by manifests/configs
    - MODERATE: detected in 1 analyzed repository
    - NONE_DETECTED: no evidence detected in analyzed GitHub repositories

    CRITICAL NOTE:
    'NONE_DETECTED' indicates absence of analyzed GitHub repository evidence.
    It does NOT prove or imply that the candidate lacks the skill.
    """

    skill: str = Field(..., description="Canonical normalized skill name (backward compatible)")
    name: Optional[str] = Field(None, description="Canonical normalized skill name")
    categories: List[str] = Field(
        default_factory=list,
        description="Shared taxonomy categories from CATEGORY_DEFINITIONS via _classify_technology()",
    )
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
    evidence: DeveloperSkillEvidence = Field(
        default_factory=DeveloperSkillEvidence,
        description="Granular evidence signals and section provenance from GitHub and Resume",
    )
    supporting_repositories: List[SupportingRepository] = Field(
        default_factory=list,
        description="Analyzed GitHub repositories demonstrating this skill",
    )

    @model_validator(mode="before")
    @classmethod
    def sync_name_and_skill(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if "skill" in data and not data.get("name"):
                data["name"] = data["skill"]
            elif "name" in data and not data.get("skill"):
                data["skill"] = data["name"]
        return data

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
    github_only_skills: int = Field(
        0,
        description="Count of unique skills detected only across GitHub repositories",
    )
    resume_only_skills: int = Field(
        0,
        description="Count of unique skills claimed only on the resume",
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
    categorized_skills: List[SkillCategoryResponse] = Field(
        default_factory=list,
        description="Unified skills grouped into standardized domain categories",
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
