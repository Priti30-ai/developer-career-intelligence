"""
repository_architecture.py
--------------------------
Pydantic schemas for GitHub Repository Architecture Analysis.

Defines models for:
- Repository metadata identification
- Architecture components and concrete evidence signals
- Dependency and build manifest detection
- Project classification (e.g. FULL_STACK, FRONTEND, BACKEND, DATA_SCIENCE, etc.)
- Summary statistics and architectural component flags
"""

from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator


class RepositoryInfo(BaseModel):
    """Basic repository identification and web metadata."""

    name: str = Field(..., description="Repository name")
    full_name: Optional[str] = Field(None, description="Full repository path, e.g. 'owner/repo'")
    html_url: Optional[str] = Field(None, description="Web link to repository on GitHub")
    default_branch: Optional[str] = Field(None, description="Default branch of the repository, e.g. 'main'")

    model_config = ConfigDict(extra="ignore")


class ArchitectureSignal(BaseModel):
    """Specific architectural component detected from repository structure with concrete evidence."""

    type: str = Field(
        ...,
        description=(
            "Component classification: 'FRONTEND', 'BACKEND', 'DATABASE', "
            "'DEVOPS', 'DATA_SCIENCE', 'MACHINE_LEARNING', 'CLI', 'TESTING', 'DOCUMENTATION'"
        ),
        examples=["FRONTEND", "BACKEND", "DATABASE", "DEVOPS"],
    )
    description: str = Field(
        ...,
        description="Explainable description of the detected architectural component",
    )
    evidence: List[str] = Field(
        default_factory=list,
        description="Concrete file or directory paths that triggered this structural signal",
    )

    model_config = ConfigDict(extra="ignore")


class RepositoryArchitectureSummary(BaseModel):
    """Deterministic aggregate statistics and architectural capability indicators."""

    total_files_analyzed: int = Field(
        ...,
        description="Total file items found and analyzed in the repository tree",
    )
    total_directories_detected: int = Field(
        ...,
        description="Total distinct structural directories identified",
    )
    primary_project_type: str = Field(
        ...,
        description="Determined project classification",
        examples=["FULL_STACK", "FRONTEND", "BACKEND", "DATA_SCIENCE", "MACHINE_LEARNING", "CLI", "LIBRARY", "UNKNOWN"],
    )
    has_frontend: bool = Field(..., description="True if frontend architecture signals were detected")
    has_backend: bool = Field(..., description="True if backend architecture signals were detected")
    has_database: bool = Field(..., description="True if database, models, or migration signals were detected")
    has_devops: bool = Field(..., description="True if CI/CD, Docker, or containerization signals were detected")
    has_documentation: bool = Field(..., description="True if structured documentation files were detected")

    model_config = ConfigDict(extra="ignore")


class RepositoryArchitectureRequest(BaseModel):
    """Request payload to analyze repository architecture."""

    owner: str = Field(
        ...,
        description="GitHub repository owner or organization",
        max_length=100,
        examples=["octocat"],
    )
    repo: str = Field(
        ...,
        description="GitHub repository name",
        max_length=100,
        examples=["Hello-World"],
    )
    branch: Optional[str] = Field(
        None,
        description="Optional branch name or commit SHA to inspect (defaults to default branch)",
        max_length=100,
    )

    @field_validator("owner")
    @classmethod
    def validate_owner(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("owner must not be empty or whitespace-only")
        return cleaned

    @field_validator("repo")
    @classmethod
    def validate_repo(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("repo must not be empty or whitespace-only")
        return cleaned

    model_config = ConfigDict(extra="ignore")


class RepositoryArchitectureResponse(BaseModel):
    """Structured architectural analysis of a GitHub repository."""

    repository: RepositoryInfo = Field(..., description="Repository identification and metadata")
    project_type: str = Field(
        ...,
        description="High-level project classification",
        examples=["FULL_STACK", "FRONTEND", "BACKEND", "DATA_SCIENCE", "MACHINE_LEARNING", "CLI", "LIBRARY", "UNKNOWN"],
    )
    primary_language: Optional[str] = Field(None, description="Primary programming language reported by GitHub")
    languages_detected: List[str] = Field(
        default_factory=list,
        description="Normalized programming and markup languages detected across repository files",
    )
    directories_detected: List[str] = Field(
        default_factory=list,
        description="Key architectural directories detected in the repository tree",
    )
    important_files: List[str] = Field(
        default_factory=list,
        description="Prominent architectural, configuration, and build files detected",
    )
    dependency_files: List[str] = Field(
        default_factory=list,
        description="Dependency and package management manifests identified",
    )
    documentation_files: List[str] = Field(
        default_factory=list,
        description="Documentation files identified",
    )
    architecture_signals: List[ArchitectureSignal] = Field(
        default_factory=list,
        description="Structured architecture signals with concrete evidence paths",
    )
    summary: RepositoryArchitectureSummary = Field(
        ...,
        description="Summary statistics and architectural component flags",
    )

    model_config = ConfigDict(extra="ignore")
