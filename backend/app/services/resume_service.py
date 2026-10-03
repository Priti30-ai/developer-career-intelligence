"""
resume_service.py
-----------------
Service layer for plain-text resume analysis and deterministic information extraction.

Converts unstructured resume text into structured developer metadata:
- Section Detection (Summary, Skills, Education, Experience, Projects, Certifications, Achievements)
- Normalized Skill Extraction (reusing technology_service.normalize_technology_name)
- Structured Education, Experience, and Project representations
"""

import re
from typing import Any, Dict, List, Optional, Set, Tuple

from app.services.skill_profile_service import _classify_technology
from app.services.technology_service import (
    TECHNOLOGY_ALIASES,
    normalize_technology_name,
)

# ---------------------------------------------------------------------------
# Section Heading Definitions
# ---------------------------------------------------------------------------

SECTION_HEADINGS: Dict[str, Set[str]] = {
    "summary": {
        "summary",
        "professional summary",
        "profile",
        "professional profile",
        "objective",
        "career objective",
        "about me",
        "about",
    },
    "skills": {
        "skills",
        "technical skills",
        "technical skill",
        "key skills",
        "core competencies",
        "competencies",
        "technologies",
        "tech stack",
        "tools & technologies",
        "skills & tools",
        "skills & technologies",
        "skills and technologies",
        "programming skills",
        "technical proficiencies",
    },
    "education": {
        "education",
        "academic background",
        "academics",
        "educational qualifications",
        "academic qualifications",
        "qualifications",
    },
    "experience": {
        "experience",
        "work experience",
        "professional experience",
        "employment history",
        "internship",
        "internships",
        "work history",
        "practical experience",
    },
    "projects": {
        "projects",
        "academic projects",
        "key projects",
        "personal projects",
        "notable projects",
        "technical projects",
    },
    "certifications": {
        "certifications",
        "certificates",
        "certification",
        "licenses & certifications",
        "courses & certifications",
        "trainings & certifications",
    },
    "achievements": {
        "achievements",
        "accomplishments",
        "honors",
        "awards",
        "honors & awards",
        "key achievements",
        "extracurricular activities",
    },
}

# Regex to detect clean heading lines
HEADING_CLEAN_RE = re.compile(r"^[\s#*_\-=:]+|[\s#*_\-=:]+$")

# Date pattern for years
YEAR_RANGE_RE = re.compile(
    r"\b((?:19|20)\d{2})\b\s*(?:-|–|to)\s*(\b(?:19|20)\d{2}\b|present|current)",
    re.IGNORECASE,
)
SINGLE_YEAR_RE = re.compile(r"\b((?:19|20)\d{2})\b")

# Date pattern for month + year
MONTH_YEAR_RANGE_RE = re.compile(
    r"\b((?:(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+)?(?:19|20)\d{2})\s*(?:-|–|to)\s*((?:(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+)?(?:19|20)\d{2}|present|current)\b",
    re.IGNORECASE,
)

# Degree identification keywords
DEGREE_KEYWORDS = [
    "diploma",
    "bachelor",
    "b.e.",
    "b.tech",
    "btech",
    "b.s.",
    "b.sc",
    "master",
    "m.e.",
    "m.tech",
    "mtech",
    "m.s.",
    "m.sc",
    "ph.d",
    "phd",
    "associate",
    "hsc",
    "ssc",
]

# Role title identification keywords
ROLE_KEYWORDS = [
    "intern",
    "developer",
    "engineer",
    "analyst",
    "architect",
    "scientist",
    "specialist",
    "lead",
    "manager",
    "consultant",
    "assistant",
    "associate",
    "administrator",
    "trainee",
]


