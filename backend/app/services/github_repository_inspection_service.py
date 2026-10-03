"""
github_repository_inspection_service.py
---------------------------------------
Service for deep inspection of individual GitHub repositories.

Target Workflow:
Discovered Repository (Metadata)
        ↓
Fetch repository tree (with truncation detection)
        ↓
Identify relevant project files and configuration manifests
        ↓
Extract architecture signals & classify project type (via repository_architecture_service)
        ↓
Detect programming and markup languages
        ↓
Populate RepositoryAnalysisDetail with factual inspection data

Design Constraints:
1. Reuses RepositoryArchitectureService for structural and architectural analysis.
2. Isolates failures: errors in one repository never abort the entire inspection process.
3. Preserves complete repository catalog without silent filtering.
4. Concurrency safety via asyncio.Semaphore with bounded limits.
5. Factual signals only: does not fabricate technologies, skills, or cross-repo aggregations.
"""

import asyncio
from pathlib import PurePosixPath
from typing import Any, Dict, List, Optional, Set, Tuple, Union

from app.schemas.github_account import RepositoryAnalysisDetail
from app.services.github_service import (
    GitHubAPIError,
    GitHubRepositoryNotFoundError,
    GitHubService,
    github_service,
)
from app.services.repository_architecture_service import (
    PROJECT_TYPE_UNKNOWN,
    RepositoryArchitectureService,
    repository_architecture_service,
)

# Known manifest and build configuration filenames (case-insensitive)
KNOWN_MANIFEST_NAMES: Set[str] = {
    # JavaScript / TypeScript / Frontend
    "package.json",
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    "bun.lockb",
    "tsconfig.json",
    "angular.json",
    # Python
    "requirements.txt",
    "requirements-dev.txt",
    "pyproject.toml",
    "setup.py",
    "setup.cfg",
    "pipfile",
    "pipfile.lock",
    "poetry.lock",
    "environment.yml",
    # Java / JVM
    "pom.xml",
    "build.gradle",
    "build.gradle.kts",
    # Go
    "go.mod",
    "go.sum",
    # Rust
    "cargo.toml",
    "cargo.lock",
    # Ruby
    "gemfile",
    "gemfile.lock",
    # PHP
    "composer.json",
    "composer.lock",
    # C/C++
    "cmakelists.txt",
    "makefile",
    "meson.build",
    # Containers & Orchestration
    "dockerfile",
    "docker-compose.yml",
    "docker-compose.yaml",
}


