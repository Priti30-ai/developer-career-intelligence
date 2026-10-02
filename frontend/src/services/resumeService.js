import apiClient from './api.js';

/**
 * Service for interacting with the Resume Analysis FastAPI backend.
 *
 * Supported workflows:
 * 1. File Upload (Primary):
 *    - Method: POST /resume/analyze
 *    - Content-Type: multipart/form-data
 *    - Payload: FormData containing 'file'
 *    - Supported formats: .pdf, .docx, .txt (max 5 MB)
 *
 * 2. Pasted Text (Fallback):
 *    - Method: POST /resume/analyze
 *    - Content-Type: application/json
 *    - Payload: { resume_text: string }
 */

/**
 * Parses and extracts structured developer profile data from raw resume text (JSON).
 *
 * @param {string} resumeText - Raw plain text resume string
 * @returns {Promise<Object>} ResumeAnalysisResponse matching backend schema
 */
export const analyzeResumeText = async (resumeText) => {
  if (!resumeText || !resumeText.trim()) {
    throw new Error('Resume text must not be empty or whitespace-only.');
  }

  const trimmed = resumeText.trim();
  if (trimmed.length > 50000) {
    throw new Error(
      `Resume text exceeds maximum allowed length of 50,000 characters (current: ${trimmed.length.toLocaleString()}).`
    );
  }

  const response = await apiClient.post('/resume/analyze', {
    resume_text: trimmed,
  });

  return response.data;
};

/**
 * Uploads an actual resume document file (PDF, DOCX, TXT) using multipart/form-data.
 * Sends raw file bytes directly to the backend without client-side text conversion.
 *
 * @param {File} file - Uploaded File object
 * @returns {Promise<Object>} Object containing backend analysis response and file metadata
 */
export const analyzeResumeFile = async (file) => {
  if (!file) {
    throw new Error('Please select a resume file to analyze.');
  }

  // 1. Empty file validation
  if (file.size === 0) {
    throw new Error('The selected file is empty. Please choose a valid resume document.');
  }

  // 2. File size validation (5 MB limit)
  const MAX_FILE_SIZE = 5 * 1024 * 1024;
  if (file.size > MAX_FILE_SIZE) {
    throw new Error('File size exceeds the 5 MB limit. Please upload a smaller resume document.');
  }

  // 3. Supported extension and MIME type validation (PDF, DOCX, TXT only)
  const allowedExtensions = ['.pdf', '.docx', '.txt'];
  const fileName = file.name || '';
  const fileExt = fileName.slice(fileName.lastIndexOf('.')).toLowerCase();

  const isAllowedExt = allowedExtensions.includes(fileExt);
  const isAllowedMime =
    file.type === 'application/pdf' ||
    file.type === 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' ||
    file.type === 'text/plain';

  if (!isAllowedExt && !isAllowedMime) {
    throw new Error('Unsupported file type. Please upload a PDF, DOCX, or TXT resume.');
  }

  // 4. Construct multipart/form-data payload with actual file bytes
  const formData = new FormData();
  formData.append('file', file);

  // Send FormData to backend. apiClient interceptor automatically removes default
  // Content-Type so the browser sets multipart/form-data with proper boundary.
  const response = await apiClient.post('/resume/analyze', formData);

  return {
    ...response.data,
    _fileMeta: {
      name: file.name,
      size: file.size,
      type: file.type || fileExt,
      lastModified: file.lastModified,
    },
  };
};

export default {
  analyzeResumeText,
  analyzeResumeFile,
};
