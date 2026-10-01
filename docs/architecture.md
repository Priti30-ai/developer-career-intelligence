# Developer Career Intelligence System — Architecture

## Overview

The **Developer Career Intelligence System** is an extensible backend intelligence platform designed to analyze a developer's software footprint, assess skill readiness against targeted technology careers, and generate tailored, sequential learning roadmaps.

The system is developed incrementally using clean architecture:
- **API Routes**: Parse parameters, validate schemas, and handle HTTP errors.
- **Service Layer**: Encapsulates pure business logic, calculations, and catalog definitions.
- **Schemas**: Standardized Pydantic models for request validation and response formatting.

---

## Architectural Pipeline

```
GitHub Profile & Repositories
            ↓
Repository Analysis (GitHubService)
            ↓
Technology Signal Extraction (TechnologyService)
            ↓
Technology Normalization & Aliases (TechnologyService)
            ↓
Categorized Skill Profiling (SkillProfileService)
            ↓
Skill Gap Analysis (SkillGapService & CareerRoleService)
            ↓
Career & Learning Recommendations (CareerRecommendationService & LearningResourceService)
            ↓
Multi-Stage Sequential Learning Roadmap
```

---

## Components

### 1. GitHub Integration & Repository Analysis
- **Service**: `app.services.github_service.GitHubService`
- Fetches public repositories, primary languages, repository topics, star counts, and fork counts.
- Implements robust error handling (HTTP 404, rate-limiting HTTP 403, and gateway timeouts).

### 2. Technology Extraction & Normalization
- **Service**: `app.services.technology_service.TechnologyService`
- Normalizes technology names into canonical forms using a curated alias dictionary (`TECHNOLOGY_ALIASES`) and case-insensitive fallback logic.
- Counts technology frequency across repositories, counting each technology at most once per repository.

### 3. Skill Profiling
- **Service**: `app.services.skill_profile_service.SkillProfileService`
- Groups normalized technologies into logical skill categories:
  - Programming Languages
  - Frameworks & Libraries
  - AI / Machine Learning
  - Web Technologies
  - Databases
  - DevOps & Cloud
  - Tools & Other (fallback)

### 4. Career Role Requirements & Skill Gap Analysis
- **Services**: `app.services.career_role_service.CareerRoleService`, `app.services.skill_gap_service.SkillGapService`
- Predefined canonical role profiles for 6 target roles:
  - Data Scientist
  - Machine Learning Engineer
  - AI Engineer
  - Data Analyst
  - Backend Developer
  - Full Stack Developer
- Deterministic calculation of matched and missing skills.
- Skill match coverage metric:
  $$\text{skill\_match\_percentage} = \text{round}\left(\frac{\text{total\_matched\_skills}}{\text{total\_required\_skills}} \times 100, 2\right)$$
  *(Partition invariant: $\text{matched} + \text{missing} \equiv \text{required}$)*

### 5. Career Recommendations & Learning Roadmap
- **Services**: `app.services.learning_resource_service.LearningResourceService`, `app.services.career_recommendation_service.CareerRecommendationService`
- **Rule-based & Deterministic**: The current engine is purely deterministic and rule-based; it does NOT use machine learning or LLMs.
- Generates:
  - Prioritized skill learning guidance (`HIGH`, `MEDIUM`, `LOW`) with explainable rationale based on dependency unblocking.
  - Core curriculum topics and career-system-related suggested portfolio projects.
  - Sequential, non-empty learning roadmap stages ordered topologically according to prerequisites.
- Disclaimer: Recommendations represent structured skill guidance and do not guarantee employment or hiring outcomes.

### 6. Resume Analysis (Deterministic Foundation)
- **Service**: `app.services.resume_service.ResumeService`
- **Schema**: `app.schemas.resume.ResumeAnalysisRequest`, `app.schemas.resume.ResumeAnalysisResponse`
- Deterministic parsing pipeline:

```
Resume Text
    ↓
Resume Service
    ↓
Section Detection
    ↓
Structured Resume Data
    ↓
Normalized Skills
```

- Converts unstructured plain text resumes into structured sections: Summary, Skills, Education, Experience, Projects, Certifications, and Achievements.
- Normalizes extracted skills using `normalize_technology_name` from the shared technology service, ensuring alias canonicalization and deduplication.
- Extracts structured education credentials, work experience/internships, and projects with associated technologies.
- *(Note: Resume Skill Profile and Resume-vs-Code Evidence Analysis will be integrated in subsequent milestones).*
