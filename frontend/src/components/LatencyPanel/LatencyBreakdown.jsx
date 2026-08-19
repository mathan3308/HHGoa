import React from 'react';
import { Gauge, Zap, CheckCircle2, AlertCircle } from 'lucide-react';

export const LatencyBreakdown = ({ latency }) => {
  if (!latency) return null;

  const targetMs = 200;
  const isRagUnderTarget = latency.total_rag_ms <= targetMs;

  const stages = [
    { label: 'STT (Speech-to-Text)', value: latency.stt_ms, color: 'bg-violet-500' },
    { label: 'Embedding (multilingual-e5-small)', value: latency.embedding_ms, color: 'bg-cyan-400' },
    { label: 'Retrieval (Dense + Sparse + RRF)', value: latency.retrieval_ms, color: 'bg-indigo-500' },
    { label: 'Reranking', value: latency.reranking_ms, color: 'bg-purple-400' },
    { label: 'Generation (Sarvam-105b LLM)', value: latency.generation_ms, color: 'bg-emerald-400' },
    { label: 'Guardrails & Grounding Validation', value: latency.guardrail_ms, color: 'bg-amber-400' },
  ];

  const maxVal = Math.max(...stages.map(s => s.value), 1);

  return (
    <div className="glass-panel rounded-3xl p-6 md:p-8 border border-slate-800 shadow-2xl relative overflow-hidden">
      <div className="flex flex-col md:flex-row md:items-center justify-between mb-6 gap-3">
        <div>
          <h3 className="text-lg font-bold text-white flex items-center gap-2.5">
            <div className="p-2 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-400">
              <Gauge className="w-5 h-5" />
            </div>
            <span>Pipeline Latency & Telemetry</span>
          </h3>
          <p className="text-xs text-slate-400 mt-1">Stage-by-stage microsecond timing breakdown</p>
        </div>
        
        <div className="flex items-center gap-2">
          <div className={`px-3.5 py-1.5 rounded-full text-xs font-mono font-bold border flex items-center gap-1.5 ${
            isRagUnderTarget
              ? 'bg-emerald-950/60 text-emerald-300 border-emerald-500/40 badge-glow-emerald'
              : 'bg-amber-950/60 text-amber-300 border-amber-500/40 badge-glow-amber'
          }`}>
            <Zap className="w-4 h-4 text-emerald-400" />
            <span>RAG Core: {latency.total_rag_ms} ms</span>
          </div>
          <div className="px-3.5 py-1.5 rounded-full text-xs font-mono font-bold bg-slate-900 text-slate-200 border border-slate-700">
            E2E: {latency.total_end_to_end_ms} ms
          </div>
        </div>
      </div>

      <div className="space-y-3.5 mb-6">
        {stages.map((stage) => {
          const widthPct = Math.min(100, Math.max(4, (stage.value / maxVal) * 100));
          return (
            <div key={stage.label} className="space-y-1">
              <div className="flex justify-between text-xs font-medium">
                <span className="text-slate-300">{stage.label}</span>
                <span className="font-mono text-slate-400 font-semibold">{stage.value} ms</span>
              </div>
              <div className="w-full bg-slate-950/80 rounded-full h-2.5 overflow-hidden border border-slate-800">
                <div
                  className={`h-full rounded-full transition-all duration-500 ${stage.color}`}
                  style={{ width: `${widthPct}%` }}
                ></div>
              </div>
            </div>
          );
        })}
      </div>

      <div className="p-4 bg-slate-900/80 rounded-2xl border border-slate-800 flex items-center justify-between text-xs text-slate-300">
        <div className="flex items-center gap-2.5">
          {isRagUnderTarget ? (
            <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
          ) : (
            <AlertCircle className="w-4 h-4 text-amber-400 shrink-0" />
          )}
          <span>
            {isRagUnderTarget
              ? `Target latency (< 200 ms) satisfied cleanly at ${latency.total_rag_ms} ms!`
              : `External LLM generation latency is ${latency.generation_ms} ms; RAG core retrieval optimized at ${latency.total_rag_ms} ms.`}
          </span>
        </div>
        <span className="text-[10px] text-slate-500 uppercase tracking-wider font-mono font-bold">Target: &lt;200ms</span>
      </div>
    </div>
  );
};
