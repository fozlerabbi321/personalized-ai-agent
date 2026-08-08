"use client";

import React from "react";
import { widgetRegistry } from "./registry";
import { WidgetPayload } from "./types";
import { AlertCircle } from "lucide-react";

interface WidgetRendererProps {
  widget: WidgetPayload | any;
}

export function WidgetRenderer({ widget }: WidgetRendererProps) {
  if (!widget || typeof widget !== "object") return null;

  const type = widget.widget_type;
  const Component = widgetRegistry[type];

  if (!Component) {
    return (
      <div className="flex items-center gap-2 p-3 my-2 text-xs text-amber-400 bg-amber-500/10 border border-amber-500/20 rounded-xl">
        <AlertCircle className="h-4 w-4 shrink-0" />
        <span>Unknown widget type: {type || "unspecified"}</span>
      </div>
    );
  }

  return <Component {...widget} />;
}