class GitHubRepositoryInspectionService:
    """
    Dedicated service for deep, factual inspection of individual GitHub repositories.
    """

    def __init__(
        self,
        service: Optional[GitHubService] = None,
        arch_service: Optional[RepositoryArchitectureService] = None,
        concurrency_limit: int = 5,
    ):
        self.github_service = service or github_service
        self.arch_service = arch_service or repository_architecture_service
        self.concurrency_limit = max(1, concurrency_limit)

    def detect_manifest_files(self, file_paths: List[str]) -> List[str]:
        """
        Identify build, dependency, container, and configuration manifests from file paths.

        Args:
            file_paths: List of relative repository file paths.

        Returns:
            Sorted, deduplicated list of manifest paths.
        """
        manifests: Set[str] = set()

        for path in file_paths:
            filename = PurePosixPath(path).name.lower()

            if filename in KNOWN_MANIFEST_NAMES:
                manifests.add(path)
            elif filename.startswith("dockerfile."):
                manifests.add(path)
            elif filename.startswith("requirements") and filename.endswith(".txt"):
                manifests.add(path)
            elif filename.endswith(".csproj") or filename.endswith(".sln"):
                manifests.add(path)
            elif filename.startswith("vite.config.") or filename.startswith("next.config."):
                manifests.add(path)

        return sorted(list(manifests))

    def _resolve_owner_and_repo(
        self, repo_detail: RepositoryAnalysisDetail, default_owner: Optional[str] = None
    ) -> Tuple[str, str]:
        """Extract clean owner and repository name from detail model."""
        full_name = (repo_detail.full_name or "").strip()
        if "/" in full_name:
            parts = full_name.split("/", 1)
            return parts[0].strip(), parts[1].strip()

        owner = (default_owner or "").strip()
        name = (repo_detail.name or "").strip()
        return owner, name

    async def _fetch_tree_safe(
        self, owner: str, repo_name: str, branch: Optional[str]
    ) -> Tuple[List[Dict[str, Any]], bool, Optional[str]]:
        """
        Fetch repository tree with error isolation and truncation detection.

        Returns:
            Tuple of (raw_tree_items, is_truncated, error_message).
        """
        try:
            # Prefer get_repository_tree_data if available for truncation metadata
            if hasattr(self.github_service, "get_repository_tree_data"):
                data = await self.github_service.get_repository_tree_data(
                    owner, repo_name, branch=branch
                )
                if isinstance(data, dict):
                    return data.get("tree", []), bool(data.get("truncated", False)), None
                elif isinstance(data, list):
                    return data, False, None

            # Fallback to get_repository_tree
            tree = await self.github_service.get_repository_tree(
                owner, repo_name, branch=branch
            )
            return tree or [], False, None

        except GitHubRepositoryNotFoundError as exc:
            return [], False, f"Repository or branch not found (404): {str(exc)}"
        except GitHubAPIError as exc:
            return [], False, f"GitHub API error ({exc.status_code}): {str(exc)}"
        except Exception as exc:
            return [], False, f"Unexpected error inspecting repository tree: {str(exc)}"

    async def inspect_repository(
        self,
        repo: Union[RepositoryAnalysisDetail, Dict[str, Any]],
        default_owner: Optional[str] = None,
        raise_on_error: bool = False,
    ) -> RepositoryAnalysisDetail:
        """
        Deeply inspect an individual GitHub repository.

        Args:
            repo: RepositoryAnalysisDetail instance or dict from discovery.
            default_owner: Fallback owner if full_name is unqualified.
            raise_on_error: If True, re-raises fatal API errors instead of isolating.

        Returns:
            Updated RepositoryAnalysisDetail with populated architecture signals,
            project type, manifests, detected languages, and inspection status.
        """
        if isinstance(repo, dict):
            detail = RepositoryAnalysisDetail(**repo)
        else:
            detail = repo.model_copy(deep=True)

        owner, repo_name = self._resolve_owner_and_repo(detail, default_owner)
        if not owner or not repo_name:
            detail.analysis_status = "ERROR"
            detail.is_partial = True
            detail.warnings.append("Could not determine owner and repository name for inspection")
            return detail

        # Determine target branch (fallback to HEAD if missing or empty)
        target_branch = (detail.default_branch or "").strip()
        if not target_branch:
            target_branch = "HEAD"
            detail.warnings.append("Default branch not specified; fell back to 'HEAD'")

        # Fetch tree
        raw_tree, is_truncated, error_msg = await self._fetch_tree_safe(
            owner, repo_name, branch=target_branch
        )

        if error_msg:
            detail.analysis_status = "ERROR"
            detail.is_partial = True
            detail.warnings.append(error_msg)
            if raise_on_error:
                raise GitHubAPIError(error_msg, status_code=500)
            return detail

        # Handle completely empty repository (0 tree items)
        if not raw_tree:
            detail.is_empty = True
            detail.analysis_status = "SUCCESS"
            detail.project_type = PROJECT_TYPE_UNKNOWN
            detail.manifest_files = []
            detail.architecture_signals = []
            detail.warnings.append("Repository is empty (no commits or tree items found)")
            return detail

        # Normalize tree paths into files and directories
        file_paths, dir_paths = self.arch_service.normalize_tree_paths(raw_tree)

        # Detect manifests
        manifests = self.detect_manifest_files(file_paths)
        detail.manifest_files = manifests

        # Detect all languages from file extensions & primary language
        detected_languages = self.arch_service.detect_languages(
            file_paths, detail.primary_language
        )
        detail.languages = detected_languages

        # Extract architectural signals & capabilities
        signals, flags = self.arch_service.extract_architecture_signals(
            file_paths, dir_paths
        )
        detail.architecture_signals = signals

        # Classify deterministic project type
        project_type = self.arch_service.classify_project_type(
            flags, file_paths, dir_paths, detail.primary_language
        )
        detail.project_type = project_type

        # Check truncation state
        if is_truncated:
            detail.tree_truncated = True
            detail.is_partial = True
            detail.analysis_status = "PARTIAL"
            detail.warnings.append("Repository tree was truncated by GitHub API (>100,000 entries)")
        else:
            detail.tree_truncated = False
            detail.is_partial = False
            detail.analysis_status = "SUCCESS"

        return detail

    async def inspect_repositories(
        self,
        repositories: List[RepositoryAnalysisDetail],
        default_owner: Optional[str] = None,
        concurrency_limit: Optional[int] = None,
    ) -> List[RepositoryAnalysisDetail]:
        """
        Inspect multiple repositories with bounded concurrency using asyncio.Semaphore.
        Isolates failures so that one repository's error does not affect others.

        Args:
            repositories: List of RepositoryAnalysisDetail models to inspect.
            default_owner: Fallback repository owner.
            concurrency_limit: Optional custom concurrency ceiling.

        Returns:
            List of deeply inspected RepositoryAnalysisDetail models in original order.
        """
        limit = max(1, concurrency_limit or self.concurrency_limit)
        semaphore = asyncio.Semaphore(limit)

        async def _bounded_inspect(repo_item: RepositoryAnalysisDetail) -> RepositoryAnalysisDetail:
            async with semaphore:
                return await self.inspect_repository(repo_item, default_owner=default_owner)

        tasks = [_bounded_inspect(repo) for repo in repositories]
        return await asyncio.gather(*tasks)


# Singleton instance for route and service consumption
github_repository_inspection_service = GitHubRepositoryInspectionService()
