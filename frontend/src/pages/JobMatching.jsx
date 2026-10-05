import React, { useState } from 'react';
import {
  Briefcase,
  Layers,
  Sparkles,
  Info,
  CheckCircle2,
  AlertTriangle,
  RotateCcw,
} from 'lucide-react';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import JobMatchingForm, {
  SAMPLE_JOB_DESCRIPTION,
} from '../components/job-matching/JobMatchingForm';
import JobMatchingEmptyState from '../components/job-matching/JobMatchingEmptyState';
import JobMatchingMetricCards from '../components/job-matching/JobMatchingMetricCards';
import SkillMatchBreakdown from '../components/job-matching/SkillMatchBreakdown';
import CategoryBreakdownCard from '../components/job-matching/CategoryBreakdownCard';
import { matchJobDescription } from '../services/jobMatchingService';

export const JobMatching = () => {
  const [jobDescription, setJobDescription] = useState('');
  const [developerSkills, setDeveloperSkills] = useState([]);
  const [loading, setLoading] = useState(false);
  const [matchResult, setMatchResult] = useState(null);
  const [error, setError] = useState(null);
  const [validationError, setValidationError] = useState(null);

  const handleAnalyze = async () => {
    const cleanJD = jobDescription.trim();

    // Client-side validation
    if (!cleanJD) {
      setValidationError('Please paste or enter a job description to analyze.');
      return;
    }

    if (cleanJD.length > 50000) {
      setValidationError('Job description text exceeds the maximum limit of 50,000 characters.');
      return;
    }

    setValidationError(null);
    setLoading(true);
    setError(null);

    try {
      const responseData = await matchJobDescription({
        jobDescription: cleanJD,
        developerSkills: developerSkills,
      });

      setMatchResult(responseData);
      setError(null);
    } catch (err) {
      const rawMessage = err.message || '';
      const statusMatch = rawMessage.match(/\b(400|404|422|429|500|502|503)\b/);
      const httpStatus = statusMatch ? parseInt(statusMatch[1], 10) : err.response?.status;

      let errorTitle = 'Job Matching Failed';
      let errorMessage = 'An unexpected error occurred while communicating with the matching service.';

      if (httpStatus === 422 || rawMessage.toLowerCase().includes('validation') || rawMessage.toLowerCase().includes('whitespace')) {
        errorTitle = 'Invalid Input Data';
        errorMessage = 'The job description must not be empty or whitespace-only. Please provide text with discernible requirements.';
      } else if (httpStatus === 400) {
        errorTitle = 'Malformed Request';
        errorMessage = rawMessage || 'The request payload was rejected by the server.';
      } else if (
        rawMessage.toLowerCase().includes('network') ||
        rawMessage.toLowerCase().includes('failed to fetch') ||
        rawMessage.toLowerCase().includes('connect')
      ) {
        errorTitle = 'Backend Connection Offline';
        errorMessage = 'Unable to connect to the FastAPI backend server at http://localhost:8000. Please verify that the backend process is running.';
      } else if (rawMessage) {
        errorMessage = rawMessage;
      }

      setError({
        title: errorTitle,
        message: errorMessage,
        status: httpStatus || null,
      });
      setMatchResult(null);
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setJobDescription('');
    setDeveloperSkills([]);
    setMatchResult(null);
    setError(null);
    setValidationError(null);
  };

  const handleLoadSample = () => {
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
    setValidationError(null);
  };

  return (
    <div className="space-y-6">
      {/* 1. Header & System Context Banner */}
      <div className="bg-white border border-slate-200 rounded-xl p-6 sm:p-7 shadow-sm">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="max-w-3xl">
            <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded-full text-xs font-medium bg-indigo-50 text-indigo-700 border border-indigo-100 mb-3">
              <Briefcase className="w-3.5 h-3.5" />
              Career Intelligence
            </div>
            <h2 className="text-xl sm:text-2xl font-bold text-slate-900 tracking-tight">
              Job Description Matching Intelligence
            </h2>
            <p className="mt-1.5 text-xs sm:text-sm text-slate-600 leading-relaxed">
              Extract technical competencies deterministically from live job postings and match them against
              candidate skills. Computes explainable match scores, partitions skill gaps, and evaluates category-by-category coverage.
            </p>
          </div>

          {matchResult && (
            <div className="flex-shrink-0">
              <Button
                variant="outline"
                size="sm"
                onClick={handleReset}
                icon={RotateCcw}
                className="text-xs text-slate-600 hover:text-slate-900"
              >
                New Match Analysis
              </Button>
            </div>
          )}
        </div>
      </div>

      {/* 2. Interactive Input Form */}
      <JobMatchingForm
        jobDescription={jobDescription}
        setJobDescription={setJobDescription}
        developerSkills={developerSkills}
        setDeveloperSkills={setDeveloperSkills}
        onSubmit={handleAnalyze}
        loading={loading}
        validationError={validationError}
        error={error}
        onRetry={handleAnalyze}
        onReset={handleReset}
      />

      {/* 3. Empty State or Live Match Results */}
      {!matchResult && !loading && (
        <JobMatchingEmptyState onLoadSample={handleLoadSample} />
      )}

      {/* Live Match Results */}
      {matchResult && (
        <div className="space-y-6">
          {/* Key Metric Cards */}
          <JobMatchingMetricCards
            matchPercentage={matchResult.match_percentage}
            totalRequiredSkills={matchResult.total_required_skills}
            matchedSkillCount={matchResult.matched_skill_count}
            missingSkillCount={matchResult.missing_skill_count}
          />

          {/* Explainability Summary Card */}
          {matchResult.explanation && (
            <div className="p-4 rounded-xl border border-indigo-100 bg-indigo-50/40 text-xs sm:text-sm">
              <div className="flex items-start gap-3">
                <div className="w-7 h-7 rounded-lg bg-indigo-100 text-indigo-700 flex items-center justify-center flex-shrink-0 mt-0.5">
                  <Info className="w-4 h-4" />
                </div>
                <div className="space-y-1">
                  <span className="font-semibold text-slate-900 block text-xs uppercase tracking-wider">
                    Deterministic Match Assessment
                  </span>
                  <p className="text-slate-700 leading-relaxed">
                    {matchResult.explanation}
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Skill Alignment Breakdown (Matched vs Missing vs Extracted) */}
          <SkillMatchBreakdown
            matchedSkills={matchResult.matched_skills || []}
            missingSkills={matchResult.missing_skills || []}
            extractedSkills={matchResult.extracted_skills || []}
            matchedSkillDetails={matchResult.matched_skill_details || []}
            missingSkillDetails={matchResult.missing_skill_details || []}
          />

          {/* Category-Level Coverage Progress */}
          {matchResult.category_breakdown && matchResult.category_breakdown.length > 0 && (
            <CategoryBreakdownCard
              categoryBreakdown={matchResult.category_breakdown}
            />
          )}
        </div>
      )}
    </div>
  );
};

export default JobMatching;
