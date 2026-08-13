"use client";

import React, { useState } from "react";
import { InterviewWidgetPayload } from "../types";
import { Briefcase, CheckCircle2, ChevronDown, ChevronUp, Sparkles, Target } from "lucide-react";

export function InterviewWidget(props: InterviewWidgetPayload) {
  const [showStarGuide, setShowStarGuide] = useState(true);

  return (
    <div className="my-3 rounded-2xl border border-white/10 bg-gradient-to-b from-white/5 to-transparent backdrop-blur-sm overflow-hidden">
      {/* Header */}
      <div className="px-4 py-3.5 border-b border-white/8 bg-gradient-to-r from-blue-500/15 to-indigo-500/5">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-xl bg-blue-500/20 flex items-center justify-center">
              <Briefcase className="w-4 h-4 text-blue-400" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-white">Mock Interview Question</h3>
              <p className="text-xs text-white/40">{props.target_role} · {props.category}</p>
            </div>
          </div>
          <span className="text-xs px-2.5 py-1 rounded-full bg-blue-500/20 text-blue-300 font-bold capitalize">
            {props.question_type.replace("_", " ")}
          </span>
        </div>
      </div>

      <div className="p-4 space-y-4">
        {/* Question */}
        <div className="p-3.5 rounded-xl bg-white/5 border border-white/8">
          <p className="text-xs font-semibold text-blue-400 uppercase tracking-wide mb-1">Interviewer Prompt</p>
          <p className="text-sm font-bold text-white leading-relaxed">"{props.question}"</p>
        </div>

        {/* Evaluation Criteria */}
        {props.evaluation_criteria?.length > 0 && (
          <div>
            <div className="flex items-center gap-1.5 mb-2 text-blue-400">
              <Target className="w-3.5 h-3.5" />
              <p className="text-xs font-semibold uppercase tracking-wide">What Top Interviewers Look For</p>
            </div>
            <div className="space-y-1.5">
              {props.evaluation_criteria.map((criterion, i) => (
                <div key={i} className="flex gap-2 text-xs text-white/70 bg-white/3 p-2 rounded-lg border border-white/5">
                  <CheckCircle2 className="w-3.5 h-3.5 text-blue-400 shrink-0 mt-0.5" />
                  <span>{criterion}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* STAR Method Guide */}
        {props.star_guide && (
          <div>
            <button
              onClick={() => setShowStarGuide(!showStarGuide)}
              className="flex items-center justify-between w-full p-2.5 rounded-xl bg-blue-500/10 border border-blue-500/20 text-left"
            >
              <div className="flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-blue-400" />
                <span className="text-xs font-bold text-blue-300">STAR Response Framework Guide</span>
              </div>
              {showStarGuide ? <ChevronUp className="w-4 h-4 text-blue-300" /> : <ChevronDown className="w-4 h-4 text-blue-300" />}
            </button>

            {showStarGuide && (
              <div className="mt-2 grid grid-cols-2 gap-2 text-xs">
                <div className="p-2.5 rounded-lg bg-white/4 border border-white/5">
                  <p className="font-bold text-blue-400 mb-0.5">S — Situation</p>
                  <p className="text-white/60 leading-tight">{props.star_guide.situation}</p>
                </div>
                <div className="p-2.5 rounded-lg bg-white/4 border border-white/5">
                  <p className="font-bold text-blue-400 mb-0.5">T — Task</p>
                  <p className="text-white/60 leading-tight">{props.star_guide.task}</p>
                </div>
                <div className="p-2.5 rounded-lg bg-white/4 border border-white/5">
                  <p className="font-bold text-blue-400 mb-0.5">A — Action</p>
                  <p className="text-white/60 leading-tight">{props.star_guide.action}</p>
                </div>
                <div className="p-2.5 rounded-lg bg-white/4 border border-white/5">
                  <p className="font-bold text-blue-400 mb-0.5">R — Result</p>
                  <p className="text-white/60 leading-tight">{props.star_guide.result}</p>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Sample Keywords */}
        {props.sample_keywords?.length > 0 && (
          <div>
            <p className="text-xs text-white/40 mb-1.5">High-Impact Keywords to Include:</p>
            <div className="flex flex-wrap gap-1.5">
              {props.sample_keywords.map((kw, i) => (
                <span key={i} className="text-xs px-2 py-0.5 rounded-md bg-blue-500/15 text-blue-300 font-mono">
                  {kw}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
