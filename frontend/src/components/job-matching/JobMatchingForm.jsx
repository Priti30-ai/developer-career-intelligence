import React, { useState } from 'react';
import Card from '../common/Card';
import Button from '../common/Button';
import {
  Briefcase,
  FileText,
  Plus,
  X,
  AlertTriangle,
  RefreshCw,
  Loader2,
  Sparkles,
  RotateCcw,
  Check,
  Tag,
  HelpCircle,
} from 'lucide-react';

export const SAMPLE_JOB_DESCRIPTION = `Senior Backend Engineer

About the Role:
We are seeking an experienced Senior Backend Engineer to architect, build, and maintain mission-critical microservices and high-throughput data processing pipelines.

Key Responsibilities:
- Design, develop, and deploy asynchronous backend APIs using Python, FastAPI, and Pydantic.
- Architect scalable relational databases and optimize complex queries using PostgreSQL.
- Package and containerize microservices using Docker and configure Kubernetes deployment manifests.
- Implement reliable caching, task queues, and asynchronous messaging with Redis and RabbitMQ.
- Build continuous integration and deployment pipelines with GitHub Actions and Linux automation scripts.
- Write thorough unit and integration test suites using pytest and testclient.
- Collaborate with frontend engineers developing user interfaces in React and TypeScript.

Requirements:
- 4+ years of professional backend software engineering experience.
- Strong proficiency in Python, FastAPI, and modern Python asynchronous paradigms.
- Solid hands-on experience with PostgreSQL, relational database indexing, and query optimization.
- Proficiency with Docker containerization, Git version control, and Linux environments.
- Practical experience with Redis caching and REST API architecture.

Nice to Have:
- Familiarity with AWS or GCP cloud infrastructure.
- Experience with React, Node.js, and GraphQL.
- Background in system observability and monitoring.`;

export const POPULAR_SKILL_SUGGESTIONS = [
  'Python',
  'FastAPI',
  'PostgreSQL',
  'Docker',
  'Git',
  'Redis',
  'React',
  'TypeScript',
  'Node.js',
  'Kubernetes',
  'AWS',
  'Linux',
  'SQL',
  'RabbitMQ',
];

export const SKILL_PRESETS = [
  {
    name: 'Backend Python',
    skills: ['Python', 'FastAPI', 'PostgreSQL', 'Docker', 'Git', 'Redis', 'Linux'],
  },
  {
    name: 'Full-Stack Web',
    skills: ['Python', 'FastAPI', 'React', 'TypeScript', 'PostgreSQL', 'Docker', 'Git', 'TailwindCSS'],
  },
  {
    name: 'DevOps / Cloud',
    skills: ['Docker', 'Kubernetes', 'AWS', 'Linux', 'Git', 'Python', 'CI/CD'],
  },
];

