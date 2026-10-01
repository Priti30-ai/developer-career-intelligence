# Developer Career Intelligence System — Roadmap

## Progress Overview

### Completed Milestones
- [x] **Milestone 1: Backend Foundation & API Routing**
  - FastAPI application structure, configuration, and API v1 routing.
- [x] **Milestone 2: GitHub Integration & Repository Analysis**
  - Public profile and repository fetching via GitHub REST API with full error handling.
- [x] **Milestone 3: Technology Extraction & Normalization**
  - Deterministic technology extraction from languages and topics, canonical alias mapping, and deduplication.
- [x] **Milestone 4: Categorized Skill Profiling**
  - Multi-category classification into canonical technical domains without redundant queries.
- [x] **Milestone 5: Skill Gap Analysis**
  - Centralized career role definitions for 6 core industry profiles.
  - Deterministic skill-coverage calculation and matched/missing partitioning.
- [x] **Milestone 6: Career Recommendations & Learning Roadmap (Current Milestone)**
  - Centralized learning guidance catalog for prerequisite technical skills.
  - Explainable priority assignment (`HIGH`, `MEDIUM`, `LOW`) based on dependency unblocking.
  - Multi-stage sequential learning roadmaps respecting topological prerequisites.
  - Suggested career-system-relevant portfolio projects.

---

### Future Milestones (Not Yet Implemented)
- [ ] **Milestone 7: Persistence & Database Modeling**
  - PostgreSQL schema design for developer profiles, repositories, roles, and learning roadmaps.
  - Database migrations and connection pooling.
- [ ] **Milestone 8: Semantic & Vector Matching**
  - Embeddings (pgvector) for fuzzy skill matching and non-exact role similarities.
- [ ] **Milestone 9: Authentication & Profile Management**
  - User authentication, OAuth GitHub login, and private dashboard access.
- [ ] **Milestone 10: AI & Agentic Career Mentorship**
  - RAG-powered career advisory agents and personalized resume insights.
- [ ] **Milestone 11: Frontend Application**
  - Modern web dashboard for developer skill visualization, gap exploration, and interactive roadmaps.
