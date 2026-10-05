import React from 'react';
import Card from '../common/Card';
import StatusBadge from '../common/StatusBadge';
import {
  GitBranch,
  ExternalLink,
  Layers,
  Server,
  Monitor,
  Database,
  Container,
  FileText,
  CheckCircle2,
  XCircle,
  Code2,
} from 'lucide-react';

export const ArchitectureOverview = ({ data }) => {
  if (!data) return null;

  const {
    repository = {},
    project_type = 'UNKNOWN',
    primary_language,
    languages_detected = [],
    summary = {},
  } = data;

  const capabilities = [
    {
      label: 'Frontend Interface',
      detected: summary.has_frontend,
      icon: Monitor,
      description: 'Web client, templates, or component hierarchy',
    },
    {
      label: 'Backend / API Layer',
      detected: summary.has_backend,
      icon: Server,
      description: 'Routing, services, controllers, or business logic',
    },
    {
      label: 'Database / Storage',
      detected: summary.has_database,
      icon: Database,
      description: 'Migrations, SQL scripts, models, or ORM schemas',
    },
    {
      label: 'DevOps / Containerization',
      detected: summary.has_devops,
      icon: Container,
      description: 'Dockerfile, compose files, or CI/CD pipelines',
    },
    {
      label: 'Structured Documentation',
      detected: summary.has_documentation,
      icon: FileText,
      description: 'Architecture guides, API docs, or specs',
    },
  ];

  return (
    <Card className="mb-6 shadow-sm overflow-hidden border-indigo-100 bg-gradient-to-br from-white via-indigo-50/15 to-white">
      {/* Top Header: Repo Title & Link */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-5 border-b border-slate-100">
        <div className="flex items-start gap-3.5">
          <div className="w-12 h-12 rounded-xl bg-indigo-600 text-white flex items-center justify-center font-bold text-lg shrink-0 shadow-sm shadow-indigo-200">
            <GitBranch className="w-6 h-6" />
          </div>

          <div>
            <div className="flex items-center gap-2 flex-wrap mb-1">
              <span className="text-xs font-semibold uppercase tracking-wider text-indigo-600">
                Analyzed Repository
              </span>
              <StatusBadge status="info" text={project_type} />
            </div>

            <h2 className="text-xl sm:text-2xl font-bold text-slate-900 tracking-tight flex items-center gap-2">
              <span>{repository.full_name || repository.name}</span>
              {repository.html_url && (
                <a
                  href={repository.html_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-slate-400 hover:text-indigo-600 transition-colors"
                  title="View repository on GitHub"
                >
                  <ExternalLink className="w-4 h-4" />
                </a>
              )}
            </h2>

            <div className="flex items-center gap-3 text-xs text-slate-500 mt-1 flex-wrap">
              {repository.default_branch && (
                <span>
                  Default Branch: <code className="font-mono bg-slate-100 px-1.5 py-0.5 rounded text-slate-700">{repository.default_branch}</code>
                </span>
              )}
              {primary_language && (
                <span>
                  • Primary: <strong className="text-slate-700">{primary_language}</strong>
                </span>
              )}
              {languages_detected.length > 0 && (
                <span>
                  • Languages: <span className="text-slate-600">{languages_detected.join(', ')}</span>
                </span>
              )}
            </div>
          </div>
        </div>

        {/* Primary Project Classification Pill */}
        <div className="p-3 bg-white rounded-xl border border-slate-200 shadow-2xs self-stretch sm:self-auto text-right">
          <span className="text-2xs font-semibold uppercase tracking-wider text-slate-400 block">
            Topology Classification
          </span>
          <span className="text-sm font-bold text-slate-900 block mt-0.5">
            {project_type}
          </span>
        </div>
      </div>

      {/* Structural Capability Checklist */}
      <div className="pt-5">
        <span className="text-2xs font-semibold uppercase tracking-wider text-slate-400 block mb-3">
          Detected Architectural Subsystems & Capabilities:
        </span>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
          {capabilities.map((cap) => {
            const Icon = cap.icon;
            return (
              <div
                key={cap.label}
                className={`p-3 rounded-lg border transition-all flex flex-col justify-between ${
                  cap.detected
                    ? 'bg-white border-emerald-200 shadow-2xs'
                    : 'bg-slate-50/60 border-slate-200/80 opacity-75'
                }`}
              >
                <div className="flex items-center justify-between mb-1.5">
                  <div
                    className={`w-7 h-7 rounded-md flex items-center justify-center ${
                      cap.detected ? 'bg-emerald-50 text-emerald-700' : 'bg-slate-200/60 text-slate-400'
                    }`}
                  >
                    <Icon className="w-4 h-4" />
                  </div>
                  {cap.detected ? (
                    <span className="inline-flex items-center gap-1 text-2xs font-semibold text-emerald-700">
                      <CheckCircle2 className="w-3.5 h-3.5" />
                      Detected
                    </span>
                  ) : (
                    <span className="inline-flex items-center gap-1 text-2xs text-slate-400">
                      <XCircle className="w-3.5 h-3.5" />
                      None
                    </span>
                  )}
                </div>

                <div>
                  <h4 className="text-xs font-bold text-slate-800">{cap.label}</h4>
                  <p className="text-2xs text-slate-500 mt-0.5 leading-snug">{cap.description}</p>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </Card>
  );
};

export default ArchitectureOverview;
