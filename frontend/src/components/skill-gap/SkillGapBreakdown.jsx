import React, { useState } from 'react';
import Card from '../common/Card';
import {
  CheckCircle2,
  AlertCircle,
  Layers,
  Check,
  Minus,
  Sparkles,
  Award,
  BookOpen,
  Tag,
  Github,
  FileText,
} from 'lucide-react';

export const SkillGapBreakdown = ({
  matchedSkills = [],
  missingSkills = [],
  matchedSkillDetails = [],
  missingSkillDetails = [],
  targetRole = '',
}) => {
  const [activeTab, setActiveTab] = useState('missing'); // 'missing' | 'matched' | 'curriculum'

  // Build detail map lookup
  const matchedDetailMap = new Map();
  matchedSkillDetails.forEach((item) => {
    if (item && item.name) {
      matchedDetailMap.set(item.name.toLowerCase(), item);
    }
  });

  const missingDetailMap = new Map();
  missingSkillDetails.forEach((item) => {
    if (item && item.name) {
      missingDetailMap.set(item.name.toLowerCase(), item);
    }
  });

  const allRoleSkills = [...matchedSkills, ...missingSkills].sort((a, b) =>
    a.localeCompare(b)
  );

  const matchedSet = new Set(matchedSkills.map((s) => s.toLowerCase()));

  return (
    <Card
      title="Role Competency & Skill Gap Analysis"
      subtitle={`Detailed evaluation of prerequisites for ${targetRole || 'the selected role'}.`}
      action={
        <div className="flex items-center gap-1 p-1 bg-slate-100 rounded-lg text-xs font-medium">
          <button
            type="button"
            onClick={() => setActiveTab('missing')}
            className={`px-3 py-1.5 rounded-md transition-all flex items-center gap-1.5 ${
              activeTab === 'missing'
                ? 'bg-white text-rose-700 shadow-2xs font-semibold'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            <AlertCircle className="w-3.5 h-3.5 text-rose-600" />
            <span>Missing Gaps ({missingSkills.length})</span>
          </button>

          <button
            type="button"
            onClick={() => setActiveTab('matched')}
            className={`px-3 py-1.5 rounded-md transition-all flex items-center gap-1.5 ${
              activeTab === 'matched'
                ? 'bg-white text-emerald-700 shadow-2xs font-semibold'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
            <span>Possessed ({matchedSkills.length})</span>
          </button>

          <button
            type="button"
            onClick={() => setActiveTab('curriculum')}
            className={`px-3 py-1.5 rounded-md transition-all flex items-center gap-1.5 ${
              activeTab === 'curriculum'
                ? 'bg-white text-indigo-700 shadow-2xs font-semibold'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            <BookOpen className="w-3.5 h-3.5 text-indigo-600" />
            <span>All Requirements ({allRoleSkills.length})</span>
          </button>
        </div>
      }
    >
      {/* 1. MISSING SKILLS / GAPS TAB (PROMINENT BY DEFAULT) */}
      {activeTab === 'missing' && (
        <div className="space-y-4">
          <div className="flex items-center justify-between text-xs text-slate-500 pb-1 border-b border-slate-100 flex-wrap gap-2">
            <span>
              Target role expects <strong>{missingSkills.length}</strong> competencies not currently detected in your skill set.
            </span>
            <span className="text-[11px] text-rose-700 font-semibold bg-rose-50 px-2.5 py-0.5 rounded-full border border-rose-200">
              High-Value Upskilling Targets
            </span>
          </div>

          {missingSkills.length > 0 ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
              {missingSkills.map((skillName) => {
                const detail = missingDetailMap.get(skillName.toLowerCase());
                const categories = detail?.categories || [];

                return (
                  <div
                    key={skillName}
                    className="p-3.5 rounded-xl border border-rose-200/80 bg-gradient-to-br from-white to-rose-50/30 hover:border-rose-300 hover:shadow-xs transition-all flex flex-col justify-between space-y-3"
                  >
                    <div>
                      <div className="flex items-start justify-between gap-2">
                        <div className="flex items-center gap-2">
                          <div className="w-6 h-6 rounded-md bg-rose-100 text-rose-700 flex items-center justify-center flex-shrink-0">
                            <AlertCircle className="w-3.5 h-3.5" />
                          </div>
                          <span className="text-sm font-bold text-slate-900">
                            {skillName}
                          </span>
                        </div>

                        <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-rose-100 text-rose-800 border border-rose-200">
                          Gap
                        </span>
                      </div>

                      {/* Categories */}
                      {categories.length > 0 && (
                        <div className="flex flex-wrap gap-1 mt-2.5">
                          {categories.map((cat) => (
                            <span
                              key={cat}
                              className="px-2 py-0.5 rounded text-[10px] bg-slate-100 text-slate-600 border border-slate-200/60 font-medium"
                            >
                              {cat}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>

                    <div className="pt-2.5 border-t border-rose-100 text-[11px] text-rose-700/90 flex items-center justify-between">
                      <span>Required for {targetRole}</span>
                      <span className="font-semibold text-rose-800">Needs Study</span>
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <div className="p-8 text-center bg-emerald-50/40 rounded-xl border border-emerald-200">
              <CheckCircle2 className="w-8 h-8 text-emerald-600 mx-auto mb-2" />
              <p className="text-sm font-bold text-emerald-950">
                Zero Skill Gaps Detected!
              </p>
              <p className="text-xs text-emerald-700 mt-1 max-w-md mx-auto">
                You possess 100% of the prerequisite skills required for the <strong>{targetRole}</strong> role.
              </p>
            </div>
          )}
        </div>
      )}

      {/* 2. MATCHED / POSSESSED SKILLS TAB */}
      {activeTab === 'matched' && (
        <div className="space-y-4">
          <div className="flex items-center justify-between text-xs text-slate-500 pb-1 border-b border-slate-100 flex-wrap gap-2">
            <span>
              You possess <strong>{matchedSkills.length}</strong> of the required competencies for this role.
            </span>
            <span className="text-[11px] text-emerald-700 font-semibold bg-emerald-50 px-2.5 py-0.5 rounded-full border border-emerald-200">
              Verified Prerequisites
            </span>
          </div>

          {matchedSkills.length > 0 ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
              {matchedSkills.map((skillName) => {
                const detail = matchedDetailMap.get(skillName.toLowerCase());
                const categories = detail?.categories || [];
                const sources = detail?.sources || [];
                const evidenceStatus = detail?.evidence_status;
                const repos = detail?.supporting_repositories || [];

                return (
                  <div
                    key={skillName}
                    className="p-3.5 rounded-xl border border-emerald-200/80 bg-gradient-to-br from-white to-emerald-50/30 hover:border-emerald-300 hover:shadow-xs transition-all flex flex-col justify-between space-y-3"
                  >
                    <div>
                      <div className="flex items-start justify-between gap-2">
                        <div className="flex items-center gap-2">
                          <div className="w-6 h-6 rounded-md bg-emerald-100 text-emerald-700 flex items-center justify-center flex-shrink-0">
                            <Check className="w-3.5 h-3.5" />
                          </div>
                          <span className="text-sm font-bold text-slate-900">
                            {skillName}
                          </span>
                        </div>

                        {evidenceStatus && (
                          <span
                            className={`px-1.5 py-0.5 rounded text-[10px] font-semibold uppercase tracking-wider ${
                              evidenceStatus === 'STRONG'
                                ? 'bg-emerald-100 text-emerald-800'
                                : evidenceStatus === 'MODERATE'
                                ? 'bg-indigo-100 text-indigo-800'
                                : 'bg-slate-100 text-slate-600'
                            }`}
                          >
                            {evidenceStatus}
                          </span>
                        )}
                      </div>

                      {/* Categories */}
                      {categories.length > 0 && (
                        <div className="flex flex-wrap gap-1 mt-2.5">
                          {categories.map((cat) => (
                            <span
                              key={cat}
                              className="px-2 py-0.5 rounded text-[10px] bg-slate-100 text-slate-600 border border-slate-200/60 font-medium"
                            >
                              {cat}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>

                    {/* Sources & Repos provenance */}
                    {(sources.length > 0 || repos.length > 0) && (
                      <div className="pt-2.5 border-t border-emerald-100/70 flex items-center justify-between text-[11px] text-slate-500">
                        {sources.length > 0 && (
                          <div className="flex items-center gap-1.5">
                            {sources.includes('github') && (
                              <span className="inline-flex items-center gap-0.5 text-slate-600">
                                <Github className="w-3 h-3" />
                                <span>GitHub</span>
                              </span>
                            )}
                            {sources.includes('resume') && (
                              <span className="inline-flex items-center gap-0.5 text-slate-600">
                                <FileText className="w-3 h-3" />
                                <span>Resume</span>
                              </span>
                            )}
                          </div>
                        )}

                        {repos.length > 0 && (
                          <span className="text-[10px] text-indigo-700 bg-indigo-50 px-1.5 py-0.5 rounded font-mono">
                            {repos.length} {repos.length === 1 ? 'repo' : 'repos'}
                          </span>
                        )}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          ) : (
            <div className="p-8 text-center bg-slate-50 rounded-xl border border-slate-200">
              <p className="text-xs text-slate-500">
                None of your currently entered skills match the prerequisites for this role.
              </p>
            </div>
          )}
        </div>
      )}

      {/* 3. ALL ROLE REQUIREMENTS TAB */}
      {activeTab === 'curriculum' && (
        <div className="space-y-4">
          <div className="flex items-center justify-between text-xs text-slate-500 pb-1 border-b border-slate-100 flex-wrap gap-2">
            <span>
              Complete curriculum of <strong>{allRoleSkills.length}</strong> required skills for <strong>{targetRole}</strong>.
            </span>
            <div className="flex items-center gap-3 text-[11px]">
              <span className="inline-flex items-center gap-1 text-emerald-700 font-medium">
                <span className="w-2 h-2 rounded-full bg-emerald-500" />
                Possessed ({matchedSkills.length})
              </span>
              <span className="inline-flex items-center gap-1 text-rose-700 font-medium">
                <span className="w-2 h-2 rounded-full bg-rose-500" />
                Missing ({missingSkills.length})
              </span>
            </div>
          </div>

          <div className="flex flex-wrap gap-2">
            {allRoleSkills.map((skill) => {
              const isMatched = matchedSet.has(skill.toLowerCase());
              return (
                <span
                  key={skill}
                  className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium border ${
                    isMatched
                      ? 'bg-emerald-50 text-emerald-800 border-emerald-200 shadow-2xs'
                      : 'bg-rose-50/70 text-rose-800 border-rose-200'
                  }`}
                >
                  {isMatched ? (
                    <Check className="w-3.5 h-3.5 text-emerald-600" />
                  ) : (
                    <Minus className="w-3.5 h-3.5 text-rose-500" />
                  )}
                  <span className="font-semibold">{skill}</span>
                  <span
                    className={`text-[10px] px-1 py-0.2 rounded font-normal ${
                      isMatched ? 'bg-emerald-100 text-emerald-800' : 'bg-rose-100 text-rose-800'
                    }`}
                  >
                    {isMatched ? 'Possessed' : 'Missing'}
                  </span>
                </span>
              );
            })}
          </div>
        </div>
      )}
    </Card>
  );
};

export default SkillGapBreakdown;
