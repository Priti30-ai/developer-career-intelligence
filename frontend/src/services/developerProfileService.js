import apiClient from './api';

/**
 * Service for interacting with the Developer Profile FastAPI endpoints
 */

/**
 * Synthesizes and analyzes a Unified Developer Profile from GitHub and resume inputs.
 *
 * @param {Object} payload
 * @param {string} payload.github_username - Target GitHub username (required)
 * @param {string|null} [payload.resume_text] - Optional plain text resume content
 * @param {string[]} [payload.resume_skills] - Optional list of explicit resume skills
 * @returns {Promise<Object>} DeveloperProfileResponse
 */
export const analyzeDeveloperProfile = async (payload) => {
  const sanitizedPayload = {
    github_username: payload.github_username?.trim(),
    resume_text: payload.resume_text ? payload.resume_text.trim() : null,
    resume_skills: Array.isArray(payload.resume_skills) ? payload.resume_skills : [],
  };

  const response = await apiClient.post('/developer-profile/analyze', sanitizedPayload);
  return response.data;
};

export default {
  analyzeDeveloperProfile,
};
