import React from 'react';
import {
  Layers,
  FileCode,
  FolderTree,
  Code2,
  Package,
  Activity,
} from 'lucide-react';

export const ArchitectureMetricCards = ({ data }) => {
  if (!data) return null;

  const {
    project_type,
    primary_language,
    languages_detected = [],
    directories_detected = [],
    important_files = [],
    dependency_files = [],
    architecture_signals = [],
    summary = {},
  } = data;

  const totalFiles = summary.total_files_analyzed || 0;
  const totalDirs = summary.total_directories_detected || directories_detected.length || 0;
  const classification = summary.primary_project_type || project_type || 'UNKNOWN';

  const formatClassification = (type) => {
    switch (type) {
      case 'FULL_STACK':
        return 'Full-Stack Platform';
      case 'FRONTEND':
        return 'Frontend Web App';
      case 'BACKEND':
        return 'Backend API / Service';
      case 'DATA_SCIENCE':
        return 'Data Science Project';
      case 'MACHINE_LEARNING':
        return 'Machine Learning / AI';
      case 'CLI':
        return 'CLI Utility';
      case 'LIBRARY':
        return 'Package / Library';
      default:
        return type || 'Generic Repository';
    }
  };

  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3.5 mb-6">
      {/* Classification */}
      <div className="p-4 bg-white rounded-xl border border-slate-200 shadow-2xs flex flex-col justify-between col-span-2 sm:col-span-1 lg:col-span-2">
        <div className="flex items-center justify-between text-xs text-slate-500 mb-1">
          <span>Project Classification</span>
          <Activity className="w-3.5 h-3.5 text-indigo-600" />
        </div>
        <div className="text-base font-extrabold text-slate-900 truncate" title={classification}>
          {formatClassification(classification)}
        </div>
        <div className="text-2xs font-mono text-indigo-600 font-semibold mt-1">
          {classification}
        </div>
      </div>

      {/* Primary Language */}
      <div className="p-4 bg-white rounded-xl border border-slate-200 shadow-2xs flex flex-col justify-between">
        <div className="flex items-center justify-between text-xs text-slate-500 mb-1">
          <span>Primary Language</span>
          <Code2 className="w-3.5 h-3.5 text-emerald-600" />
        </div>
        <div className="text-lg font-bold text-slate-900 truncate">
          {primary_language || (languages_detected.length > 0 ? languages_detected[0] : 'None')}
        </div>
        <div className="text-2xs text-slate-400 mt-1">
          {languages_detected.length} detected
        </div>
      </div>

      {/* Files Analyzed */}
      <div className="p-4 bg-white rounded-xl border border-slate-200 shadow-2xs flex flex-col justify-between">
        <div className="flex items-center justify-between text-xs text-slate-500 mb-1">
          <span>Files Analyzed</span>
          <FileCode className="w-3.5 h-3.5 text-sky-600" />
        </div>
        <div className="text-lg font-extrabold text-slate-900">
          {totalFiles}
        </div>
        <div className="text-2xs text-slate-400 mt-1">
          Tree items scanned
        </div>
      </div>

      {/* Structural Directories */}
      <div className="p-4 bg-white rounded-xl border border-slate-200 shadow-2xs flex flex-col justify-between">
        <div className="flex items-center justify-between text-xs text-slate-500 mb-1">
          <span>Directories</span>
          <FolderTree className="w-3.5 h-3.5 text-amber-600" />
        </div>
        <div className="text-lg font-extrabold text-slate-900">
          {totalDirs}
        </div>
        <div className="text-2xs text-slate-400 mt-1">
          Structural paths
        </div>
      </div>

      {/* Architecture Signals */}
      <div className="p-4 bg-white rounded-xl border border-slate-200 shadow-2xs flex flex-col justify-between">
        <div className="flex items-center justify-between text-xs text-slate-500 mb-1">
          <span>Architecture Signals</span>
          <Layers className="w-3.5 h-3.5 text-indigo-600" />
        </div>
        <div className="text-lg font-extrabold text-indigo-600">
          {architecture_signals.length}
        </div>
        <div className="text-2xs text-slate-400 mt-1">
          Concrete layers verified
        </div>
      </div>
    </div>
  );
};

export default ArchitectureMetricCards;
