import React from 'react';
import Card from '../common/Card';
import { Layers } from 'lucide-react';

export const SkillGapCategoryCard = ({ categoryBreakdown = [] }) => {
  if (!categoryBreakdown || categoryBreakdown.length === 0) {
    return null;
  }

  // Filter to categories that actually have required skills for this role
  const activeCategories = categoryBreakdown.filter((cat) => cat.required_count > 0);

  if (activeCategories.length === 0) {
    return null;
  }

  return (
    <Card
      title="Category-Level Skill Coverage"
      subtitle="Deterministic breakdown of role prerequisites across standardized technical taxonomy categories."
    >
      <div className="space-y-4">
        {activeCategories.map((item) => {
          const pct = Math.round(item.coverage_percentage || 0);

          let barColor = 'bg-rose-500';
          let badgeBg = 'bg-rose-50 text-rose-700 border-rose-200';

          if (pct === 100) {
            barColor = 'bg-emerald-500';
            badgeBg = 'bg-emerald-50 text-emerald-700 border-emerald-200';
          } else if (pct >= 50) {
            barColor = 'bg-indigo-600';
            badgeBg = 'bg-indigo-50 text-indigo-700 border-indigo-200';
          } else if (pct > 0) {
            barColor = 'bg-amber-500';
            badgeBg = 'bg-amber-50 text-amber-700 border-amber-200';
          }

          return (
            <div
              key={item.category}
              className="p-3.5 rounded-lg border border-slate-100 hover:border-slate-200 bg-slate-50/50 transition-all space-y-2"
            >
              <div className="flex items-center justify-between flex-wrap gap-2">
                <div className="flex items-center gap-2">
                  <div className="w-6 h-6 rounded-md bg-white border border-slate-200 flex items-center justify-center text-slate-600">
                    <Layers className="w-3.5 h-3.5" />
                  </div>
                  <span className="text-xs sm:text-sm font-semibold text-slate-900">
                    {item.category}
                  </span>
                </div>

                <div className="flex items-center gap-2">
                  <span className="text-xs text-slate-500">
                    <strong className="text-slate-800">{item.matched_count}</strong> of{' '}
                    <strong className="text-slate-800">{item.required_count}</strong> prerequisites met
                    {item.missing_count > 0 && (
                      <span className="text-rose-600 ml-1">({item.missing_count} missing)</span>
                    )}
                  </span>
                  <span
                    className={`px-2 py-0.5 rounded-full text-xs font-bold border ${badgeBg}`}
                  >
                    {pct}%
                  </span>
                </div>
              </div>

              {/* Progress Bar */}
              <div className="w-full bg-slate-200/80 rounded-full h-2 overflow-hidden">
                <div
                  className={`h-full rounded-full transition-all duration-500 ${barColor}`}
                  style={{ width: `${Math.min(100, Math.max(0, pct))}%` }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </Card>
  );
};

export default SkillGapCategoryCard;
