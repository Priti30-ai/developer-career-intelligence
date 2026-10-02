import React, { useState } from 'react';
import Card from '../common/Card';
import Button from '../common/Button';
import apiClient from '../../services/api';
import { RefreshCw, CheckCircle2, AlertCircle } from 'lucide-react';

export const ApiHealthCard = () => {
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState(null);

  const runEndpointTest = async () => {
    setTesting(true);
    setTestResult(null);
    const start = Date.now();
    try {
      const response = await apiClient.get('/health');
      setTestResult({
        success: true,
        latency: Date.now() - start,
        data: response.data,
      });
    } catch (err) {
      setTestResult({
        success: false,
        error: err.message || 'Failed to connect to backend server.',
      });
    } finally {
      setTesting(false);
    }
  };

  return (
    <Card
      title="Backend API Connectivity"
      subtitle="Verify client-to-server connection using the centralized Axios client."
      action={
        <Button
          variant="outline"
          size="sm"
          onClick={runEndpointTest}
          disabled={testing}
          icon={RefreshCw}
        >
          {testing ? 'Testing...' : 'Test Connection'}
        </Button>
      }
    >
      <div className="space-y-3">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between p-3 rounded-lg bg-slate-50 border border-slate-200 text-xs text-slate-600 gap-2">
          <div>
            <span className="font-semibold text-slate-700">Configured Base URL: </span>
            <code className="text-indigo-600 font-mono bg-white px-2 py-0.5 rounded border border-slate-200">
              {apiClient.defaults.baseURL}
            </code>
          </div>
          <div className="text-slate-500">
            Source: <code className="font-mono">import.meta.env.VITE_API_BASE_URL</code>
          </div>
        </div>

        {testResult && (
          <div
            className={`p-4 rounded-lg border text-sm flex items-start gap-3 ${
              testResult.success
                ? 'bg-emerald-50 border-emerald-200 text-emerald-800'
                : 'bg-amber-50 border-amber-200 text-amber-800'
            }`}
          >
            {testResult.success ? (
              <CheckCircle2 className="w-5 h-5 text-emerald-600 flex-shrink-0 mt-0.5" />
            ) : (
              <AlertCircle className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
            )}
            <div className="min-w-0 flex-1">
              <div className="font-semibold">
                {testResult.success ? 'FastAPI Backend Online' : 'FastAPI Backend Unreachable'}
              </div>
              <div className="text-xs mt-1">
                {testResult.success ? (
                  <span>
                    Endpoint returned HTTP 200 in {testResult.latency}ms. Response:{' '}
                    <code className="font-mono">{JSON.stringify(testResult.data)}</code>
                  </span>
                ) : (
                  <span>
                    {testResult.error}. Make sure the FastAPI backend is running via{' '}
                    <code className="font-mono bg-amber-100/60 px-1 py-0.5 rounded">
                      uvicorn app.main:app --reload
                    </code>{' '}
                    on port 8000.
                  </span>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </Card>
  );
};

export default ApiHealthCard;
