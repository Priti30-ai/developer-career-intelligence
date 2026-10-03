import re
from typing import Any, Dict, List, Optional, Set
from urllib.parse import urlsplit
import httpx

from app.core.config import settings


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


class InvalidGitHubUsernameError(GitHubServiceError, ValueError):
    """Raised when a provided GitHub username or profile URL format is invalid."""
    pass


# GitHub usernames: 1-39 alphanumeric characters or single non-consecutive hyphens,
# cannot start or end with a hyphen.
GITHUB_USERNAME_REGEX = re.compile(
    r"^[a-zA-Z0-9](?:[a-zA-Z0-9]|-(?=[a-zA-Z0-9])){0,38}$"
)

# Reserved GitHub paths that are not user accounts
RESERVED_GITHUB_PATHS: Set[str] = {
    "settings",
    "orgs",
    "explore",
    "topics",
    "collections",
    "trending",
    "events",
    "marketplace",
    "sponsors",
    "login",
    "logout",
    "session",
    "signup",
    "pricing",
    "features",
    "security",
    "enterprise",
    "team",
    "readme",
    "contact",
    "about",
    "pulls",
    "issues",
    "notifications",
    "search",
    "site",
    "organizations",
}


def normalize_github_username(raw_input: Optional[str]) -> str:
    """
    Convert a GitHub username, handle, or profile URL into a canonical username.

    Supports:
        - 'octocat'
        - '@octocat'
        - 'https://github.com/octocat'
        - 'https://github.com/octocat/'
        - 'http://github.com/octocat/'
        - 'github.com/octocat'
        - 'www.github.com/octocat/'

    Rejects:
        - None, empty string, or whitespace-only input
        - Reserved GitHub paths ('settings', 'orgs', 'explore', etc.)
        - Repository URLs (e.g. 'https://github.com/user/repository')
        - Non-github.com hostnames
        - Usernames violating GitHub naming rules (consecutive hyphens, leading/trailing hyphen, unsafe chars)

    Returns:
        Canonical GitHub username string.

    Raises:
        InvalidGitHubUsernameError: If the input cannot be resolved to a valid GitHub username.
    """
    if raw_input is None:
        raise InvalidGitHubUsernameError("GitHub username or profile URL cannot be None")

    value = str(raw_input).strip()
    if not value:
        raise InvalidGitHubUsernameError("GitHub username or profile URL cannot be empty or whitespace-only")

    # Strip leading @ if present (e.g. '@octocat' -> 'octocat')
    if value.startswith("@"):
        value = value[1:].strip()
        if not value:
            raise InvalidGitHubUsernameError("GitHub username cannot be just '@'")

    # Detect if input resembles a URL or domain path
    is_url_like = (
        "://" in value
        or value.lower().startswith("github.com/")
        or value.lower().startswith("www.github.com/")
        or "/" in value
    )

    candidate = value
    if is_url_like:
        url_to_parse = value
        if not (value.startswith("http://") or value.startswith("https://")):
            url_to_parse = f"https://{value}"

        try:
            parsed = urlsplit(url_to_parse)
        except Exception as exc:
            raise InvalidGitHubUsernameError(f"Malformed GitHub URL: '{value}'") from exc

        hostname = (parsed.hostname or "").lower()
        if hostname not in ("github.com", "www.github.com"):
            raise InvalidGitHubUsernameError(
                f"URL must be on github.com (received '{hostname or value}')"
            )

        # Extract path segments, stripping leading and trailing slashes
        path_segments = [seg for seg in parsed.path.strip("/").split("/") if seg]
        if not path_segments:
            raise InvalidGitHubUsernameError("GitHub URL does not contain a profile username")

        # Disallow repository paths (e.g. /user/repo) or deeper paths when resolving a profile username
        if len(path_segments) > 1:
            raise InvalidGitHubUsernameError(
                f"Expected a GitHub profile URL, but received repository or deep path: '{parsed.path}'"
            )

        candidate = path_segments[0]

    # Check for reserved system paths
    if candidate.lower() in RESERVED_GITHUB_PATHS:
        raise InvalidGitHubUsernameError(
            f"'{candidate}' is a reserved GitHub system path, not a user profile"
        )

    # Validate against GitHub's username format requirements
    if not GITHUB_USERNAME_REGEX.match(candidate):
        raise InvalidGitHubUsernameError(
            f"Invalid GitHub username format: '{candidate}'. GitHub usernames must be 1-39 characters, "
            "contain only alphanumeric characters or single hyphens, and cannot start or end with a hyphen."
        )

    return candidate


