"use client";

import React, { useState } from "react";
import { StudyRoadmapPayload, RoadmapWeek } from "../types";
import { Map, Clock, BookOpen, ChevronDown, ChevronUp, Trophy, Flame } from "lucide-react";

const LEVEL_COLOR: Record<string, string> = {
  beginner:     "#22C55E",
  intermediate: "#6366F1",
  advanced:     "#EF4444",
};

function WeekCard({ week, isLast }: { week: RoadmapWeek; isLast: boolean }) {
  const [open, setOpen] = useState(week.week === 1);

  return (
    <div className="flex gap-3">
      {/* Timeline */}
      <div className="flex flex-col items-center">
        <div className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-black shrink-0 ${open ? "bg-indigo-500 text-white" : "bg-white/10 text-white/50"}`}>
          {week.week}
        </div>
        {!isLast && <div className="w-px flex-1 bg-white/8 mt-1" />}
      </div>

      {/* Content */}
      <div className={`flex-1 mb-3 rounded-xl border transition-all duration-200 overflow-hidden ${open ? "border-indigo-500/25 bg-indigo-500/5" : "border-white/8 bg-white/3"}`}>
        <button
          onClick={() => setOpen(!open)}
          className="w-full flex items-center justify-between px-3 py-2.5 text-left"
        >
          <div className="flex-1 min-w-0">
            <p className={`text-sm font-semibold truncate ${open ? "text-white" : "text-white/60"}`}>{week.topic}</p>
            <div className="flex items-center gap-2 mt-0.5">
              <Clock className="w-3 h-3 text-white/30" />
              <span className="text-xs text-white/30">{week.hours}h</span>
            </div>
          </div>
          {open ? <ChevronUp className="w-4 h-4 text-white/30 shrink-0 ml-2" /> : <ChevronDown className="w-4 h-4 text-white/30 shrink-0 ml-2" />}
        </button>

        {open && (
          <div className="px-3 pb-3 space-y-2.5">
            {/* Subtopics */}
            <div className="flex flex-wrap gap-1.5">
              {week.subtopics.map((st, i) => (
                <span key={i} className="text-xs px-2 py-0.5 rounded-full bg-indigo-500/15 text-indigo-300">{st}</span>
              ))}
            </div>
            {/* Resources */}
            {week.resources?.length > 0 && (
              <div>
                <p className="text-xs text-white/30 mb-1 flex items-center gap-1">
                  <BookOpen className="w-3 h-3" /> Resources
                </p>
                <ul className="space-y-0.5">
                  {week.resources.map((r, i) => (
                    <li key={i} className="text-xs text-white/50 flex gap-1.5">
                      <span className="text-indigo-400 shrink-0">→</span> {r}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export function StudyRoadmap(props: StudyRoadmapPayload) {
  const levelColor = LEVEL_COLOR[props.skill_level] ?? "#6366F1";

  return (
    <div className="my-3 rounded-2xl border border-white/10 bg-gradient-to-b from-white/5 to-transparent backdrop-blur-sm overflow-hidden">
      {/* Header */}
      <div className="px-4 py-3 border-b border-white/8 bg-gradient-to-r from-indigo-500/12 to-violet-500/5">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-xl bg-indigo-500/20 flex items-center justify-center">
              <Map className="w-4 h-4 text-indigo-400" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-white">{props.subject} Roadmap</h3>
              <p className="text-xs text-white/40">{props.duration_weeks}-week curriculum</p>
            </div>
          </div>
          <span
            className="text-xs px-2.5 py-1 rounded-full font-bold capitalize"
            style={{ background: `${levelColor}20`, color: levelColor }}
          >
            {props.skill_level}
          </span>
        </div>
      </div>

      {/* Stats */}
      <div className="px-4 py-3 grid grid-cols-3 gap-2 text-center border-b border-white/5">
        {[
          { label: "Weeks", value: props.duration_weeks.toString(), icon: Flame },
          { label: "Total Hours", value: `${props.total_hours}h`, icon: Clock },
          { label: "Daily", value: `${props.daily_hours}h`, icon: Trophy },
        ].map(({ label, value, icon: Icon }) => (
          <div key={label} className="bg-white/4 rounded-xl py-2">
            <p className="text-sm font-black text-indigo-300">{value}</p>
            <p className="text-xs text-white/30 mt-0.5">{label}</p>
          </div>
        ))}
      </div>

      {/* Weekly breakdown */}
      <div className="p-4">
        {props.weeks.map((week, i) => (
          <WeekCard key={week.week} week={week} isLast={i === props.weeks.length - 1} />
        ))}

        {/* Milestone */}
        <div className="mt-2 flex items-center gap-2 p-3 rounded-xl bg-indigo-500/10 border border-indigo-500/20">
          <Trophy className="w-4 h-4 text-indigo-400 shrink-0" />
          <p className="text-xs font-semibold text-indigo-300">{props.milestone}</p>
        </div>
      </div>
    </div>
  );
}
