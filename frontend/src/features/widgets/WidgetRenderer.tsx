"use client";

import React from "react";
import { widgetRegistry } from "./registry";
import { WidgetPayload } from "./types";
import { AlertCircle } from "lucide-react";

interface WidgetRendererProps {
  widget: WidgetPayload | Record<string, unknown> | string;
}

export function WidgetRenderer({ widget }: WidgetRendererProps) {
  let targetWidget: WidgetPayload | null = null;

  if (typeof widget === "string") {
    try {
      targetWidget = JSON.parse(widget) as WidgetPayload;
    } catch {
      return null;
    }
  } else if (widget && typeof widget === "object") {
    targetWidget = widget as WidgetPayload;
  }

  if (!targetWidget) return null;

  const type = targetWidget.widget_type;
  if (!type) return null;

  const Component = widgetRegistry[type];

  if (!Component) {
    return (
      <div className="flex items-center gap-2 p-3 my-2 text-xs text-amber-400 bg-amber-500/10 border border-amber-500/20 rounded-xl">
        <AlertCircle className="h-4 w-4 shrink-0" />
        <span>Unknown widget type: {type}</span>
      </div>
    );
  }

  return <Component {...targetWidget} />;
}
