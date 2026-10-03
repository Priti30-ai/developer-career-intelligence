from collections import Counter
from typing import Any, Dict, List, Set

# Known technology aliases and canonical naming map
TECHNOLOGY_ALIASES: Dict[str, str] = {
    # Programming Languages
    "python": "Python",
    "javascript": "JavaScript",
    "js": "JavaScript",
    "typescript": "TypeScript",
    "ts": "TypeScript",
    "c++": "C++",
    "cpp": "C++",
    "c#": "C#",
    "csharp": "C#",
    "c": "C",
    "go": "Go",
    "golang": "Go",
    "rust": "Rust",
    "java": "Java",
    "kotlin": "Kotlin",
    "swift": "Swift",
    "ruby": "Ruby",
    "php": "PHP",
    "r": "R",
    "dart": "Dart",
    "html": "HTML",
    "html5": "HTML",
    "css": "CSS",
    "css3": "CSS",
    "sql": "SQL",

    # Web & Backend Frameworks
    "nodejs": "Node.js",
    "node.js": "Node.js",
    "node": "Node.js",
    "react": "React",
    "reactjs": "React",
    "react.js": "React",
    "react-native": "React Native",
    "vue": "Vue.js",
    "vuejs": "Vue.js",
    "vue.js": "Vue.js",
    "angular": "Angular",
    "angularjs": "Angular",
    "next": "Next.js",
    "nextjs": "Next.js",
    "next.js": "Next.js",
    "nestjs": "NestJS",
    "express": "Express",
    "expressjs": "Express",
    "fastapi": "FastAPI",
    "flask": "Flask",
    "django": "Django",
    "spring": "Spring",
    "spring-boot": "Spring Boot",
    "springboot": "Spring Boot",
    "gin": "Gin",
    "fiber": "Fiber",
    "actix-web": "Actix Web",
    "tokio": "Tokio",
    "graphql": "GraphQL",
    "rest-api": "REST API",
    "api": "API",
    "vite": "Vite",
    "axios": "Axios",
    "tailwind": "Tailwind CSS",
    "tailwindcss": "Tailwind CSS",
    "redux": "Redux",

    # AI / Machine Learning / Data Science
    "machine-learning": "Machine Learning",
    "machine learning": "Machine Learning",
    "ml": "Machine Learning",
    "deep-learning": "Deep Learning",
    "deep learning": "Deep Learning",
    "dl": "Deep Learning",
    "artificial-intelligence": "Artificial Intelligence",
    "artificial intelligence": "Artificial Intelligence",
    "ai": "Artificial Intelligence",
    "tensorflow": "TensorFlow",
    "tensorflow.js": "TensorFlow.js",
    "@tensorflow/tfjs": "TensorFlow.js",
    "pytorch": "PyTorch",
    "torch": "PyTorch",
    "scikit-learn": "Scikit-learn",
    "sklearn": "Scikit-learn",
    "pandas": "Pandas",
    "numpy": "NumPy",
    "scipy": "SciPy",
    "matplotlib": "Matplotlib",
    "seaborn": "Seaborn",
    "keras": "Keras",
    "nlp": "NLP",
    "computer-vision": "Computer Vision",
    "llm": "LLM",

    # DevOps, Databases & Cloud
    "docker": "Docker",
    "kubernetes": "Kubernetes",
    "k8s": "Kubernetes",
    "postgresql": "PostgreSQL",
    "postgres": "PostgreSQL",
    "mongodb": "MongoDB",
    "mysql": "MySQL",
    "redis": "Redis",
    "sqlite": "SQLite",
    "prisma": "Prisma",
    "sqlalchemy": "SQLAlchemy",
    "alembic": "Alembic",
    "git": "Git",
    "github": "GitHub",
    "linux": "Linux",
    "nginx": "Nginx",
    "apache": "Apache",
    "aws": "AWS",
    "gcp": "GCP",
    "azure": "Azure",
    "rabbitmq": "RabbitMQ",
    "kafka": "Apache Kafka",

    # Testing & Tooling
    "pytest": "Pytest",
    "jest": "Jest",
    "mocha": "Mocha",
    "junit": "JUnit",
    "pydantic": "Pydantic",
    "celery": "Celery",
    "httpx": "HTTPX",
    "requests": "Requests",
    "cargo": "Cargo",
    "maven": "Maven",
    "gradle": "Gradle",
}


def normalize_technology_name(raw_name: str) -> str:
    """
    Normalize technology name using known aliases or standard formatting.

    Examples:
        'python' -> 'Python'
        'nodejs' -> 'Node.js'
        'web-development' -> 'Web Development'
    """
    cleaned = raw_name.strip()
    if not cleaned:
        return ""

    key = cleaned.lower()
    if key in TECHNOLOGY_ALIASES:
        return TECHNOLOGY_ALIASES[key]

    # Convert hyphenated or underscore-separated words into title case
    words = cleaned.replace("-", " ").replace("_", " ").split()
    return " ".join(word.capitalize() for word in words)


class TechnologyService:
    """Service to extract, normalize, and aggregate technology signals from repositories."""

    def extract_technologies(self, repositories: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Extract normalized technology signals and count occurrences across repositories.

        Each technology is counted at most once per repository.

        Args:
            repositories: List of repository dicts (from GitHubService).

        Returns:
            Dict containing:
                - technologies: List of dicts with 'name' and 'repository_count'
                - total_repositories: Total number of analyzed repositories
        """
        tech_counts: Counter[str] = Counter()
        total_repositories = len(repositories)

        for repo in repositories:
            repo_techs: Set[str] = set()

            # 1. Primary language
            language = repo.get("language")
            if language and isinstance(language, str) and language.strip():
                normalized_lang = normalize_technology_name(language)
                if normalized_lang:
                    repo_techs.add(normalized_lang)

            # 2. Repository topics
            topics = repo.get("topics") or []
            if isinstance(topics, list):
                for topic in topics:
                    if isinstance(topic, str) and topic.strip():
                        normalized_topic = normalize_technology_name(topic)
                        if normalized_topic:
                            repo_techs.add(normalized_topic)

            # Count each technology at most once per repository
            for tech in repo_techs:
                tech_counts[tech] += 1

        # Sort technologies: highest repository_count first, then alphabetical by name
        sorted_technologies = [
            {"name": name, "repository_count": count}
            for name, count in sorted(tech_counts.items(), key=lambda item: (-item[1], item[0]))
        ]

        return {
            "technologies": sorted_technologies,
            "total_repositories": total_repositories,
        }


# Singleton instance for route usage
technology_service = TechnologyService()
