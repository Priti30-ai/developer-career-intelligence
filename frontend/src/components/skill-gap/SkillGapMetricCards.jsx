import React from 'react';
import Card from '../common/Card';
import {
  Percent,
  Target,
  CheckCircle2,
  AlertCircle,
  Briefcase,
  Compass,
} from 'lucide-react';

export const SkillGapMetricCards = ({
  skillMatchPercentage = 0,
  targetRole = '',
  totalRequiredSkills = 0,
  totalMatchedSkills = 0,
  totalMissingSkills = 0,
}) => {
  // Determine score color and status
  const getCoverageTheme = (pct) => {
    if (pct >= 75) {
      return {
        badgeBg: 'bg-emerald-50 text-emerald-700 border-emerald-200',
        barBg: 'bg-emerald-500',
        statusText: 'Strong Alignment',
        textColor: 'text-emerald-700',
      };
    }
    if (pct >= 50) {
      return {
        badgeBg: 'bg-amber-50 text-amber-700 border-amber-200',
        barBg: 'bg-amber-500',
        statusText: 'Moderate Alignment',
        textColor: 'text-amber-700',
      };
    }
    return {
      badgeBg: 'bg-rose-50 text-rose-700 border-rose-200',
      barBg: 'bg-rose-500',
      statusText: 'Significant Gap',
      textColor: 'text-rose-700',
    };
  };

  const theme = getCoverageTheme(skillMatchPercentage);

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {/* 1. Skill Coverage Card */}
      <Card className="relative overflow-hidden border-indigo-200/80 bg-gradient-to-br from-white to-indigo-50/30">
        <div className="flex items-start justify-between">
          <div>
            <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-500 block">
              Skill Coverage
            </span>
            <div className="mt-1 flex items-baseline gap-1.5">
              <span className={`text-3xl font-extrabold tracking-tight ${theme.textColor}`}>
                {skillMatchPercentage}%
              </span>
            </div>
          </div>
          <span
            className={`px-2 py-0.5 rounded-full text-[11px] font-semibold border ${theme.badgeBg}`}
          >
            {theme.statusText}
          </span>
        </div>

        {/* Progress bar */}
        <div className="mt-3 w-full bg-slate-100 rounded-full h-1.5 overflow-hidden">
          <div
            className={`h-full rounded-full transition-all duration-500 ${theme.barBg}`}
            style={{ width: `${Math.min(100, Math.max(0, skillMatchPercentage))}%` }}
          />
        </div>

        <p className="mt-2 text-[11px] text-slate-500">
          {totalMatchedSkills} of {totalRequiredSkills} prerequisites satisfied
        </p>
      </Card>

      {/* 2. Target Role */}
      <Card>
        <div className="flex items-start justify-between">
          <div className="min-w-0 flex-1 mr-2">
            <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-500 block">
              Target Role
            </span>
            <div className="mt-1">
              <h4 className="text-base sm:text-lg font-bold text-slate-900 tracking-tight truncate" title={targetRole}>
                {targetRole || 'Not Selected'}
              </h4>
            </div>
          </div>
          <div className="w-9 h-9 rounded-lg bg-indigo-50 text-indigo-600 flex items-center justify-center flex-shrink-0">
            <Briefcase className="w-5 h-5" />
          </div>
        </div>
        <p className="mt-2.5 text-[11px] text-slate-500">
          {totalRequiredSkills} core required competencies
        </p>
      </Card>

      {/* 3. Matched Skills */}
      <Card>
        <div className="flex items-start justify-between">
          <div>
            <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-500 block">
              Possessed Skills
            </span>
            <div className="mt-1 flex items-baseline gap-1">
              <span className="text-3xl font-extrabold text-emerald-600 tracking-tight">
                {totalMatchedSkills}
              </span>
              <span className="text-xs text-emerald-600/70 font-medium">skills</span>
            </div>
          </div>
          <div className="w-9 h-9 rounded-lg bg-emerald-50 text-emerald-600 flex items-center justify-center">
            <CheckCircle2 className="w-5 h-5" />
          </div>
        </div>
        <p className="mt-2.5 text-[11px] text-slate-500">
          Prerequisites met by developer
        </p>
      </Card>

      {/* 4. Missing Skills */}
      <Card>
        <div className="flex items-start justify-between">
          <div>
            <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-500 block">
              Skill Gaps
            </span>
            <div className="mt-1 flex items-baseline gap-1">
              <span className={`text-3xl font-extrabold tracking-tight ${
                totalMissingSkills > 0 ? 'text-rose-600' : 'text-slate-400'
              }`}>
                {totalMissingSkills}
              </span>
              <span className="text-xs text-slate-400 font-medium">missing</span>
            </div>
          </div>
          <div className={`w-9 h-9 rounded-lg flex items-center justify-center ${
            totalMissingSkills > 0 ? 'bg-rose-50 text-rose-600' : 'bg-slate-100 text-slate-400'
          }`}>
            <AlertCircle className="w-5 h-5" />
          </div>
        </div>
        <p className="mt-2.5 text-[11px] text-slate-500">
          {totalMissingSkills === 0
            ? 'Complete prerequisite coverage!'
            : 'Competencies to acquire for this role'}
        </p>
      </Card>
    </div>
  );
};

export default SkillGapMetricCards;
