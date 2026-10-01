"""
verify_resume.py
----------------
Command-line verification script for Resume Analysis module.
Tests parser, skill extraction, normalization, deduplication, structured sections, and API contract.

Usage:
    .\\backend\\venv\\Scripts\\python.exe scripts\\verify_resume.py
"""

import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from fastapi.testclient import TestClient

from app.main import app
from app.services.resume_service import resume_service


SAMPLE_RESUME = """SUMMARY
Computer engineering student interested in AI and data science.

TECHNICAL SKILLS
Python, C++, SQL, Pandas, NumPy, Machine Learning, cpp, c++, python

EDUCATION
Government Polytechnic Nashik
Diploma in Computer Technology
2022 - 2025

PROJECTS
Fake Profile Detection
Built a machine learning system using Random Forest.

EXPERIENCE
Python Intern
Company XYZ
June 2025 - August 2025
Developed automated pipelines.

CERTIFICATIONS
Python Certification
AWS Cloud Practitioner
"""


def main() -> int:
    client = TestClient(app)
    failures = []

    print("Resume Analysis Verification")
    print("----------------------------")

    # 1. Resume parsed
    try:
        parsed = resume_service.analyze_resume(SAMPLE_RESUME)
        if parsed and parsed.get("summary"):
            print("Resume parsed: PASS")
        else:
            print("Resume parsed: FAIL (empty or invalid output)")
            failures.append("Resume parsed")
    except Exception as exc:
        print(f"Resume parsed: FAIL ({exc})")
        failures.append("Resume parsed")
        return 1

    # 2. Skills extracted
    try:
        skills = parsed.get("skills", [])
        if "Python" in skills and "SQL" in skills:
            print("Skills extracted: PASS")
        else:
            print(f"Skills extracted: FAIL (skills found: {skills})")
            failures.append("Skills extracted")
    except Exception as exc:
        print(f"Skills extracted: FAIL ({exc})")
        failures.append("Skills extracted")

    # 3. Skills normalized
    try:
        # Check that cpp/c++ became C++ and python became Python
        if "C++" in skills and "cpp" not in skills and "c++" not in skills:
            print("Skills normalized: PASS")
        else:
            print("Skills normalized: FAIL (aliases not canonicalized)")
            failures.append("Skills normalized")
    except Exception as exc:
        print(f"Skills normalized: FAIL ({exc})")
        failures.append("Skills normalized")

    # 4. Duplicate skills removed
    try:
        # Check that Python and C++ each appear exactly once
        if skills.count("Python") == 1 and skills.count("C++") == 1:
            print("Duplicate skills removed: PASS")
        else:
            print(f"Duplicate skills removed: FAIL (skills: {skills})")
            failures.append("Duplicate skills removed")
    except Exception as exc:
        print(f"Duplicate skills removed: FAIL ({exc})")
        failures.append("Duplicate skills removed")

    # 5. Projects extracted
    try:
        projects = parsed.get("projects", [])
        if (
            len(projects) >= 1
            and projects[0].get("name") == "Fake Profile Detection"
            and "Machine Learning" in projects[0].get("technologies", [])
        ):
            print("Projects extracted: PASS")
        else:
            print(f"Projects extracted: FAIL ({projects})")
            failures.append("Projects extracted")
    except Exception as exc:
        print(f"Projects extracted: FAIL ({exc})")
        failures.append("Projects extracted")

    # 6. Education extracted
    try:
        education = parsed.get("education", [])
        if (
            len(education) >= 1
            and "Government Polytechnic Nashik" in education[0].get("institution", "")
            and education[0].get("degree") == "Diploma"
            and education[0].get("start_year") == "2022"
            and education[0].get("end_year") == "2025"
        ):
            print("Education extracted: PASS")
        else:
            print(f"Education extracted: FAIL ({education})")
            failures.append("Education extracted")
    except Exception as exc:
        print(f"Education extracted: FAIL ({exc})")
        failures.append("Education extracted")

    # 7. Experience extracted
    try:
        experience = parsed.get("experience", [])
        if (
            len(experience) >= 1
            and experience[0].get("company") == "Company XYZ"
            and experience[0].get("role") == "Python Intern"
            and experience[0].get("start_date") == "June 2025"
            and experience[0].get("end_date") == "August 2025"
        ):
            print("Experience extracted: PASS")
        else:
            print(f"Experience extracted: FAIL ({experience})")
            failures.append("Experience extracted")
    except Exception as exc:
        print(f"Experience extracted: FAIL ({exc})")
        failures.append("Experience extracted")

    # 8. Certifications extracted
    try:
        certs = parsed.get("certifications", [])
        if len(certs) >= 2 and "Python Certification" in certs:
            print("Certifications extracted: PASS")
        else:
            print(f"Certifications extracted: FAIL ({certs})")
            failures.append("Certifications extracted")
    except Exception as exc:
        print(f"Certifications extracted: FAIL ({exc})")
        failures.append("Certifications extracted")

    # 9. API contract
    try:
        response = client.post("/api/v1/resume/analyze", json={"resume_text": SAMPLE_RESUME})
        if response.status_code == 200:
            data = response.json()
            required_keys = [
                "summary",
                "skills",
                "education",
                "experience",
                "projects",
                "certifications",
                "achievements",
                "skill_count",
                "project_count",
                "experience_count",
            ]
            if all(k in data for k in required_keys):
                print("API contract: PASS")
            else:
                print("API contract: FAIL (missing expected keys)")
                failures.append("API contract")
        else:
            print(f"API contract: FAIL (status {response.status_code})")
            failures.append("API contract")
    except Exception as exc:
        print(f"API contract: FAIL ({exc})")
        failures.append("API contract")

    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
