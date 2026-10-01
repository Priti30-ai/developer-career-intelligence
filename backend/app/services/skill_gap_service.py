"""
skill_gap_service.py
--------------------
Service layer for Skill Gap Analysis.

Compares a developer's current skill profile against the required skills
for a target career role, identifying matched and missing skills in a
deterministic, explainable manner.
"""

from typing import Any, Dict, List, Optional, Sequence
from app.services.career_role_service import (
    CareerRoleNotFoundError,
    career_role_service,
)
from app.services.technology_service import normalize_technology_name


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

    Metric Definition:
    Skill match percentage is strictly a deterministic skill-coverage metric
    indicating the fraction of predefined prerequisite skills identified.
    It does NOT measure depth of expertise, problem-solving proficiency,
    candidate employability, or guarantee career readiness.
    """

    def analyze_gap(
        self,
        target_role: str,
        current_skills: Sequence[str],
        custom_required_skills: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Analyze skill gap for a target role against current skills.

        Args:
            target_role: Role slug or display name (e.g., 'data-scientist' or 'Data Scientist').
            current_skills: List of technology or skill names possessed by the developer.
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

        # 1. Normalize current skills and build fast lookup structures
        normalized_current_set = set()
        normalized_current_lower = set()

        for raw_skill in current_skills:
            if not raw_skill or not isinstance(raw_skill, str):
                continue
            cleaned = raw_skill.strip()
            if not cleaned:
                continue
            normalized = normalize_technology_name(cleaned)
            if normalized:
                normalized_current_set.add(normalized)
                normalized_current_lower.add(normalized.lower())
            else:
                normalized_current_lower.add(cleaned.lower())

        # 2. Compare required skills against current skills (partition)
        matched_skills: List[str] = []
        missing_skills: List[str] = []

        for req_skill in required_skills:
            # Check exact canonical match or lowercase match
            if req_skill in normalized_current_set or req_skill.lower() in normalized_current_lower:
                matched_skills.append(req_skill)
            else:
                missing_skills.append(req_skill)

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
        }


# Singleton instance for route usage
skill_gap_service = SkillGapService()
