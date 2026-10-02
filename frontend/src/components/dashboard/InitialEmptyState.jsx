import React from 'react';
import Card from '../common/Card';
import { UserCheck, GitBranch, FileSearch, ShieldCheck, ArrowUp } from 'lucide-react';

export const InitialEmptyState = () => {
  const steps = [
    {
      title: '1. Ingest Public Repositories',
      description: 'Scans repositories, primary programming languages, metadata, and topic tags.',
      icon: GitBranch,
    },
    {
      title: '2. Normalize Technologies',
      description: 'Maps raw repository dependencies to canonical technology and framework taxonomy.',
      icon: UserCheck,
    },
    {
      title: '3. Cross-Corroborate Resume',
      description: 'Compares claimed resume competencies against repository ground truth.',
      icon: FileSearch,
    },
    {
      title: '4. Assign Evidence Grounding',
      description: 'Scores evidence deterministically based on repository presence and artifacts.',
      icon: ShieldCheck,
    },
  ];

  return (
    <Card
      title="Awaiting Developer Profile Target"
      subtitle="Enter a GitHub username above to trigger automated repository analysis and evidence synthesis."
    >
      <div className="py-6 px-2 text-center max-w-2xl mx-auto">
        <div className="w-12 h-12 rounded-2xl bg-indigo-50 border border-indigo-100 text-indigo-600 flex items-center justify-center mx-auto mb-3 shadow-sm">
          <ArrowUp className="w-6 h-6 animate-pulse" />
        </div>
        <h3 className="text-base font-semibold text-slate-900 mb-1">
          No Profile Synthesized Yet
        </h3>
        <p className="text-xs text-slate-500 leading-relaxed mb-6">
          Provide a public GitHub handle (e.g., your own or a team member's) in the input section above.
          Optionally attach resume text to benchmark claimed skills against empirical code evidence.
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

export default InitialEmptyState;
