"""
test_developer_profile_unified.py
---------------------------------
Task 11.0B — Unified Developer Profile Synthesis Tests.

Verifies:
1. GitHub-only skill representation and tagging
2. Resume-only skill representation and tagging
3. Skill present in both sources with dual sources ['github', 'resume']
4. Python/python casing normalization
5. React/reactjs alias normalization
6. GitHub manifest evidence signal preservation
7. GitHub evidence strength preservation (STRONG, MODERATE, WEAK)
8. Resume skills_section provenance tracking
9. Resume project_text provenance tracking
10. Resume experience_text provenance tracking
11. Multi-category skill classification (e.g. SQL, TensorFlow, Prisma)
12. NONE_DETECTED semantics (indicates absence of GitHub evidence, not lack of skill)
13. Supporting repository names and models preservation
14. Summary metric correctness and mathematical invariants
15. Existing get_skill_names() compatibility with downstream modules
16. Existing frontend field compatibility (dashboard components, chart fields, status badges)
"""

import sys
import unittest
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from app.schemas.developer_profile import (
    SOURCE_GITHUB,
    SOURCE_RESUME,
    DeveloperProfileResponse,
    DeveloperSkill,
)
from app.schemas.github_account import (
    EVIDENCE_SOURCE_CONFIG,
    EVIDENCE_SOURCE_LANGUAGE,
    EVIDENCE_SOURCE_MANIFEST,
    EVIDENCE_SOURCE_TOPIC,
    EVIDENCE_STRENGTH_MODERATE,
    EVIDENCE_STRENGTH_STRONG,
    EvidenceSourceSignal,
    RepositoryAnalysisDetail,
)
from app.services.developer_profile_service import (
    EVIDENCE_LEVEL_MODERATE,
    EVIDENCE_LEVEL_NONE_DETECTED,
    EVIDENCE_LEVEL_STRONG,
    developer_profile_service,
    extract_developer_skills,
)


