"use client";

import React, { useState } from "react";
import { QuizWidgetPayload } from "../types";
import { CheckCircle2, XCircle, Sparkles, Star } from "lucide-react";

const DIFFICULTY_COLOR: Record<string, string> = {
  beginner:     "#22C55E",
  intermediate: "#6366F1",
  advanced:     "#EF4444",
};

const SUBJECT_EMOJI: Record<string, string> = {
  Python: "🐍", JavaScript: "⚡", "Data Structures": "🌳",
  Algorithms: "🔢", "Machine Learning": "🧠", TypeScript: "💙",
  default: "📚",
};

export function QuizWidget(props: QuizWidgetPayload) {
  const [selected, setSelected]   = useState<string | null>(null);
  const [revealed, setRevealed]   = useState(false);
  const [showXP, setShowXP]       = useState(false);

  const diffColor = DIFFICULTY_COLOR[props.difficulty] ?? "#6366F1";
  const emoji     = SUBJECT_EMOJI[props.subject] ?? SUBJECT_EMOJI.default;

  function handleSelect(optId: string) {
    if (revealed) return;
    setSelected(optId);
  }

  function handleReveal() {
    if (!selected) return;
    setRevealed(true);
    if (selected === props.correct_answer) {
      setTimeout(() => setShowXP(true), 300);
    }
  }

  const isCorrect = selected === props.correct_answer;

  return (
    <div className="my-3 rounded-2xl border border-white/10 bg-gradient-to-b from-white/5 to-transparent backdrop-blur-sm overflow-hidden">
      {/* Header */}
      <div
        className="px-4 py-3 border-b border-white/8"
        style={{ background: `linear-gradient(135deg, ${diffColor}15, ${diffColor}05)` }}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-xl">{emoji}</span>
            <div>
              <h3 className="text-sm font-bold text-white">{props.subject} Quiz</h3>
              <p className="text-xs text-white/40">Q{props.question_no} · <span style={{ color: diffColor }} className="capitalize">{props.difficulty}</span></p>
            </div>
          </div>
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full" style={{ background: `${diffColor}18` }}>
            <Star className="w-3 h-3" style={{ color: diffColor }} />
            <span className="text-xs font-bold" style={{ color: diffColor }}>+{props.xp_reward} XP</span>
          </div>
        </div>
      </div>

      <div className="p-4">
        {/* Question */}
        <p className="text-sm font-semibold text-white leading-relaxed mb-4">{props.question}</p>

        {/* Options */}
        <div className="space-y-2">
          {props.options.map((opt) => {
            const isSelected = selected === opt.id;
            const isRight    = opt.id === props.correct_answer;
            let bg = "bg-white/5 hover:bg-white/8 border-white/10";
            let textColor = "text-white/80";
            if (revealed) {
              if (isRight)            { bg = "bg-green-500/15 border-green-500/40"; textColor = "text-green-300"; }
              else if (isSelected)    { bg = "bg-red-500/15 border-red-500/40";     textColor = "text-red-300"; }
              else                    { bg = "bg-white/3 border-white/5 opacity-50"; }
            } else if (isSelected) {
              bg = "bg-indigo-500/15 border-indigo-500/40"; textColor = "text-indigo-300";
            }

            return (
              <button
                key={opt.id}
                onClick={() => handleSelect(opt.id)}
                disabled={revealed}
                className={`w-full flex items-center gap-3 p-3 rounded-xl border transition-all duration-200 text-left ${bg} ${!revealed ? "cursor-pointer" : "cursor-default"}`}
              >
                <span className={`w-6 h-6 rounded-lg border flex items-center justify-center text-xs font-bold shrink-0 transition-all ${isSelected && !revealed ? "border-indigo-400 bg-indigo-500/20 text-indigo-300" : "border-white/20 text-white/40"}`}>
                  {opt.id}
                </span>
                <span className={`text-sm ${textColor}`}>{opt.text}</span>
                {revealed && isRight && <CheckCircle2 className="w-4 h-4 text-green-400 ml-auto shrink-0" />}
                {revealed && isSelected && !isRight && <XCircle className="w-4 h-4 text-red-400 ml-auto shrink-0" />}
              </button>
            );
          })}
        </div>

        {/* Submit button */}
        {!revealed && (
          <button
            onClick={handleReveal}
            disabled={!selected}
            className={`w-full mt-4 py-2.5 rounded-xl text-sm font-bold transition-all duration-200 ${selected ? "bg-indigo-600 hover:bg-indigo-500 text-white" : "bg-white/5 text-white/20 cursor-not-allowed"}`}
          >
            Check Answer
          </button>
        )}

        {/* Explanation */}
        {revealed && (
          <div className={`mt-4 p-3 rounded-xl ${isCorrect ? "bg-green-500/10 border border-green-500/20" : "bg-amber-500/10 border border-amber-500/20"}`}>
            <div className="flex items-center gap-2 mb-1.5">
              {isCorrect
                ? <CheckCircle2 className="w-4 h-4 text-green-400 shrink-0" />
                : <XCircle className="w-4 h-4 text-amber-400 shrink-0" />
              }
              <span className={`text-xs font-bold ${isCorrect ? "text-green-400" : "text-amber-400"}`}>
                {isCorrect ? "Correct! 🎉" : `Incorrect — correct answer: ${props.correct_answer}`}
              </span>
            </div>
            <p className="text-xs text-white/60 leading-relaxed">{props.explanation}</p>
          </div>
        )}

        {/* XP toast */}
        {showXP && (
          <div className="mt-3 flex items-center justify-center gap-2 py-2 rounded-xl bg-indigo-500/15 border border-indigo-500/20 animate-pulse">
            <Sparkles className="w-4 h-4 text-indigo-400" />
            <span className="text-sm font-bold text-indigo-300">+{props.xp_reward} XP earned!</span>
          </div>
        )}
      </div>
    </div>
  );
}
