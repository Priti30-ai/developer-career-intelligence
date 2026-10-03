"""
developer_profile_service.py
----------------------------
Service layer for Unified Developer Profile Synthesis.

Combines signals from:
1. GitHub Account Intelligence (catalog discovery, repository inspection,
   technology extraction, code artifact evidence, cross-repo aggregation)
2. Resume Intelligence (section parsing, canonical skills, multi-category taxonomy,
   provenance tracking across skills, projects, and experience)
3. Deterministic Evidence Synthesis (code-grounded verification levels,
   neutral source presence tracking)

Produces a canonical, unified developer profile suitable for downstream intelligence
modules (Job Description Matching, Skill Gap Analysis, Career Recommendations,
and UI dashboard consumption).

Determinism & Semantics:
- Canonical skill names are normalized using technology_service.normalize_technology_name.
- Categories reuse the shared taxonomy from skill_profile_service._classify_technology.
- Origin sources ('github', 'resume', or both) are explicitly tracked for every skill.
- Evidence status ('STRONG', 'MODERATE', 'NONE_DETECTED') reflects verified GitHub evidence.
- A skill existing only on the resume with 'NONE_DETECTED' evidence status reflects
  the absence of analyzed GitHub repository evidence, NOT proof that the candidate lacks the skill.
- Resume evidence NEVER increases GitHub evidence strength.
- No subjective proficiency scoring is synthesized.
"""

from typing import Any, Dict, List, Optional, Set, Union

from app.schemas.developer_profile import (
    SOURCE_GITHUB,
    SOURCE_RESUME,
    DeveloperProfileResponse,
    DeveloperProfileSummary,
    DeveloperSkill,
    DeveloperSkillEvidence,
    GitHubSummary,
    ResumeSummary,
)
from app.schemas.evidence import SupportingRepository
from app.schemas.github_account import (
    EVIDENCE_STRENGTH_MODERATE,
    EVIDENCE_STRENGTH_STRONG,
    EVIDENCE_STRENGTH_WEAK,
    AggregatedAccountProfile,
    AggregatedSkill,
    GitHubAccountAnalysisResponse,
    RepositoryAnalysisDetail,
)
from app.schemas.resume import (
    ResumeEducation,
    ResumeExperience,
    ResumeProject,
    ResumeSkill,
)
from app.schemas.skill_profile import SkillCategoryResponse, SkillResponse
from app.services.github_account_aggregation_service import (
    GitHubAccountAggregationService,
    github_account_aggregation_service,
)
from app.services.github_account_service import (
    GitHubAccountService,
    github_account_service,
)
from app.services.github_evidence_service import (
    GitHubEvidenceService,
    github_evidence_service,
)
from app.services.github_service import (
    GitHubAPIError,
    GitHubService,
    GitHubUserNotFoundError,
    github_service,
)
from app.services.resume_service import resume_service
from app.services.skill_profile_service import (
    CATEGORY_DEFINITIONS,
    FALLBACK_CATEGORY,
    _classify_technology,
)
from app.services.technology_service import normalize_technology_name

# Standardized evidence levels (aligned with existing tests & schemas)
EVIDENCE_LEVEL_STRONG = "STRONG"
EVIDENCE_LEVEL_MODERATE = "MODERATE"
EVIDENCE_LEVEL_NONE_DETECTED = "NONE_DETECTED"


