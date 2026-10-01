"""
evidence_service.py
-------------------
Service layer for Resume vs GitHub Evidence Analysis.

Compares skills claimed in a resume with skills verified and detected
from analyzed public GitHub repositories.

Classification rules:
- STRONG: Skill detected across multiple (>= 2) analyzed repositories.
- MODERATE: Skill detected in at least one (== 1) analyzed repository.
- NONE_DETECTED: Skill claimed on resume but not detected (== 0) in analyzed repositories.

NOTE: Missing GitHub evidence does NOT imply a candidate lacks skill or made a false claim.
"""

from typing import Any, Dict, List, Optional, Set

from app.schemas.evidence import (
    EvidenceAnalysisResponse,
    EvidenceItem,
    EvidenceSummary,
    SupportingRepository,
)
from app.services.github_service import (
    GitHubAPIError,
    GitHubUserNotFoundError,
    github_service,
)
from app.services.resume_service import resume_service
from app.services.technology_service import normalize_technology_name

EVIDENCE_LEVEL_STRONG = "STRONG"
EVIDENCE_LEVEL_MODERATE = "MODERATE"
EVIDENCE_LEVEL_NONE_DETECTED = "NONE_DETECTED"


class EvidenceService:
    """
    Deterministic service for evaluating resume skills against repository-level GitHub evidence.
    """

    def classify_evidence_level(self, repo_count: int) -> str:
        """
        Classify evidence level deterministically:
        - STRONG: Detected across multiple (>= 2) analyzed repositories.
        - MODERATE: Detected in at least one (== 1) analyzed repository.
        - NONE_DETECTED: Claimed in resume but not detected (== 0) in analyzed repositories.
        """
        if repo_count >= 2:
            return EVIDENCE_LEVEL_STRONG
        elif repo_count == 1:
            return EVIDENCE_LEVEL_MODERATE
        else:
            return EVIDENCE_LEVEL_NONE_DETECTED

    def extract_repository_skills(self, repo: Dict[str, Any]) -> List[str]:
        """
        Extract and normalize all technical skill signals from a single repository.
        """
        detected: Set[str] = set()

        # 1. Primary language
        language = repo.get("language")
        if language and isinstance(language, str) and language.strip():
            normalized_lang = normalize_technology_name(language)
            if normalized_lang:
                detected.add(normalized_lang)

        # 2. Repository topics
        topics = repo.get("topics") or []
        if isinstance(topics, list):
            for topic in topics:
                if isinstance(topic, str) and topic.strip():
                    normalized_topic = normalize_technology_name(topic)
                    if normalized_topic:
                        detected.add(normalized_topic)

        return sorted(list(detected))

    def normalize_resume_skills(
        self,
        resume_skills: Optional[List[str]] = None,
        resume_text: Optional[str] = None,
    ) -> List[str]:
        """
        Normalize and deduplicate resume skills preserving deterministic ordering.
        If resume_skills is empty/None and resume_text is provided, skills are extracted
        from resume_text via resume_service.
        """
        raw_skills: List[str] = []

        if resume_skills:
            raw_skills.extend(resume_skills)
        elif resume_text and resume_text.strip():
            parsed_resume = resume_service.analyze_resume(resume_text)
            raw_skills.extend(parsed_resume.get("skills", []))

        normalized_skills: List[str] = []
        seen: Set[str] = set()

        for skill in raw_skills:
            if not skill or not isinstance(skill, str):
                continue
            normalized = normalize_technology_name(skill)
            if normalized and normalized not in seen:
                seen.add(normalized)
                normalized_skills.append(normalized)

        return normalized_skills

    async def analyze_evidence(
        self,
        username: str,
        resume_skills: Optional[List[str]] = None,
        resume_text: Optional[str] = None,
        repositories: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Analyze claimed resume skills against verified GitHub repository evidence.

        Args:
            username: Target GitHub username.
            resume_skills: Optional list of skill names from resume.
            resume_text: Optional plain-text resume string.
            repositories: Optional pre-fetched repository list (for testing or offline analysis).

        Returns:
            Dict matching EvidenceAnalysisResponse schema.

        Raises:
            GitHubUserNotFoundError: If GitHub user does not exist.
            GitHubAPIError: If GitHub API returns rate limit, timeout, or failure.
        """
        clean_username = username.strip()

        # 1. Fetch repositories if not provided
        if repositories is None:
            repos = await github_service.get_user_repositories(clean_username)
        else:
            repos = repositories

        # 2. Normalize resume skills
        norm_resume_skills = self.normalize_resume_skills(
            resume_skills=resume_skills,
            resume_text=resume_text,
        )

        # 3. Analyze repository evidence
        supporting_repos_list: List[SupportingRepository] = []
        all_github_skills: Set[str] = set()

        for repo in repos:
            repo_skills = self.extract_repository_skills(repo)
            for skill in repo_skills:
                all_github_skills.add(skill)

            supporting_repos_list.append(
                SupportingRepository(
                    name=repo.get("name") or "",
                    full_name=repo.get("full_name"),
                    html_url=repo.get("html_url"),
                    skills_detected=repo_skills,
                )
            )

        sorted_github_skills = sorted(list(all_github_skills))

        # 4. Compare each resume skill with repository evidence
        evidence_items: List[Dict[str, Any]] = []
        skills_with_evidence_count = 0

        for skill in norm_resume_skills:
            # Find matching repositories for this skill
            matching_repos = [
                repo for repo in supporting_repos_list
                if skill in repo.skills_detected
            ]
            # Sort supporting repositories deterministically by name
            matching_repos.sort(key=lambda r: r.name.lower())

            repo_count = len(matching_repos)
            github_detected = repo_count > 0
            evidence_level = self.classify_evidence_level(repo_count)

            if github_detected:
                skills_with_evidence_count += 1

            evidence_items.append({
                "skill": skill,
                "resume_claimed": True,
                "github_detected": github_detected,
                "evidence_level": evidence_level,
                "supporting_repositories": [r.model_dump() for r in matching_repos],
            })

        # 5. Calculate summary metrics
        total_resume_skills = len(norm_resume_skills)
        skills_without_evidence_count = total_resume_skills - skills_with_evidence_count

        if total_resume_skills > 0:
            coverage_percentage = round(
                (skills_with_evidence_count / total_resume_skills) * 100, 2
            )
        else:
            coverage_percentage = 0.0

        summary = {
            "total_resume_skills": total_resume_skills,
            "skills_with_evidence": skills_with_evidence_count,
            "skills_without_evidence": skills_without_evidence_count,
            "evidence_coverage_percentage": coverage_percentage,
        }

        return {
            "github_username": clean_username,
            "resume_skills": norm_resume_skills,
            "github_skills": sorted_github_skills,
            "evidence_items": evidence_items,
            "summary": summary,
        }


# Singleton instance for route and script usage
evidence_service = EvidenceService()
