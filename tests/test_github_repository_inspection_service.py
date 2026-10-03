"""
test_github_repository_inspection_service.py
--------------------------------------------
Unit and integration tests for GitHubRepositoryInspectionService and Task 4 workflow.

Tests cover:
- Basic inspection (tree fetching, manifests, architecture signals, project type, branch targeting)
- Manifest detection (package.json, requirements.txt, pyproject.toml, multi-manifests, missing manifests)
- Repository edge cases (empty repo, truncated tree, missing default branch, large tree, 404, timeout, rate limits)
- Account service integration (independent repos, error isolation, factual signals only, no cross-repo aggregation)
"""

import sys
from pathlib import Path
from unittest.mock import AsyncMock, patch
import pytest

# Ensure backend directory is in sys.path
backend_dir = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from app.schemas.github_account import (
    GitHubAccountAnalysisResponse,
    RepositoryAnalysisDetail,
)
from app.services.github_account_service import GitHubAccountService
from app.services.github_repository_inspection_service import (
    GitHubRepositoryInspectionService,
)
from app.services.github_service import (
    GitHubAPIError,
    GitHubRepositoryNotFoundError,
    GitHubService,
)
from app.services.repository_architecture_service import (
    PROJECT_TYPE_BACKEND,
    PROJECT_TYPE_FULL_STACK,
    PROJECT_TYPE_UNKNOWN,
)


def _make_repo_detail(
    name: str = "demo-repo",
    full_name: str = "octocat/demo-repo",
    default_branch: str = "main",
    primary_language: str = "Python",
    is_fork: bool = False,
    is_archived: bool = False,
    size: int = 100,
) -> RepositoryAnalysisDetail:
    return RepositoryAnalysisDetail(
        name=name,
        full_name=full_name,
        html_url=f"https://github.com/{full_name}",
        default_branch=default_branch,
        primary_language=primary_language,
        is_fork=is_fork,
        is_archived=is_archived,
        is_empty=(size == 0),
    )


class TestBasicInspection:
    """1 to 5: Basic repository inspection functionality."""

    @pytest.mark.anyio
    async def test_01_repository_tree_is_inspected(self):
        """1. Repository tree is fetched and inspected for files and directories."""
        mock_github = AsyncMock(spec=GitHubService)
        mock_github.get_repository_tree_data = AsyncMock(
            return_value={
                "tree": [
                    {"path": "backend/api.py", "type": "blob", "size": 100},
                    {"path": "backend", "type": "tree"},
                ],
                "truncated": False,
            }
        )

        service = GitHubRepositoryInspectionService(service=mock_github)
        repo = _make_repo_detail()

        inspected = await service.inspect_repository(repo)

        mock_github.get_repository_tree_data.assert_called_once_with(
            "octocat", "demo-repo", branch="main"
        )
        assert inspected.analysis_status == "SUCCESS"
        assert not inspected.is_partial
        assert not inspected.tree_truncated

    @pytest.mark.anyio
    async def test_02_manifest_files_are_detected(self):
        """2. Manifest files in tree are detected and saved in manifest_files."""
        mock_github = AsyncMock(spec=GitHubService)
        mock_github.get_repository_tree_data = AsyncMock(
            return_value={
                "tree": [
                    {"path": "requirements.txt", "type": "blob", "size": 50},
                    {"path": "Dockerfile", "type": "blob", "size": 200},
                    {"path": "src/main.py", "type": "blob", "size": 300},
                ],
                "truncated": False,
            }
        )

        service = GitHubRepositoryInspectionService(service=mock_github)
        repo = _make_repo_detail()

        inspected = await service.inspect_repository(repo)

        assert "requirements.txt" in inspected.manifest_files
        assert "Dockerfile" in inspected.manifest_files
        assert "src/main.py" not in inspected.manifest_files

    @pytest.mark.anyio
    async def test_03_architecture_signals_are_populated(self):
        """3. Architecture signals are populated with concrete evidence."""
        mock_github = AsyncMock(spec=GitHubService)
        mock_github.get_repository_tree_data = AsyncMock(
            return_value={
                "tree": [
                    {"path": "backend/server.py", "type": "blob", "size": 150},
                    {"path": "backend", "type": "tree"},
                    {"path": "tests/test_api.py", "type": "blob", "size": 120},
                    {"path": "tests", "type": "tree"},
                ],
                "truncated": False,
            }
        )

        service = GitHubRepositoryInspectionService(service=mock_github)
        repo = _make_repo_detail()

        inspected = await service.inspect_repository(repo)

        signal_types = [s.type for s in inspected.architecture_signals]
        assert "BACKEND" in signal_types
        assert "TESTING" in signal_types

    @pytest.mark.anyio
    async def test_04_project_type_is_populated_from_existing_architecture_service(self):
        """4. Project type is populated using deterministic classification from architecture service."""
        mock_github = AsyncMock(spec=GitHubService)
        mock_github.get_repository_tree_data = AsyncMock(
            return_value={
                "tree": [
                    {"path": "frontend/package.json", "type": "blob", "size": 100},
                    {"path": "frontend/src/App.tsx", "type": "blob", "size": 200},
                    {"path": "frontend", "type": "tree"},
                    {"path": "backend/requirements.txt", "type": "blob", "size": 50},
                    {"path": "backend/app.py", "type": "blob", "size": 250},
                    {"path": "backend", "type": "tree"},
                ],
                "truncated": False,
            }
        )

        service = GitHubRepositoryInspectionService(service=mock_github)
        repo = _make_repo_detail()

        inspected = await service.inspect_repository(repo)

        assert inspected.project_type == PROJECT_TYPE_FULL_STACK

    @pytest.mark.anyio
    async def test_05_default_branch_is_respected(self):
        """5. Specific default branch on the repository is requested."""
        mock_github = AsyncMock(spec=GitHubService)
        mock_github.get_repository_tree_data = AsyncMock(
            return_value={"tree": [], "truncated": False}
        )

        service = GitHubRepositoryInspectionService(service=mock_github)
        repo = _make_repo_detail(default_branch="develop")

        await service.inspect_repository(repo)

        mock_github.get_repository_tree_data.assert_called_once_with(
            "octocat", "demo-repo", branch="develop"
        )


