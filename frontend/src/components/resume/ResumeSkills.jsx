import React, { useState } from 'react';
import { Cpu, Search, Check, Copy } from 'lucide-react';
import Card from '../common/Card';

export const ResumeSkills = ({ skills = [] }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [copied, setCopied] = useState(false);

  const filteredSkills = skills.filter((skill) =>
    skill.toLowerCase().includes(searchTerm.toLowerCase().trim())
  );

  const handleCopySkills = () => {
    if (!skills.length) return;
    navigator.clipboard.writeText(skills.join(', '));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <Card
      title="Normalized Technical Skills"
      subtitle="Canonical technology skills identified and normalized from resume text"
      action={
        skills.length > 0 && (
          <div className="flex items-center gap-2">
            <button
              onClick={handleCopySkills}
              className="inline-flex items-center gap-1.5 px-2.5 py-1 text-xs font-medium text-slate-600 hover:text-indigo-600 bg-slate-50 hover:bg-indigo-50 border border-slate-200 rounded-lg transition-colors"
              title="Copy all skills as comma-separated list"
            >
              {copied ? (
                <>
                  <Check className="w-3.5 h-3.5 text-emerald-600" />
                  Copied
                </>
              ) : (
                <>
                  <Copy className="w-3.5 h-3.5" />
                  Copy All
                </>
              )}
            </button>
            <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-indigo-50 text-indigo-700 border border-indigo-100">
              {skills.length} skills
            </span>
          </div>
        )
      }
    >
      {skills.length > 0 ? (
        <div className="space-y-4">
          {skills.length > 6 && (
            <div className="relative">
              <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                placeholder="Filter extracted skills..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-9 pr-4 py-2 text-xs rounded-lg border border-slate-200 bg-slate-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all text-slate-800"
              />
            </div>
          )}

          {filteredSkills.length > 0 ? (
            <div className="flex flex-wrap gap-2">
              {filteredSkills.map((skill, idx) => (
                <span
                  key={`${skill}-${idx}`}
                  className="inline-flex items-center gap-1.5 px-3 py-1 rounded-lg text-xs font-medium bg-slate-50 text-slate-800 border border-slate-200 hover:border-indigo-300 hover:bg-indigo-50/50 hover:text-indigo-700 transition-all shadow-2xs"
                >
                  <Cpu className="w-3 h-3 text-indigo-500" />
                  {skill}
                </span>
              ))}
            </div>
          ) : (
            <p className="text-xs text-slate-500 py-3 text-center">
              No skills match &quot;{searchTerm}&quot;.
            </p>
          )}
        </div>
      ) : (
        <div className="text-center py-6 text-slate-500">
          <Cpu className="w-8 h-8 mx-auto text-slate-300 mb-2" />
          <p className="text-xs">No technical skills detected in the provided resume text.</p>
        </div>
      )}
    </Card>
  );
};

export default ResumeSkills;
