import React, { useState } from 'react';
import Card from '../common/Card';
import StatusBadge from '../common/StatusBadge';
import {
  ShieldCheck,
  ShieldAlert,
  HelpCircle,
  Search,
  GitBranch,
  FileText,
  CheckCheck,
  Info,
  FolderGit2
} from 'lucide-react';

export const SkillEvidenceOverview = ({ skills = [] }) => {
  const [selectedTab, setSelectedTab] = useState('ALL'); // 'ALL' | 'STRONG' | 'MODERATE' | 'NONE_DETECTED'
  const [searchTerm, setSearchTerm] = useState('');

  // Calculate real deterministic counts
  const strongSkills = skills.filter((s) => s.evidence_status === 'STRONG');
  const moderateSkills = skills.filter((s) => s.evidence_status === 'MODERATE');
  const noneDetectedSkills = skills.filter((s) => s.evidence_status === 'NONE_DETECTED');

  const filteredSkills = skills
    .filter((s) => {
      if (selectedTab === 'ALL') return true;
      return s.evidence_status === selectedTab;
    })
    .filter((s) =>
      s.skill.toLowerCase().includes(searchTerm.toLowerCase().trim())
    );

  const renderSourceBadge = (sources = []) => {
    const hasGithub = sources.includes('github');
    const hasResume = sources.includes('resume');

    if (hasGithub && hasResume) {
      return (
        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-medium bg-purple-50 text-purple-700 border border-purple-200">
          <CheckCheck className="w-3 h-3" />
          <span>GitHub & Resume</span>
        </span>
      );
    }
    if (hasGithub) {
      return (
        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-medium bg-emerald-50 text-emerald-700 border border-emerald-200">
          <GitBranch className="w-3 h-3" />
          <span>GitHub Only</span>
        </span>
      );
    }
    if (hasResume) {
      return (
        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-medium bg-sky-50 text-sky-700 border border-sky-200">
          <FileText className="w-3 h-3" />
          <span>Resume Only</span>
        </span>
      );
    }
    return null;
  };

  const renderEvidenceStatus = (status) => {
    switch (status) {
      case 'STRONG':
        return <StatusBadge status="success" text="Strong Evidence" />;
      case 'MODERATE':
        return <StatusBadge status="info" text="Moderate Evidence" />;
      case 'NONE_DETECTED':
      default:
        return <StatusBadge status="neutral" text="None Detected" />;
    }
  };

  return (
    <Card
      title={`Unified Skill Inventory & Evidence Grounding (${skills.length})`}
      subtitle="Canonical skills mapped to their detection sources and repository verification levels."
      action={
        <div className="relative">
          <Search className="w-3.5 h-3.5 absolute left-2.5 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            placeholder="Search skill..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="text-xs pl-8 pr-2.5 py-1.5 rounded-lg border border-slate-200 bg-slate-50 focus:bg-white focus:outline-none focus:ring-1 focus:ring-indigo-500 w-44"
          />
        </div>
      }
    >
      <div className="space-y-4">
        {/* Evidence Status Filter Pills */}
        <div className="flex flex-wrap items-center gap-2 border-b border-slate-100 pb-3">
          <button
            onClick={() => setSelectedTab('ALL')}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
              selectedTab === 'ALL'
                ? 'bg-slate-900 text-white'
                : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
            }`}
          >
            All Skills ({skills.length})
          </button>
          <button
            onClick={() => setSelectedTab('STRONG')}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors flex items-center gap-1.5 ${
              selectedTab === 'STRONG'
                ? 'bg-emerald-600 text-white'
                : 'bg-emerald-50 text-emerald-700 hover:bg-emerald-100 border border-emerald-200'
            }`}
          >
            <ShieldCheck className="w-3.5 h-3.5" />
            <span>Strong ({strongSkills.length})</span>
          </button>
          <button
            onClick={() => setSelectedTab('MODERATE')}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors flex items-center gap-1.5 ${
              selectedTab === 'MODERATE'
                ? 'bg-sky-600 text-white'
                : 'bg-sky-50 text-sky-700 hover:bg-sky-100 border border-sky-200'
            }`}
          >
            <ShieldAlert className="w-3.5 h-3.5" />
            <span>Moderate ({moderateSkills.length})</span>
          </button>
          <button
            onClick={() => setSelectedTab('NONE_DETECTED')}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors flex items-center gap-1.5 ${
              selectedTab === 'NONE_DETECTED'
                ? 'bg-slate-700 text-white'
                : 'bg-slate-100 text-slate-700 hover:bg-slate-200 border border-slate-200'
            }`}
          >
            <HelpCircle className="w-3.5 h-3.5" />
            <span>None Detected ({noneDetectedSkills.length})</span>
          </button>
        </div>

        {/* Mandatory Explanatory Note */}
        <div className="flex items-start gap-2.5 p-3 rounded-lg bg-amber-50/70 border border-amber-200 text-xs text-amber-900 leading-relaxed">
          <Info className="w-4 h-4 text-amber-600 flex-shrink-0 mt-0.5" />
          <div>
            <strong>Evaluation Note:</strong> <code className="font-mono text-amber-800">NONE_DETECTED</code> means no analyzed GitHub evidence was found in the candidate's public repositories; it must <strong>not</strong> be presented as proof that the developer lacks that skill.
          </div>
        </div>

        {/* Skills Table / List */}
        {filteredSkills.length === 0 ? (
          <div className="text-center py-8 text-xs text-slate-400">
            No skills match the current filter or search criteria.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-slate-200 text-[11px] font-semibold uppercase tracking-wider text-slate-500">
                  <th className="py-2.5 px-3">Canonical Skill</th>
                  <th className="py-2.5 px-3">Information Source</th>
                  <th className="py-2.5 px-3">Evidence Grounding</th>
                  <th className="py-2.5 px-3">Supporting Repositories</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-xs text-slate-700">
                {filteredSkills.map((item) => (
                  <tr key={item.skill} className="hover:bg-slate-50/80 transition-colors">
                    <td className="py-2.5 px-3 font-semibold text-slate-900">
                      {item.skill}
                    </td>
                    <td className="py-2.5 px-3">
                      {renderSourceBadge(item.sources)}
                    </td>
                    <td className="py-2.5 px-3">
                      {renderEvidenceStatus(item.evidence_status)}
                    </td>
                    <td className="py-2.5 px-3 text-slate-500">
                      {item.supporting_repositories && item.supporting_repositories.length > 0 ? (
                        <div className="flex flex-wrap gap-1">
                          {item.supporting_repositories.map((repo, idx) => (
                            <span
                              key={idx}
                              className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded bg-slate-100 text-[11px] font-mono text-slate-700 border border-slate-200"
                              title={repo.name || repo.full_name}
                            >
                              <FolderGit2 className="w-3 h-3 text-slate-400" />
                              <span className="truncate max-w-[120px]">
                                {repo.name || repo.full_name}
                              </span>
                            </span>
                          ))}
                        </div>
                      ) : (
                        <span className="text-slate-400 italic text-[11px]">
                          No public repos linked
                        </span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </Card>
  );
};

export default SkillEvidenceOverview;
