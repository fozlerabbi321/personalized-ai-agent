"use client";

import React from "react";
import { ExerciseCardPayload } from "../types";
import { AlertTriangle, CheckCircle, Gauge } from "lucide-react";

const DIFFICULTY_COLOR: Record<string, string> = {
  beginner:     "#22C55E",
  intermediate: "#FF6B35",
  advanced:     "#EF4444",
  elite:        "#A855F7",
};

export function ExerciseCard(props: ExerciseCardPayload) {
  const diffColor = DIFFICULTY_COLOR[props.difficulty] ?? "#FF6B35";

  return (
    <div className="my-3 rounded-2xl border border-white/10 bg-gradient-to-b from-white/5 to-transparent backdrop-blur-sm overflow-hidden">
      {/* Header */}
      <div className="px-4 py-3 border-b border-white/8 bg-gradient-to-r from-orange-500/10 to-transparent">
        <div className="flex items-start justify-between gap-2">
          <div>
            <h3 className="text-sm font-bold text-white">{props.name}</h3>
            <div className="flex flex-wrap gap-1.5 mt-1.5">
              <span className="text-xs px-2 py-0.5 rounded-full bg-orange-500/15 text-orange-400 font-medium">
                {props.muscle_primary}
              </span>
              {props.muscle_secondary && (
                <span className="text-xs px-2 py-0.5 rounded-full bg-white/8 text-white/50">
                  {props.muscle_secondary}
                </span>
              )}
              <span className="text-xs px-2 py-0.5 rounded-full bg-white/8 text-white/50 capitalize">
                🏋️ {props.equipment.replace(/_/g, " ")}
              </span>
            </div>
          </div>
          <div className="text-right shrink-0">
            <span
              className="text-xs px-2.5 py-1 rounded-full font-bold capitalize"
              style={{ background: `${diffColor}20`, color: diffColor }}
            >
              {props.difficulty}
            </span>
            <div className="flex items-center justify-end gap-1 mt-1.5">
              <Gauge className="w-3 h-3 text-white/40" />
              <span className="text-xs text-white/40">RPE {props.rpe_recommendation}</span>
            </div>
          </div>
        </div>
      </div>

      <div className="p-4 space-y-4">
        {/* Form cues */}
        <div>
          <div className="flex items-center gap-1.5 mb-2">
            <CheckCircle className="w-3.5 h-3.5 text-green-400" />
            <p className="text-xs font-semibold text-white/70 uppercase tracking-wide">Form Cues</p>
          </div>
          <ul className="space-y-1.5">
            {props.form_cues.map((cue, i) => (
              <li key={i} className="flex gap-2 text-xs text-white/60">
                <span className="text-orange-400 shrink-0">→</span>
                {cue}
              </li>
            ))}
          </ul>
        </div>

        {/* Common mistakes */}
        <div>
          <div className="flex items-center gap-1.5 mb-2">
            <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
            <p className="text-xs font-semibold text-white/70 uppercase tracking-wide">Common Mistakes</p>
          </div>
          <ul className="space-y-1.5">
            {props.common_mistakes.map((mistake, i) => (
              <li key={i} className="flex gap-2 text-xs text-white/60">
                <span className="text-amber-400 shrink-0">✗</span>
                {mistake}
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}
