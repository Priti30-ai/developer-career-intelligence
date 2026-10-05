import React, { useState } from 'react';
import Card from '../common/Card';
import Button from '../common/Button';
import {
  GraduationCap,
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

export const COMMON_SKILLS = [
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
  'PyTorch',
  'Redis',
  'REST API',
];

export const ROADMAP_PRESETS = [
  {
    name: 'Backend Python',
    roleSlug: 'backend-developer',
    skills: ['Python', 'SQL', 'FastAPI', 'PostgreSQL', 'Docker', 'Git', 'Linux'],
  },
  {
    name: 'Full-Stack Web',
    roleSlug: 'full-stack-developer',
    skills: ['JavaScript', 'TypeScript', 'React', 'Node.js', 'HTML', 'CSS', 'SQL', 'Git'],
  },
  {
    name: 'Data Science',
    roleSlug: 'data-scientist',
    skills: ['Python', 'SQL', 'Pandas', 'NumPy', 'Statistics', 'Git'],
  },
  {
    name: 'AI/ML',
    roleSlug: 'ai-engineer',
    skills: ['Python', 'Machine Learning', 'Deep Learning', 'PyTorch', 'Docker'],
  },
];

export const SAMPLE_ROADMAP_INPUT = {
  roleSlug: 'backend-developer',
  skills: ['Python', 'SQL', 'Git', 'FastAPI', 'Pandas'],
};

export const LearningRoadmapForm = ({
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
    if (preset.roleSlug && !selectedRole) {
      setSelectedRole(preset.roleSlug);
    }
  };

  const handleLoadSample = () => {
    setSelectedRole(SAMPLE_ROADMAP_INPUT.roleSlug);
    setCurrentSkills([...SAMPLE_ROADMAP_INPUT.skills]);
  };

  const handleFormSubmit = (e) => {
    e.preventDefault();
    if (loading) return;

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
              <GraduationCap className="w-4 h-4" />
            </div>
            <div>
              <h2 className="text-sm font-semibold text-slate-900">Roadmap Curriculum Inputs</h2>
              <p className="text-xs text-slate-500">
                Specify your target career goal and current technical baseline.
              </p>
            </div>
          </div>

          {/* Quick Presets & Demo Sample */}
          <div className="flex items-center gap-1.5 flex-wrap">
            <span className="text-xs text-slate-400 mr-1 flex items-center gap-1">
              <Sparkles className="w-3 h-3 text-indigo-500" /> Presets:
            </span>
            {ROADMAP_PRESETS.map((preset) => (
              <button
                key={preset.name}
                type="button"
                onClick={() => handleLoadPreset(preset)}
                className="px-2.5 py-1 text-xs font-medium text-slate-600 bg-slate-50 hover:bg-indigo-50 hover:text-indigo-700 border border-slate-200 rounded-md transition-colors"
                title={`Load ${preset.name} (${preset.skills.length} skills)`}
              >
                {preset.name}
              </button>
            ))}
            <button
              type="button"
              onClick={handleLoadSample}
              className="px-2.5 py-1 text-xs font-semibold text-indigo-700 bg-indigo-50 hover:bg-indigo-100 border border-indigo-200 rounded-md transition-colors ml-1"
            >
              Demo Sample
            </button>
          </div>
        </div>

        {/* Target Role Selector */}
        <div>
          <div className="flex items-center justify-between mb-1.5">
            <label htmlFor="target-role-dropdown" className="text-xs font-semibold text-slate-700 flex items-center gap-1.5">
              <Briefcase className="w-3.5 h-3.5 text-indigo-600" />
              Target Career Benchmark
              <span className="text-rose-500">*</span>
            </label>
            {rolesLoading && (
              <span className="text-xs text-slate-400 flex items-center gap-1">
                <Loader2 className="w-3 h-3 animate-spin" />
                Loading roles...
              </span>
            )}
          </div>

          {rolesError ? (
            <div className="p-3 bg-rose-50 border border-rose-200 rounded-lg flex items-center justify-between gap-3 text-xs text-rose-700">
              <div className="flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 shrink-0 text-rose-500" />
                <span>Error loading roles: {rolesError}</span>
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
                id="target-role-dropdown"
                value={selectedRole}
                onChange={(e) => setSelectedRole(e.target.value)}
                disabled={rolesLoading || loading}
                className="w-full px-3.5 py-2.5 bg-white border border-slate-200 rounded-lg text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all appearance-none pr-10 cursor-pointer disabled:bg-slate-50 disabled:cursor-not-allowed"
              >
                <option value="">-- Select a Target Career Role --</option>
                {roles.map((role) => (
                  <option key={role.slug} value={role.slug}>
                    {role.display_name} ({role.required_skill_count} required skills)
                  </option>
                ))}
              </select>
              <div className="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none text-slate-400">
                <ChevronDown className="w-4 h-4" />
              </div>
            </div>
          )}

          {activeRoleObj && activeRoleObj.description && (
            <p className="text-xs text-slate-500 mt-1.5 flex items-center gap-1.5 italic">
              <HelpCircle className="w-3.5 h-3.5 text-slate-400 shrink-0" />
              {activeRoleObj.description}
            </p>
          )}
        </div>

        {/* Current Skills Section */}
        <div>
          <div className="flex items-center justify-between mb-1.5">
            <label className="text-xs font-semibold text-slate-700 flex items-center gap-1.5">
              <Tag className="w-3.5 h-3.5 text-indigo-600" />
              Current Skills Possessed
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

          {/* Skill Tag Input Field */}
          <div className="flex items-center gap-2 mb-2.5">
            <div className="relative flex-1">
              <input
                type="text"
                value={skillInput}
                onChange={(e) => setSkillInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Type a skill (e.g. Python, SQL, Docker) and press Enter..."
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
                No current skills added yet. Add skills or load a preset above to calculate your learning gap.
              </p>
            </div>
          )}

          {/* Quick-Add Suggestions */}
          <div className="mt-2.5 flex items-center gap-1.5 flex-wrap">
            <span className="text-2xs font-medium text-slate-400 uppercase tracking-wider mr-1">
              Suggestions:
            </span>
            {COMMON_SKILLS.map((s) => {
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

        {/* Validation Warning Banner */}
        {validationError && (
          <div className="p-3 bg-amber-50 border border-amber-200 rounded-lg flex items-start gap-2.5 text-xs text-amber-800">
            <AlertTriangle className="w-4 h-4 text-amber-600 mt-0.5 shrink-0" />
            <div>
              <p className="font-semibold">Validation Required</p>
              <p className="mt-0.5">{validationError}</p>
            </div>
          </div>
        )}

        {/* Server Error Banner */}
        {error && (
          <div className="p-3.5 bg-rose-50 border border-rose-200 rounded-lg flex items-start justify-between gap-3 text-xs text-rose-800">
            <div className="flex items-start gap-2.5">
              <AlertTriangle className="w-4 h-4 text-rose-600 mt-0.5 shrink-0" />
              <div>
                <p className="font-semibold">{error.title || 'Roadmap Analysis Failed'}</p>
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
            {activeRoleObj ? (
              <span>
                Roadmap target: <strong className="text-slate-800">{activeRoleObj.display_name}</strong>
              </span>
            ) : (
              <span>Select a role to generate sequential stages.</span>
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
              icon={loading ? Loader2 : GraduationCap}
              className={loading ? 'cursor-not-allowed opacity-80' : ''}
            >
              {loading ? (
                <span className="flex items-center gap-2">
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Generating Roadmap...
                </span>
              ) : (
                'Generate Learning Roadmap'
              )}
            </Button>
          </div>
        </div>
      </form>
    </Card>
  );
};

export default LearningRoadmapForm;
