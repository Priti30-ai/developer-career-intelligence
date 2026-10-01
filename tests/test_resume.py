"""
test_resume.py
--------------
Unit and integration tests for Resume Analysis module.

Tests:
1. Valid resume parsing
2. Empty resume rejection
3. Whitespace-only resume rejection
4. Skill extraction
5. Skill normalization
6. Duplicate skill removal
7. Section detection (heading variations)
8. Project extraction
9. Education extraction
10. Experience extraction
11. Certification extraction
12. API response structure and contract
"""

import sys
import unittest
from pathlib import Path

# Add backend directory to sys.path so 'app' imports resolve cleanly
backend_dir = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.main import app
from app.schemas.resume import ResumeAnalysisRequest
from app.services.resume_service import resume_service


SAMPLE_RESUME = """SUMMARY
Computer engineering student interested in AI and data science.

TECHNICAL SKILLS
Python, C++, SQL, Pandas, NumPy, Machine Learning

EDUCATION
Government Polytechnic Nashik
Diploma in Computer Technology
2022 - 2025

PROJECTS
Fake Profile Detection
Built a machine learning system using Random Forest.

EXPERIENCE
Python Intern
Company XYZ
June 2025 - August 2025

CERTIFICATIONS
Python Certification
AWS Certified Cloud Practitioner

ACHIEVEMENTS
First place in State Level Hackathon 2024
"""


