import React, { useState, useEffect } from 'react';
import {
  GraduationCap,
  RotateCcw,
  Sparkles,
  Layers,
  Target,
  Briefcase,
  AlertTriangle,
  Info,
} from 'lucide-react';
import Button from '../components/common/Button';
import LearningRoadmapForm, {
  SAMPLE_ROADMAP_INPUT,
} from '../components/learning-roadmap/LearningRoadmapForm';
import LearningRoadmapEmptyState from '../components/learning-roadmap/LearningRoadmapEmptyState';
import RoadmapProgress from '../components/learning-roadmap/RoadmapProgress';
import RoadmapTimeline from '../components/learning-roadmap/RoadmapTimeline';
import LearningGuidance from '../components/learning-roadmap/LearningGuidance';
import ProjectRecommendations from '../components/learning-roadmap/ProjectRecommendations';
import { getRoles, analyzeRoadmap } from '../services/learningRoadmapService';

export const LearningRoadmap = () => {
  // Roles list state
  const [roles, setRoles] = useState([]);
  const [rolesLoading, setRolesLoading] = useState(false);
  const [rolesError, setRolesError] = useState(null);

  // Form input state
  const [selectedRole, setSelectedRole] = useState('');
  const [currentSkills, setCurrentSkills] = useState([]);

  // Analysis execution state
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [validationError, setValidationError] = useState(null);

  // Analysis result from backend (100% real backend response)
  const [roadmapData, setRoadmapData] = useState(null);

  const fetchRoles = async () => {
    setRolesLoading(true);
    setRolesError(null);
    try {
      const data = await getRoles();
      setRoles(data || []);
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

    // Client-side validations
    if (!cleanRole) {
      setValidationError('Please select a target career role to generate a learning roadmap.');
      return;
    }

    setValidationError(null);
    setLoading(true);
    setError(null);

    try {
      const response = await analyzeRoadmap(cleanRole, currentSkills);
      setRoadmapData(response);
      setError(null);
    } catch (err) {
      const rawMessage = err.message || '';
      const statusMatch = rawMessage.match(/\b(400|404|422|429|500|502|503)\b/);
      const httpStatus = statusMatch ? parseInt(statusMatch[1], 10) : err.response?.status;

      let errorTitle = 'Roadmap Generation Failed';
      let errorMessage = 'An unexpected error occurred while communicating with the roadmap service.';

      if (httpStatus === 404 || rawMessage.toLowerCase().includes('not found')) {
        errorTitle = 'Target Role Not Found';
        errorMessage = `The target role "${cleanRole}" was not found by the backend service.`;
      } else if (httpStatus === 422 || rawMessage.toLowerCase().includes('validation')) {
        errorTitle = 'Invalid Request Format';
        errorMessage = 'The backend rejected the request format. Please verify entered parameters.';
      } else if (
        rawMessage.toLowerCase().includes('network') ||
        rawMessage.toLowerCase().includes('failed to fetch') ||
        rawMessage.toLowerCase().includes('connect')
      ) {
        errorTitle = 'Backend Server Offline';
        errorMessage = 'Unable to connect to the FastAPI backend server at http://localhost:8000. Please verify that the backend is running.';
      } else if (rawMessage) {
        errorMessage = rawMessage;
      }

      setError({
        title: errorTitle,
        message: errorMessage,
        status: httpStatus || null,
      });
      setRoadmapData(null);
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setSelectedRole('');
    setCurrentSkills([]);
    setRoadmapData(null);
    setError(null);
    setValidationError(null);
  };

  const handleLoadSample = () => {
    setSelectedRole(SAMPLE_ROADMAP_INPUT.roleSlug);
    setCurrentSkills([...SAMPLE_ROADMAP_INPUT.skills]);
    setValidationError(null);
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-2 border-b border-slate-200">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-2xs font-bold uppercase tracking-wider text-indigo-600 bg-indigo-50 px-2 py-0.5 rounded-full border border-indigo-100">
              Career Intelligence
            </span>
          </div>
          <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight flex items-center gap-2.5">
            <GraduationCap className="w-7 h-7 text-indigo-600" />
            Learning Roadmap
          </h1>
          <p className="text-sm text-slate-500 mt-1 max-w-2xl">
            Converts your current technical competencies and target career benchmark into a structured,
            milestone-driven learning path with ordered prerequisites and portfolio projects.
          </p>
        </div>

        {roadmapData && (
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={handleReset}
              icon={RotateCcw}
              className="text-xs"
            >
              Create New Roadmap
            </Button>
          </div>
        )}
      </div>

      {/* Input Parameters Form */}
      <LearningRoadmapForm
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

      {/* Empty State before Analysis */}
      {!roadmapData && !loading && (
        <LearningRoadmapEmptyState onLoadSample={handleLoadSample} />
      )}

      {/* Loading Skeleton */}
      {loading && (
        <div className="p-12 text-center bg-white rounded-xl border border-slate-200 shadow-sm space-y-4">
          <div className="w-12 h-12 rounded-full bg-indigo-50 text-indigo-600 flex items-center justify-center mx-auto animate-pulse">
            <GraduationCap className="w-6 h-6 animate-spin" />
          </div>
          <div>
            <h3 className="text-base font-bold text-slate-900">
              Generating Learning Roadmap...
            </h3>
            <p className="text-xs text-slate-500 mt-1 max-w-md mx-auto">
              Analyzing skill dependencies, ordering prerequisites, and assembling sequential milestone stages.
            </p>
          </div>
        </div>
      )}

      {/* Roadmap Results Dashboard */}
      {roadmapData && (
        <div className="space-y-6">
          {/* Summary Progress Cards */}
          <RoadmapProgress data={roadmapData} />

          {/* Vertical Sequential Roadmap Timeline */}
          <RoadmapTimeline
            roadmap={roadmapData.roadmap}
            targetRole={roadmapData.target_role}
          />

          {/* Actionable Portfolio Projects */}
          <ProjectRecommendations
            roadmap={roadmapData.roadmap}
            recommendations={roadmapData.recommendations}
            targetRole={roadmapData.target_role}
          />

          {/* Prioritized Learning Guidance */}
          <LearningGuidance
            recommendations={roadmapData.recommendations}
            targetRole={roadmapData.target_role}
          />

          {/* Official Disclaimer Banner */}
          {roadmapData.disclaimer && (
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 flex items-start gap-3 text-xs text-slate-600 shadow-2xs">
              <Info className="w-4 h-4 text-slate-400 mt-0.5 shrink-0" />
              <p className="leading-relaxed">
                <strong className="text-slate-800">Notice:</strong> {roadmapData.disclaimer}
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default LearningRoadmap;
