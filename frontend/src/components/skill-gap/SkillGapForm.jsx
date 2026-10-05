import React, { useState } from 'react';
import Card from '../common/Card';
import Button from '../common/Button';
import {
  Target,
  Briefcase,
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
  ChevronDown,
} from 'lucide-react';

export const COMMON_SKILL_SUGGESTIONS = [
  'Python',
  'SQL',
  'FastAPI',
  'PostgreSQL',
  'Docker',
  'Git',
  'Linux',
  'React',
  'TypeScript',
  'Node.js',
  'Pandas',
  'NumPy',
  'Machine Learning',
  'TensorFlow',
  'REST API',
];

export const SKILL_PRESETS = [
  {
    name: 'Backend Stack',
    skills: ['Python', 'SQL', 'FastAPI', 'PostgreSQL', 'Docker', 'Git', 'Linux', 'REST API'],
  },
  {
    name: 'Data Science Stack',
    skills: ['Python', 'SQL', 'Pandas', 'NumPy', 'Scikit-learn', 'Statistics', 'Git'],
  },
  {
    name: 'Full Stack Stack',
    skills: ['JavaScript', 'TypeScript', 'React', 'Node.js', 'HTML', 'CSS', 'SQL', 'Git', 'REST API'],
  },
];

export const SkillGapForm = ({
  roles = [],
  rolesLoading = false,
  rolesError = null,
  onRetryRoles,
  selectedRole,
  setSelectedRole,
  currentSkills = [],
  setCurrentSkills,
  onSubmit,
  loading = false,
  validationError,
  error,
  onRetry,
  onReset,
}) => {
  const [skillInput, setSkillInput] = useState('');

  // Find currently selected role object
  const activeRoleObj = roles.find((r) => r.slug === selectedRole);

  const handleAddSkill = (textToAdd) => {
    const raw = textToAdd !== undefined ? textToAdd : skillInput;
    if (!raw || !raw.trim()) return;

    // Split on commas, semicolons, or newlines
    const parts = raw
      .split(/[,;\n]+/)
      .map((s) => s.trim())
      .filter((s) => s.length > 0);

    const updated = [...currentSkills];
    for (const part of parts) {
      const exists = updated.some((s) => s.toLowerCase() === part.toLowerCase());
      if (!exists) {
        updated.push(part);
      }
    }

    setCurrentSkills(updated);
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
    setCurrentSkills(currentSkills.filter((_, idx) => idx !== indexToRemove));
  };

  const handleClearSkills = () => {
    setCurrentSkills([]);
  };

  const handleLoadPreset = (presetSkills) => {
    const merged = [...currentSkills];
    for (const s of presetSkills) {
      if (!merged.some((existing) => existing.toLowerCase() === s.toLowerCase())) {
        merged.push(s);
      }
    }
    setCurrentSkills(merged);
  };

  const handleLoadSample = () => {
    setSelectedRole('backend-developer');
    setCurrentSkills(['Python', 'SQL', 'Git', 'Pandas']);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!loading) {
      onSubmit();
    }
  };

  return (
    <Card
      title="Skill Gap Benchmark Parameters"
      subtitle="Select a target engineering career role and provide your current technical skills to identify missing competencies."
      action={
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={handleLoadSample}
            disabled={loading}
            icon={Sparkles}
            className="text-xs"
          >
            Load Sample
          </Button>
          {(selectedRole || currentSkills.length > 0) && (
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
        {/* 1. Target Role Selection */}
        <div>
          <div className="flex items-center justify-between mb-1.5 flex-wrap gap-2">
            <label
              htmlFor="target-role-select"
              className="text-xs font-semibold text-slate-700 flex items-center gap-1.5"
            >
              <Briefcase className="w-3.5 h-3.5 text-slate-400" />
              <span>Target Career Role <span className="text-rose-500">*</span></span>
            </label>
            {rolesLoading && (
              <span className="text-[11px] text-slate-400 flex items-center gap-1">
                <Loader2 className="w-3 h-3 animate-spin text-indigo-500" />
                <span>Loading career roles from API...</span>
              </span>
            )}
          </div>

          {rolesError ? (
            <div className="p-3 rounded-lg border border-rose-200 bg-rose-50 text-rose-800 text-xs flex items-center justify-between gap-3">
              <div className="flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 text-rose-600 flex-shrink-0" />
                <span>Failed to load career roles from backend.</span>
              </div>
              {onRetryRoles && (
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={onRetryRoles}
                  icon={RefreshCw}
                  className="bg-white text-xs text-rose-700 border-rose-300"
                >
                  Retry
                </Button>
              )}
            </div>
          ) : (
            <div className="relative">
              <select
                id="target-role-select"
                value={selectedRole}
                onChange={(e) => setSelectedRole(e.target.value)}
                disabled={loading || rolesLoading || roles.length === 0}
                className="w-full px-3.5 py-2.5 text-xs sm:text-sm rounded-lg border border-slate-300 bg-white text-slate-900 focus:outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-100 disabled:bg-slate-50 disabled:text-slate-400 transition-all appearance-none pr-10"
              >
                <option value="">-- Choose a Target Career Role --</option>
                {roles.map((r) => (
                  <option key={r.slug} value={r.slug}>
                    {r.display_name} ({r.required_skill_count} required skills)
                  </option>
                ))}
              </select>
              <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none text-slate-400">
                <ChevronDown className="w-4 h-4" />
              </div>
            </div>
          )}

          {/* Active role description snippet */}
          {activeRoleObj && (
            <div className="mt-2 p-2.5 rounded-lg bg-indigo-50/50 border border-indigo-100/70 text-xs text-slate-700 flex items-start gap-2">
              <Target className="w-4 h-4 text-indigo-600 flex-shrink-0 mt-0.5" />
              <div className="flex-1 min-w-0">
                <div className="font-semibold text-slate-900">
                  {activeRoleObj.display_name}
                  <span className="ml-2 font-normal text-indigo-700 text-[11px] bg-indigo-100/70 px-1.5 py-0.2 rounded-full">
                    {activeRoleObj.required_skill_count} required prerequisites
                  </span>
                </div>
                {activeRoleObj.description && (
                  <p className="mt-0.5 text-slate-600 leading-relaxed text-[11px]">
                    {activeRoleObj.description}
                  </p>
                )}
              </div>
            </div>
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
                <span>Your Current Skills</span>
              </label>
              <p className="text-[11px] text-slate-500">
                Enter your existing technical competencies (type and press Enter, or paste comma-separated skills).
              </p>
            </div>
            {currentSkills.length > 0 && (
              <button
                type="button"
                onClick={handleClearSkills}
                disabled={loading}
                className="text-[11px] text-rose-600 hover:text-rose-700 font-medium"
              >
                Clear all ({currentSkills.length})
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
                placeholder="e.g. Python, SQL, Docker, React (press Enter to add)"
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

          {/* Active Skill Chips */}
          {currentSkills.length > 0 ? (
            <div className="flex flex-wrap items-center gap-1.5 p-3 rounded-lg bg-slate-50 border border-slate-200 min-h-[44px]">
              {currentSkills.map((skill, idx) => (
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
                No current skills added. Enter your skills above or click a preset below.
              </p>
            </div>
          )}

          {/* Quick-add presets & suggestions */}
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
              <span className="text-[11px] font-semibold text-slate-600 mr-1">Suggestions:</span>
              {COMMON_SKILL_SUGGESTIONS.map((skill) => {
                const isSelected = currentSkills.some(
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

        {/* Validation Error Message */}
        {validationError && (
          <p className="text-xs text-rose-600 flex items-center gap-1.5 font-medium">
            <AlertTriangle className="w-3.5 h-3.5 flex-shrink-0" />
            <span>{validationError}</span>
          </p>
        )}

        {/* Submit Action Bar */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pt-3 border-t border-slate-100">
          <div className="text-[11px] text-slate-500 flex items-center gap-1.5">
            <HelpCircle className="w-3.5 h-3.5 text-slate-400 flex-shrink-0" />
            <span>
              Calls <code>POST /api/v1/skill-gap/analyze</code> with deterministic skill normalization and taxonomy breakdown.
            </span>
          </div>

          <Button
            type="submit"
            variant="primary"
            size="md"
            disabled={loading || !selectedRole}
            icon={loading ? Loader2 : Target}
            className={loading ? 'cursor-wait' : ''}
          >
            {loading ? 'Analyzing Skill Gap...' : 'Analyze Skill Gap'}
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
                {error.title || 'Skill Gap Analysis Failed'}
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

export default SkillGapForm;
