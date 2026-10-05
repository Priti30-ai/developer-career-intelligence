import React, { useState } from 'react';
import Card from '../common/Card';
import Button from '../common/Button';
import {
  Network,
  GitBranch,
  Search,
  Sparkles,
  AlertTriangle,
  RefreshCw,
  Loader2,
  RotateCcw,
  ExternalLink,
  Code2,
} from 'lucide-react';
import { parseRepositoryInput } from '../../services/repositoryArchitectureService';

export const SAMPLE_REPOSITORIES = [
  {
    name: 'Developer Career Intelligence',
    owner: 'Priti30-ai',
    repo: 'developer-career-intelligence',
    branch: 'main',
    type: 'Full-Stack Platform',
  },
  {
    name: 'Octocat Hello-World',
    owner: 'octocat',
    repo: 'Hello-World',
    branch: 'master',
    type: 'Starter Repository',
  },
  {
    name: 'FastAPI Framework',
    owner: 'tiangolo',
    repo: 'fastapi',
    branch: 'master',
    type: 'Python Backend Framework',
  },
];

export const RepositoryArchitectureForm = ({
  repoInput = '',
  setRepoInput,
  branch = '',
  setBranch,
  onSubmit,
  loading = false,
  validationError,
  error,
  onRetry,
  onReset,
}) => {
  const handleLoadSample = (sample) => {
    setRepoInput(`${sample.owner}/${sample.repo}`);
    if (setBranch) {
      setBranch(sample.branch || '');
    }
  };

  const handleFormSubmit = (e) => {
    e.preventDefault();
    if (loading) return;
    onSubmit();
  };

  return (
    <Card className="mb-6 shadow-sm">
      <form onSubmit={handleFormSubmit} className="space-y-5">
        {/* Section Header */}
        <div className="flex items-center justify-between pb-4 border-b border-slate-100 flex-wrap gap-2">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-indigo-50 border border-indigo-100 flex items-center justify-center text-indigo-600">
              <Network className="w-4 h-4" />
            </div>
            <div>
              <h2 className="text-sm font-semibold text-slate-900">Repository Target</h2>
              <p className="text-xs text-slate-500">
                Specify a public GitHub repository to analyze its architectural patterns and file topology.
              </p>
            </div>
          </div>

          {/* Quick Sample Loaders */}
          <div className="flex items-center gap-1.5 flex-wrap">
            <span className="text-xs text-slate-400 mr-1 flex items-center gap-1">
              <Sparkles className="w-3 h-3 text-indigo-500" /> Samples:
            </span>
            {SAMPLE_REPOSITORIES.map((sample) => (
              <button
                key={`${sample.owner}/${sample.repo}`}
                type="button"
                onClick={() => handleLoadSample(sample)}
                className="px-2.5 py-1 text-xs font-medium text-slate-600 bg-slate-50 hover:bg-indigo-50 hover:text-indigo-700 border border-slate-200 rounded-md transition-colors"
                title={`${sample.type}: ${sample.owner}/${sample.repo}`}
              >
                {sample.name}
              </button>
            ))}
          </div>
        </div>

        {/* Inputs Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3.5">
          {/* Main Repo URL / Shorthand */}
          <div className="sm:col-span-2">
            <label
              htmlFor="repo-url-input"
              className="text-xs font-semibold text-slate-700 mb-1.5 flex items-center gap-1.5"
            >
              <GitBranch className="w-3.5 h-3.5 text-indigo-600" />
              GitHub Repository URL or Shorthand
              <span className="text-rose-500">*</span>
            </label>
            <div className="relative">
              <input
                id="repo-url-input"
                type="text"
                value={repoInput}
                onChange={(e) => setRepoInput(e.target.value)}
                placeholder="e.g. owner/repo or https://github.com/owner/repo"
                disabled={loading}
                className="w-full px-3.5 py-2.5 bg-white border border-slate-200 rounded-lg text-sm text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all disabled:bg-slate-50 font-mono text-xs"
              />
            </div>
            <p className="text-2xs text-slate-400 mt-1">
              Accepts <code className="font-mono">owner/repo</code>, <code className="font-mono">https://github.com/owner/repo</code>, or GitHub web URLs.
            </p>
          </div>

          {/* Optional Branch */}
          <div>
            <label
              htmlFor="branch-input"
              className="text-xs font-semibold text-slate-700 mb-1.5 flex items-center gap-1.5"
            >
              <Code2 className="w-3.5 h-3.5 text-slate-400" />
              Branch / Commit
              <span className="text-slate-400 font-normal">(optional)</span>
            </label>
            <input
              id="branch-input"
              type="text"
              value={branch}
              onChange={(e) => setBranch(e.target.value)}
              placeholder="e.g. main, master"
              disabled={loading}
              className="w-full px-3.5 py-2.5 bg-white border border-slate-200 rounded-lg text-sm text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all disabled:bg-slate-50 font-mono text-xs"
            />
            <p className="text-2xs text-slate-400 mt-1">
              Defaults to repository's default branch.
            </p>
          </div>
        </div>

        {/* Validation Warning Banner */}
        {validationError && (
          <div className="p-3 bg-amber-50 border border-amber-200 rounded-lg flex items-start gap-2.5 text-xs text-amber-800">
            <AlertTriangle className="w-4 h-4 text-amber-600 mt-0.5 shrink-0" />
            <div>
              <p className="font-semibold">Validation Required</p>
              <p className="mt-0.5">{validationError}</p>
            </div>
          </div>
        )}

        {/* API Error Banner */}
        {error && (
          <div className="p-3.5 bg-rose-50 border border-rose-200 rounded-lg flex items-start justify-between gap-3 text-xs text-rose-800">
            <div className="flex items-start gap-2.5">
              <AlertTriangle className="w-4 h-4 text-rose-600 mt-0.5 shrink-0" />
              <div>
                <p className="font-semibold">{error.title || 'Architecture Analysis Failed'}</p>
                <p className="mt-0.5 text-rose-700">{error.message}</p>
              </div>
            </div>
            {onRetry && (
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={onRetry}
                icon={RefreshCw}
                className="shrink-0 text-xs bg-white text-rose-700 border-rose-300 hover:bg-rose-100"
              >
                Retry
              </Button>
            )}
          </div>
        )}

        {/* Action Controls */}
        <div className="pt-2 flex items-center justify-between flex-wrap gap-3">
          <div className="text-xs text-slate-500">
            Inspecting file trees and structural configurations via GitHub API.
          </div>

          <div className="flex items-center gap-2">
            {onReset && (
              <Button
                type="button"
                variant="ghost"
                size="md"
                onClick={onReset}
                disabled={loading}
                icon={RotateCcw}
              >
                Reset
              </Button>
            )}

            <Button
              type="submit"
              variant="primary"
              size="md"
              disabled={loading}
              icon={loading ? Loader2 : Search}
              className={loading ? 'cursor-not-allowed opacity-80' : ''}
            >
              {loading ? (
                <span className="flex items-center gap-2">
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Analyzing Architecture...
                </span>
              ) : (
                'Analyze Repository Architecture'
              )}
            </Button>
          </div>
        </div>
      </form>
    </Card>
  );
};

export default RepositoryArchitectureForm;
