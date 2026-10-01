"""
test_repository_architecture.py
-------------------------------
Unit and integration tests for GitHub Repository Architecture Analysis.

Tests:
1. Tree path normalization (nested directories, files, root files, empty tree)
2. Frontend structure detection and signals
3. Backend structure detection and signals
4. Full-stack repository classification (both frontend and backend present)
5. Data science and machine learning repository classification
6. CLI and Library repository classification
7. Configuration and dependency manifest identification
8. Weak evidence semantics (models/ alone does not claim PostgreSQL database)
9. Concrete database evidence recognition (migrations, sql, prisma)
10. Containerization and DevOps detection
11. API contract for valid requests
12. API validation for invalid/blank inputs
13. API error handling for repository not found (404) and upstream failure (502)
"""

import sys
import unittest
from pathlib import Path
from unittest.mock import patch

# Ensure backend directory is in sys.path
backend_dir = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from fastapi.testclient import TestClient

from app.main import app
from app.services.github_service import (
    GitHubAPIError,
    GitHubRepositoryNotFoundError,
)
from app.services.repository_architecture_service import (
    PROJECT_TYPE_BACKEND,
    PROJECT_TYPE_CLI,
    PROJECT_TYPE_DATA_SCIENCE,
    PROJECT_TYPE_FRONTEND,
    PROJECT_TYPE_FULL_STACK,
    PROJECT_TYPE_LIBRARY,
    PROJECT_TYPE_MACHINE_LEARNING,
    PROJECT_TYPE_UNKNOWN,
    repository_architecture_service,
)

SAMPLE_FULL_STACK_TREE = [
    {"path": "frontend/package.json", "type": "blob"},
    {"path": "frontend/vite.config.ts", "type": "blob"},
    {"path": "frontend/src/App.tsx", "type": "blob"},
    {"path": "frontend/src/components/Header.tsx", "type": "blob"},
    {"path": "backend/requirements.txt", "type": "blob"},
    {"path": "backend/app/main.py", "type": "blob"},
    {"path": "backend/app/api/routes.py", "type": "blob"},
    {"path": "backend/app/services/user_service.py", "type": "blob"},
    {"path": "backend/migrations/0001_initial.sql", "type": "blob"},
    {"path": "Dockerfile", "type": "blob"},
    {"path": "docker-compose.yml", "type": "blob"},
    {"path": "README.md", "type": "blob"},
    {"path": "tests/test_main.py", "type": "blob"},
]

SAMPLE_REPO_DETAILS = {
    "name": "fullstack-platform",
    "full_name": "octocat/fullstack-platform",
    "html_url": "https://github.com/octocat/fullstack-platform",
    "description": "Full stack intelligence platform",
    "language": "Python",
    "default_branch": "main",
}


