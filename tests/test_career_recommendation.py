"""
test_career_recommendation.py
------------------------------
Comprehensive test suite for Career Recommendations & Learning Roadmap.

Tests:
  1. Valid target role
  2. Unknown target role
  3. Empty current skills
  4. Current skills already covering all required skills (100% match)
  5. Partial skill coverage
  6. Skill normalization (Python/python, Node.js/nodejs, etc.)
  7. Missing skills produce recommendations
  8. Recommendations contain valid priorities (HIGH, MEDIUM, LOW)
  9. Roadmap stages are sequentially ordered
  10. Prerequisites are respected in roadmap ordering
  11. Invariant: matched + missing == required
  12. Invariant: every roadmap skill comes from missing_skills
  13. API success response (/roles and /analyze)
  14. API validation errors (HTTP 422 on invalid/missing fields)
"""

import sys
import unittest
from pathlib import Path

# Add backend directory to sys.path so 'app' imports resolve cleanly
backend_dir = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from app.main import app
from app.services.career_recommendation_service import (
    career_recommendation_service,
)
from app.services.career_role_service import (
    CareerRoleNotFoundError,
    career_role_service,
)


class TestCareerRecommendation(unittest.TestCase):
    """Test suite for the recommendation service logic."""

    def test_01_valid_target_role(self):
        """Test 1: Valid target role produces valid recommendation structure."""
        res = career_recommendation_service.generate_recommendations(
            target_role="data-scientist",
            current_skills=["Python", "SQL"],
        )
        self.assertEqual(res["target_role"], "Data Scientist")
        self.assertEqual(res["role_slug"], "data-scientist")
        self.assertIn("Python", res["matched_skills"])
        self.assertIn("SQL", res["matched_skills"])
        self.assertGreater(len(res["missing_skills"]), 0)
        self.assertGreater(len(res["recommendations"]), 0)
        self.assertGreater(len(res["roadmap"]), 0)
        self.assertIn("disclaimer", res)

    def test_02_unknown_target_role(self):
        """Test 2: Unknown target role raises CareerRoleNotFoundError."""
        with self.assertRaises(CareerRoleNotFoundError):
            career_recommendation_service.generate_recommendations(
                target_role="quantum-computing-specialist",
                current_skills=["Python"],
            )

    def test_03_empty_current_skills(self):
        """Test 3: Empty current skills -> all required skills are missing and recommended."""
        role = career_role_service.get_role("backend-developer")
        req_skills = role["required_skills"]

        res = career_recommendation_service.generate_recommendations(
            target_role="backend-developer",
            current_skills=[],
        )

        self.assertEqual(res["total_matched_skills"], 0)
        self.assertEqual(res["total_missing_skills"], len(req_skills))
        self.assertEqual(res["skill_match_percentage"], 0.0)
        self.assertEqual(len(res["recommendations"]), len(req_skills))

        # Check invariant
        self.assertEqual(
            res["total_matched_skills"] + res["total_missing_skills"],
            res["total_required_skills"],
        )

    def test_04_full_skill_coverage(self):
        """Test 4: Current skills cover 100% of required skills -> empty roadmap and recommendations."""
        role = career_role_service.get_role("data-scientist")
        req_skills = role["required_skills"]

        res = career_recommendation_service.generate_recommendations(
            target_role="data-scientist",
            current_skills=req_skills,
        )

        self.assertEqual(res["skill_match_percentage"], 100.0)
        self.assertEqual(res["total_missing_skills"], 0)
        self.assertEqual(res["missing_skills"], [])
        self.assertEqual(res["recommendations"], [])
        self.assertEqual(res["roadmap"], [])

    def test_05_partial_skill_coverage(self):
        """Test 5: Partial skill coverage calculates correct gap and recommendations."""
        current = ["Python", "Pandas", "NumPy", "Machine Learning"]
        res = career_recommendation_service.generate_recommendations(
            target_role="data-scientist",
            current_skills=current,
        )

        self.assertEqual(res["total_matched_skills"], 4)
        self.assertEqual(res["total_missing_skills"], 4)
        self.assertEqual(res["skill_match_percentage"], 50.0)

        missing_names = [r["skill"] for r in res["recommendations"]]
        self.assertEqual(
            set(missing_names),
            {"SQL", "Scikit-learn", "Data Visualization", "Statistics"},
        )

    def test_06_skill_normalization(self):
        """Test 6: Skill normalization handles casing and aliases without duplicate entries."""
        # Full stack requires: JavaScript, TypeScript, HTML, CSS, React, Node.js, SQL, REST API, Docker, Git
        noisy_skills = [
            "python",          # irrelevant
            "JAVASCRIPT",      # uppercase
            "javascript",      # lowercase
            "nodejs",          # alias for Node.js
            "node.js",         # alias for Node.js
            "react",           # lowercase
            "HTML",
            "css",
            "git",
        ]
        res = career_recommendation_service.generate_recommendations(
            target_role="full-stack-developer",
            current_skills=noisy_skills,
        )

        matched = res["matched_skills"]
        self.assertIn("JavaScript", matched)
        self.assertIn("Node.js", matched)
        self.assertIn("React", matched)
        self.assertIn("HTML", matched)
        self.assertIn("CSS", matched)
        self.assertIn("Git", matched)
        self.assertEqual(len(matched), len(set(matched)))

    def test_07_missing_skills_produce_recommendations(self):
        """Test 7: Every missing skill produces a corresponding recommendation."""
        res = career_recommendation_service.generate_recommendations(
            target_role="machine-learning-engineer",
            current_skills=["Python", "SQL"],
        )
        rec_skills = [r["skill"] for r in res["recommendations"]]
        self.assertEqual(sorted(rec_skills), sorted(res["missing_skills"]))

    def test_08_recommendation_priorities_valid(self):
        """Test 8: Recommendations contain valid priority levels (HIGH, MEDIUM, LOW) and reasons."""
        res = career_recommendation_service.generate_recommendations(
            target_role="ai-engineer",
            current_skills=[],
        )
        valid_priorities = {"HIGH", "MEDIUM", "LOW"}
        for rec in res["recommendations"]:
            self.assertIn(rec["priority"], valid_priorities)
            self.assertTrue(len(rec["reason"]) > 10, "Reason should be descriptive")
            self.assertTrue(len(rec["learning_topics"]) > 0, "Topics should be present")
            self.assertTrue(len(rec["suggested_projects"]) > 0, "Projects should be present")

    def test_09_roadmap_stages_sequential(self):
        """Test 9: Roadmap stages are numbered sequentially 1, 2, ..."""
        res = career_recommendation_service.generate_recommendations(
            target_role="data-scientist",
            current_skills=[],
        )
        roadmap = res["roadmap"]
        self.assertGreater(len(roadmap), 0)
        for idx, stage in enumerate(roadmap, start=1):
            self.assertEqual(stage["stage_number"], idx)
            self.assertTrue(stage["title"].startswith(f"Stage {idx}:"))
            self.assertGreater(len(stage["skills"]), 0)
            self.assertGreater(len(stage["objective"]), 0)

    def test_10_prerequisites_respected(self):
        """Test 10: Prerequisites are respected in the roadmap stages."""
        # AI Engineer with empty skills needs Python before Deep Learning / NLP / LLM
        res = career_recommendation_service.generate_recommendations(
            target_role="ai-engineer",
            current_skills=[],
        )
        # Find which stage contains Python and which contains Deep Learning/LLM
        skill_to_stage = {}
        for stage in res["roadmap"]:
            for s in stage["skills"]:
                skill_to_stage[s] = stage["stage_number"]

        if "Python" in skill_to_stage and "Deep Learning" in skill_to_stage:
            self.assertLess(
                skill_to_stage["Python"],
                skill_to_stage["Deep Learning"],
                "Python must precede Deep Learning in roadmap stages",
            )
        if "Deep Learning" in skill_to_stage and "LLM" in skill_to_stage:
            self.assertLessEqual(
                skill_to_stage["Deep Learning"],
                skill_to_stage["LLM"],
                "Deep Learning must precede or equal LLM in roadmap stages",
            )

    def test_11_invariant_matched_plus_missing_equals_required(self):
        """Test 11: Invariant check matched + missing == required across multiple roles."""
        for role_slug in ["data-scientist", "backend-developer", "full-stack-developer"]:
            res = career_recommendation_service.generate_recommendations(
                target_role=role_slug,
                current_skills=["Python", "Docker"],
            )
            self.assertEqual(
                res["total_matched_skills"] + res["total_missing_skills"],
                res["total_required_skills"],
            )

    def test_12_roadmap_skills_come_from_missing(self):
        """Test 12: Every skill appearing in the roadmap comes from missing_skills."""
        res = career_recommendation_service.generate_recommendations(
            target_role="backend-developer",
            current_skills=["Python", "SQL"],
        )
        roadmap_skills = []
        for stage in res["roadmap"]:
            roadmap_skills.extend(stage["skills"])

        missing_set = set(res["missing_skills"])
        for s in roadmap_skills:
            self.assertIn(s, missing_set)
        self.assertEqual(set(roadmap_skills), missing_set)


