import React from 'react';
import Card from '../common/Card';
import StatusBadge from '../common/StatusBadge';
import { Server, Database, Network, Cpu } from 'lucide-react';

export const SystemStatusCard = () => {
  const subsystems = [
    {
      name: 'FastAPI Service Engine',
      description: 'REST API v1 router with modular sub-routers',
      route: '/api/v1',
      icon: Server,
      status: 'active',
      badge: 'Operational',
    },
    {
      name: 'Intelligence & Scoring Pipeline',
      description: 'Skill gap analyzer, career recommendations, and job matching',
      route: '/api/v1/skill-gap, /career-recommendations',
      icon: Cpu,
      status: 'active',
      badge: 'Registered',
    },
    {
      name: 'Evidence & Architecture Engine',
      description: 'Repository structure analysis and resume evidence extraction',
      route: '/api/v1/evidence, /repository-architecture',
      icon: Network,
      status: 'active',
      badge: 'Registered',
    },
    {
      name: 'Database Persistence Layer',
      description: 'Relational storage for profiles, jobs, skills, and assessment logs',
      route: 'PostgreSQL / SQLite schemas',
      icon: Database,
      status: 'active',
      badge: 'Configured',
    },
  ];

  return (
    <Card
      title="System Architecture & Integration Status"
      subtitle="Overview of backend micro-services and endpoint readiness for the Developer Career Intelligence platform."
    >
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {subsystems.map((subsystem) => {
          const Icon = subsystem.icon;
          return (
            <div
              key={subsystem.name}
              className="p-4 rounded-lg border border-slate-200 bg-slate-50/50 hover:bg-slate-50 transition-colors flex items-start gap-3.5"
            >
              <div className="p-2 rounded-lg bg-indigo-50 text-indigo-600 border border-indigo-100 flex-shrink-0">
                <Icon className="w-5 h-5" />
              </div>
              <div className="min-w-0 flex-1">
                <div className="flex items-center justify-between gap-2">
                  <h4 className="text-sm font-semibold text-slate-900 truncate">
                    {subsystem.name}
                  </h4>
                  <StatusBadge
                    status="success"
                    text={subsystem.badge}
                    className="flex-shrink-0"
                  />
                </div>
                <p className="text-xs text-slate-500 mt-1 leading-relaxed">
                  {subsystem.description}
                </p>
                <div className="mt-2 text-[11px] font-mono text-slate-600 bg-white px-2 py-0.5 rounded border border-slate-200 inline-block">
                  {subsystem.route}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </Card>
  );
};

export default SystemStatusCard;