class GitHubService:
    """Service for interacting with the public GitHub REST API."""

    BASE_URL = "https://api.github.com"
    HEADERS = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "Developer-Career-Intelligence-System",
    }
    TIMEOUT = 10.0

    def __init__(self, token: Optional[str] = None):
        self._token = token
        self.last_rate_limit: Optional[Dict[str, int]] = None

    @property
    def token(self) -> Optional[str]:
        """Return the active GitHub token if configured, else None."""
        if self._token is not None:
            clean = self._token.strip()
            return clean if clean else None
        tok = getattr(settings, "github_token", None)
        return tok.strip() if tok and tok.strip() else None

    def _get_headers(self) -> Dict[str, str]:
        """
        Build request headers for GitHub API requests.
        Includes Authorization header only when a valid token is configured.
        """
        headers = dict(self.HEADERS)
        active_token = self.token
        if active_token:
            headers["Authorization"] = f"Bearer {active_token}"
        return headers

    def _record_rate_limit(self, response: httpx.Response) -> None:
        """Capture rate-limit headers from GitHub response if present."""
        if "x-ratelimit-remaining" in response.headers:
            try:
                self.last_rate_limit = {
                    "limit": int(response.headers.get("x-ratelimit-limit", 0)),
                    "remaining": int(response.headers.get("x-ratelimit-remaining", 0)),
                    "reset": int(response.headers.get("x-ratelimit-reset", 0)),
                    "used": int(response.headers.get("x-ratelimit-used", 0)),
                }
            except (ValueError, TypeError):
                pass

    def normalize_username(self, raw_input: Optional[str]) -> str:
        """Helper method exposing username normalization on the service instance."""
        return normalize_github_username(raw_input)

    async def get_user_profile(self, username: str) -> Dict[str, Any]:
        """
        Fetch public profile details for a given GitHub username or profile URL.

        Args:
            username: Public GitHub username or profile URL.

        Returns:
            Dict containing structured profile data.

        Raises:
            InvalidGitHubUsernameError: When username format or URL is invalid.
            GitHubUserNotFoundError: When the user is not found (HTTP 404).
            GitHubAPIError: When the GitHub API cannot be reached or returns an error.
        """
        clean_username = normalize_github_username(username)
        url = f"{self.BASE_URL}/users/{clean_username}"

        try:
            async with httpx.AsyncClient(timeout=self.TIMEOUT) as client:
                response = await client.get(url, headers=self._get_headers())
        except httpx.TimeoutException as exc:
            raise GitHubAPIError("GitHub API request timed out", status_code=504) from exc
        except httpx.RequestError as exc:
            raise GitHubAPIError("Failed to connect to GitHub API", status_code=502) from exc
        except Exception as exc:
            raise GitHubAPIError(f"Unexpected error communicating with GitHub: {str(exc)}", status_code=500) from exc

        self._record_rate_limit(response)

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
                "account_type": data.get("type"),
                "company": data.get("company"),
                "location": data.get("location"),
                "blog": data.get("blog"),
                "email": data.get("email"),
                "twitter_username": data.get("twitter_username"),
                "created_at": data.get("created_at"),
                "updated_at": data.get("updated_at"),
            }

        if response.status_code == 404:
            raise GitHubUserNotFoundError(f"GitHub user '{clean_username}' not found")

        if response.status_code == 403:
            raise GitHubAPIError("GitHub API rate limit exceeded or access forbidden", status_code=403)

        raise GitHubAPIError(
            f"GitHub API returned error status: {response.status_code}",
            status_code=response.status_code if response.status_code < 500 else 502,
        )

    async def get_user_repositories(
        self, username: str, page: int = 1, per_page: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Fetch public repositories for a given GitHub username or profile URL with pagination.

        Args:
            username: Public GitHub username or profile URL.
            page: 1-indexed page number (default 1).
            per_page: Number of items per page (default 100, max 100).

        Returns:
            List of dicts containing structured repository data.

        Raises:
            InvalidGitHubUsernameError: When username format or URL is invalid.
            GitHubUserNotFoundError: When the user is not found (HTTP 404).
            GitHubAPIError: When the GitHub API cannot be reached or returns an error.
        """
        clean_username = normalize_github_username(username)
        url = f"{self.BASE_URL}/users/{clean_username}/repos"
        params = {
            "per_page": per_page,
            "page": page,
            "sort": "updated",
            "direction": "desc",
        }

        try:
            async with httpx.AsyncClient(timeout=self.TIMEOUT) as client:
                response = await client.get(url, headers=self._get_headers(), params=params)
        except httpx.TimeoutException as exc:
            raise GitHubAPIError("GitHub API request timed out", status_code=504) from exc
        except httpx.RequestError as exc:
            raise GitHubAPIError("Failed to connect to GitHub API", status_code=502) from exc
        except Exception as exc:
            raise GitHubAPIError(f"Unexpected error communicating with GitHub: {str(exc)}", status_code=500) from exc

        self._record_rate_limit(response)

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
                    "watchers_count": repo.get("watchers_count", 0),
                    "default_branch": repo.get("default_branch", "main"),
                    "topics": repo.get("topics", []),
                    "created_at": repo.get("created_at"),
                    "updated_at": repo.get("updated_at"),
                    "pushed_at": repo.get("pushed_at"),
                    "private": repo.get("private", False),
                    "fork": repo.get("fork", False),
                    "archived": repo.get("archived", False),
                    "size": repo.get("size", 0),
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

    async def get_all_user_repositories(
        self, username: str, max_pages: int = 10, per_page: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Fetch all public repositories for a given GitHub username across multiple pages.

        Stops when:
        - GitHub returns an empty list
        - GitHub returns fewer than per_page items
        - max_pages is reached (safeguard against excessive API consumption)

        Args:
            username: Public GitHub username or profile URL.
            max_pages: Maximum number of pages to retrieve (default 10).
            per_page: Number of items per page (default 100).

        Returns:
            Deduplicated list of structured repository dicts across all retrieved pages.
        """
        clean_username = normalize_github_username(username)
        all_repos: List[Dict[str, Any]] = []
        seen_full_names: Set[str] = set()

        for page in range(1, max_pages + 1):
            page_repos = await self.get_user_repositories(
                clean_username, page=page, per_page=per_page
            )
            if not page_repos:
                break

            for repo in page_repos:
                repo_id = repo.get("full_name") or repo.get("name")
                if repo_id and repo_id not in seen_full_names:
                    seen_full_names.add(repo_id)
                    all_repos.append(repo)

            # If page had fewer items than per_page, no more pages exist
            if len(page_repos) < per_page:
                break

        return all_repos

    async def get_repository_details(self, owner: str, repo: str) -> Dict[str, Any]:
        """
        Fetch public repository metadata for a given owner and repository name.

        Args:
            owner: Repository owner/organization or profile URL.
            repo: Repository name.

        Returns:
            Dict containing repository details.

        Raises:
            InvalidGitHubUsernameError: When owner format or URL is invalid.
            GitHubRepositoryNotFoundError: When repository is not found (HTTP 404).
            GitHubAPIError: When GitHub API request fails or rate limit exceeded.
        """
        clean_owner = normalize_github_username(owner)
        clean_repo = repo.strip()
        if not clean_repo:
            raise ValueError("Repository name cannot be empty")
        url = f"{self.BASE_URL}/repos/{clean_owner}/{clean_repo}"

        try:
            async with httpx.AsyncClient(timeout=self.TIMEOUT) as client:
                response = await client.get(url, headers=self._get_headers())
        except httpx.TimeoutException as exc:
            raise GitHubAPIError("GitHub API request timed out", status_code=504) from exc
        except httpx.RequestError as exc:
            raise GitHubAPIError("Failed to connect to GitHub API", status_code=502) from exc
        except Exception as exc:
            raise GitHubAPIError(f"Unexpected error communicating with GitHub: {str(exc)}", status_code=500) from exc

        self._record_rate_limit(response)

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

    async def get_repository_tree_data(
        self, owner: str, repo: str, branch: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Fetch the recursive file and directory tree of a GitHub repository,
        including tree metadata (e.g. truncated flag).

        Args:
            owner: Repository owner/organization or profile URL.
            repo: Repository name.
            branch: Optional branch name or commit SHA (defaults to 'HEAD').

        Returns:
            Dict containing:
            - 'tree': List of dicts representing tree items with 'path', 'type', and 'size'
            - 'truncated': bool indicating whether the tree was truncated by GitHub API

        Raises:
            InvalidGitHubUsernameError: When owner format or URL is invalid.
            GitHubRepositoryNotFoundError: When repository or branch is not found (HTTP 404).
            GitHubAPIError: When GitHub API request fails or rate limit exceeded.
        """
        clean_owner = normalize_github_username(owner)
        clean_repo = repo.strip()
        if not clean_repo:
            raise ValueError("Repository name cannot be empty")
        target_branch = branch.strip() if branch and branch.strip() else "HEAD"
        url = f"{self.BASE_URL}/repos/{clean_owner}/{clean_repo}/git/trees/{target_branch}?recursive=1"

        try:
            async with httpx.AsyncClient(timeout=self.TIMEOUT) as client:
                response = await client.get(url, headers=self._get_headers())
        except httpx.TimeoutException as exc:
            raise GitHubAPIError("GitHub API request timed out", status_code=504) from exc
        except httpx.RequestError as exc:
            raise GitHubAPIError("Failed to connect to GitHub API", status_code=502) from exc
        except Exception as exc:
            raise GitHubAPIError(f"Unexpected error communicating with GitHub: {str(exc)}", status_code=500) from exc

        self._record_rate_limit(response)

        if response.status_code == 200:
            data = response.json()
            raw_tree = data.get("tree", [])
            is_truncated = bool(data.get("truncated", False))
            tree_items = [
                {
                    "path": item.get("path"),
                    "type": item.get("type", "blob"),
                    "size": item.get("size"),
                }
                for item in raw_tree
                if item.get("path")
            ]
            return {
                "tree": tree_items,
                "truncated": is_truncated,
            }

        # 409 Conflict occurs if the repository is completely empty (no commits)
        if response.status_code == 409:
            return {"tree": [], "truncated": False}

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

    async def get_repository_tree(
        self, owner: str, repo: str, branch: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch the recursive file and directory tree of a GitHub repository.

        Args:
            owner: Repository owner/organization or profile URL.
            repo: Repository name.
            branch: Optional branch name or commit SHA (defaults to 'HEAD').

        Returns:
            List of dicts representing tree items with 'path', 'type' ('blob' or 'tree'), and 'size'.

        Raises:
            InvalidGitHubUsernameError: When owner format or URL is invalid.
            GitHubRepositoryNotFoundError: When repository or branch is not found (HTTP 404).
            GitHubAPIError: When GitHub API request fails or rate limit exceeded.
        """
        data = await self.get_repository_tree_data(owner, repo, branch=branch)
        return data["tree"]

    async def get_repository_file_content(
        self, owner: str, repo: str, path: str, branch: Optional[str] = None
    ) -> Optional[str]:
        """
        Fetch raw text content of a file in a GitHub repository.

        Args:
            owner: Repository owner/organization.
            repo: Repository name.
            path: Relative file path within repository.
            branch: Optional branch name or ref.

        Returns:
            File content as text, or None if not found or empty.

        Raises:
            GitHubAPIError: When rate limit exceeded or network error occurs.
        """
        clean_owner = normalize_github_username(owner)
        clean_repo = repo.strip()
        clean_path = path.strip().lstrip("/")
        if not clean_repo or not clean_path:
            return None

        url = f"{self.BASE_URL}/repos/{clean_owner}/{clean_repo}/contents/{clean_path}"
        params = {}
        if branch and branch.strip():
            params["ref"] = branch.strip()

        headers = self._get_headers()
        headers["Accept"] = "application/vnd.github.v3.raw"

        try:
            async with httpx.AsyncClient(timeout=self.TIMEOUT) as client:
                response = await client.get(url, headers=headers, params=params)
        except httpx.TimeoutException as exc:
            raise GitHubAPIError("GitHub API request timed out", status_code=504) from exc
        except httpx.RequestError as exc:
            raise GitHubAPIError("Failed to connect to GitHub API", status_code=502) from exc
        except Exception as exc:
            raise GitHubAPIError(f"Unexpected error communicating with GitHub: {str(exc)}", status_code=500) from exc

        self._record_rate_limit(response)

        if response.status_code == 200:
            return response.text
        if response.status_code == 404:
            return None
        if response.status_code == 403:
            raise GitHubAPIError("GitHub API rate limit exceeded or access forbidden", status_code=403)

        return None


# Singleton instance for route usage
github_service = GitHubService()
