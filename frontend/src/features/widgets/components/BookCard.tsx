"use client";

import React, { useState } from "react";
import { BookCardPayload, RecommendedBook } from "../types";
import { BookOpen, Star, Bookmark, Check, Sparkles } from "lucide-react";

function SingleBookCard({ book }: { book: RecommendedBook }) {
  const [saved, setSaved] = useState(false);
  const color = book.cover_theme || "#F59E0B";

  return (
    <div className="p-4 rounded-xl bg-white/5 border border-white/8 hover:bg-white/8 transition-all duration-200">
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-start gap-3">
          {/* Book Spine Mock */}
          <div
            className="w-10 h-14 rounded-lg flex items-center justify-center shrink-0 shadow-md font-bold text-white text-xs text-center p-1 leading-tight"
            style={{ background: `linear-gradient(135deg, ${color}, ${color}99)` }}
          >
            📖
          </div>
          <div>
            <h4 className="text-sm font-bold text-white">{book.title}</h4>
            <p className="text-xs text-white/50">by {book.author} · {book.published_year}</p>
            <div className="flex items-center gap-2 mt-1.5">
              <div className="flex items-center gap-1 text-amber-400 text-xs font-bold">
                <Star className="w-3 h-3 fill-amber-400" />
                <span>{book.rating}</span>
              </div>
              <span className="text-xs text-white/30">•</span>
              <span className="text-xs text-white/40">{book.pages} pages</span>
              <span className="text-xs text-white/30">•</span>
              <span className="text-xs px-2 py-0.5 rounded-full bg-amber-500/15 text-amber-300 font-medium">{book.genre}</span>
            </div>
          </div>
        </div>

        <button
          onClick={() => setSaved(!saved)}
          className={`p-2 rounded-lg border transition-all ${saved ? "bg-amber-500/20 border-amber-500/40 text-amber-300" : "border-white/10 text-white/40 hover:text-white"}`}
          aria-label={saved ? "Remove from shelf" : "Save to shelf"}
        >
          {saved ? <Check className="w-4 h-4" /> : <Bookmark className="w-4 h-4" />}
        </button>
      </div>

      <p className="text-xs text-white/70 italic mt-3 bg-white/3 p-2.5 rounded-lg border border-white/5">
        "{book.tagline}"
      </p>

      <div className="mt-2.5 flex items-center gap-1.5 text-xs text-amber-300/80">
        <Sparkles className="w-3.5 h-3.5 text-amber-400 shrink-0" />
        <span>{book.match_reason}</span>
      </div>
    </div>
  );
}

export function BookCard(props: BookCardPayload) {
  return (
    <div className="my-3 rounded-2xl border border-white/10 bg-gradient-to-b from-white/5 to-transparent backdrop-blur-sm overflow-hidden">
      {/* Header */}
      <div className="px-4 py-3 border-b border-white/8 bg-gradient-to-r from-amber-500/12 to-orange-500/5">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-xl bg-amber-500/20 flex items-center justify-center">
              <BookOpen className="w-4 h-4 text-amber-400" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-white">Recommended Reading</h3>
              <p className="text-xs text-white/40">{props.genre} · {props.total_matches} selections</p>
            </div>
          </div>
          <span className="text-xs px-2.5 py-1 rounded-full bg-amber-500/18 text-amber-300 font-bold">
            Curated Picks
          </span>
        </div>
      </div>

      <div className="p-3 space-y-3">
        {props.books.map((book, i) => (
          <SingleBookCard key={i} book={book} />
        ))}
      </div>
    </div>
  );
}
