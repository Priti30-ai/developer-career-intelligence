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

import io
import sys
import unittest
from pathlib import Path

# Add backend directory to sys.path so 'app' imports resolve cleanly
backend_dir = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

import docx
import pymupdf
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.main import app
from app.schemas.resume import ResumeAnalysisRequest
from app.services.document_extraction_service import (
    DocumentExtractionError,
    DocumentExtractionService,
    EmptyFileError,
    FileTooLargeError,
    NoTextExtractedError,
    UnsupportedFormatError,
    document_extraction_service,
)
from app.services.resume_service import resume_service


def _generate_test_pdf(text: str = "") -> bytes:
    """Helper to generate an in-memory test PDF."""
    doc = pymupdf.open()
    page = doc.new_page()
    if text:
        page.insert_text((50, 72), text)
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


def _generate_test_docx(text: str = "") -> bytes:
    """Helper to generate an in-memory test DOCX."""
    doc = docx.Document()
    if text:
        for line in text.split("\n"):
            doc.add_paragraph(line)
    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()


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

    def test_13_pdf_upload_valid(self):
        """Test 13: Valid text-based PDF document is extracted and parsed into structured data."""
        pdf_bytes = _generate_test_pdf(SAMPLE_RESUME)
        response = self.client.post(
            "/api/v1/resume/analyze",
            files={"file": ("resume.pdf", pdf_bytes, "application/pdf")},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("Python", data["skills"])
        self.assertGreater(data["skill_count"], 0)
        self.assertGreater(data["project_count"], 0)
        self.assertGreater(len(data["education"]), 0)

    def test_14_pdf_upload_no_text(self):
        """Test 14: PDF with no extractable text returns HTTP 400 with clear message."""
        empty_pdf_bytes = _generate_test_pdf("")
        response = self.client.post(
            "/api/v1/resume/analyze",
            files={"file": ("scanned.pdf", empty_pdf_bytes, "application/pdf")},
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("Could not extract text from this PDF", response.json()["detail"])

    def test_15_pdf_upload_corrupted(self):
        """Test 15: Corrupted PDF bytes return HTTP 400 with corruption message."""
        corrupted_bytes = b"%PDF-1.4\ncorrupted garbage binary data not a valid trailer"
        response = self.client.post(
            "/api/v1/resume/analyze",
            files={"file": ("broken.pdf", corrupted_bytes, "application/pdf")},
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("corrupted or invalid", response.json()["detail"].lower())

    def test_16_docx_upload_valid(self):
        """Test 16: Valid DOCX document is extracted and parsed into structured data."""
        docx_bytes = _generate_test_docx(SAMPLE_RESUME)
        response = self.client.post(
            "/api/v1/resume/analyze",
            files={
                "file": (
                    "candidate_resume.docx",
                    docx_bytes,
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                )
            },
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("Python", data["skills"])
        self.assertGreater(data["skill_count"], 0)
        self.assertEqual(data["project_count"], 1)

    def test_17_docx_upload_empty(self):
        """Test 17: Empty DOCX document returns HTTP 400."""
        empty_docx_bytes = _generate_test_docx("")
        response = self.client.post(
            "/api/v1/resume/analyze",
            files={
                "file": (
                    "empty.docx",
                    empty_docx_bytes,
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                )
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("empty", response.json()["detail"].lower())

    def test_18_docx_upload_corrupted(self):
        """Test 18: Corrupted DOCX file returns HTTP 400."""
        corrupted_docx_bytes = b"PK\x03\x04not a valid zip package content"
        response = self.client.post(
            "/api/v1/resume/analyze",
            files={
                "file": (
                    "corrupt.docx",
                    corrupted_docx_bytes,
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                )
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("corrupted or invalid", response.json()["detail"].lower())

    def test_19_txt_upload_valid(self):
        """Test 19: Valid UTF-8 TXT document upload is extracted and parsed."""
        txt_bytes = SAMPLE_RESUME.encode("utf-8")
        response = self.client.post(
            "/api/v1/resume/analyze",
            files={"file": ("resume.txt", txt_bytes, "text/plain")},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("Python", data["skills"])
        self.assertEqual(data["skill_count"], 6)

    def test_20_txt_upload_invalid_utf8(self):
        """Test 20: Non-UTF-8 binary content uploaded as .txt returns HTTP 400."""
        invalid_bytes = b"\x80\x81\x82\x90\x91\xff\xfe\xfa"
        response = self.client.post(
            "/api/v1/resume/analyze",
            files={"file": ("invalid.txt", invalid_bytes, "text/plain")},
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("utf-8", response.json()["detail"].lower())

    def test_21_unsupported_file_type(self):
        """Test 21: Unsupported file formats (e.g., .png, .exe) return HTTP 400."""
        png_bytes = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR"
        response = self.client.post(
            "/api/v1/resume/analyze",
            files={"file": ("resume_screenshot.png", png_bytes, "image/png")},
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("Unsupported resume format", response.json()["detail"])

    def test_22_empty_file_upload(self):
        """Test 22: 0-byte file upload returns HTTP 400."""
        response = self.client.post(
            "/api/v1/resume/analyze",
            files={"file": ("empty.txt", b"", "text/plain")},
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("empty", response.json()["detail"].lower())

    def test_23_oversized_file_upload(self):
        """Test 23: File exceeding 5 MB limit returns HTTP 413."""
        # 5 MB + 100 bytes
        oversized_bytes = b"X" * (5 * 1024 * 1024 + 100)
        response = self.client.post(
            "/api/v1/resume/analyze",
            files={"file": ("large.txt", oversized_bytes, "text/plain")},
        )
        self.assertEqual(response.status_code, 413)
        self.assertIn("5 MB limit", response.json()["detail"])

    def test_24_missing_file_and_body(self):
        """Test 24: Request with neither file nor JSON body returns HTTP 400."""
        response = self.client.post("/api/v1/resume/analyze", data={})
        self.assertEqual(response.status_code, 400)
        self.assertIn("No resume file was uploaded", response.json()["detail"])

    def test_25_document_extraction_service_unit(self):
        """Test 25: Direct unit tests on DocumentExtractionService methods and validation."""
        service = DocumentExtractionService()

        # Format validation
        self.assertEqual(service.validate_file_metadata("test.pdf"), "pdf")
        self.assertEqual(service.validate_file_metadata("test.docx"), "docx")
        self.assertEqual(service.validate_file_metadata("test.txt"), "txt")

        # Unsupported
        with self.assertRaises(UnsupportedFormatError):
            service.validate_file_metadata("test.jpg")

        # Empty
        with self.assertRaises(EmptyFileError):
            service.extract_text(b"", "test.txt")

        # Oversized
        with self.assertRaises(FileTooLargeError):
            service.extract_text(b"A" * (6 * 1024 * 1024), "test.txt")


if __name__ == "__main__":
    unittest.main()

