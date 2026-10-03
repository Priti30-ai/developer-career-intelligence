"""
github_account_service.py
-------------------------
Service for discovering and cataloging GitHub user accounts and their public repositories.

Target Workflow:
GitHub username / profile URL
      ↓
Normalize username (via normalize_github_username)
      ↓
Fetch GitHub account profile
      ↓
Discover all public repositories (with pagination)
      ↓
Return clean repository catalog and AccountMetadata conforming to GitHubAccountAnalysisResponse

Design Constraint:
This service performs account and repository discovery only.
It does NOT perform deep manifest parsing, AST inspection, or technology/evidence synthesis.
Deep analysis fields remain safely empty until downstream inspection tasks.
"""

from typing import Any, Dict, List, Optional

from app.schemas.github_account import (
    AccountMetadata,
    AggregatedAccountProfile,
    AggregatedLanguage,
    GitHubAccountAnalysisResponse,
    RepositoryAnalysisDetail,
    RepositoryCoverage,
)
from app.services.github_account_aggregation_service import (
    GitHubAccountAggregationService,
    github_account_aggregation_service,
)
from app.services.github_evidence_service import (
    GitHubEvidenceService,
    github_evidence_service,
)
from app.services.github_repository_inspection_service import (
    GitHubRepositoryInspectionService,
    github_repository_inspection_service,
)
from app.services.github_service import (
    GitHubAPIError,
    GitHubService,
    GitHubUserNotFoundError,
    InvalidGitHubUsernameError,
    github_service,
    normalize_github_username,
)


