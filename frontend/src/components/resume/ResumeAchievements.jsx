import React from 'react';
import { Trophy, Star } from 'lucide-react';
import Card from '../common/Card';

export const ResumeAchievements = ({ achievements = [] }) => {
  return (
    <Card
      title="Honors & Key Achievements"
      subtitle="Competitions, awards, and notable milestones highlighted in resume"
      action={
        <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-rose-50 text-rose-700 border border-rose-100">
          {achievements.length} {achievements.length === 1 ? 'achievement' : 'achievements'}
        </span>
      }
    >
      {achievements.length > 0 ? (
        <div className="space-y-3">
          {achievements.map((item, idx) => (
            <div
              key={idx}
              className="p-3.5 rounded-xl border border-slate-200 bg-white hover:border-slate-300 transition-colors flex items-start gap-3"
            >
              <div className="p-2 rounded-lg bg-rose-50 text-rose-600 flex-shrink-0 mt-0.5">
                <Trophy className="w-4 h-4" />
              </div>
              <div className="min-w-0">
                <p className="text-xs sm:text-sm font-semibold text-slate-800 leading-snug">
                  {item}
                </p>
                <div className="flex items-center gap-1 mt-1 text-[11px] text-slate-400">
                  <Star className="w-3 h-3 text-amber-500 fill-amber-500" />
                  Recognized achievement
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-6 text-slate-500">
          <Trophy className="w-8 h-8 mx-auto text-slate-300 mb-2" />
          <p className="text-xs">No honors or achievements section detected in resume text.</p>
        </div>
      )}
    </Card>
  );
};

export default ResumeAchievements;
