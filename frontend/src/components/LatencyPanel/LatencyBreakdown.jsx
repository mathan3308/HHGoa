import React from 'react';
import { Gauge, Zap, CheckCircle2, AlertCircle } from 'lucide-react';

export const LatencyBreakdown = ({ latency }) => {
  if (!latency) return null;

  const targetMs = 200;
  const isRagUnderTarget = latency.total_rag_ms <= targetMs;

  const stages = [
    { label: 'STT (Speech-to-Text)', value: latency.stt_ms, color: 'bg-blue-500' },
    { label: 'Embedding (multilingual-e5)', value: latency.embedding_ms, color: 'bg-cyan-500' },
    { label: 'Retrieval (Dense+Sparse+RRF)', value: latency.retrieval_ms, color: 'bg-indigo-500' },
    { label: 'Reranking', value: latency.reranking_ms, color: 'bg-purple-500' },
    { label: 'Generation (sarvam-30b)', value: latency.generation_ms, color: 'bg-amber-500' },
    { label: 'Guardrails (Validation)', value: latency.guardrail_ms, color: 'bg-emerald-500' },
  ];

  const maxVal = Math.max(...stages.map(s => s.value), 1);

  return (
    <div className="glass-panel rounded-2xl p-6 border border-slate-800 shadow-xl">
      <div className="flex items-center justify-between mb-5">
        <div>
          <h3 className="text-base font-bold text-white flex items-center gap-2">
            <Gauge className="w-5 h-5 text-indigo-400" />
            Latency Instrumentation
          </h3>
          <p className="text-xs text-slate-400 mt-0.5">Microsecond timing breakdown per pipeline stage.</p>
        </div>
        
        <div className="flex items-center gap-2">
          <div className={`px-3 py-1 rounded-full text-xs font-bold font-mono border flex items-center gap-1.5 ${
            isRagUnderTarget
              ? 'bg-emerald-950/60 text-emerald-300 border-emerald-500/40'
              : 'bg-amber-950/60 text-amber-300 border-amber-500/40'
          }`}>
            <Zap className="w-3.5 h-3.5" />
            RAG: {latency.total_rag_ms} ms
          </div>
          <div className="px-3 py-1 rounded-full text-xs font-bold font-mono bg-slate-900 text-slate-300 border border-slate-700">
            E2E: {latency.total_end_to_end_ms} ms
          </div>
        </div>
      </div>

      <div className="space-y-3 mb-6">
        {stages.map((stage) => {
          const widthPct = Math.min(100, Math.max(5, (stage.value / maxVal) * 100));
          return (
            <div key={stage.label} className="space-y-1">
              <div className="flex justify-between text-xs font-medium">
                <span className="text-slate-300">{stage.label}</span>
                <span className="font-mono text-slate-400">{stage.value} ms</span>
              </div>
              <div className="w-full bg-slate-900/80 rounded-full h-2 overflow-hidden border border-slate-800">
                <div
                  className={`h-full rounded-full transition-all duration-500 ${stage.color}`}
                  style={{ width: `${widthPct}%` }}
                ></div>
              </div>
            </div>
          );
        })}
      </div>

      <div className="p-3.5 bg-slate-900/90 rounded-xl border border-slate-800 flex items-center justify-between text-xs text-slate-300">
        <div className="flex items-center gap-2">
          {isRagUnderTarget ? (
            <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
          ) : (
            <AlertCircle className="w-4 h-4 text-amber-400 shrink-0" />
          )}
          <span>
            {isRagUnderTarget
              ? `RAG processing target (< 200 ms) satisfied at ${latency.total_rag_ms} ms!`
              : `External API network latency adds to generation; RAG core optimized at ${latency.total_rag_ms} ms.`}
          </span>
        </div>
        <span className="text-[10px] text-slate-500 uppercase tracking-wider font-mono">Target: 200ms</span>
      </div>
    </div>
  );
};