class TestManifestHandling:
    """6 to 10: Manifest detection variations."""

    @pytest.mark.anyio
    async def test_06_package_json_detected(self):
        """6. Root and nested package.json detected."""
        mock_github = AsyncMock(spec=GitHubService)
        mock_github.get_repository_tree_data = AsyncMock(
            return_value={
                "tree": [
                    {"path": "package.json", "type": "blob", "size": 100},
                    {"path": "client/package.json", "type": "blob", "size": 100},
                ],
                "truncated": False,
            }
        )

        service = GitHubRepositoryInspectionService(service=mock_github)
        repo = _make_repo_detail()

        inspected = await service.inspect_repository(repo)

        assert "package.json" in inspected.manifest_files
        assert "client/package.json" in inspected.manifest_files

    @pytest.mark.anyio
    async def test_07_requirements_txt_detected(self):
        """7. Standard and variant requirements.txt detected."""
        mock_github = AsyncMock(spec=GitHubService)
        mock_github.get_repository_tree_data = AsyncMock(
            return_value={
                "tree": [
                    {"path": "requirements.txt", "type": "blob", "size": 50},
                    {"path": "requirements-dev.txt", "type": "blob", "size": 40},
                ],
                "truncated": False,
            }
        )

        service = GitHubRepositoryInspectionService(service=mock_github)
        repo = _make_repo_detail()

        inspected = await service.inspect_repository(repo)

        assert "requirements.txt" in inspected.manifest_files
        assert "requirements-dev.txt" in inspected.manifest_files

    @pytest.mark.anyio
    async def test_08_pyproject_toml_detected(self):
        """8. pyproject.toml detected."""
        mock_github = AsyncMock(spec=GitHubService)
        mock_github.get_repository_tree_data = AsyncMock(
            return_value={
                "tree": [
                    {"path": "pyproject.toml", "type": "blob", "size": 150},
                ],
                "truncated": False,
            }
        )

        service = GitHubRepositoryInspectionService(service=mock_github)
        repo = _make_repo_detail()

        inspected = await service.inspect_repository(repo)

        assert "pyproject.toml" in inspected.manifest_files

    @pytest.mark.anyio
    async def test_09_multiple_manifests_are_preserved(self):
        """9. Multiple diverse manifests (npm, python, docker, rust) preserved together."""
        mock_github = AsyncMock(spec=GitHubService)
        mock_github.get_repository_tree_data = AsyncMock(
            return_value={
                "tree": [
                    {"path": "package.json", "type": "blob", "size": 100},
                    {"path": "requirements.txt", "type": "blob", "size": 50},
                    {"path": "Cargo.toml", "type": "blob", "size": 80},
                    {"path": "docker-compose.yml", "type": "blob", "size": 200},
                    {"path": "tsconfig.json", "type": "blob", "size": 120},
                ],
                "truncated": False,
            }
        )

        service = GitHubRepositoryInspectionService(service=mock_github)
        repo = _make_repo_detail()

        inspected = await service.inspect_repository(repo)

        assert len(inspected.manifest_files) == 5
        assert "Cargo.toml" in inspected.manifest_files
        assert "docker-compose.yml" in inspected.manifest_files

    @pytest.mark.anyio
    async def test_10_missing_manifests_do_not_fail_analysis(self):
        """10. Repositories without standard manifests succeed gracefully."""
        mock_github = AsyncMock(spec=GitHubService)
        mock_github.get_repository_tree_data = AsyncMock(
            return_value={
                "tree": [
                    {"path": "src/script.py", "type": "blob", "size": 150},
                    {"path": "README.md", "type": "blob", "size": 50},
                ],
                "truncated": False,
            }
        )

        service = GitHubRepositoryInspectionService(service=mock_github)
        repo = _make_repo_detail()

        inspected = await service.inspect_repository(repo)

        assert inspected.analysis_status == "SUCCESS"
        assert inspected.manifest_files == []
        assert "Python" in inspected.languages


