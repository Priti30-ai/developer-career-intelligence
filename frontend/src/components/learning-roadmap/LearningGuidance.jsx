import React, { useState } from 'react';
import Card from '../common/Card';
import StatusBadge from '../common/StatusBadge';
import {
  BookOpen,
  Sparkles,
  Clock,
  FolderGit2,
  AlertTriangle,
  Layers,
  ChevronDown,
  ChevronUp,
  Tag,
  CheckCircle2,
  Compass,
} from 'lucide-react';

export const LearningGuidance = ({ recommendations = [], targetRole = '' }) => {
  const [priorityFilter, setPriorityFilter] = useState('ALL');
  const [expandedSkill, setExpandedSkill] = useState(null);

  if (!recommendations || recommendations.length === 0) {
    return null;
  }

  const highPriority = recommendations.filter((r) => r.priority === 'HIGH');
  const mediumPriority = recommendations.filter((r) => r.priority === 'MEDIUM');
  const lowPriority = recommendations.filter((r) => r.priority === 'LOW');

  const filteredRecommendations =
    priorityFilter === 'ALL'
      ? recommendations
      : recommendations.filter((r) => r.priority === priorityFilter);

  const getPriorityStyle = (priority) => {
    switch ((priority || '').toUpperCase()) {
      case 'HIGH':
        return {
          status: 'danger',
          border: 'border-rose-200 bg-rose-50/20',
          badgeText: 'HIGH PRIORITY',
          badgeClass: 'bg-rose-50 text-rose-700 border-rose-200',
          iconColor: 'text-rose-600',
        };
      case 'MEDIUM':
        return {
          status: 'warning',
          border: 'border-amber-200 bg-amber-50/20',
          badgeText: 'MEDIUM PRIORITY',
          badgeClass: 'bg-amber-50 text-amber-700 border-amber-200',
          iconColor: 'text-amber-600',
        };
      case 'LOW':
        return {
          status: 'neutral',
          border: 'border-slate-200 bg-slate-50/30',
          badgeText: 'LOW PRIORITY',
          badgeClass: 'bg-slate-100 text-slate-700 border-slate-200',
          iconColor: 'text-slate-600',
        };
      default:
        return {
          status: 'info',
          border: 'border-slate-200',
          badgeText: priority,
          badgeClass: 'bg-slate-100 text-slate-700 border-slate-200',
          iconColor: 'text-slate-600',
        };
    }
  };

  const getDifficultyBadge = (difficulty) => {
    switch ((difficulty || '').toLowerCase()) {
      case 'beginner':
        return <span className="text-2xs font-semibold px-2 py-0.5 rounded bg-emerald-100 text-emerald-800">Beginner</span>;
      case 'intermediate':
        return <span className="text-2xs font-semibold px-2 py-0.5 rounded bg-sky-100 text-sky-800">Intermediate</span>;
      case 'advanced':
        return <span className="text-2xs font-semibold px-2 py-0.5 rounded bg-purple-100 text-purple-800">Advanced</span>;
      default:
        return <span className="text-2xs font-semibold px-2 py-0.5 rounded bg-slate-100 text-slate-700">{difficulty}</span>;
    }
  };

  return (
    <Card
      title="Prioritized Skill Learning Guidance"
      subtitle={`Detailed curriculum guidance for closing each missing skill required by ${targetRole}.`}
      className="shadow-sm mb-6"
    >
      {/* Priority Filter Bar */}
      <div className="flex items-center justify-between pb-4 mb-4 border-b border-slate-100 flex-wrap gap-2">
        <div className="flex items-center gap-1.5 flex-wrap">
          <button
            type="button"
            onClick={() => setPriorityFilter('ALL')}
            className={`px-3 py-1 rounded-md text-xs font-semibold transition-colors ${
              priorityFilter === 'ALL'
                ? 'bg-indigo-600 text-white shadow-2xs'
                : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
            }`}
          >
            All Skills ({recommendations.length})
          </button>
          <button
            type="button"
            onClick={() => setPriorityFilter('HIGH')}
            className={`px-3 py-1 rounded-md text-xs font-semibold transition-colors ${
              priorityFilter === 'HIGH'
                ? 'bg-rose-600 text-white shadow-2xs'
                : 'bg-rose-50 text-rose-700 hover:bg-rose-100'
            }`}
          >
            High Priority ({highPriority.length})
          </button>
          <button
            type="button"
            onClick={() => setPriorityFilter('MEDIUM')}
            className={`px-3 py-1 rounded-md text-xs font-semibold transition-colors ${
              priorityFilter === 'MEDIUM'
                ? 'bg-amber-600 text-white shadow-2xs'
                : 'bg-amber-50 text-amber-700 hover:bg-amber-100'
            }`}
          >
            Medium Priority ({mediumPriority.length})
          </button>
          <button
            type="button"
            onClick={() => setPriorityFilter('LOW')}
            className={`px-3 py-1 rounded-md text-xs font-semibold transition-colors ${
              priorityFilter === 'LOW'
                ? 'bg-slate-700 text-white shadow-2xs'
                : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
            }`}
          >
            Low Priority ({lowPriority.length})
          </button>
        </div>

        <span className="text-2xs text-slate-400">
          Showing {filteredRecommendations.length} of {recommendations.length} recommendations
        </span>
      </div>

      {/* Recommendations Cards Grid */}
      <div className="space-y-4">
        {filteredRecommendations.map((rec, idx) => {
          const style = getPriorityStyle(rec.priority);
          const isExpanded = expandedSkill === rec.skill;

          return (
            <div
              key={`${rec.skill}-${idx}`}
              className={`p-4 sm:p-5 rounded-xl border ${style.border} transition-all`}
            >
              {/* Header: Skill, Priority, Difficulty */}
              <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 pb-3 border-b border-slate-100">
                <div className="flex items-center gap-2.5">
                  <div className="w-7 h-7 rounded-lg bg-indigo-600 text-white text-xs font-bold flex items-center justify-center shrink-0">
                    {idx + 1}
                  </div>
                  <div>
                    <h4 className="text-base font-bold text-slate-900 tracking-tight">
                      {rec.skill}
                    </h4>
                  </div>
                  {getDifficultyBadge(rec.difficulty)}
                </div>

                <div className="flex items-center gap-2">
                  <span
                    className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-bold border ${style.badgeClass}`}
                  >
                    <span className="w-1.5 h-1.5 rounded-full bg-current" />
                    {style.badgeText}
                  </span>
                </div>
              </div>

              {/* Rationale / Reason */}
              {rec.reason && (
                <div className="mt-3 p-3 bg-white/90 rounded-lg border border-slate-200 text-xs">
                  <div className="font-semibold text-slate-700 mb-1 flex items-center gap-1.5">
                    <Sparkles className="w-3.5 h-3.5 text-indigo-600 shrink-0" />
                    Learning Rationale & Dependency Sequencing:
                  </div>
                  <p className="text-slate-600 leading-relaxed">{rec.reason}</p>
                </div>
              )}

              {/* Prerequisites */}
              {rec.prerequisites && rec.prerequisites.length > 0 && (
                <div className="mt-3 flex items-center gap-2 flex-wrap text-xs">
                  <span className="font-medium text-slate-500 flex items-center gap-1">
                    <Clock className="w-3.5 h-3.5 text-slate-400" />
                    Prerequisites:
                  </span>
                  {rec.prerequisites.map((p) => (
                    <span
                      key={p}
                      className="px-2 py-0.5 rounded text-2xs font-semibold bg-slate-100 text-slate-700 border border-slate-200"
                    >
                      {p}
                    </span>
                  ))}
                </div>
              )}

              {/* Learning Topics */}
              {rec.learning_topics && rec.learning_topics.length > 0 && (
                <div className="mt-3">
                  <span className="text-2xs font-semibold uppercase tracking-wider text-slate-500 mb-1.5 flex items-center gap-1">
                    <BookOpen className="w-3.5 h-3.5 text-indigo-500" />
                    Core Conceptual & Practical Learning Topics:
                  </span>
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
                  <span className="text-2xs font-semibold uppercase tracking-wider text-slate-500 mb-1.5 flex items-center gap-1">
                    <FolderGit2 className="w-3.5 h-3.5 text-emerald-600" />
                    Suggested Hands-On Portfolio Projects:
                  </span>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                    {rec.suggested_projects.map((proj, pIdx) => (
                      <div
                        key={pIdx}
                        className="text-xs text-slate-700 bg-emerald-50/40 p-2.5 rounded-lg border border-emerald-100 flex items-start gap-2"
                      >
                        <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 mt-1.5 shrink-0" />
                        <span className="font-medium">{proj}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </Card>
  );
};

export default LearningGuidance;
