"""
test_github_account_api.py
--------------------------
Integration and API endpoint tests for the unified GitHub Account Analysis endpoint:
`GET /api/v1/github/{username_or_url}/analysis`

Covers:
1. Successful analysis across input variants (username, @username, full URLs, query param)
2. Response contract integrity (account, repositories[], aggregated_profile)
3. Input validation errors (422)
4. GitHub upstream errors (404, 403, 429, 502, 504, 500)
5. Robustness against individual repository failures (partial, error, empty)
6. Full pipeline orchestration sequence (discovery -> inspection -> evidence -> aggregation)
7. Legacy GitHub route preservation (regression tests)
"""

import sys
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch

# Ensure backend directory is in sys.path
backend_dir = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from fastapi.testclient import TestClient

from app.main import app
from app.schemas.github_account import (
    AccountMetadata,
    AggregatedAccountProfile,
    AggregatedLanguage,
    AggregatedSkill,
    AggregatedTechnology,
    EvidenceSourceSignal,
    EvidenceSummary,
    GitHubAccountAnalysisResponse,
    RepositoryAnalysisDetail,
    RepositoryCoverage,
)
from app.services.github_service import (
    GitHubAPIError,
    GitHubUserNotFoundError,
    InvalidGitHubUsernameError,
)


def _build_dummy_account_analysis(
    login: str = "octocat",
    repo_count: int = 2,
    has_error: bool = False,
    has_empty: bool = False,
) -> GitHubAccountAnalysisResponse:
    """Helper to build a realistic dummy GitHubAccountAnalysisResponse for route testing."""
    account = AccountMetadata(
        login=login,
        name="The Octocat",
        avatar_url="https://avatars.githubusercontent.com/u/583231?v=4",
        html_url=f"https://github.com/{login}",
        public_repos=repo_count,
        followers=1000,
        following=10,
        account_type="User",
        bio="GitHub Mascot",
    )

    repos = []
    # Repo 1: standard success
    repos.append(
        RepositoryAnalysisDetail(
            name="frontend-app",
            full_name=f"{login}/frontend-app",
            html_url=f"https://github.com/{login}/frontend-app",
            primary_language="TypeScript",
            languages=["TypeScript", "CSS"],
            technologies=["React", "TypeScript", "Tailwind CSS"],
            manifest_files=["package.json"],
            project_type="FRONTEND",
            skills=["React", "TypeScript", "Frontend Development"],
            evidence=[
                EvidenceSourceSignal(
                    source_type="DEPENDENCY_MANIFEST",
                    technology="React",
                    path="package.json",
                    strength="STRONG",
                    reason="Found in dependencies",
                )
            ],
            analysis_status="SUCCESS",
        )
    )

    if has_error:
        repos.append(
            RepositoryAnalysisDetail(
                name="broken-repo",
                full_name=f"{login}/broken-repo",
                html_url=f"https://github.com/{login}/broken-repo",
                analysis_status="ERROR",
                warnings=["Repository failed deep inspection: 500 Server Error"],
            )
        )
    elif has_empty:
        repos.append(
            RepositoryAnalysisDetail(
                name="empty-repo",
                full_name=f"{login}/empty-repo",
                html_url=f"https://github.com/{login}/empty-repo",
                is_empty=True,
                analysis_status="SUCCESS",
            )
        )
    elif repo_count > 1:
        repos.append(
            RepositoryAnalysisDetail(
                name="backend-service",
                full_name=f"{login}/backend-service",
                html_url=f"https://github.com/{login}/backend-service",
                primary_language="Python",
                languages=["Python"],
                technologies=["FastAPI", "Python"],
                manifest_files=["requirements.txt"],
                project_type="BACKEND",
                skills=["FastAPI", "Python"],
                evidence=[
                    EvidenceSourceSignal(
                        source_type="DEPENDENCY_MANIFEST",
                        technology="FastAPI",
                        path="requirements.txt",
                        strength="STRONG",
                    )
                ],
                analysis_status="SUCCESS",
            )
        )

    aggregated = AggregatedAccountProfile(
        languages=[
            AggregatedLanguage(name="TypeScript", repository_count=1, percentage=50.0, supporting_repositories=["frontend-app"]),
            AggregatedLanguage(name="Python", repository_count=1, percentage=50.0, supporting_repositories=["backend-service"]),
        ],
        technologies=[
            AggregatedTechnology(name="React", repository_count=1, evidence_count=1, supporting_repositories=["frontend-app"]),
            AggregatedTechnology(name="FastAPI", repository_count=1, evidence_count=1, supporting_repositories=["backend-service"]),
        ],
        skills=[
            AggregatedSkill(
                name="React",
                category="Frameworks & Libraries",
                repository_count=1,
                evidence_count=1,
                evidence_strength="STRONG",
                supporting_repositories=["frontend-app"],
            ),
            AggregatedSkill(
                name="FastAPI",
                category="Frameworks & Libraries",
                repository_count=1,
                evidence_count=1,
                evidence_strength="STRONG",
                supporting_repositories=["backend-service"],
            ),
        ],
        repository_coverage=RepositoryCoverage(
            total_repositories_analyzed=len(repos),
            original_repositories=len(repos),
            active_repositories=len(repos),
            successfully_analyzed_repositories=1 if (has_error or has_empty) else len(repos),
            empty_repositories=1 if has_empty else 0,
            error_repositories=1 if has_error else 0,
        ),
        evidence_summary=EvidenceSummary(
            strong_evidence_count=2,
            total_evidence_signals=2,
            technologies_with_strong_evidence=2,
            technologies_with_evidence=2,
        ),
        total_unique_technologies=2,
        total_unique_skills=2,
    )

    return GitHubAccountAnalysisResponse(
        account=account,
        repositories=repos,
        aggregated_profile=aggregated,
    )


