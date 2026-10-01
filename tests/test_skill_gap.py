"""
test_skill_gap.py
-----------------
Automated tests for Skill Gap Analysis.
Tests:
  Test 1: All required skills present (no missing skills, 100% skill_match_percentage)
  Test 2: Some required skills missing (correct missing-skill list and percentage)
  Test 3: No current skills (all required skills missing, 0% skill_match_percentage)
  Test 4: Unknown target role (raises CareerRoleNotFoundError / returns 404)
  Test 5: Duplicate and case variation in current skills (Python vs python, Node.js vs nodejs, C++ vs c++)
  Test 6: Empty required-skill list (safe behavior, no division-by-zero)
  Test 7: Partition invariant: total_matched_skills + total_missing_skills == total_required_skills
  Test 8: API endpoints testing via Starlette/FastAPI TestClient
  Test 9: API validation error handling (422 on malformed payloads)
"""

import sys
import unittest
from pathlib import Path

# Add backend directory to sys.path so 'app' imports resolve cleanly
backend_dir = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from app.main import app
from app.services.career_role_service import (
    CareerRoleNotFoundError,
    career_role_service,
)
from app.services.skill_gap_service import skill_gap_service


class TestSkillGapAnalysis(unittest.TestCase):
    """Test suite for the Skill Gap Analysis service and requirements."""

    def test_01_all_required_skills_present(self):
        """Test 1: All required skills present -> expected: no missing skills, 100% match."""
        role = career_role_service.get_role("data-scientist")
        self.assertIsNotNone(role, "data-scientist role should exist")
        required_skills = role["required_skills"]

        result = skill_gap_service.analyze_gap(
            target_role="data-scientist",
            current_skills=required_skills,
        )

        self.assertEqual(result["total_missing_skills"], 0)
        self.assertEqual(result["missing_skills"], [])
        self.assertEqual(result["total_matched_skills"], len(required_skills))
        self.assertEqual(result["matched_skills"], required_skills)
        self.assertEqual(result["skill_match_percentage"], 100.0)
        self.assertEqual(result["match_percentage"], 100.0)
        # Invariant check
        self.assertEqual(
            result["total_matched_skills"] + result["total_missing_skills"],
            result["total_required_skills"],
        )

    def test_02_some_required_skills_missing(self):
        """Test 2: Some required skills missing -> expected: correct missing-skill list."""
        current_skills = ["Python", "Pandas", "NumPy", "Machine Learning"]

        result = skill_gap_service.analyze_gap(
            target_role="data-scientist",
            current_skills=current_skills,
        )

        expected_matched = ["Python", "Pandas", "NumPy", "Machine Learning"]
        expected_missing = ["SQL", "Scikit-learn", "Data Visualization", "Statistics"]

        self.assertEqual(result["matched_skills"], expected_matched)
        self.assertEqual(result["missing_skills"], expected_missing)
        self.assertEqual(result["total_matched_skills"], 4)
        self.assertEqual(result["total_missing_skills"], 4)
        self.assertEqual(result["total_required_skills"], 8)
        self.assertEqual(result["skill_match_percentage"], 50.0)
        self.assertEqual(result["match_percentage"], 50.0)
        # Invariant check
        self.assertEqual(
            result["total_matched_skills"] + result["total_missing_skills"],
            result["total_required_skills"],
        )

    def test_03_no_current_skills(self):
        """Test 3: No current skills -> expected: all role-required skills are missing."""
        role = career_role_service.get_role("backend-developer")
        required_skills = role["required_skills"]

        result = skill_gap_service.analyze_gap(
            target_role="backend-developer",
            current_skills=[],
        )

        self.assertEqual(result["total_matched_skills"], 0)
        self.assertEqual(result["matched_skills"], [])
        self.assertEqual(result["total_missing_skills"], len(required_skills))
        self.assertEqual(result["missing_skills"], required_skills)
        self.assertEqual(result["skill_match_percentage"], 0.0)
        self.assertEqual(result["match_percentage"], 0.0)
        # Invariant check
        self.assertEqual(
            result["total_matched_skills"] + result["total_missing_skills"],
            result["total_required_skills"],
        )

    def test_04_unknown_target_role(self):
        """Test 4: Unknown target role -> expected: clean error handling."""
        with self.assertRaises(CareerRoleNotFoundError):
            skill_gap_service.analyze_gap(
                target_role="non-existent-role-xyz",
                current_skills=["Python", "Go"],
            )

    def test_05_duplicate_and_case_variation(self):
        """Test 5: Duplicate and case variations (Python vs python, Node.js vs nodejs, etc.)."""
        # Full Stack Developer requires: JavaScript, TypeScript, HTML, CSS, React, Node.js, SQL, REST API, Docker, Git
        current_skills = [
            "python",          # irrelevant
            "Python",          # duplicate
            "JAVASCRIPT",      # case variation
            "javascript",      # duplicate case variation
            "nodejs",          # alias for Node.js
            "node.js",         # alias for Node.js
            "React",
            "react",           # duplicate
            "git",             # lowercase
            "GIT",             # uppercase
            "docker",          # lowercase
        ]

        result = skill_gap_service.analyze_gap(
            target_role="full-stack-developer",
            current_skills=current_skills,
        )

        matched = result["matched_skills"]
        self.assertIn("JavaScript", matched)
        self.assertIn("Node.js", matched)
        self.assertIn("React", matched)
        self.assertIn("Docker", matched)
        self.assertIn("Git", matched)
        # Should not duplicate matched skills
        self.assertEqual(len(matched), len(set(matched)))
        # Invariant check
        self.assertEqual(
            result["total_matched_skills"] + result["total_missing_skills"],
            result["total_required_skills"],
        )

    def test_06_empty_required_skill_list(self):
        """Test 6: Empty required-skill list -> expected: safe behavior without crash."""
        result = skill_gap_service.analyze_gap(
            target_role="Custom Empty Role",
            current_skills=["Python", "SQL"],
            custom_required_skills=[],
        )

        self.assertEqual(result["total_required_skills"], 0)
        self.assertEqual(result["total_matched_skills"], 0)
        self.assertEqual(result["total_missing_skills"], 0)
        self.assertEqual(result["matched_skills"], [])
        self.assertEqual(result["missing_skills"], [])
        self.assertEqual(result["skill_match_percentage"], 0.0)
        self.assertEqual(result["match_percentage"], 0.0)
        # Invariant check
        self.assertEqual(
            result["total_matched_skills"] + result["total_missing_skills"],
            result["total_required_skills"],
        )


