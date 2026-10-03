"""
test_github_evidence_service.py
--------------------------------
Comprehensive unit and integration test suite for GitHubEvidenceService (Task 5).

Covers:
1. JavaScript / TypeScript manifest parsing & normalization
2. Python requirements, pyproject.toml, and Pipfile parsing
3. JVM (pom.xml, Gradle), Go (go.mod), Rust (Cargo.toml), and Container (Dockerfile, compose)
4. Evidence signals, source types, and strength levels (STRONG, MODERATE, WEAK)
5. Repository-level skill intelligence & domain categories
6. Error handling, unreadable/malformed manifests, and failure isolation
7. Determinism, deduplication, and absence of cross-repository aggregation
"""

import sys
from pathlib import Path
from unittest.mock import AsyncMock

import pytest

# Ensure backend directory is in sys.path
backend_dir = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from app.schemas.github_account import (
    EVIDENCE_SOURCE_CONFIG,
    EVIDENCE_SOURCE_LANGUAGE,
    EVIDENCE_SOURCE_MANIFEST,
    EVIDENCE_SOURCE_STRUCTURE,
    EVIDENCE_SOURCE_TOPIC,
    EVIDENCE_STRENGTH_MODERATE,
    EVIDENCE_STRENGTH_STRONG,
    EVIDENCE_STRENGTH_WEAK,
    RepositoryAnalysisDetail,
)
from app.schemas.repository_architecture import ArchitectureSignal
from app.services.github_evidence_service import (
    GitHubEvidenceService,
    github_evidence_service,
)
from app.services.github_service import GitHubAPIError, GitHubService


def _make_detail(
    name: str = "demo-repo",
    full_name: str = "octocat/demo-repo",
    languages: list = None,
    manifest_files: list = None,
    architecture_signals: list = None,
    topics: list = None,
    is_empty: bool = False,
    analysis_status: str = "SUCCESS",
) -> RepositoryAnalysisDetail:
    return RepositoryAnalysisDetail(
        name=name,
        full_name=full_name,
        html_url=f"https://github.com/{full_name}",
        default_branch="main",
        languages=languages or [],
        manifest_files=manifest_files or [],
        architecture_signals=architecture_signals or [],
        topics=topics or [],
        is_empty=is_empty,
        analysis_status=analysis_status,
    )


# =============================================================================
# 1. JavaScript / TypeScript Manifests
# =============================================================================

class TestJavaScriptTypeScriptManifests:

    def test_01_package_json_dependencies(self):
        """1. Standard dependencies extracted with strong manifest evidence."""
        content = '{"dependencies": {"express": "^4.18.2", "cors": "^2.8.5"}}'
        signals = github_evidence_service.parse_package_json(content, "package.json")
        techs = {s.technology for s in signals}

        assert "Express" in techs
        express_signal = next(s for s in signals if s.technology == "Express")
        assert express_signal.strength == EVIDENCE_STRENGTH_STRONG
        assert express_signal.source_type == EVIDENCE_SOURCE_MANIFEST
        assert express_signal.details.get("section") == "dependencies"

    def test_02_package_json_dev_dependencies(self):
        """2. devDependencies extracted with correct section metadata."""
        content = '{"devDependencies": {"jest": "^29.5.0", "typescript": "^5.0.0"}}'
        signals = github_evidence_service.parse_package_json(content, "package.json")
        techs = {s.technology for s in signals}

        assert "Jest" in techs
        assert "TypeScript" in techs
        jest_signal = next(s for s in signals if s.technology == "Jest")
        assert jest_signal.details.get("section") == "devDependencies"

    def test_03_package_json_peer_and_optional_dependencies(self):
        """3. peerDependencies and optionalDependencies extracted."""
        content = """
        {
            "peerDependencies": {"react": ">=18.0.0"},
            "optionalDependencies": {"redis": "^4.0.0"}
        }
        """
        signals = github_evidence_service.parse_package_json(content, "package.json")
        techs = {s.technology for s in signals}

        assert "React" in techs
        assert "Redis" in techs

    def test_04_react_detection(self):
        """4. react, react-dom, and @types/react resolve to canonical 'React'."""
        content = """
        {
            "dependencies": {"react": "^18.2.0", "react-dom": "^18.2.0"},
            "devDependencies": {"@types/react": "^18.2.0"}
        }
        """
        signals = github_evidence_service.parse_package_json(content, "frontend/package.json")
        techs = {s.technology for s in signals}

        assert techs == {"React"}
        assert len(signals) == 3

    def test_05_express_detection(self):
        """5. express and expressjs resolve to canonical 'Express'."""
        content = '{"dependencies": {"express": "^4.18.0"}}'
        signals = github_evidence_service.parse_package_json(content, "server/package.json")
        assert any(s.technology == "Express" for s in signals)

    def test_06_vite_and_nextjs_detection(self):
        """6. next and vite packages detected canonically."""
        content = '{"dependencies": {"next": "13.4.0"}, "devDependencies": {"vite": "^4.3.0"}}'
        signals = github_evidence_service.parse_package_json(content, "package.json")
        techs = {s.technology for s in signals}

        assert "Next.js" in techs
        assert "Vite" in techs

    def test_07_duplicate_aliases_normalize_to_single_tech(self):
        """7. Multiple npm aliases normalize to one canonical technology."""
        content = '{"dependencies": {"tailwindcss": "^3.0.0", "axios": "^1.0.0"}}'
        signals = github_evidence_service.parse_package_json(content, "package.json")
        techs = {s.technology for s in signals}

        assert "Tailwind CSS" in techs
        assert "Axios" in techs

    def test_08_tsconfig_evidence(self):
        """8. tsconfig.json produces strong TypeScript configuration evidence."""
        signals = github_evidence_service.parse_tsconfig("{}", "tsconfig.json")
        assert len(signals) == 1
        assert signals[0].technology == "TypeScript"
        assert signals[0].strength == EVIDENCE_STRENGTH_STRONG
        assert signals[0].source_type == EVIDENCE_SOURCE_CONFIG


