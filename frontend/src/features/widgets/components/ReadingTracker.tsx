"use client";

import React from "react";
import { ReadingTrackerPayload } from "../types";
import { BookOpen, Flame, Trophy, CheckCircle2, Star, Target } from "lucide-react";

export function ReadingTracker(props: ReadingTrackerPayload) {
  return (
    <div className="my-3 rounded-2xl border border-white/10 bg-gradient-to-b from-white/5 to-transparent backdrop-blur-sm overflow-hidden">
      {/* Header */}
      <div className="px-4 py-3.5 border-b border-white/8 bg-gradient-to-r from-amber-500/15 to-orange-500/5">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-xl bg-amber-500/20 flex items-center justify-center">
              <Trophy className="w-4 h-4 text-amber-400" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-white">{props.year} Reading Challenge</h3>
              <p className="text-xs text-white/40">{props.status_label}</p>
            </div>
          </div>
          <div className="flex items-center gap-1 px-2.5 py-1 rounded-full bg-orange-500/20 text-orange-300 text-xs font-bold">
            <Flame className="w-3.5 h-3.5 text-orange-400" />
            <span>{props.current_streak_days}d streak</span>
          </div>
        </div>
      </div>

      <div className="p-4 space-y-4">
        {/* Progress Bar */}
        <div>
          <div className="flex items-center justify-between text-xs mb-1.5">
            <span className="text-white/60 font-medium">Annual Goal Progress</span>
            <span className="font-bold text-amber-300">{props.books_read} / {props.annual_target} books ({props.completion_pct}%)</span>
          </div>
          <div className="h-2.5 bg-white/8 rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-amber-500 to-orange-500 rounded-full transition-all duration-700"
              style={{ width: `${Math.min(props.completion_pct, 100)}%` }}
            />
          </div>
        </div>

        {/* Quick Stats Grid */}
        <div className="grid grid-cols-3 gap-2 text-center">
          {[
            { label: "Books Finished", value: `${props.books_read}`, icon: BookOpen },
            { label: "Pages Read", value: `${props.pages_read.toLocaleString()}`, icon: Target },
            { label: "Top Genre", value: props.favorite_genre, icon: Star },
          ].map(({ label, value }) => (
            <div key={label} className="bg-white/4 rounded-xl py-2 px-1">
              <p className="text-sm font-black text-amber-300 truncate">{value}</p>
              <p className="text-xs text-white/40 mt-0.5">{label}</p>
            </div>
          ))}
        </div>

        {/* Recent Books Finished */}
        {props.recent_books?.length > 0 && (
          <div>
            <p className="text-xs font-semibold text-amber-400 uppercase tracking-wide mb-2">Recently Completed</p>
            <div className="space-y-1.5">
              {props.recent_books.map((book, i) => (
                <div key={i} className="flex items-center justify-between p-2.5 rounded-lg bg-white/4 text-xs">
                  <div className="flex items-center gap-2">
                    <CheckCircle2 className="w-3.5 h-3.5 text-green-400 shrink-0" />
                    <div>
                      <p className="font-semibold text-white">{book.title}</p>
                      <p className="text-white/40">{book.author}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-1 text-amber-400 font-bold shrink-0">
                    <Star className="w-3 h-3 fill-amber-400" />
                    <span>{book.rating}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
