from typing import Any, Dict, List, Optional
import httpx


class GitHubServiceError(Exception):
    """Base exception for GitHub service errors."""
    pass


class GitHubUserNotFoundError(GitHubServiceError):
    """Raised when the requested GitHub user is not found."""
    pass


class GitHubRepositoryNotFoundError(GitHubServiceError):
    """Raised when the requested GitHub repository is not found."""
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

    async def get_repository_details(self, owner: str, repo: str) -> Dict[str, Any]:
        """
        Fetch public repository metadata for a given owner and repository name.

        Args:
            owner: Repository owner/organization.
            repo: Repository name.

        Returns:
            Dict containing repository details.

        Raises:
            GitHubRepositoryNotFoundError: When repository is not found (HTTP 404).
            GitHubAPIError: When GitHub API request fails or rate limit exceeded.
        """
        clean_owner = owner.strip()
        clean_repo = repo.strip()
        url = f"{self.BASE_URL}/repos/{clean_owner}/{clean_repo}"

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
                "name": data.get("name") or clean_repo,
                "full_name": data.get("full_name") or f"{clean_owner}/{clean_repo}",
                "html_url": data.get("html_url") or f"https://github.com/{clean_owner}/{clean_repo}",
                "description": data.get("description"),
                "language": data.get("language"),
                "topics": data.get("topics", []),
                "default_branch": data.get("default_branch", "main"),
                "fork": data.get("fork", False),
                "stargazers_count": data.get("stargazers_count", 0),
                "forks_count": data.get("forks_count", 0),
            }

        if response.status_code == 404:
            raise GitHubRepositoryNotFoundError(f"GitHub repository '{clean_owner}/{clean_repo}' not found")

        if response.status_code == 403:
            raise GitHubAPIError("GitHub API rate limit exceeded or access forbidden", status_code=403)

        raise GitHubAPIError(
            f"GitHub API returned error status: {response.status_code}",
            status_code=response.status_code if response.status_code < 500 else 502,
        )

    async def get_repository_tree(
        self, owner: str, repo: str, branch: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch the recursive file and directory tree of a GitHub repository.

        Args:
            owner: Repository owner/organization.
            repo: Repository name.
            branch: Optional branch name or commit SHA (defaults to 'HEAD').

        Returns:
            List of dicts representing tree items with 'path', 'type' ('blob' or 'tree'), and 'size'.

        Raises:
            GitHubRepositoryNotFoundError: When repository or branch is not found (HTTP 404).
            GitHubAPIError: When GitHub API request fails or rate limit exceeded.
        """
        clean_owner = owner.strip()
        clean_repo = repo.strip()
        target_branch = branch.strip() if branch and branch.strip() else "HEAD"
        url = f"{self.BASE_URL}/repos/{clean_owner}/{clean_repo}/git/trees/{target_branch}?recursive=1"

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
            raw_tree = data.get("tree", [])
            return [
                {
                    "path": item.get("path"),
                    "type": item.get("type", "blob"),
                    "size": item.get("size"),
                }
                for item in raw_tree
                if item.get("path")
            ]

        # 409 Conflict occurs if the repository is completely empty (no commits)
        if response.status_code == 409:
            return []

        if response.status_code == 404:
            raise GitHubRepositoryNotFoundError(
                f"GitHub repository '{clean_owner}/{clean_repo}' (or branch '{target_branch}') not found"
            )

        if response.status_code == 403:
            raise GitHubAPIError("GitHub API rate limit exceeded or access forbidden", status_code=403)

        raise GitHubAPIError(
            f"GitHub API returned error status: {response.status_code}",
            status_code=response.status_code if response.status_code < 500 else 502,
        )


# Singleton instance for route usage
github_service = GitHubService()
