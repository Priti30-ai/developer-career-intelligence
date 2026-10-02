import { useState, useCallback } from 'react';
import apiClient from '../services/api';

/**
 * Custom hook for making API requests with loading, error, and data states
 */
export const useApi = (apiFunc) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const execute = useCallback(
    async (...args) => {
      setLoading(true);
      setError(null);
      try {
        const response = await (apiFunc ? apiFunc(...args) : apiClient(...args));
        setData(response.data);
        return response.data;
      } catch (err) {
        const errorMessage = err.message || 'An unexpected error occurred';
        setError(errorMessage);
        throw err;
      } finally {
        setLoading(false);
      }
    },
    [apiFunc]
  );

  return { data, loading, error, execute, setData };
};

export default useApi;
