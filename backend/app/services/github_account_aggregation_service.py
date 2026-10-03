"""
github_account_aggregation_service.py
-------------------------------------
Service for synthesizing account-level intelligence across multiple analyzed repositories.

Target Workflow:
List of Analyzed Repositories (Tasks 3–5)
        ↓
Aggregate languages (counting repositories, not file/line numbers)
        ↓
Aggregate technologies (normalized, deduplicated per repo, tracking supporting repos)
        ↓
Aggregate skills (domain categorized, evidence strength based on multi-repo proof)
        ↓
Compute evidence summary (STRONG, MODERATE, WEAK counts and technology coverage)
        ↓
Compute repository coverage statistics (original, forks, archived, active, empty, error)
        ↓
Produce AggregatedAccountProfile

Design Constraints:
1. Pure in-memory aggregation: NEVER calls GitHub API, never fetches trees/manifests.
2. Read-only preservation: NEVER mutates individual repository records.
3. Unit semantics: Counts REPOSITORIES, not raw evidence occurrences or line numbers.
4. Determinism: Alphabetical and frequency-based stable ordering.
"""

from collections import defaultdict
from typing import Any, Dict, List, Optional, Set, Tuple

from app.schemas.github_account import (
    EVIDENCE_STRENGTH_MODERATE,
    EVIDENCE_STRENGTH_STRONG,
    EVIDENCE_STRENGTH_WEAK,
    AggregatedAccountProfile,
    AggregatedLanguage,
    AggregatedSkill,
    AggregatedTechnology,
    EvidenceSummary,
    RepositoryAnalysisDetail,
    RepositoryCoverage,
)
from app.schemas.skill_profile import SkillCategoryResponse, SkillResponse
from app.services.skill_profile_service import (
    CATEGORY_DEFINITIONS,
    FALLBACK_CATEGORY,
    SkillProfileService,
    _classify_technology,
    skill_profile_service,
)
from app.services.technology_service import (
    TechnologyService,
    normalize_technology_name,
    technology_service,
)