class TestDeveloperProfileUnified(unittest.IsolatedAsyncioTestCase):
    """Focused tests for the enhanced Unified Developer Profile synthesis."""

    def _build_rich_test_repos(self):
        """Create mock RepositoryAnalysisDetail objects with manifest and language evidence."""
        repo1 = RepositoryAnalysisDetail(
            name="backend-api",
            full_name="testuser/backend-api",
            html_url="https://github.com/testuser/backend-api",
            primary_language="Python",
            languages=["Python"],
            technologies=["Python", "FastAPI", "PostgreSQL", "Docker"],
            skills=["Python", "FastAPI", "PostgreSQL", "Docker"],
            evidence=[
                EvidenceSourceSignal(
                    source_type=EVIDENCE_SOURCE_MANIFEST,
                    technology="FastAPI",
                    strength=EVIDENCE_STRENGTH_STRONG,
                    path="requirements.txt",
                ),
                EvidenceSourceSignal(
                    source_type=EVIDENCE_SOURCE_LANGUAGE,
                    technology="Python",
                    strength=EVIDENCE_STRENGTH_MODERATE,
                ),
                EvidenceSourceSignal(
                    source_type=EVIDENCE_SOURCE_CONFIG,
                    technology="Docker",
                    strength=EVIDENCE_STRENGTH_STRONG,
                    path="Dockerfile",
                ),
                EvidenceSourceSignal(
                    source_type=EVIDENCE_SOURCE_MANIFEST,
                    technology="PostgreSQL",
                    strength=EVIDENCE_STRENGTH_STRONG,
                    path="docker-compose.yml",
                ),
            ],
        )

        repo2 = RepositoryAnalysisDetail(
            name="data-service",
            full_name="testuser/data-service",
            html_url="https://github.com/testuser/data-service",
            primary_language="Python",
            languages=["Python"],
            technologies=["Python", "TensorFlow", "PostgreSQL"],
            skills=["Python", "TensorFlow", "PostgreSQL"],
            evidence=[
                EvidenceSourceSignal(
                    source_type=EVIDENCE_SOURCE_LANGUAGE,
                    technology="Python",
                    strength=EVIDENCE_STRENGTH_MODERATE,
                ),
                EvidenceSourceSignal(
                    source_type=EVIDENCE_SOURCE_MANIFEST,
                    technology="TensorFlow",
                    strength=EVIDENCE_STRENGTH_STRONG,
                    path="requirements.txt",
                ),
                EvidenceSourceSignal(
                    source_type=EVIDENCE_SOURCE_MANIFEST,
                    technology="PostgreSQL",
                    strength=EVIDENCE_STRENGTH_STRONG,
                    path="requirements.txt",
                ),
            ],
        )

        return [repo1, repo2]

    # 1. GitHub-only skill
    async def test_01_github_only_skill(self):
        repos = self._build_rich_test_repos()
        profile = await developer_profile_service.synthesize_profile(
            username="testuser",
            resume_skills=["React"],  # Docker is only on GitHub
            repositories=repos,
        )
        skills_map = {s["name"]: s for s in profile["skills"]}
        self.assertIn("Docker", skills_map)
        docker = skills_map["Docker"]
        self.assertEqual(docker["sources"], [SOURCE_GITHUB])
        self.assertEqual(docker["evidence_status"], EVIDENCE_LEVEL_STRONG)
        self.assertIn("backend-api", docker["evidence"]["supporting_repositories"])

    # 2. Resume-only skill
    async def test_02_resume_only_skill(self):
        repos = self._build_rich_test_repos()
        profile = await developer_profile_service.synthesize_profile(
            username="testuser",
            resume_skills=["Kubernetes"],  # Kubernetes not in GitHub repos
            repositories=repos,
        )
        skills_map = {s["name"]: s for s in profile["skills"]}
        self.assertIn("Kubernetes", skills_map)
        k8s = skills_map["Kubernetes"]
        self.assertEqual(k8s["sources"], [SOURCE_RESUME])
        self.assertEqual(k8s["evidence_status"], EVIDENCE_LEVEL_NONE_DETECTED)
        self.assertEqual(k8s["evidence"]["repository_count"], 0)
        self.assertEqual(k8s["supporting_repositories"], [])

    # 3. Skill present in both
    async def test_03_skill_present_in_both(self):
        repos = self._build_rich_test_repos()
        profile = await developer_profile_service.synthesize_profile(
            username="testuser",
            resume_skills=["FastAPI"],
            repositories=repos,
        )
        skills_map = {s["name"]: s for s in profile["skills"]}
        self.assertIn("FastAPI", skills_map)
        fastapi = skills_map["FastAPI"]
        self.assertEqual(sorted(fastapi["sources"]), [SOURCE_GITHUB, SOURCE_RESUME])
        self.assertEqual(fastapi["evidence_status"], EVIDENCE_LEVEL_STRONG)

    # 4. Python/python normalization
    async def test_04_python_casing_normalization(self):
        repos = self._build_rich_test_repos()
        profile = await developer_profile_service.synthesize_profile(
            username="testuser",
            resume_skills=["python", "PYTHON", "Python"],
            repositories=repos,
        )
        python_entries = [s for s in profile["skills"] if s["name"] == "Python"]
        self.assertEqual(len(python_entries), 1)
        self.assertEqual(python_entries[0]["name"], "Python")
        self.assertEqual(python_entries[0]["skill"], "Python")

    # 5. React/reactjs normalization
    async def test_05_react_alias_normalization(self):
        repo = RepositoryAnalysisDetail(
            name="frontend-app",
            full_name="testuser/frontend-app",
            html_url="https://github.com/testuser/frontend-app",
            primary_language="TypeScript",
            topics=["reactjs"],
            skills=["React"],
            technologies=["React"],
            evidence=[
                EvidenceSourceSignal(
                    source_type=EVIDENCE_SOURCE_TOPIC,
                    technology="React",
                    strength=EVIDENCE_STRENGTH_MODERATE,
                )
            ],
        )
        profile = await developer_profile_service.synthesize_profile(
            username="testuser",
            resume_skills=["reactjs"],
            repositories=[repo],
        )
        react_entries = [s for s in profile["skills"] if s["name"] == "React"]
        self.assertEqual(len(react_entries), 1)
        self.assertEqual(react_entries[0]["name"], "React")
        self.assertIn(SOURCE_GITHUB, react_entries[0]["sources"])
        self.assertIn(SOURCE_RESUME, react_entries[0]["sources"])

    # 6. GitHub manifest evidence preservation
    async def test_06_manifest_evidence_preservation(self):
        repos = self._build_rich_test_repos()
        profile = await developer_profile_service.synthesize_profile(
            username="testuser",
            repositories=repos,
        )
        skills_map = {s["name"]: s for s in profile["skills"]}
        fastapi = skills_map["FastAPI"]
        self.assertIn("DEPENDENCY_MANIFEST", fastapi["evidence"]["signal_types"])

    # 7. GitHub evidence strength preservation
    async def test_07_evidence_strength_preservation(self):
        repos = self._build_rich_test_repos()
        profile = await developer_profile_service.synthesize_profile(
            username="testuser",
            repositories=repos,
        )
        skills_map = {s["name"]: s for s in profile["skills"]}
        # PostgreSQL has manifests in 2 repos -> STRONG
        self.assertEqual(skills_map["PostgreSQL"]["evidence"]["evidence_strength"], EVIDENCE_STRENGTH_STRONG)
        # Python in 2 repos -> STRONG
        self.assertEqual(skills_map["Python"]["evidence"]["evidence_strength"], EVIDENCE_STRENGTH_STRONG)

    # 8. Resume skills_section provenance
    # 9. Resume project_text provenance
    # 10. Resume experience_text provenance
    async def test_08_09_10_resume_provenance_tracking(self):
        resume_text = (
            "TECHNICAL SKILLS\n"
            "Python, Redis\n\n"
            "PROJECTS\n"
            "Chat Server\n"
            "Built websocket server with Node.js and Socket.io.\n\n"
            "EXPERIENCE\n"
            "Backend Intern\n"
            "Corp XYZ\n"
            "June 2024 - August 2024\n"
            "Automated ETL pipelines using Pandas and PostgreSQL.\n"
        )
        profile = await developer_profile_service.synthesize_profile(
            username="testuser",
            resume_text=resume_text,
            repositories=[],
        )
        skills_map = {s["name"]: s for s in profile["skills"]}

        # 8. skills_section provenance
        self.assertIn("skills_section", skills_map["Redis"]["evidence"]["resume_sources"])

        # 9. project_text provenance
        self.assertIn("project_text", skills_map["Node.js"]["evidence"]["resume_sources"])

        # 10. experience_text provenance
        self.assertIn("experience_text", skills_map["Pandas"]["evidence"]["resume_sources"])

    # 11. Multi-category skill
    async def test_11_multi_category_skills(self):
        profile = await developer_profile_service.synthesize_profile(
            username="testuser",
            resume_skills=["SQL", "TensorFlow", "Prisma"],
            repositories=[],
        )
        skills_map = {s["name"]: s for s in profile["skills"]}

        # SQL -> Programming Languages + Databases
        sql_cats = skills_map["SQL"]["categories"]
        self.assertIn("Programming Languages", sql_cats)
        self.assertIn("Databases", sql_cats)

        # TensorFlow -> Frameworks & Libraries + AI / Machine Learning
        tf_cats = skills_map["TensorFlow"]["categories"]
        self.assertIn("Frameworks & Libraries", tf_cats)
        self.assertIn("AI / Machine Learning", tf_cats)

        # Prisma -> Frameworks & Libraries + Databases
        prisma_cats = skills_map["Prisma"]["categories"]
        self.assertIn("Frameworks & Libraries", prisma_cats)
        self.assertIn("Databases", prisma_cats)

    # 12. NONE_DETECTED semantics
    async def test_12_none_detected_semantics(self):
        profile = await developer_profile_service.synthesize_profile(
            username="testuser",
            resume_skills=["Go"],
            repositories=[],
        )
        skills_map = {s["name"]: s for s in profile["skills"]}
        go = skills_map["Go"]
        self.assertEqual(go["evidence_status"], EVIDENCE_LEVEL_NONE_DETECTED)
        self.assertIsNone(go["evidence"]["evidence_strength"])
        self.assertEqual(go["evidence"]["repository_count"], 0)
        self.assertEqual(go["supporting_repositories"], [])
        self.assertEqual(go["sources"], [SOURCE_RESUME])

    # 13. Supporting repositories
    async def test_13_supporting_repositories(self):
        repos = self._build_rich_test_repos()
        profile = await developer_profile_service.synthesize_profile(
            username="testuser",
            repositories=repos,
        )
        skills_map = {s["name"]: s for s in profile["skills"]}
        python = skills_map["Python"]
        self.assertEqual(len(python["supporting_repositories"]), 2)
        repo_names = [r.name if hasattr(r, "name") else r["name"] for r in python["supporting_repositories"]]
        self.assertIn("backend-api", repo_names)
        self.assertIn("data-service", repo_names)

    # 14. Summary metric correctness
    async def test_14_summary_metrics_and_invariants(self):
        repos = self._build_rich_test_repos()
        profile = await developer_profile_service.synthesize_profile(
            username="testuser",
            resume_skills=["Python", "FastAPI", "Kubernetes", "Redis"],
            repositories=repos,
        )
        summary = profile["summary"]

        # Invariant: total = supported + unsupported
        self.assertEqual(
            summary["total_skills"],
            summary["supported_skill_count"] + summary["skills_without_github_evidence"],
        )
        # Invariant: total = github + resume - both
        self.assertEqual(
            summary["total_skills"],
            summary["github_skill_count"] + summary["resume_skill_count"] - summary["skills_from_both_sources"],
        )
        # Invariant: total = github_only + resume_only + both
        self.assertEqual(
            summary["total_skills"],
            summary["github_only_skills"] + summary["resume_only_skills"] + summary["skills_from_both_sources"],
        )

        self.assertEqual(summary["skills_from_both_sources"], 2)  # Python, FastAPI
        self.assertEqual(summary["resume_only_skills"], 2)  # Kubernetes, Redis
        self.assertEqual(summary["skills_without_github_evidence"], 2)

    # 15. Existing get_skill_names() compatibility
    async def test_15_get_skill_names_compatibility(self):
        profile = await developer_profile_service.synthesize_profile(
            username="testuser",
            resume_skills=["Python", "Docker", "SQL"],
            repositories=[],
        )
        response_model = DeveloperProfileResponse(**profile)
        names = response_model.get_skill_names()
        self.assertEqual(sorted(names), ["Docker", "Python", "SQL"])

        extracted = extract_developer_skills(response_model)
        self.assertEqual(sorted(extracted), ["Docker", "Python", "SQL"])

    # 16. Existing frontend field compatibility
    async def test_16_frontend_field_compatibility(self):
        repos = self._build_rich_test_repos()
        profile = await developer_profile_service.synthesize_profile(
            username="testuser",
            resume_skills=["Python", "SQL"],
            repositories=repos,
        )
        # Dashboard expects developer_id, github, resume, skills, summary, categorized_skills
        self.assertIn("developer_id", profile)
        self.assertIn("github", profile)
        self.assertIn("resume", profile)
        self.assertIn("skills", profile)
        self.assertIn("summary", profile)
        self.assertIn("categorized_skills", profile)

        # Dashboard / TechnologyList expects github.technologies_detected
        self.assertIn("technologies_detected", profile["github"])
        self.assertIn("username", profile["github"])
        self.assertIn("repositories_analyzed", profile["github"])

        # SkillEvidenceOverview expects for each skill:
        # skill, sources, evidence_status, supporting_repositories
        for s in profile["skills"]:
            self.assertIn("skill", s)
            self.assertIn("name", s)
            self.assertIn("sources", s)
            self.assertIn("evidence_status", s)
            self.assertIn("supporting_repositories", s)
            self.assertIn("categories", s)
            self.assertIn("evidence", s)


if __name__ == "__main__":
    unittest.main()
