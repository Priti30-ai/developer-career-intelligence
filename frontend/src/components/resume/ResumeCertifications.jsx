import React from 'react';
import { Award, CheckCircle } from 'lucide-react';
import Card from '../common/Card';

export const ResumeCertifications = ({ certifications = [] }) => {
  return (
    <Card
      title="Certifications & Licenses"
      subtitle="Industry credentials and verified learning achievements"
      action={
        <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-50 text-amber-700 border border-amber-100">
          {certifications.length} {certifications.length === 1 ? 'credential' : 'credentials'}
        </span>
      }
    >
      {certifications.length > 0 ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {certifications.map((cert, idx) => (
            <div
              key={idx}
              className="p-3.5 rounded-xl border border-slate-200 bg-white hover:border-slate-300 transition-colors flex items-start gap-3"
            >
              <div className="p-2 rounded-lg bg-amber-50 text-amber-600 flex-shrink-0 mt-0.5">
                <Award className="w-4 h-4" />
              </div>
              <div className="min-w-0">
                <p className="text-xs sm:text-sm font-semibold text-slate-800 leading-snug">
                  {cert}
                </p>
                <div className="flex items-center gap-1 mt-1 text-[11px] text-emerald-600 font-medium">
                  <CheckCircle className="w-3 h-3" />
                  Identified in resume
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-6 text-slate-500">
          <Award className="w-8 h-8 mx-auto text-slate-300 mb-2" />
          <p className="text-xs">No certifications section or items detected in resume text.</p>
        </div>
      )}
    </Card>
  );
};

export default ResumeCertifications;
