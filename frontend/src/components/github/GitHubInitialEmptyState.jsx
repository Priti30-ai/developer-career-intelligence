import React from 'react';
import Card from '../common/Card';
import { GitBranch, FolderGit2, Cpu, Layers, ArrowUp } from 'lucide-react';

export const GitHubInitialEmptyState = () => {
  const steps = [
    {
      title: '1. Profile Extraction',
      description: 'Queries public account metadata, identity information, repository count, and follower activity.',
      icon: GitBranch,
    },
    {
      title: '2. Repository Inspection',
      description: 'Collects up to 100 recent public repositories, stargazers, forks, and topic labels.',
      icon: FolderGit2,
    },
    {
      title: '3. Technology Signal Detection',
      description: 'Normalizes programming languages and package topics against a canonical technology taxonomy.',
      icon: Cpu,
    },
    {
      title: '4. Skill Categorization',
      description: 'Classifies detected technologies into engineering domains with repository presence weighting.',
      icon: Layers,
    },
  ];

  return (
    <Card
      title="Awaiting GitHub Account Query"
      subtitle="Enter a public GitHub handle above to trigger the 4-stage repository and skill intelligence pipeline."
    >
      <div className="py-6 px-2 text-center max-w-2xl mx-auto">
        <div className="w-12 h-12 rounded-2xl bg-indigo-50 border border-indigo-100 text-indigo-600 flex items-center justify-center mx-auto mb-3 shadow-sm">
          <ArrowUp className="w-6 h-6 animate-pulse" />
        </div>
        <h3 className="text-base font-semibold text-slate-900 mb-1">
          No GitHub Profile Analyzed Yet
        </h3>
        <p className="text-xs text-slate-500 leading-relaxed mb-6">
          Provide a public GitHub username (for example, <code className="font-mono text-indigo-600 bg-indigo-50 px-1 py-0.5 rounded">octocat</code> or your personal GitHub handle) to evaluate repositories and extract empirical engineering skills.
        </p>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-left">
          {steps.map((step) => {
            const Icon = step.icon;
            return (
              <div
                key={step.title}
                className="p-3.5 rounded-lg border border-slate-200/90 bg-slate-50/60"
              >
                <div className="flex items-center gap-2 mb-1 text-xs font-semibold text-slate-800">
                  <Icon className="w-4 h-4 text-indigo-600 flex-shrink-0" />
                  <span>{step.title}</span>
                </div>
                <p className="text-[11px] text-slate-500 leading-normal pl-6">
                  {step.description}
                </p>
              </div>
            );
          })}
        </div>
      </div>
    </Card>
  );
};

export default GitHubInitialEmptyState;
