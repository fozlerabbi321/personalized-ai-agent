"use client";

import React, { useState } from "react";
import { Dumbbell, Clock, Target, ChevronDown, ChevronUp, CheckCircle2, Circle } from "lucide-react";
import { WorkoutPlanWidgetPayload, ExerciseItem } from "../types";

const MUSCLE_COLORS: Record<string, string> = {
  chest: "#FF6B35", back: "#FF8C42", shoulders: "#FFA500",
  legs: "#FFB347", biceps: "#FF7F50", triceps: "#FF6347",
  core: "#FF4500", full_body: "#FF6B35",
};

const EQUIPMENT_EMOJI: Record<string, string> = {
  barbell: "🏋️", dumbbells: "💪", cable_machine: "🔗",
  bodyweight: "🤸", pull_up_bar: "⬆️", resistance_bands: "🔄",
  leg_press_machine: "🦵", bench: "🪑", default: "🏃",
};

function ExerciseRow({ ex, index }: { ex: ExerciseItem; index: number }) {
  const [done, setDone] = useState(false);
  const emoji = EQUIPMENT_EMOJI[ex.equipment] ?? EQUIPMENT_EMOJI.default;
  const color = MUSCLE_COLORS[ex.muscle_group] ?? "#FF6B35";

  return (
    <div
      className={`flex items-center gap-3 p-3 rounded-xl transition-all duration-300 ${
        done ? "opacity-50 bg-white/3" : "bg-white/5 hover:bg-white/8"
      }`}
    >
      <button
        onClick={() => setDone(!done)}
        className="shrink-0 text-orange-400 hover:text-orange-300 transition-colors"
        aria-label={done ? "Mark incomplete" : "Mark complete"}
      >
        {done ? (
          <CheckCircle2 className="w-5 h-5" />
        ) : (
          <Circle className="w-5 h-5 text-white/30" />
        )}
      </button>

      <span className="text-lg shrink-0">{emoji}</span>

      <div className="flex-1 min-w-0">
        <p className={`text-sm font-semibold truncate ${done ? "line-through text-white/40" : "text-white"}`}>
          {ex.name}
        </p>
        <p className="text-xs text-white/40 mt-0.5 capitalize">{ex.type}</p>
      </div>

      <div className="flex items-center gap-3 shrink-0 text-right">
        <div className="text-center">
          <p className="text-sm font-bold text-white">{ex.sets}</p>
          <p className="text-xs text-white/40">sets</p>
        </div>
        <div className="text-white/30 text-xs">×</div>
        <div className="text-center">
          <p className="text-sm font-bold" style={{ color }}>{ex.reps}</p>
          <p className="text-xs text-white/40">reps</p>
        </div>
        <div className="text-center hidden sm:block">
          <p className="text-xs font-medium text-white/50">{ex.rest_seconds}s</p>
          <p className="text-xs text-white/30">rest</p>
        </div>
      </div>
    </div>
  );
}

export function WorkoutPlanWidget(props: WorkoutPlanWidgetPayload) {
  const [expanded, setExpanded] = useState(true);
  const color = MUSCLE_COLORS[props.muscle_group] ?? "#FF6B35";

  const goalLabel = props.goal.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
  const levelLabel = props.fitness_level.replace(/\b\w/g, (c) => c.toUpperCase());

  return (
    <div className="my-3 rounded-2xl border border-white/10 overflow-hidden bg-gradient-to-b from-white/5 to-transparent backdrop-blur-sm">
      {/* Header */}
      <div
        className="px-4 py-3 flex items-center justify-between cursor-pointer"
        style={{ background: `linear-gradient(135deg, ${color}18, ${color}08)` }}
        onClick={() => setExpanded(!expanded)}
      >
        <div className="flex items-center gap-3">
          <div
            className="w-9 h-9 rounded-xl flex items-center justify-center"
            style={{ background: `${color}25` }}
          >
            <Dumbbell className="w-5 h-5" style={{ color }} />
          </div>
          <div>
            <h3 className="text-sm font-bold text-white leading-tight">{props.title}</h3>
            <div className="flex items-center gap-2 mt-0.5">
              <span className="text-xs px-2 py-0.5 rounded-full font-medium" style={{ background: `${color}20`, color }}>
                {goalLabel}
              </span>
              <span className="text-xs text-white/40">{levelLabel}</span>
            </div>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <div className="text-right hidden sm:block">
            <div className="flex items-center gap-1.5 text-white/60">
              <Clock className="w-3.5 h-3.5" />
              <span className="text-xs">{props.estimated_duration_min} min</span>
            </div>
            <div className="flex items-center gap-1.5 text-white/60 mt-0.5">
              <Target className="w-3.5 h-3.5" />
              <span className="text-xs">{props.total_exercises} exercises</span>
            </div>
          </div>
          {expanded ? (
            <ChevronUp className="w-4 h-4 text-white/40" />
          ) : (
            <ChevronDown className="w-4 h-4 text-white/40" />
          )}
        </div>
      </div>

      {/* Exercise list */}
      {expanded && (
        <div className="px-3 pb-3 space-y-1.5 mt-1">
          {props.exercises.map((ex, i) => (
            <ExerciseRow key={i} ex={ex} index={i} />
          ))}
          <p className="text-center text-xs text-white/30 pt-2">{props.rep_scheme_note}</p>
        </div>
      )}
    </div>
  );
}
