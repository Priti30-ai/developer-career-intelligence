"""
verify_developer_profile.py
---------------------------
Command-line verification script for Unified Developer Profile Synthesis.

Runs deterministic standalone checks for:
1. Normalization and duplicate alias removal
2. GitHub + Resume skill merging and deduplication
3. Accurate source tracking ('github', 'resume', both)
4. Evidence preservation (STRONG, MODERATE, NONE_DETECTED)
5. Summary count calculations and mathematical invariants
6. Resume-only skill semantic integrity (NONE_DETECTED != lack of skill)
7. Downstream Job Description Matching integration
8. API endpoint validation and error handling

Usage:
    .\\backend\\venv\\Scripts\\python.exe scripts\\verify_developer_profile.py
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
from app.schemas.developer_profile import (
    SOURCE_GITHUB,
    SOURCE_RESUME,
    DeveloperProfileResponse,
)
from app.services.developer_profile_service import (
    developer_profile_service,
    extract_developer_skills,
)
from app.services.evidence_service import (
    EVIDENCE_LEVEL_MODERATE,
    EVIDENCE_LEVEL_NONE_DETECTED,
    EVIDENCE_LEVEL_STRONG,
)
from app.services.github_service import GitHubUserNotFoundError
from app.services.job_matching_service import job_matching_service

SAMPLE_REPOSITORIES = [
    {
        "name": "ai-profiler",
        "full_name": "octocat/ai-profiler",
        "description": "ML profiler tool",
        "html_url": "https://github.com/octocat/ai-profiler",
        "language": "Python",
        "topics": ["machine-learning", "pandas"],
    },
    {
        "name": "api-service",
        "full_name": "octocat/api-service",
        "description": "Core backend API",
        "html_url": "https://github.com/octocat/api-service",
        "language": "Python",
        "topics": ["fastapi", "machine-learning"],
    },
    {
        "name": "web-frontend",
        "full_name": "octocat/web-frontend",
        "description": "React UI dashboard",
        "html_url": "https://github.com/octocat/web-frontend",
        "language": "TypeScript",
        "topics": ["react", "css"],
    },
]


def main() -> int:
    client = TestClient(app)
    failures = []

    print("==================================================")
    print("Unified Developer Profile Synthesis Verification")
    print("==================================================")

    # 1. Normalization & Duplicate Removal
    try:
        norm = developer_profile_service.normalize_skills(
            ["python", "Python", "PYTHON", "fastapi", "FastAPI", "js", "javascript"]
        )
        if norm == ["Python", "FastAPI", "JavaScript"]:
            print("1. Normalization & duplicate removal: PASS")
        else:
            print(f"1. Normalization & duplicate removal: FAIL (got {norm})")
            failures.append("Normalization & duplicate removal")
    except Exception as exc:
        print(f"1. Normalization & duplicate removal: FAIL ({exc})")
        failures.append("Normalization & duplicate removal")

    # Run base profile synthesis
    try:
        profile = asyncio.run(
            developer_profile_service.synthesize_profile(
                username="octocat",
                resume_skills=["Python", "FastAPI", "SQL", "Docker"],
                repositories=SAMPLE_REPOSITORIES,
            )
        )
        skills_map = {s["skill"]: s for s in profile["skills"]}
    except Exception as exc:
        print(f"Base profile synthesis: FAIL ({exc})")
        return 1

    # 2. Skill Merging & Deduplication
    try:
        all_skills = list(skills_map.keys())
        expected_skills = [
            "CSS",
            "Docker",
            "FastAPI",
            "Machine Learning",
            "Pandas",
            "Python",
            "React",
            "SQL",
            "TypeScript",
        ]
        if sorted(all_skills) == sorted(expected_skills):
            print("2. GitHub + Resume skill merging: PASS")
        else:
            print(f"2. GitHub + Resume skill merging: FAIL (got {all_skills})")
            failures.append("Skill merging")
    except Exception as exc:
        print(f"2. GitHub + Resume skill merging: FAIL ({exc})")
        failures.append("Skill merging")

    # 3. Source Tracking
    try:
        py_sources = skills_map["Python"]["sources"]
        react_sources = skills_map["React"]["sources"]
        sql_sources = skills_map["SQL"]["sources"]

        if (
            SOURCE_GITHUB in py_sources
            and SOURCE_RESUME in py_sources
            and react_sources == [SOURCE_GITHUB]
            and sql_sources == [SOURCE_RESUME]
        ):
            print("3. Source tracking ('github', 'resume', both): PASS")
        else:
            print(
                f"3. Source tracking: FAIL (Python: {py_sources}, React: {react_sources}, SQL: {sql_sources})"
            )
            failures.append("Source tracking")
    except Exception as exc:
        print(f"3. Source tracking: FAIL ({exc})")
        failures.append("Source tracking")

    # 4. Evidence Classification Preservation
    try:
        py_evidence = skills_map["Python"]["evidence_status"]
        fastapi_evidence = skills_map["FastAPI"]["evidence_status"]
        sql_evidence = skills_map["SQL"]["evidence_status"]

        if (
            py_evidence == EVIDENCE_LEVEL_STRONG
            and fastapi_evidence == EVIDENCE_LEVEL_MODERATE
            and sql_evidence == EVIDENCE_LEVEL_NONE_DETECTED
            and len(skills_map["Python"]["supporting_repositories"]) == 2
            and len(skills_map["FastAPI"]["supporting_repositories"]) == 1
            and len(skills_map["SQL"]["supporting_repositories"]) == 0
        ):
            print("4. Evidence preservation (STRONG, MODERATE, NONE_DETECTED): PASS")
        else:
            print(
                f"4. Evidence preservation: FAIL (Py: {py_evidence}, FastAPI: {fastapi_evidence}, SQL: {sql_evidence})"
            )
            failures.append("Evidence preservation")
    except Exception as exc:
        print(f"4. Evidence preservation: FAIL ({exc})")
        failures.append("Evidence preservation")

    # 5. Summary Counts & Mathematical Invariants
    try:
        summary = profile["summary"]
        inv1 = (
            summary["total_skills"]
            == summary["supported_skill_count"] + summary["skills_without_github_evidence"]
        )
        inv2 = (
            summary["total_skills"]
            == summary["github_skill_count"]
            + summary["resume_skill_count"]
            - summary["skills_from_both_sources"]
        )

        if (
            summary["total_skills"] == 9
            and summary["github_skill_count"] == 7
            and summary["resume_skill_count"] == 4
            and summary["skills_from_both_sources"] == 2
            and summary["supported_skill_count"] == 7
            and summary["skills_without_github_evidence"] == 2
            and inv1
            and inv2
        ):
            print("5. Summary counts & mathematical invariants: PASS")
        else:
            print(f"5. Summary counts & invariants: FAIL ({summary}, inv1={inv1}, inv2={inv2})")
            failures.append("Summary counts & invariants")
    except Exception as exc:
        print(f"5. Summary counts & invariants: FAIL ({exc})")
        failures.append("Summary counts & invariants")

    # 6. Resume-Only Skill Semantics
    try:
        sql = skills_map.get("SQL")
        if (
            sql
            and sql["evidence_status"] == EVIDENCE_LEVEL_NONE_DETECTED
            and sql["sources"] == [SOURCE_RESUME]
            and "SQL" in profile["resume"]["skills"]
            and "SQL" in [s["skill"] for s in profile["skills"]]
        ):
            print("6. Resume-only skill semantic integrity (retained, non-punitive): PASS")
        else:
            print(f"6. Resume-only skill semantic integrity: FAIL ({sql})")
            failures.append("Resume-only skill semantics")
    except Exception as exc:
        print(f"6. Resume-only skill semantic integrity: FAIL ({exc})")
        failures.append("Resume-only skill semantics")

    # 7. Downstream Job Matching Integration
    try:
        resp_model = DeveloperProfileResponse(**profile)
        dev_skills = resp_model.get_skill_names()
        extracted_skills = extract_developer_skills(profile)

        jd_text = "Looking for a backend software engineer with Python, FastAPI, and SQL experience."
        match = job_matching_service.match_job_description(
            job_description=jd_text,
            developer_skills=extracted_skills,
        )

        if (
            sorted(dev_skills) == sorted(extracted_skills)
            and match["match_percentage"] == 100.0
            and len(match["missing_skills"]) == 0
            and "Python" in match["matched_skills"]
            and "FastAPI" in match["matched_skills"]
            and "SQL" in match["matched_skills"]
        ):
            print("7. Downstream Job Description Matching integration: PASS")
        else:
            print(f"7. Downstream Job Matching integration: FAIL (match: {match})")
            failures.append("Downstream Job Matching integration")
    except Exception as exc:
        print(f"7. Downstream Job Matching integration: FAIL ({exc})")
        failures.append("Downstream Job Matching integration")

    # 8. API Contract & Error Handling
    try:
        with patch(
            "app.services.github_service.github_service.get_user_repositories"
        ) as mock_repos:
            mock_repos.return_value = SAMPLE_REPOSITORIES

            # Valid request
            res_valid = client.post(
                "/api/v1/developer-profile/analyze",
                json={
                    "github_username": "octocat",
                    "resume_skills": ["Python", "SQL"],
                },
            )
            val_ok = (
                res_valid.status_code == 200
                and res_valid.json()["developer_id"] == "octocat"
                and res_valid.json()["summary"]["total_skills"] > 0
            )

            # Invalid blank username
            res_invalid = client.post(
                "/api/v1/developer-profile/analyze",
                json={"github_username": "   "},
            )
            inv_ok = res_invalid.status_code == 422

            # User not found error
            mock_repos.side_effect = GitHubUserNotFoundError("User missing not found")
            res_404 = client.post(
                "/api/v1/developer-profile/analyze",
                json={"github_username": "missing"},
            )
            notfound_ok = res_404.status_code == 404

        if val_ok and inv_ok and notfound_ok:
            print("8. API endpoint validation & error handling: PASS")
        else:
            print(
                f"8. API endpoint: FAIL (val={res_valid.status_code}, inv={res_invalid.status_code}, 404={res_404.status_code})"
            )
            failures.append("API endpoint validation")
    except Exception as exc:
        print(f"8. API endpoint validation & error handling: FAIL ({exc})")
        failures.append("API endpoint validation")

    print("--------------------------------------------------")
    if not failures:
        print("ALL 8 VERIFICATION CHECKS PASSED")
        return 0
    else:
        print(f"{len(failures)} VERIFICATION CHECKS FAILED: {', '.join(failures)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
