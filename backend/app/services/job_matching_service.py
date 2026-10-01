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
"""

from typing import Any, Dict, List, Optional, Set

from app.services.job_description_service import (
    job_description_service,
)
from app.services.technology_service import normalize_technology_name


class JobMatchingService:
    """
    Deterministic service for matching extracted job description skills
    against developer skills.
    """

    def match_job_description(
        self,
        job_description: str,
        developer_skills: Optional[List[str]] = None,
        extracted_skills: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Compare job description skills against a developer skill set.

        Args:
            job_description: Raw plain text of the job description.
            developer_skills: Optional list of skills claimed or demonstrated by the developer.
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

        # 2. Normalize developer skills
        normalized_dev_skills: Set[str] = set()
        dev_skills_list: List[str] = []

        if developer_skills:
            for raw_skill in developer_skills:
                if not raw_skill or not isinstance(raw_skill, str):
                    continue
                normalized = normalize_technology_name(raw_skill)
                if normalized and normalized not in normalized_dev_skills:
                    normalized_dev_skills.add(normalized)
                    dev_skills_list.append(normalized)

        # 3. Compare required vs developer skills
        matched_skills = [
            skill for skill in required_skills
            if skill in normalized_dev_skills
        ]
        missing_skills = [
            skill for skill in required_skills
            if skill not in normalized_dev_skills
        ]

        matched_count = len(matched_skills)
        missing_count = len(missing_skills)

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
        }


# Singleton instance for route and script usage
job_matching_service = JobMatchingService()
