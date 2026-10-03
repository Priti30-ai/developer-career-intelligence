import React, { useState, useMemo } from 'react';
import Card from '../common/Card';
import Button from '../common/Button';
import {
  FolderGit2,
  Star,
  GitFork,
  ExternalLink,
  Search,
  ChevronLeft,
  ChevronRight,
  ChevronDown,
  ChevronUp,
  Calendar,
  Tag,
  FileCode2,
  Cpu,
  ShieldCheck,
  ShieldAlert,
  Shield,
  LayoutTemplate,
  AlertTriangle,
  Archive,
  PackageOpen,
} from 'lucide-react';

// ─────────────────────────────────────────────────────────────────────────────
// EVIDENCE BADGE
// ─────────────────────────────────────────────────────────────────────────────
const EVIDENCE_ICONS = {
  STRONG: ShieldCheck,
  MODERATE: ShieldAlert,
  WEAK: Shield,
};

const EVIDENCE_COLORS = {
  STRONG: 'text-emerald-700 bg-emerald-50 border-emerald-200',
  MODERATE: 'text-amber-700 bg-amber-50 border-amber-200',
  WEAK: 'text-slate-500 bg-slate-50 border-slate-200',
};

const SOURCE_TYPE_LABELS = {
  DEPENDENCY_MANIFEST: 'Manifest',
  SOURCE_LANGUAGE: 'Language',
  REPOSITORY_TOPIC: 'Topic',
  PROJECT_STRUCTURE: 'Structure',
  CONFIGURATION: 'Config',
  README: 'README',
};

const EvidenceBadge = ({ strength }) => {
  const Icon = EVIDENCE_ICONS[strength] || Shield;
  const color = EVIDENCE_COLORS[strength] || EVIDENCE_COLORS.WEAK;
  return (
    <span
      className={`inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[10px] font-semibold border ${color}`}
    >
      <Icon className="w-2.5 h-2.5" />
      {strength}
    </span>
  );
};

