import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { Menu, Terminal, ChevronRight } from 'lucide-react';
import apiClient from '../../services/api';
import StatusBadge from '../common/StatusBadge';
import { getRouteMetadata, APP_NAME } from '../../utils/constants';

export const Header = ({ onOpenSidebar }) => {
  const location = useLocation();
  const currentRoute = getRouteMetadata(location.pathname);

  const [apiStatus, setApiStatus] = useState('checking'); // 'connected' | 'offline' | 'checking'
  const [apiLatency, setApiLatency] = useState(null);

  useEffect(() => {
    let isMounted = true;

    const checkBackendStatus = async () => {
      const startTime = Date.now();
      try {
        await apiClient.get('/health');
        if (isMounted) {
          setApiLatency(Date.now() - startTime);
          setApiStatus('connected');
        }
      } catch (err) {
        if (isMounted) {
          setApiStatus('offline');
          setApiLatency(null);
        }
      }
    };

    checkBackendStatus();
    const interval = setInterval(checkBackendStatus, 15000);

    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, []);

  return (
    <header className="h-16 bg-white border-b border-slate-200 sticky top-0 z-30 px-4 sm:px-6 lg:px-8 flex items-center justify-between shadow-sm/50">
      {/* Left: Mobile Toggle & Page Title / Breadcrumb */}
      <div className="flex items-center gap-3 sm:gap-4 min-w-0">
        <button
          onClick={onOpenSidebar}
          className="p-2 -ml-2 rounded-lg text-slate-500 hover:text-slate-800 hover:bg-slate-100 lg:hidden focus:outline-none focus:ring-2 focus:ring-indigo-500"
          aria-label="Open navigation sidebar"
        >
          <Menu className="w-5 h-5" />
        </button>

        <div className="min-w-0">
          <div className="flex items-center gap-1.5 text-xs text-slate-500 font-medium">
            <span className="hidden sm:inline-block text-slate-500 hover:text-slate-700">
              {APP_NAME}
            </span>
            {currentRoute.group && (
              <>
                <ChevronRight className="w-3 h-3 text-slate-400 hidden sm:inline-block flex-shrink-0" />
                <span className="text-slate-500 hidden sm:inline-block truncate">
                  {currentRoute.group}
                </span>
              </>
            )}
          </div>
          <h1 className="text-sm sm:text-base font-semibold text-slate-900 tracking-tight truncate">
            {currentRoute.name}
          </h1>
        </div>
      </div>

      {/* Right: Real API Backend Status & API Version Indicator */}
      <div className="flex items-center gap-2 sm:gap-4 flex-shrink-0">
        <div className="flex items-center">
          {apiStatus === 'connected' ? (
            <StatusBadge
              status="success"
              text={`FastAPI Online (${apiLatency}ms)`}
            />
          ) : apiStatus === 'offline' ? (
            <StatusBadge
              status="neutral"
              text="FastAPI Ready (:8000)"
            />
          ) : (
            <StatusBadge
              status="info"
              text="Connecting..."
            />
          )}
        </div>

        <div className="hidden md:flex items-center gap-1.5 pl-3 border-l border-slate-200 text-xs text-slate-500">
          <Terminal className="w-3.5 h-3.5 text-slate-400" />
          <span className="font-mono text-[11px]">API v1</span>
        </div>
      </div>
    </header>
  );
};

export default Header;
