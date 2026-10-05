import apiClient from './api';

/**
 * Service for interacting with the Skill Gap FastAPI endpoints.
 *
 * Endpoints:
 * - GET  /api/v1/skill-gap/roles
 * - GET  /api/v1/skill-gap/roles/{slug}
 * - POST /api/v1/skill-gap/analyze
 */

/**
 * Retrieves the summary list of all predefined career roles.
 *
 * @returns {Promise<Array<{slug: string, display_name: string, description: string, required_skill_count: number}>>}
 */
export const listCareerRoles = async () => {
  const response = await apiClient.get('/skill-gap/roles');
  return response.data;
};

/**
 * Retrieves complete requirement details for a specific career role.
 *
 * @param {string} roleSlug - Normalized URL-safe role slug (e.g. 'backend-developer')
 * @returns {Promise<{slug: string, display_name: string, description: string, required_skills: string[]}>}
 */
export const getCareerRoleDetails = async (roleSlug) => {
  const cleanSlug = encodeURIComponent((roleSlug || '').trim());
  const response = await apiClient.get(`/skill-gap/roles/${cleanSlug}`);
  return response.data;
};

/**
 * Compares current developer skills against target role requirements.
 *
 * @param {Object} params
 * @param {string} params.targetRole - Target career role slug or title (e.g. 'backend-developer')
 * @param {string[]} [params.currentSkills] - List of skills possessed by the developer
 * @returns {Promise<Object>} SkillGapResponse
 */
export const analyzeSkillGap = async ({ targetRole, currentSkills = [] }) => {
  const sanitizedRole = (targetRole || '').trim();
  const sanitizedSkills = Array.isArray(currentSkills)
    ? currentSkills
        .map((s) => (typeof s === 'string' ? s.trim() : ''))
        .filter(Boolean)
    : [];

  const response = await apiClient.post('/skill-gap/analyze', {
    target_role: sanitizedRole,
    current_skills: sanitizedSkills,
  });

  return response.data;
};

export default {
  listCareerRoles,
  getCareerRoleDetails,
  analyzeSkillGap,
};
