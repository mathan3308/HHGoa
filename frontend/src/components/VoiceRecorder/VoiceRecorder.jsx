import React from 'react';
import { Mic, Square, Loader2, Sparkles } from 'lucide-react';

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

  return (
    <div className="glass-panel rounded-2xl p-6 border border-slate-800 shadow-2xl relative overflow-hidden">
      <div className="absolute top-0 right-0 w-64 h-64 bg-indigo-500/10 rounded-full blur-3xl -mr-20 -mt-20 pointer-events-none"></div>

      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Mic className="w-5 h-5 text-indigo-400" />
            Voice & Text Input
          </h2>
          <p className="text-xs text-slate-400 mt-1">Speak your question or type a query to search the dataset.</p>
        </div>
        <span className={`px-3 py-1 rounded-full text-xs font-semibold uppercase tracking-wider ${
          isRecording ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30' :
          isProcessing ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30' :
          'bg-slate-800 text-slate-400 border border-slate-700'
        }`}>
          {isRecording ? 'RECORDING' : status}
        </span>
      </div>

      <div className="flex flex-col items-center justify-center py-6">
        <button
          onClick={isRecording ? onStop : onStart}
          disabled={isProcessing}
          className={`relative group w-24 h-24 rounded-full flex items-center justify-center transition-all duration-300 transform active:scale-95 ${
            isRecording
              ? 'bg-rose-600 hover:bg-rose-500 text-white recording-pulse shadow-lg shadow-rose-600/50'
              : isProcessing
              ? 'bg-slate-800 text-slate-500 cursor-not-allowed border border-slate-700'
              : 'bg-gradient-to-tr from-indigo-600 via-indigo-500 to-purple-600 text-white hover:shadow-xl hover:shadow-indigo-500/30 hover:scale-105'
          }`}
          title={isRecording ? "Click to stop recording" : "Click to start recording voice"}
        >
          {isProcessing ? (
            <Loader2 className="w-10 h-10 animate-spin" />
          ) : isRecording ? (
            <Square className="w-8 h-8 fill-current" />
          ) : (
            <Mic className="w-10 h-10 group-hover:scale-110 transition-transform" />
          )}
        </button>

        <div className="mt-4 text-center">
          {isRecording ? (
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 rounded-full bg-rose-500 animate-ping"></span>
              <span className="text-lg font-mono font-bold text-rose-400">{formatTime(recordingTime)}</span>
            </div>
          ) : (
            <p className="text-sm font-medium text-slate-300">
              {isProcessing ? 'Processing query pipeline...' : 'Click microphone to record voice'}
            </p>
          )}
        </div>
      </div>

      {error && (
        <div className="mt-2 p-3 bg-rose-950/60 border border-rose-800/80 rounded-xl text-xs text-rose-300">
          {error}
        </div>
      )}

      <div className="mt-6 pt-6 border-t border-slate-800">
        <form onSubmit={onTextSubmit} className="flex gap-2">
          <input
            type="text"
            value={textQuery}
            onChange={(e) => setTextQuery(e.target.value)}
            placeholder="Or type a question (e.g. What is the capital of India?)..."
            disabled={isProcessing || isRecording}
            className="flex-1 bg-slate-900/80 border border-slate-700/80 rounded-xl px-4 py-2.5 text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-all disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={isProcessing || isRecording || !textQuery.trim()}
            className="bg-indigo-600 hover:bg-indigo-500 disabled:bg-slate-800 disabled:text-slate-600 text-white font-medium px-4 py-2.5 rounded-xl text-sm transition-all flex items-center gap-1.5 shadow-lg shadow-indigo-600/20"
          >
            <Sparkles className="w-4 h-4" />
            Query
          </button>
        </form>
      </div>
    </div>
  );
};
