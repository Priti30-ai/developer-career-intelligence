import React, { useEffect } from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import {
  LayoutDashboard,
  GitBranch,
  Cpu,
  Target,
  Network,
  ShieldCheck,
  Compass,
  Briefcase,
  GraduationCap,
  FileText,
  X,
  Server
} from 'lucide-react';
import { NAVIGATION_CONFIG } from '../../utils/constants';

// Icon dictionary mapped to constants icon names
const ICON_MAP = {
  LayoutDashboard,
  GitBranch,
  Cpu,
  Target,
  Network,
  ShieldCheck,
  Compass,
  Briefcase,
  GraduationCap,
  FileText,
};

export const Sidebar = ({ isOpen, onClose }) => {
  const location = useLocation();

  // Close drawer on route change on mobile
  useEffect(() => {
    if (isOpen) {
      onClose();
    }
  }, [location.pathname]);

  // Close drawer on Escape key press
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  return (
    <>
      {/* Mobile backdrop */}
      {isOpen && (
        <div
          className="fixed inset-0 z-40 bg-slate-900/60 backdrop-blur-sm lg:hidden transition-opacity"
          onClick={onClose}
          aria-hidden="true"
        />
      )}

      {/* Accessible Sidebar Container */}
      <aside
        id="app-sidebar"
        aria-label="Application Navigation"
        className={`fixed top-0 bottom-0 left-0 z-50 w-64 bg-slate-900 text-slate-300 flex flex-col border-r border-slate-800 transition-transform duration-200 ease-in-out lg:translate-x-0 ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        {/* Brand Banner */}
        <div className="h-16 flex items-center justify-between px-5 border-b border-slate-800/80 bg-slate-950/40 flex-shrink-0">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center text-white font-bold text-sm shadow-md ring-1 ring-white/10">
              CI
            </div>
            <div>
              <span className="text-sm font-semibold tracking-tight text-white block">
                Career Intelligence
              </span>
              <span className="text-[10px] text-slate-400 font-mono tracking-wider uppercase block">
                Analytics Platform
              </span>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 lg:hidden focus:outline-none focus:ring-2 focus:ring-indigo-500"
            aria-label="Close navigation menu"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Scrollable Navigation Groups */}
        <div className="flex-1 overflow-y-auto px-3.5 py-4 space-y-6">
          <nav aria-label="Main Navigation" className="space-y-6">
            {NAVIGATION_CONFIG.map((group, groupIdx) => (
              <div key={group.group || `group-${groupIdx}`}>
                {group.group && (
                  <div className="px-2.5 mb-2 text-[11px] font-semibold uppercase tracking-wider text-slate-400 select-none">
                    {group.group}
                  </div>
                )}
                <div className="space-y-1">
                  {group.items.map((item) => {
                    const IconComponent = ICON_MAP[item.icon] || LayoutDashboard;
                    return (
                      <NavLink
                        key={item.path}
                        to={item.path}
                        className={({ isActive }) =>
                          `group relative flex items-center gap-3 px-3 py-2 rounded-lg text-xs sm:text-sm font-medium transition-all ${
                            isActive
                              ? 'bg-indigo-600 text-white shadow-sm font-semibold'
                              : 'text-slate-300 hover:bg-slate-800/90 hover:text-white'
                          }`
                        }
                        title={item.description}
                      >
                        {({ isActive }) => (
                          <>
                            <IconComponent
                              className={`w-4 h-4 flex-shrink-0 transition-colors ${
                                isActive ? 'text-white' : 'text-slate-400 group-hover:text-slate-200'
                              }`}
                            />
                            <span className="truncate flex-1">{item.name}</span>
                            {/* Subtle in-progress indicator badge if not active */}
                            {item.status === 'in-progress' && !isActive && (
                              <span className="w-1.5 h-1.5 rounded-full bg-slate-500/60 flex-shrink-0" />
                            )}
                          </>
                        )}
                      </NavLink>
                    );
                  })}
                </div>
              </div>
            ))}
          </nav>
        </div>

        {/* Bottom Platform Meta */}
        <div className="p-3.5 border-t border-slate-800/80 bg-slate-950/40 flex-shrink-0">
          <div className="flex items-center justify-between px-2 text-xs text-slate-400">
            <div className="flex items-center gap-2">
              <Server className="w-3.5 h-3.5 text-indigo-400" />
              <span className="font-mono text-[11px]">FastAPI v1</span>
            </div>
            <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-800/90 text-slate-400 font-mono border border-slate-700/60">
              Dev Mode
            </span>
          </div>
        </div>
      </aside>
    </>
  );
};

export default Sidebar;
