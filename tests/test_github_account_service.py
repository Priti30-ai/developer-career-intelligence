"""
test_github_account_service.py
------------------------------
Unit tests for GitHub Account Discovery Service:
1. Account discovery with valid handles and profile URLs
2. Individual repository metadata preservation (fork, archived, empty, languages)
3. Multi-page repository pagination and deduplication
4. Error handling (User not found 404, Rate limited 403, Timeout 504, Invalid format)
5. Strict schema conformance and verification that deep-analysis fields remain empty
"""

import sys
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch

# Ensure backend directory is in sys.path
backend_dir = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from app.schemas.github_account import GitHubAccountAnalysisResponse
from app.services.github_account_service import (
    GitHubAccountService,
    github_account_service,
)
from app.services.github_service import (
    GitHubAPIError,
    GitHubService,
    GitHubUserNotFoundError,
    InvalidGitHubUsernameError,
)

MOCK_PROFILE = {
    "login": "octocat",
    "name": "The Octocat",
    "bio": "GitHub mascot and developer",
    "avatar_url": "https://avatars.githubusercontent.com/u/583231?v=4",
    "html_url": "https://github.com/octocat",
    "public_repos": 3,
    "followers": 15000,
    "following": 5,
    "account_type": "User",
    "company": "@github",
    "location": "San Francisco",
    "blog": "https://github.blog",
    "email": "octocat@github.com",
    "twitter_username": "octocat",
    "created_at": "2011-01-25T18:44:36Z",
    "updated_at": "2024-01-01T12:00:00Z",
}

MOCK_REPOS_PAGE_1 = [
    {
        "name": "Hello-World",
        "full_name": "octocat/Hello-World",
        "description": "My first repo",
        "html_url": "https://github.com/octocat/Hello-World",
        "language": "Python",
        "stargazers_count": 2500,
        "forks_count": 1200,
        "watchers_count": 2500,
        "default_branch": "master",
        "topics": ["tutorial", "beginner"],
        "created_at": "2011-01-26T19:01:12Z",
        "updated_at": "2024-01-02T10:00:00Z",
        "pushed_at": "2024-01-02T09:00:00Z",
        "private": False,
        "fork": False,
        "archived": False,
        "size": 120,
    },
    {
        "name": "Spoon-Knife",
        "full_name": "octocat/Spoon-Knife",
        "description": "This repo is for forking",
        "html_url": "https://github.com/octocat/Spoon-Knife",
        "language": "HTML",
        "stargazers_count": 12000,
        "forks_count": 140000,
        "watchers_count": 12000,
        "default_branch": "main",
        "topics": [],
        "created_at": "2011-03-05T01:42:24Z",
        "updated_at": "2024-01-03T10:00:00Z",
        "pushed_at": "2024-01-03T09:00:00Z",
        "private": False,
        "fork": True,  # Forked repository
        "archived": False,
        "size": 85,
    },
]

MOCK_REPOS_PAGE_2 = [
    {
        "name": "old-archive",
        "full_name": "octocat/old-archive",
        "description": "Historical repository",
        "html_url": "https://github.com/octocat/old-archive",
        "language": None,  # No primary language
        "stargazers_count": 5,
        "forks_count": 1,
        "watchers_count": 5,
        "default_branch": "main",
        "topics": ["archive"],
        "created_at": "2012-05-10T11:00:00Z",
        "updated_at": "2015-01-01T00:00:00Z",
        "pushed_at": "2015-01-01T00:00:00Z",
        "private": False,
        "fork": False,
        "archived": True,  # Archived repository
        "size": 0,  # Empty repository
    }
]


