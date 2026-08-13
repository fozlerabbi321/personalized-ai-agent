import { BrainCircuit, BookOpen, Map } from "lucide-react";

export const SUGGESTED_PROMPTS = [
  {
    title: "Python Quiz",
    prompt: "Quiz me on Python intermediate level",
    icon: BrainCircuit,
  },
  {
    title: "Explain Concept",
    prompt: "Explain recursion to me with an analogy and example",
    icon: BookOpen,
  },
  {
    title: "Study Roadmap",
    prompt: "Give me a 6-week Python study roadmap for beginners",
    icon: Map,
  },
] as const;
