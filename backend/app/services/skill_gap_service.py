"""
skill_gap_service.py
--------------------
Service layer for Skill Gap Analysis.

Compares a developer's current skill profile (either legacy flat string list
or Unified Developer Profile) against the required skills for a target career
role, identifying matched and missing skills in a deterministic, explainable,
and evidence-aware manner.
"""

from typing import Any, Dict, List, Optional, Sequence, Union

from app.schemas.developer_profile import DeveloperProfileResponse, DeveloperSkill
from app.services.career_role_service import (
    CareerRoleNotFoundError,
    career_role_service,
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
    current_skills: Union[Sequence[Union[str, DeveloperSkill, Dict[str, Any]]], DeveloperProfileResponse, Any],
) -> Dict[str, _AdaptedSkill]:
    """
    Internal adapter to normalize and extract metadata from diverse skill inputs
    (Sequence[str], DeveloperProfileResponse, Sequence[DeveloperSkill], or dicts).

    Returns a mapping of canonical_skill_name -> _AdaptedSkill.
    """
    if current_skills is None:
        return {}

    if isinstance(current_skills, DeveloperProfileResponse) or hasattr(current_skills, "skills"):
        skills_iterable = current_skills.skills
    elif isinstance(current_skills, str):
        skills_iterable = [current_skills]
    else:
        try:
            skills_iterable = list(current_skills)
        except TypeError:
            skills_iterable = [current_skills]

    canonical_map: Dict[str, _AdaptedSkill] = {}

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

    return canonical_map


class SkillGapService:
    """
    Evaluates skill gaps between a developer's skills and a target role.

    Comparison Logic:
    1. Look up role definition via CareerRoleService.
       If not found, raises CareerRoleNotFoundError.
    2. Normalize all user-supplied current skills using normalize_technology_name
       to resolve casing differences and common aliases (e.g. 'nodejs' -> 'Node.js').
    3. Partition role required skills into matched vs missing:
       - matched: required skill is found in normalized current skills
       - missing: required skill is NOT found in normalized current skills
    4. Calculate skill match percentage:
       Formula: round((total_matched_skills / total_required_skills) * 100, 2)
       If total_required_skills == 0, returns 0.0 (safe division guard).
    5. Populate matched_skill_details and missing_skill_details with taxonomy
       and provenance metadata.
    6. Compute category-level requirement, match, and coverage statistics.

    Metric Definition:
    Skill match percentage is strictly a deterministic skill-coverage metric
    indicating the fraction of predefined prerequisite skills identified.
    It does NOT measure depth of expertise, problem-solving proficiency,
    candidate employability, or guarantee career readiness.
    """

    def analyze_gap(
        self,
        target_role: str,
        current_skills: Union[Sequence[Union[str, DeveloperSkill, Dict[str, Any]]], DeveloperProfileResponse, Any],
        custom_required_skills: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Analyze skill gap for a target role against current skills or profile.

        Args:
            target_role: Role slug or display name (e.g., 'data-scientist' or 'Data Scientist').
            current_skills: Sequence of skills (strings, DeveloperSkill objects) or DeveloperProfileResponse.
            custom_required_skills: Optional override for required skills (used for custom testing).

        Returns:
            Dict containing:
                - target_role: Human-readable role title
                - role_slug: Normalized role slug
                - total_required_skills: int
                - total_matched_skills: int
                - total_missing_skills: int
                - skill_match_percentage: float (0.0 to 100.0)
                - match_percentage: float (alias for backward compatibility)
                - matched_skills: List of matched canonical skill names
                - missing_skills: List of missing canonical skill names
                - matched_skill_details: List of dicts for matched skills
                - missing_skill_details: List of dicts for missing skills
                - category_breakdown: List of category coverage statistics

        Raises:
            CareerRoleNotFoundError: If the target role cannot be resolved.
        """
        if custom_required_skills is not None:
            role_display_name = target_role.strip()
            role_slug = target_role.strip().lower().replace(" ", "-")
            required_skills = [
                normalize_technology_name(s) for s in custom_required_skills if s and s.strip()
            ]
        else:
            role_defn = career_role_service.get_role(target_role)
            if not role_defn:
                raise CareerRoleNotFoundError(f"Target career role '{target_role}' is not supported.")
            role_display_name = role_defn["display_name"]
            role_slug = role_defn["slug"]
            required_skills = role_defn["required_skills"]

        # 1. Adapt and normalize current developer skills
        canonical_map = _adapt_developer_input(current_skills)
        lower_to_canonical = {k.lower(): k for k in canonical_map}

        # 2. Compare required skills against current skills (partition)
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

        # 3. Compute deterministic metrics
        total_required = len(required_skills)
        total_matched = len(matched_skills)
        total_missing = len(missing_skills)

        # Invariant check: matched + missing must equal total required
        assert total_matched + total_missing == total_required, (
            "Partition invariant violated: total_matched + total_missing != total_required"
        )

        if total_required > 0:
            percentage = round((total_matched / total_required) * 100.0, 2)
        else:
            percentage = 0.0

        # 4. Compute deterministic category breakdown
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
            "target_role": role_display_name,
            "role_slug": role_slug,
            "total_required_skills": total_required,
            "total_matched_skills": total_matched,
            "total_missing_skills": total_missing,
            "skill_match_percentage": percentage,
            "match_percentage": percentage,
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "matched_skill_details": matched_skill_details,
            "missing_skill_details": missing_skill_details,
            "category_breakdown": category_breakdown,
        }

    def analyze_profile_gap(
        self,
        profile: DeveloperProfileResponse,
        target_role: str,
    ) -> Dict[str, Any]:
        """
        Analyze skill gap for a target role against a Unified Developer Profile.

        Args:
            profile: DeveloperProfileResponse containing unified skills with
                     provenance, categories, and evidence.
            target_role: Target career role slug or title.

        Returns:
            Dict containing complete skill gap metrics, matched/missing skills,
            rich evidence-aware matched skill details, missing skill details,
            and category breakdown.
        """
        return self.analyze_gap(
            target_role=target_role,
            current_skills=profile,
        )


# Singleton instance for route usage
skill_gap_service = SkillGapService()

