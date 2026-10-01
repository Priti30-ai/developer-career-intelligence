"""
developer_profile_service.py
----------------------------
Service layer for Unified Developer Profile Synthesis.

Combines signals from:
1. GitHub repository analysis (languages, topics, verified code artifacts)
2. Resume analysis (claimed skills, education, experience, projects)
3. Evidence analysis (repository backing, evidence classification levels)

Produces a canonical, unified developer profile suitable for downstream intelligence
modules (Job Description Matching, Skill Gap Analysis, Career Recommendations,
and UI dashboard consumption).

Determinism & Semantics:
- Canonical skill names are normalized using the project's technology service.
- Origin sources ('github', 'resume', or both) are explicitly tracked for every skill.
- Evidence status ('STRONG', 'MODERATE', 'NONE_DETECTED') reflects verified GitHub evidence.
- A skill existing only on the resume with 'NONE_DETECTED' evidence status reflects
  the absence of analyzed GitHub repository evidence, NOT proof that the candidate lacks the skill.
"""

from typing import Any, Dict, List, Optional, Set, Union

from app.schemas.developer_profile import (
    SOURCE_GITHUB,
    SOURCE_RESUME,
    DeveloperProfileResponse,
    DeveloperProfileSummary,
    DeveloperSkill,
    GitHubSummary,
    ResumeSummary,
)
from app.schemas.evidence import SupportingRepository
from app.schemas.resume import (
    ResumeEducation,
    ResumeExperience,
    ResumeProject,
)
from app.services.evidence_service import (
    EVIDENCE_LEVEL_MODERATE,
    EVIDENCE_LEVEL_NONE_DETECTED,
    EVIDENCE_LEVEL_STRONG,
    evidence_service,
)
from app.services.github_service import (
    GitHubAPIError,
    GitHubUserNotFoundError,
    github_service,
)
from app.services.resume_service import resume_service
from app.services.technology_service import normalize_technology_name


class DeveloperProfileService:
    """
    Deterministic synthesis service for building a Unified Developer Profile.
    """

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
    ) -> Dict[str, Any]:
        """
        Synthesize a unified developer profile by aggregating GitHub repositories
        and resume data.

        Args:
            username: Target developer GitHub username.
            resume_text: Optional plain-text resume content.
            resume_skills: Optional explicit list of resume skills.
            repositories: Optional pre-fetched repository list (for testing or offline use).

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

        # 1. Fetch GitHub repositories if not provided
        if repositories is None:
            repos = await github_service.get_user_repositories(clean_username)
        else:
            repos = repositories

        # 2. Extract repository skills and build supporting repository instances
        supporting_repos_list: List[SupportingRepository] = []
        github_skill_to_repos: Dict[str, List[SupportingRepository]] = {}

        for repo in repos:
            repo_skills = evidence_service.extract_repository_skills(repo)
            repo_model = SupportingRepository(
                name=repo.get("name") or "",
                full_name=repo.get("full_name"),
                html_url=repo.get("html_url"),
                skills_detected=repo_skills,
            )
            supporting_repos_list.append(repo_model)

            for skill in repo_skills:
                if skill not in github_skill_to_repos:
                    github_skill_to_repos[skill] = []
                github_skill_to_repos[skill].append(repo_model)

        all_github_skills = sorted(list(github_skill_to_repos.keys()))

        # 3. Parse resume or normalize provided resume skills
        resume_summary_data: Dict[str, Any] = {
            "summary": None,
            "skills": [],
            "education": [],
            "experience": [],
            "projects": [],
            "certifications": [],
            "achievements": [],
        }

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
        elif resume_skills:
            norm_res_skills = self.normalize_skills(resume_skills)
            resume_summary_data["skills"] = norm_res_skills

        resume_skill_set: Set[str] = set(resume_summary_data["skills"])

        # 4. Merge skills, determine sources, and attach evidence
        all_canonical_skills = sorted(
            list(set(all_github_skills) | resume_skill_set),
            key=lambda s: s.lower(),
        )

        unified_skills: List[DeveloperSkill] = []
        for skill in all_canonical_skills:
            in_github = skill in github_skill_to_repos
            in_resume = skill in resume_skill_set

            sources: List[str] = []
            if in_github:
                sources.append(SOURCE_GITHUB)
            if in_resume:
                sources.append(SOURCE_RESUME)

            # Get supporting repositories and sort them deterministically by name
            matching_repos = github_skill_to_repos.get(skill, [])
            sorted_matching_repos = sorted(matching_repos, key=lambda r: r.name.lower())

            repo_count = len(sorted_matching_repos)
            if repo_count >= 2:
                evidence_status = EVIDENCE_LEVEL_STRONG
            elif repo_count == 1:
                evidence_status = EVIDENCE_LEVEL_MODERATE
            else:
                evidence_status = EVIDENCE_LEVEL_NONE_DETECTED

            unified_skills.append(
                DeveloperSkill(
                    skill=skill,
                    sources=sources,
                    evidence_status=evidence_status,
                    supporting_repositories=sorted_matching_repos,
                )
            )

        # 5. Compute deterministic summary statistics
        total_skills = len(unified_skills)
        github_skill_count = len(all_github_skills)
        resume_skill_count = len(resume_skill_set)
        skills_from_both_sources = len(set(all_github_skills) & resume_skill_set)
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
            supported_skill_count=supported_skill_count,
            skills_without_github_evidence=skills_without_github_evidence,
        )

        github_summary = GitHubSummary(
            username=clean_username,
            repositories_analyzed=len(repos),
            technologies_detected=all_github_skills,
        )

        resume_summary = ResumeSummary(**resume_summary_data)

        response = DeveloperProfileResponse(
            developer_id=clean_username,
            github=github_summary,
            resume=resume_summary,
            skills=unified_skills,
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
