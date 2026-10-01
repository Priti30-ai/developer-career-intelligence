"""
verify_repository_architecture.py
---------------------------------
Command-line verification script for GitHub Repository Architecture Analysis.

Runs deterministic standalone checks for:
1. Tree normalization & nested directory inference
2. Frontend structure detection (FRONTEND)
3. Backend service detection (BACKEND)
4. Full-stack architecture synthesis (FULL_STACK)
5. Dependency manifest detection (package.json, requirements.txt, pyproject.toml)
6. Documentation files detection (README.md, docs/)
7. Concrete architecture signals generation
8. Project classification determinism
9. Weak evidence semantics (models/ alone != database claim)
10. API endpoint contract and error handling

Usage:
    .\\backend\\venv\\Scripts\\python.exe scripts\\verify_repository_architecture.py
"""

import asyncio
import sys
from pathlib import Path
from unittest.mock import patch

# Ensure backend directory is in sys.path
backend_dir = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from fastapi.testclient import TestClient

from app.main import app
from app.services.github_service import GitHubRepositoryNotFoundError
from app.services.repository_architecture_service import (
    PROJECT_TYPE_BACKEND,
    PROJECT_TYPE_FRONTEND,
    PROJECT_TYPE_FULL_STACK,
    repository_architecture_service,
)

SAMPLE_FULL_STACK_TREE = [
    {"path": "frontend/package.json", "type": "blob"},
    {"path": "frontend/vite.config.ts", "type": "blob"},
    {"path": "frontend/src/App.tsx", "type": "blob"},
    {"path": "frontend/src/components/Navbar.tsx", "type": "blob"},
    {"path": "backend/requirements.txt", "type": "blob"},
    {"path": "backend/app/main.py", "type": "blob"},
    {"path": "backend/app/api/endpoints.py", "type": "blob"},
    {"path": "backend/app/services/auth.py", "type": "blob"},
    {"path": "backend/migrations/001_initial.sql", "type": "blob"},
    {"path": "Dockerfile", "type": "blob"},
    {"path": "docker-compose.yml", "type": "blob"},
    {"path": "README.md", "type": "blob"},
    {"path": "docs/architecture.md", "type": "blob"},
    {"path": "tests/test_api.py", "type": "blob"},
]


