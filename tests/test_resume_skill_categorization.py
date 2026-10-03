"""
test_resume_skill_categorization.py
-------------------------------------
Task 10.1 - Resume Skill Source Tracking and Categorization.

Focused tests for the new categorized_skills field added to ResumeAnalysisResponse.
"""

import sys
import unittest
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from app.services.resume_service import resume_service


class TestResumeSkillCategorization(unittest.TestCase):

    def _analyze(self, resume_text):
        return resume_service.analyze_resume(resume_text)

    def _categorized(self, resume_text):
        return self._analyze(resume_text)["categorized_skills"]

    def _get_skill(self, categorized, name):
        return next((s for s in categorized if s["name"] == name), None)

    def test_01_alias_normalization(self):
        resume = "TECHNICAL SKILLS\nreactjs, tensorflow, nodejs, sklearn\n"
        categorized = self._categorized(resume)
        names = [s["name"] for s in categorized]
        self.assertIn("React", names)
        self.assertIn("TensorFlow", names)
        self.assertIn("Node.js", names)
        self.assertIn("Scikit-learn", names)
        self.assertNotIn("reactjs", names)
        self.assertNotIn("sklearn", names)

    def test_02a_python_single_category(self):
        skill = self._get_skill(self._categorized("SKILLS\nPython\n"), "Python")
        self.assertIsNotNone(skill)
        self.assertIn("Programming Languages", skill["categories"])

    def test_02b_docker_single_category(self):
        skill = self._get_skill(self._categorized("SKILLS\nDocker\n"), "Docker")
        self.assertIsNotNone(skill)
        self.assertIn("DevOps & Cloud", skill["categories"])

    def test_03a_sql_multi_category(self):
        skill = self._get_skill(self._categorized("SKILLS\nSQL\n"), "SQL")
        self.assertIsNotNone(skill)
        self.assertIn("Programming Languages", skill["categories"])
        self.assertIn("Databases", skill["categories"])

    def test_03b_tensorflow_multi_category(self):
        skill = self._get_skill(self._categorized("SKILLS\nTensorFlow\n"), "TensorFlow")
        self.assertIsNotNone(skill)
        self.assertIn("Frameworks & Libraries", skill["categories"])
        self.assertIn("AI / Machine Learning", skill["categories"])

    def test_03c_bootstrap_multi_category(self):
        skill = self._get_skill(self._categorized("SKILLS\nBootstrap\n"), "Bootstrap")
        self.assertIsNotNone(skill)
        self.assertIn("Frameworks & Libraries", skill["categories"])
        self.assertIn("Web Technologies", skill["categories"])

    def test_03d_prisma_multi_category(self):
        skill = self._get_skill(self._categorized("SKILLS\nPrisma\n"), "Prisma")
        self.assertIsNotNone(skill)
        self.assertIn("Frameworks & Libraries", skill["categories"])
        self.assertIn("Databases", skill["categories"])

    def test_04a_html_web_technologies_only(self):
        skill = self._get_skill(self._categorized("SKILLS\nHTML\n"), "HTML")
        self.assertIsNotNone(skill)
        self.assertIn("Web Technologies", skill["categories"])
        self.assertNotIn("Programming Languages", skill["categories"])

    def test_04b_css_web_technologies_only(self):
        skill = self._get_skill(self._categorized("SKILLS\nCSS\n"), "CSS")
        self.assertIsNotNone(skill)
        self.assertIn("Web Technologies", skill["categories"])
        self.assertNotIn("Programming Languages", skill["categories"])

    def test_04c_junit_testing_qa(self):
        skill = self._get_skill(self._categorized("SKILLS\nJUnit\n"), "JUnit")
        self.assertIsNotNone(skill)
        self.assertIn("Testing & QA", skill["categories"])

    def test_04d_pytest_testing_qa(self):
        skill = self._get_skill(self._categorized("SKILLS\nPytest\n"), "Pytest")
        self.assertIsNotNone(skill)
        self.assertIn("Testing & QA", skill["categories"])

    def test_05_source_skills_section(self):
        resume = "TECHNICAL SKILLS\nPython, Docker\n"
        categorized = self._categorized(resume)
        python = self._get_skill(categorized, "Python")
        self.assertIsNotNone(python)
        self.assertIn("skills_section", python["sources"])

    def test_06_source_project_text(self):
        resume = "PROJECTS\nWeather Dashboard\nBuilt using React and Flask.\n"
        categorized = self._categorized(resume)
        react = self._get_skill(categorized, "React")
        self.assertIsNotNone(react)
        self.assertIn("project_text", react["sources"])
        flask = self._get_skill(categorized, "Flask")
        self.assertIsNotNone(flask)
        self.assertIn("project_text", flask["sources"])

    def test_07_source_experience_text(self):
        resume = ("EXPERIENCE\nSoftware Developer\nCompany ABC\nJune 2024 - August 2024\n"
                  "Developed REST API endpoints using FastAPI and PostgreSQL.\n")
        categorized = self._categorized(resume)
        fastapi = self._get_skill(categorized, "FastAPI")
        self.assertIsNotNone(fastapi)
        self.assertIn("experience_text", fastapi["sources"])
        pg = self._get_skill(categorized, "PostgreSQL")
        self.assertIsNotNone(pg)
        self.assertIn("experience_text", pg["sources"])

    def test_08a_three_sources_merged(self):
        resume = ("SKILLS\nPython\n\nPROJECTS\nData Pipeline\nETL pipeline written in Python and Pandas.\n\n"
                  "EXPERIENCE\nPython Intern\nCorp XYZ\nJune 2024 - August 2024\nAutomated tasks using Python.\n")
        categorized = self._categorized(resume)
        python = self._get_skill(categorized, "Python")
        self.assertIsNotNone(python)
        self.assertIn("skills_section", python["sources"])
        self.assertIn("project_text", python["sources"])
        self.assertIn("experience_text", python["sources"])
        self.assertEqual(len(python["sources"]), 3)

    def test_08b_two_sources_skills_and_project(self):
        resume = "SKILLS\nReact\n\nPROJECTS\nPortfolio\nFrontend built with React.\n"
        categorized = self._categorized(resume)
        react = self._get_skill(categorized, "React")
        self.assertIsNotNone(react)
        self.assertIn("skills_section", react["sources"])
        self.assertIn("project_text", react["sources"])
        self.assertEqual(len(react["sources"]), 2)

    def test_08c_two_sources_skills_and_experience(self):
        resume = ("SKILLS\nFastAPI\n\nEXPERIENCE\nBackend Dev\nStartup\nJan 2025 - Present\n"
                  "Built microservices with FastAPI.\n")
        categorized = self._categorized(resume)
        fastapi = self._get_skill(categorized, "FastAPI")
        self.assertIsNotNone(fastapi)
        self.assertIn("skills_section", fastapi["sources"])
        self.assertIn("experience_text", fastapi["sources"])

    def test_09a_flat_skills_list_unchanged(self):
        resume = "SKILLS\nPython, JavaScript, Docker\n"
        result = self._analyze(resume)
        self.assertIn("skills", result)
        self.assertIn("Python", result["skills"])
        self.assertIn("JavaScript", result["skills"])
        self.assertIn("Docker", result["skills"])

    def test_09b_categorized_skills_additive(self):
        resume = "SKILLS\nPython\n"
        result = self._analyze(resume)
        self.assertIn("skills", result)
        self.assertIn("categorized_skills", result)
        self.assertIn("Python", result["skills"])
        self.assertIn("Python", [s["name"] for s in result["categorized_skills"]])

    def test_09c_count_fields_present(self):
        result = self._analyze("SKILLS\nPython\n")
        self.assertIn("skill_count", result)
        self.assertIn("project_count", result)
        self.assertIn("experience_count", result)

    def test_09d_skill_count_matches_flat_list(self):
        result = self._analyze("SKILLS\nPython, Docker, React\n")
        self.assertEqual(result["skill_count"], len(result["skills"]))

    def test_09e_dedup_in_flat_list_unchanged(self):
        resume = "SKILLS\nPython, python, PYTHON, cpp, c++, C++, nodejs, Node.js, NODEJS\n"
        result = self._analyze(resume)
        self.assertEqual(result["skills"], ["Python", "C++", "Node.js"])

    def test_10_unknown_technology_tools_other(self):
        resume = "SKILLS\nmycustomtool\n"
        categorized = self._categorized(resume)
        self.assertGreater(len(categorized), 0)
        self.assertIn("Tools & Other", categorized[0]["categories"])

    def test_11a_alphabetical_ordering(self):
        resume = "SKILLS\nPython, React, Docker, Angular, Flask\n"
        categorized = self._categorized(resume)
        names = [s["name"] for s in categorized]
        self.assertEqual(names, sorted(names))

    def test_11b_sources_alphabetically_ordered(self):
        resume = "SKILLS\nPython\n\nPROJECTS\nDemo\nBuilt with Python.\n"
        categorized = self._categorized(resume)
        python = self._get_skill(categorized, "Python")
        self.assertIsNotNone(python)
        self.assertEqual(python["sources"], sorted(python["sources"]))

    def test_12a_no_duplicate_entries(self):
        resume = "SKILLS\nDocker, docker, DOCKER\n\nPROJECTS\nCI Pipeline\nContainerized with Docker.\n"
        categorized = self._categorized(resume)
        docker_entries = [s for s in categorized if s["name"] == "Docker"]
        self.assertEqual(len(docker_entries), 1)
        self.assertIn("skills_section", docker_entries[0]["sources"])
        self.assertIn("project_text", docker_entries[0]["sources"])

    def test_12b_all_names_unique(self):
        resume = "SKILLS\nPython, React, Docker, Python, python\n"
        categorized = self._categorized(resume)
        names = [s["name"] for s in categorized]
        self.assertEqual(len(names), len(set(names)))

    def test_13_empty_result_on_no_skills(self):
        resume = "SUMMARY\nPassionate professional with strong communication skills.\n"
        result = self._analyze(resume)
        self.assertEqual(result["categorized_skills"], [])
        self.assertEqual(result["skills"], [])

    def test_14_valid_source_labels_only(self):
        allowed = {"skills_section", "project_text", "experience_text"}
        resume = ("SKILLS\nPython, React\n\nPROJECTS\nApp\nBuilt with React and Python.\n\n"
                  "EXPERIENCE\nDeveloper\nCorp\nJune 2024 - Present\nWrote scripts in Python using FastAPI.\n")
        categorized = self._categorized(resume)
        self.assertGreater(len(categorized), 0)
        for skill in categorized:
            for src in skill["sources"]:
                self.assertIn(src, allowed, f"Unexpected source '{src}' on '{skill['name']}'")

    def test_15_rest_api_normalization_regression(self):
        """
        Regression: 'rest api' (space-separated, from multi-word scan) must normalize
        to 'REST API', identical to 'rest-api' (hyphen form).
        Before the fix, 'rest api' fell through to the capitalize path -> 'Rest Api'.
        """
        from app.services.technology_service import normalize_technology_name
        self.assertEqual(normalize_technology_name('rest api'), 'REST API')
        self.assertEqual(normalize_technology_name('rest-api'), 'REST API')
        self.assertEqual(normalize_technology_name('REST API'), 'REST API')

        resume = ('EXPERIENCE\nBackend Engineer\nCorp\nJune 2024 - Present\n'
                  'Designed REST API endpoints using FastAPI.\n')
        categorized = self._categorized(resume)
        names = [s['name'] for s in categorized]
        self.assertIn('REST API', names)
        self.assertNotIn('Rest Api', names)


if __name__ == "__main__":
    unittest.main()
