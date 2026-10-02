import apiClient from './api';

/**
 * Service for interacting with backend GitHub analysis endpoints.
 *
 * NOTE: The backend mounts GitHub analysis routes under `/api/github` rather than `/api/v1/github`.
 * We dynamically derive the base `/api` URL from apiClient.defaults.baseURL to ensure compatibility
 * across different deployment environments and hosts.
 */
const getGitHubApiBaseUrl = () => {
  const currentBase = apiClient.defaults.baseURL || 'http://localhost:8000/api/v1';
  // Strip trailing /v1 or /v1/ to reach /api
  return currentBase.replace(/\/v1\/?$/, '');
};

/**
 * Fetch public GitHub profile for a user.
 * GET /api/github/{username}
 */
export const getGitHubProfile = async (username) => {
  const cleanUsername = encodeURIComponent(username.trim());
  const response = await apiClient.get(`/github/${cleanUsername}`, {
    baseURL: getGitHubApiBaseUrl(),
  });
  return response.data;
};

/**
 * Fetch public repositories for a GitHub user.
 * GET /api/github/{username}/repos
 */
export const getGitHubRepositories = async (username) => {
  const cleanUsername = encodeURIComponent(username.trim());
  const response = await apiClient.get(`/github/${cleanUsername}/repos`, {
    baseURL: getGitHubApiBaseUrl(),
  });
  return response.data;
};

/**
 * Extract normalized technologies and repository counts from user repositories.
 * GET /api/github/{username}/technologies
 */
export const getGitHubTechnologies = async (username) => {
  const cleanUsername = encodeURIComponent(username.trim());
  const response = await apiClient.get(`/github/${cleanUsername}/technologies`, {
    baseURL: getGitHubApiBaseUrl(),
  });
  return response.data;
};

/**
 * Fetch categorized developer skill profile based on repository analysis.
 * GET /api/github/{username}/skills
 */
export const getGitHubSkills = async (username) => {
  const cleanUsername = encodeURIComponent(username.trim());
  const response = await apiClient.get(`/github/${cleanUsername}/skills`, {
    baseURL: getGitHubApiBaseUrl(),
  });
  return response.data;
};

/**
 * Aggregator: Fetches profile, repos, technologies, and skills concurrently.
 * Rejects if any request fails so that analysis state remains atomic and consistent.
 */
export const getCompleteGitHubAnalysis = async (username) => {
  const cleanUsername = username.trim();
  const [profile, repos, technologies, skills] = await Promise.all([
    getGitHubProfile(cleanUsername),
    getGitHubRepositories(cleanUsername),
    getGitHubTechnologies(cleanUsername),
    getGitHubSkills(cleanUsername),
  ]);

  return {
    profile,
    repos,
    technologies,
    skills,
  };
};

export default {
  getGitHubProfile,
  getGitHubRepositories,
  getGitHubTechnologies,
  getGitHubSkills,
  getCompleteGitHubAnalysis,
};
