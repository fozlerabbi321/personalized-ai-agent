"use client";

import React from "react";
import { BookReviewPayload } from "../types";
import { Star, Clock, Quote, Compass, Award } from "lucide-react";

export function BookReview(props: BookReviewPayload) {
  return (
    <div className="my-3 rounded-2xl border border-white/10 bg-gradient-to-b from-white/5 to-transparent backdrop-blur-sm overflow-hidden">
      {/* Header */}
      <div className="px-4 py-3.5 border-b border-white/8 bg-gradient-to-r from-amber-500/15 to-orange-500/5">
        <div className="flex items-start justify-between gap-3">
          <div>
            <span className="text-xs px-2.5 py-0.5 rounded-full bg-amber-500/20 text-amber-300 font-semibold uppercase tracking-wider">
              {props.genre}
            </span>
            <h3 className="text-base font-bold text-white mt-1.5">{props.title}</h3>
            <p className="text-xs text-white/50">by {props.author} ({props.published_year})</p>
          </div>
          <div className="flex items-center gap-1.5 px-3 py-1 rounded-xl bg-white/8 border border-white/10 shrink-0">
            <Star className="w-4 h-4 fill-amber-400 text-amber-400" />
            <span className="text-sm font-bold text-amber-300">{props.rating} / 5</span>
          </div>
        </div>
      </div>

      <div className="p-4 space-y-4">
        {/* Summary */}
        <div>
          <p className="text-xs font-semibold text-amber-400 uppercase tracking-wide mb-1">Synopsis</p>
          <p className="text-sm text-white/80 leading-relaxed">{props.summary}</p>
        </div>

        {/* Memorable Quote */}
        {props.memorable_quote && (
          <div className="p-3.5 rounded-xl bg-amber-500/8 border border-amber-500/15">
            <div className="flex items-center gap-1.5 mb-1 text-amber-400">
              <Quote className="w-3.5 h-3.5" />
              <span className="text-xs font-semibold uppercase tracking-wide">Memorable Quote</span>
            </div>
            <p className="text-sm text-white/80 italic leading-relaxed">"{props.memorable_quote}"</p>
          </div>
        )}

        {/* Core Themes */}
        {props.themes?.length > 0 && (
          <div>
            <p className="text-xs font-semibold text-amber-400 uppercase tracking-wide mb-2">Central Themes</p>
            <div className="flex flex-wrap gap-1.5">
              {props.themes.map((theme, i) => (
                <span key={i} className="text-xs px-2.5 py-1 rounded-full bg-white/8 text-white/70">
                  {theme}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Key Takeaways */}
        {props.key_takeaways?.length > 0 && (
          <div>
            <div className="flex items-center gap-1.5 mb-2 text-amber-400">
              <Award className="w-3.5 h-3.5" />
              <p className="text-xs font-semibold uppercase tracking-wide">Key Takeaways</p>
            </div>
            <div className="space-y-1.5">
              {props.key_takeaways.map((takeaway, i) => (
                <div key={i} className="flex gap-2 text-xs text-white/70 bg-white/3 p-2 rounded-lg border border-white/5">
                  <span className="text-amber-400 shrink-0 font-bold">•</span>
                  <span>{takeaway}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Target Audience & Reading Time */}
        <div className="flex items-center justify-between text-xs text-white/40 pt-2 border-t border-white/5">
          <div className="flex items-center gap-1.5">
            <Compass className="w-3.5 h-3.5" />
            <span className="truncate max-w-[220px]">Ideal for: {props.target_audience}</span>
          </div>
          <div className="flex items-center gap-1 shrink-0">
            <Clock className="w-3.5 h-3.5" />
            <span>~{props.reading_time_hours}h read</span>
          </div>
        </div>
      </div>
    </div>
  );
}
