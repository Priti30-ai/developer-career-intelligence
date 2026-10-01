"""
test_evidence.py
----------------
Unit and integration tests for Resume vs GitHub Evidence Analysis.

Tests:
1. Resume skill normalization
2. Matching resume skill with GitHub skill
3. Unmatched resume skill
4. Duplicate skill handling
5. Multiple repositories supporting one skill
6. Strong evidence classification
7. Moderate evidence classification
8. None-detected classification
9. Evidence coverage calculation
10. Repository evidence preservation
11. GitHub failure handling
12. API response validation
"""

import sys
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch

# Add backend directory to sys.path so 'app' imports resolve cleanly
backend_dir = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from fastapi.testclient import TestClient

from app.main import app
from app.services.evidence_service import evidence_service
from app.services.github_service import (
    GitHubAPIError,
    GitHubUserNotFoundError,
)

MOCK_REPOSITORIES = [
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


class TestEvidenceAnalysis(unittest.TestCase):
    """Test suite for Resume vs GitHub Evidence Analysis."""

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_01_resume_skill_normalization(self):
        """Test 1: Resume skill normalization canonicalizes known aliases."""
        input_skills = ["python", "cpp", "nodejs", "scikit-learn"]
        normalized = evidence_service.normalize_resume_skills(resume_skills=input_skills)
        expected = ["Python", "C++", "Node.js", "Scikit-learn"]
        self.assertEqual(normalized, expected)

    async def _run_analyze(self, username="testuser", resume_skills=None, resume_text=None, repos=None):
        return await evidence_service.analyze_evidence(
            username=username,
            resume_skills=resume_skills or [],
            resume_text=resume_text,
            repositories=repos if repos is not None else MOCK_REPOSITORIES,
        )

    def test_02_matching_resume_skill_with_github(self):
        """Test 2: Matching resume skill is marked as github_detected=True with resume_claimed=True."""
        import asyncio
        result = asyncio.run(self._run_analyze(resume_skills=["Python"]))
        items = result["evidence_items"]
        self.assertEqual(len(items), 1)

        item = items[0]
        self.assertEqual(item["skill"], "Python")
        self.assertTrue(item["resume_claimed"])
        self.assertTrue(item["github_detected"])
        self.assertGreaterEqual(len(item["supporting_repositories"]), 1)

    def test_03_unmatched_resume_skill(self):
        """Test 3: Unmatched resume skill is marked as github_detected=False, level NONE_DETECTED."""
        import asyncio
        result = asyncio.run(self._run_analyze(resume_skills=["Docker"]))
        items = result["evidence_items"]
        self.assertEqual(len(items), 1)

        item = items[0]
        self.assertEqual(item["skill"], "Docker")
        self.assertTrue(item["resume_claimed"])
        self.assertFalse(item["github_detected"])
        self.assertEqual(item["evidence_level"], "NONE_DETECTED")
        self.assertEqual(item["supporting_repositories"], [])

    def test_04_duplicate_skill_handling(self):
        """Test 4: Duplicate and case-variant resume skills are deduplicated."""
        input_skills = ["Python", "python", "PYTHON", "c++", "cpp", "C++"]
        normalized = evidence_service.normalize_resume_skills(resume_skills=input_skills)
        self.assertEqual(normalized, ["Python", "C++"])

        import asyncio
        result = asyncio.run(self._run_analyze(resume_skills=input_skills))
        self.assertEqual(len(result["evidence_items"]), 2)
        self.assertEqual(result["summary"]["total_resume_skills"], 2)

    def test_05_multiple_repositories_supporting_one_skill(self):
        """Test 5: Multiple repositories supporting one skill are all preserved in supporting_repositories."""
        import asyncio
        result = asyncio.run(self._run_analyze(resume_skills=["Python"]))
        item = result["evidence_items"][0]
        self.assertEqual(item["skill"], "Python")
        supporting = item["supporting_repositories"]
        self.assertEqual(len(supporting), 2)
        repo_names = [r["name"] for r in supporting]
        self.assertIn("fake-profile-detector", repo_names)
        self.assertIn("career-intelligence", repo_names)

    def test_06_strong_evidence_classification(self):
        """Test 6: Skill present in multiple (>=2) repositories gets STRONG evidence level."""
        import asyncio
        result = asyncio.run(self._run_analyze(resume_skills=["Machine Learning"]))
        item = result["evidence_items"][0]
        self.assertEqual(item["skill"], "Machine Learning")
        self.assertEqual(len(item["supporting_repositories"]), 2)
        self.assertEqual(item["evidence_level"], "STRONG")

    def test_07_moderate_evidence_classification(self):
        """Test 7: Skill present in exactly 1 repository gets MODERATE evidence level."""
        import asyncio
        result = asyncio.run(self._run_analyze(resume_skills=["React"]))
        item = result["evidence_items"][0]
        self.assertEqual(item["skill"], "React")
        self.assertEqual(len(item["supporting_repositories"]), 1)
        self.assertEqual(item["evidence_level"], "MODERATE")

    def test_08_none_detected_classification(self):
        """Test 8: Skill not present in any repository gets NONE_DETECTED evidence level."""
        import asyncio
        result = asyncio.run(self._run_analyze(resume_skills=["Kubernetes"]))
        item = result["evidence_items"][0]
        self.assertEqual(item["skill"], "Kubernetes")
        self.assertEqual(len(item["supporting_repositories"]), 0)
        self.assertEqual(item["evidence_level"], "NONE_DETECTED")

    def test_09_evidence_coverage_calculation(self):
        """Test 9: Deterministic evidence coverage calculation and partition invariant."""
        import asyncio
        # 4 resume skills: 2 detected (Python, React), 2 undetected (Docker, Kubernetes)
        claimed = ["Python", "React", "Docker", "Kubernetes"]
        result = asyncio.run(self._run_analyze(resume_skills=claimed))
        summary = result["summary"]

        self.assertEqual(summary["total_resume_skills"], 4)
        self.assertEqual(summary["skills_with_evidence"], 2)
        self.assertEqual(summary["skills_without_evidence"], 2)
        self.assertEqual(summary["evidence_coverage_percentage"], 50.0)

        # Invariant check: with + without == total
        self.assertEqual(
            summary["skills_with_evidence"] + summary["skills_without_evidence"],
            summary["total_resume_skills"],
        )

        # Zero skills check: safe division
        empty_result = asyncio.run(self._run_analyze(resume_skills=[]))
        self.assertEqual(empty_result["summary"]["total_resume_skills"], 0)
        self.assertEqual(empty_result["summary"]["evidence_coverage_percentage"], 0.0)

    def test_10_repository_evidence_preservation(self):
        """Test 10: Preserved repository details include name, full_name, html_url, and skills_detected."""
        import asyncio
        result = asyncio.run(self._run_analyze(resume_skills=["FastAPI"]))
        item = result["evidence_items"][0]
        self.assertEqual(len(item["supporting_repositories"]), 1)
        repo = item["supporting_repositories"][0]

        self.assertEqual(repo["name"], "career-intelligence")
        self.assertEqual(repo["full_name"], "testuser/career-intelligence")
        self.assertEqual(repo["html_url"], "https://github.com/testuser/career-intelligence")
        self.assertIn("FastAPI", repo["skills_detected"])

    @patch("app.services.evidence_service.github_service.get_user_repositories")
    def test_11_github_failure_handling(self, mock_get_repos):
        """Test 11: GitHub API failures and non-existent users return explicit HTTP errors, never NONE_DETECTED."""
        # Case A: User Not Found -> 404
        mock_get_repos.side_effect = GitHubUserNotFoundError("GitHub user 'nonexistent-user' not found")
        response = self.client.post(
            "/api/v1/evidence/analyze",
            json={"github_username": "nonexistent-user", "resume_skills": ["Python"]},
        )
        self.assertEqual(response.status_code, 404)
        self.assertIn("not found", response.json()["detail"].lower())

        # Case B: Rate Limit (403) -> 403
        mock_get_repos.side_effect = GitHubAPIError("GitHub API rate limit exceeded", status_code=403)
        response_rate = self.client.post(
            "/api/v1/evidence/analyze",
            json={"github_username": "ratelimited-user", "resume_skills": ["Python"]},
        )
        self.assertEqual(response_rate.status_code, 403)
        self.assertIn("rate limit", response_rate.json()["detail"].lower())

    @patch("app.services.evidence_service.github_service.get_user_repositories")
    def test_12_api_response_validation(self, mock_get_repos):
        """Test 12: POST /api/v1/evidence/analyze returns HTTP 200 with schema conformant data and handles validation."""
        mock_get_repos.return_value = MOCK_REPOSITORIES

        # Success call
        payload = {
            "github_username": "testuser",
            "resume_skills": ["Python", "JavaScript", "Docker"],
        }
        response = self.client.post("/api/v1/evidence/analyze", json=payload)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(data["github_username"], "testuser")
        self.assertIn("Python", data["resume_skills"])
        self.assertIn("JavaScript", data["resume_skills"])
        self.assertIn("Docker", data["resume_skills"])
        self.assertIsInstance(data["github_skills"], list)
        self.assertIsInstance(data["evidence_items"], list)
        self.assertIn("summary", data)

        summary = data["summary"]
        self.assertEqual(summary["total_resume_skills"], 3)
        self.assertEqual(summary["skills_with_evidence"], 2)  # Python, JavaScript
        self.assertEqual(summary["skills_without_evidence"], 1)  # Docker
        self.assertEqual(summary["evidence_coverage_percentage"], 66.67)

        # Validation error: blank username -> 422
        bad_response = self.client.post(
            "/api/v1/evidence/analyze",
            json={"github_username": "   ", "resume_skills": ["Python"]},
        )
        self.assertEqual(bad_response.status_code, 422)


if __name__ == "__main__":
    unittest.main()
