import React, { useState } from 'react';
import Card from '../common/Card';
import { Cpu, Search, Hash } from 'lucide-react';

export const TechnologyList = ({ technologies = [] }) => {
  const [filterTerm, setFilterTerm] = useState('');

  const filteredTechnologies = technologies.filter((tech) =>
    tech.toLowerCase().includes(filterTerm.toLowerCase().trim())
  );

  return (
    <Card
      title={`Detected Repository Technologies (${technologies.length})`}
      subtitle="Canonical frameworks, programming languages, and tooling identified across repository codebases."
      action={
        technologies.length > 8 && (
          <div className="relative">
            <Search className="w-3.5 h-3.5 absolute left-2.5 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              placeholder="Filter tech..."
              value={filterTerm}
              onChange={(e) => setFilterTerm(e.target.value)}
              className="text-xs pl-8 pr-2.5 py-1.5 rounded-lg border border-slate-200 bg-slate-50 focus:bg-white focus:outline-none focus:ring-1 focus:ring-indigo-500 w-36"
            />
          </div>
        )
      }
    >
      {technologies.length === 0 ? (
        <div className="text-center py-6 text-xs text-slate-400">
          No technologies detected in the analyzed repositories.
        </div>
      ) : filteredTechnologies.length === 0 ? (
        <div className="text-center py-6 text-xs text-slate-400">
          No technologies match "{filterTerm}".
        </div>
      ) : (
        <div className="flex flex-wrap gap-2">
          {filteredTechnologies.map((tech) => (
            <span
              key={tech}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-slate-50 text-slate-700 border border-slate-200/90 hover:border-indigo-300 hover:bg-indigo-50/40 hover:text-indigo-700 transition-colors"
            >
              <Hash className="w-3 h-3 text-slate-400" />
              <span>{tech}</span>
            </span>
          ))}
        </div>
      )}
    </Card>
  );
};

export default TechnologyList;