class TestCareerRecommendationAPI(unittest.TestCase):
    """API endpoint tests for Career Recommendations."""

    @classmethod
    def setUpClass(cls):
        from fastapi.testclient import TestClient
        cls.client = TestClient(app)

    def test_api_list_roles(self):
        """Test GET /api/v1/career-recommendations/roles."""
        res = self.client.get("/api/v1/career-recommendations/roles")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 6)
        slugs = [r["slug"] for r in data]
        self.assertIn("data-scientist", slugs)
        self.assertIn("ai-engineer", slugs)

    def test_api_analyze_success(self):
        """Test POST /api/v1/career-recommendations/analyze."""
        payload = {
            "target_role": "data-scientist",
            "current_skills": ["Python", "Pandas", "NumPy", "Machine Learning"],
        }
        res = self.client.post("/api/v1/career-recommendations/analyze", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["target_role"], "Data Scientist")
        self.assertEqual(data["skill_match_percentage"], 50.0)
        self.assertEqual(len(data["recommendations"]), 4)
        self.assertGreater(len(data["roadmap"]), 0)
        self.assertIn("disclaimer", data)

    def test_api_analyze_unknown_role(self):
        """Test POST /api/v1/career-recommendations/analyze with unknown role -> 404."""
        payload = {
            "target_role": "invalid-role-123",
            "current_skills": ["Python"],
        }
        res = self.client.post("/api/v1/career-recommendations/analyze", json=payload)
        self.assertEqual(res.status_code, 404)
        self.assertIn("detail", res.json())

    def test_api_analyze_validation_errors(self):
        """Test POST /api/v1/career-recommendations/analyze with malformed payloads -> 422."""
        # Missing target_role
        res1 = self.client.post("/api/v1/career-recommendations/analyze", json={"current_skills": ["Python"]})
        self.assertEqual(res1.status_code, 422)

        # current_skills is not a list
        res2 = self.client.post(
            "/api/v1/career-recommendations/analyze",
            json={"target_role": "data-scientist", "current_skills": "Python"},
        )
        self.assertEqual(res2.status_code, 422)


if __name__ == "__main__":
    unittest.main()
