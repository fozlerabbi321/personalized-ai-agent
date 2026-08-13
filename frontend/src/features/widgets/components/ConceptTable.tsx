"use client";

import React, { useState } from "react";
import { ConceptTablePayload } from "../types";
import { BookOpen, Code2, ChevronDown, ChevronUp, Link2, Lightbulb } from "lucide-react";

export function ConceptTable(props: ConceptTablePayload) {
  const [showCode, setShowCode] = useState(false);

  return (
    <div className="my-3 rounded-2xl border border-white/10 bg-gradient-to-b from-white/5 to-transparent backdrop-blur-sm overflow-hidden">
      {/* Header */}
      <div className="px-4 py-3 border-b border-white/8 bg-gradient-to-r from-violet-500/12 to-indigo-500/5">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-xl bg-violet-500/20 flex items-center justify-center">
            <BookOpen className="w-4 h-4 text-violet-400" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-white">{props.topic}</h3>
            <p className="text-xs text-white/40">Concept Breakdown</p>
          </div>
        </div>
      </div>

      <div className="p-4 space-y-4">
        {/* Definition */}
        <div>
          <p className="text-xs font-semibold text-violet-400 uppercase tracking-wide mb-1.5">Definition</p>
          <p className="text-sm text-white/80 leading-relaxed">{props.definition}</p>
        </div>

        {/* Analogy */}
        {props.analogy && (
          <div className="p-3 rounded-xl bg-amber-500/8 border border-amber-500/15">
            <div className="flex items-center gap-1.5 mb-1.5">
              <Lightbulb className="w-3.5 h-3.5 text-amber-400" />
              <span className="text-xs font-semibold text-amber-400 uppercase tracking-wide">Analogy</span>
            </div>
            <p className="text-sm text-white/70 leading-relaxed italic">{props.analogy}</p>
          </div>
        )}

        {/* Key Terms */}
        {props.key_terms?.length > 0 && (
          <div>
            <p className="text-xs font-semibold text-violet-400 uppercase tracking-wide mb-2">Key Terms</p>
            <div className="space-y-1.5">
              {props.key_terms.map((kt, i) => (
                <div key={i} className="flex gap-3 p-2.5 rounded-lg bg-white/5">
                  <span className="text-xs font-bold text-violet-300 shrink-0 w-28">{kt.term}</span>
                  <span className="text-xs text-white/55 leading-relaxed">{kt.definition}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Code Example — collapsible */}
        {props.example_code && (
          <div>
            <button
              onClick={() => setShowCode(!showCode)}
              className="flex items-center gap-2 w-full text-left group"
            >
              <Code2 className="w-3.5 h-3.5 text-indigo-400" />
              <span className="text-xs font-semibold text-indigo-400 uppercase tracking-wide group-hover:text-indigo-300 transition-colors">
                Code Example {props.code_language && `(${props.code_language})`}
              </span>
              {showCode
                ? <ChevronUp className="w-3.5 h-3.5 text-white/30 ml-auto" />
                : <ChevronDown className="w-3.5 h-3.5 text-white/30 ml-auto" />
              }
            </button>
            {showCode && (
              <pre className="mt-2 p-3 rounded-xl bg-black/40 border border-white/8 text-xs text-green-300 font-mono overflow-x-auto leading-relaxed">
                {props.example_code}
              </pre>
            )}
          </div>
        )}

        {/* Related Topics */}
        {props.related_topics?.length > 0 && (
          <div>
            <div className="flex items-center gap-1.5 mb-2">
              <Link2 className="w-3.5 h-3.5 text-white/40" />
              <p className="text-xs font-semibold text-white/40 uppercase tracking-wide">Learn Next</p>
            </div>
            <div className="flex flex-wrap gap-1.5">
              {props.related_topics.map((topic, i) => (
                <span key={i} className="text-xs px-2.5 py-1 rounded-full bg-white/8 text-white/50 hover:bg-violet-500/15 hover:text-violet-300 transition-colors cursor-default">
                  {topic}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
