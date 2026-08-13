import { Briefcase, FileText, Map } from "lucide-react";

export const SUGGESTED_PROMPTS = [
  {
    title: "Mock Interview Practice",
    prompt: "Let's do a behavioral interview question for a Software Engineer position",
    icon: Briefcase,
  },
  {
    title: "Resume Review & Rewrites",
    prompt: "Can you review my resume bullet points and suggest improvements?",
    icon: FileText,
  },
  {
    title: "Senior Engineer Roadmap",
    prompt: "How can I transition from Mid-Level to Senior Software Engineer?",
    icon: Map,
  },
] as const;
