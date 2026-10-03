import React from 'react';
import Card from '../common/Card';
import Button from '../common/Button';
import { Search, Github, AlertTriangle, RefreshCw, Loader2 } from 'lucide-react';

export const GitHubAnalysisForm = ({
  username,
  setUsername,
  onSubmit,
  loading,
  validationError,
  error,
  onRetry,
}) => {
  const handleSubmit = (e) => {
    e.preventDefault();
    if (!loading) {
      onSubmit();
    }
  };

  return (
    <Card
      title="Analyze GitHub Target"
      subtitle="Enter a public GitHub username or profile URL to inspect repositories, extract language patterns, and synthesize account-level skill intelligence."
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label
            htmlFor="github-username-field"
            className="block text-xs font-semibold text-slate-700 mb-1.5"
          >
            GitHub Username or Profile URL <span className="text-rose-500">*</span>
          </label>
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
              <Github className="w-4 h-4" />
            </div>
            <input
              id="github-username-field"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              disabled={loading}
              placeholder="e.g. octocat, @octocat, or https://github.com/octocat"
              className={`w-full pl-9 pr-3 py-2 text-sm rounded-lg border bg-white text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-offset-1 transition-all ${
                validationError
                  ? 'border-rose-300 focus:border-rose-500 focus:ring-rose-200'
                  : 'border-slate-300 focus:border-indigo-500 focus:ring-indigo-100'
              } disabled:bg-slate-50 disabled:text-slate-400 disabled:cursor-not-allowed`}
              autoComplete="off"
            />
          </div>
          {validationError && (
            <p className="mt-1.5 text-xs text-rose-600 flex items-center gap-1 font-medium">
              <AlertTriangle className="w-3.5 h-3.5" />
              <span>{validationError}</span>
            </p>
          )}
        </div>

        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pt-1">
          <p className="text-[11px] text-slate-500">
            Analysis inspects public repositories, active primary languages, and declared topics.
          </p>

          <Button
            type="submit"
            variant="primary"
            size="md"
            disabled={loading}
            icon={loading ? Loader2 : Search}
            className={loading ? 'cursor-wait' : ''}
          >
            {loading ? 'Analyzing Repositories...' : 'Analyze GitHub'}
          </Button>
        </div>
      </form>

      {/* Structured Categorized Error Notice */}
      {error && (
        <div className="mt-4 p-4 rounded-xl border border-rose-200 bg-rose-50/70 text-rose-900 text-xs sm:text-sm">
          <div className="flex items-start gap-3">
            <AlertTriangle className="w-5 h-5 text-rose-600 flex-shrink-0 mt-0.5" />
            <div className="flex-1 min-w-0">
              <div className="font-semibold text-rose-950">
                {error.title || 'GitHub Analysis Failed'}
              </div>
              <p className="mt-1 text-rose-800 leading-relaxed">
                {error.message}
              </p>
              {error.status && (
                <div className="mt-1 font-mono text-[11px] text-rose-700">
                  HTTP Status: {error.status}
                </div>
              )}
            </div>
            {onRetry && (
              <Button
                variant="outline"
                size="sm"
                onClick={onRetry}
                icon={RefreshCw}
                className="bg-white hover:bg-rose-50 text-rose-700 border-rose-300 flex-shrink-0"
              >
                Retry
              </Button>
            )}
          </div>
        </div>
      )}
    </Card>
  );
};

export default GitHubAnalysisForm;
