// ── Kairo AI Widget Payload Types ─────────────────────────────────────────────

export interface StarGuide {
  situation: string;
  task: string;
  action: string;
  result: string;
}

export interface InterviewWidgetPayload {
  widget_type: "interview_widget";
  target_role: string;
  question_no: number;
  question: string;
  question_type: "behavioral" | "technical_coding" | "system_design" | "resume_walkthrough";
  category: string;
  evaluation_criteria: string[];
  star_guide: StarGuide;
  sample_keywords: string[];
}

export interface BulletRewrite {
  original: string;
  improved: string;
  impact_type: string;
  keywords: string[];
}

export interface ChecklistItem {
  item: string;
  status: "pass" | "warning" | "fail";
}

export interface ResumeWidgetPayload {
  widget_type: "resume_widget";
  ats_score: number;
  role_matched: string;
  overall_grade: string;
  top_recommendation: string;
  bullet_rewrites: BulletRewrite[];
  ats_checklist: ChecklistItem[];
}

export interface CareerPhase {
  phase: number;
  title: string;
  timeframe: string;
  milestones: string[];
  skills_to_acquire: string[];
}

export interface CareerRoadmapWidgetPayload {
  widget_type: "career_roadmap";
  current_role: string;
  target_role: string;
  timeframe: string;
  salary_range: string;
  key_metric: string;
  phases: CareerPhase[];
}

export type WidgetPayload =
  | InterviewWidgetPayload
  | ResumeWidgetPayload
  | CareerRoadmapWidgetPayload;
