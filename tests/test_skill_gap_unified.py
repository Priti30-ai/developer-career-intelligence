"""
test_skill_gap_unified.py
-------------------------
Task 11.1 — Unified Developer Profile Integration Tests for Skill Gap Analysis.

Verifies:
1. Existing behavior preserved
2. DeveloperProfileResponse integration via analyze_profile_gap()
3. Grounded GitHub evidence preservation (sources, evidence_status, supporting_repositories)
4. Resume-only semantics (NONE_DETECTED, sources=['resume'], no invented GitHub evidence)
5. Missing skill categories from canonical taxonomy
6. Multi-category skill handling (e.g. SQL contributes to both Programming Languages and Databases)
7. Category breakdown correctness, coverage percentage, and invariants (matched + missing == required)
8. Duplicate and case normalization (Python, python, PYTHON -> single match)
9. Alias normalization (nodejs -> Node.js)
10. Empty developer skills input (0% match, all required missing)
11. Unknown developer skills (no crash, no false matches)
12. Backward compatibility of SkillGapRequest / SkillGapResponse / POST /api/v1/skill-gap/analyze
13. Downstream compatibility with career_recommendation_service
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
    DeveloperSkill,
    DeveloperSkillEvidence,
)
from app.schemas.evidence import SupportingRepository
from app.schemas.github_account import (
    EVIDENCE_SOURCE_LANGUAGE,
    EVIDENCE_SOURCE_MANIFEST,
    EVIDENCE_STRENGTH_STRONG,
    EvidenceSourceSignal,
    RepositoryAnalysisDetail,
)
from app.schemas.skill_gap import (
    SkillGapCategoryBreakdown,
    SkillGapItemDetail,
    SkillGapRequest,
    SkillGapResponse,
)
from app.services.career_recommendation_service import career_recommendation_service
from app.services.career_role_service import career_role_service
from app.services.developer_profile_service import developer_profile_service
from app.services.skill_gap_service import skill_gap_service
from app.services.skill_profile_service import _classify_technology


class TestSkillGapUnified(unittest.IsolatedAsyncioTestCase):
    """Test suite for Unified Developer Profile Skill Gap Intelligence."""

    def setUp(self):
        self.client = TestClient(app)

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
                skill="Pandas",
                name="Pandas",
                categories=["Frameworks & Libraries", "AI / Machine Learning"],
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

        from app.schemas.developer_profile import (
            DeveloperProfileSummary,
            GitHubSummary,
            ResumeSummary,
        )

        return DeveloperProfileResponse(
            developer_id="octodev",
            github=GitHubSummary(
                username="octodev",
                repositories_analyzed=2,
                technologies_detected=["Python", "Pandas", "Docker"],
            ),
            resume=ResumeSummary(
                summary="Data and backend developer",
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

    # Test 1 — Existing behavior
    def test_01_existing_behavior_preserved(self):
        """Legacy flat list input continues to return exact existing fields."""
        result = skill_gap_service.analyze_gap(
            target_role="data-scientist",
            current_skills=["Python", "Pandas", "NumPy", "Machine Learning"],
        )
        self.assertIn("target_role", result)
        self.assertIn("role_slug", result)
        self.assertIn("total_required_skills", result)
        self.assertIn("total_matched_skills", result)
        self.assertIn("total_missing_skills", result)
        self.assertIn("skill_match_percentage", result)
        self.assertIn("match_percentage", result)
        self.assertIn("matched_skills", result)
        self.assertIn("missing_skills", result)

        self.assertEqual(result["total_matched_skills"], 4)
        self.assertEqual(result["total_missing_skills"], 4)
        self.assertEqual(result["total_required_skills"], 8)
        self.assertEqual(result["skill_match_percentage"], 50.0)

    # Test 2 — DeveloperProfile integration
    def test_02_developer_profile_integration(self):
        """Pass DeveloperProfileResponse to analyze_profile_gap() and verify matched/missing skills."""
        profile = self._build_mock_developer_profile()
        result = skill_gap_service.analyze_profile_gap(
            profile=profile,
            target_role="data-scientist",
        )

        # Target role data-scientist requires:
        # Python, SQL, Pandas, NumPy, Scikit-learn, Machine Learning, Data Visualization, Statistics
        # Profile contains: Python, Pandas, SQL, Docker
        matched = result["matched_skills"]
        missing = result["missing_skills"]

        self.assertIn("Python", matched)
        self.assertIn("Pandas", matched)
        self.assertIn("SQL", matched)
        self.assertNotIn("Docker", matched)  # Docker not required for data-scientist

        self.assertIn("NumPy", missing)
        self.assertIn("Scikit-learn", missing)
        self.assertIn("Machine Learning", missing)
        self.assertIn("Data Visualization", missing)
        self.assertIn("Statistics", missing)

        self.assertEqual(result["total_matched_skills"], 3)
        self.assertEqual(result["total_missing_skills"], 5)
        self.assertEqual(result["total_required_skills"], 8)
        self.assertEqual(result["skill_match_percentage"], 37.5)

    # Test 3 — Evidence preservation
    def test_03_evidence_preservation(self):
        """Verified GitHub evidence (sources, evidence_status, supporting_repositories) is preserved."""
        profile = self._build_mock_developer_profile()
        result = skill_gap_service.analyze_profile_gap(
            profile=profile,
            target_role="data-scientist",
        )

        matched_details = {item["name"]: item for item in result["matched_skill_details"]}

        # Python was present in GitHub and Resume with STRONG status
        python_detail = matched_details["Python"]
        self.assertEqual(python_detail["name"], "Python")
        self.assertEqual(sorted(python_detail["sources"]), ["github", "resume"])
        self.assertEqual(python_detail["evidence_status"], "STRONG")
        self.assertEqual(
            sorted(python_detail["supporting_repositories"]),
            ["data-pipeline", "ml-service"],
        )

        # Pandas was present in GitHub only
        pandas_detail = matched_details["Pandas"]
        self.assertEqual(pandas_detail["name"], "Pandas")
        self.assertEqual(pandas_detail["sources"], ["github"])
        self.assertEqual(pandas_detail["evidence_status"], "STRONG")
        self.assertEqual(pandas_detail["supporting_repositories"], ["data-pipeline"])

    # Test 4 — Resume-only semantics
    def test_04_resume_only_semantics(self):
        """Resume-only skill has sources=['resume'], status='NONE_DETECTED', and no invented GitHub repos."""
        profile = self._build_mock_developer_profile()
        result = skill_gap_service.analyze_profile_gap(
            profile=profile,
            target_role="data-scientist",
        )

        matched_details = {item["name"]: item for item in result["matched_skill_details"]}
        sql_detail = matched_details["SQL"]

        self.assertEqual(sql_detail["name"], "SQL")
        self.assertEqual(sql_detail["sources"], ["resume"])
        self.assertEqual(sql_detail["evidence_status"], "NONE_DETECTED")
        self.assertEqual(sql_detail["supporting_repositories"], [])

    # Test 5 — Missing skill categories
    def test_05_missing_skill_categories(self):
        """Missing skills receive taxonomy categories from _classify_technology()."""
        profile = self._build_mock_developer_profile()
        result = skill_gap_service.analyze_profile_gap(
            profile=profile,
            target_role="data-scientist",
        )

        missing_details = {item["name"]: item for item in result["missing_skill_details"]}

        # NumPy should have Frameworks & Libraries and AI / Machine Learning
        numpy_cats = missing_details["NumPy"]["categories"]
        self.assertIn("Frameworks & Libraries", numpy_cats)
        self.assertIn("AI / Machine Learning", numpy_cats)

        # Evidence fields must be empty for missing skills
        self.assertEqual(missing_details["NumPy"]["sources"], [])
        self.assertIsNone(missing_details["NumPy"]["evidence_status"])
        self.assertEqual(missing_details["NumPy"]["supporting_repositories"], [])

    # Test 6 — Multi-category skill
    def test_06_multi_category_skill(self):
        """SQL contributes to both 'Programming Languages' and 'Databases' categories."""
        profile = self._build_mock_developer_profile()
        result = skill_gap_service.analyze_profile_gap(
            profile=profile,
            target_role="data-scientist",
        )

        category_map = {c["category"]: c for c in result["category_breakdown"]}

        # SQL is required by data-scientist, and is matched
        self.assertIn("Programming Languages", category_map)
        self.assertIn("Databases", category_map)

        prog_lang = category_map["Programming Languages"]
        db = category_map["Databases"]

        # Programming Languages requires Python and SQL (2 required)
        self.assertEqual(prog_lang["required_count"], 2)
        # Both Python and SQL are matched in the mock profile
        self.assertEqual(prog_lang["matched_count"], 2)
        self.assertEqual(prog_lang["missing_count"], 0)
        self.assertEqual(prog_lang["coverage_percentage"], 100.0)

        # Databases requires SQL (1 required)
        self.assertEqual(db["required_count"], 1)
        self.assertEqual(db["matched_count"], 1)
        self.assertEqual(db["missing_count"], 0)
        self.assertEqual(db["coverage_percentage"], 100.0)

    # Test 7 — Category breakdown
    def test_07_category_breakdown_invariants(self):
        """Verify matched_count + missing_count == required_count for every category."""
        profile = self._build_mock_developer_profile()
        result = skill_gap_service.analyze_profile_gap(
            profile=profile,
            target_role="data-scientist",
        )

        breakdown = result["category_breakdown"]
        self.assertGreater(len(breakdown), 0)

        for cat in breakdown:
            req = cat["required_count"]
            mat = cat["matched_count"]
            mis = cat["missing_count"]
            cov = cat["coverage_percentage"]

            self.assertEqual(mat + mis, req, f"Invariant violated for category {cat['category']}")
            expected_cov = round((mat / req) * 100.0, 2) if req > 0 else 0.0
            self.assertEqual(cov, expected_cov)

        # Global invariants
        self.assertEqual(
            result["total_matched_skills"] + result["total_missing_skills"],
            result["total_required_skills"],
        )

    # Test 8 — Duplicate and case normalization
    def test_08_duplicate_and_case_normalization(self):
        """Input ['python', 'Python', 'PYTHON'] counts as exactly one canonical skill."""
        result = skill_gap_service.analyze_gap(
            target_role="data-scientist",
            current_skills=["python", "Python", "PYTHON"],
        )
        self.assertEqual(result["total_matched_skills"], 1)
        self.assertEqual(result["matched_skills"], ["Python"])
        self.assertEqual(len(result["matched_skill_details"]), 1)
        self.assertEqual(result["matched_skill_details"][0]["name"], "Python")

    # Test 9 — Alias normalization
    def test_09_alias_normalization(self):
        """nodejs normalizes to Node.js and matches full-stack-developer role."""
        result = skill_gap_service.analyze_gap(
            target_role="full-stack-developer",
            current_skills=["nodejs", "reactjs", "docker"],
        )
        self.assertIn("Node.js", result["matched_skills"])
        self.assertIn("React", result["matched_skills"])
        self.assertIn("Docker", result["matched_skills"])

    # Test 10 — Empty input
    def test_10_empty_developer_skills(self):
        """current_skills = [] produces 0% match and all required skills missing."""
        result = skill_gap_service.analyze_gap(
            target_role="data-scientist",
            current_skills=[],
        )
        self.assertEqual(result["total_matched_skills"], 0)
        self.assertEqual(result["matched_skills"], [])
        self.assertEqual(result["matched_skill_details"], [])
        self.assertEqual(result["total_missing_skills"], 8)
        self.assertEqual(result["skill_match_percentage"], 0.0)

        for cat in result["category_breakdown"]:
            self.assertEqual(cat["matched_count"], 0)
            self.assertEqual(cat["missing_count"], cat["required_count"])
            self.assertEqual(cat["coverage_percentage"], 0.0)

    # Test 11 — Unknown skills
    def test_11_unknown_developer_skills(self):
        """Unknown skills do not cause exceptions or create false matches."""
        result = skill_gap_service.analyze_gap(
            target_role="data-scientist",
            current_skills=["UnknownTechXYZ", "NonExistentLib123"],
        )
        self.assertEqual(result["total_matched_skills"], 0)
        self.assertEqual(result["matched_skills"], [])
        self.assertEqual(result["total_missing_skills"], 8)
        self.assertEqual(result["skill_match_percentage"], 0.0)

    # Test 12 — Backward compatibility
    def test_12_api_backward_compatibility(self):
        """POST /api/v1/skill-gap/analyze continues working with legacy payload and response."""
        payload = {
            "target_role": "data-scientist",
            "current_skills": ["Python", "Pandas", "NumPy", "Machine Learning"],
        }
        response = self.client.post("/api/v1/skill-gap/analyze", json=payload)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        # Old fields
        self.assertEqual(data["target_role"], "Data Scientist")
        self.assertEqual(data["role_slug"], "data-scientist")
        self.assertEqual(data["total_required_skills"], 8)
        self.assertEqual(data["total_matched_skills"], 4)
        self.assertEqual(data["total_missing_skills"], 4)
        self.assertEqual(data["skill_match_percentage"], 50.0)
        self.assertEqual(data["match_percentage"], 50.0)
        self.assertIsInstance(data["matched_skills"], list)
        self.assertIsInstance(data["missing_skills"], list)

        # New additive fields
        self.assertIn("matched_skill_details", data)
        self.assertIn("missing_skill_details", data)
        self.assertIn("category_breakdown", data)
        self.assertEqual(len(data["matched_skill_details"]), 4)
        self.assertEqual(len(data["missing_skill_details"]), 4)
        self.assertGreater(len(data["category_breakdown"]), 0)

        # Validates cleanly through Pydantic SkillGapResponse
        validated = SkillGapResponse(**data)
        self.assertEqual(validated.skill_match_percentage, 50.0)
        self.assertEqual(len(validated.matched_skill_details), 4)

    # Test 13 — Downstream compatibility
    def test_13_downstream_career_recommendation_service(self):
        """career_recommendation_service functions cleanly with updated SkillGapService."""
        result = career_recommendation_service.generate_recommendations(
            target_role="data-scientist",
            current_skills=["Python", "Pandas"],
        )
        self.assertEqual(result["target_role"], "Data Scientist")
        self.assertEqual(result["total_matched_skills"], 2)
        self.assertEqual(result["total_missing_skills"], 6)
        self.assertEqual(result["skill_match_percentage"], 25.0)
        self.assertGreater(len(result["recommendations"]), 0)
        self.assertGreater(len(result["roadmap"]), 0)


if __name__ == "__main__":
    unittest.main()
