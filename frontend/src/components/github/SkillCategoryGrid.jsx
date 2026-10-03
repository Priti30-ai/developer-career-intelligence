import React, { useState } from 'react';
import Card from '../common/Card';
import {
  Code,
  Layers,
  Cpu,
  Globe,
  Database,
  Cloud,
  Terminal,
  Info,
  FolderGit2,
  ChevronDown,
  ChevronUp,
  ShieldCheck,
  ShieldAlert,
  Shield,
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

const EVIDENCE_COLORS = {
  STRONG: 'text-emerald-700 bg-emerald-50 border-emerald-200',
  MODERATE: 'text-amber-700 bg-amber-50 border-amber-200',
  WEAK: 'text-slate-500 bg-slate-50 border-slate-200',
};

const EVIDENCE_ICONS = {
  STRONG: ShieldCheck,
  MODERATE: ShieldAlert,
  WEAK: Shield,
};

/**
 * SkillItem
 *
 * Individual skill badge with expandable supporting repository list.
 * No proficiency labels or subjective assessments.
 */
const SkillItem = ({ skill }) => {
  const [expanded, setExpanded] = useState(false);
  const hasRepos = skill.supporting_repositories?.length > 0;
  const EvidenceIcon = EVIDENCE_ICONS[skill.evidence_strength] || Shield;
  const evidenceColor = EVIDENCE_COLORS[skill.evidence_strength] || EVIDENCE_COLORS.WEAK;

  return (
    <div className="space-y-1">
      <button
        type="button"
        onClick={() => hasRepos && setExpanded((p) => !p)}
        className={`w-full text-left inline-flex items-center justify-between gap-1.5 px-2.5 py-1.5 rounded-md text-xs bg-slate-50 text-slate-700 border border-slate-200 transition-colors ${
          hasRepos ? 'hover:bg-slate-100 cursor-pointer' : 'cursor-default'
        } ${expanded ? 'bg-slate-100 border-slate-300' : ''}`}
        title={hasRepos ? 'Click to see supporting repositories' : undefined}
      >
        <div className="flex items-center gap-1.5 min-w-0">
          <span className="font-medium truncate">{skill.name}</span>
          <span className="font-mono text-[10px] text-indigo-700 bg-indigo-50 px-1 rounded border border-indigo-100 font-semibold flex-shrink-0">
            {skill.repository_count}
          </span>
          {skill.evidence_strength && (
            <span
              className={`inline-flex items-center gap-0.5 px-1 py-0.5 rounded text-[9px] font-semibold border flex-shrink-0 ${evidenceColor}`}
            >
              <EvidenceIcon className="w-2.5 h-2.5" />
              {skill.evidence_strength}
            </span>
          )}
        </div>
        {hasRepos && (
          <span className="text-slate-400 flex-shrink-0">
            {expanded ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
          </span>
        )}
      </button>

      {expanded && hasRepos && (
        <div className="ml-2 pl-2 border-l-2 border-indigo-100 space-y-1">
          <span className="text-[9px] text-indigo-600 uppercase tracking-wider font-semibold">
            Supporting repositories
          </span>
          <div className="flex flex-wrap gap-1">
            {skill.supporting_repositories.map((repoName) => (
              <span
                key={repoName}
                className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded bg-white border border-indigo-200 text-[10px] text-indigo-800 font-mono"
              >
                <FolderGit2 className="w-2.5 h-2.5 text-indigo-500" />
                {repoName}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

/**
 * SkillCategoryGrid
 *
 * Displays skills grouped by domain category.
 * Each skill badge shows the repository count and evidence strength.
 * Supporting repositories are expandable per skill.
 * No scoring, proficiency levels, or subjective assessments.
 */
export const SkillCategoryGrid = ({ skillsData }) => {
  const categories = skillsData?.categories || [];
  const totalUnique = skillsData?.total_unique_technologies ?? 0;

  // Fall back: if no categories but flat skills array exists, render flat list
  const flatSkills = skillsData?.skills || [];

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
            <strong>Evaluation Semantics:</strong> Each badge shows the number of analyzed public repositories in which the language or framework was identified, and the evidence strength (STRONG / MODERATE / WEAK).
            This reflects empirical code artifact frequency, not proven mastery or seniority.
            Click any badge to view the specific repositories where it was detected.
          </div>
        </div>

        {categories.length === 0 && flatSkills.length === 0 ? (
          <div className="text-center py-8 text-xs text-slate-400">
            No categorized skill data available for this profile.
          </div>
        ) : categories.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {categories.map((catGroup) => {
              const IconComponent = CATEGORY_ICONS[catGroup.category] || Layers;
              const skillItems = catGroup.skills || [];

              // Merge supporting_repositories from flat aggregated skills if available
              const aggregatedByName = {};
              if (skillsData?.skills) {
                skillsData.skills.forEach((s) => {
                  aggregatedByName[s.name] = s;
                });
              }

              const enrichedSkills = skillItems.map((skill) => ({
                ...skill,
                supporting_repositories:
                  skill.supporting_repositories ||
                  aggregatedByName[skill.name]?.supporting_repositories ||
                  [],
                evidence_strength:
                  skill.evidence_strength ||
                  aggregatedByName[skill.name]?.evidence_strength ||
                  null,
              }));

              return (
                <div
                  key={catGroup.category}
                  className="p-4 rounded-xl border border-slate-200 bg-white hover:border-slate-300 transition-colors flex flex-col"
                >
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

                  <div className="flex flex-col gap-1.5">
                    {enrichedSkills.map((skill) => (
                      <SkillItem key={skill.name} skill={skill} />
                    ))}
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          /* Flat skill list fallback (no categories from backend) */
          <div className="flex flex-wrap gap-2">
            {flatSkills.map((skill) => (
              <SkillItem key={skill.name} skill={skill} />
            ))}
          </div>
        )}
      </div>
    </Card>
  );
};

export default SkillCategoryGrid;
