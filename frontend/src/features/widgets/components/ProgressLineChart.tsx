"use client";

import React, { useMemo } from "react";
import { ProgressLineChartPayload, ProgressDataPoint } from "../types";
import { TrendingUp, TrendingDown, Minus, Trophy } from "lucide-react";

function SparkLine({ data, unit, color }: { data: ProgressDataPoint[]; unit: string; color: string }) {
  const values = data.map((d) => d.value);
  const min = Math.min(...values);
  const max = Math.max(...values);
  const range = max - min || 1;
  const W = 280, H = 80, PAD = 8;

  const points = data.map((d, i) => ({
    x: PAD + (i / (data.length - 1)) * (W - PAD * 2),
    y: PAD + ((max - d.value) / range) * (H - PAD * 2),
    d,
  }));

  const pathD = points
    .map((p, i) => `${i === 0 ? "M" : "L"} ${p.x.toFixed(1)} ${p.y.toFixed(1)}`)
    .join(" ");

  // Area fill path
  const areaD = pathD + ` L ${points[points.length - 1].x} ${H} L ${points[0].x} ${H} Z`;

  return (
    <svg width="100%" viewBox={`0 0 ${W} ${H}`} className="overflow-visible">
      <defs>
        <linearGradient id="line-gradient" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor={color} stopOpacity="0.25" />
          <stop offset="100%" stopColor={color} stopOpacity="0.01" />
        </linearGradient>
      </defs>
      {/* Area fill */}
      <path d={areaD} fill="url(#line-gradient)" />
      {/* Line */}
      <path d={pathD} fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
      {/* Data points */}
      {points.map((p, i) => (
        <circle key={i} cx={p.x} cy={p.y} r="3" fill={color} stroke="#1C1C1E" strokeWidth="1.5" />
      ))}
      {/* PR marker (last point) */}
      <circle
        cx={points[points.length - 1].x}
        cy={points[points.length - 1].y}
        r="5"
        fill={color}
        stroke="white"
        strokeWidth="2"
      />
    </svg>
  );
}

export function ProgressLineChart(props: ProgressLineChartPayload) {
  const trendColor =
    props.trend === "up" ? "#22C55E" : props.trend === "down" ? "#EF4444" : "#94A3B8";

  const TrendIcon =
    props.trend === "up" ? TrendingUp : props.trend === "down" ? TrendingDown : Minus;

  const firstDate = props.data[0]?.date
    ? new Date(props.data[0].date).toLocaleDateString("en-US", { month: "short", day: "numeric" })
    : "";
  const lastDate = props.data[props.data.length - 1]?.date
    ? new Date(props.data[props.data.length - 1].date).toLocaleDateString("en-US", { month: "short", day: "numeric" })
    : "";

  return (
    <div className="my-3 rounded-2xl border border-white/10 bg-gradient-to-b from-white/5 to-transparent backdrop-blur-sm overflow-hidden">
      {/* Header */}
      <div className="px-4 py-3 border-b border-white/8 bg-gradient-to-r from-orange-500/10 to-transparent">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-xl bg-orange-500/20 flex items-center justify-center">
              <Trophy className="w-4 h-4 text-orange-400" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-white">{props.exercise} Progress</h3>
              <p className="text-xs text-white/50">{props.muscle_group} · {props.period_weeks}-week history</p>
            </div>
          </div>
          <div className="text-right">
            <p className="text-lg font-black text-white">
              {props.current_pr}
              <span className="text-xs font-normal text-white/40 ml-1">{props.unit}</span>
            </p>
            <div className="flex items-center justify-end gap-1 mt-0.5">
              <TrendIcon className="w-3 h-3" style={{ color: trendColor }} />
              <span className="text-xs font-bold" style={{ color: trendColor }}>
                {props.trend_label} ({props.gain_pct > 0 ? "+" : ""}{props.gain_pct}%)
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Chart */}
      <div className="px-4 pt-4 pb-2">
        <SparkLine data={props.data} unit={props.unit} color="#FF6B35" />
        <div className="flex justify-between mt-1">
          <span className="text-xs text-white/30">{firstDate}</span>
          <span className="text-xs text-white/30">{lastDate}</span>
        </div>
      </div>

      {/* Stats row */}
      <div className="px-4 pb-4 grid grid-cols-3 gap-2 text-center mt-1">
        {[
          { label: "Starting", value: `${props.starting_value}${props.unit}` },
          { label: "Current PR", value: `${props.current_pr}${props.unit}`, highlight: true },
          { label: "Total Gain", value: props.trend_label },
        ].map(({ label, value, highlight }) => (
          <div key={label} className={`rounded-xl py-2 px-1 ${highlight ? "bg-orange-500/10 border border-orange-500/20" : "bg-white/5"}`}>
            <p className={`text-sm font-bold ${highlight ? "text-orange-400" : "text-white"}`}>{value}</p>
            <p className="text-xs text-white/40 mt-0.5">{label}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
