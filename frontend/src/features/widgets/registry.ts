import React from "react";
import { InterviewWidget } from "./components/InterviewWidget";
import { ResumeWidget } from "./components/ResumeWidget";
import { CareerRoadmapWidget } from "./components/CareerRoadmapWidget";
import { WidgetType } from "./constants";
import { WidgetPayload } from "./types";

export const widgetRegistry: Record<string, React.ComponentType<WidgetPayload>> = {
  [WidgetType.INTERVIEW_WIDGET]: InterviewWidget as unknown as React.ComponentType<WidgetPayload>,
  [WidgetType.RESUME_WIDGET]: ResumeWidget as unknown as React.ComponentType<WidgetPayload>,
  [WidgetType.CAREER_ROADMAP_WIDGET]: CareerRoadmapWidget as unknown as React.ComponentType<WidgetPayload>,
};
