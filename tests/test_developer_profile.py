"""
test_developer_profile.py
-------------------------
Comprehensive unit and integration tests for Unified Developer Profile Synthesis.

Tests:
1. Technology alias normalization and deduplication
2. GitHub-only skill representation
3. Resume-only skill representation
4. Skills present in both GitHub and Resume
5. Multiple skills across both sources
6. Source tracking accuracy ('github', 'resume', both)
7. Evidence level classification (STRONG, MODERATE, NONE_DETECTED)
8. Semantic integrity: resume-only skill without GitHub evidence is preserved
9. Profile summary statistics and mathematical invariants
10. Resume text parsing and section integration (education, experience, projects)
11. Downstream Job Description Matching integration helper
12. API route contract and validation
13. API route error handling (404 not found, 502 upstream error)
"""

import sys
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch

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
from app.services.github_service import (
    GitHubAPIError,
    GitHubUserNotFoundError,
)
from app.services.job_matching_service import job_matching_service

MOCK_REPOSITORIES = [
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

SAMPLE_RESUME_TEXT = (
    "SUMMARY\n"
    "Full-stack software engineer with expertise in machine learning and web systems.\n\n"
    "TECHNICAL SKILLS\n"
    "Python, SQL, Machine Learning, Docker, PostgreSQL\n\n"
    "EDUCATION\n"
    "State University of Technology\n"
    "Bachelor of Science in Computer Science\n"
    "2020 - 2024\n\n"
    "EXPERIENCE\n"
    "Software Engineering Intern\n"
    "Tech Solutions Inc\n"
    "June 2023 - August 2023\n"
    "Built automated data pipelines with Python and SQL.\n\n"
    "PROJECTS\n"
    "Cloud Analytics Platform\n"
    "Designed real-time metric collection using Python and Docker.\n\n"
    "CERTIFICATIONS\n"
    "Certified AWS Cloud Practitioner"
)


class TestDeveloperProfileSynthesis(unittest.IsolatedAsyncioTestCase):
    """Unit tests for the developer profile service synthesis logic."""

    async def test_01_normalization_and_alias_deduplication(self):
        """Test 1: Duplicate aliases normalize into single canonical skills."""
        # Repositories with 'js', 'javascript', and resume with 'JavaScript'
        custom_repos = [
            {
                "name": "repo1",
                "full_name": "test/repo1",
                "html_url": "https://github.com/test/repo1",
                "language": "js",
                "topics": ["nodejs"],
            },
            {
                "name": "repo2",
                "full_name": "test/repo2",
                "html_url": "https://github.com/test/repo2",
                "language": "javascript",
                "topics": ["node.js"],
            },
        ]
        resume_skills = ["JavaScript", "Node.js", "node"]

        profile = await developer_profile_service.synthesize_profile(
            username="testuser",
            resume_skills=resume_skills,
            repositories=custom_repos,
        )

        skills = {s["skill"]: s for s in profile["skills"]}

        # Both JavaScript and Node.js should appear exactly once
        self.assertIn("JavaScript", skills)
        self.assertIn("Node.js", skills)
        self.assertEqual(len([s for s in profile["skills"] if s["skill"] == "JavaScript"]), 1)
        self.assertEqual(len([s for s in profile["skills"] if s["skill"] == "Node.js"]), 1)

    async def test_02_github_only_skills(self):
        """Test 2: GitHub-only skills are accurately tagged with source 'github'."""
        profile = await developer_profile_service.synthesize_profile(
            username="octocat",
            resume_skills=["SQL"],  # React and TypeScript are not on resume
            repositories=MOCK_REPOSITORIES,
        )

        skills = {s["skill"]: s for s in profile["skills"]}

        self.assertIn("React", skills)
        self.assertEqual(skills["React"]["sources"], [SOURCE_GITHUB])
        self.assertEqual(skills["React"]["evidence_status"], EVIDENCE_LEVEL_MODERATE)
        self.assertEqual(len(skills["React"]["supporting_repositories"]), 1)

        self.assertIn("TypeScript", skills)
        self.assertEqual(skills["TypeScript"]["sources"], [SOURCE_GITHUB])

    async def test_03_resume_only_skills(self):
        """Test 3: Resume-only skills are accurately tagged with source 'resume'."""
        profile = await developer_profile_service.synthesize_profile(
            username="octocat",
            resume_skills=["SQL", "PostgreSQL"],
            repositories=MOCK_REPOSITORIES,
        )

        skills = {s["skill"]: s for s in profile["skills"]}

        self.assertIn("SQL", skills)
        self.assertEqual(skills["SQL"]["sources"], [SOURCE_RESUME])
        self.assertEqual(skills["SQL"]["evidence_status"], EVIDENCE_LEVEL_NONE_DETECTED)
        self.assertEqual(skills["SQL"]["supporting_repositories"], [])

        self.assertIn("PostgreSQL", skills)
        self.assertEqual(skills["PostgreSQL"]["sources"], [SOURCE_RESUME])
        self.assertEqual(skills["PostgreSQL"]["evidence_status"], EVIDENCE_LEVEL_NONE_DETECTED)

    async def test_04_skills_present_in_both_sources(self):
        """Test 4: Skills in both GitHub and Resume have sources ['github', 'resume']."""
        profile = await developer_profile_service.synthesize_profile(
            username="octocat",
            resume_skills=["Python", "Machine Learning"],
            repositories=MOCK_REPOSITORIES,
        )

        skills = {s["skill"]: s for s in profile["skills"]}

        self.assertIn("Python", skills)
        self.assertIn(SOURCE_GITHUB, skills["Python"]["sources"])
        self.assertIn(SOURCE_RESUME, skills["Python"]["sources"])
        self.assertEqual(len(skills["Python"]["sources"]), 2)

        self.assertIn("Machine Learning", skills)
        self.assertIn(SOURCE_GITHUB, skills["Machine Learning"]["sources"])
        self.assertIn(SOURCE_RESUME, skills["Machine Learning"]["sources"])

    async def test_05_multiple_skills_from_both_sources(self):
        """Test 5: Multiple skills across sources are merged cleanly."""
        profile = await developer_profile_service.synthesize_profile(
            username="octocat",
            resume_skills=["Python", "FastAPI", "SQL", "Docker"],
            repositories=MOCK_REPOSITORIES,
        )

        skills = {s["skill"]: s for s in profile["skills"]}

        # GitHub skills in MOCK_REPOSITORIES: CSS, FastAPI, Machine Learning, Pandas, Python, React, TypeScript
        # Resume skills: Python, FastAPI, SQL, Docker
        # Unified total should be 9
        self.assertIn("Python", skills)
        self.assertIn("FastAPI", skills)
        self.assertIn("SQL", skills)
        self.assertIn("Docker", skills)
        self.assertIn("React", skills)
        self.assertIn("TypeScript", skills)
        self.assertIn("Machine Learning", skills)
        self.assertIn("Pandas", skills)
        self.assertIn("CSS", skills)

        self.assertEqual(profile["summary"]["total_skills"], 9)
        self.assertEqual(profile["summary"]["skills_from_both_sources"], 2)  # Python, FastAPI

    async def test_06_evidence_level_preservation(self):
        """Test 6: Evidence status preserves STRONG (>=2 repos), MODERATE (1 repo), NONE_DETECTED (0 repos)."""
        profile = await developer_profile_service.synthesize_profile(
            username="octocat",
            resume_skills=["Python", "FastAPI", "SQL"],
            repositories=MOCK_REPOSITORIES,
        )

        skills = {s["skill"]: s for s in profile["skills"]}

        # Python is in ai-profiler and api-service (2 repos) -> STRONG
        self.assertEqual(skills["Python"]["evidence_status"], EVIDENCE_LEVEL_STRONG)
        self.assertEqual(len(skills["Python"]["supporting_repositories"]), 2)

        # Machine Learning is in ai-profiler and api-service (2 repos) -> STRONG
        self.assertEqual(skills["Machine Learning"]["evidence_status"], EVIDENCE_LEVEL_STRONG)

        # FastAPI is in api-service (1 repo) -> MODERATE
        self.assertEqual(skills["FastAPI"]["evidence_status"], EVIDENCE_LEVEL_MODERATE)
        self.assertEqual(len(skills["FastAPI"]["supporting_repositories"]), 1)

        # SQL is not in any analyzed repo (0 repos) -> NONE_DETECTED
        self.assertEqual(skills["SQL"]["evidence_status"], EVIDENCE_LEVEL_NONE_DETECTED)
        self.assertEqual(len(skills["SQL"]["supporting_repositories"]), 0)

    async def test_07_semantic_integrity_resume_only_skills(self):
        """Test 7: Resume-only skills with NONE_DETECTED do not imply lack of skill."""
        profile = await developer_profile_service.synthesize_profile(
            username="octocat",
            resume_skills=["SQL"],
            repositories=MOCK_REPOSITORIES,
        )

        skills = {s["skill"]: s for s in profile["skills"]}
        sql_skill = skills["SQL"]

        # Verified representation
        self.assertEqual(sql_skill["skill"], "SQL")
        self.assertEqual(sql_skill["sources"], [SOURCE_RESUME])
        self.assertEqual(sql_skill["evidence_status"], EVIDENCE_LEVEL_NONE_DETECTED)
        self.assertEqual(sql_skill["supporting_repositories"], [])

        # SQL is still an active unified skill of the developer
        self.assertIn("SQL", profile["resume"]["skills"])
        self.assertIn("SQL", [s["skill"] for s in profile["skills"]])

    async def test_08_summary_statistics_and_invariants(self):
        """Test 8: Summary metrics correctly calculate counts and satisfy mathematical invariants."""
        profile = await developer_profile_service.synthesize_profile(
            username="octocat",
            resume_skills=["Python", "FastAPI", "SQL", "Docker"],
            repositories=MOCK_REPOSITORIES,
        )

        summary = profile["summary"]

        # Invariant 1: total_skills = supported_skill_count + skills_without_github_evidence
        self.assertEqual(
            summary["total_skills"],
            summary["supported_skill_count"] + summary["skills_without_github_evidence"],
        )

        # Invariant 2: total_skills = github_skill_count + resume_skill_count - skills_from_both_sources
        self.assertEqual(
            summary["total_skills"],
            summary["github_skill_count"]
            + summary["resume_skill_count"]
            - summary["skills_from_both_sources"],
        )

        self.assertEqual(summary["resume_skill_count"], 4)
        self.assertEqual(summary["skills_from_both_sources"], 2)  # Python, FastAPI
        self.assertEqual(summary["skills_without_github_evidence"], 2)  # SQL, Docker
        self.assertEqual(summary["supported_skill_count"], 7)  # All 7 GitHub skills

    async def test_09_resume_text_parsing_integration(self):
        """Test 9: Full resume text parses sections (education, experience, projects) into profile."""
        profile = await developer_profile_service.synthesize_profile(
            username="octocat",
            resume_text=SAMPLE_RESUME_TEXT,
            repositories=MOCK_REPOSITORIES,
        )

        resume = profile["resume"]

        # Resume sections are populated
        self.assertIsNotNone(resume["summary"])
        self.assertIn("Full-stack", resume["summary"])
        self.assertGreater(len(resume["education"]), 0)
        self.assertEqual(resume["education"][0]["institution"], "State University of Technology")
        self.assertGreater(len(resume["experience"]), 0)
        self.assertEqual(resume["experience"][0]["company"], "Tech Solutions Inc")
        self.assertGreater(len(resume["projects"]), 0)
        self.assertEqual(resume["projects"][0]["name"], "Cloud Analytics Platform")
        self.assertIn("Certified AWS Cloud Practitioner", resume["certifications"])

        # Resume skills were parsed and normalized
        self.assertIn("Python", resume["skills"])
        self.assertIn("SQL", resume["skills"])
        self.assertIn("Machine Learning", resume["skills"])

    def test_10_downstream_job_matching_adapter(self):
        """Test 10: Unified profile skills feed seamlessly into Job Description Matching."""
        profile_response = DeveloperProfileResponse(
            developer_id="octocat",
            github={
                "username": "octocat",
                "repositories_analyzed": 3,
                "technologies_detected": ["Python", "FastAPI", "React"],
            },
            resume={
                "summary": "Full stack engineer",
                "skills": ["Python", "SQL"],
                "education": [],
                "experience": [],
                "projects": [],
                "certifications": [],
                "achievements": [],
            },
            skills=[
                {
                    "skill": "Python",
                    "sources": ["github", "resume"],
                    "evidence_status": "STRONG",
                    "supporting_repositories": [],
                },
                {
                    "skill": "FastAPI",
                    "sources": ["github"],
                    "evidence_status": "MODERATE",
                    "supporting_repositories": [],
                },
                {
                    "skill": "SQL",
                    "sources": ["resume"],
                    "evidence_status": "NONE_DETECTED",
                    "supporting_repositories": [],
                },
            ],
            summary={
                "total_skills": 3,
                "github_skill_count": 2,
                "resume_skill_count": 2,
                "skills_from_both_sources": 1,
                "supported_skill_count": 2,
                "skills_without_github_evidence": 1,
            },
        )

        # 1. Method on model
        skill_names = profile_response.get_skill_names()
        self.assertEqual(sorted(skill_names), ["FastAPI", "Python", "SQL"])

        # 2. Standalone adapter helper
        extracted = extract_developer_skills(profile_response)
        self.assertEqual(sorted(extracted), ["FastAPI", "Python", "SQL"])

        # 3. Direct execution with JobMatchingService
        jd = "Seeking a backend engineer with Python and SQL experience."
        match_result = job_matching_service.match_job_description(
            job_description=jd,
            developer_skills=extracted,
        )

        self.assertEqual(match_result["match_percentage"], 100.0)
        self.assertIn("Python", match_result["matched_skills"])
        self.assertIn("SQL", match_result["matched_skills"])
        self.assertEqual(len(match_result["missing_skills"]), 0)


class TestDeveloperProfileAPI(unittest.TestCase):
    """Integration tests for the developer profile API endpoint."""

    def setUp(self):
        self.client = TestClient(app)

    @patch("app.services.github_service.github_service.get_user_repositories")
    def test_11_api_valid_request(self, mock_repos):
        """Test 11: POST /api/v1/developer-profile/analyze returns 200 with schema conformant data."""
        mock_repos.return_value = MOCK_REPOSITORIES

        payload = {
            "github_username": "octocat",
            "resume_skills": ["Python", "SQL"],
        }
        response = self.client.post("/api/v1/developer-profile/analyze", json=payload)

        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertEqual(data["developer_id"], "octocat")
        self.assertEqual(data["github"]["username"], "octocat")
        self.assertEqual(data["github"]["repositories_analyzed"], 3)
        self.assertIn("skills", data)
        self.assertIn("summary", data)

        summary = data["summary"]
        self.assertGreater(summary["total_skills"], 0)
        self.assertEqual(
            summary["total_skills"],
            summary["supported_skill_count"] + summary["skills_without_github_evidence"],
        )

    def test_12_api_invalid_request(self):
        """Test 12: Blank or whitespace-only username returns 422 Unprocessable Entity."""
        # Blank username
        response = self.client.post(
            "/api/v1/developer-profile/analyze",
            json={"github_username": "   "},
        )
        self.assertEqual(response.status_code, 422)

        # Missing required field
        response = self.client.post(
            "/api/v1/developer-profile/analyze",
            json={"resume_skills": ["Python"]},
        )
        self.assertEqual(response.status_code, 422)

    @patch("app.services.github_service.github_service.get_user_repositories")
    def test_13_api_github_errors(self, mock_repos):
        """Test 13: Upstream GitHub errors (not found, rate limit) map to appropriate HTTP codes."""
        # 1. User not found -> 404
        mock_repos.side_effect = GitHubUserNotFoundError("User non-existent not found")
        response = self.client.post(
            "/api/v1/developer-profile/analyze",
            json={"github_username": "non-existent"},
        )
        self.assertEqual(response.status_code, 404)

        # 2. Rate limit or connection failure -> upstream code (e.g. 502)
        mock_repos.side_effect = GitHubAPIError("Rate limit exceeded", status_code=502)
        response = self.client.post(
            "/api/v1/developer-profile/analyze",
            json={"github_username": "octocat"},
        )
        self.assertEqual(response.status_code, 502)


if __name__ == "__main__":
    unittest.main()
