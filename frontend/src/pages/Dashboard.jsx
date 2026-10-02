import React, { useState } from 'react';
import DeveloperAnalysisForm from '../components/dashboard/DeveloperAnalysisForm';
import DeveloperProfileHeader from '../components/dashboard/DeveloperProfileHeader';
import ProfileMetricCards from '../components/dashboard/ProfileMetricCards';
import TechnologyList from '../components/dashboard/TechnologyList';
import SkillEvidenceOverview from '../components/dashboard/SkillEvidenceOverview';
import SkillSourceChart from '../components/dashboard/SkillSourceChart';
import InitialEmptyState from '../components/dashboard/InitialEmptyState';
import SystemStatusCard from '../components/dashboard/SystemStatusCard';
import ApiHealthCard from '../components/dashboard/ApiHealthCard';
import Card from '../components/common/Card';
import { Layers } from 'lucide-react';
import { analyzeDeveloperProfile } from '../services/developerProfileService';

export const Dashboard = () => {
  const [username, setUsername] = useState('');
  const [resumeText, setResumeText] = useState('');
  const [loading, setLoading] = useState(false);
  const [profile, setProfile] = useState(null);
  const [error, setError] = useState(null);
  const [validationError, setValidationError] = useState(null);

  const handleAnalyze = async () => {
    const cleanUsername = username.trim();

    // Client-side validation
    if (!cleanUsername) {
      setValidationError('GitHub username is required. Please enter a valid public GitHub handle.');
      return;
    }

    setValidationError(null);
    setLoading(true);
    setError(null);

    try {
      const responseData = await analyzeDeveloperProfile({
        github_username: cleanUsername,
        resume_text: resumeText.trim() || null,
        resume_skills: [],
      });

      setProfile(responseData);
      setError(null);
    } catch (err) {
      // Professional categorized error handling
      const rawMessage = err.message || '';
      const statusMatch = rawMessage.match(/\b(404|422|429|500|502|503)\b/);
      const httpStatus = statusMatch ? parseInt(statusMatch[1], 10) : err.response?.status;

      let errorTitle = 'Profile Analysis Error';
      let errorMessage = 'An unexpected error occurred while communicating with the service.';

      if (httpStatus === 404 || rawMessage.toLowerCase().includes('not found')) {
        errorTitle = 'Developer Account Not Found';
        errorMessage = `The GitHub account "${cleanUsername}" could not be located, has no public repositories, or is restricted.`;
      } else if (httpStatus === 422 || rawMessage.toLowerCase().includes('validation') || rawMessage.toLowerCase().includes('unprocessable')) {
        errorTitle = 'Validation Rejection';
        errorMessage = 'The backend rejected the request format. Please ensure the username contains valid characters.';
      } else if (httpStatus === 429 || rawMessage.toLowerCase().includes('rate limit')) {
        errorTitle = 'GitHub Rate Limit Reached';
        errorMessage = 'The GitHub API rate limit has been exceeded. Please configure a personal GITHUB_TOKEN on the backend or try again later.';
      } else if (rawMessage.toLowerCase().includes('network') || rawMessage.toLowerCase().includes('failed to fetch') || rawMessage.toLowerCase().includes('connect')) {
        errorTitle = 'Backend Connection Offline';
        errorMessage = 'Unable to establish a connection with the FastAPI backend at http://localhost:8000. Please ensure the backend is running via "uvicorn app.main:app --reload".';
      } else if (rawMessage) {
        errorMessage = rawMessage;
      }

      setError({
        title: errorTitle,
        message: errorMessage,
        status: httpStatus || null,
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Welcome & System Context Banner */}
      <div className="bg-white border border-slate-200 rounded-xl p-6 sm:p-7 shadow-sm">
        <div className="max-w-3xl">
          <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded-full text-xs font-medium bg-indigo-50 text-indigo-700 border border-indigo-100 mb-3">
            <Layers className="w-3.5 h-3.5" />
            Developer Career Intelligence System
          </div>
          <h2 className="text-xl sm:text-2xl font-bold text-slate-900 tracking-tight">
            Unified Developer Profile & Evidence Intelligence
          </h2>
          <p className="mt-1.5 text-xs sm:text-sm text-slate-600 leading-relaxed">
            Ingest public GitHub repositories and cross-corroborate candidate resume competencies.
            The system maps raw code artifacts into a canonical skill taxonomy with deterministic evidence grounding.
          </p>
        </div>
      </div>

      {/* Developer Analysis Input Form */}
      <DeveloperAnalysisForm
        username={username}
        setUsername={(val) => {
          setUsername(val);
          if (validationError) setValidationError(null);
        }}
        resumeText={resumeText}
        setResumeText={setResumeText}
        onSubmit={handleAnalyze}
        loading={loading}
        validationError={validationError}
        error={error}
        onRetry={handleAnalyze}
      />

      {/* Real Synthesized Profile Results (when active) */}
      {profile ? (
        <div className="space-y-6">
          {/* 1. Profile Identity Header */}
          <DeveloperProfileHeader profile={profile} />

          {/* 2. Deterministic Metric Cards */}
          <ProfileMetricCards summary={profile.summary} github={profile.github} />

          {/* 3. Recharts Source & Evidence Distribution */}
          <SkillSourceChart skills={profile.skills} />

          {/* 4. Detected Technologies Tag Grid */}
          <TechnologyList technologies={profile.github?.technologies_detected || []} />

          {/* 5. Canonical Skills and Evidence Grounding Table */}
          <SkillEvidenceOverview skills={profile.skills || []} />
        </div>
      ) : (
        /* Initial Empty State before analysis */
        <InitialEmptyState />
      )}

      {/* Backend API Health Verification */}
      <ApiHealthCard />

      {/* Backend Subsystems & Routers Registry */}
      <SystemStatusCard />
    </div>
  );
};

export default Dashboard;
