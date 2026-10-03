import React from 'react';
import { ShieldCheck, ShieldAlert, Shield, Zap, Hash } from 'lucide-react';

/**
 * EvidenceSummaryPanel
 *
 * Displays account-level evidence signal counts from the EvidenceSummary backend schema.
 * Evidence types are factual — derived from manifest parsing, language detection,
 * topic tags, directory structure, config files, and README content.
 *
 * No subjective scoring. Values are discrete signal counts.
 */
export const EvidenceSummaryPanel = ({ evidenceSummary = {} }) => {
  const {
    strong_evidence_count = 0,
    moderate_evidence_count = 0,
    weak_evidence_count = 0,
    total_evidence_signals = 0,
    technologies_with_strong_evidence = 0,
    technologies_with_evidence = 0,
  } = evidenceSummary;

  const hasData =
    total_evidence_signals > 0 ||
    strong_evidence_count > 0 ||
    moderate_evidence_count > 0 ||
    weak_evidence_count > 0;

  if (!hasData) return null;

  return (
    <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-slate-900">Evidence Summary</h3>
        <p className="text-xs text-slate-500 mt-0.5">
          Account-wide evidence signal counts across all analyzed repositories. Evidence is derived from dependency manifests,
          detected languages, repository topics, directory structure, configuration files, and README content.
        </p>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
        {/* Total signals */}
        <div className="flex flex-col gap-1.5 p-3 rounded-lg border border-slate-100 bg-slate-50">
          <div className="flex items-center gap-1.5">
            <Zap className="w-3.5 h-3.5 text-indigo-600" />
            <span className="text-[10px] font-semibold text-slate-500 uppercase tracking-wide">
              Total Signals
            </span>
          </div>
          <span className="text-2xl font-bold font-mono text-slate-900">
            {total_evidence_signals}
          </span>
          <span className="text-[10px] text-slate-400">Discrete evidence events</span>
        </div>

        {/* Technologies with any evidence */}
        <div className="flex flex-col gap-1.5 p-3 rounded-lg border border-slate-100 bg-slate-50">
          <div className="flex items-center gap-1.5">
            <Hash className="w-3.5 h-3.5 text-slate-500" />
            <span className="text-[10px] font-semibold text-slate-500 uppercase tracking-wide">
              Tech w/ Evidence
            </span>
          </div>
          <span className="text-2xl font-bold font-mono text-slate-900">
            {technologies_with_evidence}
          </span>
          <span className="text-[10px] text-slate-400">At least 1 signal</span>
        </div>

        {/* Strong */}
        <div className="flex flex-col gap-1.5 p-3 rounded-lg border border-emerald-100 bg-emerald-50">
          <div className="flex items-center gap-1.5">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
            <span className="text-[10px] font-semibold text-emerald-700 uppercase tracking-wide">
              Strong
            </span>
          </div>
          <span className="text-2xl font-bold font-mono text-emerald-900">
            {strong_evidence_count}
          </span>
          <span className="text-[10px] text-emerald-600">
            Skills w/ STRONG evidence
          </span>
        </div>

        {/* Tech with strong evidence */}
        <div className="flex flex-col gap-1.5 p-3 rounded-lg border border-teal-100 bg-teal-50">
          <div className="flex items-center gap-1.5">
            <ShieldCheck className="w-3.5 h-3.5 text-teal-600" />
            <span className="text-[10px] font-semibold text-teal-700 uppercase tracking-wide">
              Tech STRONG
            </span>
          </div>
          <span className="text-2xl font-bold font-mono text-teal-900">
            {technologies_with_strong_evidence}
          </span>
          <span className="text-[10px] text-teal-600">
            Multi-repo or manifest proof
          </span>
        </div>

        {/* Moderate */}
        <div className="flex flex-col gap-1.5 p-3 rounded-lg border border-amber-100 bg-amber-50">
          <div className="flex items-center gap-1.5">
            <ShieldAlert className="w-3.5 h-3.5 text-amber-600" />
            <span className="text-[10px] font-semibold text-amber-700 uppercase tracking-wide">
              Moderate
            </span>
          </div>
          <span className="text-2xl font-bold font-mono text-amber-900">
            {moderate_evidence_count}
          </span>
          <span className="text-[10px] text-amber-600">
            Skills w/ MODERATE evidence
          </span>
        </div>

        {/* Weak */}
        <div className="flex flex-col gap-1.5 p-3 rounded-lg border border-slate-200 bg-slate-50">
          <div className="flex items-center gap-1.5">
            <Shield className="w-3.5 h-3.5 text-slate-400" />
            <span className="text-[10px] font-semibold text-slate-500 uppercase tracking-wide">
              Weak
            </span>
          </div>
          <span className="text-2xl font-bold font-mono text-slate-700">
            {weak_evidence_count}
          </span>
          <span className="text-[10px] text-slate-400">
            Topic-only or inferred
          </span>
        </div>
      </div>

      {/* Evidence strength legend */}
      <div className="mt-3 pt-3 border-t border-slate-100 flex flex-wrap gap-x-5 gap-y-1.5 text-[11px] text-slate-500">
        <span>
          <span className="font-semibold text-emerald-700">STRONG</span> — present in ≥2 repositories or confirmed via dependency manifest
        </span>
        <span>
          <span className="font-semibold text-amber-700">MODERATE</span> — detected in a single repository
        </span>
        <span>
          <span className="font-semibold text-slate-500">WEAK</span> — inferred from repository topic tags only
        </span>
      </div>
    </div>
  );
};

export default EvidenceSummaryPanel;
