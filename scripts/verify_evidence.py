"""
verify_evidence.py
------------------
Command-line verification script for Resume vs GitHub Evidence Analysis.
Runs deterministic standalone checks across normalization, matching, evidence levels,
coverage calculation, error handling, and API contracts.

Usage:
    .\\backend\\venv\\Scripts\\python.exe scripts\\verify_evidence.py
"""

import asyncio
import sys
from pathlib import Path
from unittest.mock import patch

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from fastapi.testclient import TestClient

from app.main import app
from app.services.evidence_service import evidence_service
from app.services.github_service import (
    GitHubAPIError,
    GitHubUserNotFoundError,
)

SAMPLE_REPOS = [
    {
        "name": "fake-profile-detector",
        "full_name": "testuser/fake-profile-detector",
        "description": "ML detection tool",
        "html_url": "https://github.com/testuser/fake-profile-detector",
        "language": "Python",
        "topics": ["machine-learning", "pandas"],
    },
    {
        "name": "career-intelligence",
        "full_name": "testuser/career-intelligence",
        "description": "Backend API",
        "html_url": "https://github.com/testuser/career-intelligence",
        "language": "Python",
        "topics": ["fastapi", "machine-learning"],
    },
    {
        "name": "portfolio",
        "full_name": "testuser/portfolio",
        "description": "Personal frontend portfolio",
        "html_url": "https://github.com/testuser/portfolio",
        "language": "JavaScript",
        "topics": ["react"],
    },
]


