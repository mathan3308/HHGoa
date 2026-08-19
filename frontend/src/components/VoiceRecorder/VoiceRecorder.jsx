import React from 'react';
import { Mic, Square, Loader2, Sparkles, HelpCircle, ArrowRight } from 'lucide-react';

const SAMPLE_QUERIES = [
  { label: '🌿 Photosynthesis', query: 'How does photosynthesis help plants survive?' },
  { label: '🏛 Capital of India', query: 'What is the capital city of India?' },
  { label: '🇮🇳 President of India', query: 'Who is the President of India?' },
  { label: '🚀 ISRO Missions', query: 'What is ISRO and its famous space missions?' },
  { label: '⚡ Qdrant Vector DB', query: 'What is Qdrant vector search engine?' },
  { label: '🤖 Machine Learning', query: 'What is Machine Learning?' },
  { label: '🏏 Cricket in India', query: 'Tell me about cricket in India' },
  { label: '🏔 Himalayas', query: 'What are the Himalayas?' }
];

export const VoiceRecorder = ({
  isRecording,
  recordingTime,
  status,
  onStart,
  onStop,
  onTextSubmit,
  textQuery,
  setTextQuery,
  error
}) => {
  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const isProcessing = ['UPLOADING', 'TRANSCRIBING', 'RETRIEVING', 'GENERATING', 'VALIDATING'].includes(status);

  const handleChipClick = (queryText) => {
    setTextQuery(queryText);
  };

  return (
    <div className="glass-panel rounded-3xl p-6 md:p-8 border border-slate-800 shadow-2xl relative overflow-hidden">
      {/* Background Subtle Ambient Glow */}
      <div className="absolute top-0 right-0 w-72 h-72 bg-indigo-600/10 rounded-full blur-3xl -mr-20 -mt-20 pointer-events-none"></div>
      <div className="absolute bottom-0 left-0 w-72 h-72 bg-purple-600/10 rounded-full blur-3xl -ml-20 -mb-20 pointer-events-none"></div>

      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2.5">
            <div className="p-2 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-400">
              <Mic className="w-5 h-5" />
            </div>
            <span>Voice & Text Query Engine</span>
          </h2>
          <p className="text-xs text-slate-400 mt-1">Speak into your mic or pick a sample question below to query the dataset.</p>
        </div>
        <span className={`px-3 py-1 rounded-full text-[11px] font-mono font-bold uppercase tracking-wider ${
          isRecording ? 'bg-rose-500/20 text-rose-300 border border-rose-500/40 badge-glow-amber' :
          isProcessing ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40' :
          'bg-slate-800/80 text-slate-400 border border-slate-700/80'
        }`}>
          {isRecording ? 'RECORDING' : status}
        </span>
      </div>

      {/* Voice Button Section */}
      <div className="flex flex-col items-center justify-center py-6 bg-slate-900/40 rounded-2xl border border-slate-800/60 p-6 relative">
        <button
          onClick={isRecording ? onStop : onStart}
          disabled={isProcessing}
          className={`relative group w-28 h-28 rounded-full flex items-center justify-center transition-all duration-300 transform active:scale-95 ${
            isRecording
              ? 'bg-rose-600 hover:bg-rose-500 text-white recording-pulse shadow-2xl shadow-rose-600/50'
              : isProcessing
              ? 'bg-slate-800 text-slate-600 cursor-not-allowed border border-slate-700'
              : 'bg-gradient-to-tr from-indigo-600 via-indigo-500 to-purple-600 text-white hover:shadow-2xl hover:shadow-indigo-500/40 hover:scale-105 border border-indigo-400/30'
          }`}
          title={isRecording ? "Click to stop recording" : "Click to start recording voice"}
        >
          {isProcessing ? (
            <Loader2 className="w-12 h-12 animate-spin" />
          ) : isRecording ? (
            <Square className="w-10 h-10 fill-current" />
          ) : (
            <Mic className="w-12 h-12 group-hover:scale-110 transition-transform" />
          )}
        </button>

        {/* Audio Wave Visualizer when Recording */}
        {isRecording && (
          <div className="flex items-center gap-1.5 mt-4">
            <span className="w-1.5 bg-rose-500 rounded-full wave-bar"></span>
            <span className="w-1.5 bg-rose-400 rounded-full wave-bar"></span>
            <span className="w-1.5 bg-rose-500 rounded-full wave-bar"></span>
            <span className="w-1.5 bg-rose-400 rounded-full wave-bar"></span>
            <span className="w-1.5 bg-rose-500 rounded-full wave-bar"></span>
          </div>
        )}

        <div className="mt-4 text-center">
          {isRecording ? (
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-rose-500 animate-ping"></span>
              <span className="text-xl font-mono font-extrabold text-rose-400">{formatTime(recordingTime)}</span>
            </div>
          ) : (
            <p className="text-sm font-medium text-slate-300">
              {isProcessing ? 'Processing query through Sarvam AI pipeline...' : 'Click microphone to record voice'}
            </p>
          )}
        </div>
      </div>

      {error && (
        <div className="mt-4 p-3.5 bg-rose-950/60 border border-rose-800/80 rounded-xl text-xs text-rose-300 flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-rose-500"></span>
          <span>{error}</span>
        </div>
      )}

      {/* Text Query Input */}
      <div className="mt-6">
        <form onSubmit={onTextSubmit} className="flex gap-2">
          <input
            type="text"
            value={textQuery}
            onChange={(e) => setTextQuery(e.target.value)}
            placeholder="Type your question or click a sample below..."
            disabled={isProcessing || isRecording}
            className="flex-1 bg-slate-900/90 border border-slate-700/80 rounded-xl px-4 py-3 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 transition-all disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={isProcessing || isRecording || !textQuery.trim()}
            className="bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 disabled:bg-slate-800 disabled:text-slate-600 text-white font-semibold px-5 py-3 rounded-xl text-sm transition-all flex items-center gap-2 shadow-lg shadow-indigo-600/25 active:scale-95"
          >
            <Sparkles className="w-4 h-4 text-indigo-200" />
            <span>Search</span>
          </button>
        </form>
      </div>

      {/* Quick Sample Query Chips */}
      <div className="mt-5">
        <label className="text-[11px] font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1 mb-2.5">
          <HelpCircle className="w-3.5 h-3.5 text-indigo-400" />
          Suggested Dataset Questions (Click to populate)
        </label>
        <div className="flex flex-wrap gap-2">
          {SAMPLE_QUERIES.map((sq, i) => (
            <button
              key={i}
              type="button"
              onClick={() => handleChipClick(sq.query)}
              disabled={isProcessing || isRecording}
              className="text-xs bg-slate-900/80 hover:bg-indigo-950/80 hover:border-indigo-500/50 text-slate-300 hover:text-indigo-200 border border-slate-800 px-3 py-1.5 rounded-lg transition-all text-left flex items-center gap-1.5 glass-card-hover disabled:opacity-50"
            >
              <span>{sq.label}</span>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};
