import apiClient from './api';

/**
 * Service for interacting with GitHub Repository Architecture Analysis endpoint.
 *
 * Endpoint:
 * - POST /api/v1/repository-architecture/analyze
 */

/**
 * Helper to parse a repository input string which could be:
 * - Full URL: https://github.com/owner/repo
 * - Short URL: github.com/owner/repo
 * - Shorthand: owner/repo
 *
 * @param {string} input - User input string
 * @returns {{ owner: string, repo: string }}
 */
export const parseRepositoryInput = (input) => {
  if (!input || typeof input !== 'string') {
    return { owner: '', repo: '' };
  }

  let clean = input.trim();
  // Strip trailing .git and trailing slashes
  clean = clean.replace(/\.git\/?$/, '').replace(/\/+$/, '');

  // Match full or protocol-less github.com URL
  const urlMatch = clean.match(/(?:https?:\/\/)?(?:www\.)?github\.com\/([^/\s]+)\/([^/\s]+)/i);
  if (urlMatch) {
    return {
      owner: urlMatch[1].trim(),
      repo: urlMatch[2].trim(),
    };
  }

  // Match owner/repo
  const slashMatch = clean.match(/^([^/\s]+)\/([^/\s]+)$/);
  if (slashMatch) {
    return {
      owner: slashMatch[1].trim(),
      repo: slashMatch[2].trim(),
    };
  }

  // Plain string or partial
  return { owner: '', repo: clean };
};

/**
 * Analyze the structural architecture of a public GitHub repository.
 *
 * @param {Object} params
 * @param {string} params.owner - Repository owner or organization
 * @param {string} params.repo - Repository name
 * @param {string} [params.branch] - Optional branch name or commit SHA
 * @returns {Promise<Object>} RepositoryArchitectureResponse
 */
export const analyzeRepositoryArchitecture = async ({ owner, repo, branch }) => {
  const sanitizedOwner = (owner || '').trim();
  const sanitizedRepo = (repo || '').trim();
  const sanitizedBranch = branch ? branch.trim() : null;

  const payload = {
    owner: sanitizedOwner,
    repo: sanitizedRepo,
  };

  if (sanitizedBranch) {
    payload.branch = sanitizedBranch;
  }

  const response = await apiClient.post('/repository-architecture/analyze', payload);
  return response.data;
};

export default {
  parseRepositoryInput,
  analyzeRepositoryArchitecture,
};
