"""
test_github.py
--------------
Unit and integration tests for GitHub Integration Foundation:
1. Username / Profile URL normalization (valid & invalid cases)
2. Optional GITHUB_TOKEN header generation
3. Rate-limit header recording
4. API route handling and error responses
"""

import sys
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch

# Ensure backend directory is in sys.path
backend_dir = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

import httpx
from fastapi.testclient import TestClient

from app.core.config import Settings, settings
from app.main import app
from app.services.github_service import (
    GitHubAPIError,
    GitHubService,
    GitHubUserNotFoundError,
    InvalidGitHubUsernameError,
    normalize_github_username,
)


class TestGitHubUsernameNormalization(unittest.TestCase):
    """Unit tests for GitHub username and profile URL normalization."""

    def test_01_plain_username(self):
        """Standard plain alphanumeric handle."""
        self.assertEqual(normalize_github_username("octocat"), "octocat")
        self.assertEqual(normalize_github_username("torvalds"), "torvalds")
        self.assertEqual(normalize_github_username("user-name-1"), "user-name-1")
        self.assertEqual(normalize_github_username("a"), "a")

    def test_02_at_prefixed_handle(self):
        """Handles prefixed with '@'."""
        self.assertEqual(normalize_github_username("@octocat"), "octocat")
        self.assertEqual(normalize_github_username("@torvalds"), "torvalds")

    def test_03_https_profile_url(self):
        """Full HTTPS profile URLs."""
        self.assertEqual(normalize_github_username("https://github.com/octocat"), "octocat")
        self.assertEqual(normalize_github_username("https://www.github.com/octocat"), "octocat")

    def test_04_https_profile_url_with_trailing_slash(self):
        """Full HTTPS profile URLs with trailing slashes."""
        self.assertEqual(normalize_github_username("https://github.com/octocat/"), "octocat")

    def test_05_http_profile_url_with_trailing_slash(self):
        """HTTP profile URLs with trailing slashes."""
        self.assertEqual(normalize_github_username("http://github.com/octocat/"), "octocat")
        self.assertEqual(normalize_github_username("http://github.com/octocat"), "octocat")

    def test_06_domain_prefixed_url(self):
        """Domain-prefixed URLs without protocol scheme."""
        self.assertEqual(normalize_github_username("github.com/octocat"), "octocat")
        self.assertEqual(normalize_github_username("www.github.com/octocat/"), "octocat")

    def test_07_url_with_query_params_and_fragments(self):
        """URLs containing query parameters or anchor fragments."""
        self.assertEqual(
            normalize_github_username("https://github.com/octocat?tab=repositories"),
            "octocat",
        )
        self.assertEqual(
            normalize_github_username("https://github.com/octocat#overview"),
            "octocat",
        )

    def test_08_empty_and_whitespace_inputs(self):
        """Empty or whitespace-only inputs must be rejected."""
        with self.assertRaises(InvalidGitHubUsernameError):
            normalize_github_username("")
        with self.assertRaises(InvalidGitHubUsernameError):
            normalize_github_username("   ")
        with self.assertRaises(InvalidGitHubUsernameError):
            normalize_github_username(None)
        with self.assertRaises(InvalidGitHubUsernameError):
            normalize_github_username("@")

    def test_09_root_and_empty_urls(self):
        """GitHub root URLs without a username must be rejected."""
        with self.assertRaises(InvalidGitHubUsernameError):
            normalize_github_username("https://github.com/")
        with self.assertRaises(InvalidGitHubUsernameError):
            normalize_github_username("https://github.com")
        with self.assertRaises(InvalidGitHubUsernameError):
            normalize_github_username("github.com/")

    def test_10_reserved_github_paths(self):
        """Reserved GitHub platform endpoints must not be accepted as user handles."""
        reserved_examples = [
            "settings",
            "orgs",
            "explore",
            "topics",
            "marketplace",
            "https://github.com/settings",
            "https://github.com/orgs",
            "https://github.com/explore",
        ]
        for res in reserved_examples:
            with self.assertRaises(InvalidGitHubUsernameError):
                normalize_github_username(res)

    def test_11_repository_urls_rejected_for_profile(self):
        """Repository deep URLs (e.g. user/repo) must be rejected when extracting profile usernames."""
        repo_urls = [
            "https://github.com/octocat/Hello-World",
            "https://github.com/user/repository",
            "github.com/octocat/repo/blob/main/README.md",
        ]
        for url in repo_urls:
            with self.assertRaises(InvalidGitHubUsernameError):
                normalize_github_username(url)

    def test_12_malformed_urls_and_other_domains(self):
        """Non-GitHub domains and malformed URLs must be rejected."""
        with self.assertRaises(InvalidGitHubUsernameError):
            normalize_github_username("https://gitlab.com/octocat")
        with self.assertRaises(InvalidGitHubUsernameError):
            normalize_github_username("https://bitbucket.org/octocat")
        with self.assertRaises(InvalidGitHubUsernameError):
            normalize_github_username("http://")

    def test_13_invalid_username_characters(self):
        """GitHub username format rules: no consecutive hyphens, no leading/trailing hyphens, no invalid chars."""
        invalid_patterns = [
            "octo$cat",
            "octo cat",
            "octo.cat",
            "octo_cat",
            "-octocat",
            "octocat-",
            "octo--cat",
            "a" * 40,  # Max length is 39
        ]
        for pattern in invalid_patterns:
            with self.assertRaises(InvalidGitHubUsernameError):
                normalize_github_username(pattern)

    def test_14_service_method_normalization(self):
        """GitHubService instance method must delegate to normalization helper."""
        service = GitHubService()
        self.assertEqual(service.normalize_username("https://github.com/octocat/"), "octocat")


