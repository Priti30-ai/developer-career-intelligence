"""
job_matching_service.py
-----------------------
Service layer for comparing Job Description requirements with developer skills.

Calculates:
- matched_skills
- missing_skills
- total_required_skills
- matched_skill_count
- missing_skill_count
- match_percentage = round((matched_skill_count / total_required_skills) * 100, 2)
- matched_skill_details (with grounded evidence, sources, and repos)
- missing_skill_details (with canonical taxonomy categories)
- category_breakdown (deterministic category coverage statistics)
"""

from typing import Any, Dict, List, Optional, Sequence, Union

from app.schemas.developer_profile import DeveloperProfileResponse, DeveloperSkill
from app.services.job_description_service import (
    job_description_service,
)
from app.services.skill_profile_service import (
    CATEGORY_DEFINITIONS,
    FALLBACK_CATEGORY,
    _classify_technology,
)
from app.services.technology_service import normalize_technology_name


class _AdaptedSkill:
    """Internal container for adapted developer skill metadata."""

    def __init__(
        self,
        name: str,
        categories: Optional[List[str]] = None,
        sources: Optional[List[str]] = None,
        evidence_status: Optional[str] = None,
        supporting_repositories: Optional[List[str]] = None,
    ):
        self.name = name
        self.categories = categories or []
        self.sources = sources or []
        self.evidence_status = evidence_status
        self.supporting_repositories = supporting_repositories or []


def _extract_repo_names(item: Any) -> List[str]:
    """Extract repository names from a DeveloperSkill or dict representation."""
    repos: List[str] = []

    # Check evidence.supporting_repositories (List[str])
    ev = getattr(item, "evidence", None)
    if ev is None and isinstance(item, dict):
        ev = item.get("evidence")

    if ev:
        ev_repos = getattr(ev, "supporting_repositories", None)
        if ev_repos is None and isinstance(ev, dict):
            ev_repos = ev.get("supporting_repositories")
        if ev_repos:
            for r in ev_repos:
                if isinstance(r, str):
                    repos.append(r)
                elif hasattr(r, "name"):
                    repos.append(r.name)
                elif isinstance(r, dict) and "name" in r:
                    repos.append(r["name"])

    # Check item.supporting_repositories (List[SupportingRepository] or List[str])
    item_repos = getattr(item, "supporting_repositories", None)
    if item_repos is None and isinstance(item, dict):
        item_repos = item.get("supporting_repositories")
    if item_repos:
        for r in item_repos:
            if isinstance(r, str):
                repos.append(r)
            elif hasattr(r, "name"):
                repos.append(r.name)
            elif isinstance(r, dict) and "name" in r:
                repos.append(r["name"])

    return list(dict.fromkeys(repos))


