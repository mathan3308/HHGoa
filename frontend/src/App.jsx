import React, { useState, useEffect } from 'react';
import { Sparkles, Mic, Layers, Cpu, Code, BookOpen, Terminal, BarChart2 } from 'lucide-react';
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
    e.preventDefault();
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
    <div className="min-h-screen bg-[#030712] text-slate-100 p-4 md:p-8">
      <div className="max-w-6xl mx-auto space-y-8">
        
        {/* Header */}
        <header className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-6 border-b border-slate-800">
          <div>
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-indigo-600/20 border border-indigo-500/30 flex items-center justify-center text-indigo-400">
                <Mic className="w-6 h-6" />
              </div>
              <div>
                <h1 className="text-2xl md:text-3xl font-extrabold tracking-tight bg-gradient-to-r from-white via-slate-100 to-indigo-300 bg-clip-text text-transparent">
                  Voice-Enabled RAG System
                </h1>
                <p className="text-xs md:text-sm text-slate-400 font-medium">
                  HH Goa 2026 — Task 2 • Multi-Language MSMARCO-XI Knowledge Engine
                </p>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <span className="px-3 py-1 rounded-full text-xs font-mono font-medium bg-slate-900 border border-slate-800 text-slate-300">
              Qdrant + Sarvam AI
            </span>
            <span className="px-3 py-1 rounded-full text-xs font-mono font-medium bg-indigo-950/60 border border-indigo-800/60 text-indigo-300">
              Target &lt; 200ms
            </span>
          </div>
        </header>

        {/* System Health Overview */}
        <SystemStatus health={healthData} mockMode={healthData?.mock_mode} />

        {/* Main Grid Section */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          
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
              <div className="glass-panel rounded-2xl p-5 border border-slate-800 shadow-xl">
                <div className="flex items-center justify-between mb-3">
                  <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
                    <BarChart2 className="w-4 h-4 text-indigo-400" />
                    Latest Benchmark Metrics ({metricsSummary.query_count} queries)
                  </h3>
                </div>
                <div className="grid grid-cols-3 gap-2 font-mono text-center">
                  <div className="bg-slate-900/80 p-2.5 rounded-xl border border-slate-800">
                    <span className="text-[10px] text-slate-500 block uppercase">P50</span>
                    <span className="text-sm font-bold text-emerald-400">{metricsSummary.rag_latency.p50.toFixed(1)} ms</span>
                  </div>
                  <div className="bg-slate-900/80 p-2.5 rounded-xl border border-slate-800">
                    <span className="text-[10px] text-slate-500 block uppercase">P70</span>
                    <span className="text-sm font-bold text-cyan-400">{metricsSummary.rag_latency.p70.toFixed(1)} ms</span>
                  </div>
                  <div className="bg-slate-900/80 p-2.5 rounded-xl border border-slate-800">
                    <span className="text-[10px] text-slate-500 block uppercase">P100</span>
                    <span className="text-sm font-bold text-amber-400">{metricsSummary.rag_latency.p100.toFixed(1)} ms</span>
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
              <div className="glass-panel rounded-2xl p-12 border border-slate-800 text-center flex flex-col items-center justify-center min-h-[400px]">
                <div className="w-16 h-16 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400 mb-4 animate-bounce">
                  <Mic className="w-8 h-8" />
                </div>
                <h3 className="text-lg font-bold text-slate-200">Ready for Query Input</h3>
                <p className="text-sm text-slate-400 max-w-md mt-2 leading-relaxed">
                  Record your voice query or type a question to trigger the end-to-end RAG pipeline, retrieve MSMARCO-XI context, and validate grounding.
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Footer */}
        <footer className="pt-8 border-t border-slate-800 text-center text-xs text-slate-500 flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
            <span>HH Goa 2026 Production RAG Specification</span>
          </div>
          <div>
            Built with React, Vite, FastAPI, Qdrant & Sarvam AI
          </div>
        </footer>
      </div>
    </div>
  );
}
