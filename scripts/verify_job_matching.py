"""
verify_job_matching.py
----------------------
Command-line verification script for Job Description Analysis and Matching.
Runs deterministic standalone checks for skill extraction, normalization, duplicate removal,
complete match, partial match, zero match, empty detectable-skill behavior, and API contract.

Usage:
    .\\backend\\venv\\Scripts\\python.exe scripts\\verify_job_matching.py
"""

import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from fastapi.testclient import TestClient

from app.main import app
from app.services.job_description_service import job_description_service
from app.services.job_matching_service import job_matching_service

SAMPLE_JD = """Backend Engineer Position
We are looking for a software engineer proficient in Python and FastAPI.
Must have experience with Docker, PostgreSQL, and Git.
Knowledge of React and Node.js is a plus.
"""


def main() -> int:
    client = TestClient(app)
    failures = []

    print("Job Description Analysis and Matching Verification")
    print("---------------------------------------------------")

    # 1. Skill extraction
    try:
        skills = job_description_service.extract_skills(SAMPLE_JD)
        expected = ["Docker", "FastAPI", "Git", "Node.js", "PostgreSQL", "Python", "React"]
        if all(s in skills for s in expected):
            print("Skill extraction: PASS")
        else:
            print(f"Skill extraction: FAIL (extracted: {skills})")
            failures.append("Skill extraction")
    except Exception as exc:
        print(f"Skill extraction: FAIL ({exc})")
        failures.append("Skill extraction")

    # 2. Normalization
    try:
        norm_jd = "Looking for skills in nodejs, cpp, c++, sklearn, and postgres."
        norm_skills = job_description_service.extract_skills(norm_jd)
        if (
            "Node.js" in norm_skills
            and "C++" in norm_skills
            and "Scikit-learn" in norm_skills
            and "PostgreSQL" in norm_skills
            and "nodejs" not in norm_skills
            and "cpp" not in norm_skills
            and "sklearn" not in norm_skills
        ):
            print("Normalization: PASS")
        else:
            print(f"Normalization: FAIL (extracted: {norm_skills})")
            failures.append("Normalization")
    except Exception as exc:
        print(f"Normalization: FAIL ({exc})")
        failures.append("Normalization")

    # 3. Duplicate removal
    try:
        dup_jd = "Python, python, PYTHON, and cpp, c++, C++ required."
        dup_skills = job_description_service.extract_skills(dup_jd)
        if dup_skills == ["C++", "Python"]:
            print("Duplicate removal: PASS")
        else:
            print(f"Duplicate removal: FAIL (extracted: {dup_skills})")
            failures.append("Duplicate removal")
    except Exception as exc:
        print(f"Duplicate removal: FAIL ({exc})")
        failures.append("Duplicate removal")

    # 4. Complete match
    try:
        match_full = job_matching_service.match_job_description(
            job_description="Requirements: Python, Docker, PostgreSQL",
            developer_skills=["python", "docker", "postgresql"],
        )
        if (
            match_full["total_required_skills"] == 3
            and match_full["matched_skill_count"] == 3
            and match_full["missing_skill_count"] == 0
            and match_full["match_percentage"] == 100.0
            and match_full["missing_skills"] == []
        ):
            print("Complete match: PASS")
        else:
            print(f"Complete match: FAIL ({match_full})")
            failures.append("Complete match")
    except Exception as exc:
        print(f"Complete match: FAIL ({exc})")
        failures.append("Complete match")

    # 5. Partial match
    try:
        match_part = job_matching_service.match_job_description(
            job_description="Requirements: Python, Docker, PostgreSQL, Kubernetes",
            developer_skills=["Python", "Docker"],
        )
        if (
            match_part["total_required_skills"] == 4
            and match_part["matched_skill_count"] == 2
            and match_part["missing_skill_count"] == 2
            and match_part["match_percentage"] == 50.0
            and match_part["matched_skills"] == ["Docker", "Python"]
            and match_part["missing_skills"] == ["Kubernetes", "PostgreSQL"]
        ):
            print("Partial match: PASS")
        else:
            print(f"Partial match: FAIL ({match_part})")
            failures.append("Partial match")
    except Exception as exc:
        print(f"Partial match: FAIL ({exc})")
        failures.append("Partial match")

    # 6. Zero match
    try:
        match_zero = job_matching_service.match_job_description(
            job_description="Requirements: Java, Rust, Kotlin",
            developer_skills=["Python", "FastAPI"],
        )
        if (
            match_zero["total_required_skills"] == 3
            and match_zero["matched_skill_count"] == 0
            and match_zero["missing_skill_count"] == 3
            and match_zero["match_percentage"] == 0.0
        ):
            print("Zero match: PASS")
        else:
            print(f"Zero match: FAIL ({match_zero})")
            failures.append("Zero match")
    except Exception as exc:
        print(f"Zero match: FAIL ({exc})")
        failures.append("Zero match")

    # 7. Empty detectable-skill behavior
    try:
        match_empty = job_matching_service.match_job_description(
            job_description="General office administrative assistant required. Excellent phone skills.",
            developer_skills=["Python", "React"],
        )
        if (
            match_empty["total_required_skills"] == 0
            and match_empty["matched_skill_count"] == 0
            and match_empty["missing_skill_count"] == 0
            and match_empty["match_percentage"] == 0.0
            and match_empty["extracted_skills"] == []
        ):
            print("Empty detectable-skill behavior: PASS")
        else:
            print(f"Empty detectable-skill behavior: FAIL ({match_empty})")
            failures.append("Empty detectable-skill behavior")
    except Exception as exc:
        print(f"Empty detectable-skill behavior: FAIL ({exc})")
        failures.append("Empty detectable-skill behavior")

    # 8. API response behavior
    try:
        payload = {
            "job_description": SAMPLE_JD,
            "developer_skills": ["Python", "FastAPI", "Docker"],
        }
        resp = client.post("/api/v1/job-matching/analyze", json=payload)
        if resp.status_code == 200:
            data = resp.json()
            required_keys = [
                "extracted_skills",
                "developer_skills",
                "matched_skills",
                "missing_skills",
                "total_required_skills",
                "matched_skill_count",
                "missing_skill_count",
                "match_percentage",
                "explanation",
            ]
            if (
                all(k in data for k in required_keys)
                and data["matched_skill_count"] + data["missing_skill_count"] == data["total_required_skills"]
            ):
                print("API response behavior: PASS")
            else:
                print(f"API response behavior: FAIL (payload: {data})")
                failures.append("API response behavior")
        else:
            print(f"API response behavior: FAIL (status {resp.status_code})")
            failures.append("API response behavior")
    except Exception as exc:
        print(f"API response behavior: FAIL ({exc})")
        failures.append("API response behavior")

    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
