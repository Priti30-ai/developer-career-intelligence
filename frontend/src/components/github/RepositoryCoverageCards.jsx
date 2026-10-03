import React from 'react';
import {
  FolderGit2,
  GitFork,
  Archive,
  Activity,
  CheckCircle2,
  AlertTriangle,
  MinusCircle,
  XCircle,
} from 'lucide-react';

/**
 * RepositoryCoverageCards
 *
 * Displays deterministic per-repository coverage statistics from RepositoryCoverage schema.
 * Values are factual counts derived directly from the backend analysis pipeline.
 * No scores, rankings, or subjective labels.
 */
export const RepositoryCoverageCards = ({ coverage = {} }) => {
  const {
    total_repositories_analyzed = 0,
    original_repositories = 0,
    forked_repositories = 0,
    archived_repositories = 0,
    active_repositories = 0,
    successfully_analyzed_repositories = 0,
    partially_analyzed_repositories = 0,
    empty_repositories = 0,
    error_repositories = 0,
  } = coverage;

  if (total_repositories_analyzed === 0) return null;

  const tiles = [
    {
      label: 'Analyzed',
      value: total_repositories_analyzed,
      description: 'Total repositories inspected',
      icon: FolderGit2,
      color: 'text-indigo-700 bg-indigo-50 border-indigo-100',
    },
    {
      label: 'Original',
      value: original_repositories,
      description: 'Non-fork repositories',
      icon: FolderGit2,
      color: 'text-slate-700 bg-slate-100 border-slate-200',
    },
    {
      label: 'Forks',
      value: forked_repositories,
      description: 'Forked from other projects',
      icon: GitFork,
      color: 'text-sky-700 bg-sky-50 border-sky-100',
    },
    {
      label: 'Active',
      value: active_repositories,
      description: 'Non-archived repositories',
      icon: Activity,
      color: 'text-emerald-700 bg-emerald-50 border-emerald-100',
    },
    {
      label: 'Archived',
      value: archived_repositories,
      description: 'Read-only / archived',
      icon: Archive,
      color: 'text-amber-700 bg-amber-50 border-amber-100',
    },
    {
      label: 'Full Analysis',
      value: successfully_analyzed_repositories,
      description: 'Inspected without warnings',
      icon: CheckCircle2,
      color: 'text-teal-700 bg-teal-50 border-teal-100',
    },
    {
      label: 'Partial',
      value: partially_analyzed_repositories,
      description: 'Tree truncated or limited',
      icon: AlertTriangle,
      color: 'text-orange-700 bg-orange-50 border-orange-100',
    },
    {
      label: 'Empty',
      value: empty_repositories,
      description: 'No commits or files',
      icon: MinusCircle,
      color: 'text-slate-400 bg-slate-50 border-slate-200',
    },
    ...(error_repositories > 0
      ? [
          {
            label: 'Errors',
            value: error_repositories,
            description: 'Fatal inspection errors',
            icon: XCircle,
            color: 'text-red-700 bg-red-50 border-red-100',
          },
        ]
      : []),
  ];

  return (
    <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-slate-900">Repository Coverage</h3>
        <p className="text-xs text-slate-500 mt-0.5">
          Deterministic breakdown of the {total_repositories_analyzed} public repositories retrieved and analyzed.
        </p>
      </div>
      <div className="grid grid-cols-3 sm:grid-cols-4 lg:grid-cols-9 gap-2.5">
        {tiles.map((tile) => {
          const Icon = tile.icon;
          return (
            <div
              key={tile.label}
              className="flex flex-col items-center gap-1.5 p-3 rounded-lg border border-slate-100 bg-slate-50/60 text-center"
            >
              <div className={`p-1.5 rounded-md border ${tile.color}`}>
                <Icon className="w-3.5 h-3.5" />
              </div>
              <span className="text-xl font-bold font-mono text-slate-900 leading-none">
                {tile.value}
              </span>
              <span className="text-[10px] font-semibold text-slate-600 uppercase tracking-wide leading-tight">
                {tile.label}
              </span>
              <span className="text-[10px] text-slate-400 leading-tight hidden sm:block">
                {tile.description}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default RepositoryCoverageCards;
