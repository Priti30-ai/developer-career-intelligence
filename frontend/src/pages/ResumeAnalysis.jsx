import React, { useState } from 'react';
import {
  FileText,
  RotateCcw,
} from 'lucide-react';
import Button from '../components/common/Button';
import ResumeUploadForm from '../components/resume/ResumeUploadForm';
import ResumeSummaryCard from '../components/resume/ResumeSummaryCard';
import ResumeSkills from '../components/resume/ResumeSkills';
import ResumeExperience from '../components/resume/ResumeExperience';
import ResumeProjects from '../components/resume/ResumeProjects';
import ResumeEducation from '../components/resume/ResumeEducation';
import ResumeCertifications from '../components/resume/ResumeCertifications';
import ResumeAchievements from '../components/resume/ResumeAchievements';
import ResumeInitialEmptyState from '../components/resume/ResumeInitialEmptyState';
import { analyzeResumeFile, analyzeResumeText } from '../services/resumeService';

export const ResumeAnalysis = () => {
  const [loading, setLoading] = useState(false);
  const [analysisData, setAnalysisData] = useState(null);
  const [error, setError] = useState(null);
  const [validationError, setValidationError] = useState(null);

  const handleAnalyze = async (submission) => {
    setValidationError(null);
    setError(null);
    setLoading(true);

    try {
      let result;
      if (submission.type === 'file') {
        result = await analyzeResumeFile(submission.file);
      } else {
        const data = await analyzeResumeText(submission.text);
        result = {
          ...data,
          _fileMeta: null,
        };
      }

      setAnalysisData(result);
      setError(null);
    } catch (err) {
      const rawMessage = err.message || '';
      let errorTitle = 'Resume Analysis Failed';
      let errorMessage = rawMessage || 'An error occurred during resume analysis.';

      const lower = rawMessage.toLowerCase();

      if (lower.includes('network') || lower.includes('failed to fetch') || lower.includes('connect')) {
        errorTitle = 'Backend Server Offline';
        errorMessage = 'Unable to connect to the FastAPI backend server at http://localhost:8000. Please verify the backend service is running.';
      } else if (lower.includes('unsupported') || lower.includes('format')) {
        errorTitle = 'Unsupported Format';
        errorMessage = rawMessage;
      } else if (lower.includes('5 mb') || lower.includes('file size') || lower.includes('413')) {
        errorTitle = 'File Too Large';
        errorMessage = rawMessage;
      } else if (lower.includes('empty')) {
        errorTitle = 'Empty File or Text';
        errorMessage = rawMessage;
      } else if (lower.includes('scanned') || lower.includes('image-only') || lower.includes('could not extract text')) {
        errorTitle = 'No Extractable Text';
        errorMessage = rawMessage;
      } else if (lower.includes('password') || lower.includes('encrypted')) {
        errorTitle = 'Password Protected Document';
        errorMessage = rawMessage;
      } else if (lower.includes('corrupted') || lower.includes('invalid')) {
        errorTitle = 'Corrupted Document';
        errorMessage = rawMessage;
      } else if (lower.includes('utf-8')) {
        errorTitle = 'Text Encoding Error';
        errorMessage = rawMessage;
      }

      setError({
        title: errorTitle,
        message: errorMessage,
      });
      setAnalysisData(null);
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setAnalysisData(null);
    setError(null);
    setValidationError(null);
  };

  return (
    <div className="space-y-6">
      {/* SECTION 1 — PAGE HEADER */}
      <div className="bg-white border border-slate-200 rounded-xl p-6 sm:p-7 shadow-sm">
        <div className="flex items-start justify-between flex-wrap gap-4">
          <div className="max-w-3xl">
            <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded-full text-xs font-medium bg-indigo-50 text-indigo-700 border border-indigo-100 mb-3">
              <FileText className="w-3.5 h-3.5" />
              Document Analysis Engine
            </div>
            <h2 className="text-xl sm:text-2xl font-bold text-slate-900 tracking-tight">
              Resume Analysis
            </h2>
            <p className="mt-1.5 text-xs sm:text-sm text-slate-600 leading-relaxed">
              Upload your resume to extract and analyze your professional profile. The backend document engine extracts
              text from PDF, DOCX, or TXT documents, normalizes technical skills against canonical taxonomies, and structures
              education, experience, and project entries.
            </p>
            <div className="mt-3 inline-flex items-center gap-2 text-xs text-slate-500 flex-wrap">
              <span className="font-semibold text-slate-700">Supported formats:</span>
              <span className="px-2 py-0.5 rounded bg-slate-100 font-mono text-[11px] text-slate-700">.pdf</span>
              <span className="px-2 py-0.5 rounded bg-slate-100 font-mono text-[11px] text-slate-700">.docx</span>
              <span className="px-2 py-0.5 rounded bg-slate-100 font-mono text-[11px] text-slate-700">.txt</span>
              <span className="text-slate-400 font-medium">(Max 5 MB)</span>
              <span className="text-slate-300">•</span>
              <span className="text-slate-500">or direct plain text entry</span>
            </div>
          </div>

          {analysisData && (
            <Button
              variant="outline"
              size="md"
              onClick={handleReset}
              icon={RotateCcw}
              className="flex-shrink-0"
            >
              Analyze Another Resume
            </Button>
          )}
        </div>
      </div>

      {/* SECTION 2 — UPLOAD / SUBMISSION FORM */}
      <ResumeUploadForm
        onAnalyze={handleAnalyze}
        loading={loading}
        error={error}
        validationError={validationError}
        onClearError={() => {
          setError(null);
          setValidationError(null);
        }}
        success={Boolean(analysisData)}
      />

      {/* SECTION 3 — ANALYSIS RESULTS OR INITIAL EMPTY STATE */}
      {analysisData ? (
        <div className="space-y-6">
          {/* Summary Overview Card */}
          <ResumeSummaryCard
            analysis={analysisData}
            fileMeta={analysisData._fileMeta}
          />

          {/* Technical Skills Section */}
          <ResumeSkills skills={analysisData.skills || []} />

          {/* Experience and Projects Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <ResumeExperience experience={analysisData.experience || []} />
            <ResumeProjects projects={analysisData.projects || []} />
          </div>

          {/* Education Section */}
          <ResumeEducation education={analysisData.education || []} />

          {/* Certifications and Achievements Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <ResumeCertifications certifications={analysisData.certifications || []} />
            <ResumeAchievements achievements={analysisData.achievements || []} />
          </div>
        </div>
      ) : (
        /* Empty State */
        <ResumeInitialEmptyState />
      )}
    </div>
  );
};

export default ResumeAnalysis;
