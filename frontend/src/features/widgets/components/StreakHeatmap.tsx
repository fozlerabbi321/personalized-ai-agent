"use client";

import React from "react";
import { StreakHeatmapPayload } from "../types";
import { Flame, Zap, Calendar } from "lucide-react";

function getColor(count: number): string {
  if (count === 0) return "rgba(255,255,255,0.05)";
  if (count === 1) return "#FF6B3540";
  if (count === 2) return "#FF6B3570";
  if (count === 3) return "#FF6B35A0";
  return "#FF6B35";
}

export function StreakHeatmap(props: StreakHeatmapPayload) {
  const dayLabels = ["M", "W", "F"];

  return (
    <div className="my-3 rounded-2xl border border-white/10 bg-gradient-to-b from-white/5 to-transparent backdrop-blur-sm overflow-hidden">
      {/* Header */}
      <div className="px-4 py-3 border-b border-white/8 bg-gradient-to-r from-orange-500/10 to-transparent">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-xl bg-orange-500/20 flex items-center justify-center">
              <Flame className="w-4 h-4 text-orange-400" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-white">Workout Consistency</h3>
              <p className="text-xs text-white/50">Last 12 weeks</p>
            </div>
          </div>
          <div className="text-right">
            <div className="flex items-center gap-1 justify-end">
              <Zap className="w-3.5 h-3.5 text-orange-400" />
              <span className="text-sm font-black text-white">{props.current_streak}</span>
              <span className="text-xs text-white/40">day streak</span>
            </div>
            <div className="flex items-center gap-1 justify-end mt-0.5">
              <Calendar className="w-3 h-3 text-white/30" />
              <span className="text-xs text-white/40">{props.total_workouts} total</span>
            </div>
          </div>
        </div>
      </div>

      <div className="p-4">
        {/* Day labels */}
        <div className="flex gap-1 mb-1 ml-5">
          {["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"].map((d) => (
            <div key={d} className="w-4 text-center text-xs text-white/20 flex-1">{d[0]}</div>
          ))}
        </div>

        {/* Heatmap grid */}
        <div className="space-y-1">
          {props.weeks.map((week, wi) => (
            <div key={wi} className="flex items-center gap-1">
              <span className="text-xs text-white/20 w-4 text-right shrink-0">
                {wi % 3 === 0 ? `W${wi + 1}` : ""}
              </span>
              <div className="flex gap-1 flex-1">
                {week.map((day, di) => (
                  <div
                    key={di}
                    className="flex-1 aspect-square rounded-sm transition-all duration-200 hover:scale-110 cursor-default"
                    style={{ background: getColor(day.count) }}
                    title={`${day.date}: ${day.count} workout${day.count !== 1 ? "s" : ""}`}
                  />
                ))}
              </div>
            </div>
          ))}
        </div>

        {/* Legend */}
        <div className="flex items-center justify-end gap-1.5 mt-3">
          <span className="text-xs text-white/30">Less</span>
          {[0, 1, 2, 3, 4].map((level) => (
            <div
              key={level}
              className="w-3 h-3 rounded-sm"
              style={{ background: getColor(level) }}
            />
          ))}
          <span className="text-xs text-white/30">More</span>
        </div>

        {/* Streak stats */}
        <div className="grid grid-cols-3 gap-2 mt-3 text-center">
          {[
            { label: "Current Streak", value: `${props.current_streak}d` },
            { label: "Longest Streak", value: `${props.longest_streak}d` },
            { label: "Total Workouts", value: props.total_workouts.toString() },
          ].map(({ label, value }) => (
            <div key={label} className="bg-white/5 rounded-xl py-2 px-1">
              <p className="text-sm font-bold text-orange-400">{value}</p>
              <p className="text-xs text-white/40 mt-0.5 leading-tight">{label}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
