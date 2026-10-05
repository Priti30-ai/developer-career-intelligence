import React from 'react';
import Card from '../common/Card';
import StatusBadge from '../common/StatusBadge';
import {
  Compass,
  Award,
  CheckCircle2,
  AlertCircle,
  Briefcase,
  TrendingUp,
  Target,
  Sparkles,
  Layers,
} from 'lucide-react';

export const CareerTopMatchCard = ({
  recommendation,
  rank = 1,
  isTopRecommendation = true,
  onSelectRole,
  totalRolesCount,
}) => {
  if (!recommendation) return null;

  const matchPercentage =
    typeof recommendation.skill_match_percentage === 'number'
      ? recommendation.skill_match_percentage
      : recommendation.match_percentage || 0;

  const getScoreTheme = (pct) => {
    if (pct >= 75) {
      return {
        badgeStatus: 'success',
        badgeText: 'Strong Career Match',
        textColor: 'text-emerald-700',
        bgColor: 'bg-emerald-50',
        borderColor: 'border-emerald-200',
        barColor: 'bg-emerald-500',
      };
    }
    if (pct >= 50) {
      return {
        badgeStatus: 'info',
        badgeText: 'Moderate Career Match',
        textColor: 'text-sky-700',
        bgColor: 'bg-sky-50',
        borderColor: 'border-sky-200',
        barColor: 'bg-sky-500',
      };
    }
    if (pct >= 25) {
      return {
        badgeStatus: 'warning',
        badgeText: 'Developing Opportunity',
        textColor: 'text-amber-700',
        bgColor: 'bg-amber-50',
        borderColor: 'border-amber-200',
        barColor: 'bg-amber-500',
      };
    }
    return {
      badgeStatus: 'neutral',
      badgeText: 'Emerging Trajectory',
      textColor: 'text-slate-700',
      bgColor: 'bg-slate-50',
      borderColor: 'border-slate-200',
      barColor: 'bg-indigo-500',
    };
  };

  const theme = getScoreTheme(matchPercentage);

  return (
    <Card className="mb-6 border-indigo-100 bg-gradient-to-br from-white via-indigo-50/20 to-white shadow-sm overflow-hidden">
      <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-6 pb-6 border-b border-slate-100">
        {/* Left Side: Rank, Role, Title */}
        <div className="flex items-start gap-4">
          <div className="w-14 h-14 rounded-2xl bg-indigo-600 text-white flex flex-col items-center justify-center font-bold shrink-0 shadow-md shadow-indigo-200">
            {isTopRecommendation ? (
              <>
                <Award className="w-5 h-5 text-amber-300" />
                <span className="text-2xs uppercase tracking-wider mt-0.5">#1 Best</span>
              </>
            ) : (
              <>
                <span className="text-xs uppercase text-indigo-200">Rank</span>
                <span className="text-base leading-none font-extrabold">#{rank}</span>
              </>
            )}
          </div>

          <div>
            <div className="flex items-center gap-2 flex-wrap mb-1">
              <span className="text-xs font-semibold uppercase tracking-wider text-indigo-600">
                {isTopRecommendation ? 'Recommended Career Path' : 'Evaluated Career Path'}
              </span>
              <StatusBadge status={theme.badgeStatus} text={theme.badgeText} />
            </div>

            <h2 className="text-2xl font-bold text-slate-900 tracking-tight">
              {recommendation.target_role}
            </h2>

            <p className="text-xs text-slate-500 mt-1 flex items-center gap-1.5">
              <Briefcase className="w-3.5 h-3.5 text-slate-400" />
              Role slug:{' '}
              <code className="px-1.5 py-0.5 bg-slate-100 rounded text-slate-700 font-mono text-2xs">
                {recommendation.role_slug}
              </code>
              {totalRolesCount && (
                <span className="text-slate-400">
                  • Evaluated across {totalRolesCount} predefined career benchmarks
                </span>
              )}
            </p>
          </div>
        </div>

        {/* Right Side: Match Score Hero */}
        <div className="flex items-center gap-5 w-full lg:w-auto justify-between lg:justify-end">
          <div className="text-right">
            <span className="text-xs font-medium text-slate-500 uppercase tracking-wider block">
              Skill Coverage
            </span>
            <div className="flex items-baseline gap-1 justify-end">
              <span className="text-4xl font-extrabold text-slate-900 tracking-tight">
                {matchPercentage}
              </span>
              <span className="text-xl font-bold text-indigo-600">%</span>
            </div>
          </div>

          {/* Visual Circular/Bar Indicator */}
          <div className="w-24 sm:w-32">
            <div className="h-3 w-full bg-slate-100 rounded-full overflow-hidden border border-slate-200">
              <div
                className={`h-full rounded-full transition-all duration-700 ${theme.barColor}`}
                style={{ width: `${Math.min(100, Math.max(0, matchPercentage))}%` }}
              />
            </div>
            <span className="text-2xs text-slate-400 text-right block mt-1">
              {recommendation.total_matched_skills} of {recommendation.total_required_skills} skills met
            </span>
          </div>
        </div>
      </div>

      {/* 4 Summary Stats Bar */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 pt-6">
        <div className="p-3 bg-white rounded-lg border border-slate-200">
          <div className="flex items-center justify-between text-xs text-slate-500 mb-1">
            <span>Required Skills</span>
            <Target className="w-3.5 h-3.5 text-slate-400" />
          </div>
          <div className="text-lg font-bold text-slate-900">
            {recommendation.total_required_skills}
          </div>
          <div className="text-2xs text-slate-400 mt-0.5">Role curriculum total</div>
        </div>

        <div className="p-3 bg-emerald-50/50 rounded-lg border border-emerald-100">
          <div className="flex items-center justify-between text-xs text-emerald-700 mb-1">
            <span>Matched Skills</span>
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
          </div>
          <div className="text-lg font-bold text-emerald-900">
            {recommendation.total_matched_skills}
          </div>
          <div className="text-2xs text-emerald-600/80 mt-0.5">Strengths ready to leverage</div>
        </div>

        <div className="p-3 bg-amber-50/50 rounded-lg border border-amber-100">
          <div className="flex items-center justify-between text-xs text-amber-700 mb-1">
            <span>Missing Skills</span>
            <AlertCircle className="w-3.5 h-3.5 text-amber-600" />
          </div>
          <div className="text-lg font-bold text-amber-900">
            {recommendation.total_missing_skills}
          </div>
          <div className="text-2xs text-amber-600/80 mt-0.5">Actionable learning targets</div>
        </div>

        <div className="p-3 bg-sky-50/50 rounded-lg border border-sky-100">
          <div className="flex items-center justify-between text-xs text-sky-700 mb-1">
            <span>Roadmap Stages</span>
            <Layers className="w-3.5 h-3.5 text-sky-600" />
          </div>
          <div className="text-lg font-bold text-sky-900">
            {recommendation.roadmap?.length || 0}
          </div>
          <div className="text-2xs text-sky-600/80 mt-0.5">Structured milestone phases</div>
        </div>
      </div>
    </Card>
  );
};

export default CareerTopMatchCard;
