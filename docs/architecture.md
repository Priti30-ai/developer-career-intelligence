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

### 7. Resume vs GitHub Evidence Analysis (Deterministic Foundation)
- **Service**: `app.services.evidence_service.EvidenceService`
- **Schemas**: `app.schemas.evidence.EvidenceAnalysisRequest`, `app.schemas.evidence.EvidenceAnalysisResponse`
- Deterministic evidence analysis pipeline:

```
Resume Skills
      ↓
Skill Normalization
      ↓
GitHub Repository Skills
      ↓
Evidence Matching
      ↓
Evidence Classification
      ↓
Supporting Repositories
      ↓
Evidence Coverage
```

- **Explainable Classification Rules**:
  - `STRONG`: Skill detected across multiple ($\ge 2$) analyzed GitHub repositories.
  - `MODERATE`: Skill detected in at least one ($== 1$) analyzed GitHub repository.
  - `NONE_DETECTED`: Skill claimed in resume but not detected ($== 0$) across analyzed repositories.
- **Repository Evidence Preservation**: Tracks supporting repositories with repository name, full name, URL, and detected technologies.
- **Explainable Principle**: Missing GitHub evidence does NOT imply a candidate lacks knowledge or fabricated a claim; evidence reflects only verified public repository presence.
- **Error Handling**: Distinguishes GitHub API failures (HTTP 404, 403, 502, 504) from undetected skills, returning clear API errors rather than misleading `NONE_DETECTED` outputs.

### 8. Job Description Analysis & Matching (Deterministic Foundation)
- **Services**: `app.services.job_description_service.JobDescriptionService`, `app.services.job_matching_service.JobMatchingService`
- **Schemas**: `app.schemas.job_matching.JobMatchingRequest`, `app.schemas.job_matching.JobMatchingResponse`
- Deterministic analysis & matching pipeline:

```
Job Description Text
        ↓
Skill Extraction (Word-Boundary & Alias Scanning)
        ↓
Canonical Normalization (TechnologyService)
        ↓
Developer Skills Comparison
        ↓
Matched vs Missing Skills Partition
        ↓
Deterministic Match Coverage Percentage
```

- **Skill Extraction & Normalization**:
  - Reuses the centralized `TECHNOLOGY_ALIASES` mapping and `normalize_technology_name` utility.
  - Employs regex word-boundary detection to avoid substring false positives.
  - Normalizes aliases (`nodejs` $\to$ `Node.js`, `cpp` $\to$ `C++`, `sklearn` $\to$ `Scikit-learn`) and eliminates duplicates.
- **Deterministic Match Metric**:
  $$\text{match\_percentage} = \text{round}\left(\frac{\text{matched\_skill\_count}}{\text{total\_required\_skills}} \times 100, 2\right) \quad (\text{returns } 0.0 \text{ if } \text{total\_required\_skills} = 0)$$
  *(Partition invariant: $\text{matched\_skill\_count} + \text{missing\_skill\_count} \equiv \text{total\_required\_skills}$)*
- **Current Limitations & Future Enhancements**:
  - Current baseline relies on deterministic alias and keyword matching.
  - Future milestones will evaluate semantic matching and vector embeddings (`pgvector`) to capture conceptual equivalents not present in alias catalogs.

### 9. Unified Developer Profile Synthesis (Deterministic Foundation)
- **Service**: `app.services.developer_profile_service.DeveloperProfileService`
- **Schemas**: `app.schemas.developer_profile.DeveloperProfileRequest`, `app.schemas.developer_profile.DeveloperProfileResponse`
- Deterministic synthesis pipeline:

```
GitHub Analysis
       +
Resume Analysis
       +
Evidence Analysis
       ↓
Unified Developer Profile
```

- **Unified Developer-Level Representation**:
  - Serves as the central, reusable developer-level profile consumed by downstream intelligence modules (Job Description Matching, Skill Gap Analysis, Career Recommendations, Roadmap, and Frontend UI).
- **Skill Merging & Deduplication**:
  - Combines repository-derived skills with resume-extracted skills into canonical normalized forms using `TechnologyService`.
  - Removes duplicate alias variations (`python`, `Python` $\to$ `Python`).
- **Source Tracking**:
  - Unambiguously records whether each skill was identified from `github`, `resume`, or both (`["github", "resume"]`).
- **Evidence Classification & Preservation**:
  - Preserves verified repository evidence classifications:
    - `STRONG`: Detected across $\ge 2$ analyzed repositories.
    - `MODERATE`: Detected in $1$ analyzed repository.
    - `NONE_DETECTED`: Claimed in resume but not detected across analyzed repositories.
  - Attaches matching repository metadata (`name`, `full_name`, `html_url`, `skills_detected`).
  - **Critical Semantics**: Missing GitHub evidence (`NONE_DETECTED`) indicates solely the absence of verified public repository evidence; it does NOT mean or prove that the candidate lacks the skill.
- **Deterministic Profile Statistics & Invariants**:
  - Computes `total_skills`, `github_skill_count`, `resume_skill_count`, `skills_from_both_sources`, `supported_skill_count`, and `skills_without_github_evidence`.
  - Invariants hold strictly:
    $$\text{total\_skills} \equiv \text{supported\_skill\_count} + \text{skills\_without\_github\_evidence}$$
    $$\text{total\_skills} \equiv \text{github\_skill\_count} + \text{resume\_skill\_count} - \text{skills\_from\_both\_sources}$$
- **Downstream Module Adapter**:
  - Exposes `profile.get_skill_names()` and `extract_developer_skills(profile)` for zero-copy, direct integration into `job_matching_service.match_job_description`.
- **API Endpoint**:
  - `POST /api/v1/developer-profile/analyze`
