import React from "react";
import { QuizWidget } from "./components/QuizWidget";
import { ConceptTable } from "./components/ConceptTable";
import { StudyRoadmap } from "./components/StudyRoadmap";
import { WidgetType } from "./constants";
import { WidgetPayload } from "./types";

export const widgetRegistry: Record<string, React.ComponentType<WidgetPayload>> = {
  [WidgetType.QUIZ_WIDGET]: QuizWidget as unknown as React.ComponentType<WidgetPayload>,
  [WidgetType.CONCEPT_TABLE]: ConceptTable as unknown as React.ComponentType<WidgetPayload>,
  [WidgetType.STUDY_ROADMAP]: StudyRoadmap as unknown as React.ComponentType<WidgetPayload>,
};
