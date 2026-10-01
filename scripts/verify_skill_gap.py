"""
verify_skill_gap.py
-------------------
Command-line verification script for Skill Gap Analysis.
Runs standalone tests across CareerRoleService, SkillGapService, and API schemas.

Usage:
    .\\backend\\venv\\Scripts\\python.exe scripts\\verify_skill_gap.py
"""

import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from app.services.career_role_service import (
    CareerRoleNotFoundError,
    career_role_service,
)
from app.services.skill_gap_service import skill_gap_service
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
print("VERIFYING SKILL GAP ANALYSIS IMPLEMENTATION")
print("=" * 60)

# Section B: Normalization checks
print("\n--- Section B: Skill Normalization Checks ---")
record_result("Python vs python", normalize_technology_name("python") == "Python" and normalize_technology_name("PYTHON") == "Python")
record_result("Node.js vs nodejs", normalize_technology_name("nodejs") == "Node.js" and normalize_technology_name("node.js") == "Node.js")
record_result("C++ vs c++", normalize_technology_name("c++") == "C++" and normalize_technology_name("cpp") == "C++")

# Test 1: All required skills present
print("\n--- Test 1: All required skills present ---")
role = career_role_service.get_role("data-scientist")
res1 = skill_gap_service.analyze_gap("data-scientist", role["required_skills"])
record_result(
    "All skills matched (100% skill_match_percentage)",
    res1["total_missing_skills"] == 0
    and res1["skill_match_percentage"] == 100.0
    and res1["match_percentage"] == 100.0
    and res1["total_matched_skills"] + res1["total_missing_skills"] == res1["total_required_skills"],
    f"Got missing={res1['total_missing_skills']}, pct={res1['skill_match_percentage']}",
)

# Test 2: Some required skills missing
print("\n--- Test 2: Some required skills missing ---")
res2 = skill_gap_service.analyze_gap(
    "data-scientist",
    ["Python", "Pandas", "NumPy", "Machine Learning"],
)
record_result(
    "Partial match (4 of 8, 50%)",
    res2["total_matched_skills"] == 4
    and res2["total_missing_skills"] == 4
    and res2["skill_match_percentage"] == 50.0
    and res2["total_matched_skills"] + res2["total_missing_skills"] == res2["total_required_skills"],
    f"Got matched={res2['total_matched_skills']}, missing={res2['total_missing_skills']}, pct={res2['skill_match_percentage']}",
)
record_result(
    "Missing list accurate",
    res2["missing_skills"] == ["SQL", "Scikit-learn", "Data Visualization", "Statistics"],
    f"Got {res2['missing_skills']}",
)

# Test 3: No current skills
print("\n--- Test 3: No current skills ---")
res3 = skill_gap_service.analyze_gap("backend-developer", [])
role_b = career_role_service.get_role("backend-developer")
record_result(
    "Zero current skills (0% skill_match_percentage)",
    res3["total_matched_skills"] == 0
    and res3["total_missing_skills"] == len(role_b["required_skills"])
    and res3["skill_match_percentage"] == 0.0
    and res3["total_matched_skills"] + res3["total_missing_skills"] == res3["total_required_skills"],
    f"Got matched={res3['total_matched_skills']}, missing={res3['total_missing_skills']}",
)

# Test 4: Unknown target role
print("\n--- Test 4: Unknown target role ---")
try:
    skill_gap_service.analyze_gap("unknown-role-xyz", ["Python"])
    record_result("Unknown role raises exception", False, "No exception raised")
except CareerRoleNotFoundError:
    record_result("Unknown role raises CareerRoleNotFoundError", True)
except Exception as e:
    record_result("Unknown role raises expected error", False, f"Unexpected error: {type(e)}")

# Test 5: Duplicate and case variation
print("\n--- Test 5: Duplicate and case variation in current skills ---")
res5 = skill_gap_service.analyze_gap(
    "backend-developer",
    ["python", "PYTHON", "Python", "rest-api", "docker", "DOCKER", "git"],
)
record_result(
    "Deduplicated and normalized matching",
    "Python" in res5["matched_skills"]
    and "REST API" in res5["matched_skills"]
    and "Docker" in res5["matched_skills"]
    and "Git" in res5["matched_skills"]
    and res5["total_matched_skills"] == 4
    and res5["total_matched_skills"] + res5["total_missing_skills"] == res5["total_required_skills"],
    f"Got matched={res5['matched_skills']}",
)

# Test 6: Empty required-skill list
print("\n--- Test 6: Empty required-skill list safe behavior ---")
res6 = skill_gap_service.analyze_gap(
    "empty-role",
    ["Python", "Git"],
    custom_required_skills=[],
)
record_result(
    "Safe behavior with 0 required skills (no ZeroDivisionError)",
    res6["total_required_skills"] == 0
    and res6["total_matched_skills"] == 0
    and res6["skill_match_percentage"] == 0.0
    and res6["total_matched_skills"] + res6["total_missing_skills"] == res6["total_required_skills"],
    f"Got res={res6}",
)

# Test 7: Roles listing and details
print("\n--- Test 7: Career roles listing ---")
roles = career_role_service.list_roles()
record_result(
    "At least 6 roles defined",
    len(roles) >= 6,
    f"Got {len(roles)} roles",
)

print("\n" + "=" * 60)
print(f"RESULTS: {passed} passed, {failed} failed")
print("=" * 60)

if failed > 0:
    sys.exit(1)
else:
    sys.exit(0)
