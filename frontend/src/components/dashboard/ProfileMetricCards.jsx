import React from 'react';
import {
  Sparkles,
  GitBranch,
  FileText,
  CheckCheck,
  AlertCircle,
  FolderGit2
} from 'lucide-react';

export const ProfileMetricCards = ({ summary, github }) => {
  if (!summary) return null;

  const metrics = [
    {
      label: 'Total Identified Skills',
      value: summary.total_skills ?? 0,
      description: 'Canonical skills across all input channels',
      icon: Sparkles,
      color: 'indigo',
    },
    {
      label: 'Repositories Analyzed',
      value: github?.repositories_analyzed ?? 0,
      description: 'Public git repositories inspected',
      icon: FolderGit2,
      color: 'slate',
    },
    {
      label: 'GitHub Backed Skills',
      value: summary.github_skill_count ?? 0,
      description: 'Skills with detected code artifacts',
      icon: GitBranch,
      color: 'emerald',
    },
    {
      label: 'Resume Claimed Skills',
      value: summary.resume_skill_count ?? 0,
      description: 'Skills extracted from candidate resume',
      icon: FileText,
      color: 'sky',
    },
    {
      label: 'Corroborated Skills',
      value: summary.skills_from_both_sources ?? 0,
      description: 'Present in both GitHub & Resume',
      icon: CheckCheck,
      color: 'purple',
    },
    {
      label: 'Unbacked by GitHub',
      value: summary.skills_without_github_evidence ?? 0,
      description: 'Resume-only (no repo evidence found)',
      icon: AlertCircle,
      color: 'amber',
    },
  ];

  const colorStyles = {
    indigo: 'bg-indigo-50 text-indigo-700 border-indigo-100',
    slate: 'bg-slate-100 text-slate-700 border-slate-200',
    emerald: 'bg-emerald-50 text-emerald-700 border-emerald-100',
    sky: 'bg-sky-50 text-sky-700 border-sky-100',
    purple: 'bg-purple-50 text-purple-700 border-purple-100',
    amber: 'bg-amber-50 text-amber-700 border-amber-100',
  };

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
              <div
                className={`p-1.5 rounded-lg border flex-shrink-0 ${
                  colorStyles[metric.color] || colorStyles.indigo
                }`}
              >
                <Icon className="w-3.5 h-3.5" />
              </div>
            </div>
            <div>
              <div className="text-2xl font-bold text-slate-900 tracking-tight">
                {metric.value}
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

export default ProfileMetricCards;
