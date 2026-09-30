from typing import Any, Dict, List
import httpx


class GitHubServiceError(Exception):
    """Base exception for GitHub service errors."""
    pass


class GitHubUserNotFoundError(GitHubServiceError):
    """Raised when the requested GitHub user is not found."""
    pass


class GitHubAPIError(GitHubServiceError):
    """Raised when GitHub API communication fails or returns an error."""
    def __init__(self, message: str, status_code: int = 502):
        super().__init__(message)
        self.status_code = status_code


class GitHubService:
    """Service for interacting with the public GitHub REST API."""

    BASE_URL = "https://api.github.com"
    HEADERS = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "Developer-Career-Intelligence-System",
    }
    TIMEOUT = 10.0

    async def get_user_profile(self, username: str) -> Dict[str, Any]:
        """
        Fetch public profile details for a given GitHub username.

        Args:
            username: Public GitHub username.

        Returns:
            Dict containing structured profile data.

        Raises:
            GitHubUserNotFoundError: When the user is not found (HTTP 404).
            GitHubAPIError: When the GitHub API cannot be reached or returns an error.
        """
        clean_username = username.strip()
        url = f"{self.BASE_URL}/users/{clean_username}"

        try:
            async with httpx.AsyncClient(timeout=self.TIMEOUT) as client:
                response = await client.get(url, headers=self.HEADERS)
        except httpx.TimeoutException as exc:
            raise GitHubAPIError("GitHub API request timed out", status_code=504) from exc
        except httpx.RequestError as exc:
            raise GitHubAPIError("Failed to connect to GitHub API", status_code=502) from exc
        except Exception as exc:
            raise GitHubAPIError(f"Unexpected error communicating with GitHub: {str(exc)}", status_code=500) from exc

        if response.status_code == 200:
            data = response.json()
            return {
                "login": data.get("login"),
                "name": data.get("name"),
                "bio": data.get("bio"),
                "avatar_url": data.get("avatar_url"),
                "html_url": data.get("html_url"),
                "public_repos": data.get("public_repos", 0),
                "followers": data.get("followers", 0),
                "following": data.get("following", 0),
                "created_at": data.get("created_at"),
            }

        if response.status_code == 404:
            raise GitHubUserNotFoundError(f"GitHub user '{clean_username}' not found")

        if response.status_code == 403:
            raise GitHubAPIError("GitHub API rate limit exceeded or access forbidden", status_code=403)

        raise GitHubAPIError(
            f"GitHub API returned error status: {response.status_code}",
            status_code=response.status_code if response.status_code < 500 else 502,
        )

    async def get_user_repositories(self, username: str) -> List[Dict[str, Any]]:
        """
        Fetch public repositories for a given GitHub username (up to first 100).

        Args:
            username: Public GitHub username.

        Returns:
            List of dicts containing structured repository data.

        Raises:
            GitHubUserNotFoundError: When the user is not found (HTTP 404).
            GitHubAPIError: When the GitHub API cannot be reached or returns an error.
        """
        clean_username = username.strip()
        url = f"{self.BASE_URL}/users/{clean_username}/repos"
        params = {
            "per_page": 100,
            "sort": "updated",
            "direction": "desc",
        }

        try:
            async with httpx.AsyncClient(timeout=self.TIMEOUT) as client:
                response = await client.get(url, headers=self.HEADERS, params=params)
        except httpx.TimeoutException as exc:
            raise GitHubAPIError("GitHub API request timed out", status_code=504) from exc
        except httpx.RequestError as exc:
            raise GitHubAPIError("Failed to connect to GitHub API", status_code=502) from exc
        except Exception as exc:
            raise GitHubAPIError(f"Unexpected error communicating with GitHub: {str(exc)}", status_code=500) from exc

        if response.status_code == 200:
            repos_data = response.json()
            return [
                {
                    "name": repo.get("name"),
                    "full_name": repo.get("full_name"),
                    "description": repo.get("description"),
                    "html_url": repo.get("html_url"),
                    "language": repo.get("language"),
                    "stargazers_count": repo.get("stargazers_count", 0),
                    "forks_count": repo.get("forks_count", 0),
                    "topics": repo.get("topics", []),
                    "created_at": repo.get("created_at"),
                    "updated_at": repo.get("updated_at"),
                    "private": repo.get("private", False),
                    "fork": repo.get("fork", False),
                }
                for repo in repos_data
            ]

        if response.status_code == 404:
            raise GitHubUserNotFoundError(f"GitHub user '{clean_username}' not found")

        if response.status_code == 403:
            raise GitHubAPIError("GitHub API rate limit exceeded or access forbidden", status_code=403)

        raise GitHubAPIError(
            f"GitHub API returned error status: {response.status_code}",
            status_code=response.status_code if response.status_code < 500 else 502,
        )


# Singleton instance for route usage
github_service = GitHubService()
