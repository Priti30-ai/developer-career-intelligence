import React from 'react';
import Card from '../common/Card';
import {
  Monitor,
  Server,
  Database,
  Container,
  FlaskConical,
  Brain,
  Terminal,
  FileText,
  Layers,
  ArrowDown,
  CheckCircle2,
} from 'lucide-react';

export const ArchitectureDiagram = ({ signals = [], summary = {}, projectType = '' }) => {
  // Map signals to structured layers in topological order
  const layerOrder = [
    { type: 'FRONTEND', label: 'Presentation & UI Layer', icon: Monitor, color: 'sky' },
    { type: 'CLI', label: 'CLI & Entrypoint Interface', icon: Terminal, color: 'purple' },
    { type: 'BACKEND', label: 'Backend Application & Services', icon: Server, color: 'indigo' },
    { type: 'DATA_SCIENCE', label: 'Analytics & Data Processing', icon: FlaskConical, color: 'teal' },
    { type: 'MACHINE_LEARNING', label: 'ML Models & Training Pipelines', icon: Brain, color: 'rose' },
    { type: 'DATABASE', label: 'Database & Persistent Models', icon: Database, color: 'emerald' },
    { type: 'TESTING', label: 'Test Suites & Verification', icon: FlaskConical, color: 'amber' },
    { type: 'DEVOPS', label: 'DevOps & Container Infrastructure', icon: Container, color: 'slate' },
  ];

  // Filter only layers that were actually detected in architecture_signals
  const detectedSignalsMap = new Map();
  signals.forEach((sig) => {
    detectedSignalsMap.set(sig.type, sig);
  });

  const activeLayers = layerOrder
    .filter((layer) => detectedSignalsMap.has(layer.type))
    .map((layer) => ({
      ...layer,
      signal: detectedSignalsMap.get(layer.type),
    }));

  if (activeLayers.length === 0) {
    return (
      <Card
        title="Detected Architecture Topology"
        subtitle="Visual representation of detected repository subsystems."
        className="mb-6 shadow-sm"
      >
        <div className="p-8 text-center text-xs text-slate-500 bg-slate-50 rounded-xl border border-slate-200">
          No distinct multi-tiered architecture signals were identified in the repository tree.
        </div>
      </Card>
    );
  }

  const getColorClasses = (color) => {
    switch (color) {
      case 'sky':
        return {
          bg: 'bg-sky-50',
          border: 'border-sky-200',
          text: 'text-sky-900',
          iconBg: 'bg-sky-100 text-sky-700',
          badge: 'bg-sky-100 text-sky-800',
        };
      case 'indigo':
        return {
          bg: 'bg-indigo-50',
          border: 'border-indigo-200',
          text: 'text-indigo-900',
          iconBg: 'bg-indigo-100 text-indigo-700',
          badge: 'bg-indigo-100 text-indigo-800',
        };
      case 'emerald':
        return {
          bg: 'bg-emerald-50',
          border: 'border-emerald-200',
          text: 'text-emerald-900',
          iconBg: 'bg-emerald-100 text-emerald-700',
          badge: 'bg-emerald-100 text-emerald-800',
        };
      case 'teal':
        return {
          bg: 'bg-teal-50',
          border: 'border-teal-200',
          text: 'text-teal-900',
          iconBg: 'bg-teal-100 text-teal-700',
          badge: 'bg-teal-100 text-teal-800',
        };
      case 'rose':
        return {
          bg: 'bg-rose-50',
          border: 'border-rose-200',
          text: 'text-rose-900',
          iconBg: 'bg-rose-100 text-rose-700',
          badge: 'bg-rose-100 text-rose-800',
        };
      case 'purple':
        return {
          bg: 'bg-purple-50',
          border: 'border-purple-200',
          text: 'text-purple-900',
          iconBg: 'bg-purple-100 text-purple-700',
          badge: 'bg-purple-100 text-purple-800',
        };
      case 'amber':
        return {
          bg: 'bg-amber-50',
          border: 'border-amber-200',
          text: 'text-amber-900',
          iconBg: 'bg-amber-100 text-amber-700',
          badge: 'bg-amber-100 text-amber-800',
        };
      default:
        return {
          bg: 'bg-slate-50',
          border: 'border-slate-200',
          text: 'text-slate-900',
          iconBg: 'bg-slate-200 text-slate-700',
          badge: 'bg-slate-200 text-slate-800',
        };
    }
  };

  return (
    <Card
      title="Architectural Subsystems & Topology"
      subtitle={`Structured layout of the ${activeLayers.length} verified architectural layers discovered in this ${projectType} repository.`}
      className="mb-6 shadow-sm overflow-hidden"
    >
      <div className="max-w-3xl mx-auto py-2 space-y-3">
        {activeLayers.map((layer, idx) => {
          const colors = getColorClasses(layer.color);
          const Icon = layer.icon;
          const isLast = idx === activeLayers.length - 1;

          return (
            <React.Fragment key={layer.type}>
              <div
                className={`p-4 rounded-xl border ${colors.border} ${colors.bg} shadow-2xs transition-all hover:shadow-xs`}
              >
                <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
                  <div className="flex items-center gap-3">
                    <div className={`w-9 h-9 rounded-lg flex items-center justify-center font-bold ${colors.iconBg} shrink-0`}>
                      <Icon className="w-5 h-5" />
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <h4 className={`text-sm font-bold ${colors.text}`}>{layer.label}</h4>
                        <span className={`text-2xs font-semibold px-2 py-0.5 rounded-full ${colors.badge}`}>
                          {layer.type}
                        </span>
                      </div>
                      <p className="text-xs text-slate-600 mt-0.5">{layer.signal.description}</p>
                    </div>
                  </div>

                  {/* Concrete Evidence Count Tag */}
                  {layer.signal.evidence && layer.signal.evidence.length > 0 && (
                    <div className="text-right self-end sm:self-center shrink-0">
                      <span className="text-2xs font-mono font-medium text-slate-600 bg-white/80 px-2 py-1 rounded border border-slate-200">
                        {layer.signal.evidence.length} evidence {layer.signal.evidence.length === 1 ? 'path' : 'paths'}
                      </span>
                    </div>
                  )}
                </div>

                {/* Evidence snippet pills */}
                {layer.signal.evidence && layer.signal.evidence.length > 0 && (
                  <div className="mt-3 pt-3 border-t border-slate-200/60 flex flex-wrap gap-1.5 items-center">
                    <span className="text-2xs font-semibold uppercase text-slate-400 mr-1">Paths:</span>
                    {layer.signal.evidence.slice(0, 4).map((path, pIdx) => (
                      <code
                        key={pIdx}
                        className="text-2xs font-mono px-2 py-0.5 rounded bg-white text-slate-700 border border-slate-200"
                      >
                        {path}
                      </code>
                    ))}
                    {layer.signal.evidence.length > 4 && (
                      <span className="text-2xs text-slate-400">
                        +{layer.signal.evidence.length - 4} more
                      </span>
                    )}
                  </div>
                )}
              </div>

              {!isLast && (
                <div className="flex justify-center py-1">
                  <div className="flex items-center gap-1 text-slate-400 text-2xs">
                    <ArrowDown className="w-4 h-4 text-slate-300" />
                  </div>
                </div>
              )}
            </React.Fragment>
          );
        })}
      </div>
    </Card>
  );
};

export default ArchitectureDiagram;
