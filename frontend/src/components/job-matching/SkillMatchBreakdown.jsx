import React, { useState } from 'react';
import Card from '../common/Card';
import {
  CheckCircle2,
  AlertCircle,
  FileSearch,
  Tag,
  FolderGit2,
  FileText,
  Github,
  Check,
  Minus,
  Sparkles,
  ExternalLink,
} from 'lucide-react';

export const SkillMatchBreakdown = ({
  matchedSkills = [],
  missingSkills = [],
  extractedSkills = [],
  matchedSkillDetails = [],
  missingSkillDetails = [],
}) => {
  const [activeTab, setActiveTab] = useState('matched'); // 'matched' | 'missing' | 'all'

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

  const matchedSet = new Set(matchedSkills.map((s) => s.toLowerCase()));

  return (
    <Card
      title="Skill Alignment Breakdown"
      subtitle="Detailed inspection of matched developer competencies, missing requirements, and all detected posting skills."
      action={
        <div className="flex items-center gap-1 p-1 bg-slate-100 rounded-lg text-xs font-medium">
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
            <span>Matched ({matchedSkills.length})</span>
          </button>

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
            <span>Skill Gaps ({missingSkills.length})</span>
          </button>

          <button
            type="button"
            onClick={() => setActiveTab('all')}
            className={`px-3 py-1.5 rounded-md transition-all flex items-center gap-1.5 ${
              activeTab === 'all'
                ? 'bg-white text-indigo-700 shadow-2xs font-semibold'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            <FileSearch className="w-3.5 h-3.5 text-indigo-600" />
            <span>All Extracted ({extractedSkills.length})</span>
          </button>
        </div>
      }
    >
      {/* 1. MATCHED SKILLS TAB */}
      {activeTab === 'matched' && (
        <div className="space-y-4">
          <div className="flex items-center justify-between text-xs text-slate-500 pb-1 border-b border-slate-100">
            <span>
              The candidate possesses <strong>{matchedSkills.length}</strong> of the required technical skills.
            </span>
            <span className="text-[11px] text-emerald-700 font-medium bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-200">
              Verified in candidate profile
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
                    className="p-3 rounded-lg border border-emerald-100 bg-emerald-50/20 hover:bg-emerald-50/40 transition-colors flex flex-col justify-between space-y-2.5"
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
                        <div className="flex flex-wrap gap-1 mt-2">
                          {categories.map((cat) => (
                            <span
                              key={cat}
                              className="px-1.5 py-0.5 rounded text-[10px] bg-slate-100 text-slate-600 border border-slate-200/60"
                            >
                              {cat}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>

                    {/* Sources & Supporting Repos */}
                    {(sources.length > 0 || repos.length > 0) && (
                      <div className="pt-2 border-t border-emerald-100/60 flex items-center justify-between text-[11px] text-slate-500">
                        {sources.length > 0 && (
                          <div className="flex items-center gap-1.5">
                            {sources.includes('github') && (
                              <span className="inline-flex items-center gap-0.5 text-slate-600" title="Found in GitHub">
                                <Github className="w-3 h-3" />
                                <span>GitHub</span>
                              </span>
                            )}
                            {sources.includes('resume') && (
                              <span className="inline-flex items-center gap-0.5 text-slate-600" title="Found in Resume">
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
            <div className="p-8 text-center bg-slate-50 rounded-lg border border-slate-200">
              <p className="text-xs text-slate-500">
                No matching skills found between the candidate profile and this job description.
              </p>
            </div>
          )}
        </div>
      )}

      {/* 2. MISSING SKILLS TAB */}
      {activeTab === 'missing' && (
        <div className="space-y-4">
          <div className="flex items-center justify-between text-xs text-slate-500 pb-1 border-b border-slate-100">
            <span>
              The job posting specifies <strong>{missingSkills.length}</strong> technical skills not detected in candidate profile.
            </span>
            <span className="text-[11px] text-rose-700 font-medium bg-rose-50 px-2 py-0.5 rounded-full border border-rose-200">
              Candidate Skill Gaps
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
                    className="p-3 rounded-lg border border-rose-100 bg-rose-50/20 hover:bg-rose-50/40 transition-colors flex flex-col justify-between space-y-2.5"
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

                        <span className="px-1.5 py-0.5 rounded text-[10px] font-semibold bg-rose-100 text-rose-800">
                          Gap
                        </span>
                      </div>

                      {categories.length > 0 && (
                        <div className="flex flex-wrap gap-1 mt-2">
                          {categories.map((cat) => (
                            <span
                              key={cat}
                              className="px-1.5 py-0.5 rounded text-[10px] bg-slate-100 text-slate-600 border border-slate-200/60"
                            >
                              {cat}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>

                    <div className="pt-2 border-t border-rose-100/60 text-[11px] text-rose-700">
                      Required by posting; not found in skills list.
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <div className="p-8 text-center bg-emerald-50/40 rounded-lg border border-emerald-200">
              <CheckCircle2 className="w-8 h-8 text-emerald-600 mx-auto mb-2" />
              <p className="text-sm font-bold text-emerald-950">
                Zero Skill Gaps!
              </p>
              <p className="text-xs text-emerald-700 mt-1">
                The candidate profile possesses 100% of the technical requirements extracted from this job posting.
              </p>
            </div>
          )}
        </div>
      )}

      {/* 3. ALL EXTRACTED SKILLS TAB */}
      {activeTab === 'all' && (
        <div className="space-y-4">
          <div className="flex items-center justify-between text-xs text-slate-500 pb-1 border-b border-slate-100">
            <span>
              All <strong>{extractedSkills.length}</strong> technical skills extracted deterministically from the job description.
            </span>
            <div className="flex items-center gap-3 text-[11px]">
              <span className="inline-flex items-center gap-1 text-emerald-700 font-medium">
                <span className="w-2 h-2 rounded-full bg-emerald-500" />
                Matched ({matchedSkills.length})
              </span>
              <span className="inline-flex items-center gap-1 text-rose-700 font-medium">
                <span className="w-2 h-2 rounded-full bg-rose-500" />
                Missing ({missingSkills.length})
              </span>
            </div>
          </div>

          <div className="flex flex-wrap gap-2">
            {extractedSkills.map((skill) => {
              const isMatched = matchedSet.has(skill.toLowerCase());
              return (
                <span
                  key={skill}
                  className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium border ${
                    isMatched
                      ? 'bg-emerald-50 text-emerald-800 border-emerald-200 shadow-2xs'
                      : 'bg-slate-50 text-slate-700 border-slate-200'
                  }`}
                >
                  {isMatched ? (
                    <Check className="w-3.5 h-3.5 text-emerald-600" />
                  ) : (
                    <Minus className="w-3.5 h-3.5 text-slate-400" />
                  )}
                  <span className="font-semibold">{skill}</span>
                  <span
                    className={`text-[10px] px-1 py-0.2 rounded font-normal ${
                      isMatched ? 'bg-emerald-100/70 text-emerald-800' : 'bg-slate-200/70 text-slate-600'
                    }`}
                  >
                    {isMatched ? 'Matched' : 'Missing'}
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

export default SkillMatchBreakdown;
