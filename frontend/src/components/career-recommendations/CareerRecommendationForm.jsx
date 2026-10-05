import React, { useState } from 'react';
import Card from '../common/Card';
import Button from '../common/Button';
import {
  Compass,
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
  Layers,
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
  'Deep Learning',
  'TensorFlow',
  'PyTorch',
  'REST API',
];

export const CAREER_SKILL_PRESETS = [
  {
    name: 'Data Science & ML',
    roleSlug: 'data-scientist',
    skills: ['Python', 'SQL', 'Pandas', 'NumPy', 'Machine Learning', 'Data Visualization', 'Git'],
  },
  {
    name: 'Backend Engineering',
    roleSlug: 'backend-developer',
    skills: ['Python', 'SQL', 'FastAPI', 'PostgreSQL', 'Docker', 'Git', 'Linux', 'REST API'],
  },
  {
    name: 'Full Stack Web',
    roleSlug: 'full-stack-developer',
    skills: ['JavaScript', 'TypeScript', 'React', 'Node.js', 'HTML', 'CSS', 'SQL', 'Git'],
  },
  {
    name: 'AI Engineering',
    roleSlug: 'ai-engineer',
    skills: ['Python', 'Machine Learning', 'Deep Learning', 'PyTorch', 'Docker', 'Git'],
  },
];

