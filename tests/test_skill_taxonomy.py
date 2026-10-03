"""
Regression tests for skill taxonomy corrections:
- CSS classified under Web Technologies, NOT Programming Languages
- HTML classified under Web Technologies, NOT Programming Languages
- Hibernate classified under Frameworks & Libraries, NOT Tools & Other
- JUnit classified under Testing & QA, NOT Tools & Other
- SQL multi-category (Programming Languages + Databases) preserved
- Multi-category behavior preserved for TensorFlow, Bootstrap, Prisma
- Architectural capability labels preserved
"""
import pytest
from app.services.skill_profile_service import (
    _classify_technology,
    skill_profile_service,
    PROGRAMMING_LANGUAGES,
    WEB_TECHNOLOGIES,
    FRAMEWORKS_AND_LIBRARIES,
    TESTING_AND_QA,
    DATABASES,
    FALLBACK_CATEGORY,
)


class TestSkillTaxonomyCorrections:
    """Focused regression tests for taxonomy classification corrections."""

    def test_css_classification(self):
        """CSS must be in Web Technologies and NOT in Programming Languages."""
        categories = _classify_technology("CSS")
        assert "Web Technologies" in categories
        assert "Programming Languages" not in categories
        assert "CSS" not in PROGRAMMING_LANGUAGES
        assert "CSS" in WEB_TECHNOLOGIES

    def test_html_classification(self):
        """HTML must be in Web Technologies and NOT in Programming Languages."""
        categories = _classify_technology("HTML")
        assert "Web Technologies" in categories
        assert "Programming Languages" not in categories
        assert "HTML" not in PROGRAMMING_LANGUAGES
        assert "HTML" in WEB_TECHNOLOGIES

    def test_hibernate_classification(self):
        """Hibernate must be in Frameworks & Libraries and not fall through to Tools & Other."""
        categories = _classify_technology("Hibernate")
        assert "Frameworks & Libraries" in categories
        assert categories != [FALLBACK_CATEGORY]
        assert "Hibernate" in FRAMEWORKS_AND_LIBRARIES

    def test_junit_classification(self):
        """JUnit must be in Testing & QA and not fall through to Tools & Other."""
        categories = _classify_technology("JUnit")
        assert "Testing & QA" in categories
        assert categories != [FALLBACK_CATEGORY]
        assert "JUnit" in TESTING_AND_QA

    def test_sql_dual_classification_preserved(self):
        """SQL must remain under both Programming Languages and Databases."""
        categories = _classify_technology("SQL")
        assert "Programming Languages" in categories
        assert "Databases" in categories
        assert "SQL" in PROGRAMMING_LANGUAGES
        assert "SQL" in DATABASES

    def test_multi_category_behavior_preserved(self):
        """Multi-category technologies retain all expected categories."""
        # TensorFlow: Frameworks & Libraries + AI / Machine Learning
        tf_cats = _classify_technology("TensorFlow")
        assert "Frameworks & Libraries" in tf_cats
        assert "AI / Machine Learning" in tf_cats

        # Bootstrap: Frameworks & Libraries + Web Technologies
        bs_cats = _classify_technology("Bootstrap")
        assert "Frameworks & Libraries" in bs_cats
        assert "Web Technologies" in bs_cats

        # Prisma: Frameworks & Libraries + Databases
        prisma_cats = _classify_technology("Prisma")
        assert "Frameworks & Libraries" in prisma_cats
        assert "Databases" in prisma_cats

    def test_architectural_capability_labels_not_forced_into_tech_categories(self):
        """Architectural capability labels remain under fallback Tools & Other."""
        assert _classify_technology("Frontend Development") == [FALLBACK_CATEGORY]
        assert _classify_technology("Backend Development") == [FALLBACK_CATEGORY]
        assert _classify_technology("CLI Development") == [FALLBACK_CATEGORY]
        assert _classify_technology("DevOps & CI/CD") == [FALLBACK_CATEGORY]
        assert _classify_technology("Testing & QA") == [FALLBACK_CATEGORY]

    def test_skill_profile_service_build_profile_taxonomy(self):
        """SkillProfileService.build_skill_profile categorizes technologies correctly."""
        technologies = [
            {"name": "HTML", "repository_count": 2},
            {"name": "CSS", "repository_count": 2},
            {"name": "Hibernate", "repository_count": 1},
            {"name": "JUnit", "repository_count": 1},
            {"name": "Python", "repository_count": 3},
        ]
        profile = skill_profile_service.build_skill_profile(technologies, total_repositories=3)
        cat_map = {c["category"]: [s["name"] for s in c["skills"]] for c in profile["categories"]}

        # Python is in Programming Languages, but HTML/CSS are not
        assert "Python" in cat_map.get("Programming Languages", [])
        assert "HTML" not in cat_map.get("Programming Languages", [])
        assert "CSS" not in cat_map.get("Programming Languages", [])

        # HTML and CSS are in Web Technologies
        assert "HTML" in cat_map.get("Web Technologies", [])
        assert "CSS" in cat_map.get("Web Technologies", [])

        # Hibernate is in Frameworks & Libraries
        assert "Hibernate" in cat_map.get("Frameworks & Libraries", [])

        # JUnit is in Testing & QA
        assert "JUnit" in cat_map.get("Testing & QA", [])
