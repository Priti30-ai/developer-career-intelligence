from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator


class ResumeAnalysisRequest(BaseModel):
    """Request payload containing raw resume text for analysis."""

    resume_text: str = Field(
        ...,
        description="Raw plain text content of the candidate resume",
        max_length=50_000,
        examples=[
            "SUMMARY\nComputer engineering student interested in AI and data science.\n\n"
            "TECHNICAL SKILLS\nPython, C++, SQL, Pandas, NumPy, Machine Learning\n\n"
            "EDUCATION\nGovernment Polytechnic Nashik\nDiploma in Computer Technology\n2022 - 2025\n\n"
            "PROJECTS\nFake Profile Detection\nBuilt a machine learning system using Random Forest.\n\n"
            "EXPERIENCE\nPython Intern\nCompany XYZ\nJune 2025 - August 2025\n\n"
            "CERTIFICATIONS\nPython Certification"
        ],
    )

    @field_validator("resume_text")
    @classmethod
    def validate_not_blank(cls, value: str) -> str:
        """Ensure resume_text contains non-whitespace content."""
        if not value or not value.strip():
            raise ValueError("resume_text must not be empty or whitespace-only")
        return value

    model_config = ConfigDict(extra="ignore")


class ResumeEducation(BaseModel):
    """Structured representation of an educational credential."""

    institution: str = Field(..., description="Name of the university, college, polytechnic, or school")
    degree: Optional[str] = Field(None, description="Degree or diploma title (e.g., B.E., Diploma, B.S.)")
    field_of_study: Optional[str] = Field(None, description="Major or field of study (e.g., Computer Technology)")
    start_year: Optional[str] = Field(None, description="Start year of study (e.g., 2022)")
    end_year: Optional[str] = Field(None, description="Graduation or end year (e.g., 2025)")

    model_config = ConfigDict(extra="ignore")


class ResumeExperience(BaseModel):
    """Structured representation of a professional experience entry or internship."""

    company: Optional[str] = Field(None, description="Name of employer or organization")
    role: Optional[str] = Field(None, description="Job title or role held (e.g., Python Intern)")
    start_date: Optional[str] = Field(None, description="Start date (e.g., June 2025)")
    end_date: Optional[str] = Field(None, description="End date (e.g., August 2025)")
    description: Optional[str] = Field(None, description="Summary of work or responsibilities")

    model_config = ConfigDict(extra="ignore")


class ResumeProject(BaseModel):
    """Structured representation of a personal or academic project."""

    name: str = Field(..., description="Project title or name")
    description: Optional[str] = Field(None, description="Description of the project scope and outcome")
    technologies: List[str] = Field(
        default_factory=list,
        description="Normalized technical skills detected within the project entry",
    )

    model_config = ConfigDict(extra="ignore")


class ResumeAnalysisResponse(BaseModel):
    """Structured resume profile extracted deterministically from resume text."""

    summary: Optional[str] = Field(None, description="Professional summary or career objective statement")
    skills: List[str] = Field(
        default_factory=list,
        description="Deduplicated, normalized technical skills detected across the resume",
    )
    education: List[ResumeEducation] = Field(
        default_factory=list,
        description="Structured education entries",
    )
    experience: List[ResumeExperience] = Field(
        default_factory=list,
        description="Structured professional experience and internship entries",
    )
    projects: List[ResumeProject] = Field(
        default_factory=list,
        description="Structured project entries with detected technologies",
    )
    certifications: List[str] = Field(
        default_factory=list,
        description="List of certifications and licenses",
    )
    achievements: List[str] = Field(
        default_factory=list,
        description="List of academic or career honors and achievements",
    )
    skill_count: int = Field(..., description="Total count of unique normalized skills extracted")
    project_count: int = Field(..., description="Total count of projects parsed")
    experience_count: int = Field(..., description="Total count of experience entries parsed")

    model_config = ConfigDict(extra="ignore")
