"""
learning_resource_service.py
----------------------------
Centralized repository of structured learning resources, prerequisites,
and project suggestions for canonical skills across all supported career roles.

Design rules:
- Skill names MUST use canonical normalized names from technology_service.py.
- Project ideas focus on Developer Career Intelligence System domains where practical.
- Prerequisites express realistic learning dependencies.
- No external scraping or dynamic API calls.
"""

from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# Centralized Skill Guidance Catalog
# ---------------------------------------------------------------------------

SKILL_CATALOG: Dict[str, Dict[str, Any]] = {
    "Python": {
        "category": "Programming Languages",
        "difficulty": "Beginner",
        "estimated_stage": 1,
        "prerequisites": [],
        "learning_topics": [
            "Data structures (lists, dicts, sets, tuples)",
            "Object-oriented programming and classes",
            "Functional patterns, generators, and decorators",
            "File I/O and exception handling",
            "Virtual environments and package management",
        ],
        "suggested_projects": [
            "CLI-based Developer Profile Inspector",
            "Automated Code Style and Syntax Checker",
        ],
    },
    "JavaScript": {
        "category": "Programming Languages",
        "difficulty": "Beginner",
        "estimated_stage": 1,
        "prerequisites": [],
        "learning_topics": [
            "ES6+ syntax (destructuring, arrow functions, modules)",
            "Asynchronous programming (Promises, async/await)",
            "DOM manipulation and browser events",
            "Scope, closures, and the event loop",
        ],
        "suggested_projects": [
            "Interactive Repository Filter Widget",
            "Developer Activity Timeline Viewer",
        ],
    },
    "TypeScript": {
        "category": "Programming Languages",
        "difficulty": "Intermediate",
        "estimated_stage": 2,
        "prerequisites": ["JavaScript"],
        "learning_topics": [
            "Static typing, interfaces, and type aliases",
            "Generics and conditional types",
            "Union and intersection types",
            "TypeScript compiler configuration and strict mode",
        ],
        "suggested_projects": [
            "Type-Safe Career Intelligence API Client",
            "Typed Developer Profile Data Models",
        ],
    },
    "HTML": {
        "category": "Web Technologies",
        "difficulty": "Beginner",
        "estimated_stage": 1,
        "prerequisites": [],
        "learning_topics": [
            "Semantic HTML5 elements and accessibility (a11y)",
            "Forms, validation, and input types",
            "Document structure and SEO meta tags",
        ],
        "suggested_projects": [
            "Accessible Developer Resume Markup",
            "Semantic Career Report Template",
        ],
    },
    "CSS": {
        "category": "Web Technologies",
        "difficulty": "Beginner",
        "estimated_stage": 1,
        "prerequisites": ["HTML"],
        "learning_topics": [
            "Box model, flexbox, and grid layouts",
            "Responsive web design and media queries",
            "CSS variables and custom properties",
            "Modern transitions and micro-interactions",
        ],
        "suggested_projects": [
            "Responsive Developer Portfolio Theme",
            "Skill Badge Matrix Layout",
        ],
    },
    "SQL": {
        "category": "Databases",
        "difficulty": "Beginner",
        "estimated_stage": 1,
        "prerequisites": [],
        "learning_topics": [
            "Relational data modeling and normalization",
            "CRUD operations and filtering with WHERE/HAVING",
            "Complex JOINs (INNER, LEFT, FULL)",
            "Aggregation, GROUP BY, and window functions",
            "Indexes, execution plans, and query optimization",
        ],
        "suggested_projects": [
            "Developer Career Analytics Database",
            "Repository Benchmark Query Suite",
        ],
    },
    "PostgreSQL": {
        "category": "Databases",
        "difficulty": "Intermediate",
        "estimated_stage": 2,
        "prerequisites": ["SQL"],
        "learning_topics": [
            "Advanced indexing (B-Tree, GIN, GiST)",
            "JSONB querying and indexing",
            "Transactions, ACID, and isolation levels",
            "Constraints, foreign keys, and cascading rules",
        ],
        "suggested_projects": [
            "Developer Career Intelligence Relational Schema",
            "Repository Metadata Store with JSONB Attributes",
        ],
    },
    "Git": {
        "category": "DevOps & Cloud",
        "difficulty": "Beginner",
        "estimated_stage": 1,
        "prerequisites": [],
        "learning_topics": [
            "Repository initialization, branching, and merging",
            "Merge conflict resolution and rebasing",
            "Commit history inspection and git log formatting",
            "Remote collaboration workflows (pull requests, cherry-pick)",
        ],
        "suggested_projects": [
            "Multi-Branch Feature Release Workflow",
            "Git Hook for Conventional Commit Validation",
        ],
    },
    "Linux": {
        "category": "DevOps & Cloud",
        "difficulty": "Beginner",
        "estimated_stage": 1,
        "prerequisites": [],
        "learning_topics": [
            "Shell navigation, file manipulation, and permissions",
            "Process management, systemd, and signals",
            "Bash scripting, piping, and text processing (grep, awk, sed)",
            "Environment variables and path management",
        ],
        "suggested_projects": [
            "Automated Server Health Check Bash Script",
            "Backend Deployment Environment Setup Script",
        ],
    },
    "Docker": {
        "category": "DevOps & Cloud",
        "difficulty": "Intermediate",
        "estimated_stage": 2,
        "prerequisites": ["Linux"],
        "learning_topics": [
            "Container lifecycle, images, and registries",
            "Multi-stage Dockerfile creation",
            "Docker Compose multi-service orchestration",
            "Volume management and container networking",
        ],
        "suggested_projects": [
            "Containerized FastAPI Application with Uvicorn",
            "Dockerized Developer Career System Development Environment",
        ],
    },
    "REST API": {
        "category": "Web Technologies",
        "difficulty": "Intermediate",
        "estimated_stage": 2,
        "prerequisites": ["Python"],
        "learning_topics": [
            "RESTful architectural constraints and HTTP methods",
            "Status codes, error handling, and response schemas",
            "Path/query parameters and request body validation",
            "API versioning and OpenAPI documentation",
        ],
        "suggested_projects": [
            "Developer Career Intelligence REST API",
            "Public GitHub Profile Metrics API",
        ],
    },
    "React": {
        "category": "Frameworks & Libraries",
        "difficulty": "Intermediate",
        "estimated_stage": 2,
        "prerequisites": ["JavaScript", "HTML", "CSS"],
        "learning_topics": [
            "Component composition and JSX syntax",
            "State management with hooks (useState, useEffect, useMemo)",
            "Custom hooks and context API",
            "Client-side routing and asynchronous data fetching",
        ],
        "suggested_projects": [
            "Interactive Developer Career Dashboard",
            "Live Skill Gap Visualizer Component",
        ],
    },
    "Node.js": {
        "category": "Frameworks & Libraries",
        "difficulty": "Intermediate",
        "estimated_stage": 2,
        "prerequisites": ["JavaScript"],
        "learning_topics": [
            "Node.js runtime, event loop, and libuv",
            "Native modules (fs, path, http, events)",
            "Express or Fastify web server setup",
            "Middleware pattern and asynchronous error handling",
        ],
        "suggested_projects": [
            "Backend Webhook Handler for GitHub Events",
            "Developer Profile Cache Microservice",
        ],
    },
    "Pandas": {
        "category": "AI / Machine Learning",
        "difficulty": "Intermediate",
        "estimated_stage": 2,
        "prerequisites": ["Python"],
        "learning_topics": [
            "DataFrames and Series data manipulation",
            "Data cleaning, missing value imputation, and type conversion",
            "Groupby operations, aggregations, and pivot tables",
            "Time series and date manipulation",
        ],
        "suggested_projects": [
            "GitHub Repository Commit History Analyzer",
            "Developer Skill Distribution Dataset Cleaner",
        ],
    },
    "NumPy": {
        "category": "AI / Machine Learning",
        "difficulty": "Intermediate",
        "estimated_stage": 2,
        "prerequisites": ["Python"],
        "learning_topics": [
            "N-dimensional arrays (ndarray) and memory layout",
            "Vectorized operations and broadcasting rules",
            "Array slicing, indexing, and boolean masking",
            "Linear algebra operations and matrix math",
        ],
        "suggested_projects": [
            "Vectorized Skill Similarity Calculator",
            "Matrix Operations for Developer Skill Embeddings",
        ],
    },
    "Statistics": {
        "category": "AI / Machine Learning",
        "difficulty": "Intermediate",
        "estimated_stage": 2,
        "prerequisites": ["Python"],
        "learning_topics": [
            "Descriptive statistics (mean, median, variance, IQR)",
            "Probability distributions and normal distribution",
            "Hypothesis testing and p-values",
            "Correlation vs causation and statistical significance",
        ],
        "suggested_projects": [
            "Developer Experience Statistical Correlation Study",
            "A/B Test Evaluation Model for Career Paths",
        ],
    },
    "Data Visualization": {
        "category": "AI / Machine Learning",
        "difficulty": "Intermediate",
        "estimated_stage": 2,
        "prerequisites": ["Python", "Pandas"],
        "learning_topics": [
            "Visual encoding principles and chart selection",
            "Matplotlib and Seaborn plotting libraries",
            "Distribution charts, box plots, and heatmaps",
            "Interactive plotting with Plotly",
        ],
        "suggested_projects": [
            "Developer Career Progress Dashboard Visualizer",
            "Repository Technology Trend Heatmap",
        ],
    },
    "Excel": {
        "category": "AI / Machine Learning",
        "difficulty": "Beginner",
        "estimated_stage": 1,
        "prerequisites": [],
        "learning_topics": [
            "VLOOKUP, XLOOKUP, and INDEX/MATCH formulas",
            "Pivot tables, data slicing, and summarization",
            "Conditional formatting and data validation",
            "Data visualization charts and summary KPIs",
        ],
        "suggested_projects": [
            "Developer Career Gap Spreadsheet Model",
            "Tech Industry Role Requirement Matrix",
        ],
    },
    "Machine Learning": {
        "category": "AI / Machine Learning",
        "difficulty": "Intermediate",
        "estimated_stage": 3,
        "prerequisites": ["Python", "NumPy", "Pandas", "Statistics"],
        "learning_topics": [
            "Supervised vs unsupervised learning paradigms",
            "Model evaluation metrics (precision, recall, F1, ROC-AUC)",
            "Feature engineering, scaling, and train/test splits",
            "Ensemble methods (Random Forest, Gradient Boosting)",
        ],
        "suggested_projects": [
            "Developer Skill Prediction Classifier",
            "Career Role Recommendation Model",
        ],
    },
    "Scikit-learn": {
        "category": "AI / Machine Learning",
        "difficulty": "Intermediate",
        "estimated_stage": 3,
        "prerequisites": ["Python", "NumPy", "Pandas", "Machine Learning"],
        "learning_topics": [
            "Scikit-learn estimator, transformer, and predictor API",
            "Pipelines and ColumnTransformers",
            "Cross-validation and GridSearchCV hyperparameter tuning",
            "Model persistence and serialization",
        ],
        "suggested_projects": [
            "End-to-End Skill Profiler Classification Pipeline",
            "Predictive Developer Readiness Scoring Model",
        ],
    },
    "Deep Learning": {
        "category": "AI / Machine Learning",
        "difficulty": "Advanced",
        "estimated_stage": 4,
        "prerequisites": ["Python", "NumPy", "Machine Learning"],
        "learning_topics": [
            "Neural network architectures, activations, and backpropagation",
            "Loss functions and optimizers (SGD, Adam, AdamW)",
            "Regularization (dropout, batch normalization, weight decay)",
            "Convolutional and Recurrent neural networks",
        ],
        "suggested_projects": [
            "Code Token Sequence Classifier",
            "Developer Experience Neural Predictor",
        ],
    },
    "TensorFlow": {
        "category": "AI / Machine Learning",
        "difficulty": "Advanced",
        "estimated_stage": 4,
        "prerequisites": ["Python", "Deep Learning"],
        "learning_topics": [
            "Keras Sequential and Functional APIs",
            "Custom training loops and gradient tapes",
            "Data loading with tf.data.Dataset",
            "Model export to SavedModel format and TF Serving",
        ],
        "suggested_projects": [
            "TensorFlow Model for GitHub Repository Categorization",
            "Neural Skill Match Predictor",
        ],
    },
    "PyTorch": {
        "category": "AI / Machine Learning",
        "difficulty": "Advanced",
        "estimated_stage": 4,
        "prerequisites": ["Python", "Deep Learning"],
        "learning_topics": [
            "Tensors, autograd, and computation graphs",
            "torch.nn modules, datasets, and dataloaders",
            "Custom loss functions and training loops",
            "Model checkpointing and TorchScript export",
        ],
        "suggested_projects": [
            "PyTorch Repository Embedding Generator",
            "Custom Neural Classifier for Developer Skill Profiles",
        ],
    },
    "NLP": {
        "category": "AI / Machine Learning",
        "difficulty": "Advanced",
        "estimated_stage": 4,
        "prerequisites": ["Python", "Machine Learning"],
        "learning_topics": [
            "Text preprocessing, tokenization, and stemming/lemmatization",
            "TF-IDF, Bag of Words, and N-gram models",
            "Word embeddings (Word2Vec, GloVe)",
            "Transformer attention mechanisms and tokenizers",
        ],
        "suggested_projects": [
            "Repository Readme Keyword and Skill Extractor",
            "Developer Bio Topic Extraction Engine",
        ],
    },
    "LLM": {
        "category": "AI / Machine Learning",
        "difficulty": "Advanced",
        "estimated_stage": 4,
        "prerequisites": ["Python", "NLP", "Deep Learning"],
        "learning_topics": [
            "Large language model architectures (decoder-only transformers)",
            "Prompt engineering techniques (few-shot, chain-of-thought)",
            "Fine-tuning paradigms (LoRA, QLoRA)",
            "Inference optimization and context window management",
        ],
        "suggested_projects": [
            "LLM-Ready Career Roadmap Summarizer",
            "Automated Developer Portfolio Feedback Assistant",
        ],
    },
    "MLOps": {
        "category": "DevOps & Cloud",
        "difficulty": "Advanced",
        "estimated_stage": 4,
        "prerequisites": ["Python", "Machine Learning", "Docker"],
        "learning_topics": [
            "Model tracking and experiment management (MLflow)",
            "Model registries and versioning",
            "Continuous training pipelines and automated deployment",
            "Model monitoring, drift detection, and logging",
        ],
        "suggested_projects": [
            "Automated Model Training Pipeline with Docker",
            "Developer Skill Classifier Deployment with Monitoring",
        ],
    },
}