def main() -> int:
    client = TestClient(app)
    failures = []

    print("==================================================")
    print("Repository Architecture Analysis Verification")
    print("==================================================")

    # 1. Tree parsing & directory inference
    try:
        raw_tree = [
            {"path": "src/components/Header.tsx", "type": "blob"},
            {"path": "backend/api/routes.py", "type": "blob"},
            {"path": "README.md", "type": "blob"},
        ]
        files, dirs = repository_architecture_service.normalize_tree_paths(raw_tree)
        if (
            "src/components/Header.tsx" in files
            and "src" in dirs
            and "src/components" in dirs
            and "backend" in dirs
            and "backend/api" in dirs
        ):
            print("1. Tree parsing and directory inference: PASS")
        else:
            print(f"1. Tree parsing: FAIL (files={files}, dirs={dirs})")
            failures.append("Tree parsing")
    except Exception as exc:
        print(f"1. Tree parsing: FAIL ({exc})")
        failures.append("Tree parsing")

    # 2. Frontend detection
    try:
        fe_tree = [
            {"path": "package.json", "type": "blob"},
            {"path": "vite.config.ts", "type": "blob"},
            {"path": "src/App.tsx", "type": "blob"},
            {"path": "src/components/Card.tsx", "type": "blob"},
        ]
        fe_res = asyncio.run(
            repository_architecture_service.analyze_repository(
                owner="octocat",
                repo="fe-app",
                repository_details={"name": "fe-app", "language": "TypeScript"},
                tree=fe_tree,
            )
        )
        if (
            fe_res["project_type"] == PROJECT_TYPE_FRONTEND
            and fe_res["summary"]["has_frontend"]
            and not fe_res["summary"]["has_backend"]
        ):
            print("2. Frontend structure detection: PASS")
        else:
            print(f"2. Frontend detection: FAIL ({fe_res['project_type']})")
            failures.append("Frontend detection")
    except Exception as exc:
        print(f"2. Frontend detection: FAIL ({exc})")
        failures.append("Frontend detection")

    # 3. Backend detection
    try:
        be_tree = [
            {"path": "requirements.txt", "type": "blob"},
            {"path": "app/main.py", "type": "blob"},
            {"path": "app/api/v1/routes.py", "type": "blob"},
            {"path": "app/services/item_service.py", "type": "blob"},
        ]
        be_res = asyncio.run(
            repository_architecture_service.analyze_repository(
                owner="octocat",
                repo="be-app",
                repository_details={"name": "be-app", "language": "Python"},
                tree=be_tree,
            )
        )
        if (
            be_res["project_type"] == PROJECT_TYPE_BACKEND
            and be_res["summary"]["has_backend"]
            and not be_res["summary"]["has_frontend"]
        ):
            print("3. Backend structure detection: PASS")
        else:
            print(f"3. Backend detection: FAIL ({be_res['project_type']})")
            failures.append("Backend detection")
    except Exception as exc:
        print(f"3. Backend detection: FAIL ({exc})")
        failures.append("Backend detection")

    # 4. Full-stack detection
    try:
        fs_res = asyncio.run(
            repository_architecture_service.analyze_repository(
                owner="octocat",
                repo="fullstack-app",
                repository_details={"name": "fullstack-app", "language": "Python"},
                tree=SAMPLE_FULL_STACK_TREE,
            )
        )
        if (
            fs_res["project_type"] == PROJECT_TYPE_FULL_STACK
            and fs_res["summary"]["has_frontend"]
            and fs_res["summary"]["has_backend"]
        ):
            print("4. Full-stack architecture classification: PASS")
        else:
            print(f"4. Full-stack detection: FAIL ({fs_res['project_type']})")
            failures.append("Full-stack detection")
    except Exception as exc:
        print(f"4. Full-stack detection: FAIL ({exc})")
        failures.append("Full-stack detection")

    # 5. Dependency manifest detection
    try:
        deps = fs_res["dependency_files"]
        if "frontend/package.json" in deps and "backend/requirements.txt" in deps:
            print("5. Dependency manifest identification: PASS")
        else:
            print(f"5. Dependency manifests: FAIL (got {deps})")
            failures.append("Dependency manifests")
    except Exception as exc:
        print(f"5. Dependency manifests: FAIL ({exc})")
        failures.append("Dependency manifests")

    # 6. Documentation files detection
    try:
        docs = fs_res["documentation_files"]
        if "README.md" in docs and "docs/architecture.md" in docs:
            print("6. Documentation files detection: PASS")
        else:
            print(f"6. Documentation detection: FAIL (got {docs})")
            failures.append("Documentation detection")
    except Exception as exc:
        print(f"6. Documentation detection: FAIL ({exc})")
        failures.append("Documentation detection")

    # 7. Concrete architecture signals
    try:
        signals = fs_res["architecture_signals"]
        types = [s["type"] for s in signals]
        all_have_evidence = all(len(s["evidence"]) > 0 for s in signals)
        if (
            "FRONTEND" in types
            and "BACKEND" in types
            and "DATABASE" in types
            and "DEVOPS" in types
            and all_have_evidence
        ):
            print("7. Concrete architecture signals with evidence paths: PASS")
        else:
            print(f"7. Architecture signals: FAIL (types={types}, evidence_check={all_have_evidence})")
            failures.append("Architecture signals")
    except Exception as exc:
        print(f"7. Architecture signals: FAIL ({exc})")
        failures.append("Architecture signals")

    # 8. Weak evidence semantics (models/ alone != database claim)
    try:
        weak_tree = [
            {"path": "models/user.py", "type": "blob"},
            {"path": "models/product.py", "type": "blob"},
            {"path": "main.py", "type": "blob"},
        ]
        weak_res = asyncio.run(
            repository_architecture_service.analyze_repository(
                owner="octocat",
                repo="weak-repo",
                repository_details={"name": "weak-repo"},
                tree=weak_tree,
            )
        )
        db_signals = [s for s in weak_res["architecture_signals"] if s["type"] == "DATABASE"]
        model_signals = [s for s in weak_res["architecture_signals"] if s["type"] == "MODELS"]
        if (
            not weak_res["summary"]["has_database"]
            and len(db_signals) == 0
            and len(model_signals) == 1
            and "models/" in model_signals[0]["evidence"]
        ):
            print("8. Weak evidence semantics (models/ != confirmed database): PASS")
        else:
            print(f"8. Weak evidence: FAIL (has_db={weak_res['summary']['has_database']}, db_signals={db_signals})")
            failures.append("Weak evidence semantics")

    except Exception as exc:
        print(f"8. Weak evidence semantics: FAIL ({exc})")
        failures.append("Weak evidence semantics")

    # 9. Concrete database evidence recognition
    try:
        db_tree = [
            {"path": "migrations/0001_create.sql", "type": "blob"},
            {"path": "schema.prisma", "type": "blob"},
            {"path": "index.js", "type": "blob"},
        ]
        db_res = asyncio.run(
            repository_architecture_service.analyze_repository(
                owner="octocat",
                repo="db-repo",
                repository_details={"name": "db-repo"},
                tree=db_tree,
            )
        )
        if (
            db_res["summary"]["has_database"]
            and any(s["type"] == "DATABASE" for s in db_res["architecture_signals"])
        ):
            print("9. Concrete database evidence recognition (SQL, migrations, prisma): PASS")
        else:
            print(f"9. Concrete database evidence: FAIL")
            failures.append("Concrete database evidence")
    except Exception as exc:
        print(f"9. Concrete database evidence: FAIL ({exc})")
        failures.append("Concrete database evidence")

    # 10. API endpoint contract & error handling
    try:
        with patch("app.services.github_service.github_service.get_repository_details") as mock_details, \
             patch("app.services.github_service.github_service.get_repository_tree") as mock_tree:
            mock_details.return_value = {"name": "fullstack-app", "language": "Python"}
            mock_tree.return_value = SAMPLE_FULL_STACK_TREE

            # Valid request
            res_valid = client.post(
                "/api/v1/repository-architecture/analyze",
                json={"owner": "octocat", "repo": "fullstack-app"},
            )
            v_ok = (
                res_valid.status_code == 200
                and res_valid.json()["project_type"] == PROJECT_TYPE_FULL_STACK
                and res_valid.json()["summary"]["has_frontend"]
            )

            # Invalid blank owner
            res_invalid = client.post(
                "/api/v1/repository-architecture/analyze",
                json={"owner": "   ", "repo": "app"},
            )
            inv_ok = res_invalid.status_code == 422

            # 404 Not Found
            mock_details.side_effect = GitHubRepositoryNotFoundError("Repo not found")
            res_404 = client.post(
                "/api/v1/repository-architecture/analyze",
                json={"owner": "octocat", "repo": "missing"},
            )
            notfound_ok = res_404.status_code == 404

        if v_ok and inv_ok and notfound_ok:
            print("10. API contract validation and error handling: PASS")
        else:
            print(f"10. API contract: FAIL (v_ok={v_ok}, inv_ok={inv_ok}, notfound_ok={notfound_ok})")
            failures.append("API contract")
    except Exception as exc:
        print(f"10. API contract: FAIL ({exc})")
        failures.append("API contract")

    print("--------------------------------------------------")
    if not failures:
        print("ALL 10 VERIFICATION CHECKS PASSED")
        return 0
    else:
        print(f"{len(failures)} CHECKS FAILED: {', '.join(failures)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
