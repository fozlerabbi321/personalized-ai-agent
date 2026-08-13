"use client";

import React from "react";
import { ResumeWidgetPayload } from "../types";
import { FileText, CheckCircle2, AlertTriangle, ArrowRight, Zap, Award } from "lucide-react";

export function ResumeWidget(props: ResumeWidgetPayload) {
  return (
    <div className="my-3 rounded-2xl border border-white/10 bg-gradient-to-b from-white/5 to-transparent backdrop-blur-sm overflow-hidden">
      {/* Header */}
      <div className="px-4 py-3.5 border-b border-white/8 bg-gradient-to-r from-blue-500/15 to-indigo-500/5">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-xl bg-blue-500/20 flex items-center justify-center">
              <FileText className="w-4 h-4 text-blue-400" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-white">Resume ATS Evaluation</h3>
              <p className="text-xs text-white/40">Target: {props.role_matched}</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <div className="text-right">
              <p className="text-xs text-white/40">ATS Score</p>
              <p className="text-base font-black text-blue-300">{props.ats_score} / 100</p>
            </div>
            <div className="w-9 h-9 rounded-xl bg-blue-500/25 border border-blue-500/40 flex items-center justify-center font-black text-blue-300 text-sm">
              {props.overall_grade}
            </div>
          </div>
        </div>
      </div>

      <div className="p-4 space-y-4">
        {/* Top Recommendation */}
        <div className="p-3.5 rounded-xl bg-blue-500/10 border border-blue-500/20 flex items-start gap-2.5">
          <Zap className="w-4 h-4 text-blue-400 shrink-0 mt-0.5" />
          <div>
            <p className="text-xs font-bold text-blue-300 uppercase tracking-wide">Top Strategy Recommendation</p>
            <p className="text-xs text-white/80 mt-0.5 leading-relaxed">{props.top_recommendation}</p>
          </div>
        </div>

        {/* Bullet Rewrites */}
        {props.bullet_rewrites?.length > 0 && (
          <div>
            <p className="text-xs font-semibold text-blue-400 uppercase tracking-wide mb-2">Metric Impact Bullet Rewrites</p>
            <div className="space-y-3">
              {props.bullet_rewrites.map((rw, i) => (
                <div key={i} className="p-3 rounded-xl bg-white/4 border border-white/5 space-y-2">
                  <div className="flex items-center justify-between text-xs">
                    <span className="px-2 py-0.5 rounded bg-white/8 text-white/50 font-medium">{rw.impact_type}</span>
                  </div>
                  <div className="text-xs text-red-300/80 bg-red-500/10 p-2 rounded border border-red-500/15 line-through">
                    "{rw.original}"
                  </div>
                  <div className="flex items-start gap-2 text-xs text-green-300 bg-green-500/10 p-2 rounded border border-green-500/20 font-medium leading-relaxed">
                    <ArrowRight className="w-3.5 h-3.5 text-green-400 shrink-0 mt-0.5" />
                    <span>"{rw.improved}"</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* ATS Checklist */}
        {props.ats_checklist?.length > 0 && (
          <div>
            <p className="text-xs font-semibold text-blue-400 uppercase tracking-wide mb-2">ATS Readiness Checklist</p>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-1.5 text-xs">
              {props.ats_checklist.map((item, i) => (
                <div key={i} className="flex items-center gap-2 p-2 rounded-lg bg-white/3 border border-white/5">
                  {item.status === "pass" ? (
                    <CheckCircle2 className="w-3.5 h-3.5 text-green-400 shrink-0" />
                  ) : (
                    <AlertTriangle className="w-3.5 h-3.5 text-amber-400 shrink-0" />
                  )}
                  <span className={item.status === "pass" ? "text-white/80" : "text-amber-300 font-medium"}>
                    {item.item}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
