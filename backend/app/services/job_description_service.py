"""
job_description_service.py
--------------------------
Service layer for deterministic skill and technology extraction from Job Description text.

Reuses existing technology normalization and aliases from technology_service.py.
Avoids false substring matches using word boundaries and context checks for short tokens.
"""

import re
from typing import List, Set

from app.services.technology_service import (
    TECHNOLOGY_ALIASES,
    normalize_technology_name,
)

# Short ambiguous aliases that require extra context checks to avoid false positives in English text
SHORT_AMBIGUOUS_TOKENS = {"c", "r", "go"}


class JobDescriptionService:
    """
    Deterministic service for extracting and normalizing technical skills
    from job descriptions.
    """

    def __init__(self) -> None:
        # Pre-sort alias keys by descending length so longer, multi-word terms
        # (e.g. 'machine learning', 'artificial intelligence') match before abbreviations ('ml', 'ai')
        self._sorted_aliases: List[tuple[str, str]] = sorted(
            TECHNOLOGY_ALIASES.items(),
            key=lambda item: len(item[0]),
            reverse=True,
        )

    def extract_skills(self, text: str) -> List[str]:
        """
        Extract canonical, normalized skills from job description text.

        Args:
            text: Raw job description text string.

        Returns:
            Sorted list of unique normalized canonical skill names.
        """
        if not text or not isinstance(text, str) or not text.strip():
            return []

        detected: Set[str] = set()
        text_lower = text.lower()

        # 1. Match sorted aliases using boundary checks
        for alias, canonical in self._sorted_aliases:
            if canonical in detected:
                continue

            if alias in SHORT_AMBIGUOUS_TOKENS:
                # Use contextual checks for very short ambiguous tokens
                if self._match_short_token(alias, text, text_lower):
                    detected.add(canonical)
            else:
                # Use boundary check for standard tokens
                pattern = r"(?<![a-zA-Z0-9])" + re.escape(alias) + r"(?![a-zA-Z0-9])"
                if re.search(pattern, text_lower):
                    detected.add(canonical)

        # 2. Return sorted canonical skill list for deterministic ordering
        return sorted(list(detected))

    def _match_short_token(self, token: str, raw_text: str, lower_text: str) -> bool:
        """
        Check if a short token ('c', 'r', 'go') is used as a programming language
        rather than common English words ('to go', 'grade c', 'for a...').
        """
        if token == "go":
            # Matches 'golang', 'Go language', 'Go developer', 'Go programming', or standalone 'Go' in skill lists
            if re.search(r"\bgolang\b", lower_text):
                return True
            if re.search(r"\bgo\s+(?:developer|engineer|language|programming|code|backend)\b", lower_text):
                return True
            # Standalone capitalized 'Go' delimited by commas, slashes, or bullets (e.g. "Python, Go, Java")
            if re.search(r"(?:^|[\n,;|/•*\-])\s*Go\s*(?:$|[\n,;|/)\-])", raw_text):
                return True
            return False

        if token == "c":
            # Matches 'c/c++', 'c language', 'c programming', or standalone capitalized 'C' in lists
            if re.search(r"\bc\s*(?:language|programming|developer|engineer)\b", lower_text):
                return True
            if re.search(r"(?:^|[\n,;|/•*\-(])\s*C\s*(?:$|[\n,;|/)\-])", raw_text):
                return True
            return False

        if token == "r":
            # Matches 'r language', 'r programming', or standalone capitalized 'R' in lists (e.g. "Python/R", "R, Python")
            if re.search(r"\br\s*(?:language|programming|developer|scripting)\b", lower_text):
                return True
            if re.search(r"(?:^|[\n,;|/•*\-(])\s*R\s*(?:$|[\n,;|/)\-])", raw_text):
                return True
            return False

        return False


# Singleton instance for route and service usage
job_description_service = JobDescriptionService()