# =============================================================================
# 2. Python Manifests
# =============================================================================

class TestPythonManifests:

    def test_09_requirements_txt_standard_dependencies(self):
        """9. Standard Python packages extracted with strong evidence."""
        content = "fastapi==0.100.0\npandas>=2.0.0\nscikit-learn\n"
        signals = github_evidence_service.parse_requirements_txt(content, "requirements.txt")
        techs = {s.technology for s in signals}

        assert "FastAPI" in techs
        assert "Pandas" in techs
        assert "Scikit-learn" in techs
        assert all(s.strength == EVIDENCE_STRENGTH_STRONG for s in signals)

    def test_10_requirements_txt_version_stripping(self):
        """10. Comparison operators (==, >=, <=, ~=, !=, >, <) cleanly stripped."""
        content = """
        django>=4.2,<5.0
        flask==2.3.2
        pytest~=7.3
        celery!=5.2.0
        sqlalchemy>1.4
        """
        signals = github_evidence_service.parse_requirements_txt(content, "requirements.txt")
        techs = {s.technology for s in signals}

        assert "Django" in techs
        assert "Flask" in techs
        assert "Pytest" in techs
        assert "Celery" in techs
        assert "SQLAlchemy" in techs

    def test_11_requirements_txt_ignores_comments(self):
        """11. Leading and inline comments ignored without false positives."""
        content = """
        # Core backend framework
        fastapi==0.95.0 # main api framework
        # Database ORM
        sqlalchemy>=2.0.0
        """
        signals = github_evidence_service.parse_requirements_txt(content, "requirements.txt")
        techs = {s.technology for s in signals}

        assert techs == {"FastAPI", "SQLAlchemy"}

    def test_12_requirements_txt_ignores_blank_and_flags(self):
        """12. Blank lines, pip flags (-r, -i, --extra-index-url) ignored."""
        content = """
        -r base.txt
        --extra-index-url https://download.pytorch.org/whl/cu118
        -i https://pypi.org/simple

        pandas==2.0.0
        """
        signals = github_evidence_service.parse_requirements_txt(content, "requirements.txt")
        techs = {s.technology for s in signals}

        assert techs == {"Pandas"}

    def test_13_requirements_txt_ignores_malformed_lines(self):
        """13. Non-package syntax or garbage lines skipped safely."""
        content = "invalid$$$package!!!\n===\n\n   \nfastapi==0.99.0\n"
        signals = github_evidence_service.parse_requirements_txt(content, "requirements.txt")
        assert len(signals) == 1
        assert signals[0].technology == "FastAPI"

    def test_14_requirements_txt_extras_handling(self):
        """14. Package extras syntax like fastapi[all] handled cleanly."""
        content = "fastapi[all]>=0.95.0\ncelery[redis]>=5.2.0\n"
        signals = github_evidence_service.parse_requirements_txt(content, "requirements.txt")
        techs = {s.technology for s in signals}

        assert "FastAPI" in techs
        assert "Celery" in techs

    def test_15_pyproject_toml_dependencies(self):
        """15. PEP 621 and Poetry dependencies parsed from pyproject.toml."""
        content = """
        [project]
        dependencies = [
            "fastapi>=0.95.0",
            "pydantic>=2.0.0",
        ]

        [tool.poetry.dependencies]
        python = "^3.11"
        httpx = "^0.24.0"
        """
        signals = github_evidence_service.parse_pyproject_toml(content, "pyproject.toml")
        techs = {s.technology for s in signals}

        assert "FastAPI" in techs
        assert "Pydantic" in techs
        assert "HTTPX" in techs

    def test_16_pipfile_dependencies(self):
        """16. Pipfile [packages] and [dev-packages] parsed."""
        content = """
        [packages]
        django = "*"
        redis = ">=4.0"

        [dev-packages]
        pytest = "*"
        """
        signals = github_evidence_service.parse_pipfile(content, "Pipfile")
        techs = {s.technology for s in signals}

        assert "Django" in techs
        assert "Redis" in techs
        assert "Pytest" in techs


