import React from 'react';
import {
  User,
  Cpu,
  Briefcase,
  FolderGit2,
  GraduationCap,
  Award,
  Trophy,
  FileText,
  Calendar,
} from 'lucide-react';
import Card from '../common/Card';

export const ResumeSummaryCard = ({ analysis, fileMeta = null }) => {
  if (!analysis) return null;

  const {
    summary,
    skill_count,
    experience_count,
    project_count,
    education = [],
    certifications = [],
    achievements = [],
  } = analysis;

  const metrics = [
    {
      label: 'Extracted Skills',
      value: skill_count ?? 0,
      icon: Cpu,
      color: 'text-indigo-600',
      bgColor: 'bg-indigo-50',
    },
    {
      label: 'Experience Entries',
      value: experience_count ?? 0,
      icon: Briefcase,
      color: 'text-sky-600',
      bgColor: 'bg-sky-50',
    },
    {
      label: 'Projects Parsed',
      value: project_count ?? 0,
      icon: FolderGit2,
      color: 'text-emerald-600',
      bgColor: 'bg-emerald-50',
    },
    {
      label: 'Education Entries',
      value: education.length,
      icon: GraduationCap,
      color: 'text-violet-600',
      bgColor: 'bg-violet-50',
    },
    {
      label: 'Certifications',
      value: certifications.length,
      icon: Award,
      color: 'text-amber-600',
      bgColor: 'bg-amber-50',
    },
    {
      label: 'Achievements',
      value: achievements.length,
      icon: Trophy,
      color: 'text-rose-600',
      bgColor: 'bg-rose-50',
    },
  ];

  return (
    <Card className="border-slate-200">
      <div className="space-y-6">
        {/* Header & Meta */}
        <div className="flex items-start justify-between flex-wrap gap-4 pb-4 border-b border-slate-100">
          <div className="flex items-center gap-3">
            <div className="w-11 h-11 rounded-xl bg-indigo-600 text-white flex items-center justify-center font-bold shadow-sm">
              <User className="w-6 h-6" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-slate-900 tracking-tight">
                Candidate Profile Overview
              </h3>
              <p className="text-xs text-slate-500">
                Deterministic structured representation extracted from resume
              </p>
            </div>
          </div>

          {fileMeta && (
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-50 border border-slate-200 text-xs text-slate-600">
              <FileText className="w-3.5 h-3.5 text-slate-400" />
              <span className="font-medium text-slate-700">{fileMeta.name}</span>
              <span className="text-slate-300">•</span>
              <span>{(fileMeta.size / 1024).toFixed(1)} KB</span>
            </div>
          )}
        </div>

        {/* Professional Summary Section (if present in backend response) */}
        {summary && summary.trim() ? (
          <div>
            <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">
              Professional Summary
            </h4>
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-200/80 text-sm text-slate-700 leading-relaxed">
              {summary}
            </div>
          </div>
        ) : (
          <div className="p-3.5 rounded-lg bg-slate-50/80 border border-slate-200/60 text-xs text-slate-500 italic">
            No dedicated summary or objective section was detected in the resume text.
          </div>
        )}

        {/* Real Metrics Grid */}
        <div>
          <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-3">
            Structured Extraction Counts
          </h4>
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
            {metrics.map((m) => {
              const Icon = m.icon;
              return (
                <div
                  key={m.label}
                  className="p-3.5 rounded-xl border border-slate-200/90 bg-white hover:border-slate-300 transition-colors"
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs text-slate-500 font-medium">{m.label}</span>
                    <div className={`p-1.5 rounded-lg ${m.bgColor} ${m.color}`}>
                      <Icon className="w-3.5 h-3.5" />
                    </div>
                  </div>
                  <div className="text-xl font-bold text-slate-900 tracking-tight">
                    {m.value}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </Card>
  );
};

export default ResumeSummaryCard;