class TestRepositoryEdgeCases:
    """11 to 18: Repository edge cases and network fault handling."""

    @pytest.mark.anyio
    async def test_11_empty_repository(self):
        """11. Completely empty repository (0 files or 409) does not break analysis."""
        mock_github = AsyncMock(spec=GitHubService)
        mock_github.get_repository_tree_data = AsyncMock(
            return_value={"tree": [], "truncated": False}
        )

        service = GitHubRepositoryInspectionService(service=mock_github)
        repo = _make_repo_detail()

        inspected = await service.inspect_repository(repo)

        assert inspected.is_empty is True
        assert inspected.analysis_status == "SUCCESS"
        assert inspected.manifest_files == []
        assert inspected.architecture_signals == []
        assert inspected.project_type == PROJECT_TYPE_UNKNOWN
        assert any("empty" in w.lower() for w in inspected.warnings)

    @pytest.mark.anyio
    async def test_12_repository_with_no_detected_manifests(self):
        """12. Repositories with files but zero manifests produce empty manifest_files."""
        mock_github = AsyncMock(spec=GitHubService)
        mock_github.get_repository_tree_data = AsyncMock(
            return_value={
                "tree": [
                    {"path": "notes.txt", "type": "blob", "size": 20},
                ],
                "truncated": False,
            }
        )

        service = GitHubRepositoryInspectionService(service=mock_github)
        repo = _make_repo_detail()

        inspected = await service.inspect_repository(repo)

        assert inspected.manifest_files == []
        assert inspected.analysis_status == "SUCCESS"

    @pytest.mark.anyio
    async def test_13_truncated_tree(self):
        """13. Truncated tree response sets tree_truncated=True, is_partial=True, status=PARTIAL."""
        mock_github = AsyncMock(spec=GitHubService)
        mock_github.get_repository_tree_data = AsyncMock(
            return_value={
                "tree": [
                    {"path": "package.json", "type": "blob", "size": 100},
                    {"path": "src/index.ts", "type": "blob", "size": 500},
                ],
                "truncated": True,
            }
        )

        service = GitHubRepositoryInspectionService(service=mock_github)
        repo = _make_repo_detail()

        inspected = await service.inspect_repository(repo)

        assert inspected.tree_truncated is True
        assert inspected.is_partial is True
        assert inspected.analysis_status == "PARTIAL"
        assert any("truncated" in w.lower() for w in inspected.warnings)
        # Verify available files were still analyzed
        assert "package.json" in inspected.manifest_files

    @pytest.mark.anyio
    async def test_14_missing_default_branch(self):
        """14. Missing or empty default branch falls back to 'HEAD' without failing."""
        mock_github = AsyncMock(spec=GitHubService)
        mock_github.get_repository_tree_data = AsyncMock(
            return_value={
                "tree": [{"path": "main.go", "type": "blob", "size": 100}],
                "truncated": False,
            }
        )

        service = GitHubRepositoryInspectionService(service=mock_github)
        repo = _make_repo_detail()
        repo.default_branch = None

        inspected = await service.inspect_repository(repo)

        mock_github.get_repository_tree_data.assert_called_once_with(
            "octocat", "demo-repo", branch="HEAD"
        )
        assert inspected.analysis_status == "SUCCESS"
        assert any("HEAD" in w for w in inspected.warnings)

    @pytest.mark.anyio
    async def test_15_large_repository_tree_response(self):
        """15. Large tree responses (1,000+ files) are normalized and analyzed without crash."""
        large_tree = [
            {"path": f"src/module_{i}/file_{j}.py", "type": "blob", "size": 100}
            for i in range(20)
            for j in range(50)
        ]
        large_tree.append({"path": "requirements.txt", "type": "blob", "size": 50})

        mock_github = AsyncMock(spec=GitHubService)
        mock_github.get_repository_tree_data = AsyncMock(
            return_value={"tree": large_tree, "truncated": False}
        )

        service = GitHubRepositoryInspectionService(service=mock_github)
        repo = _make_repo_detail()

        inspected = await service.inspect_repository(repo)

        assert inspected.analysis_status == "SUCCESS"
        assert "requirements.txt" in inspected.manifest_files
        assert "Python" in inspected.languages

    @pytest.mark.anyio
    async def test_16_404_repository_inspection_failure(self):
        """16. 404 repository not found isolates failure into ERROR status with warning."""
        mock_github = AsyncMock(spec=GitHubService)
        mock_github.get_repository_tree_data = AsyncMock(
            side_effect=GitHubRepositoryNotFoundError("Repo not found (404)")
        )

        service = GitHubRepositoryInspectionService(service=mock_github)
        repo = _make_repo_detail()

        inspected = await service.inspect_repository(repo)

        assert inspected.analysis_status == "ERROR"
        assert inspected.is_partial is True
        assert any("404" in w for w in inspected.warnings)

    @pytest.mark.anyio
    async def test_17_timeout_network_failure(self):
        """17. Timeout/network error isolates failure into ERROR status with warning."""
        mock_github = AsyncMock(spec=GitHubService)
        mock_github.get_repository_tree_data = AsyncMock(
            side_effect=GitHubAPIError("GitHub API request timed out", status_code=504)
        )

        service = GitHubRepositoryInspectionService(service=mock_github)
        repo = _make_repo_detail()

        inspected = await service.inspect_repository(repo)

        assert inspected.analysis_status == "ERROR"
        assert inspected.is_partial is True
        assert any("timed out" in w.lower() for w in inspected.warnings)

    @pytest.mark.anyio
    async def test_18_rate_limit_failure(self):
        """18. Rate limit 403 error isolates failure into ERROR status with warning."""
        mock_github = AsyncMock(spec=GitHubService)
        mock_github.get_repository_tree_data = AsyncMock(
            side_effect=GitHubAPIError("Rate limit exceeded", status_code=403)
        )

        service = GitHubRepositoryInspectionService(service=mock_github)
        repo = _make_repo_detail()

        inspected = await service.inspect_repository(repo)

        assert inspected.analysis_status == "ERROR"
        assert inspected.is_partial is True
        assert any("403" in w for w in inspected.warnings)