class GitHubAccountService:
    """Service to discover and assemble GitHub account and repository catalogs."""

    def __init__(
        self,
        service: Optional[GitHubService] = None,
        inspection_service: Optional[GitHubRepositoryInspectionService] = None,
        evidence_service: Optional[GitHubEvidenceService] = None,
        aggregation_service: Optional[GitHubAccountAggregationService] = None,
    ):
        self.github_service = service or github_service
        self.inspection_service = inspection_service or github_repository_inspection_service
        self.evidence_service = evidence_service or github_evidence_service
        self.aggregation_service = aggregation_service or github_account_aggregation_service

    def _map_account_metadata(self, profile_data: Dict[str, Any]) -> AccountMetadata:
        """Map raw GitHub user profile dictionary into AccountMetadata schema."""
        return AccountMetadata(
            login=profile_data["login"],
            name=profile_data.get("name"),
            avatar_url=profile_data.get("avatar_url"),
            html_url=profile_data.get("html_url"),
            bio=profile_data.get("bio"),
            public_repos=profile_data.get("public_repos", 0),
            followers=profile_data.get("followers", 0),
            following=profile_data.get("following", 0),
            account_type=profile_data.get("account_type"),
            company=profile_data.get("company"),
            location=profile_data.get("location"),
            blog=profile_data.get("blog"),
            email=profile_data.get("email"),
            twitter_username=profile_data.get("twitter_username"),
            created_at=profile_data.get("created_at"),
            updated_at=profile_data.get("updated_at"),
        )

    def _map_repository_detail(self, repo: Dict[str, Any]) -> RepositoryAnalysisDetail:
        """
        Map a discovered GitHub repository dict into RepositoryAnalysisDetail.

        Deep-analysis fields (technologies, skills, evidence, architecture signals, manifests)
        are initialized as empty defaults as deep inspection has not yet occurred.
        """
        primary_lang = repo.get("language")
        languages: List[str] = [primary_lang] if primary_lang and str(primary_lang).strip() else []
        is_empty = repo.get("size", 1) == 0

        return RepositoryAnalysisDetail(
            name=repo.get("name") or "",
            full_name=repo.get("full_name") or repo.get("name") or "",
            description=repo.get("description"),
            html_url=repo.get("html_url") or "",
            default_branch=repo.get("default_branch", "main"),
            stargazers_count=repo.get("stargazers_count", 0),
            forks_count=repo.get("forks_count", 0),
            watchers_count=repo.get("watchers_count", 0),
            is_fork=bool(repo.get("fork", False)),
            is_archived=bool(repo.get("archived", False)),
            is_empty=is_empty,
            created_at=repo.get("created_at"),
            updated_at=repo.get("updated_at"),
            pushed_at=repo.get("pushed_at"),
            topics=repo.get("topics") or [],
            primary_language=primary_lang,
            languages=languages,
            # Deep-analysis fields are explicitly empty during discovery
            technologies=[],
            manifest_files=[],
            project_type=None,
            architecture_signals=[],
            skills=[],
            skill_categories=[],
            evidence=[],
            analysis_status="SUCCESS",
            is_partial=False,
            tree_truncated=False,
            warnings=[],
        )

    def _build_initial_coverage(
        self, repositories: List[RepositoryAnalysisDetail]
    ) -> RepositoryCoverage:
        """Compute deterministic account repository counts based on discovered metadata."""
        total = len(repositories)
        forked = sum(1 for r in repositories if r.is_fork)
        original = total - forked
        archived = sum(1 for r in repositories if r.is_archived)
        active = total - archived
        empty = sum(1 for r in repositories if r.is_empty)
        successfully_analyzed = sum(
            1 for r in repositories if r.analysis_status == "SUCCESS" and not r.is_partial
        )
        partially_analyzed = sum(
            1 for r in repositories if r.is_partial or r.analysis_status in ("PARTIAL", "ERROR")
        )

        return RepositoryCoverage(
            total_repositories_analyzed=total,
            original_repositories=original,
            forked_repositories=forked,
            archived_repositories=archived,
            active_repositories=active,
            successfully_analyzed_repositories=successfully_analyzed,
            partially_analyzed_repositories=partially_analyzed,
            empty_repositories=empty,
        )

    async def discover_account(
        self,
        username_or_url: str,
        max_pages: int = 10,
        inspect_repositories: bool = False,
        enrich_evidence: bool = False,
        aggregate_account: bool = False,
    ) -> GitHubAccountAnalysisResponse:
        """
        Discover a GitHub account and its public repositories.

        Args:
            username_or_url: GitHub username or profile URL.
            max_pages: Maximum repository pages to fetch (default 10).
            inspect_repositories: If True, deeply inspects each repository tree & architecture.
            enrich_evidence: If True, extracts repository-level technologies, skills & evidence.
            aggregate_account: If True, synthesizes cross-repository intelligence (Task 6).

        Returns:
            GitHubAccountAnalysisResponse with account metadata, discovered repository details,
            and repository coverage.

        Raises:
            InvalidGitHubUsernameError: When username format or URL is invalid.
            GitHubUserNotFoundError: When GitHub user does not exist (404).
            GitHubAPIError: When GitHub API request fails or is rate limited.
        """
        # 1. Normalize username/profile URL
        clean_username = normalize_github_username(username_or_url)

        # 2. Fetch public profile
        profile_data = await self.github_service.get_user_profile(clean_username)

        # 3. Discover all public repositories with pagination
        repos_data = await self.github_service.get_all_user_repositories(
            clean_username, max_pages=max_pages
        )

        # 4. Map into data contracts
        account_metadata = self._map_account_metadata(profile_data)
        repository_details = [
            self._map_repository_detail(repo) for repo in repos_data
        ]

        # 5. Deeply inspect repositories if requested (Task 4)
        if inspect_repositories:
            repository_details = await self.inspection_service.inspect_repositories(
                repository_details, default_owner=clean_username
            )

        # 6. Extract repository-level evidence, technologies, and skills if requested (Task 5)
        if enrich_evidence:
            repository_details = await self.evidence_service.enrich_repositories(
                repository_details, default_owner=clean_username
            )

        # 7. Synthesize cross-repository account intelligence if requested (Task 6)
        if aggregate_account:
            aggregated_profile = self.aggregation_service.aggregate_account_profile(
                repository_details
            )
        else:
            coverage = self._build_initial_coverage(repository_details)
            lang_counts: Dict[str, int] = {}
            for repo in repository_details:
                if repo.primary_language:
                    lang_counts[repo.primary_language] = (
                        lang_counts.get(repo.primary_language, 0) + 1
                    )

            aggregated_languages = [
                AggregatedLanguage(
                    name=lang,
                    repository_count=count,
                    percentage=round((count / len(repository_details)) * 100, 2)
                    if repository_details
                    else 0.0,
                )
                for lang, count in sorted(
                    lang_counts.items(), key=lambda item: (-item[1], item[0])
                )
            ]

            aggregated_profile = AggregatedAccountProfile(
                languages=aggregated_languages,
                technologies=[],
                skills=[],
                categorized_skills=[],
                repository_coverage=coverage,
                total_unique_technologies=0,
                total_unique_skills=0,
            )

        return GitHubAccountAnalysisResponse(
            account=account_metadata,
            repositories=repository_details,
            aggregated_profile=aggregated_profile,
        )

    async def inspect_account(
        self, username_or_url: str, max_pages: int = 10
    ) -> GitHubAccountAnalysisResponse:
        """
        Discover a GitHub account, catalog all public repositories,
        and perform deep repository-level architectural inspection (Task 4).

        Args:
            username_or_url: GitHub username or profile URL.
            max_pages: Maximum repository pages to fetch (default 10).

        Returns:
            GitHubAccountAnalysisResponse with inspected repository details.
        """
        return await self.discover_account(
            username_or_url=username_or_url,
            max_pages=max_pages,
            inspect_repositories=True,
            enrich_evidence=False,
            aggregate_account=False,
        )

    async def analyze_account_repositories(
        self, username_or_url: str, max_pages: int = 10
    ) -> GitHubAccountAnalysisResponse:
        """
        Discover a GitHub account, catalog all public repositories,
        deeply inspect architecture (Task 4), and enrich each repository with
        factual technologies, skills, and evidence signals (Task 5).

        Args:
            username_or_url: GitHub username or profile URL.
            max_pages: Maximum repository pages to fetch (default 10).

        Returns:
            GitHubAccountAnalysisResponse with enriched repository records.
        """
        return await self.discover_account(
            username_or_url=username_or_url,
            max_pages=max_pages,
            inspect_repositories=True,
            enrich_evidence=True,
            aggregate_account=False,
        )

    async def aggregate_account(
        self, username_or_url: str, max_pages: int = 10
    ) -> GitHubAccountAnalysisResponse:
        """
        Complete GitHub account intelligence pipeline (Tasks 3–6):
        1. Discover account & repository catalog (Task 3)
        2. Deeply inspect repository architecture & manifests (Task 4)
        3. Extract factual technologies, skills & evidence (Task 5)
        4. Synthesize cross-repository account-level intelligence (Task 6)

        Args:
            username_or_url: GitHub username or profile URL.
            max_pages: Maximum repository pages to fetch (default 10).

        Returns:
            GitHubAccountAnalysisResponse with complete aggregated account intelligence.
        """
        return await self.discover_account(
            username_or_url=username_or_url,
            max_pages=max_pages,
            inspect_repositories=True,
            enrich_evidence=True,
            aggregate_account=True,
        )


# Singleton instance for application usage
github_account_service = GitHubAccountService()