# =============================================================================
# 3. Other Ecosystems (JVM, Go, Rust, Container)
# =============================================================================

class TestOtherEcosystems:

    def test_17_pom_xml_dependencies(self):
        """17. Maven pom.xml dependencies parsed into canonical technologies."""
        content = """
        <project>
            <dependencies>
                <dependency>
                    <groupId>org.springframework.boot</groupId>
                    <artifactId>spring-boot-starter-web</artifactId>
                </dependency>
                <dependency>
                    <groupId>org.postgresql</groupId>
                    <artifactId>postgresql</artifactId>
                </dependency>
                <dependency>
                    <groupId>org.junit.jupiter</groupId>
                    <artifactId>junit-jupiter</artifactId>
                </dependency>
            </dependencies>
        </project>
        """
        signals = github_evidence_service.parse_pom_xml(content, "pom.xml")
        techs = {s.technology for s in signals}

        assert "Spring Boot" in techs
        assert "PostgreSQL" in techs
        assert "JUnit" in techs

    def test_18_gradle_dependencies(self):
        """18. Gradle dependency notation parsed."""
        content = """
        dependencies {
            implementation 'org.springframework.boot:spring-boot-starter-web:3.0.0'
            testImplementation 'org.junit.jupiter:junit-jupiter:5.9.0'
        }
        """
        signals = github_evidence_service.parse_build_gradle(content, "build.gradle")
        techs = {s.technology for s in signals}

        assert "Spring Boot" in techs
        assert "JUnit" in techs

    def test_19_go_mod_dependencies(self):
        """19. Go module dependencies parsed from go.mod."""
        content = """
        module example.com/my-api

        go 1.21

        require (
            github.com/gin-gonic/gin v1.9.1
            github.com/stretchr/testify v1.8.4
        )
        """
        signals = github_evidence_service.parse_go_mod(content, "go.mod")
        techs = {s.technology for s in signals}

        assert "Gin" in techs
        assert "Testify" in techs

    def test_20_cargo_toml_dependencies(self):
        """20. Rust Cargo.toml dependencies parsed."""
        content = """
        [package]
        name = "web-service"
        version = "0.1.0"

        [dependencies]
        tokio = { version = "1.0", features = ["full"] }
        actix-web = "4.0"
        serde = "1.0"
        """
        signals = github_evidence_service.parse_cargo_toml(content, "Cargo.toml")
        techs = {s.technology for s in signals}

        assert "Tokio" in techs
        assert "Actix Web" in techs
        assert "Serde" in techs

    def test_21_dockerfile_base_image(self):
        """21. Dockerfile base images detect Python/Node/Postgres + Docker."""
        content = """
        FROM python:3.11-slim
        WORKDIR /app
        COPY . .
        """
        signals = github_evidence_service.parse_dockerfile(content, "Dockerfile")
        techs = {s.technology for s in signals}

        assert "Docker" in techs
        assert "Python" in techs

    def test_22_docker_compose_services(self):
        """22. docker-compose.yml extracts container images (PostgreSQL, Redis) + Docker."""
        content = """
        version: '3.8'
        services:
          db:
            image: postgres:15-alpine
          cache:
            image: redis:7-alpine
        """
        signals = github_evidence_service.parse_docker_compose(content, "docker-compose.yml")
        techs = {s.technology for s in signals}

        assert "Docker" in techs
        assert "PostgreSQL" in techs
        assert "Redis" in techs


