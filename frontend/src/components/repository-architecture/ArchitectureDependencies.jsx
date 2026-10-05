import React from 'react';
import Card from '../common/Card';
import {
  Package,
  Code2,
  FileText,
  FileCode,
  Tag,
  CheckCircle2,
} from 'lucide-react';

export const ArchitectureDependencies = ({
  dependencyFiles = [],
  languages = [],
  documentationFiles = [],
}) => {
  return (
    <Card
      title="Technology Stack & Manifest Inventory"
      subtitle="Detected programming languages, package manifests, and project documentation."
      className="mb-6 shadow-sm"
    >
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Normalized Languages Detected */}
        <div>
          <span className="text-xs font-bold text-slate-800 flex items-center gap-1.5 mb-3">
            <Code2 className="w-4 h-4 text-emerald-600" />
            Detected Languages ({languages.length})
          </span>

          {languages.length > 0 ? (
            <div className="flex flex-wrap gap-1.5 p-3 rounded-xl bg-slate-50 border border-slate-200/80">
              {languages.map((lang) => (
                <span
                  key={lang}
                  className="px-2.5 py-1 rounded-md text-xs font-semibold bg-white text-slate-800 border border-slate-200 shadow-2xs flex items-center gap-1.5"
                >
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
                  {lang}
                </span>
              ))}
            </div>
          ) : (
            <p className="text-xs text-slate-400 italic">No recognized language extensions detected.</p>
          )}
        </div>

        {/* Dependency Manifests */}
        <div>
          <span className="text-xs font-bold text-slate-800 flex items-center gap-1.5 mb-3">
            <Package className="w-4 h-4 text-indigo-600" />
            Package & Build Manifests ({dependencyFiles.length})
          </span>

          {dependencyFiles.length > 0 ? (
            <div className="space-y-1.5 p-3 rounded-xl bg-slate-50 border border-slate-200/80 font-mono text-xs max-h-60 overflow-y-auto">
              {dependencyFiles.map((manifest, idx) => (
                <div
                  key={idx}
                  className="flex items-center gap-2 p-1.5 rounded bg-white border border-slate-200/60 shadow-2xs"
                >
                  <Package className="w-3.5 h-3.5 text-indigo-500 shrink-0" />
                  <span className="text-slate-800 truncate" title={manifest}>
                    {manifest}
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-xs text-slate-400 italic">No package manifests found.</p>
          )}
        </div>

        {/* Documentation Files */}
        <div>
          <span className="text-xs font-bold text-slate-800 flex items-center gap-1.5 mb-3">
            <FileText className="w-4 h-4 text-amber-500" />
            Documentation Artifacts ({documentationFiles.length})
          </span>

          {documentationFiles.length > 0 ? (
            <div className="space-y-1.5 p-3 rounded-xl bg-slate-50 border border-slate-200/80 font-mono text-xs max-h-60 overflow-y-auto">
              {documentationFiles.map((doc, idx) => (
                <div
                  key={idx}
                  className="flex items-center gap-2 p-1.5 rounded bg-white border border-slate-200/60 shadow-2xs"
                >
                  <FileText className="w-3.5 h-3.5 text-amber-500 shrink-0" />
                  <span className="text-slate-800 truncate" title={doc}>
                    {doc}
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-xs text-slate-400 italic">No documentation files detected.</p>
          )}
        </div>
      </div>
    </Card>
  );
};

export default ArchitectureDependencies;