// ─────────────────────────────────────────────────────────────────────────────
// EXPANDED ROW DETAIL
// ─────────────────────────────────────────────────────────────────────────────
const ExpandedRepoDetail = ({ repo }) => {
  const hasManifests = repo.manifest_files?.length > 0;
  const hasEvidence = repo.evidence?.length > 0;
  const hasArchitecture = repo.architecture_signals?.length > 0;
  const hasTechnologies = repo.technologies?.length > 0;
  const hasLanguages = repo.languages?.length > 0;
  const hasTopics = repo.topics?.length > 0;

  const formatDate = (iso) => {
    if (!iso) return '—';
    try {
      return new Date(iso).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
      });
    } catch {
      return iso;
    }
  };

  return (
    <div className="px-4 pb-4 pt-2 bg-slate-50/60 border-t border-slate-100">
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-3">

        {/* PROJECT INFORMATION */}
        <div className="rounded-lg border border-slate-200 bg-white p-3 space-y-2">
          <div className="flex items-center gap-1.5 pb-1.5 border-b border-slate-100">
            <LayoutTemplate className="w-3.5 h-3.5 text-indigo-600" />
            <span className="text-xs font-semibold text-slate-800">Project Information</span>
          </div>

          <div className="space-y-1.5 text-[11px]">
            {repo.project_type && (
              <div className="flex justify-between items-center">
                <span className="text-slate-500">Type</span>
                <span className="font-mono font-semibold text-indigo-700 bg-indigo-50 border border-indigo-100 px-1.5 py-0.5 rounded text-[10px]">
                  {repo.project_type}
                </span>
              </div>
            )}
            {repo.default_branch && (
              <div className="flex justify-between items-center">
                <span className="text-slate-500">Default Branch</span>
                <span className="font-mono text-slate-700">{repo.default_branch}</span>
              </div>
            )}
            {repo.created_at && (
              <div className="flex justify-between items-center">
                <span className="text-slate-500">Created</span>
                <span className="text-slate-700">{formatDate(repo.created_at)}</span>
              </div>
            )}
            {repo.pushed_at && (
              <div className="flex justify-between items-center">
                <span className="text-slate-500">Last Push</span>
                <span className="text-slate-700">{formatDate(repo.pushed_at)}</span>
              </div>
            )}
            {repo.watchers_count !== undefined && (
              <div className="flex justify-between items-center">
                <span className="text-slate-500">Watchers</span>
                <span className="font-mono text-slate-700">{repo.watchers_count}</span>
              </div>
            )}
            <div className="flex justify-between items-center">
              <span className="text-slate-500">Status</span>
              <div className="flex items-center gap-1">
                {repo.is_archived && (
                  <span className="flex items-center gap-0.5 text-[10px] text-amber-700 bg-amber-50 border border-amber-200 px-1.5 py-0.5 rounded font-semibold">
                    <Archive className="w-2.5 h-2.5" /> Archived
                  </span>
                )}
                {repo.is_fork && (
                  <span className="flex items-center gap-0.5 text-[10px] text-sky-700 bg-sky-50 border border-sky-200 px-1.5 py-0.5 rounded font-semibold">
                    <GitFork className="w-2.5 h-2.5" /> Fork
                  </span>
                )}
                {repo.is_empty && (
                  <span className="flex items-center gap-0.5 text-[10px] text-slate-500 bg-slate-50 border border-slate-200 px-1.5 py-0.5 rounded font-semibold">
                    <PackageOpen className="w-2.5 h-2.5" /> Empty
                  </span>
                )}
                {repo.is_partial && (
                  <span className="flex items-center gap-0.5 text-[10px] text-orange-700 bg-orange-50 border border-orange-200 px-1.5 py-0.5 rounded font-semibold">
                    <AlertTriangle className="w-2.5 h-2.5" /> Partial
                  </span>
                )}
                {!repo.is_archived && !repo.is_fork && !repo.is_empty && !repo.is_partial && (
                  <span className="text-[10px] text-emerald-700 font-semibold">Active</span>
                )}
              </div>
            </div>
          </div>

          {hasTopics && (
            <div className="pt-1.5 border-t border-slate-100">
              <span className="text-[10px] text-slate-400 uppercase tracking-wider font-semibold block mb-1.5">
                Topics
              </span>
              <div className="flex flex-wrap gap-1">
                {repo.topics.map((t) => (
                  <span
                    key={t}
                    className="px-1.5 py-0.5 rounded bg-indigo-50 text-indigo-700 text-[10px] font-mono border border-indigo-100"
                  >
                    #{t}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* ARCHITECTURE & LANGUAGES */}
        <div className="rounded-lg border border-slate-200 bg-white p-3 space-y-2">
          <div className="flex items-center gap-1.5 pb-1.5 border-b border-slate-100">
            <Cpu className="w-3.5 h-3.5 text-purple-600" />
            <span className="text-xs font-semibold text-slate-800">Architecture & Languages</span>
          </div>

          {hasLanguages && (
            <div className="space-y-1">
              <span className="text-[10px] text-slate-400 uppercase tracking-wider font-semibold block">
                All Languages
              </span>
              <div className="flex flex-wrap gap-1">
                {repo.languages.map((lang) => (
                  <span
                    key={lang}
                    className={`px-2 py-0.5 rounded text-[11px] font-mono border ${
                      lang === repo.primary_language
                        ? 'bg-purple-50 text-purple-800 border-purple-200 font-semibold'
                        : 'bg-slate-50 text-slate-700 border-slate-200'
                    }`}
                  >
                    {lang}
                    {lang === repo.primary_language && (
                      <span className="ml-1 text-[9px] text-purple-500">primary</span>
                    )}
                  </span>
                ))}
              </div>
            </div>
          )}

          {hasArchitecture ? (
            <div className="space-y-1">
              <span className="text-[10px] text-slate-400 uppercase tracking-wider font-semibold block">
                Architecture Signals
              </span>
              <div className="space-y-1">
                {repo.architecture_signals.map((sig, idx) => (
                  <div
                    key={idx}
                    className="text-[11px] flex items-start gap-1.5 py-0.5"
                  >
                    <span className="mt-0.5 flex-shrink-0 w-1.5 h-1.5 rounded-full bg-purple-400" />
                    <div>
                      <span className="font-medium text-slate-800">
                        {sig.signal_type || sig.type || sig.name || 'Signal'}
                      </span>
                      {sig.description && (
                        <span className="text-slate-500 ml-1">— {sig.description}</span>
                      )}
                      {sig.path && (
                        <span className="font-mono text-[10px] text-slate-400 ml-1">
                          ({sig.path})
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <p className="text-[11px] text-slate-400 italic">No architecture signals detected.</p>
          )}
        </div>

        {/* MANIFEST FILES & TECHNOLOGIES */}
        <div className="rounded-lg border border-slate-200 bg-white p-3 space-y-2">
          <div className="flex items-center gap-1.5 pb-1.5 border-b border-slate-100">
            <FileCode2 className="w-3.5 h-3.5 text-teal-600" />
            <span className="text-xs font-semibold text-slate-800">Manifests & Technologies</span>
          </div>

          {hasManifests ? (
            <div className="space-y-1">
              <span className="text-[10px] text-slate-400 uppercase tracking-wider font-semibold block">
                Manifest Files ({repo.manifest_files.length})
              </span>
              <div className="flex flex-col gap-0.5 max-h-24 overflow-y-auto">
                {repo.manifest_files.map((f) => (
                  <span key={f} className="font-mono text-[11px] text-teal-800 bg-teal-50 border border-teal-100 px-2 py-0.5 rounded">
                    {f}
                  </span>
                ))}
              </div>
            </div>
          ) : (
            <p className="text-[11px] text-slate-400 italic">No manifest files identified.</p>
          )}

          {hasTechnologies && (
            <div className="space-y-1 pt-1.5 border-t border-slate-100">
              <span className="text-[10px] text-slate-400 uppercase tracking-wider font-semibold block">
                Detected Technologies ({repo.technologies.length})
              </span>
              <div className="flex flex-wrap gap-1">
                {repo.technologies.map((tech) => (
                  <span
                    key={tech}
                    className="px-1.5 py-0.5 rounded bg-teal-50 text-teal-800 text-[10px] font-mono border border-teal-100"
                  >
                    {tech}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* EVIDENCE SIGNALS */}
        <div className="rounded-lg border border-slate-200 bg-white p-3 space-y-2">
          <div className="flex items-center gap-1.5 pb-1.5 border-b border-slate-100">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
            <span className="text-xs font-semibold text-slate-800">
              Evidence Signals ({repo.evidence?.length ?? 0})
            </span>
          </div>

          {hasEvidence ? (
            <div className="flex flex-col gap-1.5 max-h-48 overflow-y-auto">
              {repo.evidence.map((ev, idx) => (
                <div
                  key={idx}
                  className="text-[11px] p-1.5 rounded border border-slate-100 bg-slate-50 space-y-0.5"
                >
                  <div className="flex items-center justify-between flex-wrap gap-1">
                    <span className="font-semibold text-slate-800">{ev.technology}</span>
                    <div className="flex items-center gap-1 flex-wrap">
                      <EvidenceBadge strength={ev.strength} />
                      <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-100 text-slate-600 border border-slate-200 font-mono">
                        {SOURCE_TYPE_LABELS[ev.source_type] || ev.source_type}
                      </span>
                    </div>
                  </div>
                  {ev.path && (
                    <div className="font-mono text-[10px] text-slate-400 truncate" title={ev.path}>
                      {ev.path}
                    </div>
                  )}
                  {ev.reason && (
                    <div className="text-[10px] text-slate-500 leading-snug">{ev.reason}</div>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <p className="text-[11px] text-slate-400 italic">No evidence signals recorded for this repository.</p>
          )}

          {repo.warnings?.length > 0 && (
            <div className="pt-1.5 border-t border-slate-100 space-y-1">
              <span className="text-[10px] text-slate-400 uppercase tracking-wider font-semibold block">
                Warnings
              </span>
              {repo.warnings.map((w, i) => (
                <div
                  key={i}
                  className="flex items-start gap-1 text-[10px] text-orange-700 bg-orange-50 border border-orange-100 px-2 py-1 rounded"
                >
                  <AlertTriangle className="w-2.5 h-2.5 flex-shrink-0 mt-0.5" />
                  <span>{w}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

// ─────────────────────────────────────────────────────────────────────────────
// REPOSITORY TABLE
// ─────────────────────────────────────────────────────────────────────────────
export const RepositoryTable = ({ repos = [] }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [expandedRepo, setExpandedRepo] = useState(null);
  const pageSize = 10;

  const filteredRepos = useMemo(() => {
    const term = searchTerm.toLowerCase().trim();
    if (!term) return repos;
    return repos.filter(
      (r) =>
        r.name?.toLowerCase().includes(term) ||
        r.full_name?.toLowerCase().includes(term) ||
        r.description?.toLowerCase().includes(term) ||
        r.language?.toLowerCase().includes(term) ||
        r.primary_language?.toLowerCase().includes(term) ||
        (r.topics && r.topics.some((t) => t.toLowerCase().includes(term))) ||
        (r.technologies && r.technologies.some((t) => t.toLowerCase().includes(term)))
    );
  }, [repos, searchTerm]);

  const handleSearchChange = (e) => {
    setSearchTerm(e.target.value);
    setCurrentPage(1);
    setExpandedRepo(null);
  };

  const totalPages = Math.ceil(filteredRepos.length / pageSize) || 1;
  const paginatedRepos = useMemo(() => {
    const start = (currentPage - 1) * pageSize;
    return filteredRepos.slice(start, start + pageSize);
  }, [filteredRepos, currentPage, pageSize]);

  const formatDate = (isoString) => {
    if (!isoString) return '—';
    try {
      return new Date(isoString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
      });
    } catch {
      return isoString;
    }
  };

  const toggleExpand = (repoKey) => {
    setExpandedRepo((prev) => (prev === repoKey ? null : repoKey));
  };

  const hasInspectionData = (repo) =>
    repo.technologies?.length > 0 ||
    repo.manifest_files?.length > 0 ||
    repo.evidence?.length > 0 ||
    repo.architecture_signals?.length > 0 ||
    repo.project_type;

  return (
    <Card
      title={`Repository Catalog (${repos.length})`}
      subtitle="Public repository archive retrieved from GitHub. Click a row to inspect project details, architecture signals, manifests, and evidence."
      action={
        <div className="relative">
          <Search className="w-3.5 h-3.5 absolute left-2.5 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            placeholder="Search repos, topics, tech..."
            value={searchTerm}
            onChange={handleSearchChange}
            className="text-xs pl-8 pr-2.5 py-1.5 rounded-lg border border-slate-200 bg-slate-50 focus:bg-white focus:outline-none focus:ring-1 focus:ring-indigo-500 w-44 sm:w-64"
          />
        </div>
      }
    >
      <div className="space-y-3">
        {filteredRepos.length === 0 ? (
          <div className="text-center py-10 text-xs text-slate-400">
            No repositories found matching "{searchTerm}".
          </div>
        ) : (
          <div className="overflow-x-auto border border-slate-200 rounded-lg">
            <table className="w-full text-left border-collapse text-xs">
              <thead className="bg-slate-50 border-b border-slate-200 text-slate-500 uppercase tracking-wider font-semibold">
                <tr>
                  <th className="py-2.5 px-3 w-6" />
                  <th className="py-2.5 px-3">Repository</th>
                  <th className="py-2.5 px-3 min-w-[160px]">Description</th>
                  <th className="py-2.5 px-3">Language</th>
                  <th className="py-2.5 px-3 text-center">Stars</th>
                  <th className="py-2.5 px-3 text-center">Forks</th>
                  <th className="py-2.5 px-3 min-w-[120px]">Topics</th>
                  <th className="py-2.5 px-3">Updated</th>
                  <th className="py-2.5 px-3 text-right">GitHub</th>
                </tr>
              </thead>
              <tbody className="text-slate-700">
                {paginatedRepos.map((repo) => {
                  const repoKey = repo.full_name || repo.name;
                  const isExpanded = expandedRepo === repoKey;
                  const hasDetails = hasInspectionData(repo);

                  return (
                    <React.Fragment key={repoKey}>
                      <tr
                        className={`border-b border-slate-100 transition-colors ${
                          hasDetails
                            ? 'cursor-pointer hover:bg-indigo-50/40'
                            : 'hover:bg-slate-50/80'
                        } ${isExpanded ? 'bg-indigo-50/30' : ''}`}
                        onClick={hasDetails ? () => toggleExpand(repoKey) : undefined}
                        title={hasDetails ? 'Click to expand repository details' : undefined}
                      >
                        {/* Expand toggle */}
                        <td className="py-2.5 px-3 w-6">
                          {hasDetails ? (
                            <span className="text-indigo-400">
                              {isExpanded ? (
                                <ChevronUp className="w-3.5 h-3.5" />
                              ) : (
                                <ChevronDown className="w-3.5 h-3.5" />
                              )}
                            </span>
                          ) : null}
                        </td>

                        <td className="py-2.5 px-3 font-semibold text-slate-900">
                          <div className="flex items-center gap-1.5">
                            <FolderGit2 className="w-3.5 h-3.5 text-indigo-600 flex-shrink-0" />
                            <span className="truncate max-w-[160px]" title={repo.full_name}>
                              {repo.name}
                            </span>
                            {repo.fork && (
                              <span className="text-[10px] px-1 rounded bg-slate-100 text-slate-500 font-normal">
                                fork
                              </span>
                            )}
                            {repo.is_archived && (
                              <span className="text-[10px] px-1 rounded bg-amber-50 text-amber-600 border border-amber-100 font-normal">
                                archived
                              </span>
                            )}
                          </div>
                        </td>

                        <td className="py-2.5 px-3 text-slate-600 max-w-xs">
                          {repo.description ? (
                            <span className="line-clamp-2" title={repo.description}>
                              {repo.description}
                            </span>
                          ) : (
                            <span className="text-slate-400 italic">No description</span>
                          )}
                        </td>

                        <td className="py-2.5 px-3 font-medium">
                          {(repo.primary_language || repo.language) ? (
                            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-slate-100 text-slate-700 font-mono text-[11px]">
                              {repo.primary_language || repo.language}
                            </span>
                          ) : (
                            <span className="text-slate-400">—</span>
                          )}
                        </td>

                        <td className="py-2.5 px-3 text-center font-mono">
                          <span className="inline-flex items-center gap-1 text-slate-700">
                            <Star className="w-3 h-3 text-amber-500 fill-amber-500" />
                            <span>{repo.stargazers_count ?? 0}</span>
                          </span>
                        </td>

                        <td className="py-2.5 px-3 text-center font-mono">
                          <span className="inline-flex items-center gap-1 text-slate-700">
                            <GitFork className="w-3 h-3 text-slate-400" />
                            <span>{repo.forks_count ?? 0}</span>
                          </span>
                        </td>

                        <td className="py-2.5 px-3">
                          {repo.topics && repo.topics.length > 0 ? (
                            <div className="flex flex-wrap gap-1 max-w-[180px]">
                              {repo.topics.slice(0, 3).map((topic) => (
                                <span
                                  key={topic}
                                  className="px-1.5 py-0.5 rounded bg-indigo-50 text-indigo-700 text-[10px] font-mono border border-indigo-100"
                                >
                                  #{topic}
                                </span>
                              ))}
                              {repo.topics.length > 3 && (
                                <span className="text-[10px] text-slate-400 font-mono">
                                  +{repo.topics.length - 3}
                                </span>
                              )}
                            </div>
                          ) : (
                            <span className="text-slate-400">—</span>
                          )}
                        </td>

                        <td className="py-2.5 px-3 text-slate-500 whitespace-nowrap text-[11px]">
                          {formatDate(repo.updated_at)}
                        </td>

                        <td
                          className="py-2.5 px-3 text-right"
                          onClick={(e) => e.stopPropagation()}
                        >
                          {repo.html_url && (
                            <a
                              href={repo.html_url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="inline-flex items-center gap-1 text-indigo-600 hover:text-indigo-800 p-1 rounded hover:bg-indigo-50 transition-colors"
                              title="View on GitHub"
                            >
                              <ExternalLink className="w-3.5 h-3.5" />
                            </a>
                          )}
                        </td>
                      </tr>

                      {/* EXPANDED DETAIL ROW */}
                      {isExpanded && (
                        <tr>
                          <td colSpan={9} className="p-0">
                            <ExpandedRepoDetail repo={repo} />
                          </td>
                        </tr>
                      )}
                    </React.Fragment>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}

        {/* Pagination Footer */}
        {filteredRepos.length > pageSize && (
          <div className="flex items-center justify-between pt-2 px-1 text-xs text-slate-500">
            <span>
              Showing {(currentPage - 1) * pageSize + 1} to{' '}
              {Math.min(currentPage * pageSize, filteredRepos.length)} of{' '}
              {filteredRepos.length} repositories
            </span>

            <div className="flex items-center gap-1">
              <Button
                variant="outline"
                size="sm"
                onClick={() => {
                  setCurrentPage((p) => Math.max(1, p - 1));
                  setExpandedRepo(null);
                }}
                disabled={currentPage === 1}
                icon={ChevronLeft}
              >
                Previous
              </Button>
              <span className="px-2 font-mono text-[11px]">
                {currentPage} / {totalPages}
              </span>
              <Button
                variant="outline"
                size="sm"
                onClick={() => {
                  setCurrentPage((p) => Math.min(totalPages, p + 1));
                  setExpandedRepo(null);
                }}
                disabled={currentPage === totalPages}
                icon={ChevronRight}
              >
                Next
              </Button>
            </div>
          </div>
        )}
      </div>
    </Card>
  );
};

export default RepositoryTable;