class TestRepositoryArchitectureService(unittest.IsolatedAsyncioTestCase):
    """Unit tests for repository architecture analysis logic."""

    def test_01_tree_parsing_and_normalization(self):
        """Test 1: Tree normalization extracts file paths, root files, and parent directories."""
        raw_tree = [
            {"path": "README.md", "type": "blob"},
            {"path": "src\\components\\Button.tsx", "type": "blob"},
            {"path": "backend/api/v1/routes.py", "type": "blob"},
            {"path": "empty_dir", "type": "tree"},
        ]

        files, dirs = repository_architecture_service.normalize_tree_paths(raw_tree)

        self.assertIn("README.md", files)
        self.assertIn("src/components/Button.tsx", files)
        self.assertIn("backend/api/v1/routes.py", files)

        # Directory structure inferred
        self.assertIn("src", dirs)
        self.assertIn("src/components", dirs)
        self.assertIn("backend", dirs)
        self.assertIn("backend/api", dirs)
        self.assertIn("backend/api/v1", dirs)
        self.assertIn("empty_dir", dirs)

        # Empty tree returns empty lists
        empty_files, empty_dirs = repository_architecture_service.normalize_tree_paths([])
        self.assertEqual(empty_files, [])
        self.assertEqual(empty_dirs, [])

    async def test_02_frontend_detection(self):
        """Test 2: Frontend indicators classify project as FRONTEND with appropriate signals."""
        tree = [
            {"path": "package.json", "type": "blob"},
            {"path": "vite.config.ts", "type": "blob"},
            {"path": "src/App.tsx", "type": "blob"},
            {"path": "src/components/Navbar.tsx", "type": "blob"},
            {"path": "src/pages/Home.tsx", "type": "blob"},
            {"path": "public/index.html", "type": "blob"},
        ]

        result = await repository_architecture_service.analyze_repository(
            owner="octocat",
            repo="frontend-ui",
            repository_details={"name": "frontend-ui", "language": "TypeScript"},
            tree=tree,
        )

        self.assertEqual(result["project_type"], PROJECT_TYPE_FRONTEND)
        self.assertTrue(result["summary"]["has_frontend"])
        self.assertFalse(result["summary"]["has_backend"])
        signal_types = [s["type"] for s in result["architecture_signals"]]
        self.assertIn("FRONTEND", signal_types)

    async def test_03_backend_detection(self):
        """Test 3: Backend indicators classify project as BACKEND with API and service signals."""
        tree = [
            {"path": "requirements.txt", "type": "blob"},
            {"path": "app/main.py", "type": "blob"},
            {"path": "app/api/endpoints.py", "type": "blob"},
            {"path": "app/services/item_service.py", "type": "blob"},
            {"path": "app/routes/auth.py", "type": "blob"},
            {"path": "tests/test_api.py", "type": "blob"},
        ]

        result = await repository_architecture_service.analyze_repository(
            owner="octocat",
            repo="backend-api",
            repository_details={"name": "backend-api", "language": "Python"},
            tree=tree,
        )

        self.assertEqual(result["project_type"], PROJECT_TYPE_BACKEND)
        self.assertTrue(result["summary"]["has_backend"])
        self.assertFalse(result["summary"]["has_frontend"])
        signal_types = [s["type"] for s in result["architecture_signals"]]
        self.assertIn("BACKEND", signal_types)

    async def test_04_full_stack_detection(self):
        """Test 4: Both frontend and backend signals classify project as FULL_STACK."""
        result = await repository_architecture_service.analyze_repository(
            owner="octocat",
            repo="fullstack-platform",
            repository_details=SAMPLE_REPO_DETAILS,
            tree=SAMPLE_FULL_STACK_TREE,
        )

        self.assertEqual(result["project_type"], PROJECT_TYPE_FULL_STACK)
        self.assertTrue(result["summary"]["has_frontend"])
        self.assertTrue(result["summary"]["has_backend"])
        self.assertTrue(result["summary"]["has_database"])
        self.assertTrue(result["summary"]["has_devops"])
        self.assertTrue(result["summary"]["has_documentation"])

    async def test_05_data_science_and_machine_learning_detection(self):
        """Test 5: Notebooks, datasets, and model artifacts produce data science and ML signals."""
        # 1. Data Science
        ds_tree = [
            {"path": "notebooks/analysis.ipynb", "type": "blob"},
            {"path": "data/sales_data.csv", "type": "blob"},
            {"path": "requirements.txt", "type": "blob"},
            {"path": "README.md", "type": "blob"},
        ]
        ds_result = await repository_architecture_service.analyze_repository(
            owner="octocat",
            repo="data-analysis",
            repository_details={"name": "data-analysis", "language": "Jupyter Notebook"},
            tree=ds_tree,
        )
        self.assertEqual(ds_result["project_type"], PROJECT_TYPE_DATA_SCIENCE)

        # 2. Machine Learning
        ml_tree = [
            {"path": "training/train.py", "type": "blob"},
            {"path": "models/model.onnx", "type": "blob"},
            {"path": "models/weights.pt", "type": "blob"},
            {"path": "requirements.txt", "type": "blob"},
        ]
        ml_result = await repository_architecture_service.analyze_repository(
            owner="octocat",
            repo="ml-model",
            repository_details={"name": "ml-model", "language": "Python"},
            tree=ml_tree,
        )
        self.assertEqual(ml_result["project_type"], PROJECT_TYPE_MACHINE_LEARNING)

    async def test_06_cli_and_library_detection(self):
        """Test 6: CLI tools and library manifests without web servers are classified properly."""
        # CLI
        cli_tree = [
            {"path": "cli.py", "type": "blob"},
            {"path": "cmd/root.go", "type": "blob"},
            {"path": "go.mod", "type": "blob"},
        ]
        cli_result = await repository_architecture_service.analyze_repository(
            owner="octocat",
            repo="my-cli",
            repository_details={"name": "my-cli", "language": "Go"},
            tree=cli_tree,
        )
        self.assertEqual(cli_result["project_type"], PROJECT_TYPE_CLI)

        # Library
        lib_tree = [
            {"path": "src/lib.rs", "type": "blob"},
            {"path": "Cargo.toml", "type": "blob"},
            {"path": "README.md", "type": "blob"},
        ]
        lib_result = await repository_architecture_service.analyze_repository(
            owner="octocat",
            repo="my-crate",
            repository_details={"name": "my-crate", "language": "Rust"},
            tree=lib_tree,
        )
        self.assertEqual(lib_result["project_type"], PROJECT_TYPE_LIBRARY)

    async def test_07_dependency_and_config_manifest_detection(self):
        """Test 7: All common dependency manifests and configurations are identified."""
        tree = [
            {"path": "package.json", "type": "blob"},
            {"path": "package-lock.json", "type": "blob"},
            {"path": "requirements.txt", "type": "blob"},
            {"path": "pyproject.toml", "type": "blob"},
            {"path": "Dockerfile", "type": "blob"},
            {"path": "docker-compose.yml", "type": "blob"},
            {"path": "README.md", "type": "blob"},
            {"path": "CONTRIBUTING.md", "type": "blob"},
            {"path": ".gitignore", "type": "blob"},
        ]

        result = await repository_architecture_service.analyze_repository(
            owner="octocat",
            repo="polyglot",
            repository_details={"name": "polyglot"},
            tree=tree,
        )

        dep_files = result["dependency_files"]
        self.assertIn("package.json", dep_files)
        self.assertIn("requirements.txt", dep_files)
        self.assertIn("pyproject.toml", dep_files)

        doc_files = result["documentation_files"]
        self.assertIn("README.md", doc_files)
        self.assertIn("CONTRIBUTING.md", doc_files)

        imp_files = result["important_files"]
        self.assertIn("Dockerfile", imp_files)
        self.assertIn("docker-compose.yml", imp_files)

    async def test_08_weak_evidence_semantic_rule(self):
        """Test 8: 'models/' directory alone does NOT assert a concrete database like PostgreSQL."""
        tree = [
            {"path": "models/user.py", "type": "blob"},
            {"path": "models/order.py", "type": "blob"},
            {"path": "main.py", "type": "blob"},
        ]

        result = await repository_architecture_service.analyze_repository(
            owner="octocat",
            repo="weak-evidence-repo",
            repository_details={"name": "weak-evidence-repo", "language": "Python"},
            tree=tree,
        )

        # has_database flag should be FALSE because there are no migration files, SQL scripts, or prisma schemas
        self.assertFalse(result["summary"]["has_database"])

        # Check signals
        signals = result["architecture_signals"]
        db_signals = [s for s in signals if s["type"] == "DATABASE"]
        self.assertEqual(len(db_signals), 0)

        # MODELS signal is structural and non-punitive
        model_signals = [s for s in signals if s["type"] == "MODELS"]
        self.assertEqual(len(model_signals), 1)
        self.assertIn("models/", model_signals[0]["evidence"])
        self.assertNotIn("PostgreSQL", model_signals[0]["description"])

    async def test_09_concrete_database_evidence_detection(self):
        """Test 9: Explicit migrations, SQL files, and prisma schemas confirm DATABASE signal."""
        tree = [
            {"path": "schema.prisma", "type": "blob"},
            {"path": "migrations/001_create_tables.sql", "type": "blob"},
            {"path": "server.js", "type": "blob"},
        ]

        result = await repository_architecture_service.analyze_repository(
            owner="octocat",
            repo="db-app",
            repository_details={"name": "db-app", "language": "JavaScript"},
            tree=tree,
        )

        self.assertTrue(result["summary"]["has_database"])
        db_signals = [s for s in result["architecture_signals"] if s["type"] == "DATABASE"]
        self.assertEqual(len(db_signals), 1)
        self.assertIn("schema.prisma", db_signals[0]["evidence"])


