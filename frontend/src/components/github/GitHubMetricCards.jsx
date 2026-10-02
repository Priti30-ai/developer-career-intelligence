import React from 'react';
import {
  FolderGit2,
  Globe,
  Star,
  GitFork,
  Cpu,
  Layers
} from 'lucide-react';

export const GitHubMetricCards = ({ profile, repos = [], skills }) => {
  // Real deterministic derivations from backend payload
  const reposAnalyzed = repos.length;
  const publicReposCount = profile?.public_repos ?? 0;
  const totalStars = repos.reduce((acc, repo) => acc + (repo.stargazers_count || 0), 0);
  const totalForks = repos.reduce((acc, repo) => acc + (repo.forks_count || 0), 0);
  const uniqueTechnologies = skills?.total_unique_technologies ?? 0;
  const categoriesCount = skills?.categories?.length ?? 0;

  const metrics = [
    {
      label: 'Repositories Analyzed',
      value: reposAnalyzed,
      description: 'Active public repos parsed (up to 100)',
      icon: FolderGit2,
      style: 'bg-indigo-50 text-indigo-700 border-indigo-100',
    },
    {
      label: 'Public Repositories',
      value: publicReposCount,
      description: 'Total public repos on account',
      icon: Globe,
      style: 'bg-slate-100 text-slate-700 border-slate-200',
    },
    {
      label: 'Total Stars',
      value: totalStars,
      description: 'Stargazers across analyzed repos',
      icon: Star,
      style: 'bg-amber-50 text-amber-700 border-amber-100',
    },
    {
      label: 'Total Forks',
      value: totalForks,
      description: 'Forks across analyzed repos',
      icon: GitFork,
      style: 'bg-sky-50 text-sky-700 border-sky-100',
    },
    {
      label: 'Unique Technologies',
      value: uniqueTechnologies,
      description: 'Languages & frameworks detected',
      icon: Cpu,
      style: 'bg-emerald-50 text-emerald-700 border-emerald-100',
    },
    {
      label: 'Skill Categories',
      value: categoriesCount,
      description: 'Active taxonomy domain groupings',
      icon: Layers,
      style: 'bg-purple-50 text-purple-700 border-purple-100',
    },
  ];

  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3.5">
      {metrics.map((metric) => {
        const Icon = metric.icon;
        return (
          <div
            key={metric.label}
            className="p-4 rounded-xl border border-slate-200 bg-white shadow-sm flex flex-col justify-between"
          >
            <div className="flex items-center justify-between mb-2">
              <span className="text-[11px] font-medium text-slate-500 uppercase tracking-wider truncate">
                {metric.label}
              </span>
              <div className={`p-1.5 rounded-lg border flex-shrink-0 ${metric.style}`}>
                <Icon className="w-3.5 h-3.5" />
              </div>
            </div>
            <div>
              <div className="text-2xl font-bold text-slate-900 tracking-tight font-mono">
                {metric.value.toLocaleString()}
              </div>
              <p className="text-[11px] text-slate-500 mt-1 leading-snug">
                {metric.description}
              </p>
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default GitHubMetricCards;
