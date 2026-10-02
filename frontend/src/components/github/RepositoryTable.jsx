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
  Calendar,
  Tag
} from 'lucide-react';

export const RepositoryTable = ({ repos = [] }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const pageSize = 10;

  // Filter repositories by search term
  const filteredRepos = useMemo(() => {
    const term = searchTerm.toLowerCase().trim();
    if (!term) return repos;
    return repos.filter(
      (r) =>
        r.name?.toLowerCase().includes(term) ||
        r.full_name?.toLowerCase().includes(term) ||
        r.description?.toLowerCase().includes(term) ||
        r.language?.toLowerCase().includes(term) ||
        (r.topics && r.topics.some((t) => t.toLowerCase().includes(term)))
    );
  }, [repos, searchTerm]);

  // Reset to first page whenever search term changes
  const handleSearchChange = (e) => {
    setSearchTerm(e.target.value);
    setCurrentPage(1);
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

  return (
    <Card
      title={`Repository Catalog (${repos.length})`}
      subtitle="Public repository archive retrieved from GitHub, sorted by recent activity."
      action={
        <div className="relative">
          <Search className="w-3.5 h-3.5 absolute left-2.5 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            placeholder="Search repositories or topics..."
            value={searchTerm}
            onChange={handleSearchChange}
            className="text-xs pl-8 pr-2.5 py-1.5 rounded-lg border border-slate-200 bg-slate-50 focus:bg-white focus:outline-none focus:ring-1 focus:ring-indigo-500 w-44 sm:w-60"
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
                  <th className="py-2.5 px-3">Repository</th>
                  <th className="py-2.5 px-3 min-w-[180px]">Description</th>
                  <th className="py-2.5 px-3">Language</th>
                  <th className="py-2.5 px-3 text-center">Stars</th>
                  <th className="py-2.5 px-3 text-center">Forks</th>
                  <th className="py-2.5 px-3 min-w-[140px]">Topics</th>
                  <th className="py-2.5 px-3">Updated</th>
                  <th className="py-2.5 px-3 text-right">GitHub</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-slate-700">
                {paginatedRepos.map((repo) => (
                  <tr key={repo.full_name || repo.name} className="hover:bg-slate-50/80 transition-colors">
                    <td className="py-2.5 px-3 font-semibold text-slate-900">
                      <div className="flex items-center gap-1.5">
                        <FolderGit2 className="w-3.5 h-3.5 text-indigo-600 flex-shrink-0" />
                        <span className="truncate max-w-[180px]" title={repo.full_name}>
                          {repo.name}
                        </span>
                        {repo.fork && (
                          <span className="text-[10px] px-1 rounded bg-slate-100 text-slate-500 font-normal">
                            fork
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
                      {repo.language ? (
                        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-slate-100 text-slate-700 font-mono text-[11px]">
                          {repo.language}
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
                        <div className="flex flex-wrap gap-1 max-w-[200px]">
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

                    <td className="py-2.5 px-3 text-right">
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
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Client-side Pagination Footer */}
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
                onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
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
                onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
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