def _adapt_developer_input(
    developer_skills: Union[Sequence[Union[str, DeveloperSkill, Dict[str, Any]]], DeveloperProfileResponse, Any],
) -> tuple[Dict[str, _AdaptedSkill], List[str]]:
    """
    Internal adapter to normalize and extract metadata from diverse skill inputs
    (Sequence[str], DeveloperProfileResponse, Sequence[DeveloperSkill], or dicts).

    Returns:
        (canonical_map, dev_skills_list)
    """
    if developer_skills is None:
        return {}, []

    if isinstance(developer_skills, DeveloperProfileResponse) or hasattr(developer_skills, "skills"):
        skills_iterable = developer_skills.skills
    elif isinstance(developer_skills, str):
        skills_iterable = [developer_skills]
    else:
        try:
            skills_iterable = list(developer_skills)
        except TypeError:
            skills_iterable = [developer_skills]

    canonical_map: Dict[str, _AdaptedSkill] = {}
    dev_skills_list: List[str] = []

    status_rank = {"STRONG": 4, "MODERATE": 3, "WEAK": 2, "NONE_DETECTED": 1}

    for item in skills_iterable:
        if item is None:
            continue

        if isinstance(item, str):
            cleaned = item.strip()
            if not cleaned:
                continue
            canonical = normalize_technology_name(cleaned)
            if not canonical:
                continue
            if canonical not in canonical_map:
                canonical_map[canonical] = _AdaptedSkill(
                    name=canonical,
                    categories=_classify_technology(canonical),
                    sources=[],
                    evidence_status=None,
                    supporting_repositories=[],
                )
                dev_skills_list.append(canonical)
        else:
            # Rich object or dict (DeveloperSkill, dict)
            if isinstance(item, dict):
                raw_name = item.get("name") or item.get("skill") or ""
                categories = list(item.get("categories") or [])
                sources = list(item.get("sources") or [])
                evidence_status = item.get("evidence_status")
            else:
                raw_name = getattr(item, "name", None) or getattr(item, "skill", None) or ""
                categories = list(getattr(item, "categories", []) or [])
                sources = list(getattr(item, "sources", []) or [])
                evidence_status = getattr(item, "evidence_status", None)

            if not raw_name or not isinstance(raw_name, str):
                continue
            cleaned = raw_name.strip()
            if not cleaned:
                continue
            canonical = normalize_technology_name(cleaned)
            if not canonical:
                continue

            if not categories:
                categories = _classify_technology(canonical)

            repos = _extract_repo_names(item)

            if canonical in canonical_map:
                # Merge metadata safely without inflating counts
                existing = canonical_map[canonical]
                merged_sources = list(dict.fromkeys(existing.sources + sources))
                cur_rank = status_rank.get(existing.evidence_status or "", 0)
                new_rank = status_rank.get(evidence_status or "", 0)
                chosen_status = evidence_status if new_rank > cur_rank else existing.evidence_status
                merged_repos = list(dict.fromkeys(existing.supporting_repositories + repos))
                merged_cats = list(dict.fromkeys(existing.categories + categories))
                canonical_map[canonical] = _AdaptedSkill(
                    name=canonical,
                    categories=merged_cats,
                    sources=merged_sources,
                    evidence_status=chosen_status,
                    supporting_repositories=merged_repos,
                )
            else:
                canonical_map[canonical] = _AdaptedSkill(
                    name=canonical,
                    categories=categories,
                    sources=sources,
                    evidence_status=evidence_status,
                    supporting_repositories=repos,
                )
                dev_skills_list.append(canonical)

    return canonical_map, dev_skills_list


