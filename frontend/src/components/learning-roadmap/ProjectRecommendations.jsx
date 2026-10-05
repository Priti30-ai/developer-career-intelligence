import React from 'react';
import Card from '../common/Card';
import {
  FolderGit2,
  Sparkles,
  Layers,
  Tag,
  ExternalLink,
  Code2,
} from 'lucide-react';

export const ProjectRecommendations = ({ roadmap = [], recommendations = [], targetRole = '' }) => {
  // Aggregate real projects from both roadmap stages and skill recommendations
  const stageProjectsMap = new Map();

  roadmap.forEach((stage) => {
    (stage.recommended_projects || []).forEach((proj) => {
      if (!stageProjectsMap.has(proj)) {
        stageProjectsMap.set(proj, {
          title: proj,
          stageTitle: stage.title,
          stageNumber: stage.stage_number,
          associatedSkills: stage.skills || [],
          source: 'Roadmap Milestone',
        });
      }
    });
  });

  recommendations.forEach((rec) => {
    (rec.suggested_projects || []).forEach((proj) => {
      if (!stageProjectsMap.has(proj)) {
        stageProjectsMap.set(proj, {
          title: proj,
          stageTitle: `Skill: ${rec.skill}`,
          stageNumber: null,
          associatedSkills: [rec.skill],
          source: 'Skill Guidance',
        });
      }
    });
  });

  const projectList = Array.from(stageProjectsMap.values());

  if (projectList.length === 0) {
    return null;
  }

  return (
    <Card
      title="Actionable Portfolio Projects"
      subtitle={`Hands-on practical projects recommended by the backend to verify competency for ${targetRole}.`}
      className="shadow-sm mb-6"
    >
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5">
        {projectList.map((project, idx) => (
          <div
            key={idx}
            className="p-4 rounded-xl bg-slate-50/70 border border-slate-200 hover:border-indigo-300 hover:bg-white transition-all flex flex-col justify-between"
          >
            <div>
              <div className="flex items-start justify-between gap-2 mb-2">
                <div className="w-8 h-8 rounded-lg bg-emerald-50 border border-emerald-200 flex items-center justify-center text-emerald-700 shrink-0">
                  <FolderGit2 className="w-4 h-4" />
                </div>
                {project.stageNumber ? (
                  <span className="text-2xs font-semibold px-2 py-0.5 rounded-full bg-indigo-50 text-indigo-700 border border-indigo-200">
                    Stage {project.stageNumber} Project
                  </span>
                ) : (
                  <span className="text-2xs font-semibold px-2 py-0.5 rounded-full bg-slate-100 text-slate-700 border border-slate-200">
                    {project.source}
                  </span>
                )}
              </div>

              <h4 className="text-sm font-bold text-slate-900 mb-1">
                {project.title}
              </h4>
              <p className="text-xs text-slate-500 leading-relaxed">
                Applies {project.associatedSkills.join(', ')} to build production-grade artifacts demonstrating career readiness.
              </p>
            </div>

            <div className="mt-3 pt-3 border-t border-slate-200/60 flex items-center justify-between text-2xs text-slate-400">
              <span className="flex items-center gap-1">
                <Tag className="w-3 h-3 text-slate-400" />
                {project.associatedSkills.slice(0, 3).join(', ')}
                {project.associatedSkills.length > 3 && ` +${project.associatedSkills.length - 3} more`}
              </span>
              <span className="font-medium text-emerald-700">Verified Curriculum</span>
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
};

export default ProjectRecommendations;