class TestGitHubAccountServiceDiscovery(unittest.IsolatedAsyncioTestCase):
    """Asynchronous unit tests for account and repository discovery."""

    def setUp(self):
        self.mock_github = AsyncMock(spec=GitHubService)
        self.service = GitHubAccountService(service=self.mock_github)

    async def test_01_valid_username_discovery(self):
        """Valid username returns fully mapped AccountMetadata."""
        self.mock_github.get_user_profile.return_value = MOCK_PROFILE
        self.mock_github.get_all_user_repositories.return_value = MOCK_REPOS_PAGE_1

        response = await self.service.discover_account("octocat")

        self.assertIsInstance(response, GitHubAccountAnalysisResponse)
        self.assertEqual(response.account.login, "octocat")
        self.assertEqual(response.account.name, "The Octocat")
        self.assertEqual(response.account.company, "@github")
        self.assertEqual(response.account.public_repos, 3)
        self.assertEqual(response.account.followers, 15000)

    async def test_02_profile_url_normalizes_to_same_account(self):
        """Passing a full profile URL resolves to the canonical username."""
        self.mock_github.get_user_profile.return_value = MOCK_PROFILE
        self.mock_github.get_all_user_repositories.return_value = []

        response = await self.service.discover_account("https://github.com/octocat/")

        self.mock_github.get_user_profile.assert_awaited_once_with("octocat")
        self.assertEqual(response.account.login, "octocat")

    async def test_03_repository_list_preserved(self):
        """Repository list is completely preserved in the response."""
        self.mock_github.get_user_profile.return_value = MOCK_PROFILE
        self.mock_github.get_all_user_repositories.return_value = MOCK_REPOS_PAGE_1

        response = await self.service.discover_account("octocat")

        self.assertEqual(len(response.repositories), 2)
        repo_names = [r.name for r in response.repositories]
        self.assertIn("Hello-World", repo_names)
        self.assertIn("Spoon-Knife", repo_names)

    async def test_04_multiple_repositories_remain_separate(self):
        """Each repository maintains distinct and isolated metadata."""
        self.mock_github.get_user_profile.return_value = MOCK_PROFILE
        self.mock_github.get_all_user_repositories.return_value = MOCK_REPOS_PAGE_1

        response = await self.service.discover_account("octocat")

        repo_1 = response.get_repository("Hello-World")
        repo_2 = response.get_repository("Spoon-Knife")

        self.assertIsNotNone(repo_1)
        self.assertIsNotNone(repo_2)
        self.assertEqual(repo_1.primary_language, "Python")
        self.assertEqual(repo_2.primary_language, "HTML")
        self.assertEqual(repo_1.default_branch, "master")
        self.assertEqual(repo_2.default_branch, "main")

    async def test_05_fork_flags_preserved(self):
        """Fork status is accurately preserved on repository objects."""
        self.mock_github.get_user_profile.return_value = MOCK_PROFILE
        self.mock_github.get_all_user_repositories.return_value = MOCK_REPOS_PAGE_1

        response = await self.service.discover_account("octocat")

        repo_1 = response.get_repository("Hello-World")
        repo_2 = response.get_repository("Spoon-Knife")

        self.assertFalse(repo_1.is_fork)
        self.assertTrue(repo_2.is_fork)
        self.assertEqual(response.aggregated_profile.repository_coverage.forked_repositories, 1)
        self.assertEqual(response.aggregated_profile.repository_coverage.original_repositories, 1)

    async def test_06_archived_flags_preserved(self):
        """Archived flag is preserved on read-only repositories."""
        self.mock_github.get_user_profile.return_value = MOCK_PROFILE
        self.mock_github.get_all_user_repositories.return_value = MOCK_REPOS_PAGE_2

        response = await self.service.discover_account("octocat")

        repo = response.get_repository("old-archive")
        self.assertTrue(repo.is_archived)
        self.assertEqual(response.aggregated_profile.repository_coverage.archived_repositories, 1)
        self.assertEqual(response.aggregated_profile.repository_coverage.active_repositories, 0)

    async def test_07_empty_and_no_language_repository_handling(self):
        """Empty repositories or repositories without declared languages do not break discovery."""
        self.mock_github.get_user_profile.return_value = MOCK_PROFILE
        self.mock_github.get_all_user_repositories.return_value = MOCK_REPOS_PAGE_2

        response = await self.service.discover_account("octocat")

        repo = response.get_repository("old-archive")
        self.assertIsNone(repo.primary_language)
        self.assertEqual(repo.languages, [])
        self.assertTrue(repo.is_empty)
        self.assertEqual(response.aggregated_profile.repository_coverage.empty_repositories, 1)


