import React from 'react';
import { Activity, Server, Database, Mic, Cpu } from 'lucide-react';

export const SystemStatus = ({ health, mockMode }) => {
  const getStatusBadge = (status) => {
    const isOk = status === 'ok' || status === 'healthy' || status === 'sarvam';
    const isMock = status === 'mock';
    return (
      <span className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-semibold font-mono ${
        isOk
          ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
          : isMock
          ? 'bg-amber-500/10 text-amber-300 border border-amber-500/20'
          : 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
      }`}>
        <span className={`w-1.5 h-1.5 rounded-full ${isOk ? 'bg-emerald-400 animate-pulse' : isMock ? 'bg-amber-400' : 'bg-rose-400'}`}></span>
        {status ? status.toUpperCase() : 'UNKNOWN'}
      </span>
    );
  };

  const services = health?.services || {};

  return (
    <div className="glass-panel rounded-2xl p-5 border border-slate-800 shadow-xl">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-semibold text-slate-300 flex items-center gap-2">
          <Activity className="w-4 h-4 text-indigo-400" />
          System Health Monitor
        </h3>
        {mockMode && (
          <span className="text-[10px] bg-indigo-950/80 text-indigo-300 border border-indigo-700/60 px-2 py-0.5 rounded-full font-mono uppercase">
            Development Mode
          </span>
        )}
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <div className="glass-card p-3 rounded-xl border border-slate-800/80 flex flex-col justify-between">
          <div className="flex items-center gap-2 text-slate-400 text-xs mb-2">
            <Server className="w-3.5 h-3.5 text-indigo-400" />
            <span>FastAPI Backend</span>
          </div>
          {getStatusBadge(services.api || 'checking')}
        </div>

        <div className="glass-card p-3 rounded-xl border border-slate-800/80 flex flex-col justify-between">
          <div className="flex items-center gap-2 text-slate-400 text-xs mb-2">
            <Database className="w-3.5 h-3.5 text-indigo-400" />
            <span>Qdrant Vector DB</span>
          </div>
          {getStatusBadge(services.qdrant || 'checking')}
        </div>

        <div className="glass-card p-3 rounded-xl border border-slate-800/80 flex flex-col justify-between">
          <div className="flex items-center gap-2 text-slate-400 text-xs mb-2">
            <Mic className="w-3.5 h-3.5 text-indigo-400" />
            <span>Sarvam STT Engine</span>
          </div>
          {getStatusBadge(services.stt || 'checking')}
        </div>

        <div className="glass-card p-3 rounded-xl border border-slate-800/80 flex flex-col justify-between">
          <div className="flex items-center gap-2 text-slate-400 text-xs mb-2">
            <Cpu className="w-3.5 h-3.5 text-indigo-400" />
            <span>Sarvam LLM Engine</span>
          </div>
          {getStatusBadge(services.llm || 'checking')}
        </div>
      </div>
    </div>
  );
};