class GitHubAccountAggregationService:
    """
    Dedicated service for cross-repository aggregation and account-level synthesis.
    """

    def __init__(
        self,
        tech_service: Optional[TechnologyService] = None,
        skill_service: Optional[SkillProfileService] = None,
    ):
        self.technology_service = tech_service or technology_service
        self.skill_profile_service = skill_service or skill_profile_service

    def aggregate_account_profile(
        self, repositories: List[RepositoryAnalysisDetail]
    ) -> AggregatedAccountProfile:
        """
        Synthesize cross-repository developer intelligence into an AggregatedAccountProfile.

        Args:
            repositories: List of RepositoryAnalysisDetail models from Tasks 3–5.

        Returns:
            AggregatedAccountProfile with aggregated languages, technologies, skills,
            evidence summary, and repository coverage.
        """
        coverage = self._calculate_coverage(repositories)
        languages = self._aggregate_languages(repositories)
        technologies = self._aggregate_technologies(repositories)
        skills, categorized_skills = self._aggregate_skills(repositories)
        evidence_summary = self._calculate_evidence_summary(repositories, technologies)

        return AggregatedAccountProfile(
            languages=languages,
            technologies=technologies,
            skills=skills,
            categorized_skills=categorized_skills,
            repository_coverage=coverage,
            evidence_summary=evidence_summary,
            total_unique_technologies=len(technologies),
            total_unique_skills=len(skills),
        )

    # -------------------------------------------------------------------------
    # 1. Language Aggregation
    # -------------------------------------------------------------------------

    def _aggregate_languages(
        self, repositories: List[RepositoryAnalysisDetail]
    ) -> List[AggregatedLanguage]:
        """
        Aggregate programming languages across repositories.
        Unit: number of unique repositories utilizing the language.
        """
        lang_to_repos: Dict[str, Set[str]] = defaultdict(set)
        total_repos = len(repositories)

        for repo in repositories:
            # Skip empty or failed repositories
            if repo.is_empty or repo.analysis_status == "ERROR":
                continue

            repo_name = repo.name or repo.full_name
            repo_langs: Set[str] = set()

            for lang in repo.languages:
                norm = normalize_technology_name(lang)
                if norm:
                    repo_langs.add(norm)

            if repo.primary_language:
                norm_primary = normalize_technology_name(repo.primary_language)
                if norm_primary:
                    repo_langs.add(norm_primary)

            for norm_lang in repo_langs:
                lang_to_repos[norm_lang].add(repo_name)

        aggregated: List[AggregatedLanguage] = []
        for lang_name, supporting_set in lang_to_repos.items():
            count = len(supporting_set)
            percentage = (
                round((count / total_repos) * 100, 2) if total_repos > 0 else 0.0
            )
            aggregated.append(
                AggregatedLanguage(
                    name=lang_name,
                    repository_count=count,
                    percentage=percentage,
                    supporting_repositories=sorted(list(supporting_set)),
                )
            )

        # Deterministic sorting: highest repository_count descending, then name ascending
        return sorted(aggregated, key=lambda x: (-x.repository_count, x.name))

    # -------------------------------------------------------------------------
    # 2. Technology Aggregation
    # -------------------------------------------------------------------------

    def _aggregate_technologies(
        self, repositories: List[RepositoryAnalysisDetail]
    ) -> List[AggregatedTechnology]:
        """
        Aggregate normalized technologies across repositories.
        Unit: number of unique repositories demonstrating the technology.
        """
        tech_to_repos: Dict[str, Set[str]] = defaultdict(set)
        tech_evidence_count: Dict[str, int] = defaultdict(int)

        for repo in repositories:
            # Skip empty or failed repositories
            if repo.is_empty or repo.analysis_status == "ERROR":
                continue

            repo_name = repo.name or repo.full_name

            # Deduplicate technologies within this repository
            repo_techs: Set[str] = set()
            for t in repo.technologies:
                norm = normalize_technology_name(t)
                if norm:
                    repo_techs.add(norm)

            for norm_tech in repo_techs:
                tech_to_repos[norm_tech].add(repo_name)

            # Count discrete evidence signals supporting this technology
            for ev in repo.evidence:
                norm_ev_tech = normalize_technology_name(ev.technology)
                if norm_ev_tech in repo_techs:
                    tech_evidence_count[norm_ev_tech] += 1

        aggregated: List[AggregatedTechnology] = []
        for tech_name, supporting_set in tech_to_repos.items():
            count = len(supporting_set)
            ev_count = tech_evidence_count.get(tech_name, 0)
            aggregated.append(
                AggregatedTechnology(
                    name=tech_name,
                    repository_count=count,
                    evidence_count=ev_count,
                    supporting_repositories=sorted(list(supporting_set)),
                )
            )

        # Deterministic sorting: repository_count descending, then alphabetical name
        return sorted(aggregated, key=lambda x: (-x.repository_count, x.name))

    # -------------------------------------------------------------------------
    # 3. Skill Aggregation
    # -------------------------------------------------------------------------

    def _aggregate_skills(
        self, repositories: List[RepositoryAnalysisDetail]
    ) -> Tuple[List[AggregatedSkill], List[SkillCategoryResponse]]:
        """
        Aggregate skills across repositories with grounded evidence strength.
        Strength rules:
        - STRONG: >= 2 supporting repositories OR direct manifest/config evidence
        - MODERATE: 1 supporting repository with language/structure evidence
        - WEAK: topic-only evidence
        """
        skill_to_repos: Dict[str, Set[str]] = defaultdict(set)
        skill_to_strengths: Dict[str, Set[str]] = defaultdict(set)
        skill_evidence_count: Dict[str, int] = defaultdict(int)

        for repo in repositories:
            if repo.is_empty or repo.analysis_status == "ERROR":
                continue

            repo_name = repo.name or repo.full_name
            repo_skills = set(repo.skills)

            for skill in repo_skills:
                skill_to_repos[skill].add(repo_name)

            for ev in repo.evidence:
                if ev.technology in repo_skills:
                    skill_evidence_count[ev.technology] += 1
                    skill_to_strengths[ev.technology].add(ev.strength)

        aggregated_skills: List[AggregatedSkill] = []
        category_buckets: Dict[str, List[SkillResponse]] = {
            cat_name: [] for cat_name, _ in CATEGORY_DEFINITIONS
        }
        category_buckets[FALLBACK_CATEGORY] = []

        for skill_name, supporting_set in skill_to_repos.items():
            repo_count = len(supporting_set)
            ev_count = skill_evidence_count.get(skill_name, 0)
            strengths = skill_to_strengths.get(skill_name, set())

            # Evaluate grounded evidence strength (not skill proficiency)
            if repo_count >= 2 or EVIDENCE_STRENGTH_STRONG in strengths:
                final_strength = EVIDENCE_STRENGTH_STRONG
            elif EVIDENCE_STRENGTH_MODERATE in strengths or repo_count == 1:
                final_strength = EVIDENCE_STRENGTH_MODERATE
            else:
                final_strength = EVIDENCE_STRENGTH_WEAK

            # Classify primary domain category
            matched_cats = _classify_technology(skill_name)
            primary_cat = matched_cats[0] if matched_cats else FALLBACK_CATEGORY

            agg_skill = AggregatedSkill(
                name=skill_name,
                category=primary_cat,
                repository_count=repo_count,
                evidence_count=ev_count,
                evidence_strength=final_strength,
                supporting_repositories=sorted(list(supporting_set)),
            )
            aggregated_skills.append(agg_skill)

            # Bucket into domain categories
            for cat in matched_cats:
                if cat in category_buckets:
                    category_buckets[cat].append(
                        SkillResponse(name=skill_name, repository_count=repo_count)
                    )

        # Deterministic sorting: repository_count descending, then alphabetical
        sorted_skills = sorted(aggregated_skills, key=lambda s: (-s.repository_count, s.name))

        # Build categorized domain list
        categorized: List[SkillCategoryResponse] = []
        for cat_name, _ in CATEGORY_DEFINITIONS:
            items = category_buckets[cat_name]
            if items:
                categorized.append(
                    SkillCategoryResponse(
                        category=cat_name,
                        skills=sorted(items, key=lambda x: (-x.repository_count, x.name)),
                    )
                )

        if category_buckets[FALLBACK_CATEGORY]:
            categorized.append(
                SkillCategoryResponse(
                    category=FALLBACK_CATEGORY,
                    skills=sorted(
                        category_buckets[FALLBACK_CATEGORY],
                        key=lambda x: (-x.repository_count, x.name),
                    ),
                )
            )

        return sorted_skills, categorized

    # -------------------------------------------------------------------------
    # 4. Evidence Summary Calculation
    # -------------------------------------------------------------------------

    def _calculate_evidence_summary(
        self,
        repositories: List[RepositoryAnalysisDetail],
        technologies: List[AggregatedTechnology],
    ) -> EvidenceSummary:
        """
        Calculate account-wide evidence signal counts and technology coverage.
        """
        strong_count = 0
        moderate_count = 0
        weak_count = 0
        total_signals = 0

        techs_with_strong: Set[str] = set()
        techs_with_any: Set[str] = set()

        for repo in repositories:
            if repo.is_empty or repo.analysis_status == "ERROR":
                continue

            for ev in repo.evidence:
                total_signals += 1
                norm_tech = normalize_technology_name(ev.technology)
                techs_with_any.add(norm_tech)

                if ev.strength == EVIDENCE_STRENGTH_STRONG:
                    strong_count += 1
                    techs_with_strong.add(norm_tech)
                elif ev.strength == EVIDENCE_STRENGTH_MODERATE:
                    moderate_count += 1
                elif ev.strength == EVIDENCE_STRENGTH_WEAK:
                    weak_count += 1

        # Multi-repo technologies (>= 2 repositories) also qualify as strong evidence
        for t in technologies:
            if t.repository_count >= 2:
                techs_with_strong.add(t.name)

        return EvidenceSummary(
            strong_evidence_count=strong_count,
            moderate_evidence_count=moderate_count,
            weak_evidence_count=weak_count,
            total_evidence_signals=total_signals,
            technologies_with_strong_evidence=len(techs_with_strong),
            technologies_with_evidence=len(techs_with_any),
        )

    # -------------------------------------------------------------------------
    # 5. Repository Coverage Calculation
    # -------------------------------------------------------------------------

    def _calculate_coverage(
        self, repositories: List[RepositoryAnalysisDetail]
    ) -> RepositoryCoverage:
        """
        Compute transparent account repository statistics.
        Does not exclude forks, archived, or empty repositories from catalog.
        """
        total = len(repositories)
        forked = sum(1 for r in repositories if r.is_fork)
        original = total - forked
        archived = sum(1 for r in repositories if r.is_archived)
        active = total - archived
        empty = sum(1 for r in repositories if r.is_empty)
        error_count = sum(1 for r in repositories if r.analysis_status == "ERROR")

        successfully_analyzed = sum(
            1
            for r in repositories
            if r.analysis_status == "SUCCESS" and not r.is_partial and not r.is_empty
        )
        partially_analyzed = sum(
            1
            for r in repositories
            if (r.is_partial or r.analysis_status == "PARTIAL")
            and r.analysis_status != "ERROR"
        )

        return RepositoryCoverage(
            total_repositories_analyzed=total,
            original_repositories=original,
            forked_repositories=forked,
            archived_repositories=archived,
            active_repositories=active,
            successfully_analyzed_repositories=successfully_analyzed,
            partially_analyzed_repositories=partially_analyzed,
            empty_repositories=empty,
            error_repositories=error_count,
        )


# Singleton instance for account service integration
github_account_aggregation_service = GitHubAccountAggregationService()
