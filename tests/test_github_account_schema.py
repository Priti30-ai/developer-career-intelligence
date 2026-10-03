"""
test_github_account_schema.py
-----------------------------
Unit tests for GitHub Account Intelligence schemas and data contracts.

Verifies:
1. Minimal valid account response creation
2. Multiple repositories coexisting independently
3. Repository-level technologies, skills, and evidence isolation
4. Aggregated profile coexistence with granular repository details
5. Optional fields handling and defaults
6. Validation errors on missing required fields
7. Evidence source signal attributes and strengths
8. Lookup helper methods
9. Compatibility with existing project schemas
"""

import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

# Ensure backend directory is in sys.path
backend_dir = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from pydantic import ValidationError

from app.schemas.github import GitHubProfileResponse
from app.schemas.github_account import (
    EVIDENCE_SOURCE_CONFIG,
    EVIDENCE_SOURCE_LANGUAGE,
    EVIDENCE_SOURCE_MANIFEST,
    EVIDENCE_SOURCE_STRUCTURE,
    EVIDENCE_SOURCE_TOPIC,
    EVIDENCE_STRENGTH_MODERATE,
    EVIDENCE_STRENGTH_STRONG,
    EVIDENCE_STRENGTH_WEAK,
    AccountMetadata,
    AggregatedAccountProfile,
    AggregatedLanguage,
    AggregatedSkill,
    AggregatedTechnology,
    EvidenceSourceSignal,
    EvidenceSummary,
    GitHubAccountAnalysisResponse,
    RepositoryAnalysisDetail,
    RepositoryCoverage,
)
from app.schemas.github_repository import GitHubRepositoryResponse
from app.schemas.repository_architecture import ArchitectureSignal
from app.schemas.skill_profile import SkillCategoryResponse, SkillResponse


