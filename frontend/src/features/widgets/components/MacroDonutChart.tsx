"use client";

import React from "react";
import { MacroDonutChartPayload } from "../types";
import { Flame, Beef, Wheat, Droplets } from "lucide-react";

const MACRO_CONFIG = [
  { key: "protein_g",  pctKey: "protein_pct", label: "Protein", color: "#FF6B35", icon: Beef,     cal: 4 },
  { key: "carbs_g",    pctKey: "carbs_pct",   label: "Carbs",   color: "#22C55E", icon: Wheat,    cal: 4 },
  { key: "fat_g",      pctKey: "fat_pct",     label: "Fat",     color: "#3B82F6", icon: Droplets, cal: 9 },
] as const;

function SvgDonut({ macros }: { macros: MacroDonutChartPayload["macros"] }) {
  const cx = 60, cy = 60, r = 45, strokeW = 12;
  const circumference = 2 * Math.PI * r;

  const segments = [
    { pct: macros.protein_pct, color: "#FF6B35" },
    { pct: macros.carbs_pct,   color: "#22C55E" },
    { pct: macros.fat_pct,     color: "#3B82F6" },
  ];

  let offset = 0;
  const arcs = segments.map((seg) => {
    const dash = (seg.pct / 100) * circumference;
    const gap  = circumference - dash;
    const rotate = (offset / 100) * 360 - 90;
    offset += seg.pct;
    return { dash, gap, rotate, color: seg.color };
  });

  return (
    <svg width="120" height="120" viewBox="0 0 120 120">
      {/* background track */}
      <circle cx={cx} cy={cy} r={r} fill="none" stroke="rgba(255,255,255,0.06)" strokeWidth={strokeW} />
      {arcs.map((arc, i) => (
        <circle
          key={i}
          cx={cx} cy={cy} r={r}
          fill="none"
          stroke={arc.color}
          strokeWidth={strokeW}
          strokeDasharray={`${arc.dash} ${arc.gap}`}
          strokeLinecap="butt"
          transform={`rotate(${arc.rotate} ${cx} ${cy})`}
          style={{ transition: "stroke-dasharray 0.6s ease" }}
        />
      ))}
    </svg>
  );
}

export function MacroDonutChart(props: MacroDonutChartPayload) {
  const goalLabel = props.goal.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
  const strategyColor = props.calorie_strategy.includes("+") ? "#22C55E"
    : props.calorie_strategy.includes("-") ? "#EF4444" : "#FF6B35";

  return (
    <div className="my-3 rounded-2xl border border-white/10 bg-gradient-to-b from-white/5 to-transparent backdrop-blur-sm overflow-hidden">
      {/* Header */}
      <div className="px-4 py-3 border-b border-white/8 bg-gradient-to-r from-orange-500/10 to-green-500/5">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-xl bg-orange-500/20 flex items-center justify-center">
            <Flame className="w-4 h-4 text-orange-400" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-white">Nutrition Plan</h3>
            <p className="text-xs text-white/50">{goalLabel} · {props.gender} · {props.age}y</p>
          </div>
          <span className="ml-auto text-xs px-2 py-0.5 rounded-full font-medium" style={{ background: `${strategyColor}20`, color: strategyColor }}>
            {props.calorie_strategy}
          </span>
        </div>
      </div>

      <div className="p-4">
        {/* Donut + center calories */}
        <div className="flex items-center gap-6">
          <div className="relative shrink-0">
            <SvgDonut macros={props.macros} />
            <div className="absolute inset-0 flex flex-col items-center justify-center">
              <p className="text-lg font-black text-white leading-none">{props.target_calories.toLocaleString()}</p>
              <p className="text-xs text-white/40">kcal</p>
            </div>
          </div>

          {/* Macro breakdown */}
          <div className="flex-1 space-y-2.5">
            {MACRO_CONFIG.map(({ key, pctKey, label, color, icon: Icon }) => {
              const grams = props.macros[key];
              const pct   = props.macros[pctKey];
              return (
                <div key={key}>
                  <div className="flex items-center justify-between mb-1">
                    <div className="flex items-center gap-1.5">
                      <Icon className="w-3.5 h-3.5" style={{ color }} />
                      <span className="text-xs font-medium text-white/80">{label}</span>
                    </div>
                    <span className="text-xs font-bold text-white">{grams}g</span>
                  </div>
                  <div className="h-1.5 bg-white/8 rounded-full overflow-hidden">
                    <div
                      className="h-full rounded-full transition-all duration-700"
                      style={{ width: `${pct}%`, background: color }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* TDEE stats */}
        <div className="mt-4 grid grid-cols-3 gap-2 text-center">
          {[
            { label: "BMR", value: `${props.bmr}` },
            { label: "TDEE", value: `${props.tdee}` },
            { label: "Target", value: `${props.target_calories}` },
          ].map(({ label, value }) => (
            <div key={label} className="bg-white/5 rounded-xl py-2 px-1">
              <p className="text-sm font-bold text-white">{value}</p>
              <p className="text-xs text-white/40 mt-0.5">{label} kcal</p>
            </div>
          ))}
        </div>

        {/* Meal timing tips */}
        {props.meal_timing_tips?.length > 0 && (
          <div className="mt-3 space-y-1">
            {props.meal_timing_tips.map((tip, i) => (
              <p key={i} className="text-xs text-white/50 flex gap-1.5">
                <span className="text-orange-400 shrink-0">•</span>
                {tip}
              </p>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