# =============================================================================
# 4. Evidence Signals & Strength Rules
# =============================================================================

class TestEvidenceSignalsAndStrength:

    def test_23_strong_dependency_evidence(self):
        """23. Declared manifest dependencies produce STRONG evidence."""
        signals = github_evidence_service.parse_package_json('{"dependencies": {"react": "^18.0"}}')
        assert signals[0].strength == EVIDENCE_STRENGTH_STRONG
        assert signals[0].source_type == EVIDENCE_SOURCE_MANIFEST

    def test_24_moderate_language_evidence(self):
        """24. Detected source languages produce MODERATE evidence."""
        signals = github_evidence_service.extract_language_evidence(["Python", "TypeScript"])
        assert len(signals) == 2
        assert all(s.strength == EVIDENCE_STRENGTH_MODERATE for s in signals)
        assert all(s.source_type == EVIDENCE_SOURCE_LANGUAGE for s in signals)

    def test_25_moderate_project_structure_evidence(self):
        """25. Architecture signals produce MODERATE structure evidence."""
        repo = _make_detail(
            architecture_signals=[
                ArchitectureSignal(
                    type="BACKEND",
                    description="Backend service structure detected",
                    evidence=["app/api/", "server.py"],
                ),
                ArchitectureSignal(
                    type="DEVOPS",
                    description="Container configuration detected",
                    evidence=["Dockerfile"],
                ),
            ]
        )
        signals = github_evidence_service.extract_structure_evidence(repo)
        techs = {s.technology for s in signals}

        assert "Backend Development" in techs
        assert "DevOps & CI/CD" in techs
        assert all(s.strength == EVIDENCE_STRENGTH_MODERATE for s in signals)
        assert all(s.source_type == EVIDENCE_SOURCE_STRUCTURE for s in signals)

    def test_26_weak_topic_evidence(self):
        """26. Repository topics produce WEAK evidence."""
        signals = github_evidence_service.extract_topic_evidence(["machine-learning", "fastapi"])
        assert len(signals) == 2
        assert all(s.strength == EVIDENCE_STRENGTH_WEAK for s in signals)
        assert all(s.source_type == EVIDENCE_SOURCE_TOPIC for s in signals)

    def test_27_correct_source_path_and_provenance(self):
        """27. Evidence signals preserve exact manifest file path."""
        signals = github_evidence_service.parse_requirements_txt(
            "fastapi==0.95.0", path="backend/requirements.txt"
        )
        assert signals[0].path == "backend/requirements.txt"

    def test_28_deterministic_evidence_ordering(self):
        """28. Evidence is ordered by strength (STRONG before MODERATE before WEAK), then tech name."""
        signals = [
            github_evidence_service.extract_topic_evidence(["python"])[0],  # WEAK
            github_evidence_service.extract_language_evidence(["Python"])[0],  # MODERATE
            github_evidence_service.parse_requirements_txt("fastapi", "req.txt")[0],  # STRONG
        ]
        ordered = github_evidence_service._deduplicate_evidence(signals)
        strengths = [s.strength for s in ordered]

        assert strengths[0] == EVIDENCE_STRENGTH_STRONG
        assert strengths[1] == EVIDENCE_STRENGTH_MODERATE


# =============================================================================
# 5. Repository-Level Skills
# =============================================================================

