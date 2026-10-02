import React from 'react';
import {
  FileText,
  Cpu,
  GraduationCap,
  Briefcase,
  FolderGit2,
  CheckCircle2,
  AlertTriangle,
} from 'lucide-react';
import Card from '../common/Card';

export const ResumeInitialEmptyState = ({ onSelectFileClick }) => {
  const capabilities = [
    {
      title: 'Deterministic Section Segmentation',
      description: 'Accurately partitions Summary, Skills, Experience, Education, Projects, and Certifications.',
      icon: FileText,
      color: 'text-indigo-600',
      bgColor: 'bg-indigo-50',
    },
    {
      title: 'Canonical Skill Normalization',
      description: 'Maps aliases and variations (e.g., nodejs -> Node.js, cpp -> C++) into canonical taxonomy standards.',
      icon: Cpu,
      color: 'text-emerald-600',
      bgColor: 'bg-emerald-50',
    },
    {
      title: 'Career & Timeline Alignment',
      description: 'Extracts roles, employers, date ranges, and responsibilities for downstream career evidence checks.',
      icon: Briefcase,
      color: 'text-sky-600',
      bgColor: 'bg-sky-50',
    },
    {
      title: 'Project Technology Detection',
      description: 'Discovers academic and personal projects and identifies embedded technical stacks.',
      icon: FolderGit2,
      color: 'text-violet-600',
      bgColor: 'bg-violet-50',
    },
  ];

  return (
    <div className="space-y-6">
      {/* Empty State Banner */}
      <Card className="border-dashed border-2 border-slate-300 bg-slate-50/40 text-center py-10 px-6">
        <div className="max-w-md mx-auto space-y-3">
          <div className="w-14 h-14 rounded-2xl bg-indigo-50 text-indigo-600 flex items-center justify-center mx-auto shadow-xs border border-indigo-100">
            <FileText className="w-7 h-7" />
          </div>
          <h3 className="text-base sm:text-lg font-bold text-slate-900 tracking-tight">
            No analysis has been performed yet
          </h3>
          <p className="text-xs sm:text-sm text-slate-500 leading-relaxed">
            Upload your resume or paste plain text above to extract and analyze your structured professional profile.
          </p>

          <div className="pt-2">
            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg bg-white border border-slate-200 text-xs text-slate-600 shadow-2xs">
              <span className="w-2 h-2 rounded-full bg-emerald-500" />
              Supported formats: <strong className="text-slate-800 font-semibold">PDF, DOCX or TXT</strong> (Max 5 MB)
            </div>
          </div>
        </div>
      </Card>

      {/* Parser Capabilities Cards */}
      <div>
        <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-3">
          Analysis Engine Features
        </h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5">
          {capabilities.map((cap) => {
            const Icon = cap.icon;
            return (
              <div
                key={cap.title}
                className="p-4 rounded-xl border border-slate-200 bg-white hover:border-slate-300 transition-colors flex items-start gap-3.5"
              >
                <div className={`p-2.5 rounded-xl ${cap.bgColor} ${cap.color} flex-shrink-0`}>
                  <Icon className="w-5 h-5" />
                </div>
                <div>
                  <h5 className="text-sm font-semibold text-slate-900">{cap.title}</h5>
                  <p className="text-xs text-slate-500 mt-1 leading-relaxed">{cap.description}</p>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default ResumeInitialEmptyState;
