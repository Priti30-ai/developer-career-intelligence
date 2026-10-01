"""
verify_career_recommendations.py
--------------------------------
CLI verification script for Career Recommendations and Learning Roadmaps.
Performs deterministic sanity checks across services and schemas without external calls.

Usage:
    .\\backend\\venv\\Scripts\\python.exe scripts\\verify_career_recommendations.py
"""

import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from app.main import app
from app.services.career_recommendation_service import (
    career_recommendation_service,
)
from app.services.career_role_service import (
    CareerRoleNotFoundError,
    career_role_service,
)
from app.services.technology_service import normalize_technology_name

GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"

failed = 0
passed = 0


def record_result(test_name: str, success: bool, details: str = ""):
    global passed, failed
    if success:
        print(f"  [{GREEN}PASS{RESET}] {test_name}")
        passed += 1
    else:
        print(f"  [{RED}FAIL{RESET}] {test_name} - {details}")
        failed += 1


print("=" * 60)
print("VERIFYING CAREER RECOMMENDATIONS & LEARNING ROADMAP")
print("=" * 60)

# Check 1: Role resolution
print("\n--- Check 1: Role Resolution ---")
roles = career_role_service.list_roles()
record_result(
    "Role resolution and listing (>= 6 roles)",
    len(roles) >= 6 and any(r["slug"] == "data-scientist" for r in roles),
    f"Got {len(roles)} roles",
)

# Check 2: Skill gap integration
print("\n--- Check 2: Skill Gap Integration ---")
res2 = career_recommendation_service.generate_recommendations(
    target_role="data-scientist",
    current_skills=["Python", "Pandas", "NumPy", "Machine Learning"],
)
record_result(
    "Skill gap integration calculates 50% match",
    res2["skill_match_percentage"] == 50.0
    and res2["total_matched_skills"] == 4
    and res2["total_missing_skills"] == 4,
    f"Got match={res2['skill_match_percentage']}",
)
record_result(
    "Invariant: matched + missing == required",
    res2["total_matched_skills"] + res2["total_missing_skills"] == res2["total_required_skills"],
    f"Matched: {res2['total_matched_skills']}, Missing: {res2['total_missing_skills']}, Req: {res2['total_required_skills']}",
)

# Check 3: Recommendation generation
print("\n--- Check 3: Recommendation Generation ---")
recs = res2["recommendations"]
record_result(
    "Missing skills produce recommendations (4 recommendations)",
    len(recs) == 4,
    f"Got {len(recs)} recommendations",
)
rec_skills = {r["skill"] for r in recs}
record_result(
    "Expected missing skills present in recommendations",
    rec_skills == {"SQL", "Scikit-learn", "Data Visualization", "Statistics"},
    f"Got {rec_skills}",
)

# Check 4: Priority assignment
print("\n--- Check 4: Priority Assignment ---")
priorities = {r["priority"] for r in recs}
record_result(
    "Valid priorities assigned (HIGH, MEDIUM, LOW)",
    priorities.issubset({"HIGH", "MEDIUM", "LOW"}),
    f"Got {priorities}",
)
record_result(
    "Explainable reasons provided for all recommendations",
    all(len(r["reason"]) > 10 for r in recs),
)

# Check 5: Roadmap ordering and stages
print("\n--- Check 5: Roadmap Ordering and Stages ---")
roadmap = res2["roadmap"]
record_result(
    "Sequential roadmap stages generated",
    len(roadmap) > 0 and [s["stage_number"] for s in roadmap] == list(range(1, len(roadmap) + 1)),
    f"Stages: {[s['stage_number'] for s in roadmap]}",
)
roadmap_skills = []
for stg in roadmap:
    roadmap_skills.extend(stg["skills"])
record_result(
    "All roadmap skills belong to missing skills set",
    set(roadmap_skills) == set(res2["missing_skills"]),
    f"Roadmap: {set(roadmap_skills)} vs Missing: {set(res2['missing_skills'])}",
)

# Check 6: Normalization check
print("\n--- Check 6: Skill Normalization in Recommendations ---")
res6 = career_recommendation_service.generate_recommendations(
    target_role="backend-developer",
    current_skills=["python", "PYTHON", "docker", "DOCKER", "git"],
)
record_result(
    "Case-insensitive normalized input matching without duplicates",
    "Python" in res6["matched_skills"]
    and "Docker" in res6["matched_skills"]
    and "Git" in res6["matched_skills"]
    and len(res6["matched_skills"]) == len(set(res6["matched_skills"])),
    f"Matched: {res6['matched_skills']}",
)

# Check 7: API endpoints check via TestClient
print("\n--- Check 7: API Response Check ---")
try:
    from fastapi.testclient import TestClient
    client = TestClient(app)
    api_roles = client.get("/api/v1/career-recommendations/roles")
    api_post = client.post(
        "/api/v1/career-recommendations/analyze",
        json={"target_role": "data-scientist", "current_skills": ["Python"]},
    )
    record_result(
        "API endpoints operational (GET /roles 200, POST /analyze 200)",
        api_roles.status_code == 200 and api_post.status_code == 200,
        f"roles: {api_roles.status_code}, analyze: {api_post.status_code}",
    )
except Exception as exc:
    record_result("API endpoints operational", False, str(exc))

print("\n" + "=" * 60)
print(f"RESULTS: {passed} passed, {failed} failed")
print("=" * 60)

if failed > 0:
    sys.exit(1)
else:
    sys.exit(0)