class TestGitHubTokenConfiguration(unittest.TestCase):
    """Unit tests for optional GitHub token configuration and request headers."""

    def test_15_no_token_headers(self):
        """When no token is provided, request headers must not contain Authorization."""
        service = GitHubService(token=None)
        headers = service._get_headers()
        self.assertNotIn("Authorization", headers)
        self.assertEqual(headers["Accept"], "application/vnd.github+json")
        self.assertEqual(headers["User-Agent"], "Developer-Career-Intelligence-System")

    def test_16_empty_token_headers(self):
        """Empty or whitespace-only token string must be treated as no token."""
        service = GitHubService(token="   ")
        headers = service._get_headers()
        self.assertNotIn("Authorization", headers)

    def test_17_explicit_token_headers(self):
        """When token is passed to constructor, Authorization header must be set correctly."""
        service = GitHubService(token="ghp_mockPersonalToken12345")
        headers = service._get_headers()
        self.assertIn("Authorization", headers)
        self.assertEqual(headers["Authorization"], "Bearer ghp_mockPersonalToken12345")

    def test_18_settings_fallback_token(self):
        """When no explicit token is passed, service must read from settings.github_token."""
        mock_settings = Settings(github_token="ghp_settingsToken98765")
        with patch("app.services.github_service.settings", mock_settings):
            service = GitHubService()
            headers = service._get_headers()
            self.assertIn("Authorization", headers)
            self.assertEqual(headers["Authorization"], "Bearer ghp_settingsToken98765")

    def test_19_rate_limit_recording(self):
        """Service captures rate limit headers from HTTP response if present."""
        service = GitHubService()
        mock_response = httpx.Response(
            status_code=200,
            headers={
                "x-ratelimit-limit": "5000",
                "x-ratelimit-remaining": "4950",
                "x-ratelimit-reset": "1700000000",
                "x-ratelimit-used": "50",
            },
        )
        service._record_rate_limit(mock_response)
        self.assertIsNotNone(service.last_rate_limit)
        self.assertEqual(service.last_rate_limit["limit"], 5000)
        self.assertEqual(service.last_rate_limit["remaining"], 4950)
        self.assertEqual(service.last_rate_limit["reset"], 1700000000)
        self.assertEqual(service.last_rate_limit["used"], 50)


class TestGitHubRouteIntegration(unittest.TestCase):
    """Integration tests for GitHub API routes with normalization and error handling."""

    def setUp(self):
        self.client = TestClient(app)

    @patch("app.api.routes.github.github_service.get_user_profile")
    def test_20_route_valid_user(self, mock_get_profile):
        """Valid username returns HTTP 200 with structured profile response."""
        mock_get_profile.return_value = {
            "login": "octocat",
            "name": "The Octocat",
            "bio": "GitHub mascot",
            "avatar_url": "https://avatars.githubusercontent.com/u/583231?v=4",
            "html_url": "https://github.com/octocat",
            "public_repos": 8,
            "followers": 10000,
            "following": 9,
            "created_at": "2011-01-25T18:44:36Z",
        }
        response = self.client.get("/api/github/octocat")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["login"], "octocat")
        self.assertEqual(data["name"], "The Octocat")

    @patch("app.api.routes.github.github_service.get_user_profile")
    def test_21_route_not_found(self, mock_get_profile):
        """Non-existent GitHub user returns HTTP 404."""
        mock_get_profile.side_effect = GitHubUserNotFoundError("GitHub user 'unknown-user' not found")
        response = self.client.get("/api/github/unknown-user")
        self.assertEqual(response.status_code, 404)
        self.assertIn("not found", response.json()["detail"].lower())

    @patch("app.api.routes.github.github_service.get_user_profile")
    def test_22_route_rate_limited(self, mock_get_profile):
        """GitHub rate limit error returns HTTP 403."""
        mock_get_profile.side_effect = GitHubAPIError("GitHub API rate limit exceeded", status_code=403)
        response = self.client.get("/api/github/octocat")
        self.assertEqual(response.status_code, 403)
        self.assertIn("rate limit", response.json()["detail"].lower())

    def test_23_route_invalid_username_format_422(self):
        """Invalid username characters return HTTP 422 Unprocessable Entity."""
        response = self.client.get("/api/github/invalid$$user")
        self.assertEqual(response.status_code, 422)
        self.assertIn("Invalid GitHub username format", response.json()["detail"])

    def test_24_route_reserved_path_422(self):
        """Reserved GitHub system path passed to endpoint returns HTTP 422."""
        response = self.client.get("/api/github/settings")
        self.assertEqual(response.status_code, 422)
        self.assertIn("reserved GitHub system path", response.json()["detail"])


if __name__ == "__main__":
    unittest.main()
