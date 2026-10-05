import React from 'react';
import Card from '../common/Card';
import Button from '../common/Button';
import {
  GraduationCap,
  Sparkles,
  Target,
  Layers,
  ArrowRight,
  BookOpen,
  FolderGit2,
  CheckCircle2,
} from 'lucide-react';

export const LearningRoadmapEmptyState = ({ onLoadSample }) => {
  return (
    <Card className="text-center py-12 px-6 shadow-sm">
      <div className="max-w-2xl mx-auto flex flex-col items-center">
        {/* Decorative Graduation / Roadmap Icon */}
        <div className="w-16 h-16 rounded-2xl bg-indigo-50 border border-indigo-100 flex items-center justify-center text-indigo-600 mb-5 shadow-sm">
          <GraduationCap className="w-8 h-8" />
        </div>

        {/* Title */}
        <h3 className="text-xl font-bold text-slate-900 mb-2">
          Build Your Personalized Learning Roadmap
        </h3>

        {/* Subtitle */}
        <p className="text-sm text-slate-600 leading-relaxed mb-8 max-w-lg">
          Transform your current technical competencies into a structured, milestone-driven curriculum.
          Our deterministic engine topologically orders prerequisites, identifies high-priority gaps, and suggests portfolio projects.
        </p>

        {/* 3-Step Workflow Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-left w-full mb-8">
          <div className="p-4 rounded-xl bg-slate-50 border border-slate-200/80 flex flex-col justify-between">
            <div>
              <div className="w-7 h-7 rounded-lg bg-indigo-600 text-white text-xs font-bold flex items-center justify-center mb-3">
                1
              </div>
              <h4 className="text-xs font-bold text-slate-900 mb-1">Select Target Role</h4>
              <p className="text-xs text-slate-500 leading-relaxed">
                Choose the engineering benchmark you want to achieve.
              </p>
            </div>
            <div className="mt-3 flex items-center gap-1 text-2xs text-indigo-600 font-semibold">
              <Target className="w-3 h-3" /> Predefined Benchmarks
            </div>
          </div>

          <div className="p-4 rounded-xl bg-slate-50 border border-slate-200/80 flex flex-col justify-between">
            <div>
              <div className="w-7 h-7 rounded-lg bg-indigo-600 text-white text-xs font-bold flex items-center justify-center mb-3">
                2
              </div>
              <h4 className="text-xs font-bold text-slate-900 mb-1">Add Current Skills</h4>
              <p className="text-xs text-slate-500 leading-relaxed">
                Enter your existing languages, frameworks, and databases.
              </p>
            </div>
            <div className="mt-3 flex items-center gap-1 text-2xs text-emerald-600 font-semibold">
              <CheckCircle2 className="w-3 h-3" /> Real Skill Overlap
            </div>
          </div>

          <div className="p-4 rounded-xl bg-slate-50 border border-slate-200/80 flex flex-col justify-between">
            <div>
              <div className="w-7 h-7 rounded-lg bg-indigo-600 text-white text-xs font-bold flex items-center justify-center mb-3">
                3
              </div>
              <h4 className="text-xs font-bold text-slate-900 mb-1">Generate Roadmap</h4>
              <p className="text-xs text-slate-500 leading-relaxed">
                Receive sequential stages, learning topics, and projects.
              </p>
            </div>
            <div className="mt-3 flex items-center gap-1 text-2xs text-sky-600 font-semibold">
              <Layers className="w-3 h-3" /> Multi-Stage Path
            </div>
          </div>
        </div>

        {/* Quick Demo CTA */}
        {onLoadSample && (
          <div className="pt-2 border-t border-slate-100 w-full flex flex-col sm:flex-row items-center justify-center gap-3">
            <span className="text-xs text-slate-500">Want to explore with an example profile?</span>
            <Button
              variant="outline"
              size="sm"
              onClick={onLoadSample}
              icon={Sparkles}
              className="text-xs"
            >
              Load Backend Developer Sample
            </Button>
          </div>
        )}
      </div>
    </Card>
  );
};

export default LearningRoadmapEmptyState;
