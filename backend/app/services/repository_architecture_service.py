"""
repository_architecture_service.py
----------------------------------
Service layer for deterministic GitHub Repository Architecture Analysis.

Analyzes the file/directory tree, configuration manifests, and metadata
of a GitHub repository to determine:
- Project structural organization (frontend, backend, database, devops, testing)
- Configuration and dependency manifests
- Primary project classification (FULL_STACK, FRONTEND, BACKEND, DATA_SCIENCE,
  MACHINE_LEARNING, CLI, LIBRARY, UNKNOWN)
- Concrete architecture signals with explainable evidence paths

Strict Semantics:
- Directory existence alone (e.g. 'models/') is NOT confused with confirmed
  database technologies (e.g. PostgreSQL).
- Absence of syntax or AST parsing is acknowledged; analysis is based on concrete
  structural files, manifests, and directory topology.
"""

from pathlib import PurePosixPath
from typing import Any, Dict, List, Optional, Set, Tuple

from app.schemas.repository_architecture import (
    ArchitectureSignal,
    RepositoryArchitectureResponse,
    RepositoryArchitectureSummary,
    RepositoryInfo,
)
from app.services.github_service import (
    GitHubAPIError,
    GitHubRepositoryNotFoundError,
    github_service,
)
from app.services.technology_service import normalize_technology_name

PROJECT_TYPE_FULL_STACK = "FULL_STACK"
PROJECT_TYPE_FRONTEND = "FRONTEND"
PROJECT_TYPE_BACKEND = "BACKEND"
PROJECT_TYPE_DATA_SCIENCE = "DATA_SCIENCE"
PROJECT_TYPE_MACHINE_LEARNING = "MACHINE_LEARNING"
PROJECT_TYPE_CLI = "CLI"
PROJECT_TYPE_LIBRARY = "LIBRARY"
PROJECT_TYPE_UNKNOWN = "UNKNOWN"

# Extension to normalized language map
EXTENSION_LANGUAGE_MAP: Dict[str, str] = {
    ".py": "Python",
    ".ts": "TypeScript",
    ".tsx": "TypeScript",
    ".js": "JavaScript",
    ".jsx": "JavaScript",
    ".mjs": "JavaScript",
    ".cjs": "JavaScript",
    ".java": "Java",
    ".cpp": "C++",
    ".cc": "C++",
    ".cxx": "C++",
    ".h": "C++",
    ".hpp": "C++",
    ".c": "C",
    ".go": "Go",
    ".rs": "Rust",
    ".rb": "Ruby",
    ".php": "PHP",
    ".cs": "C#",
    ".html": "HTML",
    ".css": "CSS",
    ".scss": "CSS",
    ".sass": "CSS",
    ".less": "CSS",
    ".sql": "SQL",
    ".ipynb": "Jupyter Notebook",
    ".sh": "Shell",
    ".bash": "Shell",
    ".kt": "Kotlin",
    ".swift": "Swift",
    ".dart": "Dart",
    ".r": "R",
    ".lua": "Lua",
}

DEPENDENCY_MANIFEST_NAMES: Set[str] = {
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
    # JavaScript / TypeScript
    "package.json",
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    "bun.lockb",
    "tsconfig.json",
    "vite.config.js",
    "vite.config.ts",
    "vite.config.mjs",
    "next.config.js",
    "next.config.mjs",
    "next.config.ts",
    "webpack.config.js",
    # Java
    "pom.xml",
    "build.gradle",
    "build.gradle.kts",
    # C/C++
    "cmakelists.txt",
    "makefile",
    "meson.build",
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
}

DOCUMENTATION_FILENAMES: Set[str] = {
    "readme.md",
    "readme.rst",
    "readme.txt",
    "readme",
    "contributing.md",
    "contributing.rst",
    "contributing",
    "license",
    "license.md",
    "license.txt",
    "changelog.md",
    "changelog.rst",
    "changelog",
    "arch.md",
    "architecture.md",
}


