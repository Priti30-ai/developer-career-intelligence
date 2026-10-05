import apiClient from './api';

/**
 * Service for interacting with the Learning Roadmap and Career Recommendation backend endpoints.
 *
 * Backed by FastAPI routes:
 * - GET  /api/v1/career-recommendations/roles
 * - POST /api/v1/career-recommendations/analyze
 */

/**
 * Fetch supported career roles available for roadmap generation.
 *
 * @returns {Promise<Array<{slug: string, display_name: string, description: string, required_skill_count: number}>>}
 */
export const getRoles = async () => {
  const response = await apiClient.get('/career-recommendations/roles');
  return response.data;
};

/**
 * Generate a sequential learning roadmap and skill recommendations against a target role.
 *
 * @param {string} targetRole - Role slug or display name (e.g. 'backend-developer')
 * @param {string[]} [currentSkills=[]] - Developer skills currently possessed
 * @returns {Promise<Object>} CareerRecommendationResponse with roadmap and recommendations
 */
export const analyzeRoadmap = async (targetRole, currentSkills = []) => {
  const sanitizedRole = (targetRole || '').trim();
  const sanitizedSkills = Array.isArray(currentSkills)
    ? currentSkills
        .map((s) => (typeof s === 'string' ? s.trim() : ''))
        .filter(Boolean)
    : [];

  const response = await apiClient.post('/career-recommendations/analyze', {
    target_role: sanitizedRole,
    current_skills: sanitizedSkills,
  });

  return response.data;
};

export default {
  getRoles,
  analyzeRoadmap,
};
