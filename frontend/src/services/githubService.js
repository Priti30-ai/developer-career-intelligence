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
 * Adapt unified GitHubAccountAnalysisResponse into standardized structure
 * that preserves full raw contracts and satisfies existing dashboard components.
 *
 * @param {Object} data - Raw GitHubAccountAnalysisResponse from backend
 * @returns {Object} Unified data with backward-compatible component props
 */
export const adaptUnifiedGitHubAnalysis = (data) => {
  if (!data) return null;
  const account = data.account || {};
  const repositories = data.repositories || [];
  const aggregated = data.aggregated_profile || {};
  const coverage = aggregated.repository_coverage || {};
  const evidenceSummary = aggregated.evidence_summary || {};

  // Adapt repositories ensuring primary language and details are intact
  const adaptedRepos = repositories.map((r) => ({
    ...r,
    language: r.primary_language || r.language || (r.languages && r.languages[0]) || null,
  }));

  // Adapt technologies for TechnologyAnalysis component
  const adaptedTechnologies = {
    total_repositories: coverage.total_repositories_analyzed ?? adaptedRepos.length,
    technologies: (aggregated.technologies || []).map((t) => ({
      name: t.name,
      repository_count: t.repository_count,
      evidence_count: t.evidence_count ?? 0,
      supporting_repositories: t.supporting_repositories || [],
    })),
  };

  // Adapt skills for SkillCategoryGrid component
  const adaptedSkills = {
    total_unique_technologies:
      aggregated.total_unique_technologies ??
      aggregated.total_unique_skills ??
      (aggregated.skills?.length ?? 0),
    categories: aggregated.categorized_skills || [],
    skills: aggregated.skills || [],
  };

  return {
    // Canonical unified data contracts from Task 2–7
    account,
    repositories: adaptedRepos,
    aggregated_profile: aggregated,
    repository_coverage: coverage,
    evidence_summary: evidenceSummary,

    // Backward-compatible props for existing UI components
    profile: account,
    repos: adaptedRepos,
    technologies: adaptedTechnologies,
    skills: adaptedSkills,
  };
};

/**
 * Fetch unified GitHub account intelligence with ONE single backend request:
 * GET /api/v1/github/analysis?username=<usernameOrUrl>
 *
 * Orchestrates account discovery, repository cataloging, deep architectural inspection,
 * evidence extraction, and cross-repository account aggregation in a single call.
 *
 * @param {string} usernameOrUrl - GitHub username, @username, or profile URL
 * @returns {Promise<Object>} Adapted unified GitHub analysis
 */
export const getGitHubAccountAnalysis = async (usernameOrUrl) => {
  const cleanInput = (usernameOrUrl || '').trim();
  const response = await apiClient.get('/github/analysis', {
    params: {
      username: cleanInput,
    },
  });
  return adaptUnifiedGitHubAnalysis(response.data);
};

/**
 * Aggregator: Uses unified account analysis endpoint to fetch the complete
 * developer profile in ONE single request, avoiding 4 duplicate roundtrips.
 *
 * @param {string} username - GitHub username or profile URL
 * @returns {Promise<Object>} Adapted unified GitHub analysis
 */
export const getCompleteGitHubAnalysis = async (username) => {
  return getGitHubAccountAnalysis(username);
};

export default {
  getGitHubAccountAnalysis,
  adaptUnifiedGitHubAnalysis,
  getCompleteGitHubAnalysis,
  getGitHubProfile,
  getGitHubRepositories,
  getGitHubTechnologies,
  getGitHubSkills,
};