class TestGitHubAccountServicePagination(unittest.IsolatedAsyncioTestCase):
    """Tests for multi-page repository pagination in GitHubService."""

    async def test_08_pagination_combines_pages_correctly(self):
        """get_all_user_repositories correctly requests successive pages and concatenates results."""
        real_service = GitHubService()

        with patch.object(real_service, "get_user_repositories", new_callable=AsyncMock) as mock_get_page:
            # Page 1 returns 2 items (per_page=2), Page 2 returns 1 item (< per_page)
            mock_get_page.side_effect = [
                MOCK_REPOS_PAGE_1,  # Page 1 (2 items)
                MOCK_REPOS_PAGE_2,  # Page 2 (1 item, partial page)
            ]

            results = await real_service.get_all_user_repositories("octocat", max_pages=5, per_page=2)

            self.assertEqual(len(results), 3)
            self.assertEqual(results[0]["name"], "Hello-World")
            self.assertEqual(results[1]["name"], "Spoon-Knife")
            self.assertEqual(results[2]["name"], "old-archive")
            # Stops at page 2 because len(page_repos) < per_page
            self.assertEqual(mock_get_page.call_count, 2)

    async def test_09_pagination_stops_on_partial_page(self):
        """Pagination terminates early when a page has fewer items than per_page."""
        real_service = GitHubService()

        with patch.object(real_service, "get_user_repositories", new_callable=AsyncMock) as mock_get_page:
            # Page 1 returns 2 items when per_page=100 -> must stop immediately
            mock_get_page.return_value = MOCK_REPOS_PAGE_1

            results = await real_service.get_all_user_repositories("octocat", max_pages=5, per_page=100)

            self.assertEqual(len(results), 2)
            # Exactly 1 page request made since len(page_repos) < per_page
            self.assertEqual(mock_get_page.call_count, 1)

    async def test_10_pagination_deduplicates_by_full_name(self):
        """Duplicate repositories returned across pages are safely deduplicated."""
        real_service = GitHubService()

        with patch.object(real_service, "get_user_repositories", new_callable=AsyncMock) as mock_get_page:
            # Simulated duplicate repo appearing on both pages
            mock_get_page.side_effect = [
                MOCK_REPOS_PAGE_1,
                MOCK_REPOS_PAGE_1,  # Duplicate page
            ]

            results = await real_service.get_all_user_repositories("octocat", max_pages=2, per_page=2)

            self.assertEqual(len(results), 2)
            self.assertEqual([r["name"] for r in results], ["Hello-World", "Spoon-Knife"])


class TestGitHubAccountServiceErrors(unittest.IsolatedAsyncioTestCase):
    """Tests for error handling during account discovery."""

    def setUp(self):
        self.mock_github = AsyncMock(spec=GitHubService)
        self.service = GitHubAccountService(service=self.mock_github)

    async def test_11_github_404_raises_user_not_found(self):
        """GitHub 404 response raises GitHubUserNotFoundError."""
        self.mock_github.get_user_profile.side_effect = GitHubUserNotFoundError("GitHub user 'ghost' not found")

        with self.assertRaises(GitHubUserNotFoundError) as ctx:
            await self.service.discover_account("ghost")

        self.assertIn("not found", str(ctx.exception).lower())

    async def test_12_github_rate_limited_raises_api_error(self):
        """GitHub 403 rate limit response raises GitHubAPIError with status 403."""
        self.mock_github.get_user_profile.side_effect = GitHubAPIError("Rate limit exceeded", status_code=403)

        with self.assertRaises(GitHubAPIError) as ctx:
            await self.service.discover_account("octocat")

        self.assertEqual(ctx.exception.status_code, 403)

    async def test_13_github_timeout_raises_api_error(self):
        """Network timeout raises GitHubAPIError with status 504."""
        self.mock_github.get_user_profile.side_effect = GitHubAPIError("Gateway timeout", status_code=504)

        with self.assertRaises(GitHubAPIError) as ctx:
            await self.service.discover_account("octocat")

        self.assertEqual(ctx.exception.status_code, 504)

    async def test_14_invalid_username_raises_validation_error(self):
        """Invalid username format raises InvalidGitHubUsernameError before network call."""
        with self.assertRaises(InvalidGitHubUsernameError):
            await self.service.discover_account("invalid$$user")

        with self.assertRaises(InvalidGitHubUsernameError):
            await self.service.discover_account("https://github.com/settings")

        self.mock_github.get_user_profile.assert_not_called()


