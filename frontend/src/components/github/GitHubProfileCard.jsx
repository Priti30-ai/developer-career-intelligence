import React, { useState } from 'react';
import StatusBadge from '../common/StatusBadge';
import {
  Github,
  ExternalLink,
  Users,
  FolderGit2,
  Calendar,
  UserCheck
} from 'lucide-react';

export const GitHubProfileCard = ({ profile }) => {
  const [imageError, setImageError] = useState(false);

  if (!profile) return null;

  const {
    login,
    name,
    bio,
    avatar_url,
    html_url,
    public_repos,
    followers,
    following,
    created_at,
  } = profile;

  const formattedDate = created_at
    ? new Date(created_at).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
      })
    : 'Unknown';

  return (
    <div className="bg-white border border-slate-200 rounded-xl p-6 sm:p-7 shadow-sm">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
        {/* Left: Avatar & Identity details */}
        <div className="flex items-start gap-4">
          <div className="w-16 h-16 sm:w-20 sm:h-20 rounded-2xl bg-slate-900 border border-slate-200 overflow-hidden flex items-center justify-center flex-shrink-0 shadow-sm">
            {avatar_url && !imageError ? (
              <img
                src={avatar_url}
                alt={`${login} avatar`}
                onError={() => setImageError(true)}
                className="w-full h-full object-cover"
              />
            ) : (
              <Github className="w-10 h-10 text-white" />
            )}
          </div>

          <div className="min-w-0 flex-1">
            <div className="flex items-center gap-2.5 flex-wrap">
              <h2 className="text-xl sm:text-2xl font-bold text-slate-900 tracking-tight truncate">
                {name || login}
              </h2>
              <span className="text-xs font-mono text-slate-500 bg-slate-100 px-2 py-0.5 rounded border border-slate-200">
                @{login}
              </span>
              <StatusBadge status="success" text="Verified Profile" />
            </div>

            {bio ? (
              <p className="text-xs sm:text-sm text-slate-600 mt-1.5 line-clamp-2 max-w-2xl leading-relaxed">
                {bio}
              </p>
            ) : (
              <p className="text-xs text-slate-400 italic mt-1.5">
                No bio provided by this developer.
              </p>
            )}

            <div className="mt-3 flex items-center gap-4 flex-wrap text-xs text-slate-500">
              {html_url && (
                <a
                  href={html_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1 text-indigo-600 hover:text-indigo-800 font-medium"
                >
                  <span>github.com/{login}</span>
                  <ExternalLink className="w-3.5 h-3.5" />
                </a>
              )}
              <div className="flex items-center gap-1.5 text-slate-500">
                <Calendar className="w-3.5 h-3.5 text-slate-400" />
                <span>Joined {formattedDate}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Right: Profile Counter Highlights */}
        <div className="flex items-center gap-3 sm:gap-6 border-t md:border-t-0 md:border-l border-slate-200 pt-4 md:pt-0 md:pl-6 text-xs text-slate-600 flex-shrink-0">
          <div className="text-center md:text-left">
            <span className="text-[11px] uppercase tracking-wider text-slate-400 font-semibold block">
              Public Repos
            </span>
            <span className="text-lg font-bold text-slate-900 font-mono">
              {public_repos ?? 0}
            </span>
          </div>

          <div className="text-center md:text-left">
            <span className="text-[11px] uppercase tracking-wider text-slate-400 font-semibold block">
              Followers
            </span>
            <span className="text-lg font-bold text-slate-900 font-mono">
              {followers ?? 0}
            </span>
          </div>

          <div className="text-center md:text-left">
            <span className="text-[11px] uppercase tracking-wider text-slate-400 font-semibold block">
              Following
            </span>
            <span className="text-lg font-bold text-slate-900 font-mono">
              {following ?? 0}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default GitHubProfileCard;
