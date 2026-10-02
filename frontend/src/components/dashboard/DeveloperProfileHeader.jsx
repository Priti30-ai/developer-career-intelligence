import React from 'react';
import Card from '../common/Card';
import StatusBadge from '../common/StatusBadge';
import { Github, FolderGit2, Cpu, Sparkles, ExternalLink } from 'lucide-react';

export const DeveloperProfileHeader = ({ profile }) => {
  if (!profile) return null;

  const { developer_id, github, summary } = profile;
  const username = github?.username || developer_id;
  const reposCount = github?.repositories_analyzed ?? 0;
  const techCount = github?.technologies_detected?.length ?? 0;
  const totalSkills = summary?.total_skills ?? 0;

  return (
    <div className="bg-white border border-slate-200 rounded-xl p-6 sm:p-7 shadow-sm">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-5">
        <div className="flex items-start gap-4">
          <div className="w-14 h-14 rounded-xl bg-slate-900 text-white flex items-center justify-center flex-shrink-0 shadow-md">
            <Github className="w-8 h-8" />
          </div>
          <div>
            <div className="flex items-center gap-2.5 flex-wrap">
              <h2 className="text-xl sm:text-2xl font-bold text-slate-900 tracking-tight">
                {username}
              </h2>
              <StatusBadge status="success" text="Profile Synthesized" />
              <a
                href={`https://github.com/${username}`}
                target="_blank"
                rel="noreferrer"
                className="inline-flex items-center gap-1 text-xs text-indigo-600 hover:text-indigo-800 font-medium"
              >
                <span>GitHub Profile</span>
                <ExternalLink className="w-3 h-3" />
              </a>
            </div>
            <p className="text-xs sm:text-sm text-slate-500 mt-1">
              Unified engineering intelligence profile synthesized from public repositories and candidate documentation.
            </p>
          </div>
        </div>

        {/* Quick Highlights Pill Row */}
        <div className="flex items-center gap-3 sm:gap-4 flex-wrap border-t md:border-t-0 md:border-l border-slate-200 pt-4 md:pt-0 md:pl-6 text-xs text-slate-600">
          <div className="flex items-center gap-2">
            <FolderGit2 className="w-4 h-4 text-indigo-600" />
            <span>
              <strong className="text-slate-900 font-semibold">{reposCount}</strong> Repos Analyzed
            </span>
          </div>
          <div className="flex items-center gap-2">
            <Cpu className="w-4 h-4 text-emerald-600" />
            <span>
              <strong className="text-slate-900 font-semibold">{techCount}</strong> Tech Detected
            </span>
          </div>
          <div className="flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-purple-600" />
            <span>
              <strong className="text-slate-900 font-semibold">{totalSkills}</strong> Total Skills
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DeveloperProfileHeader;
