import React, { useState } from 'react';
import { Database, ChevronDown, ChevronUp, FileText } from 'lucide-react';

export const SourcesList = ({ sources }) => {
  const [expanded, setExpanded] = useState(true);

  if (!sources || sources.length === 0) return null;

  return (
    <div className="glass-panel rounded-3xl p-6 border border-slate-800 shadow-2xl">
      <div
        onClick={() => setExpanded(!expanded)}
        className="flex items-center justify-between cursor-pointer select-none"
      >
        <div className="flex items-center gap-2.5">
          <div className="p-2 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-400">
            <Database className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-bold text-white">Retrieved Context Passages ({sources.length})</h3>
            <p className="text-xs text-slate-400">Grounding source documents retrieved from Qdrant + BM25 index</p>
          </div>
        </div>

        <button className="p-2 rounded-xl bg-slate-800/80 hover:bg-slate-700 text-slate-300 transition-colors">
          {expanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </button>
      </div>

      {expanded && (
        <div className="mt-5 space-y-3.5">
          {sources.map((src, idx) => (
            <div key={src.chunk_id || idx} className="glass-card glass-card-hover p-4 md:p-5 rounded-2xl border border-slate-800">
              <div className="flex flex-wrap items-center justify-between text-xs text-slate-400 mb-2.5 gap-2">
                <div className="flex items-center gap-2">
                  <FileText className="w-4 h-4 text-indigo-400" />
                  <span className="font-mono text-slate-200 font-bold text-sm">{src.source_id || `Source_${idx+1}`}</span>
                  <span className="bg-slate-800 text-indigo-300 border border-slate-700 px-2 py-0.5 rounded-md text-[10px] uppercase font-mono font-bold">
                    {src.chunk_strategy || 'semantic'}
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="bg-indigo-950 text-indigo-300 border border-indigo-800/60 px-2 py-0.5 rounded-md text-[10px] uppercase font-mono font-bold">
                    {src.language || 'EN'}
                  </span>
                  {src.relevance_score !== undefined && (
                    <span className="text-emerald-400 bg-emerald-950/60 border border-emerald-800/60 px-2.5 py-0.5 rounded-md font-mono font-bold">
                      Match Score: {(src.relevance_score * 100).toFixed(1)}%
                    </span>
                  )}
                </div>
              </div>
              <p className="text-xs md:text-sm text-slate-200 leading-relaxed font-normal bg-slate-950/80 p-3.5 rounded-xl border border-slate-900">
                "{src.text}"
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
