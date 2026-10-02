import React, { useState } from 'react';
import { GitBranch, Sparkles } from 'lucide-react';
import GitHubAnalysisForm from '../components/github/GitHubAnalysisForm';
import GitHubProfileCard from '../components/github/GitHubProfileCard';
import GitHubMetricCards from '../components/github/GitHubMetricCards';
import TechnologyAnalysis from '../components/github/TechnologyAnalysis';
import SkillCategoryGrid from '../components/github/SkillCategoryGrid';
import RepositoryTable from '../components/github/RepositoryTable';
import GitHubInitialEmptyState from '../components/github/GitHubInitialEmptyState';
import { getCompleteGitHubAnalysis } from '../services/githubService';

export const GitHubAnalysis = () => {
  const [username, setUsername] = useState('');
  const [loading, setLoading] = useState(false);
  const [analysisData, setAnalysisData] = useState(null);
  const [error, setError] = useState(null);
  const [validationError, setValidationError] = useState(null);

  const handleAnalyze = async () => {
    const cleanUsername = username.trim();

    if (!cleanUsername) {
      setValidationError('GitHub username is required. Please enter a valid public handle.');
      return;
    }

    setValidationError(null);
    setLoading(true);
    setError(null);

    try {
      const data = await getCompleteGitHubAnalysis(cleanUsername);
      setAnalysisData(data);
      setError(null);
    } catch (err) {
      const rawMessage = err.message || '';
      const statusMatch = rawMessage.match(/\b(404|403|422|429|500|502|504)\b/);
      const httpStatus = statusMatch ? parseInt(statusMatch[1], 10) : err.response?.status;

      let errorTitle = 'GitHub Analysis Failed';
      let errorMessage = 'An unexpected error occurred while communicating with GitHub services.';

      if (httpStatus === 404 || rawMessage.toLowerCase().includes('not found')) {
        errorTitle = 'GitHub Account Not Found';
        errorMessage = `The user "${cleanUsername}" does not exist on GitHub or could not be found. Please check the spelling.`;
      } else if (httpStatus === 403 || rawMessage.toLowerCase().includes('rate limit') || rawMessage.toLowerCase().includes('forbidden')) {
        errorTitle = 'GitHub API Rate Limit Reached';
        errorMessage = 'The unauthenticated GitHub API hourly quota has been exceeded or access was restricted. Please wait a short while or configure a personal token on the backend.';
      } else if (httpStatus === 502 || rawMessage.toLowerCase().includes('connect to github')) {
        errorTitle = 'GitHub Connectivity Error';
        errorMessage = 'The backend service could not establish a connection to api.github.com. Please check external network availability.';
      } else if (httpStatus === 504 || rawMessage.toLowerCase().includes('timed out')) {
        errorTitle = 'GitHub Gateway Timeout';
        errorMessage = 'GitHub API took longer than 10 seconds to respond. The account may have an exceptionally large repository index.';
      } else if (httpStatus === 422 || rawMessage.toLowerCase().includes('unprocessable')) {
        errorTitle = 'Invalid Request Parameter';
        errorMessage = 'The username contains characters unsupported by the GitHub API.';
      } else if (rawMessage.toLowerCase().includes('network') || rawMessage.toLowerCase().includes('failed to fetch') || rawMessage.toLowerCase().includes('connect')) {
        errorTitle = 'Backend Server Offline';
        errorMessage = 'Unable to reach the FastAPI backend server at http://localhost:8000. Please verify that the backend process is running.';
      } else if (rawMessage) {
        errorMessage = rawMessage;
      }

      setError({
        title: errorTitle,
        message: errorMessage,
        status: httpStatus || null,
      });
      // Do not clear previous data on failure, or clear if desired to prevent confusion
      setAnalysisData(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* SECTION 1 — PAGE HEADER */}
      <div className="bg-white border border-slate-200 rounded-xl p-6 sm:p-7 shadow-sm">
        <div className="max-w-3xl">
          <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded-full text-xs font-medium bg-indigo-50 text-indigo-700 border border-indigo-100 mb-3">
            <GitBranch className="w-3.5 h-3.5" />
            Developer Analysis Module
          </div>
          <h2 className="text-xl sm:text-2xl font-bold text-slate-900 tracking-tight">
            GitHub Repository & Skill Analysis
          </h2>
          <p className="mt-1.5 text-xs sm:text-sm text-slate-600 leading-relaxed">
            Inspect public developer repositories, catalog active codebases, extract normalized technology signals,
            and structure engineering proficiencies into domain skill categories.
          </p>
        </div>
      </div>

      {/* SECTION 2 — USER INPUT FORM */}
      <GitHubAnalysisForm
        username={username}
        setUsername={(val) => {
          setUsername(val);
          if (validationError) setValidationError(null);
        }}
        onSubmit={handleAnalyze}
        loading={loading}
        validationError={validationError}
        error={error}
        onRetry={handleAnalyze}
      />

      {/* ANALYSIS RESULTS OR INITIAL EMPTY STATE */}
      {analysisData ? (
        <div className="space-y-6">
          {/* SECTION 3 — PROFILE CARD */}
          <GitHubProfileCard profile={analysisData.profile} />

          {/* SECTION 4 — METRIC CARDS */}
          <GitHubMetricCards
            profile={analysisData.profile}
            repos={analysisData.repos}
            skills={analysisData.skills}
          />

          {/* SECTION 5 — TECHNOLOGY ANALYSIS & BAR CHART */}
          <TechnologyAnalysis technologiesData={analysisData.technologies} />

          {/* SECTION 6 — CATEGORIZED SKILLS */}
          <SkillCategoryGrid skillsData={analysisData.skills} />

          {/* SECTION 7 — REPOSITORY CATALOG TABLE */}
          <RepositoryTable repos={analysisData.repos} />
        </div>
      ) : (
        /* SECTION 10 — EMPTY STATE */
        <GitHubInitialEmptyState />
      )}
    </div>
  );
};

export default GitHubAnalysis;