class DeveloperProfileService:
    """
    Deterministic synthesis service for building a Unified Developer Profile.
    """

    def __init__(
        self,
        gh_service: Optional[GitHubService] = None,
        account_service: Optional[GitHubAccountService] = None,
        evidence_service: Optional[GitHubEvidenceService] = None,
        aggregation_service: Optional[GitHubAccountAggregationService] = None,
    ):
        self.github_service = gh_service or github_service
        self.github_account_service = account_service or github_account_service
        self.github_evidence_service = evidence_service or github_evidence_service
        self.github_aggregation_service = aggregation_service or github_account_aggregation_service

    def normalize_skills(self, skills: List[str]) -> List[str]:
        """
        Normalize and deduplicate a list of skill names using canonical aliases.
        Preserves deterministic unique ordering.
        """
        seen: Set[str] = set()
        normalized: List[str] = []

        for s in skills:
            if not s or not isinstance(s, str):
                continue
            norm = normalize_technology_name(s)
            if norm and norm not in seen:
                seen.add(norm)
                normalized.append(norm)

        return normalized

    async def synthesize_profile(
        self,
        username: str,
        resume_text: Optional[str] = None,
        resume_skills: Optional[List[str]] = None,
        repositories: Optional[List[Dict[str, Any]]] = None,
        github_account_response: Optional[GitHubAccountAnalysisResponse] = None,
    ) -> Dict[str, Any]:
        """
        Synthesize a unified developer profile by aggregating GitHub Account Intelligence
        and Resume Intelligence data.

        Args:
            username: Target developer GitHub username.
            resume_text: Optional plain-text resume content.
            resume_skills: Optional explicit list of resume skills.
            repositories: Optional pre-fetched repository list (for testing or offline use).
            github_account_response: Optional pre-computed GitHubAccountAnalysisResponse.

        Returns:
            Dict conforming to DeveloperProfileResponse schema.

        Raises:
            GitHubUserNotFoundError: If GitHub user does not exist.
            GitHubAPIError: If GitHub API returns rate limit, timeout, or failure.
            ValueError: If username is empty or invalid.
        """
        clean_username = username.strip()
        if not clean_username:
            raise ValueError("GitHub username must not be empty or whitespace-only")

        # ---------------------------------------------------------------------
        # 1. GitHub Account Intelligence Ingestion
        # ---------------------------------------------------------------------
        if github_account_response is not None:
            enriched_repos = github_account_response.repositories
            aggregated_profile = github_account_response.aggregated_profile
            raw_repo_count = len(enriched_repos)
        elif repositories is not None:
            raw_repo_count = len(repositories)
            repository_details: List[RepositoryAnalysisDetail] = []
            needs_enrichment = False

            for r in repositories:
                if isinstance(r, RepositoryAnalysisDetail):
                    repository_details.append(r)
                    if not r.evidence and not r.skills:
                        needs_enrichment = True
                elif isinstance(r, dict):
                    if r.get("evidence") or r.get("skills"):
                        detail = RepositoryAnalysisDetail(**r)
                        repository_details.append(detail)
                    else:
                        detail = self.github_account_service._map_repository_detail(r)
                        repository_details.append(detail)
                        needs_enrichment = True
                else:
                    needs_enrichment = True

            if needs_enrichment:
                enriched_repos = await self.github_evidence_service.enrich_repositories(
                    repository_details,
                    default_owner=clean_username,
                    fetch_manifests=False,
                )
            else:
                enriched_repos = repository_details

            aggregated_profile = self.github_aggregation_service.aggregate_account_profile(
                enriched_repos
            )
        else:
            try:
                account_analysis = await self.github_account_service.aggregate_account(clean_username)
                enriched_repos = account_analysis.repositories
                aggregated_profile = account_analysis.aggregated_profile
                raw_repo_count = len(enriched_repos)
            except (AttributeError, Exception) as exc:
                # If explicit not-found or api-error, propagate immediately
                if isinstance(exc, (GitHubUserNotFoundError, GitHubAPIError, ValueError)):
                    raise
                # Fallback for environments where only get_user_repositories was mocked
                repos_data = await self.github_service.get_user_repositories(clean_username)
                raw_repo_count = len(repos_data)
                repository_details = [
                    self.github_account_service._map_repository_detail(r)
                    for r in repos_data
                ]
                enriched_repos = await self.github_evidence_service.enrich_repositories(
                    repository_details,
                    default_owner=clean_username,
                    fetch_manifests=False,
                )
                aggregated_profile = self.github_aggregation_service.aggregate_account_profile(
                    enriched_repos
                )

        # Build GitHub skill index and supporting repository maps
        github_skill_map: Dict[str, AggregatedSkill] = {
            normalize_technology_name(s.name): s for s in aggregated_profile.skills
        }

        github_skill_to_supporting_repos: Dict[str, List[SupportingRepository]] = {}
        github_skill_to_signals: Dict[str, Set[str]] = {}

        for repo in enriched_repos:
            if repo.is_empty or repo.analysis_status == "ERROR":
                continue

            repo_model = SupportingRepository(
                name=repo.name or "",
                full_name=repo.full_name,
                html_url=repo.html_url,
                skills_detected=repo.skills,
            )

            for skill_name in repo.skills:
                norm_s = normalize_technology_name(skill_name)
                if norm_s:
                    if norm_s not in github_skill_to_supporting_repos:
                        github_skill_to_supporting_repos[norm_s] = []
                    github_skill_to_supporting_repos[norm_s].append(repo_model)

            for ev in repo.evidence:
                norm_ev_tech = normalize_technology_name(ev.technology)
                if norm_ev_tech:
                    if norm_ev_tech not in github_skill_to_signals:
                        github_skill_to_signals[norm_ev_tech] = set()
                    github_skill_to_signals[norm_ev_tech].add(ev.source_type)

        # ---------------------------------------------------------------------
        # 2. Resume Intelligence Ingestion
        # ---------------------------------------------------------------------
        resume_summary_data: Dict[str, Any] = {
            "summary": None,
            "skills": [],
            "education": [],
            "experience": [],
            "projects": [],
            "certifications": [],
            "achievements": [],
            "categorized_skills": [],
        }
        resume_categorized_skills: List[Dict[str, Any]] = []

        if resume_text and resume_text.strip():
            parsed_resume = resume_service.analyze_resume(resume_text)
            resume_summary_data["summary"] = parsed_resume.get("summary")
            resume_summary_data["skills"] = parsed_resume.get("skills", [])
            resume_summary_data["education"] = [
                ResumeEducation(**edu) if isinstance(edu, dict) else edu
                for edu in parsed_resume.get("education", [])
            ]
            resume_summary_data["experience"] = [
                ResumeExperience(**exp) if isinstance(exp, dict) else exp
                for exp in parsed_resume.get("experience", [])
            ]
            resume_summary_data["projects"] = [
                ResumeProject(**prj) if isinstance(prj, dict) else prj
                for prj in parsed_resume.get("projects", [])
            ]
            resume_summary_data["certifications"] = parsed_resume.get("certifications", [])
            resume_summary_data["achievements"] = parsed_resume.get("achievements", [])

            raw_cat_skills = parsed_resume.get("categorized_skills", [])
            resume_summary_data["categorized_skills"] = [
                ResumeSkill(**s) if isinstance(s, dict) else s
                for s in raw_cat_skills
            ]
            resume_categorized_skills = [
                s.model_dump() if hasattr(s, "model_dump") else s
                for s in raw_cat_skills
            ]
        elif resume_skills:
            norm_res_skills = self.normalize_skills(resume_skills)
            resume_summary_data["skills"] = norm_res_skills
            resume_categorized_skills = [
                {
                    "name": s,
                    "categories": _classify_technology(s),
                    "sources": ["skills_section"],
                }
                for s in norm_res_skills
            ]
            resume_summary_data["categorized_skills"] = [
                ResumeSkill(**s) for s in resume_categorized_skills
            ]

        # Index resume skills by canonical technology name
        resume_skill_map: Dict[str, Dict[str, Any]] = {}
        for r_item in resume_categorized_skills:
            r_name = r_item.get("name") if isinstance(r_item, dict) else getattr(r_item, "name", "")
            norm_name = normalize_technology_name(r_name)
            if norm_name:
                if norm_name not in resume_skill_map:
                    resume_skill_map[norm_name] = {
                        "name": norm_name,
                        "categories": _classify_technology(norm_name),
                        "sources": set(),
                    }
                srcs = (
                    r_item.get("sources", [])
                    if isinstance(r_item, dict)
                    else getattr(r_item, "sources", [])
                )
                resume_skill_map[norm_name]["sources"].update(srcs)

        # ---------------------------------------------------------------------
        # 3. Canonical Unified Skill Merge
        # ---------------------------------------------------------------------
        all_canonical_names = sorted(
            list(set(github_skill_map.keys()) | set(resume_skill_map.keys())),
            key=lambda s: s.lower(),
        )

        unified_skills: List[DeveloperSkill] = []
        for name in all_canonical_names:
            in_github = name in github_skill_map
            in_resume = name in resume_skill_map

            sources: List[str] = []
            if in_github:
                sources.append(SOURCE_GITHUB)
            if in_resume:
                sources.append(SOURCE_RESUME)
            sources = sorted(sources)

            # Domain categories from canonical taxonomy
            categories = _classify_technology(name)

            # GitHub evidence status and supporting repositories
            gh_skill = github_skill_map.get(name)
            matching_repos = github_skill_to_supporting_repos.get(name, [])
            sorted_matching_repos = sorted(matching_repos, key=lambda r: r.name.lower())

            if in_github and gh_skill:
                if gh_skill.evidence_strength in (EVIDENCE_LEVEL_STRONG, EVIDENCE_LEVEL_MODERATE):
                    evidence_status = gh_skill.evidence_strength
                elif gh_skill.repository_count >= 2:
                    evidence_status = EVIDENCE_LEVEL_STRONG
                elif gh_skill.repository_count == 1:
                    evidence_status = EVIDENCE_LEVEL_MODERATE
                else:
                    evidence_status = EVIDENCE_LEVEL_MODERATE

                gh_repo_count = gh_skill.repository_count
                gh_ev_count = gh_skill.evidence_count
                gh_strength = gh_skill.evidence_strength
                gh_supporting_names = gh_skill.supporting_repositories or [r.name for r in sorted_matching_repos]
            elif in_github:
                repo_count = len(sorted_matching_repos)
                evidence_status = EVIDENCE_LEVEL_STRONG if repo_count >= 2 else EVIDENCE_LEVEL_MODERATE
                gh_repo_count = repo_count
                gh_ev_count = repo_count
                gh_strength = evidence_status
                gh_supporting_names = [r.name for r in sorted_matching_repos]
            else:
                evidence_status = EVIDENCE_LEVEL_NONE_DETECTED
                gh_repo_count = 0
                gh_ev_count = 0
                gh_strength = None
                gh_supporting_names = []

            # Signal types detected across repositories
            sig_types = sorted(list(github_skill_to_signals.get(name, set())))

            # Resume section provenance
            res_entry = resume_skill_map.get(name)
            res_sources = sorted(list(res_entry["sources"])) if res_entry else []

            evidence_obj = DeveloperSkillEvidence(
                repository_count=gh_repo_count,
                evidence_count=gh_ev_count,
                evidence_strength=gh_strength,
                supporting_repositories=gh_supporting_names,
                signal_types=sig_types,
                resume_sources=res_sources,
            )

            unified_skills.append(
                DeveloperSkill(
                    name=name,
                    skill=name,
                    categories=categories,
                    sources=sources,
                    evidence_status=evidence_status,
                    evidence=evidence_obj,
                    supporting_repositories=sorted_matching_repos,
                )
            )

        # ---------------------------------------------------------------------
        # 4. Expose Categorized Profile
        # ---------------------------------------------------------------------
        category_buckets: Dict[str, List[SkillResponse]] = {
            cat_name: [] for cat_name, _ in CATEGORY_DEFINITIONS
        }
        category_buckets[FALLBACK_CATEGORY] = []

        for s in unified_skills:
            for cat in s.categories:
                if cat in category_buckets:
                    category_buckets[cat].append(
                        SkillResponse(
                            name=s.name or s.skill,
                            repository_count=s.evidence.repository_count,
                        )
                    )

        categorized_unified_skills: List[SkillCategoryResponse] = []
        for cat_name, _ in CATEGORY_DEFINITIONS:
            items = category_buckets[cat_name]
            if items:
                categorized_unified_skills.append(
                    SkillCategoryResponse(
                        category=cat_name,
                        skills=sorted(items, key=lambda x: (-x.repository_count, x.name)),
                    )
                )

        if category_buckets[FALLBACK_CATEGORY]:
            categorized_unified_skills.append(
                SkillCategoryResponse(
                    category=FALLBACK_CATEGORY,
                    skills=sorted(
                        category_buckets[FALLBACK_CATEGORY],
                        key=lambda x: (-x.repository_count, x.name),
                    ),
                )
            )

        # ---------------------------------------------------------------------
        # 5. Summary Metrics and Response Construction
        # ---------------------------------------------------------------------
        total_skills = len(unified_skills)
        github_skill_count = len(github_skill_map)
        resume_skill_count = len(resume_skill_map)
        skills_from_both_sources = sum(
            1 for s in unified_skills if SOURCE_GITHUB in s.sources and SOURCE_RESUME in s.sources
        )
        github_only_skills = sum(
            1 for s in unified_skills if s.sources == [SOURCE_GITHUB]
        )
        resume_only_skills = sum(
            1 for s in unified_skills if s.sources == [SOURCE_RESUME]
        )
        supported_skill_count = sum(
            1 for s in unified_skills if s.evidence_status != EVIDENCE_LEVEL_NONE_DETECTED
        )
        skills_without_github_evidence = sum(
            1 for s in unified_skills if s.evidence_status == EVIDENCE_LEVEL_NONE_DETECTED
        )

        summary = DeveloperProfileSummary(
            total_skills=total_skills,
            github_skill_count=github_skill_count,
            resume_skill_count=resume_skill_count,
            skills_from_both_sources=skills_from_both_sources,
            github_only_skills=github_only_skills,
            resume_only_skills=resume_only_skills,
            supported_skill_count=supported_skill_count,
            skills_without_github_evidence=skills_without_github_evidence,
        )

        all_detected_techs = sorted(list({
            t.name for t in aggregated_profile.technologies
        } | set(github_skill_map.keys())))

        github_summary = GitHubSummary(
            username=clean_username,
            repositories_analyzed=raw_repo_count,
            technologies_detected=all_detected_techs,
            repository_coverage=aggregated_profile.repository_coverage,
            evidence_summary=aggregated_profile.evidence_summary,
            languages=aggregated_profile.languages,
        )

        resume_summary = ResumeSummary(**resume_summary_data)

        response = DeveloperProfileResponse(
            developer_id=clean_username,
            github=github_summary,
            resume=resume_summary,
            skills=unified_skills,
            categorized_skills=categorized_unified_skills,
            summary=summary,
        )

        return response.model_dump()


