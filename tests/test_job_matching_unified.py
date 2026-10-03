"""
test_job_matching_unified.py
----------------------------
Task 11.3 — Unified Developer Profile Integration Tests for Job Matching.

Verifies:
1. DeveloperProfile integration via match_profile_job_description()
2. Matched GitHub evidence preservation (sources, evidence_status, supporting_repositories)
3. GitHub + Resume skill retention (sources=['github', 'resume'])
4. Resume-only skill semantics (NONE_DETECTED, sources=['resume'], supporting_repositories=[])
5. Missing skill details (categories populated, empty evidence fields)
6. Multi-category skill handling (e.g. SQL in Programming Languages and Databases)
7. Category breakdown correctness and invariant (matched + missing == required)
8. Global invariant (matched_skill_count + missing_skill_count == total_required_skills)
9. Duplicate and case normalization (python, Python, PYTHON -> 1 canonical skill)
10. Alias normalization (nodejs -> Node.js, postgres -> PostgreSQL)
11. Empty developer skills handling (0.0% match, all required skills missing)
12. Zero detectable JD skills safe behavior (0.0% coverage without division error)
13. Legacy compatibility of POST /api/v1/job-matching/analyze
14. Developer profile helper compatibility (get_skill_names and extract_developer_skills)
15. Legacy List[str] matching via direct match_job_description()
16. Sequence[DeveloperSkill] direct matching
"""

import sys
import unittest
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from fastapi.testclient import TestClient

from app.main import app
from app.schemas.developer_profile import (
    DeveloperProfileResponse,
    DeveloperProfileSummary,
    DeveloperSkill,
    DeveloperSkillEvidence,
    GitHubSummary,
    ResumeSummary,
)
from app.schemas.evidence import SupportingRepository
from app.schemas.job_matching import (
    JobMatchCategoryBreakdown,
    JobMatchingRequest,
    JobMatchingResponse,
    JobMatchSkillDetail,
)
from app.services.developer_profile_service import extract_developer_skills
from app.services.job_matching_service import job_matching_service