class LearningResourceService:
    """
    Centralized service for skill learning resources, prerequisites, and projects.
    """

    def get_skill_guidance(self, skill_name: str) -> Dict[str, Any]:
        """
        Return structured learning guidance for a canonical skill.

        If the skill is not in the predefined catalog, generates safe,
        informative fallback guidance using standard conventions.
        """
        if skill_name in SKILL_CATALOG:
            item = SKILL_CATALOG[skill_name]
            return {
                "skill": skill_name,
                "category": item["category"],
                "difficulty": item["difficulty"],
                "estimated_stage": item["estimated_stage"],
                "prerequisites": list(item["prerequisites"]),
                "learning_topics": list(item["learning_topics"]),
                "suggested_projects": list(item["suggested_projects"]),
            }

        # Safe fallback for any unexpected skill
        return {
            "skill": skill_name,
            "category": "Tools & Other",
            "difficulty": "Intermediate",
            "estimated_stage": 2,
            "prerequisites": [],
            "learning_topics": [
                f"Core syntax and operational patterns for {skill_name}",
                f"Best practices and standard project architecture with {skill_name}",
                f"Debugging, testing, and production deployment of {skill_name}",
            ],
            "suggested_projects": [
                f"{skill_name} Integration Prototype for Career Intelligence",
            ],
        }

    def has_skill(self, skill_name: str) -> bool:
        """Check if a skill is in the catalog."""
        return skill_name in SKILL_CATALOG


# Singleton instance
learning_resource_service = LearningResourceService()
