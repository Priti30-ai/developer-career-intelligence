from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class CareerRoleSummaryResponse(BaseModel):
    """Schema representing basic career role metadata."""

    slug: str = Field(..., description="Normalized URL-safe slug for the role")
    display_name: str = Field(..., description="Human-readable title for the role")
    description: Optional[str] = Field(None, description="Short role summary")
    required_skill_count: int = Field(..., description="Number of required skills for this role")

    model_config = ConfigDict(extra="ignore")


class CareerRoleDetailResponse(BaseModel):
    """Schema representing complete career role requirements."""

    slug: str = Field(..., description="Normalized URL-safe slug for the role")
    display_name: str = Field(..., description="Human-readable title for the role")
    description: Optional[str] = Field(None, description="Short role summary")
    required_skills: List[str] = Field(..., description="List of normalized required skills")

    model_config = ConfigDict(extra="ignore")


class SkillGapRequest(BaseModel):
    """Schema for requesting a skill gap analysis against a target role."""

    target_role: str = Field(
        ...,
        description="Target career role slug or title (e.g., 'data-scientist' or 'Data Scientist')",
        examples=["data-scientist"],
    )
    current_skills: List[str] = Field(
        default_factory=list,
        description="List of skills or technologies currently possessed by developer",
        examples=[["Python", "Pandas", "NumPy", "Machine Learning"]],
    )

    model_config = ConfigDict(extra="ignore")


class SkillGapItemDetail(BaseModel):
    name: str = Field(..., description="Canonical skill name")
    categories: List[str] = Field(default_factory=list, description="Taxonomy categories")
    sources: List[str] = Field(default_factory=list, description="Provenance sources (e.g. 'github', 'resume')")
    evidence_status: Optional[str] = Field(None, description="Grounding evidence status ('STRONG', 'MODERATE', 'NONE_DETECTED')")
    supporting_repositories: List[str] = Field(default_factory=list, description="Names of supporting GitHub repositories")

    model_config = ConfigDict(extra="ignore")


class SkillGapCategoryBreakdown(BaseModel):
    category: str = Field(..., description="Skill taxonomy category name")
    required_count: int = Field(..., description="Number of required skills in this category")
    matched_count: int = Field(..., description="Number of matched skills in this category")
    missing_count: int = Field(..., description="Number of missing skills in this category")
    coverage_percentage: float = Field(..., description="Percentage of required skills matched in this category")

    model_config = ConfigDict(extra="ignore")


class SkillGapResponse(BaseModel):
    """Schema representing the result of a skill gap analysis."""

    target_role: str = Field(..., description="Display title of the evaluated target role")
    role_slug: str = Field(..., description="Standardized URL-safe role slug")
    total_required_skills: int = Field(..., description="Total count of skills required for the role")
    total_matched_skills: int = Field(..., description="Total count of required skills possessed by developer")
    total_missing_skills: int = Field(..., description="Total count of required skills missing")
    skill_match_percentage: float = Field(
        ...,
        description=(
            "Deterministic skill-coverage metric calculated as: "
            "round((total_matched_skills / total_required_skills) * 100, 2). "
            "Represents the proportion of target role prerequisite skills present in the profile; "
            "does not imply candidate employability, job readiness, or hiring suitability."
        ),
    )
    match_percentage: float = Field(
        ...,
        description="Alias for skill_match_percentage provided for backwards compatibility.",
    )
    matched_skills: List[str] = Field(
        default_factory=list,
        description="Canonical names of skills required that the developer possesses",
    )
    missing_skills: List[str] = Field(
        default_factory=list,
        description="Canonical names of skills required that the developer is missing",
    )
    matched_skill_details: List[SkillGapItemDetail] = Field(
        default_factory=list,
        description="Detailed evidence and taxonomy metadata for matched skills",
    )
    missing_skill_details: List[SkillGapItemDetail] = Field(
        default_factory=list,
        description="Detailed taxonomy metadata for missing skills",
    )
    category_breakdown: List[SkillGapCategoryBreakdown] = Field(
        default_factory=list,
        description="Category-level requirement, match, and coverage breakdown",
    )

    model_config = ConfigDict(extra="ignore")

