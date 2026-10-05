import React, { useState } from 'react';
import Card from '../common/Card';
import StatusBadge from '../common/StatusBadge';
import {
  Layers,
  ChevronDown,
  ChevronUp,
  FileCode,
  Folder,
  ShieldCheck,
  CheckCircle2,
} from 'lucide-react';

export const ArchitectureLayers = ({ signals = [] }) => {
  const [expandedIndex, setExpandedIndex] = useState(0); // expand first by default

  if (!signals || signals.length === 0) {
    return null;
  }

  const toggleExpand = (idx) => {
    setExpandedIndex(expandedIndex === idx ? null : idx);
  };

  const getSignalBadgeStatus = (type) => {
    switch (type) {
      case 'FRONTEND':
        return 'info';
      case 'BACKEND':
        return 'neutral';
      case 'DATABASE':
        return 'success';
      case 'DEVOPS':
        return 'warning';
      case 'MACHINE_LEARNING':
      case 'DATA_SCIENCE':
        return 'danger';
      default:
        return 'neutral';
    }
  };

  return (
    <Card
      title="Verified Architecture Signals & Concrete Evidence"
      subtitle="Each detected structural capability is grounded in concrete file, manifest, or directory path evidence."
      className="mb-6 shadow-sm"
    >
      <div className="space-y-3">
        {signals.map((sig, idx) => {
          const isExpanded = expandedIndex === idx;
          const badgeStatus = getSignalBadgeStatus(sig.type);

          return (
            <div
              key={`${sig.type}-${idx}`}
              className="rounded-xl border border-slate-200 overflow-hidden bg-white transition-all shadow-2xs"
            >
              {/* Card Header Accordion */}
              <button
                type="button"
                onClick={() => toggleExpand(idx)}
                className="w-full p-4 flex items-center justify-between text-left hover:bg-slate-50/60 transition-colors"
              >
                <div className="flex items-center gap-3">
                  <span className="w-6 h-6 rounded-md bg-indigo-50 text-indigo-600 font-bold text-xs flex items-center justify-center shrink-0">
                    {idx + 1}
                  </span>
                  <div>
                    <div className="flex items-center gap-2">
                      <h4 className="text-sm font-bold text-slate-900">{sig.type}</h4>
                      <StatusBadge status={badgeStatus} text={`${sig.evidence.length} Evidence Paths`} />
                    </div>
                    <p className="text-xs text-slate-500 mt-0.5">{sig.description}</p>
                  </div>
                </div>

                <div className="flex items-center text-slate-400">
                  {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                </div>
              </button>

              {/* Expanded Evidence List */}
              {isExpanded && (
                <div className="px-4 pb-4 pt-1 bg-slate-50/50 border-t border-slate-100">
                  <span className="text-2xs font-semibold uppercase tracking-wider text-slate-400 block mb-2 flex items-center gap-1">
                    <ShieldCheck className="w-3.5 h-3.5 text-indigo-600" />
                    Verified Evidence Paths in Repository Tree:
                  </span>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                    {sig.evidence.map((path, pIdx) => {
                      const isDir = path.endsWith('/');
                      return (
                        <div
                          key={pIdx}
                          className="px-3 py-2 rounded-lg bg-white border border-slate-200 text-xs font-mono flex items-center gap-2 shadow-2xs"
                        >
                          {isDir ? (
                            <Folder className="w-3.5 h-3.5 text-amber-500 shrink-0" />
                          ) : (
                            <FileCode className="w-3.5 h-3.5 text-sky-500 shrink-0" />
                          )}
                          <span className="truncate text-slate-700" title={path}>
                            {path}
                          </span>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </Card>
  );
};

export default ArchitectureLayers;