class TestSkillGapAPI(unittest.TestCase):
    """API endpoint tests using FastAPI / Starlette TestClient."""

    @classmethod
    def setUpClass(cls):
        from fastapi.testclient import TestClient
        cls.client = TestClient(app)

    def test_api_list_roles(self):
        """Test GET /api/v1/skill-gap/roles."""
        response = self.client.get("/api/v1/skill-gap/roles")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 6)
        slugs = [r["slug"] for r in data]
        self.assertIn("data-scientist", slugs)
        self.assertIn("backend-developer", slugs)

    def test_api_get_role_details_success(self):
        """Test GET /api/v1/skill-gap/roles/data-scientist."""
        response = self.client.get("/api/v1/skill-gap/roles/data-scientist")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["slug"], "data-scientist")
        self.assertEqual(data["display_name"], "Data Scientist")
        self.assertIn("Python", data["required_skills"])
        self.assertIn("Machine Learning", data["required_skills"])

    def test_api_get_role_details_not_found(self):
        """Test GET /api/v1/skill-gap/roles/unknown-role -> 404."""
        response = self.client.get("/api/v1/skill-gap/roles/unknown-role")
        self.assertEqual(response.status_code, 404)
        self.assertIn("detail", response.json())

    def test_api_analyze_gap_success(self):
        """Test POST /api/v1/skill-gap/analyze."""
        payload = {
            "target_role": "data-scientist",
            "current_skills": ["Python", "Pandas", "NumPy", "Machine Learning"],
        }
        response = self.client.post("/api/v1/skill-gap/analyze", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["target_role"], "Data Scientist")
        self.assertEqual(data["role_slug"], "data-scientist")
        self.assertEqual(data["total_matched_skills"], 4)
        self.assertEqual(data["total_missing_skills"], 4)
        self.assertEqual(data["skill_match_percentage"], 50.0)
        self.assertEqual(data["match_percentage"], 50.0)
        self.assertEqual(
            data["matched_skills"],
            ["Python", "Pandas", "NumPy", "Machine Learning"],
        )
        self.assertEqual(
            data["missing_skills"],
            ["SQL", "Scikit-learn", "Data Visualization", "Statistics"],
        )
        self.assertEqual(
            data["total_matched_skills"] + data["total_missing_skills"],
            data["total_required_skills"],
        )

    def test_api_analyze_gap_unknown_role(self):
        """Test POST /api/v1/skill-gap/analyze with unknown role -> 404."""
        payload = {
            "target_role": "invalid-role",
            "current_skills": ["Python"],
        }
        response = self.client.post("/api/v1/skill-gap/analyze", json=payload)
        self.assertEqual(response.status_code, 404)
        self.assertIn("detail", response.json())

    def test_api_analyze_gap_validation_errors(self):
        """Test POST /api/v1/skill-gap/analyze with malformed payloads -> 422."""
        # Missing required 'target_role' field
        response1 = self.client.post("/api/v1/skill-gap/analyze", json={"current_skills": ["Python"]})
        self.assertEqual(response1.status_code, 422)

        # 'current_skills' is not a list
        response2 = self.client.post(
            "/api/v1/skill-gap/analyze",
            json={"target_role": "data-scientist", "current_skills": "Python"},
        )
        self.assertEqual(response2.status_code, 422)


if __name__ == "__main__":
    unittest.main()
