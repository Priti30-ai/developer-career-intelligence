"""
career_role_service.py
----------------------
Defines the canonical set of supported career roles and the required
normalized skill names for each role.

Design rules:
- All skill names use the canonical forms aligned with technology_service.py.
- Role slugs are stored in lowercase with hyphens for URL-safety.
- Role lookup supports slugs (e.g. 'data-scientist') as well as display names
  (e.g. 'Data Scientist').
"""

from typing import Any, Dict, List, Optional


class CareerRoleNotFoundError(Exception):
    """Raised when a requested career role is not defined."""
    pass


# ---------------------------------------------------------------------------
# Canonical Role Definitions
# ---------------------------------------------------------------------------

ROLE_DEFINITIONS: Dict[str, Dict[str, Any]] = {
    "data-scientist": {
        "display_name": "Data Scientist",
        "description": "Analyzes complex data to extract insights and build predictive models.",
        "required_skills": [
            "Python",
            "SQL",
            "Pandas",
            "NumPy",
            "Scikit-learn",
            "Machine Learning",
            "Data Visualization",
            "Statistics",
        ],
    },
    "machine-learning-engineer": {
        "display_name": "Machine Learning Engineer",
        "description": "Designs, builds, and deploys machine learning models into production systems.",
        "required_skills": [
            "Python",
            "SQL",
            "Machine Learning",
            "Deep Learning",
            "TensorFlow",
            "PyTorch",
            "Docker",
            "MLOps",
        ],
    },
    "ai-engineer": {
        "display_name": "AI Engineer",
        "description": "Develops intelligent systems, NLP/LLM pipelines, and AI-driven applications.",
        "required_skills": [
            "Python",
            "Machine Learning",
            "Deep Learning",
            "NLP",
            "LLM",
            "TensorFlow",
            "PyTorch",
            "Docker",
            "REST API",
        ],
    },
    "data-analyst": {
        "display_name": "Data Analyst",
        "description": "Inspects, cleans, and models data to uncover trends and inform decision making.",
        "required_skills": [
            "Python",
            "SQL",
            "Pandas",
            "NumPy",
            "Data Visualization",
            "Statistics",
            "Excel",
        ],
    },
    "backend-developer": {
        "display_name": "Backend Developer",
        "description": "Builds robust server-side APIs, database architectures, and core application services.",
        "required_skills": [
            "Python",
            "SQL",
            "REST API",
            "Docker",
            "PostgreSQL",
            "Git",
            "Linux",
        ],
    },
    "full-stack-developer": {
        "display_name": "Full Stack Developer",
        "description": "Develops both user-facing client applications and backend APIs and databases.",
        "required_skills": [
            "JavaScript",
            "TypeScript",
            "HTML",
            "CSS",
            "React",
            "Node.js",
            "SQL",
            "REST API",
            "Docker",
            "Git",
        ],
    },
}


class CareerRoleService:
    """
    Service for querying career role definitions.

    All role lookups are case-insensitive and support both slug and display name formats.
    """

    def list_roles(self) -> List[Dict[str, Any]]:
        """
        Return a summary list of all supported roles.

        Returns:
            List of dicts with 'slug', 'display_name', and 'required_skill_count'.
        """
        return [
            {
                "slug": slug,
                "display_name": defn["display_name"],
                "description": defn["description"],
                "required_skill_count": len(defn["required_skills"]),
            }
            for slug, defn in ROLE_DEFINITIONS.items()
        ]

    def get_role(self, role_identifier: str) -> Optional[Dict[str, Any]]:
        """
        Return the full role definition for the given slug or display name.

        Args:
            role_identifier: Role slug (e.g. 'data-scientist') or display name
                             (e.g. 'Data Scientist').

        Returns:
            Dict with 'slug', 'display_name', 'description', and 'required_skills',
            or None if the role is not found.
        """
        if not role_identifier or not isinstance(role_identifier, str):
            return None

        clean = role_identifier.strip().lower()

        # 1. Exact slug match
        if clean in ROLE_DEFINITIONS:
            defn = ROLE_DEFINITIONS[clean]
            return {
                "slug": clean,
                "display_name": defn["display_name"],
                "description": defn["description"],
                "required_skills": list(defn["required_skills"]),
            }

        # 2. Match with spaces converted to hyphens
        hyphenated = clean.replace(" ", "-").replace("_", "-")
        if hyphenated in ROLE_DEFINITIONS:
            defn = ROLE_DEFINITIONS[hyphenated]
            return {
                "slug": hyphenated,
                "display_name": defn["display_name"],
                "description": defn["description"],
                "required_skills": list(defn["required_skills"]),
            }

        # 3. Match against display names
        for slug, defn in ROLE_DEFINITIONS.items():
            if defn["display_name"].lower() == clean:
                return {
                    "slug": slug,
                    "display_name": defn["display_name"],
                    "description": defn["description"],
                    "required_skills": list(defn["required_skills"]),
                }

        return None

    def get_required_skills(self, role_identifier: str) -> Optional[List[str]]:
        """
        Return only the required-skill list for a role.

        Args:
            role_identifier: Role slug or display name.

        Returns:
            List of canonical skill names, or None if role not found.
        """
        role = self.get_role(role_identifier)
        return role["required_skills"] if role else None

    def is_valid_role(self, role_identifier: str) -> bool:
        """Return True if the role identifier maps to a known role."""
        return self.get_role(role_identifier) is not None


# Singleton instance for route and service usage
career_role_service = CareerRoleService()
