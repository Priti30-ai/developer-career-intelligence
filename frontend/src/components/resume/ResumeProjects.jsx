import React from 'react';
import { FolderGit2, Cpu } from 'lucide-react';
import Card from '../common/Card';

export const ResumeProjects = ({ projects = [] }) => {
  return (
    <Card
      title="Projects & Technical Implementations"
      subtitle="Academic and personal projects identified with associated technologies"
      action={
        <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-100">
          {projects.length} {projects.length === 1 ? 'project' : 'projects'}
        </span>
      }
    >
      {projects.length > 0 ? (
        <div className="space-y-4">
          {projects.map((project, idx) => (
            <div
              key={idx}
              className="p-4 rounded-xl border border-slate-200 bg-white hover:border-slate-300 transition-colors space-y-2.5"
            >
              <div className="flex items-center gap-2">
                <FolderGit2 className="w-4 h-4 text-emerald-600 flex-shrink-0" />
                <h4 className="text-sm font-bold text-slate-900">{project.name}</h4>
              </div>

              {project.description && (
                <p className="text-xs text-slate-600 leading-relaxed pl-6 whitespace-pre-line">
                  {project.description}
                </p>
              )}

              {project.technologies && project.technologies.length > 0 && (
                <div className="pl-6 pt-1 flex items-center gap-1.5 flex-wrap">
                  <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider mr-1">
                    Tech Stack:
                  </span>
                  {project.technologies.map((tech, tIdx) => (
                    <span
                      key={`${tech}-${tIdx}`}
                      className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-medium bg-emerald-50 text-emerald-700 border border-emerald-200"
                    >
                      <Cpu className="w-3 h-3 text-emerald-500" />
                      {tech}
                    </span>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-6 text-slate-500">
          <FolderGit2 className="w-8 h-8 mx-auto text-slate-300 mb-2" />
          <p className="text-xs">No project entries detected in the resume text.</p>
        </div>
      )}
    </Card>
  );
};

export default ResumeProjects;
