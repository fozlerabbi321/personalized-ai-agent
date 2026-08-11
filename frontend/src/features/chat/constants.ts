import { Dumbbell, Flame, TrendingUp } from "lucide-react";

export const SUGGESTED_PROMPTS = [
  {
    title: "Workout Plan",
    prompt: "Give me a back day workout for muscle gain",
    icon: Dumbbell,
  },
  {
    title: "Macro Calculator",
    prompt: "Calculate my macros. I'm 75kg, 178cm, 25 years old, moderately active, goal: muscle gain",
    icon: Flame,
  },
  {
    title: "Progress Check",
    prompt: "Show me my bench press progress over the last 8 weeks",
    icon: TrendingUp,
  },
] as const;
