import React from 'react';
import Card from '../common/Card';
import {
  Briefcase,
  Search,
  CheckCircle2,
  Layers,
  ArrowRight,
  ShieldCheck,
  Target,
} from 'lucide-react';

export const JobMatchingEmptyState = ({ onLoadSample }) => {
  return (
    <Card className="text-center py-10 px-6 sm:px-12 bg-gradient-to-b from-white to-slate-50/60">
      <div className="max-w-2xl mx-auto space-y-6">
        {/* Central Icon */}
        <div className="w-14 h-14 rounded-2xl bg-indigo-50 border border-indigo-100 flex items-center justify-center mx-auto text-indigo-600 shadow-sm">
          <Briefcase className="w-7 h-7" />
        </div>

        {/* Title & Subtitle */}
        <div className="space-y-2">
          <h3 className="text-lg sm:text-xl font-bold text-slate-900 tracking-tight">
            Deterministic Job Description Skill Matching
          </h3>
          <p className="text-xs sm:text-sm text-slate-600 leading-relaxed max-w-xl mx-auto">
            Paste any technical job posting and input candidate skills. The deterministic matching engine
            extracts required technical competencies, matches them against developer skills, and calculates
            explainable coverage metrics and category breakdowns.
          </p>
        </div>

        {/* Processing Flow Steps */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-2 text-left">
          <div className="p-3.5 rounded-xl bg-white border border-slate-200/80 shadow-xs">
            <div className="flex items-center gap-2 mb-1.5">
              <span className="w-5 h-5 rounded-full bg-indigo-100 text-indigo-700 text-[11px] font-bold flex items-center justify-center">
                1
              </span>
              <span className="text-xs font-semibold text-slate-800">Extract Skills</span>
            </div>
            <p className="text-[11px] text-slate-500 leading-normal">
              Extracts canonical technical skills with alias normalization and boundary guards.
            </p>
          </div>

          <div className="p-3.5 rounded-xl bg-white border border-slate-200/80 shadow-xs">
            <div className="flex items-center gap-2 mb-1.5">
              <span className="w-5 h-5 rounded-full bg-indigo-100 text-indigo-700 text-[11px] font-bold flex items-center justify-center">
                2
              </span>
              <span className="text-xs font-semibold text-slate-800">Partition Gap</span>
            </div>
            <p className="text-[11px] text-slate-500 leading-normal">
              Partitions required skills into matched vs missing competencies deterministically.
            </p>
          </div>

          <div className="p-3.5 rounded-xl bg-white border border-slate-200/80 shadow-xs">
            <div className="flex items-center gap-2 mb-1.5">
              <span className="w-5 h-5 rounded-full bg-indigo-100 text-indigo-700 text-[11px] font-bold flex items-center justify-center">
                3
              </span>
              <span className="text-xs font-semibold text-slate-800">Category Coverage</span>
            </div>
            <p className="text-[11px] text-slate-500 leading-normal">
              Computes coverage percentages across standard taxonomy domains and evidence signals.
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
              <span>Load Sample Job Description & Skills</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
        )}
      </div>
    </Card>
  );
};

export default JobMatchingEmptyState;