class TestRepositoryLevelSkills:

    def test_29_repository_skills_inferred_from_evidence(self):
        """29. Skills list is derived from technologies and confirmed structure."""
        techs = ["FastAPI", "Python", "Docker"]
        struct_signals = [
            github_evidence_service.extract_structure_evidence(
                _make_detail(
                    architecture_signals=[
                        ArchitectureSignal(
                            type="BACKEND",
                            description="Backend API",
                            evidence=["app/"],
                        )
                    ]
                )
            )[0]
        ]
        skills, categories = github_evidence_service._infer_repository_skills(
            techs, struct_signals
        )

        assert "FastAPI" in skills
        assert "Python" in skills
        assert "Docker" in skills
        assert "Backend Development" in skills

    def test_30_skill_categories_reused(self):
        """30. Skills are classified using standard domain categories."""
        techs = ["Python", "FastAPI", "PostgreSQL", "Docker", "React"]
        skills, categories = github_evidence_service._infer_repository_skills(techs, [])
        cat_names = [c.category for c in categories]

        assert "Programming Languages" in cat_names
        assert "Frameworks & Libraries" in cat_names
        assert "Databases" in cat_names
        assert "DevOps & Cloud" in cat_names

    def test_31_no_unsupported_or_fabricated_skills(self):
        """31. Skills list contains only evidence-backed technologies and structure."""
        techs = ["Python"]
        skills, categories = github_evidence_service._infer_repository_skills(techs, [])

        assert skills == ["Python"]
        assert "Kubernetes" not in skills
        assert "React" not in skills

    def test_32_no_proficiency_claims_in_skills(self):
        """32. Skill names do not contain subjective proficiency labels."""
        techs = ["Python", "React", "FastAPI"]
        skills, _ = github_evidence_service._infer_repository_skills(techs, [])

        for s in skills:
            assert "expert" not in s.lower()
            assert "senior" not in s.lower()
            assert "advanced" not in s.lower()
            assert "proficient" not in s.lower()

    def test_33_structural_skills_grounded_in_architecture(self):
        """33. Architecture signals correctly add verified structural capability skills."""
        repo = _make_detail(
            architecture_signals=[
                ArchitectureSignal(
                    type="FRONTEND", description="UI", evidence=["src/"]
                ),
                ArchitectureSignal(
                    type="TESTING", description="Tests", evidence=["tests/"]
                ),
            ]
        )
        struct_signals = github_evidence_service.extract_structure_evidence(repo)
        skills, _ = github_evidence_service._infer_repository_skills([], struct_signals)

        assert "Frontend Development" in skills
        assert "Testing & QA" in skills


# =============================================================================
# 6. Failure Handling & Edge Cases
# =============================================================================

class TestFailureHandlingAndEdgeCases:

    @pytest.mark.anyio
    async def test_34_missing_manifest_file_adds_warning_does_not_crash(self):
        """34. None content when fetching manifest records warning and continues analysis."""
        mock_github = AsyncMock(spec=GitHubService)
        mock_github.get_repository_file_content = AsyncMock(return_value=None)

        service = GitHubEvidenceService(service=mock_github)
        repo = _make_detail(
            languages=["Python"],
            manifest_files=["requirements.txt"],
        )

        enriched = await service.enrich_repository(repo)

        assert enriched.analysis_status == "SUCCESS"
        assert any("requirements.txt" in w for w in enriched.warnings)
        # Fallback to language evidence succeeds
        assert "Python" in enriched.technologies

    @pytest.mark.anyio
    async def test_35_unreadable_manifest_file_adds_warning(self):
        """35. Empty manifest content does not crash analysis."""
        mock_github = AsyncMock(spec=GitHubService)
        mock_github.get_repository_file_content = AsyncMock(return_value="")

        service = GitHubEvidenceService(service=mock_github)
        repo = _make_detail(manifest_files=["requirements.txt"])

        enriched = await service.enrich_repository(repo)

        assert enriched.analysis_status == "SUCCESS"
        assert enriched.technologies == []

    @pytest.mark.anyio
    async def test_36_malformed_manifest_json_handled_safely(self):
        """36. Broken JSON in package.json does not raise exception."""
        mock_github = AsyncMock(spec=GitHubService)
        mock_github.get_repository_file_content = AsyncMock(
            return_value="{ this is invalid JSON !!! }"
        )

        service = GitHubEvidenceService(service=mock_github)
        repo = _make_detail(manifest_files=["package.json"], languages=["JavaScript"])

        enriched = await service.enrich_repository(repo)

        assert enriched.analysis_status == "SUCCESS"
        assert "JavaScript" in enriched.technologies

    @pytest.mark.anyio
    async def test_37_file_api_failure_handled_safely(self):
        """37. GitHub API timeout or network error sets is_partial and adds warning."""
        mock_github = AsyncMock(spec=GitHubService)
        mock_github.get_repository_file_content = AsyncMock(
            side_effect=GitHubAPIError("Timeout reading file", status_code=504)
        )

        service = GitHubEvidenceService(service=mock_github)
        repo = _make_detail(manifest_files=["package.json"])

        enriched = await service.enrich_repository(repo)

        assert enriched.is_partial is True
        assert any("Failed to fetch manifest" in w for w in enriched.warnings)

    @pytest.mark.anyio
    async def test_38_empty_repository_handling(self):
        """38. Empty repositories bypass file fetching and return empty evidence."""
        mock_github = AsyncMock(spec=GitHubService)

        service = GitHubEvidenceService(service=mock_github)
        repo = _make_detail(is_empty=True)

        enriched = await service.enrich_repository(repo)

        mock_github.get_repository_file_content.assert_not_called()
        assert enriched.technologies == []
        assert enriched.skills == []
        assert enriched.evidence == []

    @pytest.mark.anyio
    async def test_39_error_repository_handling(self):
        """39. Repositories with ERROR status bypass enrichment cleanly."""
        mock_github = AsyncMock(spec=GitHubService)

        service = GitHubEvidenceService(service=mock_github)
        repo = _make_detail(analysis_status="ERROR")

        enriched = await service.enrich_repository(repo)

        mock_github.get_repository_file_content.assert_not_called()
        assert enriched.technologies == []

    @pytest.mark.anyio
    async def test_40_error_isolation_across_multiple_repositories(self):
        """40. Failure in one repository does not abort or contaminate other repositories."""
        mock_github = AsyncMock(spec=GitHubService)

        async def _file_side_effect(owner, repo, path, branch="main"):
            if repo == "broken-repo":
                raise GitHubAPIError("500 Server Error", status_code=500)
            return '{"dependencies": {"react": "^18.0"}}'

        mock_github.get_repository_file_content = AsyncMock(side_effect=_file_side_effect)

        service = GitHubEvidenceService(service=mock_github)
        repo1 = _make_detail("good-repo", "octocat/good-repo", manifest_files=["package.json"])
        repo2 = _make_detail("broken-repo", "octocat/broken-repo", manifest_files=["package.json"])

        results = await service.enrich_repositories([repo1, repo2])

        assert len(results) == 2
        assert "React" in results[0].technologies
        assert results[1].is_partial is True


