from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class SkillRecommendationResponse(BaseModel):
    """Schema representing learning recommendations for a single missing skill."""

    skill: str = Field(..., description="Canonical name of the missing skill")
    priority: str = Field(..., description="Explainable priority level: HIGH, MEDIUM, or LOW")
    reason: str = Field(..., description="Rationale for the assigned priority and learning sequence")
    difficulty: str = Field(..., description="Skill difficulty level: Beginner, Intermediate, Advanced")
    prerequisites: List[str] = Field(
        default_factory=list,
        description="Prerequisite skills recommended before starting this skill",
    )
    learning_topics: List[str] = Field(
        default_factory=list,
        description="Core conceptual and practical topics to learn",
    )
    suggested_projects: List[str] = Field(
        default_factory=list,
        description="Suggested portfolio projects applying this skill to career systems",
    )

    model_config = ConfigDict(extra="ignore")


class RoadmapStageResponse(BaseModel):
    """Schema representing an ordered milestone stage within the learning roadmap."""

    stage_number: int = Field(..., description="Sequential stage index (1-based)")
    title: str = Field(..., description="Stage title describing the learning milestone")
    skills: List[str] = Field(..., description="List of missing skills addressed in this stage")
    objective: str = Field(..., description="Learning milestone objective for this stage")
    recommended_projects: List[str] = Field(
        default_factory=list,
        description="Aggregated project suggestions relevant to this stage",
    )

    model_config = ConfigDict(extra="ignore")


class CareerRecommendationRequest(BaseModel):
    """Schema for requesting career learning recommendations against a target role."""

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


class CareerRecommendationResponse(BaseModel):
    """Schema representing complete career recommendations and sequential roadmap."""

    target_role: str = Field(..., description="Display title of the evaluated target role")
    role_slug: str = Field(..., description="Standardized URL-safe role slug")
    skill_match_percentage: float = Field(
        ...,
        description=(
            "Deterministic skill-coverage metric: round((total_matched / total_required) * 100, 2). "
            "Does not imply employability or guaranteed career readiness."
        ),
    )
    match_percentage: float = Field(
        ...,
        description="Alias for skill_match_percentage provided for backwards compatibility",
    )
    total_required_skills: int = Field(..., description="Total count of skills required for the role")
    total_matched_skills: int = Field(..., description="Total count of required skills possessed by developer")
    total_missing_skills: int = Field(..., description="Total count of required skills missing")
    current_skills: List[str] = Field(default_factory=list, description="Raw input skills analyzed")
    matched_skills: List[str] = Field(default_factory=list, description="Canonical names of skills matched")
    missing_skills: List[str] = Field(default_factory=list, description="Canonical names of skills missing")
    recommendations: List[SkillRecommendationResponse] = Field(
        default_factory=list,
        description="Prioritized learning guidance for each missing skill",
    )
    roadmap: List[RoadmapStageResponse] = Field(
        default_factory=list,
        description="Ordered, multi-stage learning progression roadmap",
    )
    disclaimer: str = Field(
        ...,
        description="Notice stating that recommendations are guidance and not employment guarantees",
    )

    model_config = ConfigDict(extra="ignore")