class TestGitHubAccountAPI(unittest.TestCase):
    """Integration test suite for the unified GitHub account analysis endpoint."""

    def setUp(self):
        self.client = TestClient(app)

    # -------------------------------------------------------------------------
    # 1. Successful Analysis & Input Handling
    # -------------------------------------------------------------------------

    @patch("app.api.routes.github.github_account_service.aggregate_account")
    def test_01_api_valid_username_path_success(self, mock_aggregate):
        """GET /api/v1/github/octocat/analysis returns HTTP 200 with full analysis response."""
        mock_aggregate.return_value = _build_dummy_account_analysis("octocat")
        response = self.client.get("/api/v1/github/octocat/analysis")

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["account"]["login"], "octocat")
        self.assertIn("repositories", data)
        self.assertIn("aggregated_profile", data)
        mock_aggregate.assert_called_once_with(username_or_url="octocat", max_pages=10)

    @patch("app.api.routes.github.github_account_service.aggregate_account")
    def test_02_api_at_prefixed_username_success(self, mock_aggregate):
        """GET /api/v1/github/@octocat/analysis returns HTTP 200."""
        mock_aggregate.return_value = _build_dummy_account_analysis("octocat")
        response = self.client.get("/api/v1/github/@octocat/analysis")

        self.assertEqual(response.status_code, 200)
        mock_aggregate.assert_called_once_with(username_or_url="@octocat", max_pages=10)

    @patch("app.api.routes.github.github_account_service.aggregate_account")
    def test_03_api_https_profile_url_success(self, mock_aggregate):
        """GET /api/v1/github/https://github.com/octocat/analysis returns HTTP 200."""
        mock_aggregate.return_value = _build_dummy_account_analysis("octocat")
        response = self.client.get("/api/v1/github/https://github.com/octocat/analysis")

        self.assertEqual(response.status_code, 200)
        mock_aggregate.assert_called_once_with(username_or_url="https://github.com/octocat", max_pages=10)

    @patch("app.api.routes.github.github_account_service.aggregate_account")
    def test_04_api_https_profile_url_trailing_slash_success(self, mock_aggregate):
        """GET /api/v1/github/https://github.com/octocat//analysis returns HTTP 200."""
        mock_aggregate.return_value = _build_dummy_account_analysis("octocat")
        response = self.client.get("/api/v1/github/https://github.com/octocat//analysis")

        self.assertEqual(response.status_code, 200)

    @patch("app.api.routes.github.github_account_service.aggregate_account")
    def test_05_api_query_parameter_variant_success(self, mock_aggregate):
        """GET /api/v1/github/analysis?username=octocat returns HTTP 200."""
        mock_aggregate.return_value = _build_dummy_account_analysis("octocat")
        response = self.client.get("/api/v1/github/analysis?username=octocat")

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["account"]["login"], "octocat")
        mock_aggregate.assert_called_once_with(username_or_url="octocat", max_pages=10)

    @patch("app.api.routes.github.github_account_service.aggregate_account")
    def test_06_api_legacy_prefix_mount_success(self, mock_aggregate):
        """GET /api/github/octocat/analysis is also accessible via legacy prefix."""
        mock_aggregate.return_value = _build_dummy_account_analysis("octocat")
        response = self.client.get("/api/github/octocat/analysis")

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["account"]["login"], "octocat")

    # -------------------------------------------------------------------------
    # 2. Response Contract & Data Integrity
    # -------------------------------------------------------------------------

    @patch("app.api.routes.github.github_account_service.aggregate_account")
    def test_07_api_response_shape_and_metadata(self, mock_aggregate):
        """Response preserves detailed account metadata fields."""
        mock_aggregate.return_value = _build_dummy_account_analysis("octocat")
        response = self.client.get("/api/v1/github/octocat/analysis")

        self.assertEqual(response.status_code, 200)
        acc = response.json()["account"]
        self.assertEqual(acc["login"], "octocat")
        self.assertEqual(acc["name"], "The Octocat")
        self.assertEqual(acc["public_repos"], 2)
        self.assertEqual(acc["followers"], 1000)
        self.assertEqual(acc["following"], 10)
        self.assertEqual(acc["account_type"], "User")
        self.assertEqual(acc["bio"], "GitHub Mascot")

    @patch("app.api.routes.github.github_account_service.aggregate_account")
    def test_08_api_all_repositories_preserved(self, mock_aggregate):
        """Response preserves all repositories in repositories[] with granular details."""
        mock_aggregate.return_value = _build_dummy_account_analysis("octocat", repo_count=2)
        response = self.client.get("/api/v1/github/octocat/analysis")

        repos = response.json()["repositories"]
        self.assertEqual(len(repos), 2)
        repo0 = repos[0]
        self.assertEqual(repo0["name"], "frontend-app")
        self.assertIn("React", repo0["technologies"])
        self.assertIn("package.json", repo0["manifest_files"])
        self.assertEqual(repo0["project_type"], "FRONTEND")
        self.assertIn("React", repo0["skills"])
        self.assertEqual(len(repo0["evidence"]), 1)
        self.assertEqual(repo0["evidence"][0]["strength"], "STRONG")

    @patch("app.api.routes.github.github_account_service.aggregate_account")
    def test_09_api_aggregated_profile_present(self, mock_aggregate):
        """Aggregated technical profile contains languages, technologies, skills, coverage, evidence."""
        mock_aggregate.return_value = _build_dummy_account_analysis("octocat")
        response = self.client.get("/api/v1/github/octocat/analysis")

        agg = response.json()["aggregated_profile"]
        self.assertEqual(len(agg["languages"]), 2)
        self.assertEqual(len(agg["technologies"]), 2)
        self.assertEqual(len(agg["skills"]), 2)
        self.assertEqual(agg["total_unique_technologies"], 2)
        self.assertEqual(agg["total_unique_skills"], 2)
        self.assertEqual(agg["evidence_summary"]["strong_evidence_count"], 2)
        self.assertEqual(agg["repository_coverage"]["total_repositories_analyzed"], 2)

    @patch("app.api.routes.github.github_account_service.aggregate_account")
    def test_10_api_supporting_repositories_intact(self, mock_aggregate):
        """Supporting repositories list in aggregated tech and skills is accurate and intact."""
        mock_aggregate.return_value = _build_dummy_account_analysis("octocat")
        response = self.client.get("/api/v1/github/octocat/analysis")

        techs = response.json()["aggregated_profile"]["technologies"]
        react_tech = [t for t in techs if t["name"] == "React"][0]
        self.assertEqual(react_tech["supporting_repositories"], ["frontend-app"])
        self.assertEqual(react_tech["repository_count"], 1)

    # -------------------------------------------------------------------------
    # 3. Input Validation Errors (HTTP 422)
    # -------------------------------------------------------------------------

    def test_11_api_input_validation_invalid_characters_422(self):
        """Username with invalid special characters returns HTTP 422."""
        response = self.client.get("/api/v1/github/octo$$cat/analysis")
        self.assertEqual(response.status_code, 422)
        self.assertIn("Invalid GitHub username format", response.json()["detail"])

    def test_12_api_input_validation_invalid_host_422(self):
        """Non-GitHub profile URL returns HTTP 422."""
        response = self.client.get("/api/v1/github/https://gitlab.com/octocat/analysis")
        self.assertEqual(response.status_code, 422)
        self.assertIn("URL must be on github.com", response.json()["detail"])

    def test_13_api_input_validation_repository_url_rejected_422(self):
        """Repository URL supplied instead of profile URL returns HTTP 422."""
        response = self.client.get("/api/v1/github/https://github.com/octocat/my-repo/analysis")
        self.assertEqual(response.status_code, 422)
        self.assertIn("Expected a GitHub profile URL", response.json()["detail"])

    def test_14_api_input_validation_reserved_system_path_422(self):
        """Reserved GitHub system keyword returns HTTP 422."""
        response = self.client.get("/api/v1/github/settings/analysis")
        self.assertEqual(response.status_code, 422)
        self.assertIn("reserved GitHub system path", response.json()["detail"])

    # -------------------------------------------------------------------------
    # 4. GitHub Upstream & Server Errors
    # -------------------------------------------------------------------------

    @patch("app.api.routes.github.github_account_service.aggregate_account")
    def test_15_api_error_user_not_found_404(self, mock_aggregate):
        """Non-existent GitHub user returns HTTP 404 with clean message."""
        mock_aggregate.side_effect = GitHubUserNotFoundError("GitHub user 'nonexistent-user' not found")
        response = self.client.get("/api/v1/github/nonexistent-user/analysis")

        self.assertEqual(response.status_code, 404)
        self.assertIn("not found", response.json()["detail"].lower())

    @patch("app.api.routes.github.github_account_service.aggregate_account")
    def test_16_api_error_rate_limited_403(self, mock_aggregate):
        """GitHub rate limit error (403) is mapped directly to HTTP 403."""
        mock_aggregate.side_effect = GitHubAPIError("GitHub API rate limit exceeded", status_code=403)
        response = self.client.get("/api/v1/github/octocat/analysis")

        self.assertEqual(response.status_code, 403)
        self.assertIn("rate limit", response.json()["detail"].lower())

    @patch("app.api.routes.github.github_account_service.aggregate_account")
    def test_17_api_error_rate_limited_429(self, mock_aggregate):
        """GitHub secondary rate limit (429) is mapped directly to HTTP 429."""
        mock_aggregate.side_effect = GitHubAPIError("Too Many Requests", status_code=429)
        response = self.client.get("/api/v1/github/octocat/analysis")

        self.assertEqual(response.status_code, 429)
        self.assertIn("too many requests", response.json()["detail"].lower())

    @patch("app.api.routes.github.github_account_service.aggregate_account")
    def test_18_api_error_upstream_timeout_504(self, mock_aggregate):
        """Upstream timeout error (504) is mapped to HTTP 504."""
        mock_aggregate.side_effect = GitHubAPIError("GitHub request timed out", status_code=504)
        response = self.client.get("/api/v1/github/octocat/analysis")

        self.assertEqual(response.status_code, 504)
        self.assertIn("timed out", response.json()["detail"].lower())

    @patch("app.api.routes.github.github_account_service.aggregate_account")
    def test_19_api_error_network_failure_502(self, mock_aggregate):
        """Upstream network/bad gateway error (502) is mapped to HTTP 502."""
        mock_aggregate.side_effect = GitHubAPIError("Unable to reach GitHub API", status_code=502)
        response = self.client.get("/api/v1/github/octocat/analysis")

        self.assertEqual(response.status_code, 502)
        self.assertIn("unable to reach", response.json()["detail"].lower())

    @patch("app.api.routes.github.github_account_service.aggregate_account")
    def test_20_api_error_unexpected_internal_500(self, mock_aggregate):
        """Unexpected internal exceptions return clean HTTP 500 without leaking stack traces."""
        mock_aggregate.side_effect = RuntimeError("Internal database connection failed with secret token XYZ")
        response = self.client.get("/api/v1/github/octocat/analysis")

        self.assertEqual(response.status_code, 500)
        self.assertNotIn("secret token XYZ", response.json()["detail"])
        self.assertIn("unexpected error occurred", response.json()["detail"].lower())

    # -------------------------------------------------------------------------
    # 5. Partial, Error, and Empty Repository Handling
    # -------------------------------------------------------------------------

    @patch("app.api.routes.github.github_account_service.aggregate_account")
    def test_21_api_repository_error_does_not_break_account(self, mock_aggregate):
        """Account analysis succeeds with 200 even when a repository encounters an error."""
        mock_aggregate.return_value = _build_dummy_account_analysis("octocat", repo_count=2, has_error=True)
        response = self.client.get("/api/v1/github/octocat/analysis")

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data["repositories"]), 2)
        cov = data["aggregated_profile"]["repository_coverage"]
        self.assertEqual(cov["error_repositories"], 1)
        self.assertEqual(cov["successfully_analyzed_repositories"], 1)

    @patch("app.api.routes.github.github_account_service.aggregate_account")
    def test_22_api_empty_repositories_handling(self, mock_aggregate):
        """Account analysis preserves empty repositories in catalog without crashing."""
        mock_aggregate.return_value = _build_dummy_account_analysis("octocat", repo_count=2, has_empty=True)
        response = self.client.get("/api/v1/github/octocat/analysis")

        self.assertEqual(response.status_code, 200)
        data = response.json()
        cov = data["aggregated_profile"]["repository_coverage"]
        self.assertEqual(cov["empty_repositories"], 1)

    @patch("app.api.routes.github.github_account_service.aggregate_account")
    def test_23_api_zero_repositories_account(self, mock_aggregate):
        """Account with 0 public repositories returns HTTP 200 with empty collections."""
        empty_response = GitHubAccountAnalysisResponse(
            account=AccountMetadata(login="newdev", public_repos=0),
            repositories=[],
            aggregated_profile=AggregatedAccountProfile(
                repository_coverage=RepositoryCoverage(total_repositories_analyzed=0)
            ),
        )
        mock_aggregate.return_value = empty_response
        response = self.client.get("/api/v1/github/newdev/analysis")

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data["repositories"]), 0)
        self.assertEqual(len(data["aggregated_profile"]["languages"]), 0)
        self.assertEqual(len(data["aggregated_profile"]["technologies"]), 0)

    # -------------------------------------------------------------------------
    # 6. Service Composition & Pipeline Orchestration Verification
    # -------------------------------------------------------------------------

    @patch("app.services.github_service.github_service.get_user_profile")
    @patch("app.services.github_service.github_service.get_all_user_repositories")
    @patch("app.services.github_service.github_service.get_repository_tree_data")
    @patch("app.services.github_service.github_service.get_repository_file_content")
    def test_24_full_pipeline_orchestration_via_service(
        self,
        mock_file_content,
        mock_tree_data,
        mock_all_repos,
        mock_profile,
    ):
        """
        Verify the complete end-to-end service orchestration:
        discovery -> inspection -> evidence enrichment -> aggregation
        executed from the endpoint without hitting live GitHub API.
        """
        mock_profile.return_value = {
            "login": "octocat",
            "name": "The Octocat",
            "avatar_url": "https://avatars.githubusercontent.com/u/583231?v=4",
            "html_url": "https://github.com/octocat",
            "public_repos": 1,
            "followers": 100,
            "following": 5,
        }
        mock_all_repos.return_value = [
            {
                "name": "web-starter",
                "full_name": "octocat/web-starter",
                "html_url": "https://github.com/octocat/web-starter",
                "default_branch": "main",
                "size": 150,
                "language": "TypeScript",
                "fork": False,
                "archived": False,
                "topics": ["react", "web"],
            }
        ]
        mock_tree_data.return_value = {
            "tree": [
                {"path": "package.json", "type": "blob", "size": 120},
                {"path": "src/App.tsx", "type": "blob", "size": 300},
            ],
            "truncated": False,
        }
        mock_file_content.return_value = (
            '{"name": "web-starter", "dependencies": {"react": "^18.2.0", "typescript": "^5.0.0"}}'
        )

        response = self.client.get("/api/v1/github/octocat/analysis")
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(data["account"]["login"], "octocat")
        self.assertEqual(len(data["repositories"]), 1)

        repo = data["repositories"][0]
        self.assertIn("React", repo["technologies"])
        self.assertIn("package.json", repo["manifest_files"])

        # Aggregated profile check
        profile = data["aggregated_profile"]
        tech_names = [t["name"] for t in profile["technologies"]]
        self.assertIn("React", tech_names)
        self.assertEqual(profile["repository_coverage"]["successfully_analyzed_repositories"], 1)

    # -------------------------------------------------------------------------
    # 7. Regression: Legacy GitHub Routes Preservation
    # -------------------------------------------------------------------------

    @patch("app.api.routes.github.github_service.get_user_profile")
    def test_25_legacy_profile_route_works(self, mock_profile):
        """GET /api/github/{username} continues to work."""
        mock_profile.return_value = {
            "login": "octocat",
            "name": "The Octocat",
            "html_url": "https://github.com/octocat",
            "public_repos": 5,
            "followers": 20,
        }
        response = self.client.get("/api/github/octocat")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["login"], "octocat")

    @patch("app.api.routes.github.github_service.get_user_repositories")
    def test_26_legacy_repos_route_works(self, mock_repos):
        """GET /api/github/{username}/repos continues to work."""
        mock_repos.return_value = [
            {
                "name": "repo-1",
                "full_name": "octocat/repo-1",
                "html_url": "https://github.com/octocat/repo-1",
            }
        ]
        response = self.client.get("/api/github/octocat/repos")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]["name"], "repo-1")

    @patch("app.api.routes.github.github_service.get_user_repositories")
    def test_27_legacy_technologies_route_works(self, mock_repos):
        """GET /api/github/{username}/technologies continues to work."""
        mock_repos.return_value = [
            {
                "name": "repo-1",
                "full_name": "octocat/repo-1",
                "html_url": "https://github.com/octocat/repo-1",
                "language": "Python",
                "topics": ["fastapi"],
            }
        ]
        response = self.client.get("/api/github/octocat/technologies")
        self.assertEqual(response.status_code, 200)
        self.assertIn("technologies", response.json())

    @patch("app.api.routes.github.github_service.get_user_repositories")
    def test_28_legacy_skills_route_works(self, mock_repos):
        """GET /api/github/{username}/skills continues to work."""
        mock_repos.return_value = [
            {
                "name": "repo-1",
                "full_name": "octocat/repo-1",
                "html_url": "https://github.com/octocat/repo-1",
                "language": "Python",
            }
        ]
        response = self.client.get("/api/github/octocat/skills")
        self.assertEqual(response.status_code, 200)
        self.assertIn("categories", response.json())


if __name__ == "__main__":
    unittest.main()