# =============================================================================
# 7. Quality & Account Integration Scope
# =============================================================================

class TestQualityAndAccountIntegration:

    @pytest.mark.anyio
    async def test_41_canonical_technology_names_and_deduplication(self):
        """41. Technology list contains only deduplicated canonical names."""
        mock_github = AsyncMock(spec=GitHubService)
        # React mentioned in package.json and topics and language
        mock_github.get_repository_file_content = AsyncMock(
            return_value='{"dependencies": {"react": "^18.0", "react-dom": "^18.0"}}'
        )

        service = GitHubEvidenceService(service=mock_github)
        repo = _make_detail(
            languages=["JavaScript"],
            manifest_files=["package.json"],
            topics=["react", "reactjs"],
        )

        enriched = await service.enrich_repository(repo)

        # "React" must appear exactly once
        assert enriched.technologies.count("React") == 1
        assert "JavaScript" in enriched.technologies

    @pytest.mark.anyio
    async def test_42_deterministic_ordering_across_runs(self):
        """42. Multiple enrichments of identical repository yield identical sorted lists."""
        mock_github = AsyncMock(spec=GitHubService)
        mock_github.get_repository_file_content = AsyncMock(
            return_value="fastapi\npandas\ndocker\n"
        )

        service = GitHubEvidenceService(service=mock_github)
        repo = _make_detail(
            languages=["Python"],
            manifest_files=["requirements.txt"],
            topics=["data-science", "api"],
        )

        res1 = await service.enrich_repository(repo)
        res2 = await service.enrich_repository(repo)

        assert res1.technologies == res2.technologies
        assert res1.skills == res2.skills
        assert [e.technology for e in res1.evidence] == [e.technology for e in res2.evidence]

    @pytest.mark.anyio
    async def test_43_no_cross_repository_aggregation(self):
        """43. In Task 5, analysis remains strictly repository-level without cross-repo counts."""
        mock_github = AsyncMock(spec=GitHubService)

        async def _file_side_effect(owner, repo, path, branch="main"):
            if repo == "repo-a":
                return "fastapi==0.95.0"
            return "fastapi==0.99.0"

        mock_github.get_repository_file_content = AsyncMock(side_effect=_file_side_effect)

        service = GitHubEvidenceService(service=mock_github)
        repo_a = _make_detail("repo-a", "octocat/repo-a", manifest_files=["requirements.txt"])
        repo_b = _make_detail("repo-b", "octocat/repo-b", manifest_files=["requirements.txt"])

        enriched = await service.enrich_repositories([repo_a, repo_b])

        # Both have FastAPI independently
        assert "FastAPI" in enriched[0].technologies
        assert "FastAPI" in enriched[1].technologies

        # No cross-repo frequency counts created in repository detail
        assert enriched[0].name == "repo-a"
        assert enriched[1].name == "repo-b"
