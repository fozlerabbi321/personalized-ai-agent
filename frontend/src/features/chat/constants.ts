import { BookOpen, Star, Trophy } from "lucide-react";

export const SUGGESTED_PROMPTS = [
  {
    title: "Book Recommendations",
    prompt: "Recommend me some great sci-fi books",
    icon: BookOpen,
  },
  {
    title: "Book Review & Themes",
    prompt: "Can you give me a review and theme analysis of Dune?",
    icon: Star,
  },
  {
    title: "Reading Challenge",
    prompt: "How am I doing on my 2026 reading challenge?",
    icon: Trophy,
  },
] as const;
