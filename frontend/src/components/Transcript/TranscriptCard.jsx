import React from 'react';
import { MessageSquareText, Globe, Clock } from 'lucide-react';

export const TranscriptCard = ({ transcript, language, latencyMs }) => {
  if (!transcript) return null;

  return (
    <div className="glass-panel rounded-2xl p-5 border border-slate-800 shadow-xl">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-semibold text-slate-300 flex items-center gap-2">
          <MessageSquareText className="w-4 h-4 text-indigo-400" />
          Recognized Transcript
        </h3>
        <div className="flex items-center gap-3">
          <span className="flex items-center gap-1 text-xs text-indigo-300 bg-indigo-950/60 border border-indigo-800/60 px-2.5 py-0.5 rounded-full font-mono">
            <Globe className="w-3 h-3" />
            {language ? language.toUpperCase() : 'EN'}
          </span>
          {latencyMs > 0 && (
            <span className="flex items-center gap-1 text-xs text-emerald-400 bg-emerald-950/40 px-2 py-0.5 rounded-full font-mono">
              <Clock className="w-3 h-3" />
              {latencyMs}ms
            </span>
          )}
        </div>
      </div>
      <p className="text-slate-100 font-medium text-base bg-slate-900/60 p-4 rounded-xl border border-slate-800/60 leading-relaxed">
        "{transcript}"
      </p>
    </div>
  );
};
