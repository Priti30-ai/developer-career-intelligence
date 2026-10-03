"""
github_evidence_service.py
--------------------------
Service for repository-level evidence extraction, technology detection,
and repository-level skill intelligence.

Target Workflow:
Inspected Repository (Task 4)
        ↓
Read identified manifest files (package.json, requirements.txt, Dockerfile, etc.)
        ↓
Extract STRONG evidence (declared dependencies, explicit configurations)
        ↓
Extract MODERATE evidence (detected languages, architecture structure)
        ↓
Extract WEAK evidence (repository topic tags)
        ↓
Derive canonical normalized technologies
        ↓
Infer repository-level skills & domain categories (via skill_profile_service)
        ↓
Populate RepositoryAnalysisDetail (technologies, skills, skill_categories, evidence)

Design Constraints:
1. Operates at the repository level; does NOT perform cross-repository aggregation.
2. Reuses technology_service.normalize_technology_name for canonical naming.
3. Reuses skill_profile_service for skill categorization.
4. Isolates failures: unreadable or malformed manifests do not crash analysis.
5. Deterministic output: sorted lists, deduplicated signals, stable ordering.
"""

import asyncio
import json
import re
from pathlib import PurePosixPath
from typing import Any, Dict, List, Optional, Set, Tuple, Union
import xml.etree.ElementTree as ET

# Built-in tomllib available in Python 3.11+
try:
    import tomllib
except ImportError:
    try:
        import tomli as tomllib  # type: ignore
    except ImportError:
        tomllib = None  # type: ignore

from app.schemas.github_account import (
    EVIDENCE_SOURCE_CONFIG,
    EVIDENCE_SOURCE_LANGUAGE,
    EVIDENCE_SOURCE_MANIFEST,
    EVIDENCE_SOURCE_README,
    EVIDENCE_SOURCE_STRUCTURE,
    EVIDENCE_SOURCE_TOPIC,
    EVIDENCE_STRENGTH_MODERATE,
    EVIDENCE_STRENGTH_STRONG,
    EVIDENCE_STRENGTH_WEAK,
    EvidenceSourceSignal,
    RepositoryAnalysisDetail,
)
from app.schemas.skill_profile import SkillCategoryResponse, SkillResponse
from app.services.github_service import GitHubAPIError, GitHubService, github_service
from app.services.skill_profile_service import (
    CATEGORY_DEFINITIONS,
    FALLBACK_CATEGORY,
    SkillProfileService,
    _classify_technology,
    skill_profile_service,
)
from app.services.technology_service import (
    TechnologyService,
    normalize_technology_name,
    technology_service,
)

# Priority mapping for sorting evidence signals
STRENGTH_RANK: Dict[str, int] = {
    EVIDENCE_STRENGTH_STRONG: 0,
    EVIDENCE_STRENGTH_MODERATE: 1,
    EVIDENCE_STRENGTH_WEAK: 2,
}

# Known architectural capability meta-labels to distinguish from raw technologies
ARCHITECTURAL_CAPABILITY_SKILLS: Dict[str, str] = {
    "FRONTEND": "Frontend Development",
    "BACKEND": "Backend Development",
    "DATABASE": "Database Management",
    "DEVOPS": "DevOps & CI/CD",
    "TESTING": "Testing & QA",
    "DATA_SCIENCE": "Data Science",
    "MACHINE_LEARNING": "Machine Learning",
    "CLI": "CLI Development",
}


