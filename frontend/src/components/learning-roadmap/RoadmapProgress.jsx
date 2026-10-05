import React from 'react';
import Card from '../common/Card';
import StatusBadge from '../common/StatusBadge';
import {
  Target,
  CheckCircle2,
  AlertCircle,
  Briefcase,
  Layers,
  GraduationCap,
  TrendingUp,
  Tag,
  ShieldCheck,
} from 'lucide-react';

export const RoadmapProgress = ({ data }) => {
  if (!data) return null;

  const {
    target_role,
    role_slug,
    skill_match_percentage,
    match_percentage,
    total_required_skills,
    total_matched_skills,
    total_missing_skills,
    current_skills = [],
    matched_skills = [],
    missing_skills = [],
    roadmap = [],
  } = data;

  const coverage =
    typeof skill_match_percentage === 'number'
      ? skill_match_percentage
      : match_percentage || 0;

  const getTheme = (pct) => {
    if (pct >= 75) {
      return {
        badgeStatus: 'success',
        badgeText: 'Advanced Readiness',
        textColor: 'text-emerald-700',
        barColor: 'bg-emerald-500',
      };
    }
    if (pct >= 50) {
      return {
        badgeStatus: 'info',
        badgeText: 'Intermediate Readiness',
        textColor: 'text-sky-700',
        barColor: 'bg-sky-500',
      };
    }
    if (pct >= 25) {
      return {
        badgeStatus: 'warning',
        badgeText: 'Developing Readiness',
        textColor: 'text-amber-700',
        barColor: 'bg-amber-500',
      };
    }
    return {
      badgeStatus: 'neutral',
      badgeText: 'Foundational Baseline',
      textColor: 'text-slate-700',
      barColor: 'bg-indigo-500',
    };
  };

  const theme = getTheme(coverage);

  return (
    <div className="space-y-6 mb-6">
      {/* 5 Summary Metrics Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3.5">
        <div className="p-4 bg-white rounded-xl border border-slate-200 shadow-2xs flex flex-col justify-between">
          <div className="flex items-center justify-between text-xs text-slate-500 mb-1">
            <span>Target Role</span>
            <Briefcase className="w-3.5 h-3.5 text-indigo-600" />
          </div>
          <div className="text-sm font-bold text-slate-900 truncate" title={target_role}>
            {target_role}
          </div>
          <div className="text-2xs text-slate-400 mt-1 font-mono">
            {role_slug}
          </div>
        </div>

        <div className="p-4 bg-white rounded-xl border border-slate-200 shadow-2xs flex flex-col justify-between">
          <div className="flex items-center justify-between text-xs text-slate-500 mb-1">
            <span>Input Skills</span>
            <Tag className="w-3.5 h-3.5 text-slate-400" />
          </div>
          <div className="text-xl font-extrabold text-slate-900">
            {current_skills.length}
          </div>
          <div className="text-2xs text-slate-400 mt-1">Profile baseline</div>
        </div>

        <div className="p-4 bg-emerald-50/50 rounded-xl border border-emerald-100 shadow-2xs flex flex-col justify-between">
          <div className="flex items-center justify-between text-xs text-emerald-700 mb-1">
            <span>Skills Matched</span>
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
          </div>
          <div className="text-xl font-extrabold text-emerald-900">
            {total_matched_skills}
          </div>
          <div className="text-2xs text-emerald-600 mt-1">Strengths verified</div>
        </div>

        <div className="p-4 bg-amber-50/50 rounded-xl border border-amber-100 shadow-2xs flex flex-col justify-between">
          <div className="flex items-center justify-between text-xs text-amber-700 mb-1">
            <span>Skills to Learn</span>
            <AlertCircle className="w-3.5 h-3.5 text-amber-600" />
          </div>
          <div className="text-xl font-extrabold text-amber-900">
            {total_missing_skills}
          </div>
          <div className="text-2xs text-amber-600 mt-1">Addressed in roadmap</div>
        </div>

        <div className="p-4 bg-indigo-50/50 rounded-xl border border-indigo-100 shadow-2xs flex flex-col justify-between col-span-2 sm:col-span-1">
          <div className="flex items-center justify-between text-xs text-indigo-700 mb-1">
            <span>Curriculum Match</span>
            <GraduationCap className="w-3.5 h-3.5 text-indigo-600" />
          </div>
          <div className="flex items-baseline gap-1">
            <span className="text-xl font-extrabold text-indigo-900">{coverage}</span>
            <span className="text-xs font-bold text-indigo-600">%</span>
          </div>
          <div className="text-2xs text-indigo-600/80 mt-1">
            {total_matched_skills} of {total_required_skills} required
          </div>
        </div>
      </div>

      {/* Recommended Progression Analytical Progress Bar */}
      <Card className="shadow-2xs">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 mb-3">
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-sm font-bold text-slate-900">Recommended Progression</h3>
              <StatusBadge status={theme.badgeStatus} text={theme.badgeText} />
            </div>
            <p className="text-xs text-slate-500 mt-0.5">
              Analytical representation of curriculum coverage. Does not represent completed or tracked stages.
            </p>
          </div>

          <div className="text-right shrink-0">
            <span className="text-lg font-extrabold text-slate-900">{coverage}%</span>
            <span className="text-xs text-slate-400 block -mt-0.5">Role Coverage</span>
          </div>
        </div>

        <div className="h-3 w-full bg-slate-100 rounded-full overflow-hidden border border-slate-200">
          <div
            className={`h-full rounded-full transition-all duration-700 ${theme.barColor}`}
            style={{ width: `${Math.min(100, Math.max(0, coverage))}%` }}
          />
        </div>

        {/* Skills Division: Possessed vs Target Gaps */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6 pt-5 border-t border-slate-100">
          {/* Matched Foundations */}
          <div>
            <span className="text-2xs font-semibold uppercase tracking-wider text-emerald-700 block mb-2 flex items-center gap-1.5">
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
              Existing Foundations ({matched_skills.length})
            </span>
            {matched_skills.length > 0 ? (
              <div className="flex flex-wrap gap-1.5">
                {matched_skills.map((skill) => (
                  <span
                    key={skill}
                    className="px-2.5 py-1 rounded-md text-xs font-medium bg-emerald-50 text-emerald-800 border border-emerald-200"
                  >
                    ✓ {skill}
                  </span>
                ))}
              </div>
            ) : (
              <p className="text-xs text-slate-400 italic">
                No overlapping skills detected. All role requirements will be introduced in the roadmap.
              </p>
            )}
          </div>

          {/* Missing Skills to Learn */}
          <div>
            <span className="text-2xs font-semibold uppercase tracking-wider text-amber-700 block mb-2 flex items-center gap-1.5">
              <AlertCircle className="w-3.5 h-3.5 text-amber-600" />
              Gaps Addressed in Roadmap ({missing_skills.length})
            </span>
            {missing_skills.length > 0 ? (
              <div className="flex flex-wrap gap-1.5">
                {missing_skills.map((skill) => (
                  <span
                    key={skill}
                    className="px-2.5 py-1 rounded-md text-xs font-medium bg-amber-50 text-amber-800 border border-amber-200"
                  >
                    {skill}
                  </span>
                ))}
              </div>
            ) : (
              <p className="text-xs text-slate-400 italic">
                All required skills for this role are already covered!
              </p>
            )}
          </div>
        </div>
      </Card>
    </div>
  );
};

export default RoadmapProgress;
