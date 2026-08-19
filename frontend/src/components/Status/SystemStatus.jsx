import React from 'react';
import { Activity, Server, Database, Mic, Cpu, CheckCircle2 } from 'lucide-react';

export const SystemStatus = ({ health, mockMode }) => {
  const getStatusBadge = (status, labelExtra) => {
    const isOk = status === 'ok' || status === 'healthy' || status === 'sarvam';
    const isMock = status === 'mock';
    return (
      <div className="flex items-center justify-between mt-1">
        <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-[11px] font-bold font-mono ${
          isOk
            ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 badge-glow-emerald'
            : isMock
            ? 'bg-amber-500/10 text-amber-300 border border-amber-500/30 badge-glow-amber'
            : 'bg-rose-500/10 text-rose-400 border border-rose-500/30'
        }`}>
          <span className={`w-1.5 h-1.5 rounded-full ${isOk ? 'bg-emerald-400 animate-pulse' : isMock ? 'bg-amber-400' : 'bg-rose-400'}`}></span>
          {status ? status.toUpperCase() : 'CHECKING'}
        </span>
        {labelExtra && (
          <span className="text-[10px] text-slate-500 font-mono">{labelExtra}</span>
        )}
      </div>
    );
  };

  const services = health?.services || {};

  return (
    <div className="glass-panel rounded-3xl p-5 md:p-6 border border-slate-800 shadow-xl">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2.5">
          <div className="p-2 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-400">
            <Activity className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-slate-200">System Architecture & Health Monitor</h3>
            <p className="text-[11px] text-slate-400">Real-time status of backend services, vector database, and Sarvam AI models</p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 border border-emerald-500/30 text-emerald-300">
            <CheckCircle2 className="w-3.5 h-3.5" />
            Operational
          </span>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 md:gap-4">
        <div className="glass-card glass-card-hover p-3.5 rounded-2xl border border-slate-800/80 flex flex-col justify-between">
          <div className="flex items-center gap-2 text-slate-400 text-xs mb-1">
            <Server className="w-4 h-4 text-indigo-400" />
            <span className="font-semibold text-slate-300">FastAPI Backend</span>
          </div>
          {getStatusBadge(services.api || 'healthy', 'v1.0.0')}
        </div>

        <div className="glass-card glass-card-hover p-3.5 rounded-2xl border border-slate-800/80 flex flex-col justify-between">
          <div className="flex items-center gap-2 text-slate-400 text-xs mb-1">
            <Database className="w-4 h-4 text-indigo-400" />
            <span className="font-semibold text-slate-300">Qdrant Vector DB</span>
          </div>
          {getStatusBadge(services.qdrant || 'healthy', 'dense+sparse')}
        </div>

        <div className="glass-card glass-card-hover p-3.5 rounded-2xl border border-slate-800/80 flex flex-col justify-between">
          <div className="flex items-center gap-2 text-slate-400 text-xs mb-1">
            <Mic className="w-4 h-4 text-indigo-400" />
            <span className="font-semibold text-slate-300">Sarvam STT Engine</span>
          </div>
          {getStatusBadge(services.stt || 'sarvam', 'saaras:v3')}
        </div>

        <div className="glass-card glass-card-hover p-3.5 rounded-2xl border border-slate-800/80 flex flex-col justify-between">
          <div className="flex items-center gap-2 text-slate-400 text-xs mb-1">
            <Cpu className="w-4 h-4 text-indigo-400" />
            <span className="font-semibold text-slate-300">Sarvam LLM Engine</span>
          </div>
          {getStatusBadge(services.llm || 'sarvam', 'sarvam-105b')}
        </div>
      </div>
    </div>
  );
};
