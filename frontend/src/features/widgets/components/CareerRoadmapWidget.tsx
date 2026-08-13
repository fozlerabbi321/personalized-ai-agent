"use client";

import React, { useState } from "react";
import { CareerRoadmapWidgetPayload, CareerPhase } from "../types";
import { Map, Target, Clock, DollarSign, ChevronDown, ChevronUp, CheckCircle2, Award } from "lucide-react";

function PhaseCard({ phase, isLast }: { phase: CareerPhase; isLast: boolean }) {
  const [open, setOpen] = useState(phase.phase === 1);

  return (
    <div className="flex gap-3">
      {/* Timeline */}
      <div className="flex flex-col items-center">
        <div className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-black shrink-0 ${open ? "bg-blue-500 text-white" : "bg-white/10 text-white/50"}`}>
          P{phase.phase}
        </div>
        {!isLast && <div className="w-px flex-1 bg-white/8 mt-1" />}
      </div>

      {/* Content */}
      <div className={`flex-1 mb-3 rounded-xl border transition-all duration-200 overflow-hidden ${open ? "border-blue-500/25 bg-blue-500/5" : "border-white/8 bg-white/3"}`}>
        <button
          onClick={() => setOpen(!open)}
          className="w-full flex items-center justify-between px-3 py-2.5 text-left"
        >
          <div className="flex-1 min-w-0">
            <p className={`text-sm font-semibold truncate ${open ? "text-white" : "text-white/60"}`}>{phase.title}</p>
            <div className="flex items-center gap-2 mt-0.5">
              <Clock className="w-3 h-3 text-white/30" />
              <span className="text-xs text-white/40">{phase.timeframe}</span>
            </div>
          </div>
          {open ? <ChevronUp className="w-4 h-4 text-white/30 shrink-0 ml-2" /> : <ChevronDown className="w-4 h-4 text-white/30 shrink-0 ml-2" />}
        </button>

        {open && (
          <div className="px-3 pb-3 space-y-2.5">
            {/* Milestones */}
            <div className="space-y-1">
              <p className="text-xs text-blue-300 font-semibold uppercase tracking-wide">Milestones</p>
              {phase.milestones.map((m, i) => (
                <div key={i} className="flex items-start gap-1.5 text-xs text-white/70">
                  <CheckCircle2 className="w-3.5 h-3.5 text-blue-400 shrink-0 mt-0.5" />
                  <span>{m}</span>
                </div>
              ))}
            </div>

            {/* Skills */}
            {phase.skills_to_acquire?.length > 0 && (
              <div>
                <p className="text-xs text-white/40 mb-1">Key Competencies:</p>
                <div className="flex flex-wrap gap-1.5">
                  {phase.skills_to_acquire.map((sk, i) => (
                    <span key={i} className="text-xs px-2 py-0.5 rounded-full bg-blue-500/15 text-blue-300">
                      {sk}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export function CareerRoadmapWidget(props: CareerRoadmapWidgetPayload) {
  return (
    <div className="my-3 rounded-2xl border border-white/10 bg-gradient-to-b from-white/5 to-transparent backdrop-blur-sm overflow-hidden">
      {/* Header */}
      <div className="px-4 py-3.5 border-b border-white/8 bg-gradient-to-r from-blue-500/15 to-indigo-500/5">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-xl bg-blue-500/20 flex items-center justify-center">
              <Map className="w-4 h-4 text-blue-400" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-white">Career Growth Plan</h3>
              <p className="text-xs text-white/40">{props.current_role} → {props.target_role}</p>
            </div>
          </div>
          <div className="flex items-center gap-1 text-xs px-2.5 py-1 rounded-full bg-blue-500/20 text-blue-300 font-bold">
            <DollarSign className="w-3.5 h-3.5" />
            <span>{props.salary_range}</span>
          </div>
        </div>
      </div>

      <div className="p-4">
        {/* Phases */}
        {props.phases.map((phase, i) => (
          <PhaseCard key={phase.phase} phase={phase} isLast={i === props.phases.length - 1} />
        ))}

        {/* Key Success Metric */}
        {props.key_metric && (
          <div className="mt-2 flex items-center gap-2 p-3 rounded-xl bg-blue-500/10 border border-blue-500/20">
            <Award className="w-4 h-4 text-blue-400 shrink-0" />
            <p className="text-xs font-semibold text-blue-300">Promotion Goal: {props.key_metric}</p>
          </div>
        )}
      </div>
    </div>
  );
}
