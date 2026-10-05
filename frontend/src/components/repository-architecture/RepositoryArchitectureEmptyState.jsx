import React from 'react';
import Card from '../common/Card';
import Button from '../common/Button';
import {
  Network,
  Sparkles,
  GitBranch,
  Layers,
  Code2,
  FolderTree,
  ShieldCheck,
  CheckCircle2,
} from 'lucide-react';

export const RepositoryArchitectureEmptyState = ({ onLoadSample }) => {
  return (
    <Card className="text-center py-12 px-6 shadow-sm">
      <div className="max-w-2xl mx-auto flex flex-col items-center">
        {/* Architectural Network Icon */}
        <div className="w-16 h-16 rounded-2xl bg-indigo-50 border border-indigo-100 flex items-center justify-center text-indigo-600 mb-5 shadow-sm">
          <Network className="w-8 h-8" />
        </div>

        {/* Title */}
        <h3 className="text-xl font-bold text-slate-900 mb-2">
          Inspect Repository Architecture & Layered Design
        </h3>

        {/* Subtitle */}
        <p className="text-sm text-slate-600 leading-relaxed mb-8 max-w-lg">
          Analyze public GitHub repositories to extract architectural signals, identify project classifications
          (Full-Stack, Backend, Frontend, Data Science), detect manifests, and inspect topological directory structures.
        </p>

        {/* 3-Step Process Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-left w-full mb-8">
          <div className="p-4 rounded-xl bg-slate-50 border border-slate-200/80 flex flex-col justify-between">
            <div>
              <div className="w-7 h-7 rounded-lg bg-indigo-600 text-white text-xs font-bold flex items-center justify-center mb-3">
                1
              </div>
              <h4 className="text-xs font-bold text-slate-900 mb-1">Specify Repository</h4>
              <p className="text-xs text-slate-500 leading-relaxed">
                Enter a GitHub repository URL or shorthand <code className="text-2xs font-mono bg-white px-1 py-0.5 rounded border">owner/repo</code>.
              </p>
            </div>
            <div className="mt-3 flex items-center gap-1 text-2xs text-indigo-600 font-semibold">
              <GitBranch className="w-3 h-3" /> Public GitHub Repos
            </div>
          </div>

          <div className="p-4 rounded-xl bg-slate-50 border border-slate-200/80 flex flex-col justify-between">
            <div>
              <div className="w-7 h-7 rounded-lg bg-indigo-600 text-white text-xs font-bold flex items-center justify-center mb-3">
                2
              </div>
              <h4 className="text-xs font-bold text-slate-900 mb-1">Tree & Pattern Inspection</h4>
              <p className="text-xs text-slate-500 leading-relaxed">
                Analyzes directory topology, build manifests, and file distributions.
              </p>
            </div>
            <div className="mt-3 flex items-center gap-1 text-2xs text-emerald-600 font-semibold">
              <FolderTree className="w-3 h-3" /> Topological Detection
            </div>
          </div>

          <div className="p-4 rounded-xl bg-slate-50 border border-slate-200/80 flex flex-col justify-between">
            <div>
              <div className="w-7 h-7 rounded-lg bg-indigo-600 text-white text-xs font-bold flex items-center justify-center mb-3">
                3
              </div>
              <h4 className="text-xs font-bold text-slate-900 mb-1">Architectural Intelligence</h4>
              <p className="text-xs text-slate-500 leading-relaxed">
                View classified architecture layers, concrete evidence, and tech stacks.
              </p>
            </div>
            <div className="mt-3 flex items-center gap-1 text-2xs text-sky-600 font-semibold">
              <Layers className="w-3 h-3" /> Grounded Signals
            </div>
          </div>
        </div>

        {/* Quick Demo CTA */}
        {onLoadSample && (
          <div className="pt-2 border-t border-slate-100 w-full flex flex-col sm:flex-row items-center justify-center gap-3">
            <span className="text-xs text-slate-500">Want to see a real analysis demo?</span>
            <Button
              variant="outline"
              size="sm"
              onClick={onLoadSample}
              icon={Sparkles}
              className="text-xs"
            >
              Load Sample Repository
            </Button>
          </div>
        )}
      </div>
    </Card>
  );
};

export default RepositoryArchitectureEmptyState;
