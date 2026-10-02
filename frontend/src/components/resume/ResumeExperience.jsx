import React from 'react';
import { Briefcase, Calendar, Building2 } from 'lucide-react';
import Card from '../common/Card';

export const ResumeExperience = ({ experience = [] }) => {
  return (
    <Card
      title="Professional Experience & Internships"
      subtitle="Structured work history detected from experience sections"
      action={
        <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-sky-50 text-sky-700 border border-sky-100">
          {experience.length} {experience.length === 1 ? 'position' : 'positions'}
        </span>
      }
    >
      {experience.length > 0 ? (
        <div className="space-y-4">
          {experience.map((item, idx) => {
            const hasDates = item.start_date || item.end_date;
            const dateStr = [item.start_date, item.end_date].filter(Boolean).join(' - ');

            return (
              <div
                key={idx}
                className="p-4 rounded-xl border border-slate-200 bg-white hover:border-slate-300 transition-colors space-y-2.5"
              >
                <div className="flex items-start justify-between flex-wrap gap-2">
                  <div className="space-y-0.5">
                    <h4 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                      <Briefcase className="w-4 h-4 text-sky-600 flex-shrink-0" />
                      {item.role || 'Unspecified Role'}
                    </h4>
                    {item.company && (
                      <p className="text-xs font-medium text-slate-600 flex items-center gap-1.5 pl-6">
                        <Building2 className="w-3.5 h-3.5 text-slate-400" />
                        {item.company}
                      </p>
                    )}
                  </div>

                  {hasDates && (
                    <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-medium bg-slate-100 text-slate-700 border border-slate-200">
                      <Calendar className="w-3 h-3 text-slate-500" />
                      {dateStr}
                    </span>
                  )}
                </div>

                {item.description && (
                  <p className="text-xs text-slate-600 leading-relaxed pl-6 whitespace-pre-line">
                    {item.description}
                  </p>
                )}
              </div>
            );
          })}
        </div>
      ) : (
        <div className="text-center py-6 text-slate-500">
          <Briefcase className="w-8 h-8 mx-auto text-slate-300 mb-2" />
          <p className="text-xs">No formal professional experience or internship entries parsed.</p>
        </div>
      )}
    </Card>
  );
};

export default ResumeExperience;
