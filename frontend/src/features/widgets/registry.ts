import React from "react";
import { WorkoutPlanWidget }  from "./components/WorkoutPlanWidget";
import { MacroDonutChart }    from "./components/MacroDonutChart";
import { ProgressLineChart }  from "./components/ProgressLineChart";
import { ExerciseCard }       from "./components/ExerciseCard";
import { StreakHeatmap }      from "./components/StreakHeatmap";
import { WidgetType }         from "./constants";
import { WidgetPayload }      from "./types";

export const widgetRegistry: Record<string, React.ComponentType<WidgetPayload>> = {
  [WidgetType.WORKOUT_PLAN]:        WorkoutPlanWidget  as unknown as React.ComponentType<WidgetPayload>,
  [WidgetType.MACRO_DONUT_CHART]:   MacroDonutChart    as unknown as React.ComponentType<WidgetPayload>,
  [WidgetType.PROGRESS_LINE_CHART]: ProgressLineChart  as unknown as React.ComponentType<WidgetPayload>,
  [WidgetType.EXERCISE_CARD]:       ExerciseCard       as unknown as React.ComponentType<WidgetPayload>,
  [WidgetType.STREAK_HEATMAP]:      StreakHeatmap      as unknown as React.ComponentType<WidgetPayload>,
};