class TestAccountIntegration:
    """19 to 22: Integration with account-level orchestration and scope boundaries."""

    @pytest.mark.anyio
    async def test_19_multiple_repositories_remain_independent(self):
        """19. Multiple repositories inspected in batch retain distinct factual details."""
        mock_github = AsyncMock(spec=GitHubService)

        async def _tree_side_effect(owner, repo, branch="main"):
            if repo == "frontend-app":
                return {
                    "tree": [
                        {"path": "package.json", "type": "blob", "size": 100},
                        {"path": "src/App.tsx", "type": "blob", "size": 200},
                        {"path": "src", "type": "tree"},
                    ],
                    "truncated": False,
                }
            else:
                return {
                    "tree": [
                        {"path": "requirements.txt", "type": "blob", "size": 50},
                        {"path": "app/main.py", "type": "blob", "size": 150},
                        {"path": "app", "type": "tree"},
                    ],
                    "truncated": False,
                }

        mock_github.get_repository_tree_data = AsyncMock(side_effect=_tree_side_effect)

        service = GitHubRepositoryInspectionService(service=mock_github)
        repo1 = _make_repo_detail("frontend-app", "octocat/frontend-app", primary_language="TypeScript")
        repo2 = _make_repo_detail("backend-api", "octocat/backend-api", primary_language="Python")

        results = await service.inspect_repositories([repo1, repo2])

        assert len(results) == 2
        assert results[0].name == "frontend-app"
        assert "package.json" in results[0].manifest_files
        assert "requirements.txt" not in results[0].manifest_files

        assert results[1].name == "backend-api"
        assert "requirements.txt" in results[1].manifest_files
        assert "package.json" not in results[1].manifest_files

    @pytest.mark.anyio
    async def test_20_one_repository_failure_does_not_remove_other_repositories(self):
        """20. When one repository fails with 404, valid repositories succeed and all remain in catalog."""
        mock_github = AsyncMock(spec=GitHubService)

        async def _tree_side_effect(owner, repo, branch="main"):
            if repo == "broken-repo":
                raise GitHubRepositoryNotFoundError("Repository not found")
            return {
                "tree": [{"path": "pom.xml", "type": "blob", "size": 200}],
                "truncated": False,
            }

        mock_github.get_repository_tree_data = AsyncMock(side_effect=_tree_side_effect)

        service = GitHubRepositoryInspectionService(service=mock_github)
        repo_good = _make_repo_detail("good-repo", "octocat/good-repo")
        repo_bad = _make_repo_detail("broken-repo", "octocat/broken-repo")

        results = await service.inspect_repositories([repo_good, repo_bad])

        assert len(results) == 2
        assert results[0].analysis_status == "SUCCESS"
        assert "pom.xml" in results[0].manifest_files

        assert results[1].analysis_status == "ERROR"
        assert results[1].is_partial is True

    @pytest.mark.anyio
    async def test_21_deep_analysis_fields_are_populated_only_from_actual_inspection(self):
        """21. Inspecting via inspect_account populates manifests and architecture without fabricating technologies/skills."""
        mock_github = AsyncMock(spec=GitHubService)
        mock_github.get_user_profile = AsyncMock(
            return_value={"login": "octocat", "name": "The Octocat", "public_repos": 1}
        )
        mock_github.get_all_user_repositories = AsyncMock(
            return_value=[
                {
                    "name": "api-service",
                    "full_name": "octocat/api-service",
                    "html_url": "https://github.com/octocat/api-service",
                    "default_branch": "main",
                    "language": "Python",
                    "size": 100,
                }
            ]
        )
        mock_github.get_repository_tree_data = AsyncMock(
            return_value={
                "tree": [
                    {"path": "requirements.txt", "type": "blob", "size": 50},
                    {"path": "backend/api.py", "type": "blob", "size": 100},
                    {"path": "backend", "type": "tree"},
                ],
                "truncated": False,
            }
        )

        account_service = GitHubAccountService(
            service=mock_github,
            inspection_service=GitHubRepositoryInspectionService(service=mock_github),
        )

        response = await account_service.inspect_account("octocat")

        assert isinstance(response, GitHubAccountAnalysisResponse)
        assert len(response.repositories) == 1
        repo = response.repositories[0]

        # Factual inspection populated
        assert repo.manifest_files == ["requirements.txt"]
        assert len(repo.architecture_signals) > 0
        assert repo.project_type == PROJECT_TYPE_BACKEND

        # Scope restriction: per-repository extracted technologies/skills remain empty for Task 5
        assert repo.technologies == []
        assert repo.skills == []
        assert repo.evidence == []

    @pytest.mark.anyio
    async def test_22_no_cross_repository_aggregation_occurs(self):
        """22. In Task 4, account-level aggregated_profile technologies and skills remain empty."""
        mock_github = AsyncMock(spec=GitHubService)
        mock_github.get_user_profile = AsyncMock(
            return_value={"login": "octocat", "public_repos": 1}
        )
        mock_github.get_all_user_repositories = AsyncMock(
            return_value=[
                {
                    "name": "fullstack-repo",
                    "full_name": "octocat/fullstack-repo",
                    "html_url": "https://github.com/octocat/fullstack-repo",
                    "default_branch": "main",
                    "language": "JavaScript",
                    "size": 200,
                }
            ]
        )
        mock_github.get_repository_tree_data = AsyncMock(
            return_value={
                "tree": [
                    {"path": "package.json", "type": "blob", "size": 100},
                ],
                "truncated": False,
            }
        )

        account_service = GitHubAccountService(
            service=mock_github,
            inspection_service=GitHubRepositoryInspectionService(service=mock_github),
        )

        response = await account_service.inspect_account("octocat")

        # Explicitly verify cross-repo aggregation did NOT occur
        assert response.aggregated_profile.technologies == []
        assert response.aggregated_profile.skills == []
        assert response.aggregated_profile.total_unique_technologies == 0
        assert response.aggregated_profile.total_unique_skills == 0
        # But repository coverage shows successful analysis
        assert response.aggregated_profile.repository_coverage.successfully_analyzed_repositories == 1