class TestRepositoryArchitectureAPI(unittest.TestCase):
    """Integration tests for the repository architecture FastAPI endpoint."""

    def setUp(self):
        self.client = TestClient(app)

    @patch("app.services.github_service.github_service.get_repository_details")
    @patch("app.services.github_service.github_service.get_repository_tree")
    def test_10_api_valid_request(self, mock_tree, mock_details):
        """Test 10: POST /api/v1/repository-architecture/analyze returns 200 with schema conformant data."""
        mock_details.return_value = SAMPLE_REPO_DETAILS
        mock_tree.return_value = SAMPLE_FULL_STACK_TREE

        response = self.client.post(
            "/api/v1/repository-architecture/analyze",
            json={"owner": "octocat", "repo": "fullstack-platform"},
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertEqual(data["repository"]["name"], "fullstack-platform")
        self.assertEqual(data["project_type"], PROJECT_TYPE_FULL_STACK)
        self.assertTrue(data["summary"]["has_frontend"])
        self.assertTrue(data["summary"]["has_backend"])
        self.assertGreater(data["summary"]["total_files_analyzed"], 0)

    def test_11_api_invalid_request(self):
        """Test 11: Missing or whitespace-only owner/repo returns 422 Unprocessable Entity."""
        # Whitespace-only owner
        res1 = self.client.post(
            "/api/v1/repository-architecture/analyze",
            json={"owner": "   ", "repo": "Hello-World"},
        )
        self.assertEqual(res1.status_code, 422)

        # Missing repo
        res2 = self.client.post(
            "/api/v1/repository-architecture/analyze",
            json={"owner": "octocat"},
        )
        self.assertEqual(res2.status_code, 422)

    @patch("app.services.github_service.github_service.get_repository_details")
    def test_12_api_github_errors(self, mock_details):
        """Test 12: Repository not found (404) and upstream failures (502) return appropriate status."""
        # 1. 404 Not Found
        mock_details.side_effect = GitHubRepositoryNotFoundError("Repository not found")
        res_404 = self.client.post(
            "/api/v1/repository-architecture/analyze",
            json={"owner": "octocat", "repo": "nonexistent"},
        )
        self.assertEqual(res_404.status_code, 404)

        # 2. 502 Upstream failure
        mock_details.side_effect = GitHubAPIError("Rate limit exceeded", status_code=502)
        res_502 = self.client.post(
            "/api/v1/repository-architecture/analyze",
            json={"owner": "octocat", "repo": "rate-limited"},
        )
        self.assertEqual(res_502.status_code, 502)


if __name__ == "__main__":
    unittest.main()