export const CareerRecommendationForm = ({
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

  const handleLoadPreset = (preset) => {
    const merged = [...currentSkills];
    for (const s of preset.skills) {
      if (!merged.some((existing) => existing.toLowerCase() === s.toLowerCase())) {
        merged.push(s);
      }
    }
    setCurrentSkills(merged);
    if (preset.roleSlug && (!selectedRole || selectedRole === 'all')) {
      setSelectedRole(preset.roleSlug);
    }
  };

  const handleFormSubmit = (e) => {
    e.preventDefault();
    if (loading) return;

    // Flush any pending text in the skill input field
    if (skillInput.trim()) {
      handleAddSkill();
    }

    onSubmit();
  };

  return (
    <Card className="mb-6 shadow-sm">
      <form onSubmit={handleFormSubmit} className="space-y-6">
        {/* Section Header */}
        <div className="flex items-center justify-between pb-4 border-b border-slate-100 flex-wrap gap-2">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-indigo-50 border border-indigo-100 flex items-center justify-center text-indigo-600">
              <Compass className="w-4 h-4" />
            </div>
            <div>
              <h2 className="text-sm font-semibold text-slate-900">Career Recommendation Parameters</h2>
              <p className="text-xs text-slate-500">
                Specify your skills and select target scope to generate ranked career guidance.
              </p>
            </div>
          </div>

          {/* Preset Buttons */}
          <div className="flex items-center gap-1.5 flex-wrap">
            <span className="text-xs text-slate-400 mr-1 flex items-center gap-1">
              <Sparkles className="w-3 h-3 text-indigo-500" /> Presets:
            </span>
            {CAREER_SKILL_PRESETS.map((preset) => (
              <button
                key={preset.name}
                type="button"
                onClick={() => handleLoadPreset(preset)}
                className="px-2.5 py-1 text-xs font-medium text-slate-600 bg-slate-50 hover:bg-indigo-50 hover:text-indigo-700 border border-slate-200 rounded-md transition-colors"
                title={`Load ${preset.name} skills (${preset.skills.length} skills)`}
              >
                {preset.name}
              </button>
            ))}
          </div>
        </div>

        {/* Target Scope / Role Selector */}
        <div>
          <div className="flex items-center justify-between mb-1.5">
            <label htmlFor="target-role-select" className="text-xs font-semibold text-slate-700 flex items-center gap-1.5">
              <Briefcase className="w-3.5 h-3.5 text-indigo-600" />
              Target Career Role / Evaluation Scope
              <span className="text-rose-500">*</span>
            </label>
            {rolesLoading && (
              <span className="text-xs text-slate-400 flex items-center gap-1">
                <Loader2 className="w-3 h-3 animate-spin" />
                Loading career roles...
              </span>
            )}
          </div>

          {rolesError ? (
            <div className="p-3 bg-rose-50 border border-rose-200 rounded-lg flex items-center justify-between gap-3 text-xs text-rose-700">
              <div className="flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 shrink-0 text-rose-500" />
                <span>Failed to load roles from backend: {rolesError}</span>
              </div>
              {onRetryRoles && (
                <button
                  type="button"
                  onClick={onRetryRoles}
                  className="px-2 py-1 bg-white border border-rose-300 rounded font-medium hover:bg-rose-100 transition-colors shrink-0"
                >
                  Retry
                </button>
              )}
            </div>
          ) : (
            <div className="relative">
              <select
                id="target-role-select"
                value={selectedRole}
                onChange={(e) => setSelectedRole(e.target.value)}
                disabled={rolesLoading || loading}
                className="w-full px-3.5 py-2.5 bg-white border border-slate-200 rounded-lg text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all appearance-none pr-10 cursor-pointer disabled:bg-slate-50 disabled:cursor-not-allowed"
              >
                <option value="all">
                  🌟 All Supported Roles (Rank & Compare Best Matches)
                </option>
                <optgroup label="Specific Career Roles">
                  {roles.map((role) => (
                    <option key={role.slug} value={role.slug}>
                      {role.display_name} ({role.required_skill_count} required skills)
                    </option>
                  ))}
                </optgroup>
              </select>
              <div className="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none text-slate-400">
                <ChevronDown className="w-4 h-4" />
              </div>
            </div>
          )}

          {activeRoleObj && activeRoleObj.description && selectedRole !== 'all' && (
            <p className="text-xs text-slate-500 mt-1.5 flex items-center gap-1.5 italic">
              <HelpCircle className="w-3.5 h-3.5 text-slate-400 shrink-0" />
              {activeRoleObj.description}
            </p>
          )}
          {selectedRole === 'all' && (
            <p className="text-xs text-slate-500 mt-1.5 flex items-center gap-1.5">
              <Sparkles className="w-3.5 h-3.5 text-indigo-500 shrink-0" />
              Evaluates your skills simultaneously across all {roles.length || 8} supported roles and identifies your highest-fit career trajectory.
            </p>
          )}
        </div>

        {/* Developer Skills Section */}
        <div>
          <div className="flex items-center justify-between mb-1.5">
            <label className="text-xs font-semibold text-slate-700 flex items-center gap-1.5">
              <Tag className="w-3.5 h-3.5 text-indigo-600" />
              Current Developer Skills
              <span className="text-slate-400 font-normal">
                ({currentSkills.length} added)
              </span>
            </label>
            {currentSkills.length > 0 && (
              <button
                type="button"
                onClick={handleClearSkills}
                className="text-xs text-slate-400 hover:text-rose-600 transition-colors"
              >
                Clear all
              </button>
            )}
          </div>

          {/* Tag Input Field */}
          <div className="flex items-center gap-2 mb-2.5">
            <div className="relative flex-1">
              <input
                type="text"
                value={skillInput}
                onChange={(e) => setSkillInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Type a skill and press Enter (e.g. Python, SQL, Docker, FastAPI)..."
                disabled={loading}
                className="w-full px-3.5 py-2 bg-white border border-slate-200 rounded-lg text-sm text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all disabled:bg-slate-50"
              />
            </div>
            <Button
              type="button"
              variant="outline"
              size="md"
              onClick={() => handleAddSkill()}
              disabled={loading || !skillInput.trim()}
              icon={Plus}
              className="shrink-0"
            >
              Add
            </Button>
          </div>

          {/* Active Skill Chips */}
          {currentSkills.length > 0 ? (
            <div className="flex flex-wrap gap-1.5 p-3 rounded-lg bg-slate-50 border border-slate-200 max-h-40 overflow-y-auto">
              {currentSkills.map((skill, idx) => (
                <span
                  key={`${skill}-${idx}`}
                  className="inline-flex items-center gap-1 px-2.5 py-1 rounded-md text-xs font-medium bg-white text-slate-800 border border-slate-200 shadow-2xs group hover:border-indigo-300 transition-colors"
                >
                  <span>{skill}</span>
                  <button
                    type="button"
                    onClick={() => handleRemoveSkill(idx)}
                    disabled={loading}
                    className="w-4 h-4 rounded hover:bg-slate-100 flex items-center justify-center text-slate-400 hover:text-rose-600 transition-colors"
                    title={`Remove ${skill}`}
                  >
                    <X className="w-3 h-3" />
                  </button>
                </span>
              ))}
            </div>
          ) : (
            <div className="p-3 rounded-lg bg-slate-50/70 border border-dashed border-slate-200 text-center">
              <p className="text-xs text-slate-400">
                No skills added yet. Type your skills above or click suggestions below.
              </p>
            </div>
          )}

          {/* Quick-add suggestions */}
          <div className="mt-2.5 flex items-center gap-1.5 flex-wrap">
            <span className="text-2xs font-medium text-slate-400 uppercase tracking-wider mr-1">
              Suggestions:
            </span>
            {COMMON_SKILL_SUGGESTIONS.map((s) => {
              const alreadyAdded = currentSkills.some((c) => c.toLowerCase() === s.toLowerCase());
              return (
                <button
                  key={s}
                  type="button"
                  onClick={() => handleAddSkill(s)}
                  disabled={alreadyAdded || loading}
                  className={`text-2xs px-2 py-0.5 rounded-full border transition-all ${
                    alreadyAdded
                      ? 'bg-slate-100 text-slate-400 border-slate-200 cursor-default'
                      : 'bg-white text-slate-600 border-slate-200 hover:border-indigo-300 hover:text-indigo-600 hover:bg-indigo-50/50'
                  }`}
                >
                  {alreadyAdded && <Check className="w-2.5 h-2.5 inline mr-1 text-emerald-500" />}
                  {s}
                </button>
              );
            })}
          </div>
        </div>

        {/* Validation Error Banner */}
        {validationError && (
          <div className="p-3 bg-amber-50 border border-amber-200 rounded-lg flex items-start gap-2.5 text-xs text-amber-800">
            <AlertTriangle className="w-4 h-4 text-amber-600 mt-0.5 shrink-0" />
            <div>
              <p className="font-semibold">Validation Requirement</p>
              <p className="mt-0.5">{validationError}</p>
            </div>
          </div>
        )}

        {/* Backend API Error Banner */}
        {error && (
          <div className="p-3.5 bg-rose-50 border border-rose-200 rounded-lg flex items-start justify-between gap-3 text-xs text-rose-800">
            <div className="flex items-start gap-2.5">
              <AlertTriangle className="w-4 h-4 text-rose-600 mt-0.5 shrink-0" />
              <div>
                <p className="font-semibold">{error.title || 'Career Recommendation Failed'}</p>
                <p className="mt-0.5 text-rose-700">{error.message}</p>
              </div>
            </div>
            {onRetry && (
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={onRetry}
                icon={RefreshCw}
                className="shrink-0 text-xs bg-white text-rose-700 border-rose-300 hover:bg-rose-100"
              >
                Retry
              </Button>
            )}
          </div>
        )}

        {/* Action Controls */}
        <div className="pt-2 flex items-center justify-between flex-wrap gap-3">
          <div className="text-xs text-slate-500">
            {selectedRole === 'all' ? (
              <span>Will rank all supported roles deterministically.</span>
            ) : (
              <span>
                Evaluating against <strong className="text-slate-700">{activeRoleObj?.display_name || selectedRole}</strong>.
              </span>
            )}
          </div>

          <div className="flex items-center gap-2">
            {onReset && (
              <Button
                type="button"
                variant="ghost"
                size="md"
                onClick={onReset}
                disabled={loading}
                icon={RotateCcw}
              >
                Reset
              </Button>
            )}

            <Button
              type="submit"
              variant="primary"
              size="md"
              disabled={loading || rolesLoading}
              icon={loading ? Loader2 : Compass}
              className={loading ? 'cursor-not-allowed opacity-80' : ''}
            >
              {loading ? (
                <span className="flex items-center gap-2">
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Analyzing Career Profile...
                </span>
              ) : selectedRole === 'all' ? (
                'Rank & Compare All Roles'
              ) : (
                'Generate Career Recommendations'
              )}
            </Button>
          </div>
        </div>
      </form>
    </Card>
  );
};

export default CareerRecommendationForm;
