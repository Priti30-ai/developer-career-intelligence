import React, { useState } from 'react';
import Card from '../common/Card';
import {
  FolderTree,
  Folder,
  FileCode,
  FileText,
  ChevronRight,
  ChevronDown,
  Layers,
} from 'lucide-react';

export const ProjectStructure = ({ directories = [], importantFiles = [] }) => {
  const [showAllDirs, setShowAllDirs] = useState(false);
  const [showAllFiles, setShowAllFiles] = useState(false);

  if (directories.length === 0 && importantFiles.length === 0) {
    return null;
  }

  const displayedDirs = showAllDirs ? directories : directories.slice(0, 12);
  const displayedFiles = showAllFiles ? importantFiles : importantFiles.slice(0, 12);

  return (
    <Card
      title="Repository Structural Layout & Key Paths"
      subtitle="Architectural directory hierarchy and prominent configuration/entrypoint files identified in the repository tree."
      className="mb-6 shadow-sm"
    >
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Structural Directories */}
        <div>
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-bold text-slate-800 flex items-center gap-1.5">
              <Folder className="w-4 h-4 text-amber-500" />
              Key Architectural Directories ({directories.length})
            </span>
            {directories.length > 12 && (
              <button
                type="button"
                onClick={() => setShowAllDirs(!showAllDirs)}
                className="text-xs text-indigo-600 hover:text-indigo-800 font-medium"
              >
                {showAllDirs ? 'Show less' : `View all ${directories.length}`}
              </button>
            )}
          </div>

          <div className="space-y-1.5 p-3 rounded-xl bg-slate-50 border border-slate-200/80 max-h-80 overflow-y-auto font-mono text-xs">
            {displayedDirs.map((dir, idx) => (
              <div
                key={idx}
                className="flex items-center gap-2 p-1.5 rounded bg-white border border-slate-200/60 shadow-2xs hover:border-slate-300 transition-colors"
              >
                <Folder className="w-3.5 h-3.5 text-amber-500 shrink-0" />
                <span className="text-slate-700 truncate" title={dir}>
                  {dir}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Prominent Architectural & Build Files */}
        <div>
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-bold text-slate-800 flex items-center gap-1.5">
              <FileCode className="w-4 h-4 text-sky-500" />
              Important Configuration & Entrypoint Files ({importantFiles.length})
            </span>
            {importantFiles.length > 12 && (
              <button
                type="button"
                onClick={() => setShowAllFiles(!showAllFiles)}
                className="text-xs text-indigo-600 hover:text-indigo-800 font-medium"
              >
                {showAllFiles ? 'Show less' : `View all ${importantFiles.length}`}
              </button>
            )}
          </div>

          <div className="space-y-1.5 p-3 rounded-xl bg-slate-50 border border-slate-200/80 max-h-80 overflow-y-auto font-mono text-xs">
            {displayedFiles.map((file, idx) => (
              <div
                key={idx}
                className="flex items-center gap-2 p-1.5 rounded bg-white border border-slate-200/60 shadow-2xs hover:border-slate-300 transition-colors"
              >
                <FileCode className="w-3.5 h-3.5 text-sky-500 shrink-0" />
                <span className="text-slate-700 truncate" title={file}>
                  {file}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </Card>
  );
};

export default ProjectStructure;
