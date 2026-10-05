import React from 'react';
import Card from '../common/Card';
import StatusBadge from '../common/StatusBadge';
import {
  TrendingUp,
  Award,
  ChevronRight,
  CheckCircle2,
  AlertCircle,
  Briefcase,
} from 'lucide-react';

export const CareerRankedList = ({
  recommendations = [],
  activeSlug,
  onSelectRole,
}) => {
  if (!recommendations || recommendations.length === 0) return null;

  return (
    <Card
      title="Ranked Career Opportunities"
      subtitle={`Evaluated ${recommendations.length} supported roles ordered deterministically by skill match percentage.`}
      className="mb-6 shadow-sm"
    >
      <div className="space-y-3">
        {recommendations.map((rec, index) => {
          const rank = index + 1;
          const isActive = rec.role_slug === activeSlug;
          const matchPercentage =
            typeof rec.skill_match_percentage === 'number'
              ? rec.skill_match_percentage
              : rec.match_percentage || 0;

          const getBadgeTheme = (pct) => {
            if (pct >= 75) return { status: 'success', label: 'Strong Fit' };
            if (pct >= 50) return { status: 'info', label: 'Good Fit' };
            if (pct >= 25) return { status: 'warning', label: 'Moderate' };
            return { status: 'neutral', label: 'Emerging' };
          };

          const badge = getBadgeTheme(matchPercentage);

          return (
            <div
              key={rec.role_slug}
              onClick={() => onSelectRole && onSelectRole(rec.role_slug)}
              className={`p-4 rounded-xl border transition-all cursor-pointer ${
                isActive
                  ? 'bg-indigo-50/40 border-indigo-300 ring-2 ring-indigo-500/10 shadow-xs'
                  : 'bg-white border-slate-200 hover:border-slate-300 hover:bg-slate-50/50'
              }`}
            >
              <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
                {/* Left Side: Rank, Icon, Role Info */}
                <div className="flex items-center gap-3.5">
                  <div
                    className={`w-9 h-9 rounded-lg flex items-center justify-center font-bold text-sm shrink-0 ${
                      rank === 1
                        ? 'bg-amber-100 text-amber-800 border border-amber-200'
                        : rank === 2
                        ? 'bg-slate-100 text-slate-800 border border-slate-200'
                        : rank === 3
                        ? 'bg-amber-50 text-amber-900 border border-amber-100'
                        : 'bg-slate-50 text-slate-600 border border-slate-100'
                    }`}
                  >
                    {rank === 1 ? <Award className="w-5 h-5 text-amber-600" /> : `#${rank}`}
                  </div>

                  <div>
                    <div className="flex items-center gap-2 flex-wrap">
                      <h3 className="text-sm font-bold text-slate-900">
                        {rec.target_role}
                      </h3>
                      {rank === 1 && (
                        <span className="text-2xs font-semibold px-2 py-0.5 rounded-full bg-indigo-100 text-indigo-700">
                          Top Match
                        </span>
                      )}
                      <StatusBadge status={badge.status} text={badge.label} />
                      {isActive && (
                        <span className="text-2xs font-semibold px-2 py-0.5 rounded-full bg-indigo-600 text-white">
                          Viewing Details
                        </span>
                      )}
                    </div>
                    <div className="flex items-center gap-3 text-xs text-slate-500 mt-1">
                      <span className="flex items-center gap-1 text-emerald-700 font-medium">
                        <CheckCircle2 className="w-3 h-3 text-emerald-500" />
                        {rec.total_matched_skills} matched
                      </span>
                      <span>•</span>
                      <span className="flex items-center gap-1 text-amber-700 font-medium">
                        <AlertCircle className="w-3 h-3 text-amber-500" />
                        {rec.total_missing_skills} missing
                      </span>
                      <span>•</span>
                      <span className="text-slate-400">
                        {rec.total_required_skills} total skills
                      </span>
                    </div>
                  </div>
                </div>

                {/* Right Side: Score & Progress */}
                <div className="flex items-center gap-4 w-full sm:w-auto justify-between sm:justify-end">
                  <div className="w-24 sm:w-32">
                    <div className="flex items-center justify-between text-xs mb-1">
                      <span className="text-slate-400 text-2xs">Coverage</span>
                      <span className="font-bold text-slate-800">{matchPercentage}%</span>
                    </div>
                    <div className="h-2 w-full bg-slate-100 rounded-full overflow-hidden border border-slate-200">
                      <div
                        className={`h-full rounded-full ${
                          matchPercentage >= 75
                            ? 'bg-emerald-500'
                            : matchPercentage >= 50
                            ? 'bg-sky-500'
                            : matchPercentage >= 25
                            ? 'bg-amber-500'
                            : 'bg-indigo-500'
                        }`}
                        style={{ width: `${Math.min(100, Math.max(0, matchPercentage))}%` }}
                      />
                    </div>
                  </div>

                  <div className="flex items-center text-indigo-600 text-xs font-semibold shrink-0">
                    <ChevronRight className="w-4 h-4 text-slate-400 group-hover:text-indigo-600" />
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </Card>
  );
};

export default CareerRankedList;
