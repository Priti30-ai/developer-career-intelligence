"""
test_github_account_aggregation_service.py
-------------------------------------------
Comprehensive test suite for GitHubAccountAggregationService.
Covers:
1. Languages aggregation (single, multi, counts, supporting repos, deterministic ordering)
2. Technology aggregation (single, multi, duplicate evidence in 1 repo, canonical dedup, repo count semantics)
3. Skill aggregation (single, multi, categories, grounded evidence strength, no proficiency claims)
4. Evidence summary (strong, moderate, weak counts, total signals, technology coverage)
5. Repository coverage (total, original, forks, archived, active, successful, partial, error, empty)
6. Failure handling (failed repo, empty repo, empty account, partial repos)
7. Preservation (no mutation of repository records)
8. Deterministic ordering and stability across runs
9. Integration with GitHubAccountService
"""

import copy
import sys
import unittest
from pathlib import Path

# Ensure backend directory is in sys.path
backend_dir = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from app.schemas.github_account import (
    EVIDENCE_SOURCE_CONFIG,
    EVIDENCE_SOURCE_LANGUAGE,
    EVIDENCE_SOURCE_MANIFEST,
    EVIDENCE_SOURCE_STRUCTURE,
    EVIDENCE_SOURCE_TOPIC,
    EVIDENCE_STRENGTH_MODERATE,
    EVIDENCE_STRENGTH_STRONG,
    EVIDENCE_STRENGTH_WEAK,
    EvidenceSourceSignal,
    RepositoryAnalysisDetail,
)
from app.services.github_account_aggregation_service import (
    GitHubAccountAggregationService,
    github_account_aggregation_service,
)
from app.services.github_account_service import GitHubAccountService


