import React, { useState, useEffect } from 'react';
import {
  Target,
  Layers,
  Sparkles,
  Info,
  CheckCircle2,
  AlertTriangle,
  RotateCcw,
  Briefcase,
  Compass,
} from 'lucide-react';
import Button from '../components/common/Button';
import SkillGapForm from '../components/skill-gap/SkillGapForm';
import SkillGapEmptyState from '../components/skill-gap/SkillGapEmptyState';
import SkillGapMetricCards from '../components/skill-gap/SkillGapMetricCards';
import SkillGapBreakdown from '../components/skill-gap/SkillGapBreakdown';
import SkillGapCategoryCard from '../components/skill-gap/SkillGapCategoryCard';
import { listCareerRoles, analyzeSkillGap } from '../services/skillGapService';

export const SkillGap = () => {
  // Roles state (fetched from backend)
  const [roles, setRoles] = useState([]);
  const [rolesLoading, setRolesLoading] = useState(false);
  const [rolesError, setRolesError] = useState(null);

  // Analysis form state
  const [selectedRole, setSelectedRole] = useState('');
  const [currentSkills, setCurrentSkills] = useState([]);
  const [loading, setLoading] = useState(false);
  const [gapResult, setGapResult] = useState(null);
  const [error, setError] = useState(null);
  const [validationError, setValidationError] = useState(null);

  // Fetch available roles from backend on mount
  const fetchRoles = async () => {
    setRolesLoading(true);
    setRolesError(null);
    try {
      const data = await listCareerRoles();
      setRoles(data || []);
      // If roles exist and none selected, leave as placeholder
    } catch (err) {
      setRolesError(err.message || 'Unable to load predefined career roles from the backend.');
    } finally {
      setRolesLoading(false);
    }
  };

  useEffect(() => {
    fetchRoles();
  }, []);

  const handleAnalyze = async () => {
    const cleanRole = (selectedRole || '').trim();

    if (!cleanRole) {
      setValidationError('Please select a target career role to analyze.');
      return;
    }

    setValidationError(null);
    setLoading(true);
    setError(null);

    try {
      const responseData = await analyzeSkillGap({
        targetRole: cleanRole,
        currentSkills: currentSkills,
      });

      setGapResult(responseData);
      setError(null);
    } catch (err) {
      const rawMessage = err.message || '';
      const statusMatch = rawMessage.match(/\b(400|404|422|429|500|502|503)\b/);
      const httpStatus = statusMatch ? parseInt(statusMatch[1], 10) : err.response?.status;

      let errorTitle = 'Skill Gap Analysis Failed';
      let errorMessage = 'An unexpected error occurred while communicating with the skill gap service.';

      if (httpStatus === 404 || rawMessage.toLowerCase().includes('not supported') || rawMessage.toLowerCase().includes('not found')) {
        errorTitle = 'Career Role Not Found';
        errorMessage = `The career role "${cleanRole}" is not recognized by the backend service. Please select a valid role.`;
      } else if (httpStatus === 422 || rawMessage.toLowerCase().includes('validation')) {
        errorTitle = 'Invalid Request Parameters';
        errorMessage = 'The backend rejected the request format. Please check selected inputs.';
      } else if (
        rawMessage.toLowerCase().includes('network') ||
        rawMessage.toLowerCase().includes('failed to fetch') ||
        rawMessage.toLowerCase().includes('connect')
      ) {
        errorTitle = 'Backend Server Offline';
        errorMessage = 'Unable to connect to the FastAPI backend server at http://localhost:8000. Please verify that the backend process is running.';
      } else if (rawMessage) {
        errorMessage = rawMessage;
      }

      setError({
        title: errorTitle,
        message: errorMessage,
        status: httpStatus || null,
      });
      setGapResult(null);
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setSelectedRole('');
    setCurrentSkills([]);
    setGapResult(null);
    setError(null);
    setValidationError(null);
  };

  const handleLoadSample = () => {
    setSelectedRole('backend-developer');
    setCurrentSkills(['Python', 'SQL', 'Git', 'Pandas']);
    setValidationError(null);
  };

  return (
    <div className="space-y-6">
      {/* 1. Header & System Context Banner */}
      <div className="bg-white border border-slate-200 rounded-xl p-6 sm:p-7 shadow-sm">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="max-w-3xl">
            <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded-full text-xs font-medium bg-indigo-50 text-indigo-700 border border-indigo-100 mb-3">
              <Target className="w-3.5 h-3.5" />
              Developer Analysis
            </div>
            <h2 className="text-xl sm:text-2xl font-bold text-slate-900 tracking-tight">
              Career Role Skill Gap Analysis
            </h2>
            <p className="mt-1.5 text-xs sm:text-sm text-slate-600 leading-relaxed">
              Benchmark your technical skills against predefined engineering role requirements.
              Identifies exact missing competencies, calculates deterministic match coverage, and evaluates category-level readiness.
            </p>
          </div>

          {gapResult && (
            <div className="flex-shrink-0">
              <Button
                variant="outline"
                size="sm"
                onClick={handleReset}
                icon={RotateCcw}
                className="text-xs text-slate-600 hover:text-slate-900"
              >
                New Skill Gap Analysis
              </Button>
            </div>
          )}
        </div>
      </div>

      {/* 2. Interactive Input Form */}
      <SkillGapForm
        roles={roles}
        rolesLoading={rolesLoading}
        rolesError={rolesError}
        onRetryRoles={fetchRoles}
        selectedRole={selectedRole}
        setSelectedRole={setSelectedRole}
        currentSkills={currentSkills}
        setCurrentSkills={setCurrentSkills}
        onSubmit={handleAnalyze}
        loading={loading}
        validationError={validationError}
        error={error}
        onRetry={handleAnalyze}
        onReset={handleReset}
      />

      {/* 3. Empty State or Live Gap Results */}
      {!gapResult && !loading && (
        <SkillGapEmptyState onLoadSample={handleLoadSample} />
      )}

      {/* Live Gap Results */}
      {gapResult && (
        <div className="space-y-6">
          {/* Key Metric Cards */}
          <SkillGapMetricCards
            skillMatchPercentage={gapResult.skill_match_percentage ?? gapResult.match_percentage}
            targetRole={gapResult.target_role}
            totalRequiredSkills={gapResult.total_required_skills}
            totalMatchedSkills={gapResult.total_matched_skills}
            totalMissingSkills={gapResult.total_missing_skills}
          />

          {/* Skill Breakdown (Missing Gaps vs Possessed vs All Requirements) */}
          <SkillGapBreakdown
            matchedSkills={gapResult.matched_skills || []}
            missingSkills={gapResult.missing_skills || []}
            matchedSkillDetails={gapResult.matched_skill_details || []}
            missingSkillDetails={gapResult.missing_skill_details || []}
            targetRole={gapResult.target_role}
          />

          {/* Category-Level Coverage Progress */}
          {gapResult.category_breakdown && gapResult.category_breakdown.length > 0 && (
            <SkillGapCategoryCard
              categoryBreakdown={gapResult.category_breakdown}
            />
          )}
        </div>
      )}
    </div>
  );
};

export default SkillGap;