class ResumeService:
    """
    Deterministic service for parsing, extracting, and normalizing resume text.
    """

    def analyze_resume(self, resume_text: str) -> Dict[str, Any]:
        """
        Parse raw resume text into structured developer metadata.

        Args:
            resume_text: Raw plain-text string of the resume.

        Returns:
            Dict matching ResumeAnalysisResponse structure.
        """
        sections = self._extract_sections(resume_text)

        summary = self._parse_summary(sections.get("summary", []))
        skills = self._parse_skills(sections.get("skills", []), resume_text)
        education = self._parse_education(sections.get("education", []))
        experience = self._parse_experience(sections.get("experience", []))
        projects = self._parse_projects(sections.get("projects", []))
        certifications = self._parse_bullet_list(sections.get("certifications", []))
        achievements = self._parse_bullet_list(sections.get("achievements", []))

        categorized_skills = self._build_categorized_skills(
            skills_section_names=skills,
            projects=projects,
            experience=experience,
        )

        return {
            "summary": summary,
            "skills": skills,
            "education": education,
            "experience": experience,
            "projects": projects,
            "certifications": certifications,
            "achievements": achievements,
            "categorized_skills": categorized_skills,
            "skill_count": len(skills),
            "project_count": len(projects),
            "experience_count": len(experience),
        }

    def _extract_sections(self, text: str) -> Dict[str, List[str]]:
        """
        Split resume into section buckets based on recognized headings.
        Preserves blank lines within sections to separate distinct entry blocks.
        """
        sections: Dict[str, List[str]] = {}
        current_section: Optional[str] = None

        lines = text.replace("\r\n", "\n").split("\n")
        for raw_line in lines:
            line = raw_line.strip()
            if not line:
                # Keep a single blank line marker between entries
                if current_section and sections.get(current_section) and sections[current_section][-1] != "":
                    sections[current_section].append("")
                continue

            # Check if this line is a section heading
            heading_type = self._match_heading(line)
            if heading_type:
                current_section = heading_type
                if current_section not in sections:
                    sections[current_section] = []
                continue

            if current_section:
                sections[current_section].append(line)

        return sections

    def _match_heading(self, line: str) -> Optional[str]:
        """
        Check if a trimmed line is a recognized section heading.
        """
        # Strip decorative formatting: '#', '*', ':', '-', '='
        cleaned = HEADING_CLEAN_RE.sub("", line).strip().lower()

        # Headings must be reasonably short (<= 50 chars)
        if len(cleaned) > 50:
            return None

        for section_type, variants in SECTION_HEADINGS.items():
            if cleaned in variants:
                return section_type

        return None

    def _parse_summary(self, lines: List[str]) -> Optional[str]:
        """Join summary lines into a single coherent string."""
        filtered = [l for l in lines if l]
        if not filtered:
            return None
        text = " ".join(filtered).strip()
        return text if text else None

    def _parse_skills(self, skill_lines: List[str], full_text: str) -> List[str]:
        """
        Extract, normalize, and deduplicate skills from the skills section and full text.
        """
        extracted_skills: List[str] = []
        seen_skills: Set[str] = set()

        def add_skill(raw_name: str) -> None:
            if not raw_name or not isinstance(raw_name, str):
                return
            cleaned = raw_name.strip(" \t\r\n.,;:•*_-|/")
            if not cleaned:
                return
            normalized = normalize_technology_name(cleaned)
            if normalized and normalized not in seen_skills:
                seen_skills.add(normalized)
                extracted_skills.append(normalized)

        # 1. Parse explicitly listed items in the skills section
        for line in skill_lines:
            # If line has category prefix (e.g. "Languages: Python, Java"), strip prefix
            content = line
            if ":" in line:
                prefix, remainder = line.split(":", 1)
                if len(prefix.split()) <= 4:
                    content = remainder

            # Split tokens by common separators: comma, semicolon, pipe, bullets
            tokens = re.split(r"[,;|•/]+", content)
            for token in tokens:
                add_skill(token)

        # 2. Also scan for known canonical technologies mentioned in text
        # Compile multi-word known technologies to avoid missing terms
        known_multiwords = [
            "machine learning",
            "deep learning",
            "artificial intelligence",
            "computer vision",
            "natural language processing",
            "rest api",
            "react native",
            "scikit-learn",
            "data visualization",
        ]
        text_lower = full_text.lower()
        for mw in known_multiwords:
            if mw in text_lower:
                add_skill(mw)

        return extracted_skills

    def _parse_education(self, lines: List[str]) -> List[Dict[str, Any]]:
        """
        Parse education lines into structured ResumeEducation items.
        """
        if not lines:
            return []

        entries: List[Dict[str, Any]] = []
        # Group lines into blocks separated by blank lines or degree/institution starts
        blocks = self._group_entry_blocks(lines)

        for block in blocks:
            institution: Optional[str] = None
            degree: Optional[str] = None
            field_of_study: Optional[str] = None
            start_year: Optional[str] = None
            end_year: Optional[str] = None

            for line in block:
                # 1. Check for year range
                year_range = YEAR_RANGE_RE.search(line)
                if year_range:
                    start_year = year_range.group(1)
                    end_val = year_range.group(2)
                    end_year = end_val if end_val.lower() not in ("present", "current") else None
                    # If line only contained the year, continue
                    remaining = YEAR_RANGE_RE.sub("", line).strip(" \t\r\n,|-()")
                    if not remaining:
                        continue
                    line = remaining

                # 2. Check for degree keyword
                lower_line = line.lower()
                is_degree = any(kw in lower_line for kw in DEGREE_KEYWORDS)

                if is_degree:
                    # Attempt to split into degree and field_of_study if "in" or "of" is present
                    in_match = re.search(r"^(.*?)\s+(?:in|of)\s+(.*)$", line, re.IGNORECASE)
                    if in_match:
                        degree = in_match.group(1).strip(" \t,|-")
                        field_of_study = in_match.group(2).strip(" \t,|-")
                    else:
                        degree = line.strip(" \t,|-")
                elif not institution:
                    # Treat first non-degree line as institution
                    institution = line.strip(" \t,|-•*")

            if institution:
                entries.append({
                    "institution": institution,
                    "degree": degree,
                    "field_of_study": field_of_study,
                    "start_year": start_year,
                    "end_year": end_year,
                })
            elif degree:
                entries.append({
                    "institution": "Unknown Institution",
                    "degree": degree,
                    "field_of_study": field_of_study,
                    "start_year": start_year,
                    "end_year": end_year,
                })

        return entries

    def _parse_experience(self, lines: List[str]) -> List[Dict[str, Any]]:
        """
        Parse experience lines into structured ResumeExperience items.
        """
        if not lines:
            return []

        entries: List[Dict[str, Any]] = []
        blocks = self._group_entry_blocks(lines)

        for block in blocks:
            company: Optional[str] = None
            role: Optional[str] = None
            start_date: Optional[str] = None
            end_date: Optional[str] = None
            desc_lines: List[str] = []

            for line in block:
                # 1. Date extraction
                date_match = MONTH_YEAR_RANGE_RE.search(line)
                if date_match:
                    start_date = date_match.group(1).strip()
                    end_val = date_match.group(2).strip()
                    end_date = end_val if end_val.lower() not in ("present", "current") else None
                    line_rem = MONTH_YEAR_RANGE_RE.sub("", line).strip(" \t,|-()")
                    if not line_rem:
                        continue
                    line = line_rem

                # 2. Check for role keywords
                lower_line = line.lower()
                is_role = any(kw in lower_line for kw in ROLE_KEYWORDS)

                if is_role and not role:
                    role = line.strip(" \t,|-•*")
                elif not company and not is_role and len(line.split()) <= 6:
                    company = line.strip(" \t,|-•*")
                else:
                    desc_lines.append(line.strip(" \t•*_-"))

            if role or company:
                entries.append({
                    "company": company,
                    "role": role,
                    "start_date": start_date,
                    "end_date": end_date,
                    "description": " ".join(desc_lines) if desc_lines else None,
                })

        return entries

    def _parse_projects(self, lines: List[str]) -> List[Dict[str, Any]]:
        """
        Parse project lines into structured ResumeProject items.
        """
        if not lines:
            return []

        entries: List[Dict[str, Any]] = []
        blocks = self._group_entry_blocks(lines)

        for block in blocks:
            if not block:
                continue

            first_line = block[0].strip(" \t•*_-")
            # If project title contains description separated by colon or dash
            name = first_line
            description = None
            desc_lines: List[str] = []

            if ":" in first_line and len(first_line.split(":", 1)[0].split()) <= 6:
                name, desc_part = first_line.split(":", 1)
                name = name.strip()
                if desc_part.strip():
                    desc_lines.append(desc_part.strip())
            elif " - " in first_line and len(first_line.split(" - ", 1)[0].split()) <= 6:
                name, desc_part = first_line.split(" - ", 1)
                name = name.strip()
                if desc_part.strip():
                    desc_lines.append(desc_part.strip())

            if len(block) > 1:
                for line in block[1:]:
                    desc_lines.append(line.strip(" \t•*_-"))

            full_desc = " ".join(desc_lines).strip() if desc_lines else None

            # Detect mentioned technologies in project title and description
            combined_text = f"{name} {full_desc or ''}"
            detected_techs = self._detect_technologies_in_text(combined_text)

            entries.append({
                "name": name,
                "description": full_desc,
                "technologies": detected_techs,
            })

        return entries

    def _detect_technologies_in_text(self, text: str) -> List[str]:
        """
        Detect known canonical technologies mentioned in a text segment.
        """
        detected: List[str] = []
        seen: Set[str] = set()

        text_lower = text.lower()
        # Scan known aliases
        for alias, canonical in TECHNOLOGY_ALIASES.items():
            pattern = r"(?<![a-zA-Z0-9])" + re.escape(alias) + r"(?![a-zA-Z0-9])"
            if re.search(pattern, text_lower):
                if canonical not in seen:
                    seen.add(canonical)
                    detected.append(canonical)

        return detected

    def _build_categorized_skills(
        self,
        skills_section_names: List[str],
        projects: List[Dict[str, Any]],
        experience: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Build categorized skill entries with source provenance tracking.

        Reuses the shared taxonomy from skill_profile_service._classify_technology().
        Each entry captures:
          - canonical name  (already normalized by normalize_technology_name)
          - taxonomy categories (multi-category, from CATEGORY_DEFINITIONS)
          - resume sections where the skill was detected (source tracking)

        Source labels:
          skills_section  — explicitly listed in the SKILLS / TECHNICAL SKILLS section
                            (or detected by the full-text multi-word scan in _parse_skills)
          project_text    — detected via alias matching in project title/description
          experience_text — detected via alias matching in experience description text

        Deduplication:
          One canonical entry per technology regardless of how many sections mention it.
          If Python appears in skills + 2 projects + 1 experience entry, the result
          is one Python entry with sources ['experience_text', 'project_text', 'skills_section'].

        Ordering:
          Entries are sorted alphabetically by name for determinism.
          Sources within each entry are sorted alphabetically.

        Args:
            skills_section_names: Canonical names from _parse_skills() — already normalized.
            projects: Parsed project dicts each containing a 'technologies' List[str].
            experience: Parsed experience dicts each containing an optional 'description' str.

        Returns:
            List of dicts matching the ResumeSkill schema, sorted by name.
        """
        # name → set of source labels
        skill_sources: Dict[str, Set[str]] = {}

        # 1. Skills section (already normalized by _parse_skills)
        for name in skills_section_names:
            if name not in skill_sources:
                skill_sources[name] = set()
            skill_sources[name].add("skills_section")

        # 2. Project technologies (already detected by _detect_technologies_in_text
        #    inside _parse_projects — canonical names are pre-populated in each project dict)
        for project in projects:
            for tech in project.get("technologies", []):
                if tech not in skill_sources:
                    skill_sources[tech] = set()
                skill_sources[tech].add("project_text")

        # 3. Experience description technologies (deterministic alias scan)
        for exp in experience:
            desc = exp.get("description") or ""
            if desc.strip():
                for tech in self._detect_technologies_in_text(desc):
                    if tech not in skill_sources:
                        skill_sources[tech] = set()
                    skill_sources[tech].add("experience_text")

        # Assemble result: sorted by name for deterministic ordering
        result: List[Dict[str, Any]] = []
        for name in sorted(skill_sources.keys()):
            categories = _classify_technology(name)
            sources = sorted(skill_sources[name])  # alphabetical for determinism
            result.append({
                "name": name,
                "categories": categories,
                "sources": sources,
            })

        return result

    def _parse_bullet_list(self, lines: List[str]) -> List[str]:
        """Clean bulleted text lines into a list of strings."""
        items: List[str] = []
        for line in lines:
            cleaned = line.strip(" \t•*_-1234567890.)")
            if cleaned:
                items.append(cleaned)
        return items

    def _group_entry_blocks(self, lines: List[str]) -> List[List[str]]:
        """
        Group lines into entry blocks separated by empty lines or explicit bullets.
        """
        blocks: List[List[str]] = []
        current_block: List[str] = []

        for line in lines:
            if not line:
                if current_block:
                    blocks.append(current_block)
                    current_block = []
                continue

            # If line starts with a bullet point and we already have lines in block, start new block
            is_bullet = line.startswith(("•", "-", "*")) or bool(re.match(r"^\d+\.", line))

            if is_bullet and current_block:
                blocks.append(current_block)
                current_block = [line]
            else:
                current_block.append(line)

        if current_block:
            blocks.append(current_block)

        return blocks


# Singleton instance for route usage
resume_service = ResumeService()