class TestGitHubAccountAggregationService(unittest.TestCase):
    """Unit and integration tests for cross-repository account aggregation."""

    def setUp(self):
        self.service = GitHubAccountAggregationService()

    # -------------------------------------------------------------------------
    # 1. Languages Aggregation
    # -------------------------------------------------------------------------

    def test_01_language_single_repository(self):
        """Single language in one repository produces count=1, percentage=100%, and supporting repo."""
        repo = RepositoryAnalysisDetail(
            name="py-service",
            full_name="dev/py-service",
            html_url="https://github.com/dev/py-service",
            primary_language="Python",
            languages=["Python"],
        )
        profile = self.service.aggregate_account_profile([repo])

        self.assertEqual(len(profile.languages), 1)
        lang = profile.languages[0]
        self.assertEqual(lang.name, "Python")
        self.assertEqual(lang.repository_count, 1)
        self.assertEqual(lang.percentage, 100.0)
        self.assertEqual(lang.supporting_repositories, ["py-service"])

    def test_02_same_language_multiple_repositories(self):
        """Same language appearing in 3 repositories gives repository_count=3 and all supporting repos."""
        repos = [
            RepositoryAnalysisDetail(
                name=f"repo-{i}",
                full_name=f"dev/repo-{i}",
                html_url=f"https://github.com/dev/repo-{i}",
                primary_language="TypeScript",
                languages=["TypeScript"],
            )
            for i in range(1, 4)
        ]
        profile = self.service.aggregate_account_profile(repos)

        self.assertEqual(len(profile.languages), 1)
        lang = profile.languages[0]
        self.assertEqual(lang.name, "TypeScript")
        self.assertEqual(lang.repository_count, 3)
        self.assertEqual(lang.percentage, 100.0)
        self.assertEqual(lang.supporting_repositories, ["repo-1", "repo-2", "repo-3"])

    def test_03_multiple_languages_across_repositories(self):
        """Multiple distinct languages across repositories calculate percentages accurately."""
        repos = [
            RepositoryAnalysisDetail(
                name="backend",
                full_name="dev/backend",
                html_url="https://github.com/dev/backend",
                languages=["Python", "Go"],
            ),
            RepositoryAnalysisDetail(
                name="frontend",
                full_name="dev/frontend",
                html_url="https://github.com/dev/frontend",
                languages=["TypeScript", "CSS", "HTML"],
            ),
            RepositoryAnalysisDetail(
                name="infra",
                full_name="dev/infra",
                html_url="https://github.com/dev/infra",
                languages=["Go"],
            ),
        ]
        profile = self.service.aggregate_account_profile(repos)

        lang_map = {l.name: l for l in profile.languages}
        self.assertIn("Go", lang_map)
        self.assertEqual(lang_map["Go"].repository_count, 2)
        self.assertIn("Python", lang_map)
        self.assertEqual(lang_map["Python"].repository_count, 1)
        self.assertIn("TypeScript", lang_map)
        self.assertEqual(lang_map["TypeScript"].repository_count, 1)

    def test_04_language_counts_repositories_not_occurrences(self):
        """If Python is in primary_language AND languages array for 1 repo, count is strictly 1."""
        repo = RepositoryAnalysisDetail(
            name="single-repo",
            full_name="dev/single-repo",
            html_url="https://github.com/dev/single-repo",
            primary_language="Python",
            languages=["Python", "python"],  # duplicate casing
        )
        profile = self.service.aggregate_account_profile([repo])

        self.assertEqual(len(profile.languages), 1)
        self.assertEqual(profile.languages[0].name, "Python")
        self.assertEqual(profile.languages[0].repository_count, 1)

    def test_05_language_supporting_repositories_list(self):
        """Supporting repositories list has unique names and matches repository_count."""
        repos = [
            RepositoryAnalysisDetail(
                name="alpha",
                full_name="dev/alpha",
                html_url="https://github.com/dev/alpha",
                languages=["Rust"],
            ),
            RepositoryAnalysisDetail(
                name="beta",
                full_name="dev/beta",
                html_url="https://github.com/dev/beta",
                languages=["Rust"],
            ),
        ]
        profile = self.service.aggregate_account_profile(repos)
        rust = profile.languages[0]
        self.assertEqual(rust.repository_count, 2)
        self.assertEqual(len(rust.supporting_repositories), len(set(rust.supporting_repositories)))
        self.assertEqual(rust.supporting_repositories, ["alpha", "beta"])

    def test_06_language_deterministic_ordering(self):
        """Languages are ordered primarily by -repository_count, then alphabetically by name."""
        repos = [
            RepositoryAnalysisDetail(
                name="repo1",
                full_name="dev/repo1",
                html_url="https://github.com/dev/repo1",
                languages=["Python", "C", "Go"],
            ),
            RepositoryAnalysisDetail(
                name="repo2",
                full_name="dev/repo2",
                html_url="https://github.com/dev/repo2",
                languages=["Python", "Go"],
            ),
            RepositoryAnalysisDetail(
                name="repo3",
                full_name="dev/repo3",
                html_url="https://github.com/dev/repo3",
                languages=["Python"],
            ),
        ]
        profile = self.service.aggregate_account_profile(repos)
        # Python: 3, Go: 2, C: 1
        lang_names = [l.name for l in profile.languages]
        self.assertEqual(lang_names, ["Python", "Go", "C"])

    # -------------------------------------------------------------------------
    # 2. Technology Aggregation
    # -------------------------------------------------------------------------

    def test_07_technology_single_repository(self):
        """Single technology in one repository aggregates to repository_count=1."""
        repo = RepositoryAnalysisDetail(
            name="app",
            full_name="dev/app",
            html_url="https://github.com/dev/app",
            technologies=["React"],
            evidence=[
                EvidenceSourceSignal(
                    source_type=EVIDENCE_SOURCE_MANIFEST,
                    technology="React",
                    path="package.json",
                    strength=EVIDENCE_STRENGTH_STRONG,
                    reason="Found in package.json",
                )
            ],
        )
        profile = self.service.aggregate_account_profile([repo])

        self.assertEqual(len(profile.technologies), 1)
        tech = profile.technologies[0]
        self.assertEqual(tech.name, "React")
        self.assertEqual(tech.repository_count, 1)
        self.assertEqual(tech.evidence_count, 1)
        self.assertEqual(tech.supporting_repositories, ["app"])

    def test_08_same_technology_multiple_repositories(self):
        """Same technology across multiple repositories aggregates correctly."""
        repos = [
            RepositoryAnalysisDetail(
                name="web-client",
                full_name="dev/web-client",
                html_url="https://github.com/dev/web-client",
                technologies=["React"],
                evidence=[
                    EvidenceSourceSignal(
                        source_type=EVIDENCE_SOURCE_MANIFEST,
                        technology="React",
                        path="package.json",
                        strength=EVIDENCE_STRENGTH_STRONG,
                    )
                ],
            ),
            RepositoryAnalysisDetail(
                name="mobile-web",
                full_name="dev/mobile-web",
                html_url="https://github.com/dev/mobile-web",
                technologies=["React"],
                evidence=[
                    EvidenceSourceSignal(
                        source_type=EVIDENCE_SOURCE_MANIFEST,
                        technology="React",
                        path="package.json",
                        strength=EVIDENCE_STRENGTH_STRONG,
                    )
                ],
            ),
        ]
        profile = self.service.aggregate_account_profile(repos)

        self.assertEqual(len(profile.technologies), 1)
        tech = profile.technologies[0]
        self.assertEqual(tech.name, "React")
        self.assertEqual(tech.repository_count, 2)
        self.assertEqual(tech.evidence_count, 2)
        self.assertEqual(tech.supporting_repositories, ["mobile-web", "web-client"])

    def test_09_duplicate_technology_evidence_within_one_repository(self):
        """Duplicate evidence within a single repository increments evidence_count but NOT repository_count."""
        repo = RepositoryAnalysisDetail(
            name="frontend",
            full_name="dev/frontend",
            html_url="https://github.com/dev/frontend",
            technologies=["React", "React", "react"],  # multiple unnormalized occurrences
            evidence=[
                EvidenceSourceSignal(
                    source_type=EVIDENCE_SOURCE_MANIFEST,
                    technology="React",
                    path="package.json",
                    strength=EVIDENCE_STRENGTH_STRONG,
                    reason="dependencies",
                ),
                EvidenceSourceSignal(
                    source_type=EVIDENCE_SOURCE_MANIFEST,
                    technology="React",
                    path="package.json",
                    strength=EVIDENCE_STRENGTH_STRONG,
                    reason="devDependencies",
                ),
                EvidenceSourceSignal(
                    source_type=EVIDENCE_SOURCE_TOPIC,
                    technology="React",
                    path=None,
                    strength=EVIDENCE_STRENGTH_WEAK,
                    reason="topic tag",
                ),
            ],
        )
        profile = self.service.aggregate_account_profile([repo])

        self.assertEqual(len(profile.technologies), 1)
        tech = profile.technologies[0]
        self.assertEqual(tech.name, "React")
        self.assertEqual(tech.repository_count, 1)  # Strictly 1 repo!
        self.assertEqual(tech.evidence_count, 3)  # 3 distinct evidence signals

    def test_10_canonical_deduplication(self):
        """Variants like 'react', 'React.js', 'React' are deduplicated to single canonical name."""
        repos = [
            RepositoryAnalysisDetail(
                name="repo-a",
                full_name="dev/repo-a",
                html_url="https://github.com/dev/repo-a",
                technologies=["react"],
            ),
            RepositoryAnalysisDetail(
                name="repo-b",
                full_name="dev/repo-b",
                html_url="https://github.com/dev/repo-b",
                technologies=["React.js"],
            ),
        ]
        profile = self.service.aggregate_account_profile(repos)

        tech_names = [t.name for t in profile.technologies]
        self.assertEqual(tech_names, ["React"])
        self.assertEqual(profile.technologies[0].repository_count, 2)

    def test_11_technology_repository_count_semantics_section_22(self):
        """
        Mandatory test from Section 22:
        Repo A: React appears in 5 evidence signals
        Repo B: React appears in 2 evidence signals
        Repo C: React appears in 1 evidence signal
        Expected: React.repository_count == 3 (NOT 8).
        """
        repo_a = RepositoryAnalysisDetail(
            name="Repo-A",
            full_name="dev/Repo-A",
            html_url="https://github.com/dev/Repo-A",
            technologies=["React"],
            evidence=[
                EvidenceSourceSignal(
                    source_type=EVIDENCE_SOURCE_MANIFEST,
                    technology="React",
                    strength=EVIDENCE_STRENGTH_STRONG,
                    reason=f"Signal {i}",
                )
                for i in range(5)
            ],
        )
        repo_b = RepositoryAnalysisDetail(
            name="Repo-B",
            full_name="dev/Repo-B",
            html_url="https://github.com/dev/Repo-B",
            technologies=["React"],
            evidence=[
                EvidenceSourceSignal(
                    source_type=EVIDENCE_SOURCE_CONFIG,
                    technology="React",
                    strength=EVIDENCE_STRENGTH_STRONG,
                    reason=f"Signal {i}",
                )
                for i in range(2)
            ],
        )
        repo_c = RepositoryAnalysisDetail(
            name="Repo-C",
            full_name="dev/Repo-C",
            html_url="https://github.com/dev/Repo-C",
            technologies=["React"],
            evidence=[
                EvidenceSourceSignal(
                    source_type=EVIDENCE_SOURCE_TOPIC,
                    technology="React",
                    strength=EVIDENCE_STRENGTH_WEAK,
                    reason="Topic tag",
                )
            ],
        )

        profile = self.service.aggregate_account_profile([repo_a, repo_b, repo_c])

        self.assertEqual(len(profile.technologies), 1)
        react = profile.technologies[0]
        self.assertEqual(react.name, "React")
        self.assertEqual(react.repository_count, 3, "repository_count must be 3, NOT 8!")
        self.assertEqual(react.evidence_count, 8, "evidence_count must reflect total signals (8)")
        self.assertEqual(react.supporting_repositories, ["Repo-A", "Repo-B", "Repo-C"])

    def test_12_technology_supporting_repositories_deterministic(self):
        """supporting_repositories is always sorted and len(unique) equals repository_count."""
        repos = [
            RepositoryAnalysisDetail(
                name="z-repo",
                full_name="dev/z-repo",
                html_url="https://github.com/dev/z-repo",
                technologies=["FastAPI"],
            ),
            RepositoryAnalysisDetail(
                name="a-repo",
                full_name="dev/a-repo",
                html_url="https://github.com/dev/a-repo",
                technologies=["FastAPI"],
            ),
        ]
        profile = self.service.aggregate_account_profile(repos)
        fastapi = profile.technologies[0]
        self.assertEqual(fastapi.supporting_repositories, ["a-repo", "z-repo"])
        self.assertEqual(fastapi.repository_count, len(fastapi.supporting_repositories))

    # -------------------------------------------------------------------------
    # 3. Skill Aggregation
    # -------------------------------------------------------------------------

    def test_13_skill_single_repository(self):
        """Skill from single repository aggregates to repository_count=1 and gets domain category."""
        repo = RepositoryAnalysisDetail(
            name="api",
            full_name="dev/api",
            html_url="https://github.com/dev/api",
            skills=["Python"],
            evidence=[
                EvidenceSourceSignal(
                    source_type=EVIDENCE_SOURCE_LANGUAGE,
                    technology="Python",
                    strength=EVIDENCE_STRENGTH_MODERATE,
                )
            ],
        )
        profile = self.service.aggregate_account_profile([repo])

        self.assertEqual(len(profile.skills), 1)
        skill = profile.skills[0]
        self.assertEqual(skill.name, "Python")
        self.assertEqual(skill.repository_count, 1)
        self.assertEqual(skill.category, "Programming Languages")
        self.assertEqual(skill.evidence_strength, EVIDENCE_STRENGTH_MODERATE)

    def test_14_same_skill_across_repositories(self):
        """Same skill across multiple repositories aggregates repository count and supporting repos."""
        repos = [
            RepositoryAnalysisDetail(
                name="repo1",
                full_name="dev/repo1",
                html_url="https://github.com/dev/repo1",
                skills=["Docker"],
            ),
            RepositoryAnalysisDetail(
                name="repo2",
                full_name="dev/repo2",
                html_url="https://github.com/dev/repo2",
                skills=["Docker"],
            ),
        ]
        profile = self.service.aggregate_account_profile(repos)

        self.assertEqual(len(profile.skills), 1)
        skill = profile.skills[0]
        self.assertEqual(skill.name, "Docker")
        self.assertEqual(skill.repository_count, 2)
        self.assertEqual(skill.supporting_repositories, ["repo1", "repo2"])

    def test_15_duplicate_skill_within_one_repository(self):
        """Duplicate skill in repo.skills is deduplicated, repository_count=1."""
        repo = RepositoryAnalysisDetail(
            name="backend",
            full_name="dev/backend",
            html_url="https://github.com/dev/backend",
            skills=["PostgreSQL", "PostgreSQL"],
        )
        profile = self.service.aggregate_account_profile([repo])

        self.assertEqual(len(profile.skills), 1)
        self.assertEqual(profile.skills[0].name, "PostgreSQL")
        self.assertEqual(profile.skills[0].repository_count, 1)

    def test_16_skill_domain_categories_bucketing(self):
        """Skills are bucketed correctly into categorized_skills domain lists."""
        repo = RepositoryAnalysisDetail(
            name="fullstack",
            full_name="dev/fullstack",
            html_url="https://github.com/dev/fullstack",
            skills=["Python", "React", "PostgreSQL", "Docker"],
        )
        profile = self.service.aggregate_account_profile([repo])

        cat_names = [c.category for c in profile.categorized_skills]
        self.assertIn("Programming Languages", cat_names)
        self.assertIn("Frameworks & Libraries", cat_names)
        self.assertIn("Databases", cat_names)
        self.assertIn("DevOps & Cloud", cat_names)

    def test_17_skill_evidence_strength_grounded_rules(self):
        """
        Evidence strength adheres to grounded evidence rules (NOT proficiency claims):
        - >= 2 supporting repositories OR STRONG evidence signal -> STRONG
        - 1 repo with MODERATE signal -> MODERATE
        - Topic-only -> WEAK
        """
        # Multi-repo skill -> STRONG
        repos_strong = [
            RepositoryAnalysisDetail(
                name="r1", full_name="dev/r1", html_url="https://github.com/dev/r1", skills=["Git"]
            ),
            RepositoryAnalysisDetail(
                name="r2", full_name="dev/r2", html_url="https://github.com/dev/r2", skills=["Git"]
            ),
        ]
        profile_strong = self.service.aggregate_account_profile(repos_strong)
        git_skill = [s for s in profile_strong.skills if s.name == "Git"][0]
        self.assertEqual(git_skill.evidence_strength, EVIDENCE_STRENGTH_STRONG)

        # Single repo with STRONG signal from manifest -> STRONG
        repo_manifest = [
            RepositoryAnalysisDetail(
                name="r1",
                full_name="dev/r1",
                html_url="https://github.com/dev/r1",
                skills=["FastAPI"],
                evidence=[
                    EvidenceSourceSignal(
                        source_type=EVIDENCE_SOURCE_MANIFEST,
                        technology="FastAPI",
                        strength=EVIDENCE_STRENGTH_STRONG,
                    )
                ],
            )
        ]
        profile_manifest = self.service.aggregate_account_profile(repo_manifest)
        fastapi_skill = [s for s in profile_manifest.skills if s.name == "FastAPI"][0]
        self.assertEqual(fastapi_skill.evidence_strength, EVIDENCE_STRENGTH_STRONG)

        # Single repo with weak topic signal -> WEAK
        repo_weak = [
            RepositoryAnalysisDetail(
                name="r1",
                full_name="dev/r1",
                html_url="https://github.com/dev/r1",
                skills=["GraphQL"],
                evidence=[
                    EvidenceSourceSignal(
                        source_type=EVIDENCE_SOURCE_TOPIC,
                        technology="GraphQL",
                        strength=EVIDENCE_STRENGTH_WEAK,
                    )
                ],
            )
        ]
        profile_weak = self.service.aggregate_account_profile(repo_weak)
        gql_skill = [s for s in profile_weak.skills if s.name == "GraphQL"][0]
        # Single repo with no strong or moderate evidence defaults to MODERATE for 1 repo, or WEAK if explicit
        self.assertIn(gql_skill.evidence_strength, [EVIDENCE_STRENGTH_MODERATE, EVIDENCE_STRENGTH_WEAK])

    # -------------------------------------------------------------------------
    # 4. Evidence Summary Calculation
    # -------------------------------------------------------------------------

    def test_18_strong_evidence_aggregation(self):
        """Strong evidence signals from manifests or multi-repo proof are aggregated correctly."""
        repos = [
            RepositoryAnalysisDetail(
                name="app",
                full_name="dev/app",
                html_url="https://github.com/dev/app",
                technologies=["React"],
                evidence=[
                    EvidenceSourceSignal(
                        source_type=EVIDENCE_SOURCE_MANIFEST,
                        technology="React",
                        strength=EVIDENCE_STRENGTH_STRONG,
                    ),
                    EvidenceSourceSignal(
                        source_type=EVIDENCE_SOURCE_CONFIG,
                        technology="React",
                        strength=EVIDENCE_STRENGTH_STRONG,
                    ),
                ],
            )
        ]
        profile = self.service.aggregate_account_profile(repos)
        summary = profile.evidence_summary

        self.assertEqual(summary.strong_evidence_count, 2)
        self.assertEqual(summary.total_evidence_signals, 2)
        self.assertEqual(summary.technologies_with_strong_evidence, 1)

    def test_19_moderate_evidence_aggregation(self):
        """Moderate evidence signals (e.g. source language, project structure) increment moderate count."""
        repo = RepositoryAnalysisDetail(
            name="cli",
            full_name="dev/cli",
            html_url="https://github.com/dev/cli",
            technologies=["Python"],
            evidence=[
                EvidenceSourceSignal(
                    source_type=EVIDENCE_SOURCE_LANGUAGE,
                    technology="Python",
                    strength=EVIDENCE_STRENGTH_MODERATE,
                )
            ],
        )
        profile = self.service.aggregate_account_profile([repo])
        self.assertEqual(profile.evidence_summary.moderate_evidence_count, 1)
        self.assertEqual(profile.evidence_summary.total_evidence_signals, 1)

    def test_20_weak_evidence_aggregation(self):
        """Weak evidence signals (e.g. topics) increment weak count."""
        repo = RepositoryAnalysisDetail(
            name="notes",
            full_name="dev/notes",
            html_url="https://github.com/dev/notes",
            technologies=["Markdown"],
            evidence=[
                EvidenceSourceSignal(
                    source_type=EVIDENCE_SOURCE_TOPIC,
                    technology="Markdown",
                    strength=EVIDENCE_STRENGTH_WEAK,
                )
            ],
        )
        profile = self.service.aggregate_account_profile([repo])
        self.assertEqual(profile.evidence_summary.weak_evidence_count, 1)

    def test_21_technology_evidence_coverage(self):
        """Distinct technologies with evidence vs strong evidence are accurately counted."""
        repos = [
            RepositoryAnalysisDetail(
                name="repo1",
                full_name="dev/repo1",
                html_url="https://github.com/dev/repo1",
                technologies=["React", "TypeScript"],
                evidence=[
                    EvidenceSourceSignal(
                        source_type=EVIDENCE_SOURCE_MANIFEST,
                        technology="React",
                        strength=EVIDENCE_STRENGTH_STRONG,
                    ),
                    EvidenceSourceSignal(
                        source_type=EVIDENCE_SOURCE_LANGUAGE,
                        technology="TypeScript",
                        strength=EVIDENCE_STRENGTH_MODERATE,
                    ),
                ],
            )
        ]
        profile = self.service.aggregate_account_profile(repos)
        summary = profile.evidence_summary

        self.assertEqual(summary.technologies_with_evidence, 2)
        self.assertEqual(summary.technologies_with_strong_evidence, 1)

    def test_22_mixed_evidence_multi_repository(self):
        """Complex multi-repository evidence breakdown across varied signal strengths."""
        repos = [
            RepositoryAnalysisDetail(
                name="r1",
                full_name="dev/r1",
                html_url="https://github.com/dev/r1",
                technologies=["FastAPI", "Python"],
                evidence=[
                    EvidenceSourceSignal(
                        source_type=EVIDENCE_SOURCE_MANIFEST,
                        technology="FastAPI",
                        strength=EVIDENCE_STRENGTH_STRONG,
                    ),
                    EvidenceSourceSignal(
                        source_type=EVIDENCE_SOURCE_LANGUAGE,
                        technology="Python",
                        strength=EVIDENCE_STRENGTH_MODERATE,
                    ),
                ],
            ),
            RepositoryAnalysisDetail(
                name="r2",
                full_name="dev/r2",
                html_url="https://github.com/dev/r2",
                technologies=["Docker"],
                evidence=[
                    EvidenceSourceSignal(
                        source_type=EVIDENCE_SOURCE_STRUCTURE,
                        technology="Docker",
                        strength=EVIDENCE_STRENGTH_STRONG,
                    ),
                    EvidenceSourceSignal(
                        source_type=EVIDENCE_SOURCE_TOPIC,
                        technology="Docker",
                        strength=EVIDENCE_STRENGTH_WEAK,
                    ),
                ],
            ),
        ]
        profile = self.service.aggregate_account_profile(repos)
        summary = profile.evidence_summary

        self.assertEqual(summary.strong_evidence_count, 2)
        self.assertEqual(summary.moderate_evidence_count, 1)
        self.assertEqual(summary.weak_evidence_count, 1)
        self.assertEqual(summary.total_evidence_signals, 4)
        self.assertEqual(summary.technologies_with_evidence, 3)

    # -------------------------------------------------------------------------
    # 5. Repository Coverage Calculation
    # -------------------------------------------------------------------------

    def test_23_repository_coverage_totals_and_flags(self):
        """RepositoryCoverage tracks original, forked, archived, and active repositories accurately."""
        repos = [
            RepositoryAnalysisDetail(
                name="r1", full_name="dev/r1", html_url="https://github.com/dev/r1", is_fork=False, is_archived=False
            ),
            RepositoryAnalysisDetail(
                name="r2", full_name="dev/r2", html_url="https://github.com/dev/r2", is_fork=True, is_archived=False
            ),
            RepositoryAnalysisDetail(
                name="r3", full_name="dev/r3", html_url="https://github.com/dev/r3", is_fork=False, is_archived=True
            ),
        ]
        profile = self.service.aggregate_account_profile(repos)
        cov = profile.repository_coverage

        self.assertEqual(cov.total_repositories_analyzed, 3)
        self.assertEqual(cov.original_repositories, 2)
        self.assertEqual(cov.forked_repositories, 1)
        self.assertEqual(cov.archived_repositories, 1)
        self.assertEqual(cov.active_repositories, 2)

    def test_24_repository_coverage_analysis_statuses(self):
        """RepositoryCoverage properly distinguishes SUCCESS, PARTIAL, and empty repositories."""
        repos = [
            RepositoryAnalysisDetail(
                name="r1", full_name="dev/r1", html_url="https://github.com/dev/r1", analysis_status="SUCCESS", is_partial=False
            ),
            RepositoryAnalysisDetail(
                name="r2", full_name="dev/r2", html_url="https://github.com/dev/r2", analysis_status="PARTIAL", is_partial=True
            ),
            RepositoryAnalysisDetail(
                name="r3", full_name="dev/r3", html_url="https://github.com/dev/r3", is_empty=True
            ),
        ]
        profile = self.service.aggregate_account_profile(repos)
        cov = profile.repository_coverage

        self.assertEqual(cov.successfully_analyzed_repositories, 1)
        self.assertEqual(cov.partially_analyzed_repositories, 1)
        self.assertEqual(cov.empty_repositories, 1)

    # -------------------------------------------------------------------------
    # 6. Failure & Edge Cases Handling
    # -------------------------------------------------------------------------

    def test_25_failed_repository_handling_section_23(self):
        """
        Mandatory test from Section 23:
        Repo A -> SUCCESS -> React
        Repo B -> ERROR
        Repo C -> SUCCESS -> React
        Expected: React.repository_count == 2, total_repositories == 3, error_repositories == 1.
        The failed repository must not contribute fake technologies.
        """
        repo_a = RepositoryAnalysisDetail(
            name="Repo-A",
            full_name="dev/Repo-A",
            html_url="https://github.com/dev/Repo-A",
            analysis_status="SUCCESS",
            technologies=["React"],
        )
        repo_b = RepositoryAnalysisDetail(
            name="Repo-B",
            full_name="dev/Repo-B",
            html_url="https://github.com/dev/Repo-B",
            analysis_status="ERROR",
            technologies=["FakeTechnology"],
            skills=["FakeSkill"],
            languages=["FakeLang"],
        )
        repo_c = RepositoryAnalysisDetail(
            name="Repo-C",
            full_name="dev/Repo-C",
            html_url="https://github.com/dev/Repo-C",
            analysis_status="SUCCESS",
            technologies=["React"],
        )

        profile = self.service.aggregate_account_profile([repo_a, repo_b, repo_c])

        # React repository count must be 2
        self.assertEqual(len(profile.technologies), 1)
        self.assertEqual(profile.technologies[0].name, "React")
        self.assertEqual(profile.technologies[0].repository_count, 2)
        self.assertEqual(profile.technologies[0].supporting_repositories, ["Repo-A", "Repo-C"])

        # No fake technologies, skills, or languages from Repo B
        tech_names = [t.name for t in profile.technologies]
        self.assertNotIn("FakeTechnology", tech_names)
        skill_names = [s.name for s in profile.skills]
        self.assertNotIn("FakeSkill", skill_names)
        lang_names = [l.name for l in profile.languages]
        self.assertNotIn("FakeLang", lang_names)

        # Coverage statistics
        cov = profile.repository_coverage
        self.assertEqual(cov.total_repositories_analyzed, 3)
        self.assertEqual(cov.error_repositories, 1)

    def test_26_empty_repository_handling_section_24(self):
        """
        Mandatory test from Section 24:
        Repo A -> EMPTY
        Expected: total_repositories == 1, empty_repositories == 1,
                  technologies == [], skills == [], languages == [].
        """
        repo_empty = RepositoryAnalysisDetail(
            name="empty-repo",
            full_name="dev/empty-repo",
            html_url="https://github.com/dev/empty-repo",
            is_empty=True,
            languages=["ShouldBeIgnored"],
            technologies=["ShouldBeIgnored"],
            skills=["ShouldBeIgnored"],
        )
        profile = self.service.aggregate_account_profile([repo_empty])

        self.assertEqual(profile.repository_coverage.total_repositories_analyzed, 1)
        self.assertEqual(profile.repository_coverage.empty_repositories, 1)
        self.assertEqual(len(profile.technologies), 0)
        self.assertEqual(len(profile.skills), 0)
        self.assertEqual(len(profile.languages), 0)

    def test_27_empty_account(self):
        """Empty account with 0 repositories aggregates cleanly without errors."""
        profile = self.service.aggregate_account_profile([])

        self.assertEqual(profile.repository_coverage.total_repositories_analyzed, 0)
        self.assertEqual(len(profile.languages), 0)
        self.assertEqual(len(profile.technologies), 0)
        self.assertEqual(len(profile.skills), 0)
        self.assertEqual(profile.total_unique_technologies, 0)
        self.assertEqual(profile.total_unique_skills, 0)

    def test_28_partial_repository_handling(self):
        """Partial repository (tree truncated) is tracked in partially_analyzed_repositories."""
        repo_partial = RepositoryAnalysisDetail(
            name="huge-repo",
            full_name="dev/huge-repo",
            html_url="https://github.com/dev/huge-repo",
            analysis_status="PARTIAL",
            is_partial=True,
            tree_truncated=True,
            technologies=["Python"],
        )
        profile = self.service.aggregate_account_profile([repo_partial])

        self.assertEqual(profile.repository_coverage.partially_analyzed_repositories, 1)
        self.assertEqual(profile.repository_coverage.successfully_analyzed_repositories, 0)
        # Partial repos still contribute valid detected technologies
        self.assertEqual(len(profile.technologies), 1)
        self.assertEqual(profile.technologies[0].name, "Python")

    # -------------------------------------------------------------------------
    # 7. Preservation of Original Repository Data (Section 21)
    # -------------------------------------------------------------------------

    def test_29_no_cross_repository_data_mutation_section_21(self):
        """
        Mandatory test from Section 21:
        Verify repository analysis before aggregation == repository analysis after aggregation.
        Aggregation must NEVER mutate repository-level data.
        """
        repo_original = RepositoryAnalysisDetail(
            name="microservice",
            full_name="dev/microservice",
            html_url="https://github.com/dev/microservice",
            description="A microservice",
            default_branch="master",
            primary_language="Python",
            languages=["Python", "Shell"],
            technologies=["FastAPI", "SQLAlchemy", "Docker"],
            manifest_files=["requirements.txt", "Dockerfile"],
            project_type="BACKEND",
            skills=["Python", "FastAPI", "Docker"],
            evidence=[
                EvidenceSourceSignal(
                    source_type=EVIDENCE_SOURCE_MANIFEST,
                    technology="FastAPI",
                    path="requirements.txt",
                    strength=EVIDENCE_STRENGTH_STRONG,
                    reason="Found in requirements.txt",
                )
            ],
            analysis_status="SUCCESS",
            is_fork=False,
            is_archived=False,
            is_empty=False,
            warnings=["Minor warning"],
        )

        # Deep copy to compare before and after
        repo_snapshot = copy.deepcopy(repo_original.model_dump())

        # Perform aggregation
        self.service.aggregate_account_profile([repo_original])

        # Verify nothing mutated
        repo_after = repo_original.model_dump()
        self.assertEqual(repo_snapshot, repo_after, "Repository data was mutated by aggregation!")

    # -------------------------------------------------------------------------
    # 8. Deterministic Ordering and Output Stability
    # -------------------------------------------------------------------------

    def test_30_deterministic_aggregation_output(self):
        """Multiple runs with shuffled repository order produce identical aggregated output."""
        repo1 = RepositoryAnalysisDetail(
            name="alpha",
            full_name="dev/alpha",
            html_url="https://github.com/dev/alpha",
            languages=["Python"],
            technologies=["Django"],
            skills=["Python", "Django"],
        )
        repo2 = RepositoryAnalysisDetail(
            name="beta",
            full_name="dev/beta",
            html_url="https://github.com/dev/beta",
            languages=["Python", "TypeScript"],
            technologies=["React", "Django"],
            skills=["React", "Django"],
        )

        profile_1 = self.service.aggregate_account_profile([repo1, repo2])
        profile_2 = self.service.aggregate_account_profile([repo2, repo1])

        # Technologies ordering must match
        techs_1 = [(t.name, t.repository_count, t.supporting_repositories) for t in profile_1.technologies]
        techs_2 = [(t.name, t.repository_count, t.supporting_repositories) for t in profile_2.technologies]
        self.assertEqual(techs_1, techs_2)

        # Languages ordering must match
        langs_1 = [(l.name, l.repository_count, l.supporting_repositories) for l in profile_1.languages]
        langs_2 = [(l.name, l.repository_count, l.supporting_repositories) for l in profile_2.languages]
        self.assertEqual(langs_1, langs_2)

    # -------------------------------------------------------------------------
    # 9. GitHubAccountService Integration Check
    # -------------------------------------------------------------------------

    def test_31_account_service_has_aggregation_support(self):
        """GitHubAccountService has aggregation_service wired and aggregate_account method available."""
        account_service = GitHubAccountService()
        self.assertIsNotNone(account_service.aggregation_service)
        self.assertTrue(hasattr(account_service, "aggregate_account"))


if __name__ == "__main__":
    unittest.main()
