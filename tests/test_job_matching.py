"""
test_job_matching.py
--------------------
Unit and integration tests for Job Description Analysis and Matching.

Tests:
1. Empty job description rejected (validation)
2. Whitespace-only job description rejected (validation)
3. Overly large job description rejected (> 50,000 chars)
4. Python extraction from job description
5. Case-insensitive extraction (python, Python, PYTHON)
6. Technology alias normalization (nodejs -> Node.js, cpp -> C++, sklearn -> Scikit-learn)
7. Duplicate skill removal
8. Multiple skills extraction
9. Full skill match (100% match_percentage)
10. Partial skill match (correct percentage and missing list)
11. Zero skill match (0.0% match_percentage, all skills missing)
12. Zero detectable JD skills safe behavior (0.0% without division error)
13. API endpoint POST /api/v1/job-matching/analyze contract validation
"""

import sys
import unittest
from pathlib import Path

# Add backend directory to sys.path so 'app' imports resolve cleanly
backend_dir = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.main import app
from app.schemas.job_matching import JobMatchingRequest
from app.services.job_description_service import job_description_service
from app.services.job_matching_service import job_matching_service

SAMPLE_JD = """Senior Python Backend Engineer
We are seeking an experienced developer to join our team.

Responsibilities:
- Build high-performance APIs using FastAPI and Python
- Manage database schemas with PostgreSQL
- Deploy containerized services with Docker and Kubernetes
- Collaborate with frontend engineers using React

Requirements:
- 3+ years experience with Python
- Strong experience with Docker and PostgreSQL
- Familiarity with Git version control
"""


