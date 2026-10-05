import React from 'react';
import Card from '../common/Card';
import {
  Percent,
  Target,
  CheckCircle2,
  AlertCircle,
  TrendingUp,
  Award,
} from 'lucide-react';

export const JobMatchingMetricCards = ({
  matchPercentage = 0,
  totalRequiredSkills = 0,
  matchedSkillCount = 0,
  missingSkillCount = 0,
}) => {
  // Determine score color and status
  const getScoreTheme = (pct) => {
    if (pct >= 75) {
      return {
        badgeBg: 'bg-emerald-50 text-emerald-700 border-emerald-200',
        barBg: 'bg-emerald-500',
        statusText: 'Strong Match',
        textColor: 'text-emerald-700',
      };
    }
    if (pct >= 50) {
      return {
        badgeBg: 'bg-amber-50 text-amber-700 border-amber-200',
        barBg: 'bg-amber-500',
        statusText: 'Moderate Match',
        textColor: 'text-amber-700',
      };
    }
    return {
      badgeBg: 'bg-rose-50 text-rose-700 border-rose-200',
      barBg: 'bg-rose-500',
      statusText: 'Low Match',
      textColor: 'text-rose-700',
    };
  };

  const theme = getScoreTheme(matchPercentage);

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {/* 1. Main Match Score Card */}
      <Card className="relative overflow-hidden border-indigo-200/80 bg-gradient-to-br from-white to-indigo-50/30">
        <div className="flex items-start justify-between">
          <div>
            <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-500 block">
              Match Score
            </span>
            <div className="mt-1 flex items-baseline gap-1.5">
              <span className={`text-3xl font-extrabold tracking-tight ${theme.textColor}`}>
                {matchPercentage}%
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
            style={{ width: `${Math.min(100, Math.max(0, matchPercentage))}%` }}
          />
        </div>

        <p className="mt-2 text-[11px] text-slate-500">
          {matchedSkillCount} of {totalRequiredSkills} requirements satisfied
        </p>
      </Card>

      {/* 2. Total Required Skills */}
      <Card>
        <div className="flex items-start justify-between">
          <div>
            <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-500 block">
              Required Skills
            </span>
            <div className="mt-1 flex items-baseline gap-1">
              <span className="text-3xl font-extrabold text-slate-900 tracking-tight">
                {totalRequiredSkills}
              </span>
              <span className="text-xs text-slate-400 font-medium">skills</span>
            </div>
          </div>
          <div className="w-9 h-9 rounded-lg bg-indigo-50 text-indigo-600 flex items-center justify-center">
            <Target className="w-5 h-5" />
          </div>
        </div>
        <p className="mt-2.5 text-[11px] text-slate-500">
          Extracted from job posting text
        </p>
      </Card>

      {/* 3. Matched Skills */}
      <Card>
        <div className="flex items-start justify-between">
          <div>
            <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-500 block">
              Matched Skills
            </span>
            <div className="mt-1 flex items-baseline gap-1">
              <span className="text-3xl font-extrabold text-emerald-600 tracking-tight">
                {matchedSkillCount}
              </span>
              <span className="text-xs text-emerald-600/70 font-medium">possessed</span>
            </div>
          </div>
          <div className="w-9 h-9 rounded-lg bg-emerald-50 text-emerald-600 flex items-center justify-center">
            <CheckCircle2 className="w-5 h-5" />
          </div>
        </div>
        <p className="mt-2.5 text-[11px] text-slate-500">
          Detected in candidate competencies
        </p>
      </Card>

      {/* 4. Missing Skills */}
      <Card>
        <div className="flex items-start justify-between">
          <div>
            <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-500 block">
              Missing Skills
            </span>
            <div className="mt-1 flex items-baseline gap-1">
              <span className={`text-3xl font-extrabold tracking-tight ${
                missingSkillCount > 0 ? 'text-rose-600' : 'text-slate-400'
              }`}>
                {missingSkillCount}
              </span>
              <span className="text-xs text-slate-400 font-medium">gaps</span>
            </div>
          </div>
          <div className={`w-9 h-9 rounded-lg flex items-center justify-center ${
            missingSkillCount > 0 ? 'bg-rose-50 text-rose-600' : 'bg-slate-100 text-slate-400'
          }`}>
            <AlertCircle className="w-5 h-5" />
          </div>
        </div>
        <p className="mt-2.5 text-[11px] text-slate-500">
          {missingSkillCount === 0
            ? 'Complete skill alignment!'
            : 'Target areas for candidate upskilling'}
        </p>
      </Card>
    </div>
  );
};

export default JobMatchingMetricCards;
