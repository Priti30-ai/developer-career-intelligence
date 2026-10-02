import React, { useState } from 'react';
import Card from '../common/Card';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell
} from 'recharts';
import { Search, Hash, BarChart3 } from 'lucide-react';

export const TechnologyAnalysis = ({ technologiesData }) => {
  const [searchTerm, setSearchTerm] = useState('');

  const rawTechnologies = technologiesData?.technologies || [];
  const totalRepositories = technologiesData?.total_repositories ?? 0;

  // Chart shows top 10 technologies from backend response
  const chartData = rawTechnologies.slice(0, 10).map((t) => ({
    name: t.name,
    repository_count: t.repository_count,
  }));

  const filteredTechnologies = rawTechnologies.filter((t) =>
    t.name.toLowerCase().includes(searchTerm.toLowerCase().trim())
  );

  return (
    <Card
      title={`Technology Signal Extraction (${rawTechnologies.length})`}
      subtitle={`Normalized programming languages, frameworks, and tooling identified across ${totalRepositories} analyzed repositories.`}
    >
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left: Recharts Horizontal Bar Chart */}
        <div className="lg:col-span-7 flex flex-col">
          <div className="flex items-center justify-between mb-3 text-xs font-semibold text-slate-700">
            <span className="flex items-center gap-1.5">
              <BarChart3 className="w-4 h-4 text-indigo-600" />
              <span>Top Detected Technologies by Repository Count</span>
            </span>
            <span className="text-[11px] font-mono text-slate-400">
              Top {chartData.length}
            </span>
          </div>

          {chartData.length === 0 ? (
            <div className="h-64 flex items-center justify-center text-xs text-slate-400 border border-dashed border-slate-200 rounded-lg">
              No technologies detected in the analyzed repositories.
            </div>
          ) : (
            <div className="h-72 w-full bg-slate-50/50 rounded-lg p-2 border border-slate-100">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={chartData}
                  layout="vertical"
                  margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                >
                  <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#e2e8f0" />
                  <XAxis type="number" allowDecimals={false} tick={{ fontSize: 11 }} />
                  <YAxis
                    type="category"
                    dataKey="name"
                    width={110}
                    tick={{ fontSize: 11, fill: '#334155' }}
                  />
                  <Tooltip
                    formatter={(value) => [`${value} repositories`, 'Presence']}
                    contentStyle={{
                      backgroundColor: '#ffffff',
                      borderColor: '#cbd5e1',
                      borderRadius: '0.5rem',
                      fontSize: '12px',
                    }}
                  />
                  <Bar dataKey="repository_count" fill="#4f46e5" radius={[0, 4, 4, 0]}>
                    {chartData.map((entry, index) => (
                      <Cell
                        key={`cell-${index}`}
                        fill={index < 3 ? '#4338ca' : '#6366f1'}
                      />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}
          <p className="text-[11px] text-slate-400 mt-2">
            * Values indicate repository count (i.e. number of distinct repositories where the technology was detected).
          </p>
        </div>

        {/* Right: Detailed Technology Table / List */}
        <div className="lg:col-span-5 flex flex-col">
          <div className="flex items-center justify-between mb-3 gap-2">
            <span className="text-xs font-semibold text-slate-700">
              Complete Technology Breakdown
            </span>
            <div className="relative">
              <Search className="w-3.5 h-3.5 absolute left-2 top-1/2 -translate-y-1/2 text-slate-400" />
              <input
                type="text"
                placeholder="Search..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="text-xs pl-7 pr-2 py-1 rounded-md border border-slate-200 bg-slate-50 focus:bg-white focus:outline-none focus:ring-1 focus:ring-indigo-500 w-28 sm:w-36"
              />
            </div>
          </div>

          <div className="border border-slate-200 rounded-lg overflow-hidden flex-1 flex flex-col">
            <div className="overflow-y-auto max-h-72">
              <table className="w-full text-left border-collapse text-xs">
                <thead className="bg-slate-50 border-b border-slate-200 text-slate-500 font-semibold sticky top-0">
                  <tr>
                    <th className="py-2 px-3">Technology</th>
                    <th className="py-2 px-3 text-right">Repositories</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 text-slate-700">
                  {filteredTechnologies.length === 0 ? (
                    <tr>
                      <td colSpan={2} className="py-6 text-center text-slate-400 text-xs">
                        No technologies match search.
                      </td>
                    </tr>
                  ) : (
                    filteredTechnologies.map((t) => (
                      <tr key={t.name} className="hover:bg-slate-50 transition-colors">
                        <td className="py-2 px-3 flex items-center gap-1.5 font-medium text-slate-900">
                          <Hash className="w-3 h-3 text-slate-400" />
                          <span>{t.name}</span>
                        </td>
                        <td className="py-2 px-3 text-right font-mono text-indigo-700 font-semibold">
                          {t.repository_count}
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </Card>
  );
};

export default TechnologyAnalysis;
