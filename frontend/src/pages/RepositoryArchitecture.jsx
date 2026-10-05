import React, { useState } from 'react';
import {
  Network,
  RotateCcw,
  Sparkles,
  GitBranch,
  Layers,
  Activity,
  AlertTriangle,
  FolderTree,
} from 'lucide-react';
import Button from '../components/common/Button';
import RepositoryArchitectureForm, {
  SAMPLE_REPOSITORIES,
} from '../components/repository-architecture/RepositoryArchitectureForm';
import RepositoryArchitectureEmptyState from '../components/repository-architecture/RepositoryArchitectureEmptyState';
import ArchitectureMetricCards from '../components/repository-architecture/ArchitectureMetricCards';
import ArchitectureOverview from '../components/repository-architecture/ArchitectureOverview';
import ArchitectureDiagram from '../components/repository-architecture/ArchitectureDiagram';
import ArchitectureLayers from '../components/repository-architecture/ArchitectureLayers';
import ProjectStructure from '../components/repository-architecture/ProjectStructure';
import ArchitectureDependencies from '../components/repository-architecture/ArchitectureDependencies';
import {
  analyzeRepositoryArchitecture,
  parseRepositoryInput,
} from '../services/repositoryArchitectureService';

export const RepositoryArchitecture = () => {
  const [repoInput, setRepoInput] = useState('');
  const [branch, setBranch] = useState('');

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [validationError, setValidationError] = useState(null);

  // Analysis result from backend (100% real response)
  const [architectureData, setArchitectureData] = useState(null);

  const handleAnalyze = async () => {
    const parsed = parseRepositoryInput(repoInput);

    if (!parsed.owner || !parsed.repo) {
      setValidationError(
        'Please enter a valid GitHub repository in the format "owner/repo" or "https://github.com/owner/repo".'
      );
      return;
    }

    setValidationError(null);
    setLoading(true);
    setError(null);

    try {
      const response = await analyzeRepositoryArchitecture({
        owner: parsed.owner,
        repo: parsed.repo,
        branch: branch.trim() || undefined,
      });

      setArchitectureData(response);
      setError(null);
    } catch (err) {
      const rawMessage = err.message || '';
      const statusMatch = rawMessage.match(/\b(400|404|422|429|500|502|503|504)\b/);
      const httpStatus = statusMatch ? parseInt(statusMatch[1], 10) : err.response?.status;

      let errorTitle = 'Architecture Analysis Failed';
      let errorMessage =
        rawMessage || 'An unexpected error occurred while communicating with the architecture analysis service.';

      if (httpStatus === 404 || rawMessage.toLowerCase().includes('not found')) {
        errorTitle = 'Repository Not Found';
        errorMessage = `The repository "${parsed.owner}/${parsed.repo}" does not exist on GitHub, is private, or could not be found.`;
      } else if (httpStatus === 422 || rawMessage.toLowerCase().includes('validation')) {
        errorTitle = 'Invalid Repository Identifier';
        errorMessage = 'The backend rejected the request format. Please provide valid owner and repository names.';
      } else if (
        httpStatus === 429 ||
        httpStatus === 502 ||
        rawMessage.toLowerCase().includes('rate limit') ||
        rawMessage.toLowerCase().includes('connect to github')
      ) {
        errorTitle = 'GitHub API Connectivity / Rate Limit';
        errorMessage =
          rawMessage ||
          'The GitHub API rate limit has been exceeded or upstream connectivity failed. Please try again shortly.';
      } else if (
        rawMessage.toLowerCase().includes('network') ||
        rawMessage.toLowerCase().includes('failed to fetch') ||
        rawMessage.toLowerCase().includes('connect')
      ) {
        errorTitle = 'Backend Server Offline';
        errorMessage =
          'Unable to reach the FastAPI backend server at http://localhost:8000. Please verify that the backend process is running.';
      } else if (rawMessage) {
        errorMessage = rawMessage;
      }

      setError({
        title: errorTitle,
        message: errorMessage,
        status: httpStatus || null,
      });
      setArchitectureData(null);
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setRepoInput('');
    setBranch('');
    setArchitectureData(null);
    setError(null);
    setValidationError(null);
  };

  const handleLoadSample = () => {
    const sample = SAMPLE_REPOSITORIES[0];
    setRepoInput(`${sample.owner}/${sample.repo}`);
    setBranch(sample.branch || '');
    setValidationError(null);
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-2 border-b border-slate-200">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-2xs font-bold uppercase tracking-wider text-indigo-600 bg-indigo-50 px-2 py-0.5 rounded-full border border-indigo-100">
              Developer Analysis
            </span>
          </div>
          <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight flex items-center gap-2.5">
            <Network className="w-7 h-7 text-indigo-600" />
            Repository Architecture Analysis
          </h1>
          <p className="text-sm text-slate-500 mt-1 max-w-2xl">
            Inspect the structural organization of public GitHub repositories. Detect architectural layers,
            concrete evidence paths, dependency manifests, and topological project classifications.
          </p>
        </div>

        {architectureData && (
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={handleReset}
              icon={RotateCcw}
              className="text-xs"
            >
              Analyze Another Repository
            </Button>
          </div>
        )}
      </div>

      {/* Repository Target Input Form */}
      <RepositoryArchitectureForm
        repoInput={repoInput}
        setRepoInput={setRepoInput}
        branch={branch}
        setBranch={setBranch}
        onSubmit={handleAnalyze}
        loading={loading}
        validationError={validationError}
        error={error}
        onRetry={handleAnalyze}
        onReset={handleReset}
      />

      {/* State A: Empty State before Analysis */}
      {!architectureData && !loading && (
        <RepositoryArchitectureEmptyState onLoadSample={handleLoadSample} />
      )}

      {/* State B: Loading Skeleton */}
      {loading && (
        <div className="p-12 text-center bg-white rounded-xl border border-slate-200 shadow-sm space-y-4">
          <div className="w-12 h-12 rounded-full bg-indigo-50 text-indigo-600 flex items-center justify-center mx-auto animate-pulse">
            <Network className="w-6 h-6 animate-spin" />
          </div>
          <div>
            <h3 className="text-base font-bold text-slate-900">
              Analyzing Repository Architecture...
            </h3>
            <p className="text-xs text-slate-500 mt-1 max-w-md mx-auto">
              Scanning tree topology, inspecting build manifests, and extracting verified architectural signals.
            </p>
          </div>
        </div>
      )}

      {/* State C: Architecture Analysis Results Dashboard */}
      {architectureData && (
        <div className="space-y-6">
          {/* Summary Metric Cards */}
          <ArchitectureMetricCards data={architectureData} />

          {/* Repository Overview & Subsystem Flags */}
          <ArchitectureOverview data={architectureData} />

          {/* Visual Architecture Diagram */}
          <ArchitectureDiagram
            signals={architectureData.architecture_signals}
            summary={architectureData.summary}
            projectType={architectureData.project_type}
          />

          {/* Verified Architecture Signals & Evidence Paths */}
          <ArchitectureLayers signals={architectureData.architecture_signals} />

          {/* Project Structure Hierarchy */}
          <ProjectStructure
            directories={architectureData.directories_detected}
            importantFiles={architectureData.important_files}
          />

          {/* Technologies & Manifest Inventory */}
          <ArchitectureDependencies
            dependencyFiles={architectureData.dependency_files}
            languages={architectureData.languages_detected}
            documentationFiles={architectureData.documentation_files}
          />
        </div>
      )}
    </div>
  );
};

export default RepositoryArchitecture;
