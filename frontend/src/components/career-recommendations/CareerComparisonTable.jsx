import React from 'react';
import Card from '../common/Card';
import StatusBadge from '../common/StatusBadge';
import {
  Compass,
  ArrowUpDown,
  CheckCircle2,
  AlertCircle,
  ExternalLink,
} from 'lucide-react';

export const CareerComparisonTable = ({
  recommendations = [],
  activeSlug,
  onSelectRole,
}) => {
  if (!recommendations || recommendations.length === 0) return null;

  return (
    <Card
      title="Career Roles Comparison Matrix"
      subtitle="Side-by-side comparison of match metrics across all evaluated career roles."
      className="mb-6 shadow-sm overflow-hidden"
    >
      <div className="overflow-x-auto -mx-6 -my-6">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-slate-50/80 border-b border-slate-200 text-2xs font-semibold text-slate-500 uppercase tracking-wider">
              <th className="py-3 px-6">Rank</th>
              <th className="py-3 px-4">Career Path</th>
              <th className="py-3 px-4 text-center">Skill Coverage</th>
              <th className="py-3 px-4 text-center">Matched Skills</th>
              <th className="py-3 px-4 text-center">Missing Skills</th>
              <th className="py-3 px-4 text-center">Total Curriculum</th>
              <th className="py-3 px-6 text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 text-sm">
            {recommendations.map((rec, index) => {
              const rank = index + 1;
              const isActive = rec.role_slug === activeSlug;
              const matchPercentage =
                typeof rec.skill_match_percentage === 'number'
                  ? rec.skill_match_percentage
                  : rec.match_percentage || 0;

              return (
                <tr
                  key={rec.role_slug}
                  className={`transition-colors ${
                    isActive ? 'bg-indigo-50/50 font-medium' : 'hover:bg-slate-50/60'
                  }`}
                >
                  <td className="py-3.5 px-6 font-semibold text-slate-500 text-xs">
                    #{rank}
                  </td>
                  <td className="py-3.5 px-4 font-semibold text-slate-900">
                    <div className="flex items-center gap-2">
                      <span>{rec.target_role}</span>
                      {rank === 1 && (
                        <span className="text-2xs font-semibold px-2 py-0.5 rounded-full bg-amber-100 text-amber-800">
                          Top Match
                        </span>
                      )}
                      {isActive && (
                        <span className="text-2xs font-semibold px-2 py-0.5 rounded-full bg-indigo-100 text-indigo-700">
                          Active
                        </span>
                      )}
                    </div>
                  </td>
                  <td className="py-3.5 px-4 text-center">
                    <div className="inline-flex items-center gap-2">
                      <div className="w-16 h-2 bg-slate-100 rounded-full overflow-hidden border border-slate-200">
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
                      <span className="font-bold text-xs text-slate-800">{matchPercentage}%</span>
                    </div>
                  </td>
                  <td className="py-3.5 px-4 text-center text-xs font-semibold text-emerald-700">
                    <span className="inline-flex items-center gap-1 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-100">
                      <CheckCircle2 className="w-3 h-3 text-emerald-600" />
                      {rec.total_matched_skills}
                    </span>
                  </td>
                  <td className="py-3.5 px-4 text-center text-xs font-semibold text-amber-700">
                    <span className="inline-flex items-center gap-1 bg-amber-50 px-2 py-0.5 rounded border border-amber-100">
                      <AlertCircle className="w-3 h-3 text-amber-600" />
                      {rec.total_missing_skills}
                    </span>
                  </td>
                  <td className="py-3.5 px-4 text-center text-xs text-slate-600">
                    {rec.total_required_skills}
                  </td>
                  <td className="py-3.5 px-6 text-right">
                    <button
                      type="button"
                      onClick={() => onSelectRole && onSelectRole(rec.role_slug)}
                      className={`text-xs px-2.5 py-1 rounded font-medium transition-colors ${
                        isActive
                          ? 'bg-indigo-600 text-white shadow-2xs'
                          : 'bg-white border border-slate-200 text-slate-700 hover:bg-slate-100'
                      }`}
                    >
                      {isActive ? 'Selected' : 'View Details'}
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </Card>
  );
};

export default CareerComparisonTable;