class JobMatchingService:
    """
    Deterministic service for matching extracted job description skills
    against developer skills or Unified Developer Profiles.
    """

    def match_job_description(
        self,
        job_description: str,
        developer_skills: Optional[Union[Sequence[Union[str, DeveloperSkill, Dict[str, Any]]], DeveloperProfileResponse, Any]] = None,
        extracted_skills: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Compare job description skills against a developer skill set or Unified Developer Profile.

        Args:
            job_description: Raw plain text of the job description.
            developer_skills: Optional list of skills, DeveloperSkill objects, or DeveloperProfileResponse.
            extracted_skills: Optional pre-extracted canonical skills (for direct testing).

        Returns:
            Dict matching JobMatchingResponse schema.
        """
        # 1. Extract skills from job description if not pre-supplied
        if extracted_skills is None:
            required_skills = job_description_service.extract_skills(job_description)
        else:
            # Normalize pre-supplied skills
            required_skills = sorted(list({
                normalize_technology_name(s)
                for s in extracted_skills
                if s and s.strip()
            }))

        total_required = len(required_skills)

        # 2. Adapt developer skills
        canonical_map, dev_skills_list = _adapt_developer_input(developer_skills)
        lower_to_canonical = {k.lower(): k for k in canonical_map}

        # 3. Compare required vs developer skills
        matched_skills: List[str] = []
        missing_skills: List[str] = []
        matched_skill_details: List[Dict[str, Any]] = []
        missing_skill_details: List[Dict[str, Any]] = []

        for req_skill in required_skills:
            matched_key = None
            if req_skill in canonical_map:
                matched_key = req_skill
            elif req_skill.lower() in lower_to_canonical:
                matched_key = lower_to_canonical[req_skill.lower()]

            if matched_key is not None:
                matched_skills.append(req_skill)
                dev_info = canonical_map[matched_key]
                cats = dev_info.categories if dev_info.categories else _classify_technology(req_skill)
                matched_skill_details.append(
                    {
                        "name": req_skill,
                        "categories": cats,
                        "sources": dev_info.sources,
                        "evidence_status": dev_info.evidence_status,
                        "supporting_repositories": dev_info.supporting_repositories,
                    }
                )
            else:
                missing_skills.append(req_skill)
                missing_skill_details.append(
                    {
                        "name": req_skill,
                        "categories": _classify_technology(req_skill),
                        "sources": [],
                        "evidence_status": None,
                        "supporting_repositories": [],
                    }
                )

        matched_count = len(matched_skills)
        missing_count = len(missing_skills)

        # Invariant check: matched + missing must equal total required
        assert matched_count + missing_count == total_required, (
            "Partition invariant violated: matched_count + missing_count != total_required"
        )

        # 4. Calculate deterministic match percentage
        if total_required > 0:
            match_percentage = round((matched_count / total_required) * 100.0, 2)
        else:
            match_percentage = 0.0

        # 5. Build explainability summary
        if total_required == 0:
            explanation = "No identifiable technical skills were detected in the job description."
        elif missing_count == 0:
            explanation = (
                f"Full skill match ({match_percentage}%): Developer possesses all {total_required} "
                "required technical skills."
            )
        else:
            missing_summary = ", ".join(missing_skills)
            explanation = (
                f"Candidate matches {matched_count} of {total_required} required skills "
                f"({match_percentage}% coverage). Skills not detected in profile: {missing_summary}."
            )

        # 6. Compute deterministic category breakdown
        category_stats: Dict[str, Dict[str, int]] = {
            cat_name: {"required": 0, "matched": 0, "missing": 0}
            for cat_name, _ in CATEGORY_DEFINITIONS
        }
        category_stats[FALLBACK_CATEGORY] = {"required": 0, "matched": 0, "missing": 0}

        matched_set = set(matched_skills)

        for req_skill in required_skills:
            skill_categories = _classify_technology(req_skill)
            is_matched = req_skill in matched_set
            for cat in skill_categories:
                if cat not in category_stats:
                    category_stats[cat] = {"required": 0, "matched": 0, "missing": 0}
                category_stats[cat]["required"] += 1
                if is_matched:
                    category_stats[cat]["matched"] += 1
                else:
                    category_stats[cat]["missing"] += 1

        category_breakdown: List[Dict[str, Any]] = []

        ordered_cat_names = [cat_name for cat_name, _ in CATEGORY_DEFINITIONS]
        if FALLBACK_CATEGORY not in ordered_cat_names:
            ordered_cat_names.append(FALLBACK_CATEGORY)

        for cat_name in ordered_cat_names:
            stats = category_stats.get(cat_name)
            if not stats:
                continue
            req_cnt = stats["required"]
            if req_cnt == 0:
                continue
            mat_cnt = stats["matched"]
            mis_cnt = stats["missing"]

            assert mat_cnt + mis_cnt == req_cnt, (
                f"Category invariant violated for '{cat_name}': {mat_cnt} + {mis_cnt} != {req_cnt}"
            )

            cov_pct = round((mat_cnt / req_cnt) * 100.0, 2) if req_cnt > 0 else 0.0

            category_breakdown.append(
                {
                    "category": cat_name,
                    "required_count": req_cnt,
                    "matched_count": mat_cnt,
                    "missing_count": mis_cnt,
                    "coverage_percentage": cov_pct,
                }
            )

        return {
            "extracted_skills": required_skills,
            "developer_skills": dev_skills_list,
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "total_required_skills": total_required,
            "matched_skill_count": matched_count,
            "missing_skill_count": missing_count,
            "match_percentage": match_percentage,
            "explanation": explanation,
            "matched_skill_details": matched_skill_details,
            "missing_skill_details": missing_skill_details,
            "category_breakdown": category_breakdown,
        }

    def match_profile_job_description(
        self,
        job_description: str,
        profile: DeveloperProfileResponse,
        extracted_skills: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Compare job description skills against a Unified Developer Profile.

        Args:
            job_description: Raw plain text of the job description.
            profile: DeveloperProfileResponse containing unified skills with
                     provenance, categories, and evidence.
            extracted_skills: Optional pre-extracted canonical skills.

        Returns:
            Dict matching JobMatchingResponse schema including evidence-aware
            matched details, missing skill categories, and category breakdown.
        """
        return self.match_job_description(
            job_description=job_description,
            developer_skills=profile,
            extracted_skills=extracted_skills,
        )


# Singleton instance for route and script usage
job_matching_service = JobMatchingService()
