import React from 'react';
import { GraduationCap, Calendar, BookOpen } from 'lucide-react';
import Card from '../common/Card';

export const ResumeEducation = ({ education = [] }) => {
  return (
    <Card
      title="Educational Qualifications"
      subtitle="Degrees, diplomas, and academic credentials detected from resume"
      action={
        <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-violet-50 text-violet-700 border border-violet-100">
          {education.length} {education.length === 1 ? 'credential' : 'credentials'}
        </span>
      }
    >
      {education.length > 0 ? (
        <div className="space-y-4">
          {education.map((item, idx) => {
            const hasYears = item.start_year || item.end_year;
            const yearStr = [item.start_year, item.end_year].filter(Boolean).join(' - ');

            return (
              <div
                key={idx}
                className="p-4 rounded-xl border border-slate-200 bg-white hover:border-slate-300 transition-colors space-y-2"
              >
                <div className="flex items-start justify-between flex-wrap gap-2">
                  <div className="space-y-1">
                    <h4 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                      <GraduationCap className="w-4 h-4 text-violet-600 flex-shrink-0" />
                      {item.institution}
                    </h4>

                    {(item.degree || item.field_of_study) && (
                      <div className="flex items-center gap-2 pl-6 flex-wrap">
                        {item.degree && (
                          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-md text-xs font-semibold bg-violet-50 text-violet-700 border border-violet-200">
                            {item.degree}
                          </span>
                        )}
                        {item.field_of_study && (
                          <span className="inline-flex items-center gap-1 text-xs text-slate-600">
                            <BookOpen className="w-3.5 h-3.5 text-slate-400" />
                            {item.field_of_study}
                          </span>
                        )}
                      </div>
                    )}
                  </div>

                  {hasYears && (
                    <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-medium bg-slate-100 text-slate-700 border border-slate-200">
                      <Calendar className="w-3 h-3 text-slate-500" />
                      {yearStr}
                    </span>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      ) : (
        <div className="text-center py-6 text-slate-500">
          <GraduationCap className="w-8 h-8 mx-auto text-slate-300 mb-2" />
          <p className="text-xs">No formal educational credentials parsed from resume text.</p>
        </div>
      )}
    </Card>
  );
};

export default ResumeEducation;
