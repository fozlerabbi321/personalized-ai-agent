import { TrendingUp, Code2, Layers } from "lucide-react";

export const SUGGESTED_PROMPTS = [
  {
    title: "Bitcoin Market & OHLC Chart",
    prompt: "Show me BTC price and market analysis",
    icon: TrendingUp,
  },
  {
    title: "Python Async/Await",
    prompt: "Explain Python async/await concurrency with an example.",
    icon: Code2,
  },
  {
    title: "Summarize History",
    prompt: "Summarize our conversation so far.",
    icon: Layers,
  },
] as const;
