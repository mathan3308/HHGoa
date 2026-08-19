import React, { useState, useEffect } from 'react';
import { Mic, BarChart2, ShieldCheck, Sparkles, HelpCircle } from 'lucide-react';
import { useAudioRecorder } from './hooks/useAudioRecorder';
import { VoiceRecorder } from './components/VoiceRecorder/VoiceRecorder';
import { TranscriptCard } from './components/Transcript/TranscriptCard';
import { AnswerCard } from './components/Answer/AnswerCard';
import { SourcesList } from './components/Sources/SourcesList';
import { LatencyBreakdown } from './components/LatencyPanel/LatencyBreakdown';
import { SystemStatus } from './components/Status/SystemStatus';
import { sendVoiceQuery, sendTextQuery, checkHealth, fetchMetrics } from './services/api';

export default function App() {
  const {
    isRecording,
    recordingTime,
    audioBlob,
    error: recorderError,
    startRecording,
    stopRecording
  } = useAudioRecorder();

  const [pipelineStatus, setPipelineStatus] = useState('IDLE');
  const [textQuery, setTextQuery] = useState('');
  const [response, setResponse] = useState(null);
  const [apiError, setApiError] = useState(null);
  const [healthData, setHealthData] = useState(null);
  const [metricsSummary, setMetricsSummary] = useState(null);

  // Poll system health and benchmark metrics
  useEffect(() => {
    const loadHealth = async () => {
      try {
        const h = await checkHealth();
        setHealthData(h);
      } catch (err) {
        setHealthData({ status: 'offline', services: { api: 'offline', qdrant: 'offline' } });
      }
    };

    const loadMetrics = async () => {
      try {
        const m = await fetchMetrics();
        setMetricsSummary(m);
      } catch (err) {
        // Silently skip if metrics not yet recorded
      }
    };

    loadHealth();
    loadMetrics();
    const interval = setInterval(loadHealth, 10000);
    return () => clearInterval(interval);
  }, []);

  // Handle recorded audio submission when recording stops
  useEffect(() => {
    if (audioBlob && !isRecording) {
      handleVoiceQuerySubmit(audioBlob);
    }
  }, [audioBlob, isRecording]);

  const handleVoiceQuerySubmit = async (blob) => {
    setPipelineStatus('UPLOADING');
    setApiError(null);
    try {
      setPipelineStatus('TRANSCRIBING');
      const res = await sendVoiceQuery(blob);
      setResponse(res);
      setPipelineStatus('COMPLETED');
    } catch (err) {
      setApiError(err.response?.data?.detail || err.message || 'Voice RAG Pipeline error');
      setPipelineStatus('ERROR');
    }
  };

  const handleTextQuerySubmit = async (e) => {
    if (e && e.preventDefault) e.preventDefault();
    if (!textQuery.trim()) return;

    setPipelineStatus('RETRIEVING');
    setApiError(null);
    try {
      const res = await sendTextQuery(textQuery);
      setResponse(res);
      setPipelineStatus('COMPLETED');
    } catch (err) {
      setApiError(err.response?.data?.detail || err.message || 'Text RAG Pipeline error');
      setPipelineStatus('ERROR');
    }
  };

  return (
    <div className="min-h-screen bg-[#030712] text-slate-100 p-4 md:p-8 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-indigo-950/30 via-slate-950 to-[#030712]">
      <div className="max-w-7xl mx-auto space-y-8">
        
        {/* Sleek Header */}
        <header className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-6 border-b border-slate-800/80">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-indigo-600 to-purple-600 flex items-center justify-center text-white shadow-lg shadow-indigo-600/30 border border-indigo-400/30">
              <Mic className="w-7 h-7" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-2xl md:text-3xl font-black tracking-tight bg-gradient-to-r from-white via-slate-100 to-indigo-300 bg-clip-text text-transparent">
                  Voice-Enabled RAG System
                </h1>
                <span className="bg-indigo-500/10 border border-indigo-500/30 text-indigo-300 text-[10px] font-mono px-2 py-0.5 rounded-full uppercase font-bold">
                  HH Goa 2026
                </span>
              </div>
              <p className="text-xs md:text-sm text-slate-400 font-medium mt-0.5">
                Task 2 • Multi-Language MSMARCO-XI Knowledge Engine Grounded on Sarvam AI
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2.5">
            <span className="px-3.5 py-1.5 rounded-full text-xs font-mono font-bold bg-slate-900/90 border border-slate-800 text-slate-300 shadow-md">
              Qdrant + BM25 Hybrid
            </span>
            <span className="px-3.5 py-1.5 rounded-full text-xs font-mono font-bold bg-indigo-950/80 border border-indigo-800/80 text-indigo-300 badge-glow-indigo shadow-md">
              Target &lt; 200ms
            </span>
          </div>
        </header>

        {/* System Health Overview */}
        <SystemStatus health={healthData} mockMode={healthData?.mock_mode} />

        {/* Main Grid Section */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          
          {/* Left Column: Voice Recorder & Inputs */}
          <div className="lg:col-span-5 space-y-6">
            <VoiceRecorder
              isRecording={isRecording}
              recordingTime={recordingTime}
              status={pipelineStatus}
              onStart={startRecording}
              onStop={stopRecording}
              onTextSubmit={handleTextQuerySubmit}
              textQuery={textQuery}
              setTextQuery={setTextQuery}
              error={recorderError || apiError}
            />

            {/* Benchmark Summary Metrics Card if available */}
            {metricsSummary && metricsSummary.rag_latency && (
              <div className="glass-panel rounded-3xl p-6 border border-slate-800 shadow-xl">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-2">
                    <BarChart2 className="w-4 h-4 text-indigo-400" />
                    Empirical Latency Benchmark ({metricsSummary.query_count} queries)
                  </h3>
                </div>
                <div className="grid grid-cols-3 gap-3 font-mono text-center">
                  <div className="bg-slate-950 p-3 rounded-2xl border border-slate-800">
                    <span className="text-[10px] text-slate-500 block uppercase font-bold">P50 Latency</span>
                    <span className="text-base font-extrabold text-emerald-400">{metricsSummary.rag_latency.p50.toFixed(1)} ms</span>
                  </div>
                  <div className="bg-slate-950 p-3 rounded-2xl border border-slate-800">
                    <span className="text-[10px] text-slate-500 block uppercase font-bold">P70 Latency</span>
                    <span className="text-base font-extrabold text-cyan-400">{metricsSummary.rag_latency.p70.toFixed(1)} ms</span>
                  </div>
                  <div className="bg-slate-950 p-3 rounded-2xl border border-slate-800">
                    <span className="text-[10px] text-slate-500 block uppercase font-bold">P100 Latency</span>
                    <span className="text-base font-extrabold text-amber-400">{metricsSummary.rag_latency.p100.toFixed(1)} ms</span>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Right Column: Output Results & Instrumentation */}
          <div className="lg:col-span-7 space-y-6">
            
            {response ? (
              <>
                <TranscriptCard
                  transcript={response.transcript}
                  language={response.language}
                  latencyMs={response.latency?.stt_ms}
                />

                <AnswerCard
                  answer={response.answer}
                  grounded={response.grounded}
                  groundingDetails={response.grounding_details}
                  mockMode={response.mock_mode}
                />

                <LatencyBreakdown latency={response.latency} />

                <SourcesList sources={response.sources} />
              </>
            ) : (
              <div className="glass-panel rounded-3xl p-12 border border-slate-800/90 text-center flex flex-col items-center justify-center min-h-[440px] shadow-2xl relative overflow-hidden">
                <div className="w-20 h-20 rounded-3xl bg-indigo-500/10 border border-indigo-500/30 flex items-center justify-center text-indigo-400 mb-6 shadow-inner animate-pulse">
                  <Sparkles className="w-10 h-10" />
                </div>
                <h3 className="text-xl font-bold text-white">Ready for Query Input</h3>
                <p className="text-sm text-slate-400 max-w-md mt-2 leading-relaxed">
                  Record your voice query or select a sample question on the left to trigger hybrid Qdrant + BM25 retrieval, Sarvam-105B LLM answer generation, and grounding validation.
                </p>
                
                <div className="mt-8 flex flex-wrap items-center justify-center gap-3 text-xs text-slate-400">
                  <span className="flex items-center gap-1.5 bg-slate-900/90 px-3 py-1.5 rounded-xl border border-slate-800">
                    <ShieldCheck className="w-4 h-4 text-emerald-400" /> Grounding Protection
                  </span>
                  <span className="flex items-center gap-1.5 bg-slate-900/90 px-3 py-1.5 rounded-xl border border-slate-800">
                    <BarChart2 className="w-4 h-4 text-cyan-400" /> Microsecond Latency
                  </span>
                  <span className="flex items-center gap-1.5 bg-slate-900/90 px-3 py-1.5 rounded-xl border border-slate-800">
                    <HelpCircle className="w-4 h-4 text-indigo-400" /> MSMARCO-XI Knowledge
                  </span>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Footer */}
        <footer className="pt-8 border-t border-slate-800/80 text-center text-xs text-slate-500 flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse"></span>
            <span className="font-semibold text-slate-400">HH Goa 2026 Production RAG Specification — Task 2 Submission</span>
          </div>
          <div>
            Built with React, Vite, FastAPI, Qdrant Vector DB & Sarvam AI (Saaras v3 + Sarvam-105B)
          </div>
        </footer>
      </div>
    </div>
  );
}