export const JobMatchingForm = ({
  jobDescription,
  setJobDescription,
  developerSkills,
  setDeveloperSkills,
  onSubmit,
  loading,
  validationError,
  error,
  onRetry,
  onReset,
}) => {
  const [skillInput, setSkillInput] = useState('');

  // Handle adding a skill (supports single entry or comma-separated batch)
  const handleAddSkill = (textToAdd) => {
    const raw = textToAdd !== undefined ? textToAdd : skillInput;
    if (!raw || !raw.trim()) return;

    // Split on commas or newlines if pasted
    const parts = raw
      .split(/[,;\n]+/)
      .map((s) => s.trim())
      .filter((s) => s.length > 0);

    const updated = [...developerSkills];
    for (const part of parts) {
      // Deduplicate case-insensitively while preserving entered casing
      const exists = updated.some((s) => s.toLowerCase() === part.toLowerCase());
      if (!exists) {
        updated.push(part);
      }
    }

    setDeveloperSkills(updated);
    if (textToAdd === undefined) {
      setSkillInput('');
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleAddSkill();
    }
  };

  const handleRemoveSkill = (indexToRemove) => {
    setDeveloperSkills(developerSkills.filter((_, idx) => idx !== indexToRemove));
  };

  const handleClearSkills = () => {
    setDeveloperSkills([]);
  };

  const handleLoadPreset = (presetSkills) => {
    const merged = [...developerSkills];
    for (const s of presetSkills) {
      if (!merged.some((existing) => existing.toLowerCase() === s.toLowerCase())) {
        merged.push(s);
      }
    }
    setDeveloperSkills(merged);
  };

  const handleLoadSampleAll = () => {
    setJobDescription(SAMPLE_JOB_DESCRIPTION);
    setDeveloperSkills([
      'Python',
      'FastAPI',
      'PostgreSQL',
      'Docker',
      'Git',
      'Redis',
      'Linux',
    ]);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!loading) {
      onSubmit();
    }
  };

  const charCount = jobDescription.length;
  const isOverLimit = charCount > 50000;

  return (
    <Card
      title="Job Description & Candidate Competencies"
      subtitle="Paste job requirements and define developer skills to calculate deterministic match coverage."
      action={
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={handleLoadSampleAll}
            disabled={loading}
            icon={Sparkles}
            className="text-xs"
          >
            Load Sample
          </Button>
          {(jobDescription || developerSkills.length > 0) && (
            <Button
              variant="ghost"
              size="sm"
              onClick={onReset}
              disabled={loading}
              icon={RotateCcw}
              className="text-xs text-slate-500 hover:text-slate-800"
            >
              Reset
            </Button>
          )}
        </div>
      }
    >
      <form onSubmit={handleSubmit} className="space-y-5">
        {/* 1. Job Description Textarea */}
        <div>
          <div className="flex items-center justify-between mb-1.5 flex-wrap gap-2">
            <label
              htmlFor="job-description-input"
              className="text-xs font-semibold text-slate-700 flex items-center gap-1.5"
            >
              <Briefcase className="w-3.5 h-3.5 text-slate-400" />
              <span>Target Job Description <span className="text-rose-500">*</span></span>
            </label>
            <div className="flex items-center gap-2">
              <span
                className={`text-[11px] font-mono ${
                  isOverLimit
                    ? 'text-rose-600 font-semibold'
                    : charCount > 40000
                    ? 'text-amber-600'
                    : 'text-slate-400'
                }`}
              >
                {charCount.toLocaleString()} / 50,000 characters
              </span>
              {jobDescription && (
                <button
                  type="button"
                  onClick={() => setJobDescription('')}
                  disabled={loading}
                  className="text-[11px] text-slate-400 hover:text-slate-600 underline"
                >
                  Clear
                </button>
              )}
            </div>
          </div>

          <textarea
            id="job-description-input"
            rows={7}
            value={jobDescription}
            onChange={(e) => setJobDescription(e.target.value)}
            disabled={loading}
            placeholder="Paste complete job description text, requirements, or tech stack here... (e.g. Senior Backend Engineer - Python, FastAPI, PostgreSQL, Docker, Redis...)"
            className={`w-full px-3.5 py-2.5 text-xs sm:text-sm rounded-lg border bg-white text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-offset-1 transition-all ${
              validationError
                ? 'border-rose-300 focus:border-rose-500 focus:ring-rose-200'
                : 'border-slate-300 focus:border-indigo-500 focus:ring-indigo-100'
            } disabled:bg-slate-50 disabled:text-slate-400 disabled:cursor-not-allowed resize-y`}
          />

          {validationError && (
            <p className="mt-1.5 text-xs text-rose-600 flex items-center gap-1 font-medium">
              <AlertTriangle className="w-3.5 h-3.5 flex-shrink-0" />
              <span>{validationError}</span>
            </p>
          )}
        </div>

        {/* 2. Developer Skills Input */}
        <div className="space-y-2.5 pt-1 border-t border-slate-100">
          <div className="flex items-center justify-between flex-wrap gap-2">
            <div>
              <label
                htmlFor="developer-skill-input"
                className="text-xs font-semibold text-slate-700 flex items-center gap-1.5"
              >
                <Tag className="w-3.5 h-3.5 text-slate-400" />
                <span>Developer Skills</span>
              </label>
              <p className="text-[11px] text-slate-500">
                Enter skills to match against job requirements (type and press Enter or separate with commas).
              </p>
            </div>
            {developerSkills.length > 0 && (
              <button
                type="button"
                onClick={handleClearSkills}
                disabled={loading}
                className="text-[11px] text-rose-600 hover:text-rose-700 font-medium"
              >
                Clear all ({developerSkills.length})
              </button>
            )}
          </div>

          {/* Skill text input with Add button */}
          <div className="flex items-center gap-2">
            <div className="relative flex-1">
              <input
                id="developer-skill-input"
                type="text"
                value={skillInput}
                onChange={(e) => setSkillInput(e.target.value)}
                onKeyDown={handleKeyDown}
                disabled={loading}
                placeholder="Type skill name (e.g. Python, Docker, PostgreSQL) and press Enter"
                className="w-full px-3 py-2 text-xs sm:text-sm rounded-lg border border-slate-300 bg-white text-slate-900 placeholder-slate-400 focus:outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-100 disabled:bg-slate-50 disabled:text-slate-400"
              />
            </div>
            <Button
              type="button"
              variant="secondary"
              size="md"
              disabled={loading || !skillInput.trim()}
              onClick={() => handleAddSkill()}
              icon={Plus}
            >
              Add
            </Button>
          </div>

          {/* Active Developer Skill Chips */}
          {developerSkills.length > 0 ? (
            <div className="flex flex-wrap items-center gap-1.5 p-3 rounded-lg bg-slate-50 border border-slate-200 min-h-[44px]">
              {developerSkills.map((skill, idx) => (
                <span
                  key={`${skill}-${idx}`}
                  className="inline-flex items-center gap-1 px-2.5 py-1 rounded-md text-xs font-medium bg-white text-indigo-700 border border-indigo-200/80 shadow-2xs"
                >
                  <span>{skill}</span>
                  <button
                    type="button"
                    onClick={() => handleRemoveSkill(idx)}
                    disabled={loading}
                    className="p-0.5 rounded text-indigo-400 hover:text-rose-600 hover:bg-rose-50 transition-colors"
                    title={`Remove ${skill}`}
                  >
                    <X className="w-3 h-3" />
                  </button>
                </span>
              ))}
            </div>
          ) : (
            <div className="p-3 rounded-lg border border-dashed border-slate-200 bg-slate-50/50 text-center">
              <p className="text-xs text-slate-500">
                No developer skills added yet. Add individual skills or click a preset below.
              </p>
            </div>
          )}

          {/* Quick-add presets & popular suggestions */}
          <div className="space-y-2 pt-1">
            <div className="flex items-center gap-2 flex-wrap text-xs text-slate-500">
              <span className="font-semibold text-slate-600 text-[11px]">Quick Presets:</span>
              {SKILL_PRESETS.map((preset) => (
                <button
                  key={preset.name}
                  type="button"
                  onClick={() => handleLoadPreset(preset.skills)}
                  disabled={loading}
                  className="px-2 py-0.5 rounded text-[11px] font-medium bg-slate-100 hover:bg-indigo-50 hover:text-indigo-700 text-slate-700 border border-slate-200 transition-colors"
                >
                  + {preset.name}
                </button>
              ))}
            </div>

            <div className="flex items-center gap-1.5 flex-wrap text-xs">
              <span className="text-[11px] font-semibold text-slate-600 mr-1">Popular:</span>
              {POPULAR_SKILL_SUGGESTIONS.map((skill) => {
                const isSelected = developerSkills.some(
                  (s) => s.toLowerCase() === skill.toLowerCase()
                );
                return (
                  <button
                    key={skill}
                    type="button"
                    onClick={() => {
                      if (!isSelected) {
                        handleAddSkill(skill);
                      }
                    }}
                    disabled={loading || isSelected}
                    className={`px-2 py-0.5 rounded-full text-[11px] font-medium transition-all ${
                      isSelected
                        ? 'bg-emerald-50 text-emerald-700 border border-emerald-200 cursor-default'
                        : 'bg-white text-slate-600 border border-slate-200 hover:border-indigo-300 hover:text-indigo-600 hover:bg-indigo-50/50'
                    }`}
                  >
                    {isSelected && <Check className="w-2.5 h-2.5 inline mr-1 text-emerald-600" />}
                    {skill}
                  </button>
                );
              })}
            </div>
          </div>
        </div>

        {/* Submit Action Bar */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pt-3 border-t border-slate-100">
          <div className="text-[11px] text-slate-500 flex items-center gap-1.5">
            <HelpCircle className="w-3.5 h-3.5 text-slate-400 flex-shrink-0" />
            <span>
              Calls <code>POST /api/v1/job-matching/analyze</code> with deterministic skill extraction and coverage metrics.
            </span>
          </div>

          <Button
            type="submit"
            variant="primary"
            size="md"
            disabled={loading || isOverLimit}
            icon={loading ? Loader2 : Briefcase}
            className={loading ? 'cursor-wait' : ''}
          >
            {loading ? 'Matching Skills...' : 'Analyze Job Match'}
          </Button>
        </div>
      </form>

      {/* Professional Error Notification */}
      {error && (
        <div className="mt-4 p-4 rounded-xl border border-rose-200 bg-rose-50/70 text-rose-900 text-xs sm:text-sm">
          <div className="flex items-start gap-3">
            <AlertTriangle className="w-5 h-5 text-rose-600 flex-shrink-0 mt-0.5" />
            <div className="flex-1 min-w-0">
              <div className="font-semibold text-rose-950">
                {error.title || 'Job Matching Failed'}
              </div>
              <p className="mt-1 text-rose-800 leading-relaxed">
                {error.message}
              </p>
              {error.status && (
                <div className="mt-1.5 font-mono text-[11px] text-rose-700">
                  HTTP Status: {error.status}
                </div>
              )}
            </div>
            {onRetry && (
              <Button
                variant="outline"
                size="sm"
                onClick={onRetry}
                icon={RefreshCw}
                className="bg-white hover:bg-rose-50 text-rose-700 border-rose-300 flex-shrink-0"
              >
                Retry
              </Button>
            )}
          </div>
        </div>
      )}
    </Card>
  );
};

export default JobMatchingForm;