class TestJobMatching(unittest.TestCase):
    """Test suite for Job Description Analysis and Matching."""

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    # -----------------------------------------------------------------------
    # Validation tests
    # -----------------------------------------------------------------------

    def test_01_empty_jd_rejected(self):
        """Test 1: Empty job description is rejected by schema validator and API."""
        with self.assertRaises(ValidationError):
            JobMatchingRequest(job_description="")

        resp = self.client.post(
            "/api/v1/job-matching/analyze",
            json={"job_description": "", "developer_skills": ["Python"]},
        )
        self.assertEqual(resp.status_code, 422)

    def test_02_whitespace_only_jd_rejected(self):
        """Test 2: Whitespace-only job description is rejected by schema validator and API."""
        with self.assertRaises(ValidationError):
            JobMatchingRequest(job_description="   \n\t   \n  ")

        resp = self.client.post(
            "/api/v1/job-matching/analyze",
            json={"job_description": "   \n\t   \n  ", "developer_skills": ["Python"]},
        )
        self.assertEqual(resp.status_code, 422)

    def test_03_overly_large_jd_rejected(self):
        """Test 3: Job description exceeding 50,000 characters is safely rejected."""
        huge_text = "Python " * 10_000  # 70,000 chars
        with self.assertRaises(ValidationError):
            JobMatchingRequest(job_description=huge_text)

        resp = self.client.post(
            "/api/v1/job-matching/analyze",
            json={"job_description": huge_text, "developer_skills": ["Python"]},
        )
        self.assertEqual(resp.status_code, 422)

    # -----------------------------------------------------------------------
    # Extraction tests
    # -----------------------------------------------------------------------

    def test_04_python_extracted(self):
        """Test 4: Python is cleanly extracted from standard job text."""
        jd = "Looking for an experienced Python developer to build web services."
        extracted = job_description_service.extract_skills(jd)
        self.assertIn("Python", extracted)

    def test_05_case_insensitive_extraction(self):
        """Test 5: Extraction is case-insensitive (python, Python, PYTHON -> Python)."""
        jd1 = "Need experience in python and fastapi."
        jd2 = "Need experience in PYTHON and FASTAPI."
        jd3 = "Need experience in Python and FastAPI."

        skills1 = job_description_service.extract_skills(jd1)
        skills2 = job_description_service.extract_skills(jd2)
        skills3 = job_description_service.extract_skills(jd3)

        self.assertEqual(skills1, ["FastAPI", "Python"])
        self.assertEqual(skills2, ["FastAPI", "Python"])
        self.assertEqual(skills3, ["FastAPI", "Python"])

    def test_06_technology_alias_normalization(self):
        """Test 6: Aliases are normalized to canonical catalog names (nodejs -> Node.js, cpp -> C++, sklearn -> Scikit-learn)."""
        jd = "Tech stack includes nodejs, cpp, c++, sklearn, scikit-learn, reactjs, and postgres."
        extracted = job_description_service.extract_skills(jd)

        self.assertIn("Node.js", extracted)
        self.assertIn("C++", extracted)
        self.assertIn("Scikit-learn", extracted)
        self.assertIn("React", extracted)
        self.assertIn("PostgreSQL", extracted)

        # Aliases themselves should not appear
        self.assertNotIn("nodejs", extracted)
        self.assertNotIn("cpp", extracted)
        self.assertNotIn("sklearn", extracted)
        self.assertNotIn("reactjs", extracted)
        self.assertNotIn("postgres", extracted)

    def test_07_duplicate_skills_removed(self):
        """Test 7: Duplicate skill mentions and alias variants result in unique canonical items."""
        jd = "Python developer needed. Strong Python, python, and PYTHON skills required. Also C++ and cpp."
        extracted = job_description_service.extract_skills(jd)

        self.assertEqual(extracted.count("Python"), 1)
        self.assertEqual(extracted.count("C++"), 1)
        self.assertEqual(extracted, ["C++", "Python"])

    def test_08_multiple_skills_extracted(self):
        """Test 8: Multiple technical skills are correctly detected across paragraphs."""
        extracted = job_description_service.extract_skills(SAMPLE_JD)
        expected = ["Docker", "FastAPI", "Git", "Kubernetes", "PostgreSQL", "Python", "React"]
        for exp in expected:
            self.assertIn(exp, extracted)
        self.assertGreaterEqual(len(extracted), 7)

    # -----------------------------------------------------------------------
    # Matching tests
    # -----------------------------------------------------------------------

    def test_09_full_skill_match(self):
        """Test 9: When developer possesses all required skills, match is 100% with no missing skills."""
        jd = "Requirements: Python, Docker, PostgreSQL"
        dev_skills = ["python", "docker", "postgresql", "git"]  # extra skill included

        res = job_matching_service.match_job_description(
            job_description=jd,
            developer_skills=dev_skills,
        )

        self.assertEqual(res["total_required_skills"], 3)
        self.assertEqual(res["matched_skill_count"], 3)
        self.assertEqual(res["missing_skill_count"], 0)
        self.assertEqual(res["missing_skills"], [])
        self.assertEqual(res["match_percentage"], 100.0)
        self.assertEqual(
            res["matched_skill_count"] + res["missing_skill_count"],
            res["total_required_skills"],
        )

    def test_10_partial_skill_match(self):
        """Test 10: Partial match returns correct matched and missing lists and percentage."""
        jd = "Requirements: Python, Docker, PostgreSQL, Kubernetes"
        dev_skills = ["Python", "Docker"]  # 2 of 4

        res = job_matching_service.match_job_description(
            job_description=jd,
            developer_skills=dev_skills,
        )

        self.assertEqual(res["total_required_skills"], 4)
        self.assertEqual(res["matched_skill_count"], 2)
        self.assertEqual(res["missing_skill_count"], 2)
        self.assertEqual(res["matched_skills"], ["Docker", "Python"])
        self.assertEqual(res["missing_skills"], ["Kubernetes", "PostgreSQL"])
        self.assertEqual(res["match_percentage"], 50.0)
        self.assertEqual(
            res["matched_skill_count"] + res["missing_skill_count"],
            res["total_required_skills"],
        )

    def test_11_zero_skill_match(self):
        """Test 11: Developer possessing no matching skills yields 0.0% match with all skills missing."""
        jd = "Requirements: Java, Rust, Kotlin"
        dev_skills = ["Python", "FastAPI", "PostgreSQL"]

        res = job_matching_service.match_job_description(
            job_description=jd,
            developer_skills=dev_skills,
        )

        self.assertGreater(res["total_required_skills"], 0)
        self.assertEqual(res["matched_skill_count"], 0)
        self.assertEqual(res["missing_skill_count"], res["total_required_skills"])
        self.assertEqual(res["matched_skills"], [])
        self.assertEqual(res["match_percentage"], 0.0)

    def test_12_zero_detectable_jd_skills_safe_behavior(self):
        """Test 12: Job description with no detectable technical skills returns 0.0% without division error."""
        jd = "Manager wanted for general office duties and team scheduling. Great communication."
        dev_skills = ["Python", "React"]

        res = job_matching_service.match_job_description(
            job_description=jd,
            developer_skills=dev_skills,
        )

        self.assertEqual(res["total_required_skills"], 0)
        self.assertEqual(res["matched_skill_count"], 0)
        self.assertEqual(res["missing_skill_count"], 0)
        self.assertEqual(res["extracted_skills"], [])
        self.assertEqual(res["matched_skills"], [])
        self.assertEqual(res["missing_skills"], [])
        self.assertEqual(res["match_percentage"], 0.0)

    # -----------------------------------------------------------------------
    # API Contract tests
    # -----------------------------------------------------------------------

    def test_13_api_contract_validation(self):
        """Test 13: POST /api/v1/job-matching/analyze returns 200 with schema conformant data."""
        payload = {
            "job_description": SAMPLE_JD,
            "developer_skills": ["Python", "Docker", "PostgreSQL"],
        }
        response = self.client.post("/api/v1/job-matching/analyze", json=payload)
        self.assertEqual(response.status_code, 200)

        data = response.json()
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
        for key in required_keys:
            self.assertIn(key, data)

        self.assertIsInstance(data["extracted_skills"], list)
        self.assertIsInstance(data["developer_skills"], list)
        self.assertIsInstance(data["matched_skills"], list)
        self.assertIsInstance(data["missing_skills"], list)
        self.assertIsInstance(data["total_required_skills"], int)
        self.assertIsInstance(data["matched_skill_count"], int)
        self.assertIsInstance(data["missing_skill_count"], int)
        self.assertIsInstance(data["match_percentage"], float)

        self.assertEqual(
            data["matched_skill_count"] + data["missing_skill_count"],
            data["total_required_skills"],
        )


if __name__ == "__main__":
    unittest.main()
