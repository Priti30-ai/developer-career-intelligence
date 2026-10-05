import React, { useState } from 'react';
import Card from '../common/Card';
import StatusBadge from '../common/StatusBadge';
import {
  Sparkles,
  CheckCircle2,
  AlertCircle,
  Clock,
  Layers,
  GraduationCap,
  BookOpen,
  FolderGit2,
  Info,
  ChevronRight,
  ShieldCheck,
  Target,
  ArrowRight,
} from 'lucide-react';

export const CareerSkillBreakdown = ({ recommendation }) => {
  const [activeTab, setActiveTab] = useState('recommendations'); // 'recommendations' | 'strengths' | 'roadmap'

  if (!recommendation) return null;

  const {
    target_role,
    matched_skills = [],
    missing_skills = [],
    recommendations = [],
    roadmap = [],
    disclaimer,
  } = recommendation;

  // Filter recommendations by priority for quick metrics
  const highPriorityCount = recommendations.filter((r) => r.priority === 'HIGH').length;
  const mediumPriorityCount = recommendations.filter((r) => r.priority === 'MEDIUM').length;
  const lowPriorityCount = recommendations.filter((r) => r.priority === 'LOW').length;

  const getPriorityStyle = (priority) => {
    switch ((priority || '').toUpperCase()) {
      case 'HIGH':
        return {
          badgeStatus: 'danger',
          border: 'border-rose-200 bg-rose-50/20',
          headerBg: 'bg-rose-50 text-rose-800',
        };
      case 'MEDIUM':
        return {
          badgeStatus: 'warning',
          border: 'border-amber-200 bg-amber-50/20',
          headerBg: 'bg-amber-50 text-amber-800',
        };
      case 'LOW':
        return {
          badgeStatus: 'neutral',
          border: 'border-slate-200 bg-slate-50/30',
          headerBg: 'bg-slate-100 text-slate-700',
        };
      default:
        return {
          badgeStatus: 'info',
          border: 'border-slate-200',
          headerBg: 'bg-slate-50 text-slate-700',
        };
    }
  };

  const getDifficultyBadge = (diff) => {
    switch ((diff || '').toLowerCase()) {
      case 'beginner':
        return <span className="text-2xs px-2 py-0.5 rounded font-medium bg-emerald-100 text-emerald-800">Beginner</span>;
      case 'intermediate':
        return <span className="text-2xs px-2 py-0.5 rounded font-medium bg-sky-100 text-sky-800">Intermediate</span>;
      case 'advanced':
        return <span className="text-2xs px-2 py-0.5 rounded font-medium bg-purple-100 text-purple-800">Advanced</span>;
      default:
        return <span className="text-2xs px-2 py-0.5 rounded font-medium bg-slate-100 text-slate-700">{diff}</span>;
    }
  };

  return (
    <Card className="shadow-sm overflow-hidden">
      {/* Tab Navigation */}
      <div className="flex items-center justify-between border-b border-slate-200 px-6 pt-4 pb-0 flex-wrap gap-4 bg-slate-50/50 -mt-6 -mx-6 mb-6">
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={() => setActiveTab('recommendations')}
            className={`pb-3 text-xs font-semibold flex items-center gap-1.5 border-b-2 transition-colors ${
              activeTab === 'recommendations'
                ? 'border-indigo-600 text-indigo-600'
                : 'border-transparent text-slate-500 hover:text-slate-800'
            }`}
          >
            <Target className="w-3.5 h-3.5" />
            Prioritized Learning Guidance
            <span className="ml-1 px-1.5 py-0.2 rounded-full text-2xs bg-indigo-100 text-indigo-700 font-bold">
              {recommendations.length}
            </span>
          </button>

          <button
            type="button"
            onClick={() => setActiveTab('strengths')}
            className={`pb-3 text-xs font-semibold flex items-center gap-1.5 border-b-2 transition-colors ${
              activeTab === 'strengths'
                ? 'border-indigo-600 text-indigo-600'
                : 'border-transparent text-slate-500 hover:text-slate-800'
            }`}
          >
            <CheckCircle2 className="w-3.5 h-3.5" />
            Your Strengths
            <span className="ml-1 px-1.5 py-0.2 rounded-full text-2xs bg-emerald-100 text-emerald-800 font-bold">
              {matched_skills.length}
            </span>
          </button>

          <button
            type="button"
            onClick={() => setActiveTab('roadmap')}
            className={`pb-3 text-xs font-semibold flex items-center gap-1.5 border-b-2 transition-colors ${
              activeTab === 'roadmap'
                ? 'border-indigo-600 text-indigo-600'
                : 'border-transparent text-slate-500 hover:text-slate-800'
            }`}
          >
            <GraduationCap className="w-3.5 h-3.5" />
            Milestone Roadmap
            <span className="ml-1 px-1.5 py-0.2 rounded-full text-2xs bg-sky-100 text-sky-800 font-bold">
              {roadmap.length}
            </span>
          </button>
        </div>

        {/* Priority Counts Indicator */}
        {activeTab === 'recommendations' && (
          <div className="flex items-center gap-2 pb-3 text-2xs">
            {highPriorityCount > 0 && (
              <span className="px-2 py-0.5 rounded bg-rose-50 text-rose-700 font-semibold border border-rose-200">
                {highPriorityCount} High Priority
              </span>
            )}
            {mediumPriorityCount > 0 && (
              <span className="px-2 py-0.5 rounded bg-amber-50 text-amber-700 font-semibold border border-amber-200">
                {mediumPriorityCount} Medium
              </span>
            )}
            {lowPriorityCount > 0 && (
              <span className="px-2 py-0.5 rounded bg-slate-100 text-slate-700 font-semibold border border-slate-200">
                {lowPriorityCount} Low
              </span>
            )}
          </div>
        )}
      </div>

      {/* Tab 1: Prioritized Recommendations */}
      {activeTab === 'recommendations' && (
        <div className="space-y-4">
          {recommendations.length > 0 ? (
            recommendations.map((rec, idx) => {
              const priorityStyle = getPriorityStyle(rec.priority);

              return (
                <div
                  key={`${rec.skill}-${idx}`}
                  className={`p-4 rounded-xl border ${priorityStyle.border} transition-all`}
                >
                  {/* Top Bar: Skill Name, Priority, Difficulty */}
                  <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 pb-3 border-b border-slate-100">
                    <div className="flex items-center gap-2.5">
                      <span className="w-6 h-6 rounded-full bg-indigo-600 text-white text-xs font-bold flex items-center justify-center shrink-0">
                        {idx + 1}
                      </span>
                      <h4 className="text-base font-bold text-slate-900 tracking-tight">
                        {rec.skill}
                      </h4>
                      {getDifficultyBadge(rec.difficulty)}
                    </div>

                    <div className="flex items-center gap-2">
                      <StatusBadge
                        status={priorityStyle.badgeStatus}
                        text={`${rec.priority} PRIORITY`}
                      />
                    </div>
                  </div>

                  {/* Why this skill fits / Rationale */}
                  {rec.reason && (
                    <div className="mt-3 p-3 bg-white/80 rounded-lg border border-slate-200/80 text-xs">
                      <div className="font-semibold text-slate-700 mb-1 flex items-center gap-1.5">
                        <Sparkles className="w-3.5 h-3.5 text-indigo-600" />
                        Learning Rationale & Dependency Impact:
                      </div>
                      <p className="text-slate-600 leading-relaxed">{rec.reason}</p>
                    </div>
                  )}

                  {/* Prerequisites */}
                  {rec.prerequisites && rec.prerequisites.length > 0 && (
                    <div className="mt-3 flex items-center gap-2 flex-wrap text-xs">
                      <span className="font-medium text-slate-500 flex items-center gap-1">
                        <Clock className="w-3 h-3 text-slate-400" />
                        Prerequisites:
                      </span>
                      {rec.prerequisites.map((p) => (
                        <span
                          key={p}
                          className="px-2 py-0.5 rounded text-2xs font-medium bg-slate-100 text-slate-700 border border-slate-200"
                        >
                          {p}
                        </span>
                      ))}
                    </div>
                  )}

                  {/* Core Learning Topics */}
                  {rec.learning_topics && rec.learning_topics.length > 0 && (
                    <div className="mt-3">
                      <div className="text-2xs font-semibold uppercase tracking-wider text-slate-500 mb-1.5 flex items-center gap-1">
                        <BookOpen className="w-3 h-3 text-indigo-500" />
                        Core Conceptual & Practical Topics:
                      </div>
                      <div className="flex flex-wrap gap-1.5">
                        {rec.learning_topics.map((topic, tIdx) => (
                          <span
                            key={tIdx}
                            className="px-2.5 py-1 rounded-md text-xs bg-slate-50 text-slate-700 border border-slate-200 font-medium"
                          >
                            {topic}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Suggested Projects */}
                  {rec.suggested_projects && rec.suggested_projects.length > 0 && (
                    <div className="mt-3 pt-3 border-t border-slate-100">
                      <div className="text-2xs font-semibold uppercase tracking-wider text-slate-500 mb-1.5 flex items-center gap-1">
                        <FolderGit2 className="w-3 h-3 text-emerald-600" />
                        Recommended Portfolio Projects:
                      </div>
                      <ul className="space-y-1">
                        {rec.suggested_projects.map((proj, pIdx) => (
                          <li
                            key={pIdx}
                            className="text-xs text-slate-700 flex items-start gap-2 bg-emerald-50/40 p-2 rounded border border-emerald-100/70"
                          >
                            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 mt-1.5 shrink-0" />
                            <span>{proj}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              );
            })
          ) : (
            <div className="p-8 text-center bg-slate-50 rounded-xl border border-slate-200">
              <CheckCircle2 className="w-8 h-8 text-emerald-500 mx-auto mb-2" />
              <h4 className="text-sm font-bold text-slate-900">
                100% Skill Coverage Achieved!
              </h4>
              <p className="text-xs text-slate-500 mt-1 max-w-md mx-auto">
                Your current skills already satisfy all required competencies for {target_role}.
                No missing skill recommendations needed.
              </p>
            </div>
          )}
        </div>
      )}

      {/* Tab 2: Your Strengths */}
      {activeTab === 'strengths' && (
        <div className="space-y-4">
          <div className="p-3.5 bg-emerald-50 border border-emerald-200 rounded-lg text-xs text-emerald-800 flex items-start gap-2.5">
            <CheckCircle2 className="w-4 h-4 text-emerald-600 mt-0.5 shrink-0" />
            <div>
              <p className="font-semibold">Possessed Technical Competencies</p>
              <p className="mt-0.5 text-emerald-700">
                These are skills you already possess that directly match the {target_role} curriculum.
              </p>
            </div>
          </div>

          {matched_skills.length > 0 ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
              {matched_skills.map((skill) => (
                <div
                  key={skill}
                  className="p-3.5 rounded-lg bg-white border border-slate-200 shadow-2xs flex items-center justify-between"
                >
                  <div className="flex items-center gap-2">
                    <div className="w-6 h-6 rounded-full bg-emerald-100 flex items-center justify-center text-emerald-600 shrink-0">
                      <CheckCircle2 className="w-3.5 h-3.5" />
                    </div>
                    <span className="text-sm font-semibold text-slate-900">{skill}</span>
                  </div>
                  <span className="text-2xs font-medium px-2 py-0.5 rounded bg-emerald-50 text-emerald-700 border border-emerald-200">
                    Matched
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <div className="p-6 text-center bg-slate-50 rounded-lg border border-slate-200 text-xs text-slate-500">
              No overlapping skills detected for this role.
            </div>
          )}
        </div>
      )}

      {/* Tab 3: Milestone Roadmap Stages */}
      {activeTab === 'roadmap' && (
        <div className="space-y-6">
          <div className="p-3.5 bg-sky-50 border border-sky-200 rounded-lg text-xs text-sky-800 flex items-start gap-2.5">
            <GraduationCap className="w-4 h-4 text-sky-600 mt-0.5 shrink-0" />
            <div>
              <p className="font-semibold">Sequential Learning Progression</p>
              <p className="mt-0.5 text-sky-700">
                Roadmap stages are ordered topologically so prerequisites precede advanced specialization topics.
              </p>
            </div>
          </div>

          {roadmap.length > 0 ? (
            <div className="relative pl-6 space-y-6 before:absolute before:left-2.5 before:top-2 before:bottom-2 before:w-0.5 before:bg-indigo-100">
              {roadmap.map((stage) => (
                <div key={stage.stage_number} className="relative">
                  {/* Timeline Node */}
                  <div className="absolute -left-6 top-1 w-5 h-5 rounded-full bg-indigo-600 text-white text-2xs font-bold flex items-center justify-center ring-4 ring-white shadow-2xs">
                    {stage.stage_number}
                  </div>

                  <div className="p-5 rounded-xl bg-white border border-slate-200 shadow-sm space-y-3">
                    <div className="flex items-start justify-between gap-2 flex-wrap">
                      <h4 className="text-sm font-bold text-slate-900">
                        {stage.title}
                      </h4>
                      <span className="text-2xs font-semibold px-2 py-0.5 rounded-full bg-indigo-50 text-indigo-700 border border-indigo-200">
                        Stage {stage.stage_number}
                      </span>
                    </div>

                    <p className="text-xs text-slate-600 leading-relaxed">
                      {stage.objective}
                    </p>

                    {/* Skills in this stage */}
                    <div>
                      <span className="text-2xs font-semibold uppercase tracking-wider text-slate-400 block mb-1">
                        Skills Addressed:
                      </span>
                      <div className="flex flex-wrap gap-1.5">
                        {stage.skills.map((s) => (
                          <span
                            key={s}
                            className="px-2.5 py-1 rounded text-xs font-semibold bg-indigo-50 text-indigo-700 border border-indigo-200"
                          >
                            {s}
                          </span>
                        ))}
                      </div>
                    </div>

                    {/* Stage Recommended Projects */}
                    {stage.recommended_projects && stage.recommended_projects.length > 0 && (
                      <div className="pt-2 border-t border-slate-100">
                        <span className="text-2xs font-semibold uppercase tracking-wider text-slate-400 block mb-1">
                          Stage Projects:
                        </span>
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                          {stage.recommended_projects.map((proj, pIdx) => (
                            <div
                              key={pIdx}
                              className="text-xs text-slate-700 bg-slate-50 p-2 rounded border border-slate-200 flex items-center gap-2"
                            >
                              <FolderGit2 className="w-3.5 h-3.5 text-indigo-600 shrink-0" />
                              <span className="truncate">{proj}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="p-8 text-center bg-slate-50 rounded-xl border border-slate-200 text-xs text-slate-500">
              No roadmap stages required. Candidate has achieved complete skill coverage for {target_role}.
            </div>
          )}
        </div>
      )}

      {/* Official Disclaimer Banner */}
      {disclaimer && (
        <div className="mt-8 p-3.5 rounded-lg bg-slate-50 border border-slate-200 flex items-start gap-2.5 text-2xs text-slate-500">
          <Info className="w-4 h-4 text-slate-400 mt-0.5 shrink-0" />
          <p className="leading-relaxed">
            <strong className="text-slate-700">Notice:</strong> {disclaimer}
          </p>
        </div>
      )}
    </Card>
  );
};

export default CareerSkillBreakdown;