class TestGitHubAccountSchemas(unittest.TestCase):
    """Unit tests for GitHub Account Intelligence Pydantic models."""

    def test_01_minimal_valid_account_response(self):
        """Minimal valid response can be created with only required fields."""
        account = AccountMetadata(login="testdeveloper")
        aggregated = AggregatedAccountProfile()
        response = GitHubAccountAnalysisResponse(
            account=account,
            repositories=[],
            aggregated_profile=aggregated,
        )

        self.assertEqual(response.account.login, "testdeveloper")
        self.assertEqual(len(response.repositories), 0)
        self.assertEqual(len(response.aggregated_profile.technologies), 0)
        self.assertEqual(response.account.public_repos, 0)
        self.assertEqual(response.account.followers, 0)

    def test_02_multiple_repositories_coexist_independently(self):
        """Multiple repositories must remain distinct and independently represented."""
        account = AccountMetadata(
            login="fullstack-dev",
            name="Full Stack Developer",
            avatar_url="https://github.com/images/avatar.png",
            html_url="https://github.com/fullstack-dev",
            public_repos=2,
        )

        repo_a = RepositoryAnalysisDetail(
            name="react-frontend",
            full_name="fullstack-dev/react-frontend",
            html_url="https://github.com/fullstack-dev/react-frontend",
            primary_language="TypeScript",
            languages=["TypeScript", "CSS", "HTML"],
            technologies=["React", "TypeScript", "Tailwind CSS"],
            manifest_files=["package.json", "tsconfig.json"],
            project_type="FRONTEND",
            skills=["React", "TypeScript", "Frontend Development"],
        )

        repo_b = RepositoryAnalysisDetail(
            name="fastapi-backend",
            full_name="fullstack-dev/fastapi-backend",
            html_url="https://github.com/fullstack-dev/fastapi-backend",
            primary_language="Python",
            languages=["Python", "SQL"],
            technologies=["FastAPI", "Python", "PostgreSQL"],
            manifest_files=["requirements.txt", "Dockerfile"],
            project_type="BACKEND",
            skills=["FastAPI", "Python", "REST API", "Database Design"],
        )

        response = GitHubAccountAnalysisResponse(
            account=account,
            repositories=[repo_a, repo_b],
            aggregated_profile=AggregatedAccountProfile(
                languages=[
                    AggregatedLanguage(name="TypeScript", repository_count=1),
                    AggregatedLanguage(name="Python", repository_count=1),
                ],
                technologies=[
                    AggregatedTechnology(name="React", repository_count=1, supporting_repositories=["react-frontend"]),
                    AggregatedTechnology(name="FastAPI", repository_count=1, supporting_repositories=["fastapi-backend"]),
                ],
            ),
        )

        self.assertEqual(len(response.repositories), 2)
        # Verify repository A integrity
        self.assertEqual(response.repositories[0].name, "react-frontend")
        self.assertEqual(response.repositories[0].primary_language, "TypeScript")
        self.assertIn("React", response.repositories[0].technologies)
        self.assertNotIn("FastAPI", response.repositories[0].technologies)

        # Verify repository B integrity
        self.assertEqual(response.repositories[1].name, "fastapi-backend")
        self.assertEqual(response.repositories[1].primary_language, "Python")
        self.assertIn("FastAPI", response.repositories[1].technologies)
        self.assertNotIn("React", response.repositories[1].technologies)

    def test_03_repository_level_evidence_remains_isolated(self):
        """Evidence signals attached to a repository belong strictly to that repository."""
        evidence_signal_a = EvidenceSourceSignal(
            source_type=EVIDENCE_SOURCE_MANIFEST,
            technology="React",
            path="package.json",
            strength=EVIDENCE_STRENGTH_STRONG,
            reason="Found react in package.json dependencies",
        )

        evidence_signal_b = EvidenceSourceSignal(
            source_type=EVIDENCE_SOURCE_MANIFEST,
            technology="FastAPI",
            path="requirements.txt",
            strength=EVIDENCE_STRENGTH_STRONG,
            reason="Found fastapi in requirements.txt",
        )

        repo_a = RepositoryAnalysisDetail(
            name="repo-a",
            full_name="dev/repo-a",
            html_url="https://github.com/dev/repo-a",
            evidence=[evidence_signal_a],
        )

        repo_b = RepositoryAnalysisDetail(
            name="repo-b",
            full_name="dev/repo-b",
            html_url="https://github.com/dev/repo-b",
            evidence=[evidence_signal_b],
        )

        self.assertEqual(len(repo_a.evidence), 1)
        self.assertEqual(repo_a.evidence[0].technology, "React")
        self.assertEqual(repo_a.evidence[0].path, "package.json")

        self.assertEqual(len(repo_b.evidence), 1)
        self.assertEqual(repo_b.evidence[0].technology, "FastAPI")
        self.assertEqual(repo_b.evidence[0].path, "requirements.txt")

    def test_04_aggregated_profile_coexists_with_repository_details(self):
        """Aggregated cross-repository stats coexist without altering individual repository objects."""
        repo = RepositoryAnalysisDetail(
            name="core-service",
            full_name="dev/core-service",
            html_url="https://github.com/dev/core-service",
            primary_language="Python",
            technologies=["Python", "Docker"],
            skills=["Python", "Containerization"],
        )

        aggregated = AggregatedAccountProfile(
            languages=[AggregatedLanguage(name="Python", repository_count=1, percentage=100.0)],
            technologies=[
                AggregatedTechnology(name="Python", repository_count=1, evidence_count=2, supporting_repositories=["core-service"]),
                AggregatedTechnology(name="Docker", repository_count=1, evidence_count=1, supporting_repositories=["core-service"]),
            ],
            skills=[
                AggregatedSkill(
                    name="Python",
                    category="Programming Languages",
                    repository_count=1,
                    evidence_count=2,
                    evidence_strength=EVIDENCE_STRENGTH_STRONG,
                    supporting_repositories=["core-service"],
                )
            ],
            repository_coverage=RepositoryCoverage(
                total_repositories_analyzed=1,
                original_repositories=1,
                active_repositories=1,
                successfully_analyzed_repositories=1,
            ),
            evidence_summary=EvidenceSummary(
                strong_evidence_count=1,
                total_evidence_signals=3,
                technologies_with_strong_evidence=1,
                technologies_with_evidence=2,
            ),
            total_unique_technologies=2,
            total_unique_skills=2,
        )

        response = GitHubAccountAnalysisResponse(
            account=AccountMetadata(login="dev"),
            repositories=[repo],
            aggregated_profile=aggregated,
        )

        self.assertEqual(len(response.repositories), 1)
        self.assertEqual(response.aggregated_profile.total_unique_technologies, 2)
        self.assertEqual(response.aggregated_profile.repository_coverage.total_repositories_analyzed, 1)
        self.assertEqual(response.aggregated_profile.evidence_summary.strong_evidence_count, 1)

    def test_05_optional_fields_can_be_null_or_omitted(self):
        """Optional GitHub fields default safely to None or standard zero/empty defaults."""
        account = AccountMetadata(login="minimal-user")
        self.assertIsNone(account.name)
        self.assertIsNone(account.bio)
        self.assertIsNone(account.company)
        self.assertIsNone(account.location)
        self.assertIsNone(account.created_at)
        self.assertEqual(account.public_repos, 0)
        self.assertEqual(account.followers, 0)

        repo = RepositoryAnalysisDetail(
            name="minimal-repo",
            full_name="minimal-user/minimal-repo",
            html_url="https://github.com/minimal-user/minimal-repo",
        )
        self.assertIsNone(repo.description)
        self.assertEqual(repo.default_branch, "main")
        self.assertFalse(repo.is_fork)
        self.assertFalse(repo.is_archived)
        self.assertFalse(repo.is_empty)
        self.assertEqual(repo.stargazers_count, 0)
        self.assertEqual(len(repo.languages), 0)
        self.assertEqual(len(repo.evidence), 0)
        self.assertEqual(repo.analysis_status, "SUCCESS")

    def test_06_invalid_required_structures_rejected(self):
        """Missing mandatory attributes trigger Pydantic ValidationError."""
        # Missing login in AccountMetadata
        with self.assertRaises(ValidationError):
            AccountMetadata()

        # Missing name or html_url in RepositoryAnalysisDetail
        with self.assertRaises(ValidationError):
            RepositoryAnalysisDetail(name="repo")

        # Missing source_type or technology in EvidenceSourceSignal
        with self.assertRaises(ValidationError):
            EvidenceSourceSignal(technology="Python")

    def test_07_evidence_source_and_strength_constants(self):
        """Constants for evidence sources and strengths are accessible and well-defined."""
        self.assertEqual(EVIDENCE_SOURCE_MANIFEST, "DEPENDENCY_MANIFEST")
        self.assertEqual(EVIDENCE_SOURCE_LANGUAGE, "SOURCE_LANGUAGE")
        self.assertEqual(EVIDENCE_SOURCE_TOPIC, "REPOSITORY_TOPIC")
        self.assertEqual(EVIDENCE_SOURCE_STRUCTURE, "PROJECT_STRUCTURE")
        self.assertEqual(EVIDENCE_SOURCE_CONFIG, "CONFIGURATION")
        self.assertEqual(EVIDENCE_STRENGTH_STRONG, "STRONG")
        self.assertEqual(EVIDENCE_STRENGTH_MODERATE, "MODERATE")
        self.assertEqual(EVIDENCE_STRENGTH_WEAK, "WEAK")

    def test_08_lookup_helper_methods(self):
        """Response helper methods get_repository, get_technology_names, and get_skill_names work as expected."""
        repo1 = RepositoryAnalysisDetail(
            name="frontend-app",
            full_name="dev/frontend-app",
            html_url="https://github.com/dev/frontend-app",
        )
        repo2 = RepositoryAnalysisDetail(
            name="backend-api",
            full_name="dev/backend-api",
            html_url="https://github.com/dev/backend-api",
        )

        response = GitHubAccountAnalysisResponse(
            account=AccountMetadata(login="dev"),
            repositories=[repo1, repo2],
            aggregated_profile=AggregatedAccountProfile(
                technologies=[
                    AggregatedTechnology(name="React", repository_count=1),
                    AggregatedTechnology(name="FastAPI", repository_count=1),
                ],
                skills=[
                    AggregatedSkill(name="React", category="Web", repository_count=1),
                    AggregatedSkill(name="FastAPI", category="Web", repository_count=1),
                ],
            ),
        )

        # Lookup by repo name (case-insensitive)
        found = response.get_repository("frontend-app")
        self.assertIsNotNone(found)
        self.assertEqual(found.name, "frontend-app")

        # Lookup by full_name
        found_full = response.get_repository("dev/backend-api")
        self.assertIsNotNone(found_full)
        self.assertEqual(found_full.name, "backend-api")

        # Unknown repo returns None
        self.assertIsNone(response.get_repository("nonexistent"))

        # Technology and skill names extraction
        self.assertEqual(response.get_technology_names(), ["React", "FastAPI"])
        self.assertEqual(response.get_skill_names(), ["React", "FastAPI"])

    def test_09_existing_schemas_compatibility(self):
        """Existing project schemas can be created alongside new account schemas."""
        old_profile = GitHubProfileResponse(login="octocat", public_repos=5)
        old_repo = GitHubRepositoryResponse(
            name="Hello-World",
            full_name="octocat/Hello-World",
            html_url="https://github.com/octocat/Hello-World",
        )
        arch_signal = ArchitectureSignal(type="BACKEND", description="API routes", evidence=["app/api"])
        skill_resp = SkillResponse(name="Python", repository_count=3)
        cat_resp = SkillCategoryResponse(category="Languages", skills=[skill_resp])

        self.assertEqual(old_profile.login, "octocat")
        self.assertEqual(old_repo.name, "Hello-World")
        self.assertEqual(arch_signal.type, "BACKEND")
        self.assertEqual(cat_resp.category, "Languages")


if __name__ == "__main__":
    unittest.main()