class TestResumeAnalysis(unittest.TestCase):
    """Test suite for Resume Analysis parsing, normalization, and API routes."""

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_01_valid_resume_parsing(self):
        """Test 1: Valid resume parses all standard sections into structured output."""
        result = resume_service.analyze_resume(SAMPLE_RESUME)

        self.assertIsNotNone(result)
        self.assertIn("AI and data science", result["summary"])
        self.assertEqual(result["skill_count"], len(result["skills"]))
        self.assertEqual(result["project_count"], len(result["projects"]))
        self.assertEqual(result["experience_count"], len(result["experience"]))
        self.assertGreater(result["skill_count"], 0)
        self.assertGreater(result["project_count"], 0)
        self.assertGreater(result["experience_count"], 0)
        self.assertGreater(len(result["education"]), 0)
        self.assertGreater(len(result["certifications"]), 0)
        self.assertGreater(len(result["achievements"]), 0)

    def test_02_empty_resume_rejection(self):
        """Test 2: Empty resume text is rejected by schema validator and API."""
        with self.assertRaises(ValidationError):
            ResumeAnalysisRequest(resume_text="")

        response = self.client.post("/api/v1/resume/analyze", json={"resume_text": ""})
        self.assertEqual(response.status_code, 422)

    def test_03_whitespace_only_resume_rejection(self):
        """Test 3: Whitespace-only resume text is rejected by schema validator and API."""
        with self.assertRaises(ValidationError):
            ResumeAnalysisRequest(resume_text="   \n\t   \n  ")

        response = self.client.post(
            "/api/v1/resume/analyze",
            json={"resume_text": "   \n\t   \n  "},
        )
        self.assertEqual(response.status_code, 422)

    def test_04_skill_extraction(self):
        """Test 4: Explicit skills in SKILLS section are cleanly extracted."""
        resume = """SKILLS
Python, JavaScript, Docker, Kubernetes, SQL
"""
        result = resume_service.analyze_resume(resume)
        expected = ["Python", "JavaScript", "Docker", "Kubernetes", "SQL"]
        for skill in expected:
            self.assertIn(skill, result["skills"])

    def test_05_skill_normalization(self):
        """Test 5: Aliases are normalized to canonical project catalog names."""
        resume = """TECHNICAL SKILLS
python, cpp, c++, nodejs, scikit-learn, sklearn, reactjs, rest-api
"""
        result = resume_service.analyze_resume(resume)
        # python -> Python
        self.assertIn("Python", result["skills"])
        # cpp, c++ -> C++
        self.assertIn("C++", result["skills"])
        # nodejs -> Node.js
        self.assertIn("Node.js", result["skills"])
        # scikit-learn, sklearn -> Scikit-learn
        self.assertIn("Scikit-learn", result["skills"])
        # reactjs -> React
        self.assertIn("React", result["skills"])
        # rest-api -> REST API
        self.assertIn("REST API", result["skills"])

    def test_06_duplicate_skill_removal(self):
        """Test 6: Duplicate skills and casing/alias variations are deduplicated."""
        resume = """SKILLS
Python, python, PYTHON, cpp, c++, C++, nodejs, Node.js, NODEJS
"""
        result = resume_service.analyze_resume(resume)
        self.assertEqual(len(result["skills"]), 3)
        self.assertEqual(result["skills"], ["Python", "C++", "Node.js"])

    def test_07_section_detection_variations(self):
        """Test 7: Headings with varied casing, prefixes, and synonyms are detected."""
        resume = """### About Me
Passionate backend engineer with 3 years experience.

CORE COMPETENCIES
FastAPI, PostgreSQL, Redis, Docker

ACADEMIC QUALIFICATIONS
Pune University
Bachelor of Engineering in Information Technology
2019 - 2023

WORK HISTORY
Software Engineer
Tech Corp
Jan 2023 - Present
Developed high performance microservices.

NOTABLE PROJECTS
E-Commerce API
Built payment checkout microservice using FastAPI and Redis.

LICENSES & CERTIFICATIONS
AWS Solutions Architect Associate

HONORS & AWARDS
Best Innovation Award 2023
"""
        result = resume_service.analyze_resume(resume)
        self.assertIsNotNone(result["summary"])
        self.assertIn("backend engineer", result["summary"])
        self.assertIn("FastAPI", result["skills"])
        self.assertEqual(len(result["education"]), 1)
        self.assertEqual(result["education"][0]["institution"], "Pune University")
        self.assertEqual(len(result["experience"]), 1)
        self.assertEqual(result["experience"][0]["company"], "Tech Corp")
        self.assertEqual(len(result["projects"]), 1)
        self.assertEqual(result["projects"][0]["name"], "E-Commerce API")
        self.assertEqual(len(result["certifications"]), 1)
        self.assertEqual(len(result["achievements"]), 1)

    def test_08_project_extraction(self):
        """Test 8: Project names, descriptions, and mentioned technologies are extracted."""
        resume = """PROJECTS
Fake Profile Detection
Built a machine learning system using Random Forest.

Cloud Dashboard: Monitoring tool built using React and Docker.
"""
        result = resume_service.analyze_resume(resume)
        self.assertEqual(len(result["projects"]), 2)

        proj1 = result["projects"][0]
        self.assertEqual(proj1["name"], "Fake Profile Detection")
        self.assertIn("Random Forest", proj1["description"])
        self.assertIn("Machine Learning", proj1["technologies"])

        proj2 = result["projects"][1]
        self.assertEqual(proj2["name"], "Cloud Dashboard")
        self.assertIn("Monitoring tool", proj2["description"])
        self.assertIn("React", proj2["technologies"])
        self.assertIn("Docker", proj2["technologies"])

    def test_09_education_extraction(self):
        """Test 9: Education institution, degree, field of study, and years are parsed."""
        resume = """EDUCATION
Government Polytechnic Nashik
Diploma in Computer Technology
2022 - 2025
"""
        result = resume_service.analyze_resume(resume)
        self.assertEqual(len(result["education"]), 1)
        edu = result["education"][0]
        self.assertEqual(edu["institution"], "Government Polytechnic Nashik")
        self.assertEqual(edu["degree"], "Diploma")
        self.assertEqual(edu["field_of_study"], "Computer Technology")
        self.assertEqual(edu["start_year"], "2022")
        self.assertEqual(edu["end_year"], "2025")

    def test_10_experience_extraction(self):
        """Test 10: Experience company, role, dates, and responsibilities are parsed."""
        resume = """EXPERIENCE
Python Intern
Company XYZ
June 2025 - August 2025
Developed automated data processing pipelines using Pandas.
"""
        result = resume_service.analyze_resume(resume)
        self.assertEqual(len(result["experience"]), 1)
        exp = result["experience"][0]
        self.assertEqual(exp["role"], "Python Intern")
        self.assertEqual(exp["company"], "Company XYZ")
        self.assertEqual(exp["start_date"], "June 2025")
        self.assertEqual(exp["end_date"], "August 2025")
        self.assertIn("data processing pipelines", exp["description"])

    def test_11_certification_extraction(self):
        """Test 11: Certifications are extracted as clean bullet items."""
        resume = """CERTIFICATIONS
• Python Certification
• AWS Certified Developer - Associate
* TensorFlow Developer Certificate
"""
        result = resume_service.analyze_resume(resume)
        self.assertEqual(len(result["certifications"]), 3)
        self.assertIn("Python Certification", result["certifications"])
        self.assertIn("AWS Certified Developer - Associate", result["certifications"])
        self.assertIn("TensorFlow Developer Certificate", result["certifications"])

    def test_12_api_response_structure(self):
        """Test 12: POST /api/v1/resume/analyze returns HTTP 200 with schema conformant data."""
        payload = {"resume_text": SAMPLE_RESUME}
        response = self.client.post("/api/v1/resume/analyze", json=payload)

        self.assertEqual(response.status_code, 200)
        data = response.json()

        # Check top-level contract keys
        required_keys = [
            "summary",
            "skills",
            "education",
            "experience",
            "projects",
            "certifications",
            "achievements",
            "skill_count",
            "project_count",
            "experience_count",
        ]
        for key in required_keys:
            self.assertIn(key, data)

        self.assertIsInstance(data["skills"], list)
        self.assertIsInstance(data["education"], list)
        self.assertIsInstance(data["experience"], list)
        self.assertIsInstance(data["projects"], list)
        self.assertIsInstance(data["certifications"], list)
        self.assertIsInstance(data["achievements"], list)
        self.assertIsInstance(data["skill_count"], int)
        self.assertIsInstance(data["project_count"], int)
        self.assertIsInstance(data["experience_count"], int)

        # Validate counts
        self.assertEqual(data["skill_count"], len(data["skills"]))
        self.assertEqual(data["project_count"], len(data["projects"]))
        self.assertEqual(data["experience_count"], len(data["experience"]))


if __name__ == "__main__":
    unittest.main()
