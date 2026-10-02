import axios from 'axios';

// Centralized API configuration from environment variables
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

// Request interceptor for logging or authorization tokens
apiClient.interceptors.request.use(
  (config) => {
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for consistent error extraction
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    // Standardized error message extraction
    const message =
      error.response?.data?.detail ||
      error.response?.data?.message ||
      error.message ||
      'An unexpected error occurred while contacting the server.';
    
    return Promise.reject(new Error(message));
  }
);

export default apiClient;
