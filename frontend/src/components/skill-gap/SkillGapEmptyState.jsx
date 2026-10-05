import React from 'react';
import Card from '../common/Card';
import {
  Target,
  ArrowRight,
  CheckCircle2,
  AlertCircle,
  BarChart3,
  Compass,
} from 'lucide-react';

export const SkillGapEmptyState = ({ onLoadSample }) => {
  return (
    <Card className="text-center py-10 px-6 sm:px-12 bg-gradient-to-b from-white to-slate-50/60">
      <div className="max-w-2xl mx-auto space-y-6">
        {/* Central Icon */}
        <div className="w-14 h-14 rounded-2xl bg-indigo-50 border border-indigo-100 flex items-center justify-center mx-auto text-indigo-600 shadow-sm">
          <Target className="w-7 h-7" />
        </div>

        {/* Title & Concise Summary */}
        <div className="space-y-2">
          <h3 className="text-lg sm:text-xl font-bold text-slate-900 tracking-tight">
            Benchmark Your Skills Against Target Career Roles
          </h3>
          <p className="text-xs sm:text-sm text-slate-600 leading-relaxed max-w-xl mx-auto">
            Compare your current developer competencies with the prerequisite requirements of predefined
            engineering roles. The deterministic gap engine identifies what you already have, exact missing
            competencies, and category-by-category coverage.
          </p>
        </div>

        {/* Step-by-Step Overview */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-2 text-left">
          <div className="p-3.5 rounded-xl bg-white border border-slate-200/80 shadow-2xs">
            <div className="flex items-center gap-2 mb-1.5">
              <span className="w-5 h-5 rounded-full bg-indigo-100 text-indigo-700 text-[11px] font-bold flex items-center justify-center">
                1
              </span>
              <span className="text-xs font-semibold text-slate-800">Select Role</span>
            </div>
            <p className="text-[11px] text-slate-500 leading-normal">
              Choose an industry role such as Backend Developer, Data Scientist, or Full Stack Developer.
            </p>
          </div>

          <div className="p-3.5 rounded-xl bg-white border border-slate-200/80 shadow-2xs">
            <div className="flex items-center gap-2 mb-1.5">
              <span className="w-5 h-5 rounded-full bg-indigo-100 text-indigo-700 text-[11px] font-bold flex items-center justify-center">
                2
              </span>
              <span className="text-xs font-semibold text-slate-800">Identify Gaps</span>
            </div>
            <p className="text-[11px] text-slate-500 leading-normal">
              Evaluates current skills against role prerequisites and partitions them into matched vs missing.
            </p>
          </div>

          <div className="p-3.5 rounded-xl bg-white border border-slate-200/80 shadow-2xs">
            <div className="flex items-center gap-2 mb-1.5">
              <span className="w-5 h-5 rounded-full bg-indigo-100 text-indigo-700 text-[11px] font-bold flex items-center justify-center">
                3
              </span>
              <span className="text-xs font-semibold text-slate-800">Coverage Score</span>
            </div>
            <p className="text-[11px] text-slate-500 leading-normal">
              Calculates deterministic match percentages and category coverage across domain taxonomies.
            </p>
          </div>
        </div>

        {/* Quick action button */}
        {onLoadSample && (
          <div className="pt-2">
            <button
              type="button"
              onClick={onLoadSample}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-lg text-xs sm:text-sm font-medium bg-slate-100 text-slate-700 hover:bg-slate-200 border border-slate-200 transition-colors"
            >
              <span>Load Sample Developer Profile & Target Role</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
        )}
      </div>
    </Card>
  );
};

export default SkillGapEmptyState;