def main() -> int:
    client = TestClient(app)
    failures = []

    print("Resume vs GitHub Evidence Verification")
    print("---------------------------------------")

    # 1. Skill normalization
    try:
        norm = evidence_service.normalize_resume_skills(
            resume_skills=["python", "Python", "cpp", "c++", "nodejs", "scikit-learn"]
        )
        if norm == ["Python", "C++", "Node.js", "Scikit-learn"]:
            print("Skill normalization: PASS")
        else:
            print(f"Skill normalization: FAIL (got: {norm})")
            failures.append("Skill normalization")
    except Exception as exc:
        print(f"Skill normalization: FAIL ({exc})")
        failures.append("Skill normalization")

    # Run base analysis with sample repos
    try:
        res = asyncio.run(
            evidence_service.analyze_evidence(
                username="testuser",
                resume_skills=["Python", "React", "Docker", "Machine Learning"],
                repositories=SAMPLE_REPOS,
            )
        )
    except Exception as exc:
        print(f"Base analysis setup: FAIL ({exc})")
        return 1

    items_by_skill = {item["skill"]: item for item in res["evidence_items"]}

    # 2. Matching skills
    try:
        py_item = items_by_skill.get("Python")
        if py_item and py_item["resume_claimed"] and py_item["github_detected"]:
            print("Matching skills: PASS")
        else:
            print(f"Matching skills: FAIL ({py_item})")
            failures.append("Matching skills")
    except Exception as exc:
        print(f"Matching skills: FAIL ({exc})")
        failures.append("Matching skills")

    # 3. Unmatched skills
    try:
        docker_item = items_by_skill.get("Docker")
        if (
            docker_item
            and docker_item["resume_claimed"]
            and not docker_item["github_detected"]
            and docker_item["evidence_level"] == "NONE_DETECTED"
        ):
            print("Unmatched skills: PASS")
        else:
            print(f"Unmatched skills: FAIL ({docker_item})")
            failures.append("Unmatched skills")
    except Exception as exc:
        print(f"Unmatched skills: FAIL ({exc})")
        failures.append("Unmatched skills")

    # 4. Repository evidence
    try:
        py_repos = py_item.get("supporting_repositories", [])
        if len(py_repos) == 2 and all(
            "name" in r and "skills_detected" in r for r in py_repos
        ):
            print("Repository evidence: PASS")
        else:
            print(f"Repository evidence: FAIL ({py_repos})")
            failures.append("Repository evidence")
    except Exception as exc:
        print(f"Repository evidence: FAIL ({exc})")
        failures.append("Repository evidence")

    # 5. Strong evidence
    try:
        ml_item = items_by_skill.get("Machine Learning")
        if (
            ml_item
            and ml_item["evidence_level"] == "STRONG"
            and len(ml_item["supporting_repositories"]) >= 2
        ):
            print("Strong evidence: PASS")
        else:
            print(f"Strong evidence: FAIL ({ml_item})")
            failures.append("Strong evidence")
    except Exception as exc:
        print(f"Strong evidence: FAIL ({exc})")
        failures.append("Strong evidence")

    # 6. Moderate evidence
    try:
        react_item = items_by_skill.get("React")
        if (
            react_item
            and react_item["evidence_level"] == "MODERATE"
            and len(react_item["supporting_repositories"]) == 1
        ):
            print("Moderate evidence: PASS")
        else:
            print(f"Moderate evidence: FAIL ({react_item})")
            failures.append("Moderate evidence")
    except Exception as exc:
        print(f"Moderate evidence: FAIL ({exc})")
        failures.append("Moderate evidence")

    # 7. None-detected evidence
    try:
        if (
            docker_item
            and docker_item["evidence_level"] == "NONE_DETECTED"
            and len(docker_item["supporting_repositories"]) == 0
        ):
            print("None-detected evidence: PASS")
        else:
            print(f"None-detected evidence: FAIL ({docker_item})")
            failures.append("None-detected evidence")
    except Exception as exc:
        print(f"None-detected evidence: FAIL ({exc})")
        failures.append("None-detected evidence")

    # 8. Coverage calculation
    try:
        summary = res["summary"]
        total = summary["total_resume_skills"]
        with_ev = summary["skills_with_evidence"]
        without_ev = summary["skills_without_evidence"]
        pct = summary["evidence_coverage_percentage"]

        if (
            total == 4
            and with_ev == 3
            and without_ev == 1
            and with_ev + without_ev == total
            and pct == 75.0
        ):
            print("Coverage calculation: PASS")
        else:
            print(f"Coverage calculation: FAIL ({summary})")
            failures.append("Coverage calculation")
    except Exception as exc:
        print(f"Coverage calculation: FAIL ({exc})")
        failures.append("Coverage calculation")

    # 9. GitHub failure handling
    try:
        with patch("app.services.evidence_service.github_service.get_user_repositories") as mock_repos:
            mock_repos.side_effect = GitHubUserNotFoundError("User nonexistent not found")
            resp_404 = client.post(
                "/api/v1/evidence/analyze",
                json={"github_username": "nonexistent", "resume_skills": ["Python"]},
            )
            mock_repos.side_effect = GitHubAPIError("Rate limit exceeded", status_code=403)
            resp_403 = client.post(
                "/api/v1/evidence/analyze",
                json={"github_username": "ratelimited", "resume_skills": ["Python"]},
            )

            if resp_404.status_code == 404 and resp_403.status_code == 403:
                print("GitHub failure handling: PASS")
            else:
                print(f"GitHub failure handling: FAIL (404: {resp_404.status_code}, 403: {resp_403.status_code})")
                failures.append("GitHub failure handling")
    except Exception as exc:
        print(f"GitHub failure handling: FAIL ({exc})")
        failures.append("GitHub failure handling")

    # 10. API contract
    try:
        with patch("app.services.evidence_service.github_service.get_user_repositories") as mock_repos:
            mock_repos.return_value = SAMPLE_REPOS
            resp = client.post(
                "/api/v1/evidence/analyze",
                json={
                    "github_username": "testuser",
                    "resume_skills": ["Python", "Docker"],
                },
            )
            if resp.status_code == 200:
                data = resp.json()
                required_keys = [
                    "github_username",
                    "resume_skills",
                    "github_skills",
                    "evidence_items",
                    "summary",
                ]
                sum_keys = [
                    "total_resume_skills",
                    "skills_with_evidence",
                    "skills_without_evidence",
                    "evidence_coverage_percentage",
                ]
                if all(k in data for k in required_keys) and all(k in data["summary"] for k in sum_keys):
                    print("API contract: PASS")
                else:
                    print("API contract: FAIL (missing expected keys in payload)")
                    failures.append("API contract")
            else:
                print(f"API contract: FAIL (status {resp.status_code})")
                failures.append("API contract")
    except Exception as exc:
        print(f"API contract: FAIL ({exc})")
        failures.append("API contract")

    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
