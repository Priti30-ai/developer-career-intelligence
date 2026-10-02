import React from 'react';
import Card from '../common/Card';
import {
  Code,
  Layers,
  Cpu,
  Globe,
  Database,
  Cloud,
  Terminal,
  Info
} from 'lucide-react';

const CATEGORY_ICONS = {
  'Programming Languages': Code,
  'Frameworks & Libraries': Layers,
  'AI / Machine Learning': Cpu,
  'Web Technologies': Globe,
  'Databases': Database,
  'DevOps & Cloud': Cloud,
  'Tools & Other': Terminal,
};

export const SkillCategoryGrid = ({ skillsData }) => {
  const categories = skillsData?.categories || [];
  const totalUnique = skillsData?.total_unique_technologies ?? 0;

  return (
    <Card
      title={`Categorized Developer Skill Profile (${totalUnique} Unique Skills)`}
      subtitle="Structured classification of repository-detected technologies mapped into canonical engineering domains."
    >
      <div className="space-y-4">
        {/* Semantic Clarification Note */}
        <div className="flex items-start gap-2.5 p-3 rounded-lg bg-slate-50 border border-slate-200 text-xs text-slate-600 leading-relaxed">
          <Info className="w-4 h-4 text-indigo-600 flex-shrink-0 mt-0.5" />
          <div>
            <strong>Evaluation Semantics:</strong> Each badge indicates the number of analyzed public repositories in which the language or framework was identified. This reflects empirical code artifact frequency, not proven mastery or seniority.
          </div>
        </div>

        {categories.length === 0 ? (
          <div className="text-center py-8 text-xs text-slate-400">
            No categorized skill data available for this profile.
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {categories.map((catGroup) => {
              const IconComponent = CATEGORY_ICONS[catGroup.category] || Layers;
              const skillItems = catGroup.skills || [];

              return (
                <div
                  key={catGroup.category}
                  className="p-4 rounded-xl border border-slate-200 bg-white hover:border-slate-300 transition-colors flex flex-col justify-between"
                >
                  <div>
                    <div className="flex items-center justify-between pb-2.5 mb-3 border-b border-slate-100">
                      <div className="flex items-center gap-2">
                        <div className="p-1.5 rounded-lg bg-indigo-50 text-indigo-700 border border-indigo-100">
                          <IconComponent className="w-4 h-4" />
                        </div>
                        <h4 className="text-xs font-semibold text-slate-900">
                          {catGroup.category}
                        </h4>
                      </div>
                      <span className="text-[11px] font-mono text-slate-400 font-medium">
                        {skillItems.length}
                      </span>
                    </div>

                    <div className="flex flex-wrap gap-1.5">
                      {skillItems.map((skill) => (
                        <span
                          key={skill.name}
                          className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs bg-slate-50 text-slate-700 border border-slate-200 hover:bg-slate-100 transition-colors"
                        >
                          <span className="font-medium">{skill.name}</span>
                          <span className="font-mono text-[10px] text-indigo-700 bg-indigo-50 px-1 rounded border border-indigo-100 font-semibold">
                            {skill.repository_count}
                          </span>
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </Card>
  );
};

export default SkillCategoryGrid;
