import React from 'react';
import Card from '../common/Card';
import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid
} from 'recharts';

export const SkillSourceChart = ({ skills = [] }) => {
  if (!skills || skills.length === 0) return null;

  // Real calculations computed directly from skills array
  const githubOnlyCount = skills.filter(
    (s) => s.sources?.includes('github') && !s.sources?.includes('resume')
  ).length;

  const resumeOnlyCount = skills.filter(
    (s) => s.sources?.includes('resume') && !s.sources?.includes('github')
  ).length;

  const bothSourcesCount = skills.filter(
    (s) => s.sources?.includes('github') && s.sources?.includes('resume')
  ).length;

  const sourceData = [
    { name: 'GitHub Only', count: githubOnlyCount, color: '#10b981' },
    { name: 'Resume Only', count: resumeOnlyCount, color: '#0ea5e9' },
    { name: 'Corroborated (Both)', count: bothSourcesCount, color: '#8b5cf6' },
  ].filter((item) => item.count > 0);

  // Evidence status calculations
  const strongCount = skills.filter((s) => s.evidence_status === 'STRONG').length;
  const moderateCount = skills.filter((s) => s.evidence_status === 'MODERATE').length;
  const noneDetectedCount = skills.filter((s) => s.evidence_status === 'NONE_DETECTED').length;

  const evidenceData = [
    { level: 'Strong (>= 2 repos)', count: strongCount, fill: '#059669' },
    { level: 'Moderate (1 repo)', count: moderateCount, fill: '#0284c7' },
    { level: 'None Detected (0 repos)', count: noneDetectedCount, fill: '#64748b' },
  ];

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Skill Source Distribution Chart */}
      <Card
        title="Skill Source Distribution"
        subtitle="Distribution of skills discovered via GitHub repos versus claimed on resume."
      >
        <div className="h-64 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={sourceData}
                cx="50%"
                cy="50%"
                innerRadius={55}
                outerRadius={85}
                paddingAngle={4}
                dataKey="count"
                nameKey="name"
              >
                {sourceData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip
                formatter={(value, name) => [`${value} skills`, name]}
                contentStyle={{
                  backgroundColor: '#ffffff',
                  borderColor: '#e2e8f0',
                  borderRadius: '0.5rem',
                  fontSize: '12px',
                  boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)',
                }}
              />
              <Legend
                verticalAlign="bottom"
                height={36}
                iconType="circle"
                wrapperStyle={{ fontSize: '12px', paddingTop: '10px' }}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </Card>

      {/* Evidence Grounding Bar Chart */}
      <Card
        title="Evidence Grounding Classification"
        subtitle="Deterministic evidence levels assigned to skills based on repository backing."
      >
        <div className="h-64 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={evidenceData}
              layout="vertical"
              margin={{ top: 10, right: 30, left: 40, bottom: 5 }}
            >
              <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#f1f5f9" />
              <XAxis type="number" allowDecimals={false} tick={{ fontSize: 11 }} />
              <YAxis
                type="category"
                dataKey="level"
                tick={{ fontSize: 11 }}
                width={130}
              />
              <Tooltip
                formatter={(value) => [`${value} skills`, 'Count']}
                contentStyle={{
                  backgroundColor: '#ffffff',
                  borderColor: '#e2e8f0',
                  borderRadius: '0.5rem',
                  fontSize: '12px',
                }}
              />
              <Bar dataKey="count" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </Card>
    </div>
  );
};

export default SkillSourceChart;
