"use client";

import React from "react";
import { MetricCardWidgetPayload } from "../types";
import { TrendingUp, TrendingDown, Minus } from "lucide-react";

export function MetricCard(props: MetricCardWidgetPayload) {
  const { label, value, delta, sentiment = "neutral", subtitle } = props;

  const isPositive = sentiment === "positive" || (delta && delta.startsWith("+"));
  const isNegative = sentiment === "negative" || (delta && delta.startsWith("-"));

  return (
    <div className="w-full sm:w-72 glass-panel rounded-2xl p-4 border border-indigo-500/20 shadow-lg my-3">
      <div className="flex items-center justify-between text-xs text-gray-400 font-medium mb-1">
        <span>{label}</span>
        {delta && (
          <span
            className={`flex items-center gap-1 font-semibold px-2 py-0.5 rounded-full text-[11px] ${
              isPositive
                ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                : isNegative
                ? "bg-rose-500/10 text-rose-400 border border-rose-500/20"
                : "bg-gray-500/10 text-gray-400"
            }`}
          >
            {isPositive && <TrendingUp className="h-3 w-3" />}
            {isNegative && <TrendingDown className="h-3 w-3" />}
            {!isPositive && !isNegative && <Minus className="h-3 w-3" />}
            {delta}
          </span>
        )}
      </div>

      <div className="text-2xl font-bold text-white tracking-tight">{value}</div>

      {subtitle && <p className="text-xs text-gray-500 mt-1">{subtitle}</p>}
    </div>
  );
}