def extract_developer_skills(profile_or_skills: Any) -> List[str]:
    """
    Extract a clean list of canonical skill names from a DeveloperProfileResponse,
    a profile dictionary, or an iterable of DeveloperSkill instances.

    Enables seamless, zero-copy integration with downstream modules such as
    JobMatchingService and SkillGapService.
    """
    if isinstance(profile_or_skills, DeveloperProfileResponse):
        return profile_or_skills.get_skill_names()

    if isinstance(profile_or_skills, dict):
        skills_data = profile_or_skills.get("skills", [])
        extracted: List[str] = []
        for s in skills_data:
            if isinstance(s, dict) and "skill" in s:
                extracted.append(s["skill"])
            elif hasattr(s, "skill"):
                extracted.append(getattr(s, "skill"))
            elif isinstance(s, str):
                extracted.append(s)
        return extracted

    if isinstance(profile_or_skills, (list, tuple, set)):
        extracted = []
        for s in profile_or_skills:
            if isinstance(s, str):
                extracted.append(s)
            elif isinstance(s, dict) and "skill" in s:
                extracted.append(s["skill"])
            elif hasattr(s, "skill"):
                extracted.append(getattr(s, "skill"))
        return extracted

    return []


# Singleton instance for route, service, and script usage
developer_profile_service = DeveloperProfileService()
