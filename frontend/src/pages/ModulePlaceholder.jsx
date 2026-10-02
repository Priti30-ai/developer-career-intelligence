import React from 'react';
import { Link } from 'react-router-dom';
import Card from '../components/common/Card';
import StatusBadge from '../components/common/StatusBadge';
import Button from '../components/common/Button';
import {
  ArrowLeft,
  Server,
  Layers,
  Clock,
  Code2,
  FileCode2,
  CheckCircle2
} from 'lucide-react';

export const ModulePlaceholder = ({
  moduleName,
  group,
  description,
  apiEndpoint,
  status = 'Implementation in Progress',
  plannedCapabilities = [],
}) => {
  return (
    <div className="space-y-6">
      {/* Module Header Card */}
      <div className="bg-white border border-slate-200 rounded-xl p-6 sm:p-8 shadow-sm">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            {group && (
              <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium bg-slate-100 text-slate-700 border border-slate-200 mb-3">
                <Layers className="w-3.5 h-3.5 text-slate-500" />
                <span>{group}</span>
              </div>
            )}
            <h2 className="text-2xl font-bold text-slate-900 tracking-tight">
              {moduleName}
            </h2>
            <p className="mt-2 text-sm text-slate-600 max-w-3xl leading-relaxed">
              {description}
            </p>
          </div>

          <div className="flex sm:flex-col items-start sm:items-end gap-2 flex-shrink-0">
            <StatusBadge
              status="warning"
              text={status}
              className="text-xs"
            />
            <span className="text-[11px] text-slate-400 font-mono">
              Phase Integration
            </span>
          </div>
        </div>
      </div>

      {/* Backend Integration & Specifications Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Backend Target Endpoint */}
        <Card
          title="Backend Data Pipeline"
          subtitle="Target FastAPI endpoint powering this module"
          className="lg:col-span-1"
        >
          <div className="space-y-4">
            <div className="p-3 bg-slate-50 rounded-lg border border-slate-200">
              <div className="flex items-center gap-2 text-xs font-semibold text-slate-700 mb-1">
                <Server className="w-4 h-4 text-indigo-600" />
                <span>FastAPI Microservice</span>
              </div>
              <code className="text-xs font-mono text-indigo-700 bg-white px-2 py-1 rounded border border-slate-200 block truncate">
                {apiEndpoint || 'Pending router assignment'}
              </code>
            </div>

            <div className="text-xs text-slate-500 space-y-2">
              <div className="flex items-center gap-2">
                <Clock className="w-3.5 h-3.5 text-slate-400" />
                <span>Status: API endpoint registered in FastAPI backend</span>
              </div>
              <div className="flex items-center gap-2">
                <FileCode2 className="w-3.5 h-3.5 text-slate-400" />
                <span>Data Contract: Pydantic v2 schemas</span>
              </div>
            </div>

            <div className="pt-2">
              <Link to="/dashboard">
                <Button variant="outline" size="sm" icon={ArrowLeft} className="w-full">
                  Return to Dashboard
                </Button>
              </Link>
            </div>
          </div>
        </Card>

        {/* Factual Scope & Next Steps (No fake metrics) */}
        <Card
          title="Module Specification & Objectives"
          subtitle="Technical capabilities designated for upcoming milestone delivery"
          className="lg:col-span-2"
        >
          <div className="space-y-4">
            <p className="text-xs text-slate-600 leading-relaxed">
              In accordance with project guidelines, this module UI will be activated in subsequent
              tasks directly utilizing live data from the verified FastAPI backend endpoints.
              No synthetic or simulated metrics are displayed prior to endpoint binding.
            </p>

            <div className="border-t border-slate-100 pt-3">
              <h4 className="text-xs font-semibold text-slate-900 uppercase tracking-wider mb-2">
                Designated Deliverables
              </h4>
              <ul className="space-y-2">
                {(plannedCapabilities.length > 0
                  ? plannedCapabilities
                  : [
                      'Input parameter forms with client-side validation',
                      'Direct asynchronous querying against the FastAPI service',
                      'Deterministic, evidence-grounded visualizations',
                      'Exportable reports and audit trails',
                    ]
                ).map((cap, idx) => (
                  <li key={idx} className="flex items-start gap-2.5 text-xs text-slate-600">
                    <CheckCircle2 className="w-4 h-4 text-slate-400 flex-shrink-0 mt-0.5" />
                    <span>{cap}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
};

export default ModulePlaceholder;
