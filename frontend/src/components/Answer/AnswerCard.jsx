import React from 'react';
import { Bot, CheckCircle2, AlertTriangle, ShieldCheck, HelpCircle } from 'lucide-react';

export const AnswerCard = ({ answer, grounded, groundingDetails, mockMode }) => {
  if (!answer) return null;

  const isGrounded = grounded === true;
  const isRefusal = answer.includes("couldn't find") || answer.includes("Refusal");

  return (
    <div className="glass-panel rounded-2xl p-6 border border-slate-800 shadow-2xl relative">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-bold text-white flex items-center gap-2">
          <Bot className="w-5 h-5 text-indigo-400" />
          Generated Response
        </h3>
        
        <div className="flex items-center gap-2">
          {mockMode && (
            <span className="text-xs bg-amber-950/60 text-amber-300 border border-amber-800/80 px-2.5 py-1 rounded-full font-medium">
              Demo Mock Mode
            </span>
          )}

          <div className={`flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider ${
            isRefusal ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30' :
            isGrounded ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30' :
            'bg-rose-500/20 text-rose-300 border border-rose-500/30'
          }`}>
            {isRefusal ? (
              <>
                <HelpCircle className="w-3.5 h-3.5" />
                Insufficient Context
              </>
            ) : isGrounded ? (
              <>
                <ShieldCheck className="w-3.5 h-3.5" />
                Grounded
              </>
            ) : (
              <>
                <AlertTriangle className="w-3.5 h-3.5" />
                Ungrounded
              </>
            )}
          </div>
        </div>
      </div>

      <div className="bg-gradient-to-br from-slate-900/90 to-slate-950/90 p-5 rounded-xl border border-slate-800 text-slate-100 text-base leading-relaxed">
        {answer}
      </div>

      {groundingDetails && groundingDetails.reason && (
        <div className="mt-3 text-xs text-slate-400 flex items-center justify-between px-1">
          <span>Grounding Validator: <strong className="text-slate-300">{groundingDetails.reason}</strong></span>
          {groundingDetails.confidence !== null && (
            <span className="font-mono text-emerald-400">Confidence: {(groundingDetails.confidence * 100).toFixed(0)}%</span>
          )}
        </div>
      )}
    </div>
  );
};
