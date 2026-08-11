// ── Atlas AI Widget Payload Types ─────────────────────────────────────────────

export interface ExerciseItem {
  name: string;
  equipment: string;
  type: "compound" | "isolation" | "isometric";
  sets: number;
  reps: string;
  rest_seconds: number;
  muscle_group: string;
}

export interface WorkoutPlanWidgetPayload {
  widget_type: "workout_plan";
  title: string;
  goal: string;
  fitness_level: string;
  muscle_group: string;
  exercises: ExerciseItem[];
  total_exercises: number;
  estimated_duration_min: number;
  rep_scheme_note: string;
  generated_at: string;
}

export interface MacroData {
  protein_g: number;
  carbs_g: number;
  fat_g: number;
  protein_pct: number;
  carbs_pct: number;
  fat_pct: number;
}

export interface MacroDonutChartPayload {
  widget_type: "macro_donut_chart";
  goal: string;
  gender: string;
  weight_kg: number;
  height_cm: number;
  age: number;
  activity_level: string;
  bmr: number;
  tdee: number;
  target_calories: number;
  calorie_strategy: string;
  macros: MacroData;
  meal_timing_tips: string[];
}

export interface ProgressDataPoint {
  date: string;
  value: number;
  unit: string;
}

export interface ProgressLineChartPayload {
  widget_type: "progress_line_chart";
  exercise: string;
  muscle_group: string;
  unit: string;
  period_weeks: number;
  data: ProgressDataPoint[];
  current_pr: number;
  starting_value: number;
  total_gain: number;
  gain_pct: number;
  trend: "up" | "down" | "flat";
  trend_label: string;
  summary: string;
}

export interface ExerciseCardPayload {
  widget_type: "exercise_card";
  name: string;
  muscle_primary: string;
  muscle_secondary?: string;
  equipment: string;
  difficulty: string;
  form_cues: string[];
  common_mistakes: string[];
  rpe_recommendation: number;
}

export interface StreakHeatmapPayload {
  widget_type: "streak_heatmap";
  weeks: Array<Array<{ date: string; count: number }>>;
  total_workouts: number;
  current_streak: number;
  longest_streak: number;
}

export type WidgetPayload =
  | WorkoutPlanWidgetPayload
  | MacroDonutChartPayload
  | ProgressLineChartPayload
  | ExerciseCardPayload
  | StreakHeatmapPayload;
