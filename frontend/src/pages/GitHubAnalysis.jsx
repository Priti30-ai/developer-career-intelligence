import React, { useState } from 'react';
import { GitBranch, Sparkles } from 'lucide-react';
import GitHubAnalysisForm from '../components/github/GitHubAnalysisForm';
import GitHubProfileCard from '../components/github/GitHubProfileCard';
import GitHubMetricCards from '../components/github/GitHubMetricCards';
import TechnologyAnalysis from '../components/github/TechnologyAnalysis';
import SkillCategoryGrid from '../components/github/SkillCategoryGrid';
import RepositoryTable from '../components/github/RepositoryTable';
import GitHubInitialEmptyState from '../components/github/GitHubInitialEmptyState';
import RepositoryCoverageCards from '../components/github/RepositoryCoverageCards';
import EvidenceSummaryPanel from '../components/github/EvidenceSummaryPanel';
import { getGitHubAccountAnalysis } from '../services/githubService';

export const GitHubAnalysis = () => {
  const [username, setUsername] = useState('');
  const [loading, setLoading] = useState(false);
  const [analysisData, setAnalysisData] = useState(null);
  const [error, setError] = useState(null);
  const [validationError, setValidationError] = useState(null);

  const handleAnalyze = async () => {
    const cleanInput = username.trim();

    if (!cleanInput) {
      setValidationError('GitHub username or profile URL is required. Please enter a valid public handle or URL.');
      return;
    }

    setValidationError(null);
    setLoading(true);
    setError(null);

    try {
      // Single unified backend request orchestrating discovery, inspection, evidence, and aggregation
      const data = await getGitHubAccountAnalysis(cleanInput);
      setAnalysisData(data);
      setError(null);
    } catch (err) {
      const rawMessage = err.message || '';
      const httpStatus =
        err.status ||
        (rawMessage.match(/\b(404|403|422|429|500|502|504)\b/)
          ? parseInt(rawMessage.match(/\b(404|403|422|429|500|502|504)\b/)[1], 10)
          : null);

      let errorTitle = 'GitHub Analysis Failed';
      let errorMessage =
        rawMessage || 'An unexpected error occurred while communicating with GitHub services.';

      if (httpStatus === 404 || rawMessage.toLowerCase().includes('not found')) {
        errorTitle = 'GitHub Account Not Found';
        errorMessage = rawMessage.toLowerCase().includes('not found')
          ? rawMessage
          : `The user "${cleanInput}" does not exist on GitHub or could not be found. Please check the spelling.`;
      } else if (
        httpStatus === 422 ||
        rawMessage.toLowerCase().includes('unprocessable') ||
        rawMessage.toLowerCase().includes('invalid')
      ) {
        errorTitle = 'Invalid GitHub Target';
        errorMessage = rawMessage || 'The username or profile URL is invalid or malformed.';
      } else if (
        httpStatus === 403 ||
        httpStatus === 429 ||
        rawMessage.toLowerCase().includes('rate limit') ||
        rawMessage.toLowerCase().includes('forbidden') ||
        rawMessage.toLowerCase().includes('too many requests')
      ) {
        errorTitle = 'GitHub API Rate Limit Reached';
        errorMessage =
          rawMessage ||
          'The GitHub API rate limit has been exceeded. Please wait a short while or configure a personal token on the backend.';
      } else if (
        httpStatus === 502 ||
        rawMessage.toLowerCase().includes('connect to github') ||
        rawMessage.toLowerCase().includes('unable to reach')
      ) {
        errorTitle = 'GitHub Connectivity Error';
        errorMessage =
          rawMessage ||
          'The backend service could not establish a connection to api.github.com. Please check external network availability.';
      } else if (httpStatus === 504 || rawMessage.toLowerCase().includes('timed out')) {
        errorTitle = 'GitHub Gateway Timeout';
        errorMessage =
          rawMessage ||
          'GitHub API took longer than expected to respond. The account may have an exceptionally large repository index.';
      } else if (
        rawMessage.toLowerCase().includes('network') ||
        rawMessage.toLowerCase().includes('failed to fetch') ||
        rawMessage.toLowerCase().includes('connect')
      ) {
        errorTitle = 'Backend Server Offline';
        errorMessage =
          'Unable to reach the FastAPI backend server at http://localhost:8000. Please verify that the backend process is running.';
      }

      setError({
        title: errorTitle,
        message: errorMessage,
        status: httpStatus || null,
      });
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

          {/* SECTION 5 — REPOSITORY COVERAGE */}
          <RepositoryCoverageCards coverage={analysisData.repository_coverage} />

          {/* SECTION 6 — EVIDENCE SUMMARY */}
          <EvidenceSummaryPanel evidenceSummary={analysisData.evidence_summary} />

          {/* SECTION 7 — TECHNOLOGY ANALYSIS & BAR CHART */}
          <TechnologyAnalysis technologiesData={analysisData.technologies} />

          {/* SECTION 8 — CATEGORIZED SKILLS */}
          <SkillCategoryGrid skillsData={analysisData.skills} />

          {/* SECTION 9 — REPOSITORY CATALOG TABLE */}
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
