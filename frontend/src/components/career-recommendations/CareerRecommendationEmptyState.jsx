import React from 'react';
import Card from '../common/Card';
import Button from '../common/Button';
import {
  Compass,
  CheckCircle2,
  Sparkles,
  ArrowRight,
  TrendingUp,
  GraduationCap,
  Layers,
  Target,
} from 'lucide-react';

export const CareerRecommendationEmptyState = ({ onLoadSample }) => {
  return (
    <Card className="text-center py-12 px-6">
      <div className="max-w-2xl mx-auto flex flex-col items-center">
        {/* Decorative Compass Icon */}
        <div className="w-16 h-16 rounded-2xl bg-indigo-50 border border-indigo-100 flex items-center justify-center text-indigo-600 mb-5 shadow-sm">
          <Compass className="w-8 h-8" />
        </div>

        {/* Title */}
        <h3 className="text-xl font-bold text-slate-900 mb-2">
          Discover Your Best-Fit Career Paths
        </h3>

        {/* Subtitle */}
        <p className="text-sm text-slate-600 leading-relaxed mb-8 max-w-lg">
          Compare your current technical skills against verified career role benchmarks.
          Our deterministic engine calculates exact skill match coverage, identifies high-priority gaps,
          and generates an ordered learning roadmap.
        </p>

        {/* Feature Highlights Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-left w-full mb-8">
          <div className="flex items-start gap-3 p-3.5 rounded-lg bg-slate-50 border border-slate-100">
            <TrendingUp className="w-5 h-5 text-indigo-600 mt-0.5 shrink-0" />
            <div>
              <h4 className="text-xs font-semibold text-slate-900">Ranked Career Paths</h4>
              <p className="text-xs text-slate-500 mt-0.5">
                Evaluates match strength across all supported engineering roles.
              </p>
            </div>
          </div>

          <div className="flex items-start gap-3 p-3.5 rounded-lg bg-slate-50 border border-slate-100">
            <CheckCircle2 className="w-5 h-5 text-emerald-600 mt-0.5 shrink-0" />
            <div>
              <h4 className="text-xs font-semibold text-slate-900">Strengths & Readiness</h4>
              <p className="text-xs text-slate-500 mt-0.5">
                Highlights skills you already possess that directly qualify you for the role.
              </p>
            </div>
          </div>

          <div className="flex items-start gap-3 p-3.5 rounded-lg bg-slate-50 border border-slate-100">
            <Target className="w-5 h-5 text-amber-600 mt-0.5 shrink-0" />
            <div>
              <h4 className="text-xs font-semibold text-slate-900">Prioritized Skill Gaps</h4>
              <p className="text-xs text-slate-500 mt-0.5">
                Classifies missing competencies into explainable HIGH, MEDIUM, and LOW priorities.
              </p>
            </div>
          </div>

          <div className="flex items-start gap-3 p-3.5 rounded-lg bg-slate-50 border border-slate-100">
            <GraduationCap className="w-5 h-5 text-sky-600 mt-0.5 shrink-0" />
            <div>
              <h4 className="text-xs font-semibold text-slate-900">Sequential Learning Roadmap</h4>
              <p className="text-xs text-slate-500 mt-0.5">
                Generates ordered milestone stages with conceptual topics and portfolio projects.
              </p>
            </div>
          </div>
        </div>

        {/* Quick Sample Action */}
        {onLoadSample && (
          <div className="pt-2 border-t border-slate-100 w-full flex flex-col sm:flex-row items-center justify-center gap-3">
            <span className="text-xs text-slate-500">Want to see a live analysis?</span>
            <Button
              variant="outline"
              size="sm"
              onClick={onLoadSample}
              icon={Sparkles}
              className="text-xs"
            >
              Load Sample Developer Profile
            </Button>
          </div>
        )}
      </div>
    </Card>
  );
};

export default CareerRecommendationEmptyState;