class RepositoryArchitectureService:
    """
    Deterministic service for analyzing repository trees and structure.
    """

    def normalize_tree_paths(
        self, raw_tree: List[Dict[str, Any]]
    ) -> Tuple[List[str], List[str]]:
        """
        Normalize tree items into clean lists of file paths and directory paths.
        Standardizes separators to forward slashes.
        """
        file_paths: List[str] = []
        dir_paths: Set[str] = set()

        for item in raw_tree:
            raw_path = item.get("path")
            if not raw_path or not isinstance(raw_path, str):
                continue

            clean_path = raw_path.replace("\\", "/").strip("/")
            item_type = item.get("type", "blob")

            if item_type == "tree":
                dir_paths.add(clean_path)
            else:
                file_paths.append(clean_path)
                # Infer parent directories
                parts = clean_path.split("/")
                for i in range(1, len(parts)):
                    dir_paths.add("/".join(parts[:i]))

        return sorted(file_paths), sorted(list(dir_paths))

    def detect_languages(self, file_paths: List[str], primary_language: Optional[str]) -> List[str]:
        """
        Detect languages from file extensions and include reported primary language.
        """
        detected: Set[str] = set()

        if primary_language and primary_language.strip():
            norm_primary = normalize_technology_name(primary_language)
            if norm_primary:
                detected.add(norm_primary)

        for path in file_paths:
            ext = PurePosixPath(path).suffix.lower()
            if ext in EXTENSION_LANGUAGE_MAP:
                detected.add(EXTENSION_LANGUAGE_MAP[ext])

        return sorted(list(detected))

    def detect_dependency_files(self, file_paths: List[str]) -> List[str]:
        """
        Identify package and dependency manifests in repository.
        """
        matched: List[str] = []
        for path in file_paths:
            filename = PurePosixPath(path).name.lower()
            if filename in DEPENDENCY_MANIFEST_NAMES:
                matched.append(path)
            elif filename.startswith("requirements") and filename.endswith(".txt"):
                matched.append(path)
            elif filename.endswith(".csproj") or filename.endswith(".sln"):
                matched.append(path)
        return sorted(matched)

    def detect_documentation_files(self, file_paths: List[str]) -> List[str]:
        """
        Identify documentation files and guides.
        """
        matched: List[str] = []
        for path in file_paths:
            filename = PurePosixPath(path).name.lower()
            if filename in DOCUMENTATION_FILENAMES or path.lower().startswith("docs/"):
                matched.append(path)
        return sorted(matched)

    def detect_important_files(self, file_paths: List[str]) -> List[str]:
        """
        Identify prominent build, configuration, container, and architectural files.
        """
        important_names = {
            "dockerfile",
            "docker-compose.yml",
            "docker-compose.yaml",
            ".dockerignore",
            ".gitignore",
            ".env.example",
            ".env.sample",
            "package.json",
            "requirements.txt",
            "pyproject.toml",
            "setup.py",
            "cargo.toml",
            "go.mod",
            "pom.xml",
            "cmakelists.txt",
            "schema.prisma",
            "alembic.ini",
            "vite.config.ts",
            "vite.config.js",
            "next.config.js",
            "next.config.ts",
        }
        matched: List[str] = []
        for path in file_paths:
            filename = PurePosixPath(path).name.lower()
            if filename in important_names or filename.startswith("dockerfile"):
                matched.append(path)
        return sorted(matched)

    def extract_architecture_signals(
        self, file_paths: List[str], dir_paths: List[str]
    ) -> Tuple[List[ArchitectureSignal], Dict[str, bool]]:
        """
        Extract explainable architecture signals with concrete evidence paths.
        Returns the signal list and a dictionary of capability flags.
        """
        signals: List[ArchitectureSignal] = []
        lower_files = [f.lower() for f in file_paths]
        lower_dirs = [d.lower() for d in dir_paths]

        # 1. Frontend Signals
        frontend_evidence: List[str] = []
        for d in dir_paths:
            dl = d.lower()
            if dl in ("frontend", "client", "ui", "web", "src/components", "src/pages", "src/views", "components", "pages"):
                frontend_evidence.append(f"{d}/")

        for f in file_paths:
            fl = f.lower()
            name = PurePosixPath(fl).name
            if name.startswith("vite.config.") or name.startswith("next.config."):
                frontend_evidence.append(f)
            elif name == "package.json" and any("react" in p or "vue" in p or "frontend" in p or "client" in p for p in lower_files):
                frontend_evidence.append(f)
            elif PurePosixPath(fl).suffix in (".tsx", ".jsx"):
                # Sample up to 2 component files
                if len([x for x in frontend_evidence if x.endswith((".tsx", ".jsx"))]) < 2:
                    frontend_evidence.append(f)

        has_frontend = len(frontend_evidence) > 0
        if has_frontend:
            signals.append(
                ArchitectureSignal(
                    type="FRONTEND",
                    description="Frontend user interface structure detected",
                    evidence=sorted(list(set(frontend_evidence))),
                )
            )

        # 2. Backend Signals
        backend_evidence: List[str] = []
        for d in dir_paths:
            dl = d.lower()
            if dl in ("backend", "server", "api", "routes", "services", "controllers", "handlers", "endpoints", "app/api"):
                backend_evidence.append(f"{d}/")

        for f in file_paths:
            fl = f.lower()
            name = PurePosixPath(fl).name
            if name in ("requirements.txt", "pyproject.toml") and any(b in fl for b in ("backend", "api", "server", "routes")):
                backend_evidence.append(f)

        has_backend = len(backend_evidence) > 0
        if has_backend:
            signals.append(
                ArchitectureSignal(
                    type="BACKEND",
                    description="Backend service / API architecture detected",
                    evidence=sorted(list(set(backend_evidence))),
                )
            )

        # 3. Database / Persistence Signals (Strict concrete evidence)
        database_evidence: List[str] = []
        for d in dir_paths:
            dl = d.lower()
            if dl in ("migrations", "db", "database", "prisma", "sql", "alembic", "db/migrations"):
                database_evidence.append(f"{d}/")

        for f in file_paths:
            fl = f.lower()
            name = PurePosixPath(fl).name
            if name in ("schema.prisma", "alembic.ini") or PurePosixPath(fl).suffix == ".sql":
                database_evidence.append(f)

        has_database = len(database_evidence) > 0
        if has_database:
            signals.append(
                ArchitectureSignal(
                    type="DATABASE",
                    description="Database migration and persistence schema detected",
                    evidence=sorted(list(set(database_evidence))),
                )
            )
        else:
            # Check for domain models directory without claiming a database exists
            model_dirs = [d for d in dir_paths if d.lower() in ("models", "app/models", "src/models")]
            if model_dirs:
                signals.append(
                    ArchitectureSignal(
                        type="MODELS",
                        description="Domain data models directory structure detected (unconfirmed persistence)",
                        evidence=[f"{d}/" for d in model_dirs],
                    )
                )

        # 4. DevOps & Containerization
        devops_evidence: List[str] = []
        for f in file_paths:
            fl = f.lower()
            name = PurePosixPath(fl).name
            if name in ("dockerfile", "docker-compose.yml", "docker-compose.yaml", ".dockerignore") or name.startswith("dockerfile."):
                devops_evidence.append(f)
            elif fl.startswith(".github/workflows/") or name == ".gitlab-ci.yml":
                devops_evidence.append(f)

        for d in dir_paths:
            dl = d.lower()
            if dl in ("k8s", "kubernetes", "helm", "terraform", ".github/workflows"):
                devops_evidence.append(f"{d}/")

        has_devops = len(devops_evidence) > 0
        if has_devops:
            signals.append(
                ArchitectureSignal(
                    type="DEVOPS",
                    description="Containerization, deployment, or CI/CD workflow configuration detected",
                    evidence=sorted(list(set(devops_evidence))),
                )
            )

        # 5. Data Science Signals
        ds_evidence: List[str] = []
        for f in file_paths:
            if f.lower().endswith(".ipynb"):
                ds_evidence.append(f)
        for d in dir_paths:
            if d.lower() in ("notebooks", "data", "datasets", "experiments"):
                ds_evidence.append(f"{d}/")

        has_data_science = len(ds_evidence) > 0
        if has_data_science:
            signals.append(
                ArchitectureSignal(
                    type="DATA_SCIENCE",
                    description="Data science analysis or interactive notebook structure detected",
                    evidence=sorted(list(set(ds_evidence))),
                )
            )

        # 6. Machine Learning Signals
        ml_evidence: List[str] = []
        for f in file_paths:
            ext = PurePosixPath(f).suffix.lower()
            if ext in (".pt", ".pth", ".onnx", ".pkl", ".h5", ".tflite"):
                ml_evidence.append(f)
        for d in dir_paths:
            if d.lower() in ("training", "pipelines", "ml_models"):
                ml_evidence.append(f"{d}/")

        has_ml = len(ml_evidence) > 0
        if has_ml:
            signals.append(
                ArchitectureSignal(
                    type="MACHINE_LEARNING",
                    description="Machine learning model training or serialized model artifact detected",
                    evidence=sorted(list(set(ml_evidence))),
                )
            )

        # 7. CLI Signals
        cli_evidence: List[str] = []
        for d in dir_paths:
            if d.lower() in ("cli", "bin", "cmd"):
                cli_evidence.append(f"{d}/")
        for f in file_paths:
            if PurePosixPath(f).name.lower() in ("cli.py", "main_cli.py"):
                cli_evidence.append(f)

        has_cli = len(cli_evidence) > 0
        if has_cli and not (has_frontend and has_backend):
            signals.append(
                ArchitectureSignal(
                    type="CLI",
                    description="Command-line interface structure detected",
                    evidence=sorted(list(set(cli_evidence))),
                )
            )

        # 8. Testing Signals
        test_evidence: List[str] = []
        for d in dir_paths:
            if d.lower() in ("tests", "test", "__tests__", "spec", "testing"):
                test_evidence.append(f"{d}/")
        for f in file_paths:
            name = PurePosixPath(f).name.lower()
            if name.startswith("test_") or name.endswith("_test.py") or name.endswith(".test.ts") or name.endswith(".spec.ts"):
                if len(test_evidence) < 3:
                    test_evidence.append(f)

        has_testing = len(test_evidence) > 0
        if has_testing:
            signals.append(
                ArchitectureSignal(
                    type="TESTING",
                    description="Automated unit or integration test suite detected",
                    evidence=sorted(list(set(test_evidence))),
                )
            )

        # 9. Documentation Signals
        docs = self.detect_documentation_files(file_paths)
        has_documentation = len(docs) > 0
        if has_documentation:
            signals.append(
                ArchitectureSignal(
                    type="DOCUMENTATION",
                    description="Project documentation files detected",
                    evidence=docs,
                )
            )

        flags = {
            "has_frontend": has_frontend,
            "has_backend": has_backend,
            "has_database": has_database,
            "has_devops": has_devops,
            "has_documentation": has_documentation,
            "has_data_science": has_data_science,
            "has_ml": has_ml,
            "has_cli": has_cli,
        }

        return signals, flags

    def classify_project_type(
        self,
        flags: Dict[str, bool],
        file_paths: List[str],
        dir_paths: List[str],
        primary_language: Optional[str],
    ) -> str:
        """
        Classify the repository into a deterministic, explainable project type.
        """
        has_frontend = flags.get("has_frontend", False)
        has_backend = flags.get("has_backend", False)
        has_data_science = flags.get("has_data_science", False)
        has_ml = flags.get("has_ml", False)
        has_cli = flags.get("has_cli", False)

        # 1. Full-Stack
        if has_frontend and has_backend:
            return PROJECT_TYPE_FULL_STACK

        # 2. Frontend Only
        if has_frontend and not has_backend:
            return PROJECT_TYPE_FRONTEND

        # 3. Backend Only
        if has_backend and not has_frontend:
            return PROJECT_TYPE_BACKEND

        # 4. Machine Learning
        if has_ml and not (has_frontend or has_backend):
            return PROJECT_TYPE_MACHINE_LEARNING

        # 5. Data Science
        if has_data_science and not (has_frontend or has_backend):
            return PROJECT_TYPE_DATA_SCIENCE

        # 6. CLI
        if has_cli and not (has_frontend or has_backend):
            return PROJECT_TYPE_CLI

        # 7. Library / Module Check
        filenames = {PurePosixPath(f).name.lower() for f in file_paths}
        is_library_manifest = any(
            m in filenames for m in ("setup.py", "pyproject.toml", "cargo.toml", "go.mod", "pom.xml")
        )
        has_src_lib = any(d.lower() in ("src", "lib") for d in dir_paths)
        if is_library_manifest and (has_src_lib or len(file_paths) > 0) and not (has_frontend or has_backend):
            return PROJECT_TYPE_LIBRARY

        # 8. Single language fallback if tree is very simple
        if not file_paths:
            return PROJECT_TYPE_UNKNOWN

        return PROJECT_TYPE_UNKNOWN

    async def analyze_repository(
        self,
        owner: str,
        repo: str,
        branch: Optional[str] = None,
        repository_details: Optional[Dict[str, Any]] = None,
        tree: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Analyze a GitHub repository's tree and structural signals.

        Args:
            owner: Repository owner.
            repo: Repository name.
            branch: Optional branch name or commit SHA.
            repository_details: Optional pre-fetched repository metadata (for testing).
            tree: Optional pre-fetched tree items (for testing).

        Returns:
            Dict conforming to RepositoryArchitectureResponse.

        Raises:
            GitHubRepositoryNotFoundError: If repository is not found (404).
            GitHubAPIError: If communication or rate limit fails.
            ValueError: If owner or repo is empty.
        """
        clean_owner = owner.strip()
        clean_repo = repo.strip()

        if not clean_owner or not clean_repo:
            raise ValueError("Repository owner and repo must not be empty or whitespace-only")

        # 1. Fetch repository details if not provided
        if repository_details is None:
            details = await github_service.get_repository_details(clean_owner, clean_repo)
        else:
            details = repository_details

        target_branch = branch or details.get("default_branch") or "HEAD"

        # 2. Fetch repository tree if not provided
        if tree is None:
            raw_tree = await github_service.get_repository_tree(
                clean_owner, clean_repo, branch=target_branch
            )
        else:
            raw_tree = tree

        # 3. Normalize tree paths
        file_paths, dir_paths = self.normalize_tree_paths(raw_tree)

        # 4. Detect languages and manifests
        primary_lang = details.get("language")
        languages_detected = self.detect_languages(file_paths, primary_lang)
        dependency_files = self.detect_dependency_files(file_paths)
        documentation_files = self.detect_documentation_files(file_paths)
        important_files = self.detect_important_files(file_paths)

        # 5. Extract architectural signals and capabilities
        signals, flags = self.extract_architecture_signals(file_paths, dir_paths)

        # 6. Classify project type
        project_type = self.classify_project_type(flags, file_paths, dir_paths, primary_lang)

        # Filter prominent directories for summary
        prominent_dirs = [
            d for d in dir_paths
            if "/" not in d or d.count("/") <= 1
        ][:30]

        summary = RepositoryArchitectureSummary(
            total_files_analyzed=len(file_paths),
            total_directories_detected=len(dir_paths),
            primary_project_type=project_type,
            has_frontend=flags.get("has_frontend", False),
            has_backend=flags.get("has_backend", False),
            has_database=flags.get("has_database", False),
            has_devops=flags.get("has_devops", False),
            has_documentation=flags.get("has_documentation", False),
        )

        response = RepositoryArchitectureResponse(
            repository=RepositoryInfo(
                name=details.get("name") or clean_repo,
                full_name=details.get("full_name") or f"{clean_owner}/{clean_repo}",
                html_url=details.get("html_url") or f"https://github.com/{clean_owner}/{clean_repo}",
                default_branch=details.get("default_branch") or target_branch,
            ),
            project_type=project_type,
            primary_language=primary_lang,
            languages_detected=languages_detected,
            directories_detected=prominent_dirs,
            important_files=important_files,
            dependency_files=dependency_files,
            documentation_files=documentation_files,
            architecture_signals=signals,
            summary=summary,
        )

        return response.model_dump()


# Singleton instance for route, service, and script usage
repository_architecture_service = RepositoryArchitectureService()
