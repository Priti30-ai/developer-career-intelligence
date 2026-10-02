import React, { useState, useRef } from 'react';
import {
  UploadCloud,
  FileText,
  X,
  AlertCircle,
  Loader2,
  CheckCircle2,
  RefreshCw,
  FileCode,
  Edit3,
} from 'lucide-react';
import Button from '../common/Button';

export const ResumeUploadForm = ({
  onAnalyze,
  loading = false,
  error = null,
  validationError = null,
  onClearError,
  success = false,
}) => {
  const [mode, setMode] = useState('file'); // 'file' | 'text'
  const [selectedFile, setSelectedFile] = useState(null);
  const [resumeText, setResumeText] = useState('');
  const [isDragging, setIsDragging] = useState(false);
  const [localValidationError, setLocalValidationError] = useState(null);

  const fileInputRef = useRef(null);

  const formatFileSize = (bytes) => {
    if (!bytes || bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return `${(bytes / Math.pow(k, i)).toFixed(1)} ${sizes[i]}`;
  };

  const validateFile = (file) => {
    if (!file) return 'Please select a file.';

    // Check empty file
    if (file.size === 0) {
      return 'The selected file is empty. Please choose a valid resume document.';
    }

    // Check 5 MB limit
    if (file.size > 5 * 1024 * 1024) {
      return 'File size exceeds the 5 MB limit. Please upload a smaller resume document.';
    }

    // Validate supported extensions: PDF, DOCX, TXT only
    const allowedExtensions = ['.pdf', '.docx', '.txt'];
    const name = file.name || '';
    const ext = name.slice(name.lastIndexOf('.')).toLowerCase();

    const isAllowedExt = allowedExtensions.includes(ext);
    const isAllowedMime =
      file.type === 'application/pdf' ||
      file.type === 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' ||
      file.type === 'text/plain';

    if (!isAllowedExt && !isAllowedMime) {
      return 'Unsupported file type. Please upload a PDF, DOCX, or TXT resume.';
    }

    return null;
  };

  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const valErr = validateFile(file);
    if (valErr) {
      setLocalValidationError(valErr);
      setSelectedFile(null);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
      return;
    }

    setLocalValidationError(null);
    if (onClearError) onClearError();
    setSelectedFile(file);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    const file = e.dataTransfer.files?.[0];
    if (!file) return;

    const valErr = validateFile(file);
    if (valErr) {
      setLocalValidationError(valErr);
      setSelectedFile(null);
      return;
    }

    setLocalValidationError(null);
    if (onClearError) onClearError();
    setSelectedFile(file);
  };

  const handleRemoveFile = () => {
    setSelectedFile(null);
    setLocalValidationError(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    setLocalValidationError(null);

    if (mode === 'file') {
      if (!selectedFile) {
        setLocalValidationError('Please choose a resume file to upload and analyze.');
        return;
      }
      const valErr = validateFile(selectedFile);
      if (valErr) {
        setLocalValidationError(valErr);
        return;
      }
      onAnalyze({ type: 'file', file: selectedFile });
    } else {
      const trimmed = resumeText.trim();
      if (!trimmed) {
        setLocalValidationError('Resume text cannot be empty or whitespace-only.');
        return;
      }
      if (trimmed.length > 50000) {
        setLocalValidationError(`Resume text exceeds 50,000 characters limit (${trimmed.length.toLocaleString()} chars).`);
        return;
      }
      onAnalyze({ type: 'text', text: trimmed });
    }
  };

  const activeValidationError = localValidationError || validationError;

  return (
    <div className="bg-white border border-slate-200 rounded-xl p-6 sm:p-7 shadow-sm">
      {/* Mode Switch Tabs */}
      <div className="flex items-center justify-between pb-5 mb-5 border-b border-slate-100 flex-wrap gap-3">
        <div>
          <h3 className="text-base font-semibold text-slate-900">Upload or Enter Resume</h3>
          <p className="text-xs text-slate-500 mt-0.5">
            Submit candidate resume for backend text extraction, skill normalization, and deterministic analysis
          </p>
        </div>

        <div className="flex items-center gap-1.5 p-1 bg-slate-100 rounded-lg border border-slate-200/80">
          <button
            type="button"
            onClick={() => {
              setMode('file');
              setLocalValidationError(null);
            }}
            className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-md transition-all ${
              mode === 'file'
                ? 'bg-white text-indigo-700 shadow-sm font-semibold'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            <UploadCloud className="w-3.5 h-3.5" />
            Upload Document (PDF, DOCX, TXT)
          </button>
          <button
            type="button"
            onClick={() => {
              setMode('text');
              setLocalValidationError(null);
            }}
            className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-md transition-all ${
              mode === 'text'
                ? 'bg-white text-indigo-700 shadow-sm font-semibold'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            <Edit3 className="w-3.5 h-3.5" />
            Paste Resume Text
          </button>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        {mode === 'file' ? (
          <div>
            {!selectedFile ? (
              <div
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                onClick={() => fileInputRef.current?.click()}
                className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all ${
                  isDragging
                    ? 'border-indigo-500 bg-indigo-50/50 scale-[1.005]'
                    : 'border-slate-300 hover:border-indigo-400 hover:bg-slate-50/70 bg-slate-50/30'
                }`}
              >
                <input
                  ref={fileInputRef}
                  type="file"
                  id="resume-file-input"
                  accept=".pdf,.docx,.txt,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document,text/plain"
                  onChange={handleFileChange}
                  className="hidden"
                  disabled={loading}
                />
                <div className="w-12 h-12 rounded-full bg-indigo-50 text-indigo-600 mx-auto flex items-center justify-center mb-3">
                  <UploadCloud className="w-6 h-6" />
                </div>
                <p className="text-sm font-semibold text-slate-800">
                  Click to select resume file or drag & drop here
                </p>
                <p className="text-xs text-slate-600 mt-1 font-medium">
                  PDF, DOCX or TXT <span className="text-slate-400 font-normal">• Maximum size: 5 MB</span>
                </p>
                <div className="mt-3 inline-flex items-center gap-2 text-[11px] text-slate-400">
                  <FileCode className="w-3.5 h-3.5" />
                  Files are extracted securely on the backend using PyMuPDF and python-docx
                </div>
              </div>
            ) : (
              <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl flex items-center justify-between flex-wrap gap-3">
                <div className="flex items-center gap-3 min-w-0">
                  <div className="w-10 h-10 rounded-lg bg-indigo-100 text-indigo-700 flex items-center justify-center flex-shrink-0">
                    <FileText className="w-5 h-5" />
                  </div>
                  <div className="min-w-0">
                    <p className="text-sm font-semibold text-slate-900 truncate">
                      {selectedFile.name}
                    </p>
                    <p className="text-xs text-slate-500">
                      {formatFileSize(selectedFile.size)} • {selectedFile.name.slice(selectedFile.name.lastIndexOf('.')).toUpperCase() || 'DOCUMENT'}
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <button
                    type="button"
                    onClick={() => fileInputRef.current?.click()}
                    disabled={loading}
                    className="text-xs text-slate-600 hover:text-indigo-600 px-2.5 py-1.5 rounded-lg border border-slate-200 bg-white hover:bg-slate-50 disabled:opacity-50"
                  >
                    Change file
                  </button>
                  <button
                    type="button"
                    onClick={handleRemoveFile}
                    disabled={loading}
                    className="p-1.5 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded-lg transition-colors disabled:opacity-50"
                    title="Remove file"
                  >
                    <X className="w-4 h-4" />
                  </button>
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept=".pdf,.docx,.txt,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document,text/plain"
                    onChange={handleFileChange}
                    className="hidden"
                    disabled={loading}
                  />
                </div>
              </div>
            )}
          </div>
        ) : (
          <div>
            <label htmlFor="resume-raw-textarea" className="block text-xs font-semibold text-slate-700 mb-1.5">
              Resume Text Content (Raw Text)
            </label>
            <textarea
              id="resume-raw-textarea"
              rows={8}
              value={resumeText}
              onChange={(e) => {
                setResumeText(e.target.value);
                if (localValidationError) setLocalValidationError(null);
                if (onClearError) onClearError();
              }}
              disabled={loading}
              placeholder="Paste plain text resume here with standard sections:&#10;&#10;SUMMARY&#10;Computer engineering student interested in AI and data science.&#10;&#10;TECHNICAL SKILLS&#10;Python, C++, SQL, Pandas, NumPy, Machine Learning&#10;&#10;EDUCATION&#10;Government Polytechnic Nashik&#10;Diploma in Computer Technology&#10;2022 - 2025&#10;&#10;PROJECTS&#10;Fake Profile Detection&#10;Built a machine learning system using Random Forest.&#10;&#10;EXPERIENCE&#10;Python Intern&#10;Company XYZ&#10;June 2025 - August 2025&#10;&#10;CERTIFICATIONS&#10;Python Certification"
              className="w-full text-xs font-mono p-3.5 bg-slate-50 border border-slate-200 rounded-xl text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white transition-all disabled:opacity-50"
            />
            <div className="flex justify-between items-center mt-1 text-[11px] text-slate-400">
              <span>Standard sections: SUMMARY, SKILLS, EDUCATION, EXPERIENCE, PROJECTS, CERTIFICATIONS</span>
              <span>{resumeText.length.toLocaleString()} / 50,000 chars</span>
            </div>
          </div>
        )}

        {/* Validation Error Message */}
        {activeValidationError && (
          <div className="flex items-start gap-2.5 p-3 rounded-lg bg-amber-50 border border-amber-200 text-amber-900 text-xs">
            <AlertCircle className="w-4 h-4 text-amber-600 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <span className="font-semibold">Validation Notice: </span>
              {activeValidationError}
            </div>
          </div>
        )}

        {/* Backend / API Error Message */}
        {error && (
          <div className="flex items-start gap-2.5 p-3.5 rounded-lg bg-rose-50 border border-rose-200 text-rose-900 text-xs">
            <AlertCircle className="w-4 h-4 text-rose-600 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <p className="font-semibold text-rose-800">{error.title || 'Resume Analysis Error'}</p>
              <p className="mt-0.5 text-rose-700 leading-relaxed">{error.message}</p>
            </div>
          </div>
        )}

        {/* Submit Actions */}
        <div className="flex items-center justify-between pt-2 flex-wrap gap-3">
          <div className="text-xs text-slate-500">
            {success && !loading && (
              <span className="inline-flex items-center gap-1.5 text-emerald-600 font-medium">
                <CheckCircle2 className="w-4 h-4" />
                Resume analysis completed successfully
              </span>
            )}
          </div>

          <div className="flex items-center gap-2.5">
            {error && (
              <Button
                type="button"
                variant="outline"
                size="md"
                onClick={handleSubmit}
                disabled={loading}
                icon={RefreshCw}
              >
                Retry
              </Button>
            )}

            <Button
              type="submit"
              variant="primary"
              size="md"
              disabled={loading || (mode === 'file' && !selectedFile) || (mode === 'text' && !resumeText.trim())}
              className="min-w-[160px]"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Uploading and analyzing resume...
                </>
              ) : (
                <>
                  <FileText className="w-4 h-4" />
                  Analyze Resume
                </>
              )}
            </Button>
          </div>
        </div>
      </form>
    </div>
  );
};

export default ResumeUploadForm;
