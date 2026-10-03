"""
github_account.py
-----------------
Pydantic schemas and data contracts for the GitHub Account Intelligence module.

Represents:
1. AccountMetadata: Account-level identity and statistics from public GitHub API.
2. EvidenceSourceSignal: Grounded provenance explaining why a technology or skill was detected.
3. RepositoryAnalysisDetail: Complete per-repository analysis preserving individual repository integrity.
4. AggregatedLanguage: Aggregated cross-repository language counts and distribution.
5. AggregatedTechnology: Normalized cross-repository technology counts and supporting repositories.
6. AggregatedSkill: Categorized cross-repository skills with supporting repository links.
7. RepositoryCoverage: Deterministic repository counts (original, forks, archived, active, empty).
8. EvidenceSummary: Account-wide evidence classification counts (STRONG, MODERATE, WEAK).
9. AggregatedAccountProfile: Synthesized cross-repository profile.
10. GitHubAccountAnalysisResponse: Root container combining account, repositories, and aggregated profile.

Critical Architectural Invariant:
Repository details MUST NOT be collapsed or lost during cross-repository aggregation.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field

from app.schemas.repository_architecture import ArchitectureSignal
from app.schemas.skill_profile import SkillCategoryResponse

# Evidence source classifications
EVIDENCE_SOURCE_MANIFEST = "DEPENDENCY_MANIFEST"
EVIDENCE_SOURCE_LANGUAGE = "SOURCE_LANGUAGE"
EVIDENCE_SOURCE_TOPIC = "REPOSITORY_TOPIC"
EVIDENCE_SOURCE_STRUCTURE = "PROJECT_STRUCTURE"
EVIDENCE_SOURCE_CONFIG = "CONFIGURATION"
EVIDENCE_SOURCE_README = "README"

# Evidence strength classifications (aligned with project standards)
EVIDENCE_STRENGTH_STRONG = "STRONG"
EVIDENCE_STRENGTH_MODERATE = "MODERATE"
EVIDENCE_STRENGTH_WEAK = "WEAK"


class AccountMetadata(BaseModel):
    """Public GitHub account profile identity and high-level platform statistics."""

    login: str = Field(..., description="Canonical GitHub username / handle")
    name: Optional[str] = Field(None, description="Public display name")
    avatar_url: Optional[str] = Field(None, description="Avatar image URL")
    html_url: Optional[str] = Field(None, description="Web link to the GitHub profile")
    bio: Optional[str] = Field(None, description="Public biography statement")
    public_repos: int = Field(0, description="Total count of public repositories")
    followers: int = Field(0, description="Follower count")
    following: int = Field(0, description="Following count")
    account_type: Optional[str] = Field(None, description="Account classification (e.g. 'User', 'Organization')")
    company: Optional[str] = Field(None, description="Company or organization affiliation")
    location: Optional[str] = Field(None, description="Geographic location string")
    blog: Optional[str] = Field(None, description="Website or blog URL")
    email: Optional[str] = Field(None, description="Public email address if available")
    twitter_username: Optional[str] = Field(None, description="Twitter / X username")
    created_at: Optional[datetime] = Field(None, description="Account creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last account update timestamp")

    model_config = ConfigDict(extra="ignore")


class EvidenceSourceSignal(BaseModel):
    """
    Concrete signal explaining WHY and WHERE a technology or skill was detected.

    Grounded in:
    - DEPENDENCY_MANIFEST (e.g. requirements.txt, package.json)
    - SOURCE_LANGUAGE (e.g. primary language or file extensions)
    - REPOSITORY_TOPIC (e.g. repository topic tags)
    - PROJECT_STRUCTURE (e.g. frontend/ or migrations/ directory topology)
    - CONFIGURATION (e.g. Dockerfile, tsconfig.json, vite.config.js)
    - README (e.g. project documentation)
    """

    source_type: str = Field(
        ...,
        description="Evidence source: 'DEPENDENCY_MANIFEST', 'SOURCE_LANGUAGE', 'REPOSITORY_TOPIC', 'PROJECT_STRUCTURE', 'CONFIGURATION', 'README'",
        examples=["DEPENDENCY_MANIFEST", "SOURCE_LANGUAGE", "REPOSITORY_TOPIC", "PROJECT_STRUCTURE"],
    )
    technology: str = Field(..., description="Canonical normalized technology or skill name")
    path: Optional[str] = Field(None, description="File path, directory, or manifest triggering the signal")
    strength: str = Field(
        EVIDENCE_STRENGTH_MODERATE,
        description="Evidence strength classification: 'STRONG', 'MODERATE', or 'WEAK'",
        examples=["STRONG", "MODERATE", "WEAK"],
    )
    reason: Optional[str] = Field(
        None,
        description="Human-readable explanation of why this evidence confirms the technology",
    )
    details: Dict[str, Any] = Field(
        default_factory=dict,
        description="Optional auxiliary attributes (e.g. detected version, line number, pattern)",
    )

    model_config = ConfigDict(extra="ignore")


class RepositoryAnalysisDetail(BaseModel):
    """
    Complete analysis of an individual GitHub repository.
    Preserves repository-level granularity without collapsing during account aggregation.
    """

    # Repository metadata
    name: str = Field(..., description="Repository name")
    full_name: str = Field(..., description="Full repository path, e.g. 'owner/repo'")
    description: Optional[str] = Field(None, description="Repository description")
    html_url: str = Field(..., description="Web link to the repository on GitHub")
    default_branch: Optional[str] = Field("main", description="Default branch name")
    stargazers_count: int = Field(0, description="Star count")
    forks_count: int = Field(0, description="Fork count")
    watchers_count: int = Field(0, description="Watcher count")
    is_fork: bool = Field(False, description="True if repository is a fork of another project")
    is_archived: bool = Field(False, description="True if repository is read-only / archived")
    is_empty: bool = Field(False, description="True if repository has no commits or files")
    created_at: Optional[datetime] = Field(None, description="Repository creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    pushed_at: Optional[datetime] = Field(None, description="Last commit push timestamp")
    topics: List[str] = Field(default_factory=list, description="Repository topic tags")

    # Language information
    primary_language: Optional[str] = Field(None, description="Primary programming language identified by GitHub")
    languages: List[str] = Field(default_factory=list, description="All detected languages across repository")

    # Technology information
    technologies: List[str] = Field(default_factory=list, description="Normalized technologies extracted from this repository")

    # Project and Architecture information
    manifest_files: List[str] = Field(default_factory=list, description="Dependency and build manifests identified in repository")
    project_type: Optional[str] = Field(None, description="Architectural classification: FULL_STACK, BACKEND, FRONTEND, etc.")
    architecture_signals: List[ArchitectureSignal] = Field(default_factory=list, description="Structural signals detected from repository tree")

    # Skills
    skills: List[str] = Field(default_factory=list, description="Skills detected in this repository")
    skill_categories: List[SkillCategoryResponse] = Field(default_factory=list, description="Grouped skills if categorized")

    # Evidence
    evidence: List[EvidenceSourceSignal] = Field(default_factory=list, description="Concrete evidence signals from this repository")

    # Analysis metadata
    analysis_status: str = Field("SUCCESS", description="Analysis status: SUCCESS, PARTIAL, SKIPPED, ERROR")
    is_partial: bool = Field(False, description="True if analysis was limited (e.g. tree truncated or timeout)")
    tree_truncated: bool = Field(False, description="True if GitHub tree exceeded API limit (truncated: true)")
    warnings: List[str] = Field(default_factory=list, description="Non-fatal warnings encountered during analysis")

    model_config = ConfigDict(extra="ignore")


class AggregatedLanguage(BaseModel):
    """Aggregated language statistics across analyzed repositories."""

    name: str = Field(..., description="Canonical language name")
    repository_count: int = Field(..., description="Number of repositories utilizing this language")
    percentage: Optional[float] = Field(
        None,
        description="Share of repositories using this language (percentage, e.g. 75.0)",
    )
    supporting_repositories: List[str] = Field(
        default_factory=list,
        description="Names of analyzed repositories utilizing this language",
    )

    model_config = ConfigDict(extra="ignore")


class AggregatedTechnology(BaseModel):
    """Normalized technology aggregated across all analyzed repositories."""

    name: str = Field(..., description="Canonical normalized technology name")
    repository_count: int = Field(..., description="Count of repositories containing this technology")
    evidence_count: int = Field(0, description="Total concrete evidence signals confirming this technology")
    supporting_repositories: List[str] = Field(
        default_factory=list,
        description="Names of analyzed repositories demonstrating this technology",
    )

    model_config = ConfigDict(extra="ignore")


class AggregatedSkill(BaseModel):
    """Categorized skill aggregated across all analyzed repositories with evidence summary."""

    name: str = Field(..., description="Canonical skill name")
    category: str = Field(
        ...,
        description="Skill category: 'Programming Languages', 'Frameworks & Libraries', 'AI / Machine Learning', 'Web Technologies', 'Databases', 'DevOps & Cloud', 'Tools & Other'",
    )
    repository_count: int = Field(..., description="Count of repositories demonstrating this skill")
    evidence_count: int = Field(0, description="Total concrete evidence signals confirming this skill")
    evidence_strength: str = Field(
        EVIDENCE_STRENGTH_MODERATE,
        description="Aggregated evidence strength: 'STRONG' (>=2 repos or manifest), 'MODERATE' (1 repo), 'WEAK'",
    )
    supporting_repositories: List[str] = Field(
        default_factory=list,
        description="Names of analyzed repositories demonstrating this skill",
    )

    model_config = ConfigDict(extra="ignore")


class RepositoryCoverage(BaseModel):
    """Deterministic account-level repository statistics and coverage metrics."""

    total_repositories_analyzed: int = Field(0, description="Total public repositories analyzed")
    original_repositories: int = Field(0, description="Non-fork repositories created by the user")
    forked_repositories: int = Field(0, description="Forked repositories")
    archived_repositories: int = Field(0, description="Archived / read-only repositories")
    active_repositories: int = Field(0, description="Active, non-archived repositories")
    successfully_analyzed_repositories: int = Field(0, description="Repositories fully inspected without warnings")
    partially_analyzed_repositories: int = Field(0, description="Repositories analyzed partially (e.g. tree truncated)")
    empty_repositories: int = Field(0, description="Empty repositories (0 commits)")
    error_repositories: int = Field(0, description="Count of repositories that encountered fatal errors during analysis")

    model_config = ConfigDict(extra="ignore")


class EvidenceSummary(BaseModel):
    """Account-level aggregate evidence counts and classifications."""

    strong_evidence_count: int = Field(0, description="Count of skills with STRONG evidence")
    moderate_evidence_count: int = Field(0, description="Count of skills with MODERATE evidence")
    weak_evidence_count: int = Field(0, description="Count of skills with WEAK / topic-only evidence")
    total_evidence_signals: int = Field(0, description="Total discrete evidence signals detected across all repositories")
    technologies_with_strong_evidence: int = Field(0, description="Count of technologies supported by manifests or multi-repo proof")
    technologies_with_evidence: int = Field(0, description="Total unique technologies with >= 1 evidence signal")

    model_config = ConfigDict(extra="ignore")


class AggregatedAccountProfile(BaseModel):
    """
    Synthesized account-level technical profile across all public repositories.
    Preserves technology frequency, domain skill categories, and grounded evidence metrics.
    """

    languages: List[AggregatedLanguage] = Field(default_factory=list, description="Aggregated programming and markup languages")
    technologies: List[AggregatedTechnology] = Field(default_factory=list, description="Normalized technologies across repositories")
    skills: List[AggregatedSkill] = Field(default_factory=list, description="Aggregated skills with evidence strength and supporting repos")
    categorized_skills: List[SkillCategoryResponse] = Field(default_factory=list, description="Skills grouped into standardized domain categories")
    repository_coverage: RepositoryCoverage = Field(default_factory=RepositoryCoverage, description="Account-level repository statistics")
    evidence_summary: EvidenceSummary = Field(default_factory=EvidenceSummary, description="Account-level evidence signal counts")
    total_unique_technologies: int = Field(0, description="Total distinct normalized technologies")
    total_unique_skills: int = Field(0, description="Total distinct normalized skills")

    model_config = ConfigDict(extra="ignore")


class GitHubAccountAnalysisResponse(BaseModel):
    """
    Root response container for GitHub Account Intelligence.

    Hierarchical Architecture:
    - account: High-level account metadata.
    - repositories: Granular, per-repository analyses with individual technologies, manifests, and evidence.
    - aggregated_profile: Cross-repository synthesized skills, technology frequencies, and evidence summaries.
    """

    account: AccountMetadata = Field(..., description="GitHub account metadata and platform statistics")
    repositories: List[RepositoryAnalysisDetail] = Field(default_factory=list, description="Per-repository detailed analyses")
    aggregated_profile: AggregatedAccountProfile = Field(..., description="Cross-repository aggregated developer intelligence")

    def get_repository(self, name: str) -> Optional[RepositoryAnalysisDetail]:
        """Lookup a specific repository analysis by name."""
        clean_name = name.strip().lower()
        for repo in self.repositories:
            if repo.name.lower() == clean_name or repo.full_name.lower() == clean_name:
                return repo
        return None

    def get_technology_names(self) -> List[str]:
        """Extract deduplicated canonical technology names from aggregated profile."""
        return [tech.name for tech in self.aggregated_profile.technologies]

    def get_skill_names(self) -> List[str]:
        """Extract deduplicated canonical skill names for downstream intelligence consumption."""
        return [skill.name for skill in self.aggregated_profile.skills]

    model_config = ConfigDict(extra="ignore")