class TestJobMatchingUnified(unittest.TestCase):
    """Test suite for Unified Developer Profile Job Matching Intelligence."""

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def _build_mock_developer_profile(self) -> DeveloperProfileResponse:
        """Construct a realistic DeveloperProfileResponse with rich evidence."""
        skills = [
            DeveloperSkill(
                skill="Python",
                name="Python",
                categories=["Programming Languages"],
                sources=["github", "resume"],
                evidence_status="STRONG",
                evidence=DeveloperSkillEvidence(
                    repository_count=2,
                    evidence_count=3,
                    evidence_strength="STRONG",
                    supporting_repositories=["data-pipeline", "ml-service"],
                    signal_types=["SOURCE_LANGUAGE", "DEPENDENCY_MANIFEST"],
                    resume_sources=["skills_section", "project_text"],
                ),
                supporting_repositories=[
                    SupportingRepository(name="data-pipeline", confidence="STRONG"),
                    SupportingRepository(name="ml-service", confidence="STRONG"),
                ],
            ),
            DeveloperSkill(
                skill="FastAPI",
                name="FastAPI",
                categories=["Frameworks & Libraries"],
                sources=["github"],
                evidence_status="STRONG",
                evidence=DeveloperSkillEvidence(
                    repository_count=1,
                    evidence_count=1,
                    evidence_strength="STRONG",
                    supporting_repositories=["data-pipeline"],
                    signal_types=["DEPENDENCY_MANIFEST"],
                ),
                supporting_repositories=[
                    SupportingRepository(name="data-pipeline", confidence="STRONG"),
                ],
            ),
            DeveloperSkill(
                skill="SQL",
                name="SQL",
                categories=["Programming Languages", "Databases"],
                sources=["resume"],
                evidence_status="NONE_DETECTED",
                evidence=DeveloperSkillEvidence(
                    repository_count=0,
                    evidence_count=0,
                    evidence_strength=None,
                    supporting_repositories=[],
                    signal_types=[],
                    resume_sources=["skills_section"],
                ),
                supporting_repositories=[],
            ),
            DeveloperSkill(
                skill="Docker",
                name="Docker",
                categories=["DevOps & Cloud"],
                sources=["github"],
                evidence_status="MODERATE",
                evidence=DeveloperSkillEvidence(
                    repository_count=1,
                    evidence_count=1,
                    evidence_strength="MODERATE",
                    supporting_repositories=["ml-service"],
                    signal_types=["DEPENDENCY_MANIFEST"],
                ),
                supporting_repositories=[
                    SupportingRepository(name="ml-service", confidence="MODERATE"),
                ],
            ),
        ]

        return DeveloperProfileResponse(
            developer_id="octodev",
            github=GitHubSummary(
                username="octodev",
                repositories_analyzed=2,
                technologies_detected=["Python", "FastAPI", "Docker"],
            ),
            resume=ResumeSummary(
                summary="Backend developer",
                skills=["Python", "SQL"],
            ),
            skills=skills,
            categorized_skills=[],
            summary=DeveloperProfileSummary(
                total_skills=4,
                github_skill_count=3,
                resume_skill_count=2,
                skills_from_both_sources=1,
                github_only_skills=2,
                resume_only_skills=1,
                supported_skill_count=3,
                skills_without_github_evidence=1,
            ),
        )

    # 1. DeveloperProfile integration
    def test_01_developer_profile_integration(self):
        """Pass DeveloperProfileResponse to match_profile_job_description and verify matching."""
        profile = self._build_mock_developer_profile()
        jd = "Requirements: Python, FastAPI, PostgreSQL, Docker, Kubernetes"

        res = job_matching_service.match_profile_job_description(
            job_description=jd,
            profile=profile,
        )

        self.assertEqual(res["total_required_skills"], 5)
        self.assertEqual(res["matched_skill_count"], 3)
        self.assertEqual(res["missing_skill_count"], 2)
        self.assertEqual(sorted(res["matched_skills"]), ["Docker", "FastAPI", "Python"])
        self.assertEqual(sorted(res["missing_skills"]), ["Kubernetes", "PostgreSQL"])
        self.assertEqual(res["match_percentage"], 60.0)

        # Output should validate directly through JobMatchingResponse
        validated = JobMatchingResponse(**res)
        self.assertEqual(validated.match_percentage, 60.0)
        self.assertEqual(len(validated.matched_skill_details), 3)
        self.assertEqual(len(validated.missing_skill_details), 2)

    # 2. Matched GitHub evidence
    def test_02_matched_github_evidence_preservation(self):
        """Verified GitHub evidence (sources, evidence_status, supporting_repositories) is preserved."""
        profile = self._build_mock_developer_profile()
        jd = "Must have experience with FastAPI and Docker."

        res = job_matching_service.match_profile_job_description(
            job_description=jd,
            profile=profile,
        )

        matched_details = {item["name"]: item for item in res["matched_skill_details"]}

        fastapi = matched_details["FastAPI"]
        self.assertEqual(fastapi["name"], "FastAPI")
        self.assertEqual(fastapi["sources"], ["github"])
        self.assertEqual(fastapi["evidence_status"], "STRONG")
        self.assertEqual(fastapi["supporting_repositories"], ["data-pipeline"])

        docker = matched_details["Docker"]
        self.assertEqual(docker["name"], "Docker")
        self.assertEqual(docker["sources"], ["github"])
        self.assertEqual(docker["evidence_status"], "MODERATE")
        self.assertEqual(docker["supporting_repositories"], ["ml-service"])

    # 3. GitHub + Resume skill
    def test_03_github_plus_resume_skill_retention(self):
        """Skills present in both sources retain sources=['github', 'resume'] with GitHub evidence."""
        profile = self._build_mock_developer_profile()
        jd = "Looking for a Python developer."

        res = job_matching_service.match_profile_job_description(
            job_description=jd,
            profile=profile,
        )

        matched_details = {item["name"]: item for item in res["matched_skill_details"]}
        python = matched_details["Python"]
        self.assertEqual(sorted(python["sources"]), ["github", "resume"])
        self.assertEqual(python["evidence_status"], "STRONG")
        self.assertEqual(sorted(python["supporting_repositories"]), ["data-pipeline", "ml-service"])

    # 4. Resume-only skill
    def test_04_resume_only_skill_semantics(self):
        """Resume-only skill maintains sources=['resume'], status='NONE_DETECTED', and repos=[]."""
        profile = self._build_mock_developer_profile()
        jd = "Position requires strong SQL knowledge."

        res = job_matching_service.match_profile_job_description(
            job_description=jd,
            profile=profile,
        )

        matched_details = {item["name"]: item for item in res["matched_skill_details"]}
        sql = matched_details["SQL"]
        self.assertEqual(sql["name"], "SQL")
        self.assertEqual(sql["sources"], ["resume"])
        self.assertEqual(sql["evidence_status"], "NONE_DETECTED")
        self.assertEqual(sql["supporting_repositories"], [])

    # 5. Missing skill
    def test_05_missing_skill_details(self):
        """Missing skills have categories populated, sources=[], evidence_status=None, repos=[]."""
        profile = self._build_mock_developer_profile()
        jd = "Requirements: Python, PostgreSQL, Redis"

        res = job_matching_service.match_profile_job_description(
            job_description=jd,
            profile=profile,
        )

        missing_details = {item["name"]: item for item in res["missing_skill_details"]}
        self.assertIn("PostgreSQL", missing_details)
        self.assertIn("Redis", missing_details)

        postgres = missing_details["PostgreSQL"]
        self.assertEqual(postgres["name"], "PostgreSQL")
        self.assertIn("Databases", postgres["categories"])
        self.assertEqual(postgres["sources"], [])
        self.assertIsNone(postgres["evidence_status"])
        self.assertEqual(postgres["supporting_repositories"], [])

    # 6. Multi-category skill
    def test_06_multi_category_skill(self):
        """Multi-category skills (e.g. SQL) belong to both Programming Languages and Databases."""
        profile = self._build_mock_developer_profile()
        jd = "Seeking a developer skilled in Python and SQL."

        res = job_matching_service.match_profile_job_description(
            job_description=jd,
            profile=profile,
        )

        matched_details = {item["name"]: item for item in res["matched_skill_details"]}
        sql = matched_details["SQL"]
        self.assertIn("Programming Languages", sql["categories"])
        self.assertIn("Databases", sql["categories"])

        category_map = {c["category"]: c for c in res["category_breakdown"]}
        self.assertIn("Programming Languages", category_map)
        self.assertIn("Databases", category_map)

        # SQL is counted in Programming Languages (with Python) and in Databases
        self.assertEqual(category_map["Programming Languages"]["required_count"], 2)
        self.assertEqual(category_map["Programming Languages"]["matched_count"], 2)
        self.assertEqual(category_map["Databases"]["required_count"], 1)
        self.assertEqual(category_map["Databases"]["matched_count"], 1)

    # 7. Category breakdown
    def test_07_category_breakdown_invariants(self):
        """Verify matched_count + missing_count == required_count for every category."""
        profile = self._build_mock_developer_profile()
        jd = "Requirements: Python, SQL, Docker, Redis, Kubernetes"

        res = job_matching_service.match_profile_job_description(
            job_description=jd,
            profile=profile,
        )

        breakdown = res["category_breakdown"]
        self.assertGreater(len(breakdown), 0)

        for cat in breakdown:
            req = cat["required_count"]
            mat = cat["matched_count"]
            mis = cat["missing_count"]
            cov = cat["coverage_percentage"]

            self.assertEqual(mat + mis, req, f"Invariant violated for category {cat['category']}")
            expected_cov = round((mat / req) * 100.0, 2) if req > 0 else 0.0
            self.assertEqual(cov, expected_cov)

    # 8. Global invariant
    def test_08_global_invariant(self):
        """matched_skill_count + missing_skill_count == total_required_skills."""
        profile = self._build_mock_developer_profile()
        jd = "Requirements: Python, FastAPI, Docker, PostgreSQL, Redis, Kubernetes"

        res = job_matching_service.match_profile_job_description(
            job_description=jd,
            profile=profile,
        )

        self.assertEqual(
            res["matched_skill_count"] + res["missing_skill_count"],
            res["total_required_skills"],
        )

    # 9. Duplicate and case normalization
    def test_09_duplicate_and_case_normalization(self):
        """Input ['python', 'Python', 'PYTHON'] counts as exactly one canonical skill."""
        jd = "Requirements: Python, FastAPI"
        res = job_matching_service.match_job_description(
            job_description=jd,
            developer_skills=["python", "Python", "PYTHON"],
        )

        self.assertEqual(res["matched_skill_count"], 1)
        self.assertEqual(res["matched_skills"], ["Python"])
        self.assertEqual(len(res["matched_skill_details"]), 1)
        self.assertEqual(res["matched_skill_details"][0]["name"], "Python")

    # 10. Alias normalization
    def test_10_alias_normalization(self):
        """Aliases like nodejs -> Node.js and postgres -> PostgreSQL match canonical JD skills."""
        res = job_matching_service.match_job_description(
            job_description="Requirements: Node.js, PostgreSQL, Docker",
            extracted_skills=["Node.js", "PostgreSQL", "Docker"],
            developer_skills=["nodejs", "postgres", "docker"],
        )

        self.assertEqual(res["matched_skill_count"], 3)
        self.assertEqual(sorted(res["matched_skills"]), ["Docker", "Node.js", "PostgreSQL"])
        self.assertEqual(res["missing_skill_count"], 0)
        self.assertEqual(res["match_percentage"], 100.0)

    # 11. Empty developer skills
    def test_11_empty_developer_skills(self):
        """Empty developer skill input yields 0.0% match with all skills missing."""
        jd = "Requirements: Python, FastAPI, Docker"
        res = job_matching_service.match_job_description(
            job_description=jd,
            developer_skills=[],
        )

        self.assertEqual(res["total_required_skills"], 3)
        self.assertEqual(res["matched_skill_count"], 0)
        self.assertEqual(res["missing_skill_count"], 3)
        self.assertEqual(res["matched_skills"], [])
        self.assertEqual(res["matched_skill_details"], [])
        self.assertEqual(res["match_percentage"], 0.0)

        for cat in res["category_breakdown"]:
            self.assertEqual(cat["matched_count"], 0)
            self.assertEqual(cat["missing_count"], cat["required_count"])
            self.assertEqual(cat["coverage_percentage"], 0.0)

    # 12. Zero detectable JD skills
    def test_12_zero_detectable_jd_skills(self):
        """Job description with zero detectable technical skills returns 0.0% safely."""
        jd = "General office manager needed with communication and leadership abilities."
        profile = self._build_mock_developer_profile()

        res = job_matching_service.match_profile_job_description(
            job_description=jd,
            profile=profile,
        )

        self.assertEqual(res["total_required_skills"], 0)
        self.assertEqual(res["matched_skill_count"], 0)
        self.assertEqual(res["missing_skill_count"], 0)
        self.assertEqual(res["match_percentage"], 0.0)
        self.assertEqual(res["matched_skill_details"], [])
        self.assertEqual(res["missing_skill_details"], [])
        self.assertEqual(res["category_breakdown"], [])

    # 13. Legacy compatibility
    def test_13_api_backward_compatibility(self):
        """POST /api/v1/job-matching/analyze contract remains fully functional."""
        payload = {
            "job_description": "We need Python and Docker expertise.",
            "developer_skills": ["Python", "FastAPI"],
        }
        resp = self.client.post("/api/v1/job-matching/analyze", json=payload)
        self.assertEqual(resp.status_code, 200)

        data = resp.json()
        # Verify legacy fields
        self.assertEqual(sorted(data["extracted_skills"]), ["Docker", "Python"])
        self.assertEqual(data["matched_skills"], ["Python"])
        self.assertEqual(data["missing_skills"], ["Docker"])
        self.assertEqual(data["total_required_skills"], 2)
        self.assertEqual(data["matched_skill_count"], 1)
        self.assertEqual(data["missing_skill_count"], 1)
        self.assertEqual(data["match_percentage"], 50.0)

        # Verify additive fields
        self.assertIn("matched_skill_details", data)
        self.assertIn("missing_skill_details", data)
        self.assertIn("category_breakdown", data)
        self.assertEqual(len(data["matched_skill_details"]), 1)
        self.assertEqual(len(data["missing_skill_details"]), 1)
        self.assertGreater(len(data["category_breakdown"]), 0)

    # 14. Developer profile helper compatibility
    def test_14_developer_profile_helpers(self):
        """get_skill_names() and extract_developer_skills() behave as expected."""
        profile = self._build_mock_developer_profile()
        names = profile.get_skill_names()
        self.assertEqual(sorted(names), ["Docker", "FastAPI", "Python", "SQL"])

        extracted = extract_developer_skills(profile)
        self.assertEqual(sorted(extracted), ["Docker", "FastAPI", "Python", "SQL"])

    # 15. Legacy List[str] matching
    def test_15_legacy_list_str_matching(self):
        """Direct call to match_job_description with List[str] works cleanly."""
        res = job_matching_service.match_job_description(
            job_description="Requirements: Python, Docker, PostgreSQL",
            developer_skills=["Python", "Docker"],
        )
        self.assertEqual(res["matched_skill_count"], 2)
        self.assertEqual(res["missing_skill_count"], 1)
        self.assertEqual(res["match_percentage"], 66.67)
        self.assertEqual(len(res["matched_skill_details"]), 2)
        # For legacy flat string input, evidence fields default cleanly
        self.assertEqual(res["matched_skill_details"][0]["sources"], [])
        self.assertIsNone(res["matched_skill_details"][0]["evidence_status"])
        self.assertEqual(res["matched_skill_details"][0]["supporting_repositories"], [])

    # 16. Sequence[DeveloperSkill]
    def test_16_sequence_developer_skill_matching(self):
        """Direct call with Sequence[DeveloperSkill] preserves rich metadata."""
        profile = self._build_mock_developer_profile()
        res = job_matching_service.match_job_description(
            job_description="Requirements: Python, Docker",
            developer_skills=profile.skills,
        )
        self.assertEqual(res["matched_skill_count"], 2)
        self.assertEqual(res["match_percentage"], 100.0)

        matched_details = {item["name"]: item for item in res["matched_skill_details"]}
        self.assertEqual(matched_details["Python"]["evidence_status"], "STRONG")
        self.assertEqual(matched_details["Docker"]["evidence_status"], "MODERATE")


if __name__ == "__main__":
    unittest.main()
