// ── Nova AI Widget Payload Types ──────────────────────────────────────────────

export interface QuizOption {
  id: string;
  text: string;
}

export interface QuizWidgetPayload {
  widget_type: "quiz_widget";
  subject: string;
  difficulty: string;
  question_no: number;
  question: string;
  question_type: "mcq" | "true_false" | "fill_blank" | "short_answer";
  options: QuizOption[];
  correct_answer: string;
  explanation: string;
  xp_reward: number;
}

export interface KeyTerm {
  term: string;
  definition: string;
}

export interface ConceptTablePayload {
  widget_type: "concept_table";
  topic: string;
  definition: string;
  analogy: string;
  key_terms: KeyTerm[];
  example_code: string;
  code_language: string;
  related_topics: string[];
}

export interface RoadmapWeek {
  week: number;
  topic: string;
  subtopics: string[];
  hours: number;
  resources: string[];
}

export interface StudyRoadmapPayload {
  widget_type: "study_roadmap";
  subject: string;
  skill_level: string;
  duration_weeks: number;
  total_hours: number;
  daily_hours: number;
  weeks: RoadmapWeek[];
  milestone: string;
}

export type WidgetPayload =
  | QuizWidgetPayload
  | ConceptTablePayload
  | StudyRoadmapPayload;
