import React, { useState } from 'react';
import { Database, ChevronDown, ChevronUp, FileText, Tag } from 'lucide-react';

export const SourcesList = ({ sources }) => {
  const [expanded, setExpanded] = useState(false);

  if (!sources || sources.length === 0) return null;

  return (
    <div className="glass-panel rounded-2xl p-5 border border-slate-800 shadow-xl">
      <div
        onClick={() => setExpanded(!expanded)}
        className="flex items-center justify-between cursor-pointer select-none"
      >
        <h3 className="text-sm font-semibold text-slate-300 flex items-center gap-2">
          <Database className="w-4 h-4 text-indigo-400" />
          Retrieved Context Passages ({sources.length})
        </h3>
        <button className="text-slate-400 hover:text-white transition-colors">
          {expanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </button>
      </div>

      {expanded && (
        <div className="mt-4 space-y-3">
          {sources.map((src, idx) => (
            <div key={src.chunk_id || idx} className="glass-card p-4 rounded-xl border border-slate-800/80">
              <div className="flex items-center justify-between text-xs text-slate-400 mb-2">
                <div className="flex items-center gap-2">
                  <FileText className="w-3.5 h-3.5 text-indigo-400" />
                  <span className="font-mono text-slate-300 font-semibold">{src.source_id || `Source_${idx+1}`}</span>
                  <span className="bg-slate-800 text-slate-300 px-2 py-0.5 rounded text-[10px] uppercase font-mono">
                    {src.chunk_strategy || 'semantic'}
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-indigo-300 bg-indigo-950/60 px-2 py-0.5 rounded text-[10px] uppercase font-mono">
                    {src.language || 'EN'}
                  </span>
                  <span className="text-emerald-400 font-mono font-bold">
                    Score: {(src.relevance_score * 100).toFixed(1)}%
                  </span>
                </div>
              </div>
              <p className="text-xs text-slate-300 leading-relaxed font-sans bg-slate-950/40 p-3 rounded-lg border border-slate-900">
                {src.text}
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
