"use client";

import React, { useState } from "react";
import { CandlestickWidgetPayload, OHLCItem } from "../types";
import { TrendingUp, TrendingDown, Activity, DollarSign, Calendar } from "lucide-react";

export function CandlestickChart(props: CandlestickWidgetPayload) {
  const { ticker, title, current_price, change, change_pct, data = [], seven_day_high, seven_day_low } = props;
  const [hoveredItem, setHoveredItem] = useState<OHLCItem | null>(null);

  const isPositive = change_pct >= 0;

  // Chart dimensions & scaling
  const width = 600;
  const height = 240;
  const padding = { top: 20, right: 30, bottom: 40, left: 50 };

  const chartWidth = width - padding.left - padding.right;
  const chartHeight = height - padding.top - padding.bottom;

  // Price Extrents
  const allLow = data.length > 0 ? Math.min(...data.map((d) => d.low)) : 100;
  const allHigh = data.length > 0 ? Math.max(...data.map((d) => d.high)) : 200;
  const priceRange = allHigh - allLow || 1;

  const getY = (val: number) => {
    return padding.top + chartHeight - ((val - allLow) / priceRange) * chartHeight;
  };

  const candleWidth = Math.max(8, Math.floor((chartWidth / (data.length || 1)) * 0.6));
  const stepX = chartWidth / (data.length || 1);

  return (
    <div className="w-full glass-panel rounded-2xl p-5 border border-indigo-500/20 shadow-xl shadow-indigo-950/40 my-3 overflow-hidden">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-4 pb-4 border-b border-gray-800">
        <div>
          <div className="flex items-center gap-2">
            <span className="px-2.5 py-0.5 rounded-lg text-xs font-bold bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
              {ticker}
            </span>
            <h4 className="text-sm font-semibold text-gray-200">{title}</h4>
          </div>
          <p className="text-xs text-gray-400 mt-1 flex items-center gap-1.5">
            <Activity className="h-3.5 w-3.5 text-gray-500" />
            7-Day Historical Market OHLC Data
          </p>
        </div>

        <div className="text-right">
          <div className="text-2xl font-extrabold text-white tracking-tight">
            ${current_price?.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </div>
          <div
            className={`flex items-center justify-end gap-1 text-xs font-semibold mt-0.5 ${
              isPositive ? "text-emerald-400" : "text-rose-400"
            }`}
          >
            {isPositive ? <TrendingUp className="h-3.5 w-3.5" /> : <TrendingDown className="h-3.5 w-3.5" />}
            <span>
              {isPositive ? "+" : ""}
              {change} ({isPositive ? "+" : ""}
              {change_pct}%)
            </span>
          </div>
        </div>
      </div>

      {/* Hover Information / Quick Stats */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 py-3 text-xs bg-gray-900/60 rounded-xl p-3 my-3 border border-gray-800/80">
        <div>
          <span className="text-gray-500 block">7D High</span>
          <span className="font-semibold text-emerald-400">${seven_day_high ?? allHigh.toFixed(2)}</span>
        </div>
        <div>
          <span className="text-gray-500 block">7D Low</span>
          <span className="font-semibold text-rose-400">${seven_day_low ?? allLow.toFixed(2)}</span>
        </div>
        <div>
          <span className="text-gray-500 block">Open (Hover/Latest)</span>
          <span className="font-semibold text-gray-200">
            ${hoveredItem ? hoveredItem.open.toFixed(2) : data[data.length - 1]?.open.toFixed(2) ?? "-"}
          </span>
        </div>
        <div>
          <span className="text-gray-500 block">Close (Hover/Latest)</span>
          <span className="font-semibold text-gray-200">
            ${hoveredItem ? hoveredItem.close.toFixed(2) : data[data.length - 1]?.close.toFixed(2) ?? "-"}
          </span>
        </div>
      </div>

      {/* SVG Candlestick Graphic */}
      <div className="relative w-full overflow-x-auto">
        <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-auto min-w-[500px] select-none">
          {/* Grid lines */}
          {[0, 0.25, 0.5, 0.75, 1].map((pct, i) => {
            const y = padding.top + chartHeight * pct;
            const priceVal = (allHigh - pct * priceRange).toFixed(1);
            return (
              <g key={i}>
                <line
                  x1={padding.left}
                  y1={y}
                  x2={width - padding.right}
                  y2={y}
                  stroke="#1f2937"
                  strokeDasharray="3 3"
                  strokeWidth="1"
                />
                <text
                  x={padding.left - 8}
                  y={y + 4}
                  fill="#6b7280"
                  fontSize="10"
                  textAnchor="end"
                  fontFamily="monospace"
                >
                  ${priceVal}
                </text>
              </g>
            );
          })}

          {/* Candlesticks */}
          {data.map((item, index) => {
            const xCenter = padding.left + index * stepX + stepX / 2;
            const yOpen = getY(item.open);
            const yClose = getY(item.close);
            const yHigh = getY(item.high);
            const yLow = getY(item.low);

            const candleIsUp = item.close >= item.open;
            const color = candleIsUp ? "#10b981" : "#f43f5e"; // Emerald / Rose

            const candleTop = Math.min(yOpen, yClose);
            const candleHeight = Math.max(2, Math.abs(yClose - yOpen));

            return (
              <g
                key={index}
                className="cursor-pointer transition-opacity hover:opacity-80"
                onMouseEnter={() => setHoveredItem(item)}
                onMouseLeave={() => setHoveredItem(null)}
              >
                {/* Wick */}
                <line
                  x1={xCenter}
                  y1={yHigh}
                  x2={xCenter}
                  y2={yLow}
                  stroke={color}
                  strokeWidth="1.5"
                />

                {/* Body */}
                <rect
                  x={xCenter - candleWidth / 2}
                  y={candleTop}
                  width={candleWidth}
                  height={candleHeight}
                  fill={color}
                  rx="1.5"
                />

                {/* X-Axis Date Labels */}
                <text
                  x={xCenter}
                  y={height - 10}
                  fill="#9ca3af"
                  fontSize="9"
                  textAnchor="middle"
                >
                  {item.date ? item.date.slice(5) : ""}
                </text>
              </g>
            );
          })}
        </svg>
      </div>
    </div>
  );
}
