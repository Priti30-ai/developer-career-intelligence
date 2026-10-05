import React, { useState, useEffect } from 'react';
import {
  Compass,
  RotateCcw,
  Sparkles,
  Layers,
  Award,
  TrendingUp,
  Briefcase,
  AlertTriangle,
} from 'lucide-react';
import Button from '../components/common/Button';
import CareerRecommendationForm from '../components/career-recommendations/CareerRecommendationForm';
import CareerRecommendationEmptyState from '../components/career-recommendations/CareerRecommendationEmptyState';
import CareerTopMatchCard from '../components/career-recommendations/CareerTopMatchCard';
import CareerRankedList from '../components/career-recommendations/CareerRankedList';
import CareerComparisonTable from '../components/career-recommendations/CareerComparisonTable';
import CareerSkillBreakdown from '../components/career-recommendations/CareerSkillBreakdown';
import {
  listCareerRecommendationRoles,
  analyzeCareerRecommendations,
  compareAllCareerRoles,
} from '../services/careerRecommendationService';

export const CareerRecommendations = () => {
  // Roles state (fetched from backend)
  const [roles, setRoles] = useState([]);
  const [rolesLoading, setRolesLoading] = useState(false);
  const [rolesError, setRolesError] = useState(null);

  // Analysis form inputs
  const [selectedRole, setSelectedRole] = useState('all'); // 'all' or specific slug
  const [currentSkills, setCurrentSkills] = useState([]);

  // Execution state
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [validationError, setValidationError] = useState(null);

  // Results state (100% real backend response)
  const [rankedResults, setRankedResults] = useState(null); // When selectedRole === 'all'
  const [singleResult, setSingleResult] = useState(null); // When selectedRole !== 'all'
  const [activeSlug, setActiveSlug] = useState(null);

  // Fetch available roles from backend on mount
  const fetchRoles = async () => {
    setRolesLoading(true);
    setRolesError(null);
    try {
      const data = await listCareerRecommendationRoles();
      setRoles(data || []);
    } catch (err) {
      setRolesError(err.message || 'Unable to load supported career roles from backend.');
    } finally {
      setRolesLoading(false);
    }
  };

  useEffect(() => {
    fetchRoles();
  }, []);

  const handleAnalyze = async () => {
    // Client-side validation
    if (!currentSkills || currentSkills.length === 0) {
      setValidationError('Please specify at least one skill or load a preset to generate recommendations.');
      return;
    }

    setValidationError(null);
    setLoading(true);
    setError(null);

    try {
      if (selectedRole === 'all') {
        // Compare across all predefined roles via real backend calls
        const ranked = await compareAllCareerRoles({
          currentSkills,
          roles,
        });

        if (!ranked || ranked.length === 0) {
          throw new Error('No career recommendation results returned by the backend.');
        }

        setRankedResults(ranked);
        setSingleResult(null);
        setActiveSlug(ranked[0].role_slug);
      } else {
        // Single target role analysis
        const single = await analyzeCareerRecommendations({
          targetRole: selectedRole,
          currentSkills,
        });

        setSingleResult(single);
        setRankedResults(null);
        setActiveSlug(single.role_slug);
      }
    } catch (err) {
      const rawMessage = err.message || '';
      const statusMatch = rawMessage.match(/\b(400|404|422|429|500|502|503)\b/);
      const httpStatus = statusMatch ? parseInt(statusMatch[1], 10) : err.response?.status;

      let errorTitle = 'Career Recommendation Failed';
      let errorMessage = 'An unexpected error occurred while communicating with the career recommendation service.';

      if (httpStatus === 404 || rawMessage.toLowerCase().includes('not found')) {
        errorTitle = 'Target Role Not Found';
        errorMessage = `The selected role "${selectedRole}" was not found by the backend service.`;
      } else if (httpStatus === 422 || rawMessage.toLowerCase().includes('validation')) {
        errorTitle = 'Invalid Request Format';
        errorMessage = 'The backend rejected the request format. Please verify entered skills.';
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
      setRankedResults(null);
      setSingleResult(null);
      setActiveSlug(null);
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setCurrentSkills([]);
    setSelectedRole('all');
    setRankedResults(null);
    setSingleResult(null);
    setActiveSlug(null);
    setError(null);
    setValidationError(null);
  };

  const handleLoadSample = () => {
    setSelectedRole('all');
    setCurrentSkills([
      'Python',
      'SQL',
      'Pandas',
      'NumPy',
      'Machine Learning',
      'Data Visualization',
      'Git',
    ]);
    setValidationError(null);
  };

  const handleSelectRole = (slug) => {
    setActiveSlug(slug);
  };

  // Determine currently active recommendation to display in detail
  const activeRecommendation = rankedResults
    ? rankedResults.find((r) => r.role_slug === activeSlug) || rankedResults[0]
    : singleResult;

  const activeRank = rankedResults
    ? rankedResults.findIndex((r) => r.role_slug === activeSlug) + 1
    : 1;

  const hasResults = Boolean(rankedResults || singleResult);

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
            <Compass className="w-7 h-7 text-indigo-600" />
            Career Recommendations
          </h1>
          <p className="text-sm text-slate-500 mt-1 max-w-2xl">
            Evaluate developer skills against industry career benchmarks. Calculate deterministic suitability scores,
            discover ranked career trajectories, and receive structured learning roadmaps.
          </p>
        </div>

        {hasResults && (
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={handleReset}
              icon={RotateCcw}
              className="text-xs"
            >
              New Career Analysis
            </Button>
          </div>
        )}
      </div>

      {/* Input Parameters Form */}
      <CareerRecommendationForm
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

      {/* Empty State */}
      {!hasResults && !loading && (
        <CareerRecommendationEmptyState onLoadSample={handleLoadSample} />
      )}

      {/* Loading Skeleton */}
      {loading && (
        <div className="p-12 text-center bg-white rounded-xl border border-slate-200 shadow-sm space-y-4">
          <div className="w-12 h-12 rounded-full bg-indigo-50 text-indigo-600 flex items-center justify-center mx-auto animate-pulse">
            <Compass className="w-6 h-6 animate-spin" />
          </div>
          <div>
            <h3 className="text-base font-bold text-slate-900">
              Analyzing Career Trajectory...
            </h3>
            <p className="text-xs text-slate-500 mt-1 max-w-md mx-auto">
              Evaluating skill match coverage against {selectedRole === 'all' ? 'all supported roles' : selectedRole} and
              generating topological learning roadmaps.
            </p>
          </div>
        </div>
      )}

      {/* Analysis Results */}
      {hasResults && activeRecommendation && (
        <div className="space-y-6">
          {/* Top / Inspected Role Hero Card */}
          <CareerTopMatchCard
            recommendation={activeRecommendation}
            rank={activeRank}
            isTopRecommendation={rankedResults ? activeRank === 1 : true}
            totalRolesCount={roles.length}
          />

          {/* If Multiple Roles Analyzed: Ranked List & Comparison Matrix */}
          {rankedResults && rankedResults.length > 1 && (
            <>
              {/* Ranked Cards View */}
              <CareerRankedList
                recommendations={rankedResults}
                activeSlug={activeSlug}
                onSelectRole={handleSelectRole}
              />

              {/* Side-by-side Table Matrix */}
              <CareerComparisonTable
                recommendations={rankedResults}
                activeSlug={activeSlug}
                onSelectRole={handleSelectRole}
              />
            </>
          )}

          {/* Detailed Skill Guidance & Roadmap for the Active Role */}
          <div className="pt-2">
            <div className="mb-3 flex items-center justify-between">
              <div>
                <h3 className="text-base font-bold text-slate-900">
                  Curriculum & Learning Guidance for {activeRecommendation.target_role}
                </h3>
                <p className="text-xs text-slate-500">
                  Prioritized missing skills, prerequisite dependencies, portfolio projects, and progression stages.
                </p>
              </div>
            </div>

            <CareerSkillBreakdown recommendation={activeRecommendation} />
          </div>
        </div>
      )}
    </div>
  );
};

export default CareerRecommendations;
