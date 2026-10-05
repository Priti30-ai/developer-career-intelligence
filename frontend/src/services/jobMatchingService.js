import apiClient from './api';

/**
 * Service for interacting with the Job Matching FastAPI endpoints.
 *
 * Endpoint: POST /api/v1/job-matching/analyze
 */

/**
 * Analyzes and matches a job description against developer skills.
 *
 * @param {Object} params
 * @param {string} params.jobDescription - Raw plain text of the job description
 * @param {string[]} [params.developerSkills] - List of skills possessed by the developer
 * @returns {Promise<Object>} JobMatchingResponse from backend
 */
export const matchJobDescription = async ({ jobDescription, developerSkills = [] }) => {
  const sanitizedJobDescription = jobDescription?.trim() || '';
  const sanitizedSkills = Array.isArray(developerSkills)
    ? developerSkills
        .map((s) => (typeof s === 'string' ? s.trim() : ''))
        .filter(Boolean)
    : [];

  const response = await apiClient.post('/job-matching/analyze', {
    job_description: sanitizedJobDescription,
    developer_skills: sanitizedSkills,
  });

  return response.data;
};

export default {
  matchJobDescription,
};
