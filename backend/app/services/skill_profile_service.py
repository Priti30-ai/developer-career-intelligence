from typing import Any, Dict, List, Set

# ---------------------------------------------------------------------------
# Category definitions
# Each set contains the canonical technology names (after normalization)
# that belong to that category. A technology may appear in multiple sets.
# ---------------------------------------------------------------------------

PROGRAMMING_LANGUAGES: Set[str] = {
    "Python", "JavaScript", "TypeScript", "Java", "C", "C++", "C#",
    "Go", "Rust", "PHP", "Ruby", "Kotlin", "Swift", "Dart", "R",
    "Scala", "Haskell", "Lua", "Perl", "Shell", "Bash", "PowerShell",
    "Objective-C", "MATLAB", "Groovy", "Elixir", "Erlang", "Clojure",
    "F#", "SQL",
}

FRAMEWORKS_AND_LIBRARIES: Set[str] = {
    "React", "Angular", "Vue.js", "React Native", "Next.js", "NestJS",
    "Node.js", "Express", "Django", "Flask", "FastAPI", "Spring",
    "Spring Boot", "Gin", "Fiber", "Actix Web", "Tokio", "Axios",
    "Laravel", "Rails", "Symfony", "ASP.NET", ".NET", "jQuery",
    "Bootstrap", "Tailwind CSS", "Redux", "Svelte", "Nuxt.js",
    "TensorFlow", "TensorFlow.js", "PyTorch", "Keras", "Scikit-learn", "Pandas",
    "NumPy", "OpenCV", "Hugging Face", "LangChain", "Prisma", "SQLAlchemy",
    "Hibernate",
}

AI_MACHINE_LEARNING: Set[str] = {
    "Machine Learning", "Deep Learning", "Artificial Intelligence",
    "NLP", "Computer Vision", "Generative AI", "LLM",
    "TensorFlow", "TensorFlow.js", "PyTorch", "Scikit-learn", "Keras", "Pandas", "NumPy",
    "Data Science", "Neural Network", "Reinforcement Learning",
    "Natural Language Processing", "SciPy", "Matplotlib", "Seaborn",
}

WEB_TECHNOLOGIES: Set[str] = {
    "HTML", "CSS", "Bootstrap", "Tailwind CSS", "REST API", "GraphQL",
    "Web Development", "Web Design", "API", "JSON", "XML",
    "WebSockets", "Progressive Web App", "Webpack", "Vite", "Axios",
}

DATABASES: Set[str] = {
    "MySQL", "PostgreSQL", "MongoDB", "SQLite", "Redis", "Oracle",
    "SQL", "MariaDB", "Cassandra", "DynamoDB", "Elasticsearch",
    "Neo4j", "InfluxDB", "Firebase", "Prisma", "SQLAlchemy", "Alembic",
}

DEVOPS_AND_CLOUD: Set[str] = {
    "Docker", "Kubernetes", "AWS", "Azure", "GCP", "Google Cloud",
    "GitHub Actions", "CI/CD", "Terraform", "Ansible", "Jenkins",
    "Git", "GitHub", "Linux", "Nginx", "Apache", "Heroku",
    "Vercel", "Netlify", "DigitalOcean", "RabbitMQ", "Apache Kafka",
    "Cargo", "Maven", "Gradle",
}

TESTING_AND_QA: Set[str] = {
    "JUnit", "Pytest", "Jest", "Mocha",
}

# Ordered list of (category_name, category_set) used for classification.
# The order controls which categories appear first in the response.
CATEGORY_DEFINITIONS: List[tuple] = [
    ("Programming Languages", PROGRAMMING_LANGUAGES),
    ("Frameworks & Libraries", FRAMEWORKS_AND_LIBRARIES),
    ("AI / Machine Learning", AI_MACHINE_LEARNING),
    ("Web Technologies", WEB_TECHNOLOGIES),
    ("Databases", DATABASES),
    ("DevOps & Cloud", DEVOPS_AND_CLOUD),
    ("Testing & QA", TESTING_AND_QA),
]

FALLBACK_CATEGORY = "Tools & Other"


def _classify_technology(name: str) -> List[str]:
    """
    Return a list of category names that the technology belongs to.

    A technology may belong to multiple categories (e.g. TensorFlow belongs
    to both 'Frameworks & Libraries' and 'AI / Machine Learning').
    If no category matches, returns ['Tools & Other'].
    """
    matched: List[str] = [
        category_name
        for category_name, category_set in CATEGORY_DEFINITIONS
        if name in category_set
    ]
    return matched if matched else [FALLBACK_CATEGORY]


class SkillProfileService:
    """
    Service to convert extracted technologies into a categorized skill profile.

    Reuses technology data produced by TechnologyService — does not
    re-fetch repositories or re-normalize technology names.
    """

    def build_skill_profile(
        self,
        technologies: List[Dict[str, Any]],
        total_repositories: int,
    ) -> Dict[str, Any]:
        """
        Classify normalized technologies into skill categories.

        Args:
            technologies: List of {'name': str, 'repository_count': int} dicts
                          from TechnologyService.extract_technologies().
            total_repositories: Total repositories analyzed (passed through).

        Returns:
            Dict suitable for constructing SkillProfileResponse, containing:
                - categories: List of {'category': str, 'skills': [...]}
                - total_repositories: int
                - total_unique_technologies: int
        """
        # category_name → {skill_name → repository_count}
        category_buckets: Dict[str, Dict[str, int]] = {
            category_name: {}
            for category_name, _ in CATEGORY_DEFINITIONS
        }
        category_buckets[FALLBACK_CATEGORY] = {}

        for tech in technologies:
            name: str = tech["name"]
            count: int = tech["repository_count"]
            matched_categories = _classify_technology(name)
            for category_name in matched_categories:
                category_buckets[category_name][name] = count

        # Build ordered category list; skip empty categories
        categories: List[Dict[str, Any]] = []
        for category_name, _ in CATEGORY_DEFINITIONS:
            skills_dict = category_buckets[category_name]
            if not skills_dict:
                continue
            categories.append({
                "category": category_name,
                "skills": _sort_skills(skills_dict),
            })

        # Append fallback category last if it has entries
        fallback_skills = category_buckets[FALLBACK_CATEGORY]
        if fallback_skills:
            categories.append({
                "category": FALLBACK_CATEGORY,
                "skills": _sort_skills(fallback_skills),
            })

        return {
            "categories": categories,
            "total_repositories": total_repositories,
            "total_unique_technologies": len(technologies),
        }


def _sort_skills(skills_dict: Dict[str, int]) -> List[Dict[str, Any]]:
    """Sort skills by repository_count descending, then name ascending."""
    return [
        {"name": name, "repository_count": count}
        for name, count in sorted(
            skills_dict.items(), key=lambda item: (-item[1], item[0])
        )
    ]


# Singleton instance for route usage
skill_profile_service = SkillProfileService()
