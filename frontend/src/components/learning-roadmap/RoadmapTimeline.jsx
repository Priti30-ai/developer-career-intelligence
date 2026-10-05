import React from 'react';
import Card from '../common/Card';
import StatusBadge from '../common/StatusBadge';
import {
  Layers,
  GraduationCap,
  Target,
  FolderGit2,
  CheckCircle2,
  ArrowRight,
  BookOpen,
  Sparkles,
  Compass,
} from 'lucide-react';

export const RoadmapTimeline = ({ roadmap = [], targetRole = '' }) => {
  if (!roadmap || roadmap.length === 0) {
    return (
      <Card className="text-center py-8 shadow-sm">
        <CheckCircle2 className="w-10 h-10 text-emerald-500 mx-auto mb-2" />
        <h4 className="text-sm font-bold text-slate-900">
          No Roadmap Stages Required
        </h4>
        <p className="text-xs text-slate-500 mt-1 max-w-md mx-auto">
          Your current skill profile already fulfills all required competencies for {targetRole || 'the target role'}.
        </p>
      </Card>
    );
  }

  return (
    <Card
      title="Sequential Learning Progression"
      subtitle={`Topologically ordered milestones to close skill gaps for ${targetRole}. Stages progress from foundational concepts to advanced systems.`}
      className="shadow-sm mb-6"
    >
      {/* Timeline Steps Indicator Bar */}
      <div className="flex items-center justify-between pb-6 mb-6 border-b border-slate-100 overflow-x-auto gap-2">
        {roadmap.map((stage, idx) => (
          <div key={stage.stage_number} className="flex items-center gap-2 shrink-0">
            <div className="flex items-center gap-2">
              <div className="w-6 h-6 rounded-full bg-indigo-600 text-white font-bold text-xs flex items-center justify-center">
                {stage.stage_number}
              </div>
              <span className="text-xs font-semibold text-slate-800 hidden sm:inline">
                Stage {stage.stage_number}
              </span>
            </div>
            {idx < roadmap.length - 1 && (
              <ArrowRight className="w-4 h-4 text-slate-300 mx-1 shrink-0" />
            )}
          </div>
        ))}
      </div>

      {/* Vertical Timeline Structure */}
      <div className="relative pl-6 sm:pl-8 space-y-8 before:absolute before:left-3 sm:before:left-4 before:top-3 before:bottom-3 before:w-0.5 before:bg-indigo-100">
        {roadmap.map((stage) => {
          return (
            <div key={stage.stage_number} className="relative group">
              {/* Timeline Pin Node */}
              <div className="absolute -left-6 sm:-left-8 top-1.5 w-6 h-6 sm:w-8 sm:h-8 rounded-full bg-white border-2 border-indigo-600 text-indigo-600 font-extrabold text-xs flex items-center justify-center ring-4 ring-indigo-50 shadow-2xs group-hover:bg-indigo-600 group-hover:text-white transition-all">
                {stage.stage_number}
              </div>

              {/* Stage Card */}
              <div className="p-5 sm:p-6 rounded-xl bg-slate-50/70 border border-slate-200/90 shadow-2xs hover:border-indigo-300 hover:bg-white transition-all space-y-4">
                {/* Header */}
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-3 border-b border-slate-200/60">
                  <div>
                    <span className="text-2xs font-bold uppercase tracking-wider text-indigo-600">
                      Milestone Stage {stage.stage_number}
                    </span>
                    <h3 className="text-base font-bold text-slate-900 mt-0.5">
                      {stage.title}
                    </h3>
                  </div>

                  <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-indigo-50 text-indigo-700 border border-indigo-200 self-start sm:self-auto">
                    <Layers className="w-3.5 h-3.5" />
                    {stage.skills.length} {stage.skills.length === 1 ? 'Skill' : 'Skills'}
                  </span>
                </div>

                {/* Milestone Objective Prominently */}
                <div className="p-3.5 rounded-lg bg-white border border-slate-200 text-xs shadow-2xs">
                  <div className="flex items-center gap-1.5 font-semibold text-slate-800 mb-1">
                    <Target className="w-3.5 h-3.5 text-indigo-600 shrink-0" />
                    <span>Learning Milestone Objective:</span>
                  </div>
                  <p className="text-slate-600 leading-relaxed pl-5">
                    {stage.objective}
                  </p>
                </div>

                {/* Skills Addressed */}
                <div>
                  <span className="text-2xs font-semibold uppercase tracking-wider text-slate-400 block mb-2">
                    Competencies Introduced in this Stage:
                  </span>
                  <div className="flex flex-wrap gap-2">
                    {stage.skills.map((skill) => (
                      <span
                        key={skill}
                        className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-white text-slate-800 border border-slate-200 shadow-2xs flex items-center gap-1.5"
                      >
                        <span className="w-2 h-2 rounded-full bg-indigo-500" />
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>

                {/* Recommended Portfolio Projects */}
                {stage.recommended_projects && stage.recommended_projects.length > 0 && (
                  <div className="pt-3 border-t border-slate-200/60">
                    <span className="text-2xs font-semibold uppercase tracking-wider text-slate-400 block mb-2 flex items-center gap-1">
                      <FolderGit2 className="w-3.5 h-3.5 text-emerald-600" />
                      Milestone Portfolio Project Suggestions:
                    </span>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                      {stage.recommended_projects.map((project, pIdx) => (
                        <div
                          key={pIdx}
                          className="p-3 rounded-lg bg-emerald-50/40 border border-emerald-200/70 text-xs flex items-start gap-2.5"
                        >
                          <FolderGit2 className="w-4 h-4 text-emerald-600 mt-0.5 shrink-0" />
                          <div>
                            <span className="font-semibold text-slate-900 block">{project}</span>
                            <span className="text-2xs text-emerald-700/80 mt-0.5 block">
                              Hands-on application verifying Stage {stage.stage_number} skills
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </Card>
  );
};

export default RoadmapTimeline;
