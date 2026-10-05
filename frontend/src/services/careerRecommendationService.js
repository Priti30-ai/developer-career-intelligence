import apiClient from './api';

/**
 * Service for interacting with the Career Recommendations FastAPI endpoints.
 *
 * Endpoints:
 * - GET  /api/v1/career-recommendations/roles
 * - POST /api/v1/career-recommendations/analyze
 * - GET  /api/v1/career-recommendations/github/{username}/{role_slug}
 */

/**
 * Retrieves the summary list of all supported career roles for recommendations.
 *
 * @returns {Promise<Array<{slug: string, display_name: string, description: string, required_skill_count: number}>>}
 */
export const listCareerRecommendationRoles = async () => {
  const response = await apiClient.get('/career-recommendations/roles');
  return response.data;
};

/**
 * Analyzes developer skill gaps against a target role and generates prioritized learning recommendations and roadmap.
 *
 * @param {Object} params
 * @param {string} params.targetRole - Target career role slug or title (e.g. 'data-scientist')
 * @param {string[]} [params.currentSkills] - List of skills currently possessed by developer
 * @returns {Promise<Object>} CareerRecommendationResponse
 */
export const analyzeCareerRecommendations = async ({ targetRole, currentSkills = [] }) => {
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

/**
 * Compares current developer skills against all available career roles by querying the real backend endpoint
 * for each role in parallel and returning ranked recommendations.
 *
 * @param {Object} params
 * @param {string[]} params.currentSkills - Developer skills to evaluate
 * @param {Array<Object>} [params.roles] - Pre-fetched role list, or fetched automatically if omitted
 * @returns {Promise<Array<Object>>} Ranked list of CareerRecommendationResponses sorted by match percentage descending
 */
export const compareAllCareerRoles = async ({ currentSkills = [], roles = [] }) => {
  let roleList = roles;
  if (!roleList || roleList.length === 0) {
    roleList = await listCareerRecommendationRoles();
  }

  if (!roleList || roleList.length === 0) {
    return [];
  }

  // Call the real backend endpoint for each role
  const results = await Promise.all(
    roleList.map((role) =>
      analyzeCareerRecommendations({
        targetRole: role.slug,
        currentSkills,
      })
    )
  );

  // Deterministically sort descending by skill_match_percentage, tie-breaker by total_matched_skills descending
  return results.sort((a, b) => {
    if (b.skill_match_percentage !== a.skill_match_percentage) {
      return b.skill_match_percentage - a.skill_match_percentage;
    }
    return (b.total_matched_skills || 0) - (a.total_matched_skills || 0);
  });
};

/**
 * Generates career recommendations for a specific GitHub user against a target role.
 *
 * @param {Object} params
 * @param {string} params.username - Public GitHub username
 * @param {string} params.roleSlug - Target career role slug (e.g. 'data-scientist')
 * @returns {Promise<Object>} CareerRecommendationResponse
 */
export const generateFromGitHubProfile = async ({ username, roleSlug }) => {
  const cleanUsername = encodeURIComponent((username || '').trim());
  const cleanSlug = encodeURIComponent((roleSlug || '').trim());
  const response = await apiClient.get(
    `/career-recommendations/github/${cleanUsername}/${cleanSlug}`
  );
  return response.data;
};

export default {
  listCareerRecommendationRoles,
  analyzeCareerRecommendations,
  compareAllCareerRoles,
  generateFromGitHubProfile,
};