class GitHubEvidenceService:
    """
    Dedicated service for repository-level evidence extraction,
    technology detection, and skill intelligence.
    """

    def __init__(
        self,
        service: Optional[GitHubService] = None,
        tech_service: Optional[TechnologyService] = None,
        skill_service: Optional[SkillProfileService] = None,
        max_manifest_fetches: int = 8,
    ):
        self.github_service = service or github_service
        self.technology_service = tech_service or technology_service
        self.skill_profile_service = skill_service or skill_profile_service
        self.max_manifest_fetches = max(1, max_manifest_fetches)

    # -------------------------------------------------------------------------
    # Manifest Parsers (Factual, Deterministic Dependency Extractors)
    # -------------------------------------------------------------------------

    def parse_package_json(
        self, content: str, path: str = "package.json"
    ) -> List[EvidenceSourceSignal]:
        """
        Extract declared dependencies from package.json with strong evidence.
        """
        signals: List[EvidenceSourceSignal] = []
        try:
            data = json.loads(content)
        except Exception:
            return signals

        if not isinstance(data, dict):
            return signals

        sections = [
            ("dependencies", data.get("dependencies", {})),
            ("devDependencies", data.get("devDependencies", {})),
            ("peerDependencies", data.get("peerDependencies", {})),
            ("optionalDependencies", data.get("optionalDependencies", {})),
        ]

        for section_name, section_dict in sections:
            if not isinstance(section_dict, dict):
                continue

            for pkg_name, version_spec in section_dict.items():
                if not isinstance(pkg_name, str) or not pkg_name.strip():
                    continue

                raw_pkg = pkg_name.strip()
                canonical_tech = self._resolve_js_package_to_tech(raw_pkg)
                if canonical_tech:
                    signals.append(
                        EvidenceSourceSignal(
                            source_type=EVIDENCE_SOURCE_MANIFEST,
                            technology=canonical_tech,
                            path=path,
                            strength=EVIDENCE_STRENGTH_STRONG,
                            reason=f"Declared dependency '{raw_pkg}' in {path} ({section_name})",
                            details={
                                "package": raw_pkg,
                                "section": section_name,
                                "version": str(version_spec),
                            },
                        )
                    )

        return signals

    def _resolve_js_package_to_tech(self, raw_pkg: str) -> Optional[str]:
        """Map npm package name to canonical normalized technology name."""
        pkg_lower = raw_pkg.lower()

        # Handle scoped packages
        if pkg_lower.startswith("@types/"):
            target = pkg_lower.replace("@types/", "")
        elif pkg_lower.startswith("@angular/"):
            return "Angular"
        elif pkg_lower.startswith("@nestjs/"):
            return "NestJS"
        elif pkg_lower.startswith("@prisma/"):
            return "Prisma"
        elif pkg_lower == "@tensorflow/tfjs" or pkg_lower.startswith("@tensorflow/"):
            return "TensorFlow.js"
        elif "/" in pkg_lower:
            parts = pkg_lower.split("/", 1)
            target = parts[1]
        else:
            target = pkg_lower

        # Strip react- prefix if present (e.g. react-router, react-redux)
        if target == "react-dom" or target == "react":
            return "React"
        if target == "react-native":
            return "React Native"

        normalized = normalize_technology_name(target)
        if normalized:
            # Check if recognized in category definitions or canonical alias
            matched = _classify_technology(normalized)
            if matched != [FALLBACK_CATEGORY] or normalized in {
                "Vite", "Axios", "Prisma", "Redux", "Jest", "Mocha", "Tailwind CSS",
            }:
                return normalized

        return None

    def parse_requirements_txt(
        self, content: str, path: str = "requirements.txt"
    ) -> List[EvidenceSourceSignal]:
        """
        Extract declared Python packages from requirements.txt with strong evidence.
        Strips version constraints, comments, options, and extras.
        """
        signals: List[EvidenceSourceSignal] = []

        for line in content.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            # Strip inline comments
            line = line.split("#")[0].strip()
            if not line:
                continue

            # Skip pip flags
            if line.startswith("-") or line.startswith("--"):
                continue

            # Split on version comparison operators: ==, >=, <=, ~=, !=, >, <, ===, @
            pkg_part = re.split(r"[<>=~@!]", line)[0].strip()
            # Strip extras like fastapi[all] -> fastapi
            pkg_part = re.sub(r"\[.*?\]", "", pkg_part).strip()

            if not pkg_part or not re.match(r"^[a-zA-Z0-9_.-]+$", pkg_part):
                continue

            canonical = normalize_technology_name(pkg_part)
            if canonical:
                # Confirm it is a recognized technology/library
                matched = _classify_technology(canonical)
                if matched != [FALLBACK_CATEGORY] or canonical in {
                    "FastAPI", "Pandas", "Scikit-learn", "PyTorch", "TensorFlow",
                    "Django", "Flask", "SQLAlchemy", "Pytest", "Pydantic", "Celery",
                    "HTTPX", "Requests", "Alembic", "NumPy", "SciPy",
                }:
                    signals.append(
                        EvidenceSourceSignal(
                            source_type=EVIDENCE_SOURCE_MANIFEST,
                            technology=canonical,
                            path=path,
                            strength=EVIDENCE_STRENGTH_STRONG,
                            reason=f"Declared dependency '{pkg_part}' in {path}",
                            details={"package": pkg_part, "raw_line": line},
                        )
                    )

        return signals

    def parse_pyproject_toml(
        self, content: str, path: str = "pyproject.toml"
    ) -> List[EvidenceSourceSignal]:
        """
        Extract declared dependencies from pyproject.toml (PEP 621 and Poetry).
        """
        signals: List[EvidenceSourceSignal] = []
        if tomllib is None:
            return self._parse_toml_fallback(content, path)

        try:
            data = tomllib.loads(content)
        except Exception:
            return self._parse_toml_fallback(content, path)

        raw_packages: Set[str] = set()

        # 1. PEP 621 [project.dependencies]
        project_deps = data.get("project", {}).get("dependencies", [])
        if isinstance(project_deps, list):
            for dep in project_deps:
                if isinstance(dep, str):
                    pkg = re.split(r"[<>=~@!]", dep)[0].strip()
                    pkg = re.sub(r"\[.*?\]", "", pkg).strip()
                    if pkg:
                        raw_packages.add(pkg)

        # 2. Poetry [tool.poetry.dependencies]
        poetry_deps = (
            data.get("tool", {}).get("poetry", {}).get("dependencies", {})
        )
        if isinstance(poetry_deps, dict):
            for pkg in poetry_deps.keys():
                if pkg.lower() != "python":
                    raw_packages.add(pkg)

        # 3. Poetry [tool.poetry.group.*.dependencies]
        groups = data.get("tool", {}).get("poetry", {}).get("group", {})
        if isinstance(groups, dict):
            for group_name, group_data in groups.items():
                if isinstance(group_data, dict):
                    deps = group_data.get("dependencies", {})
                    if isinstance(deps, dict):
                        for pkg in deps.keys():
                            raw_packages.add(pkg)

        for pkg in sorted(list(raw_packages)):
            canonical = normalize_technology_name(pkg)
            if canonical:
                signals.append(
                    EvidenceSourceSignal(
                        source_type=EVIDENCE_SOURCE_MANIFEST,
                        technology=canonical,
                        path=path,
                        strength=EVIDENCE_STRENGTH_STRONG,
                        reason=f"Declared dependency '{pkg}' in {path}",
                        details={"package": pkg},
                    )
                )

        return signals

    def _parse_toml_fallback(self, content: str, path: str) -> List[EvidenceSourceSignal]:
        """Line-based fallback for TOML files when tomllib is unavailable or syntax is loose."""
        signals: List[EvidenceSourceSignal] = []
        in_deps = False

        for line in content.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            if line.startswith("[") and line.endswith("]"):
                in_deps = any(
                    k in line.lower()
                    for k in ("dependencies", "poetry.dependencies", "packages")
                )
                continue

            if in_deps and "=" in line:
                pkg = line.split("=")[0].strip().strip('"').strip("'")
                if pkg and pkg.lower() != "python" and re.match(r"^[a-zA-Z0-9_.-]+$", pkg):
                    canonical = normalize_technology_name(pkg)
                    if canonical:
                        signals.append(
                            EvidenceSourceSignal(
                                source_type=EVIDENCE_SOURCE_MANIFEST,
                                technology=canonical,
                                path=path,
                                strength=EVIDENCE_STRENGTH_STRONG,
                                reason=f"Declared dependency '{pkg}' in {path}",
                                details={"package": pkg},
                            )
                        )

        return signals

    def parse_pipfile(
        self, content: str, path: str = "Pipfile"
    ) -> List[EvidenceSourceSignal]:
        """Extract declared dependencies from Pipfile."""
        signals: List[EvidenceSourceSignal] = []
        in_packages = False

        for line in content.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            if line.startswith("[") and line.endswith("]"):
                in_packages = line.lower() in ("[packages]", "[dev-packages]")
                continue

            if in_packages and "=" in line:
                pkg = line.split("=")[0].strip().strip('"').strip("'")
                if pkg and pkg.lower() != "python":
                    canonical = normalize_technology_name(pkg)
                    if canonical:
                        signals.append(
                            EvidenceSourceSignal(
                                source_type=EVIDENCE_SOURCE_MANIFEST,
                                technology=canonical,
                                path=path,
                                strength=EVIDENCE_STRENGTH_STRONG,
                                reason=f"Declared Pipfile package '{pkg}' in {path}",
                                details={"package": pkg},
                            )
                        )

        return signals

    def parse_pom_xml(
        self, content: str, path: str = "pom.xml"
    ) -> List[EvidenceSourceSignal]:
        """Extract declared dependencies from Maven pom.xml."""
        signals: List[EvidenceSourceSignal] = []
        try:
            root = ET.fromstring(content)
        except Exception:
            return signals

        # Strip XML namespaces for uniform querying
        for elem in root.iter():
            if "}" in elem.tag:
                elem.tag = elem.tag.split("}", 1)[1]

        for dep in root.findall(".//dependency"):
            artifact_elem = dep.find("artifactId")
            if artifact_elem is not None and artifact_elem.text:
                artifact = artifact_elem.text.strip().lower()
                tech = None
                if "spring-boot" in artifact:
                    tech = "Spring Boot"
                elif "spring" in artifact:
                    tech = "Spring"
                elif "postgres" in artifact:
                    tech = "PostgreSQL"
                elif "mysql" in artifact:
                    tech = "MySQL"
                elif "junit" in artifact:
                    tech = "JUnit"
                elif "hibernate" in artifact:
                    tech = "Hibernate"
                elif "lombok" in artifact:
                    tech = "Lombok"
                else:
                    norm = normalize_technology_name(artifact)
                    if norm and _classify_technology(norm) != [FALLBACK_CATEGORY]:
                        tech = norm

                if tech:
                    signals.append(
                        EvidenceSourceSignal(
                            source_type=EVIDENCE_SOURCE_MANIFEST,
                            technology=tech,
                            path=path,
                            strength=EVIDENCE_STRENGTH_STRONG,
                            reason=f"Declared Maven dependency '{artifact}' in {path}",
                            details={"artifactId": artifact},
                        )
                    )

        return signals

    def parse_build_gradle(
        self, content: str, path: str = "build.gradle"
    ) -> List[EvidenceSourceSignal]:
        """Extract dependencies from build.gradle or build.gradle.kts."""
        signals: List[EvidenceSourceSignal] = []

        pattern = re.compile(
            r"""(?:implementation|api|testImplementation|compileOnly)\s*\(?['"]([^'"]+)['"]\)? """,
            re.VERBOSE,
        )

        for match in pattern.finditer(content):
            dep_str = match.group(1).lower()
            tech = None
            if "spring-boot" in dep_str:
                tech = "Spring Boot"
            elif "spring" in dep_str:
                tech = "Spring"
            elif "postgresql" in dep_str:
                tech = "PostgreSQL"
            elif "mysql" in dep_str:
                tech = "MySQL"
            elif "junit" in dep_str:
                tech = "JUnit"
            else:
                parts = dep_str.split(":")
                artifact = parts[1] if len(parts) > 1 else parts[0]
                norm = normalize_technology_name(artifact)
                if norm and _classify_technology(norm) != [FALLBACK_CATEGORY]:
                    tech = norm

            if tech:
                signals.append(
                    EvidenceSourceSignal(
                        source_type=EVIDENCE_SOURCE_MANIFEST,
                        technology=tech,
                        path=path,
                        strength=EVIDENCE_STRENGTH_STRONG,
                        reason=f"Declared Gradle dependency '{dep_str}' in {path}",
                        details={"dependency": dep_str},
                    )
                )

        return signals

    def parse_go_mod(
        self, content: str, path: str = "go.mod"
    ) -> List[EvidenceSourceSignal]:
        """Extract declared Go modules from go.mod."""
        signals: List[EvidenceSourceSignal] = []

        in_require = False
        for line in content.splitlines():
            line = line.strip()
            if not line or line.startswith("//"):
                continue

            if line.startswith("require ("):
                in_require = True
                continue
            if in_require and line == ")":
                in_require = False
                continue

            dep_module = None
            if in_require:
                parts = line.split()
                if parts:
                    dep_module = parts[0]
            elif line.startswith("require "):
                parts = line.split()
                if len(parts) > 1:
                    dep_module = parts[1]

            if dep_module:
                mod_lower = dep_module.lower()
                tech = None
                if "gin-gonic/gin" in mod_lower:
                    tech = "Gin"
                elif "gofiber/fiber" in mod_lower:
                    tech = "Fiber"
                elif "gorm.io" in mod_lower or "jinzhu/gorm" in mod_lower:
                    tech = "GORM"
                elif "stretchr/testify" in mod_lower:
                    tech = "Testify"
                else:
                    pkg_leaf = mod_lower.split("/")[-1]
                    norm = normalize_technology_name(pkg_leaf)
                    if norm and _classify_technology(norm) != [FALLBACK_CATEGORY]:
                        tech = norm

                if tech:
                    signals.append(
                        EvidenceSourceSignal(
                            source_type=EVIDENCE_SOURCE_MANIFEST,
                            technology=tech,
                            path=path,
                            strength=EVIDENCE_STRENGTH_STRONG,
                            reason=f"Declared Go module '{dep_module}' in {path}",
                            details={"module": dep_module},
                        )
                    )

        return signals

    def parse_cargo_toml(
        self, content: str, path: str = "Cargo.toml"
    ) -> List[EvidenceSourceSignal]:
        """Extract Rust dependencies from Cargo.toml."""
        signals: List[EvidenceSourceSignal] = []
        if tomllib is None:
            return self._parse_toml_fallback(content, path)

        try:
            data = tomllib.loads(content)
        except Exception:
            return self._parse_toml_fallback(content, path)

        crates: Set[str] = set()
        for section in ("dependencies", "dev-dependencies", "build-dependencies"):
            sec_dict = data.get(section, {})
            if isinstance(sec_dict, dict):
                crates.update(sec_dict.keys())

        for crate in sorted(list(crates)):
            c_lower = crate.lower()
            tech = None
            if c_lower == "actix-web":
                tech = "Actix Web"
            elif c_lower == "tokio":
                tech = "Tokio"
            elif c_lower == "serde":
                tech = "Serde"
            else:
                norm = normalize_technology_name(crate)
                if norm and _classify_technology(norm) != [FALLBACK_CATEGORY]:
                    tech = norm

            if tech:
                signals.append(
                    EvidenceSourceSignal(
                        source_type=EVIDENCE_SOURCE_MANIFEST,
                        technology=tech,
                        path=path,
                        strength=EVIDENCE_STRENGTH_STRONG,
                        reason=f"Declared Cargo crate '{crate}' in {path}",
                        details={"crate": crate},
                    )
                )

        return signals

    def parse_dockerfile(
        self, content: str, path: str = "Dockerfile"
    ) -> List[EvidenceSourceSignal]:
        """Extract base image and container evidence from Dockerfile."""
        signals: List[EvidenceSourceSignal] = []

        # Always add Docker configuration evidence
        signals.append(
            EvidenceSourceSignal(
                source_type=EVIDENCE_SOURCE_CONFIG,
                technology="Docker",
                path=path,
                strength=EVIDENCE_STRENGTH_STRONG,
                reason=f"Container specification defined in {path}",
                details={"file": path},
            )
        )

        for line in content.splitlines():
            line = line.strip()
            if line.upper().startswith("FROM "):
                parts = line.split()
                if len(parts) > 1:
                    base_image = parts[1].split(":")[0].lower()
                    tech = None
                    if "python" in base_image:
                        tech = "Python"
                    elif "node" in base_image:
                        tech = "Node.js"
                    elif "golang" in base_image:
                        tech = "Go"
                    elif "rust" in base_image:
                        tech = "Rust"
                    elif any(j in base_image for j in ("openjdk", "temurin", "java")):
                        tech = "Java"
                    elif "nginx" in base_image:
                        tech = "Nginx"
                    elif "redis" in base_image:
                        tech = "Redis"
                    elif "postgres" in base_image:
                        tech = "PostgreSQL"

                    if tech:
                        signals.append(
                            EvidenceSourceSignal(
                                source_type=EVIDENCE_SOURCE_CONFIG,
                                technology=tech,
                                path=path,
                                strength=EVIDENCE_STRENGTH_STRONG,
                                reason=f"Container base image '{parts[1]}' in {path}",
                                details={"base_image": parts[1]},
                            )
                        )

        return signals

    def parse_docker_compose(
        self, content: str, path: str = "docker-compose.yml"
    ) -> List[EvidenceSourceSignal]:
        """Extract container and service images from docker-compose.yml."""
        signals: List[EvidenceSourceSignal] = []

        signals.append(
            EvidenceSourceSignal(
                source_type=EVIDENCE_SOURCE_CONFIG,
                technology="Docker",
                path=path,
                strength=EVIDENCE_STRENGTH_STRONG,
                reason=f"Multi-container service definition in {path}",
                details={"file": path},
            )
        )

        for line in content.splitlines():
            line = line.strip()
            if line.startswith("image:"):
                img_part = line.split("image:")[1].strip().strip('"').strip("'")
                img_name = img_part.split(":")[0].lower()

                tech = None
                if "postgres" in img_name:
                    tech = "PostgreSQL"
                elif "redis" in img_name:
                    tech = "Redis"
                elif "mysql" in img_name:
                    tech = "MySQL"
                elif "mongo" in img_name:
                    tech = "MongoDB"
                elif "nginx" in img_name:
                    tech = "Nginx"
                elif "rabbitmq" in img_name:
                    tech = "RabbitMQ"
                elif "kafka" in img_name:
                    tech = "Apache Kafka"

                if tech:
                    signals.append(
                        EvidenceSourceSignal(
                            source_type=EVIDENCE_SOURCE_CONFIG,
                            technology=tech,
                            path=path,
                            strength=EVIDENCE_STRENGTH_STRONG,
                            reason=f"Containerized service image '{img_part}' in {path}",
                            details={"image": img_part},
                        )
                    )

        return signals

    def parse_tsconfig(
        self, content: str, path: str = "tsconfig.json"
    ) -> List[EvidenceSourceSignal]:
        """Extract TypeScript configuration evidence from tsconfig.json."""
        return [
            EvidenceSourceSignal(
                source_type=EVIDENCE_SOURCE_CONFIG,
                technology="TypeScript",
                path=path,
                strength=EVIDENCE_STRENGTH_STRONG,
                reason=f"TypeScript compiler configuration defined in {path}",
                details={"file": path},
            )
        ]

    # -------------------------------------------------------------------------
    # Auxiliary Evidence Extractors (Languages, Structure, Topics)
    # -------------------------------------------------------------------------

    def extract_language_evidence(
        self, languages: List[str]
    ) -> List[EvidenceSourceSignal]:
        """Generate MODERATE evidence signals for detected programming languages."""
        signals: List[EvidenceSourceSignal] = []
        for lang in languages:
            norm_lang = normalize_technology_name(lang)
            if norm_lang:
                signals.append(
                    EvidenceSourceSignal(
                        source_type=EVIDENCE_SOURCE_LANGUAGE,
                        technology=norm_lang,
                        path=None,
                        strength=EVIDENCE_STRENGTH_MODERATE,
                        reason=f"Source code language detected in repository: {lang}",
                        details={"language": lang},
                    )
                )
        return signals

    def extract_structure_evidence(
        self, repo: RepositoryAnalysisDetail
    ) -> List[EvidenceSourceSignal]:
        """Generate MODERATE evidence signals based on architecture signals from Task 4."""
        signals: List[EvidenceSourceSignal] = []
        for signal in repo.architecture_signals:
            capability_skill = ARCHITECTURAL_CAPABILITY_SKILLS.get(signal.type)
            if capability_skill:
                signals.append(
                    EvidenceSourceSignal(
                        source_type=EVIDENCE_SOURCE_STRUCTURE,
                        technology=capability_skill,
                        path=signal.evidence[0] if signal.evidence else None,
                        strength=EVIDENCE_STRENGTH_MODERATE,
                        reason=signal.description,
                        details={"evidence_paths": signal.evidence},
                    )
                )
        return signals

    def extract_topic_evidence(
        self, topics: List[str]
    ) -> List[EvidenceSourceSignal]:
        """Generate WEAK contextual evidence signals for repository topic tags."""
        signals: List[EvidenceSourceSignal] = []
        for topic in topics:
            norm_topic = normalize_technology_name(topic)
            if norm_topic:
                signals.append(
                    EvidenceSourceSignal(
                        source_type=EVIDENCE_SOURCE_TOPIC,
                        technology=norm_topic,
                        path=None,
                        strength=EVIDENCE_STRENGTH_WEAK,
                        reason=f"Repository topic tag '{topic}'",
                        details={"topic": topic},
                    )
                )
        return signals

    # -------------------------------------------------------------------------
    # Deduplication & Ordering
    # -------------------------------------------------------------------------

    def _deduplicate_evidence(
        self, signals: List[EvidenceSourceSignal]
    ) -> List[EvidenceSourceSignal]:
        """
        Deduplicate evidence signals by (technology, source_type, path).
        Preserves strongest signal when duplicates exist and sorts deterministically.
        """
        best_signals: Dict[Tuple[str, str, Optional[str]], EvidenceSourceSignal] = {}

        for signal in signals:
            key = (signal.technology, signal.source_type, signal.path)
            if key not in best_signals:
                best_signals[key] = signal
            else:
                existing = best_signals[key]
                if STRENGTH_RANK.get(signal.strength, 3) < STRENGTH_RANK.get(
                    existing.strength, 3
                ):
                    best_signals[key] = signal

        # Sort deterministically: Strength rank (STRONG=0, MODERATE=1, WEAK=2), then tech name, then path
        return sorted(
            best_signals.values(),
            key=lambda s: (
                STRENGTH_RANK.get(s.strength, 3),
                s.technology,
                s.source_type,
                s.path or "",
            ),
        )

    def _infer_repository_skills(
        self,
        technologies: List[str],
        architecture_signals: List[EvidenceSourceSignal],
    ) -> Tuple[List[str], List[SkillCategoryResponse]]:
        """
        Infer repository-level skills and standardized category groups
        using skill_profile_service definitions.
        """
        skill_set: Set[str] = set(technologies)

        # Include confirmed structural capabilities
        for s in architecture_signals:
            if s.source_type == EVIDENCE_SOURCE_STRUCTURE:
                skill_set.add(s.technology)

        sorted_skills = sorted(list(skill_set))

        # Build categorized skills bucketed into domain categories
        category_buckets: Dict[str, List[SkillResponse]] = {
            cat_name: [] for cat_name, _ in CATEGORY_DEFINITIONS
        }
        category_buckets[FALLBACK_CATEGORY] = []

        for skill in sorted_skills:
            matched_cats = _classify_technology(skill)
            for cat in matched_cats:
                if cat in category_buckets:
                    category_buckets[cat].append(
                        SkillResponse(name=skill, repository_count=1)
                    )

        skill_categories: List[SkillCategoryResponse] = []
        for cat_name, _ in CATEGORY_DEFINITIONS:
            items = category_buckets[cat_name]
            if items:
                skill_categories.append(
                    SkillCategoryResponse(
                        category=cat_name,
                        skills=sorted(items, key=lambda x: x.name),
                    )
                )

        if category_buckets[FALLBACK_CATEGORY]:
            skill_categories.append(
                SkillCategoryResponse(
                    category=FALLBACK_CATEGORY,
                    skills=sorted(category_buckets[FALLBACK_CATEGORY], key=lambda x: x.name),
                )
            )

        return sorted_skills, skill_categories

    # -------------------------------------------------------------------------
    # Core Orchestration (Repository-Level Analysis)
    # -------------------------------------------------------------------------

    async def enrich_repository(
        self,
        repo: Union[RepositoryAnalysisDetail, Dict[str, Any]],
        owner: Optional[str] = None,
        fetch_manifests: bool = True,
    ) -> RepositoryAnalysisDetail:
        """
        Enrich a single repository analysis with technologies, skills, and evidence.

        Args:
            repo: RepositoryAnalysisDetail model from Task 4 inspection.
            owner: Fallback owner if repo.full_name is unqualified.
            fetch_manifests: If True, fetches lightweight manifest content via GitHub API.

        Returns:
            Updated RepositoryAnalysisDetail populated with technologies, skills,
            skill_categories, and explicit evidence signals.
        """
        if isinstance(repo, dict):
            detail = RepositoryAnalysisDetail(**repo)
        else:
            detail = repo.model_copy(deep=True)

        # Skip empty or errored repositories gracefully
        if detail.is_empty or detail.analysis_status == "ERROR":
            detail.technologies = []
            detail.skills = []
            detail.skill_categories = []
            detail.evidence = []
            return detail

        # Resolve owner and repository name
        if "/" in (detail.full_name or ""):
            resolved_owner, repo_name = detail.full_name.split("/", 1)
        else:
            resolved_owner = owner or detail.full_name
            repo_name = detail.name

        all_evidence: List[EvidenceSourceSignal] = []

        # 1. Manifest evidence
        if fetch_manifests and detail.manifest_files:
            # Select relevant manifests up to safety ceiling
            selected_manifests = [
                m
                for m in detail.manifest_files
                if any(
                    k in PurePosixPath(m).name.lower()
                    for k in (
                        "package.json",
                        "requirements",
                        "pyproject.toml",
                        "pipfile",
                        "pom.xml",
                        "build.gradle",
                        "go.mod",
                        "cargo.toml",
                        "dockerfile",
                        "docker-compose",
                        "tsconfig.json",
                    )
                )
            ][: self.max_manifest_fetches]

            for manifest_path in selected_manifests:
                try:
                    content = await self.github_service.get_repository_file_content(
                        resolved_owner,
                        repo_name,
                        manifest_path,
                        branch=detail.default_branch,
                    )
                except Exception as exc:
                    detail.warnings.append(
                        f"Failed to fetch manifest '{manifest_path}': {str(exc)}"
                    )
                    detail.is_partial = True
                    continue

                if content is None:
                    detail.warnings.append(
                        f"Manifest file '{manifest_path}' returned empty or not found"
                    )
                    continue

                # Parse according to manifest type
                fname = PurePosixPath(manifest_path).name.lower()
                manifest_signals: List[EvidenceSourceSignal] = []

                if fname == "package.json":
                    manifest_signals = self.parse_package_json(content, path=manifest_path)
                elif "requirements" in fname and fname.endswith(".txt"):
                    manifest_signals = self.parse_requirements_txt(content, path=manifest_path)
                elif fname == "pyproject.toml":
                    manifest_signals = self.parse_pyproject_toml(content, path=manifest_path)
                elif fname.lower() == "pipfile":
                    manifest_signals = self.parse_pipfile(content, path=manifest_path)
                elif fname == "pom.xml":
                    manifest_signals = self.parse_pom_xml(content, path=manifest_path)
                elif fname.startswith("build.gradle"):
                    manifest_signals = self.parse_build_gradle(content, path=manifest_path)
                elif fname == "go.mod":
                    manifest_signals = self.parse_go_mod(content, path=manifest_path)
                elif fname == "cargo.toml":
                    manifest_signals = self.parse_cargo_toml(content, path=manifest_path)
                elif "dockerfile" in fname:
                    manifest_signals = self.parse_dockerfile(content, path=manifest_path)
                elif "docker-compose" in fname:
                    manifest_signals = self.parse_docker_compose(content, path=manifest_path)
                elif fname == "tsconfig.json":
                    manifest_signals = self.parse_tsconfig(content, path=manifest_path)

                all_evidence.extend(manifest_signals)

        # 2. Language evidence
        all_evidence.extend(self.extract_language_evidence(detail.languages))

        # 3. Project structure evidence
        structure_signals = self.extract_structure_evidence(detail)
        all_evidence.extend(structure_signals)

        # 4. Topic evidence
        all_evidence.extend(self.extract_topic_evidence(detail.topics))

        # 5. Deduplicate and order evidence
        deduped_evidence = self._deduplicate_evidence(all_evidence)
        detail.evidence = deduped_evidence

        # 6. Extract canonical technologies (filtering out meta capability labels)
        raw_tech_names = {
            sig.technology
            for sig in deduped_evidence
            if sig.source_type != EVIDENCE_SOURCE_STRUCTURE
        }
        detail.technologies = sorted(list(raw_tech_names))

        # 7. Infer repository skills & skill categories
        skills, skill_cats = self._infer_repository_skills(
            detail.technologies, structure_signals
        )
        detail.skills = skills
        detail.skill_categories = skill_cats

        return detail

    async def enrich_repositories(
        self,
        repositories: List[RepositoryAnalysisDetail],
        default_owner: Optional[str] = None,
        fetch_manifests: bool = True,
        concurrency_limit: int = 5,
    ) -> List[RepositoryAnalysisDetail]:
        """
        Enrich multiple repositories with bounded concurrency.
        Isolates failures so that one repository's error does not affect others.
        """
        semaphore = asyncio.Semaphore(max(1, concurrency_limit))

        async def _bounded_enrich(r: RepositoryAnalysisDetail) -> RepositoryAnalysisDetail:
            async with semaphore:
                return await self.enrich_repository(
                    r, owner=default_owner, fetch_manifests=fetch_manifests
                )

        tasks = [_bounded_enrich(repo) for repo in repositories]
        return await asyncio.gather(*tasks)


# Singleton instance for route and service consumption
github_evidence_service = GitHubEvidenceService()