class TestGitHubAccountServiceSchemaIntegrity(unittest.IsolatedAsyncioTestCase):
    """Tests verifying schema integrity and that deep-analysis fields remain explicitly unanalyzed."""

    def setUp(self):
        self.mock_github = AsyncMock(spec=GitHubService)
        self.service = GitHubAccountService(service=self.mock_github)

    async def test_15_response_conforms_to_schema(self):
        """Response validates successfully against GitHubAccountAnalysisResponse."""
        self.mock_github.get_user_profile.return_value = MOCK_PROFILE
        self.mock_github.get_all_user_repositories.return_value = MOCK_REPOS_PAGE_1 + MOCK_REPOS_PAGE_2

        response = await self.service.discover_account("octocat")

        self.assertIsInstance(response, GitHubAccountAnalysisResponse)
        self.assertEqual(len(response.repositories), 3)
        self.assertEqual(response.aggregated_profile.repository_coverage.total_repositories_analyzed, 3)

    async def test_16_account_metadata_mapping_accuracy(self):
        """Account metadata is mapped accurately without data loss."""
        self.mock_github.get_user_profile.return_value = MOCK_PROFILE
        self.mock_github.get_all_user_repositories.return_value = []

        response = await self.service.discover_account("octocat")

        acc = response.account
        self.assertEqual(acc.login, "octocat")
        self.assertEqual(acc.name, "The Octocat")
        self.assertEqual(acc.bio, "GitHub mascot and developer")
        self.assertEqual(acc.email, "octocat@github.com")
        self.assertEqual(acc.location, "San Francisco")
        self.assertEqual(acc.blog, "https://github.blog")
        self.assertEqual(acc.twitter_username, "octocat")

    async def test_17_repository_metadata_mapping_accuracy(self):
        """Discovered repository metadata attributes are mapped accurately."""
        self.mock_github.get_user_profile.return_value = MOCK_PROFILE
        self.mock_github.get_all_user_repositories.return_value = MOCK_REPOS_PAGE_1

        response = await self.service.discover_account("octocat")
        repo = response.get_repository("Hello-World")

        self.assertEqual(repo.name, "Hello-World")
        self.assertEqual(repo.full_name, "octocat/Hello-World")
        self.assertEqual(repo.description, "My first repo")
        self.assertEqual(repo.html_url, "https://github.com/octocat/Hello-World")
        self.assertEqual(repo.stargazers_count, 2500)
        self.assertEqual(repo.forks_count, 1200)
        self.assertEqual(repo.watchers_count, 2500)
        self.assertEqual(repo.default_branch, "master")
        self.assertEqual(repo.topics, ["tutorial", "beginner"])
        self.assertFalse(repo.is_fork)
        self.assertFalse(repo.is_archived)

    async def test_18_deep_analysis_fields_remain_empty(self):
        """Crucial requirement: Deep analysis fields must remain empty during discovery."""
        self.mock_github.get_user_profile.return_value = MOCK_PROFILE
        self.mock_github.get_all_user_repositories.return_value = MOCK_REPOS_PAGE_1

        response = await self.service.discover_account("octocat")

        for repo in response.repositories:
            # Technologies, skills, manifests, architecture signals, and evidence must be empty
            self.assertEqual(repo.technologies, [])
            self.assertEqual(repo.skills, [])
            self.assertEqual(repo.manifest_files, [])
            self.assertEqual(repo.architecture_signals, [])
            self.assertEqual(repo.evidence, [])
            self.assertIsNone(repo.project_type)
            self.assertEqual(repo.analysis_status, "SUCCESS")

        # Aggregated technologies and skills must also be empty at discovery stage
        self.assertEqual(response.aggregated_profile.technologies, [])
        self.assertEqual(response.aggregated_profile.skills, [])
        self.assertEqual(response.aggregated_profile.total_unique_technologies, 0)
        self.assertEqual(response.aggregated_profile.total_unique_skills, 0)
        self.assertEqual(response.aggregated_profile.evidence_summary.total_evidence_signals, 0)


if __name__ == "__main__":
    unittest.main()
