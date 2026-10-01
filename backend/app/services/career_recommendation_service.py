"""
career_recommendation_service.py
--------------------------------
Service layer for Career Recommendations & Learning Roadmaps.

Builds on top of SkillGapService to generate an explainable, deterministic
learning plan for closing identified skill gaps.

Pipeline:
Current Skills + Target Role
        ↓
Skill Gap Analysis (SkillGapService)
        ↓
Missing Skills Identification
        ↓
Learning Guidance Lookup (LearningResourceService)
        ↓
Deterministic Priority & Dependency Ordering
        ↓
Multi-Stage Learning Roadmap
"""

from typing import Any, Dict, List, Sequence, Set
from app.services.career_role_service import CareerRoleNotFoundError
from app.services.learning_resource_service import learning_resource_service
from app.services.skill_gap_service import skill_gap_service


class CareerRecommendationService:
    """
    Generates actionable learning recommendations and multi-stage roadmaps.

    Design rules:
    - Reuses SkillGapService for gap analysis (no duplicate comparison logic).
    - Assigns explainable priorities (HIGH, MEDIUM, LOW) based on dependency
      unblocking and foundational readiness.
    - Orders recommendations topologically so prerequisites precede dependent skills.
    - Groups missing skills into logical, non-empty progression stages.
    - Explicitly states that roadmaps are guidance tools and do not guarantee employment.
    """

    DISCLAIMER = (
        "This learning roadmap is an automated, deterministic guidance tool based on "
        "predefined role requirements and identified skill gaps. It does not imply "
        "or guarantee candidate employability, hiring outcomes, or career readiness."
    )

    def generate_recommendations(
        self,
        target_role: str,
        current_skills: Sequence[str],
    ) -> Dict[str, Any]:
        """
        Produce complete career recommendations and learning roadmap.

        Args:
            target_role: Target career role identifier or display name.
            current_skills: Sequence of skills currently possessed by the candidate.

        Returns:
            Dict containing skill gap metrics, prioritized recommendations,
            and sequential roadmap stages.

        Raises:
            CareerRoleNotFoundError: If the target role cannot be resolved.
        """
        # 1. Reuse existing SkillGapService for gap analysis
        gap_result = skill_gap_service.analyze_gap(
            target_role=target_role,
            current_skills=current_skills,
        )

        missing_skills: List[str] = gap_result["missing_skills"]
        matched_skills: List[str] = gap_result["matched_skills"]
        missing_set: Set[str] = set(missing_skills)

        # 2. If no missing skills (100% coverage), return clean empty-recommendation response
        if not missing_skills:
            return {
                "target_role": gap_result["target_role"],
                "role_slug": gap_result["role_slug"],
                "skill_match_percentage": gap_result["skill_match_percentage"],
                "match_percentage": gap_result["match_percentage"],
                "total_required_skills": gap_result["total_required_skills"],
                "total_matched_skills": gap_result["total_matched_skills"],
                "total_missing_skills": 0,
                "current_skills": list(current_skills),
                "matched_skills": matched_skills,
                "missing_skills": [],
                "recommendations": [],
                "roadmap": [],
                "disclaimer": self.DISCLAIMER,
            }

        # 3. Gather guidance for all missing skills
        guidance_map: Dict[str, Dict[str, Any]] = {
            skill: learning_resource_service.get_skill_guidance(skill)
            for skill in missing_skills
        }

        # 4. Determine priority and reason for each missing skill
        # A skill is HIGH priority if it unblocks other missing skills, or has stage 1.
        # A skill is MEDIUM if it has moderate stage or dependent on foundations.
        # A skill is LOW if it is an advanced terminal leaf with no dependents in this gap.
        dependents_map: Dict[str, List[str]] = {s: [] for s in missing_skills}
        for s, guide in guidance_map.items():
            for prereq in guide["prerequisites"]:
                if prereq in dependents_map:
                    dependents_map[prereq].append(s)

        recommendations: List[Dict[str, Any]] = []
        for skill in missing_skills:
            guide = guidance_map[skill]
            unblocks = dependents_map.get(skill, [])
            stage = guide["estimated_stage"]
            prereqs = guide["prerequisites"]

            # Explainable priority assignment logic
            if unblocks or stage == 1:
                priority = "HIGH"
                if unblocks:
                    reason = (
                        f"Foundational prerequisite required to unblock subsequent skills: "
                        f"{', '.join(unblocks)}."
                    )
                else:
                    reason = "Core foundational requirement ready to learn immediately."
            elif stage in (2, 3) or any(p in missing_set for p in prereqs):
                priority = "MEDIUM"
                reason = "Intermediate core competency building upon fundamental concepts."
            else:
                priority = "LOW"
                reason = "Specialized advanced competency best approached after mastering foundational skills."

            recommendations.append({
                "skill": skill,
                "priority": priority,
                "reason": reason,
                "difficulty": guide["difficulty"],
                "prerequisites": list(guide["prerequisites"]),
                "learning_topics": list(guide["learning_topics"]),
                "suggested_projects": list(guide["suggested_projects"]),
                "estimated_stage": stage,
            })

        # 5. Order recommendations topologically by prerequisite dependencies and estimated stage
        recommendations = self._order_recommendations(recommendations)

        # 6. Group recommendations into ordered Roadmap Stages
        roadmap = self._build_roadmap_stages(recommendations, gap_result["target_role"])

        return {
            "target_role": gap_result["target_role"],
            "role_slug": gap_result["role_slug"],
            "skill_match_percentage": gap_result["skill_match_percentage"],
            "match_percentage": gap_result["match_percentage"],
            "total_required_skills": gap_result["total_required_skills"],
            "total_matched_skills": gap_result["total_matched_skills"],
            "total_missing_skills": gap_result["total_missing_skills"],
            "current_skills": list(current_skills),
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "recommendations": recommendations,
            "roadmap": roadmap,
            "disclaimer": self.DISCLAIMER,
        }

    def _order_recommendations(
        self, recommendations: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Sort recommendations deterministically so prerequisites appear before dependents.
        Tie-breaker: estimated_stage ascending, then skill name alphabetical.
        """
        priority_weight = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
        return sorted(
            recommendations,
            key=lambda item: (
                item["estimated_stage"],
                priority_weight.get(item["priority"], 3),
                item["skill"],
            ),
        )

    def _build_roadmap_stages(
        self,
        ordered_recommendations: List[Dict[str, Any]],
        role_display_name: str,
    ) -> List[Dict[str, Any]]:
        """
        Partition ordered recommendations into sequential, non-empty roadmap stages.
        """
        # Group by estimated stage (1: Foundations, 2: Core Engineering, 3: Applied Systems, 4: Advanced Specialization)
        stage_buckets: Dict[int, List[Dict[str, Any]]] = {1: [], 2: [], 3: [], 4: []}
        for rec in ordered_recommendations:
            stage_idx = min(max(rec.get("estimated_stage", 2), 1), 4)
            stage_buckets[stage_idx].append(rec)

        stage_meta = {
            1: {
                "title": "Foundational Essentials",
                "objective": f"Establish core programming, data, and tooling prerequisites for {role_display_name}.",
            },
            2: {
                "title": "Core Competencies & Tooling",
                "objective": f"Build intermediate operational fluency with foundational frameworks and data tools.",
            },
            3: {
                "title": "Applied Systems & Analysis",
                "objective": f"Synthesize core tools into applied workflows, architectures, and predictive solutions.",
            },
            4: {
                "title": "Advanced Specialization & Production",
                "objective": f"Master specialized domain algorithms, architectures, and production-grade deployment patterns.",
            },
        }

        roadmap: List[Dict[str, Any]] = []
        stage_counter = 1

        for stage_idx in (1, 2, 3, 4):
            bucket = stage_buckets[stage_idx]
            if not bucket:
                continue

            stage_skills = [item["skill"] for item in bucket]

            # Aggregate unique recommended projects across skills in this stage
            seen_projects = set()
            stage_projects = []
            for item in bucket:
                for proj in item.get("suggested_projects", []):
                    if proj not in seen_projects:
                        seen_projects.add(proj)
                        stage_projects.append(proj)

            meta = stage_meta[stage_idx]
            roadmap.append({
                "stage_number": stage_counter,
                "title": f"Stage {stage_counter}: {meta['title']}",
                "skills": stage_skills,
                "objective": meta["objective"],
                "recommended_projects": stage_projects,
            })
            stage_counter += 1

        return roadmap


# Singleton instance for route usage
career_recommendation_service = CareerRecommendationService()
