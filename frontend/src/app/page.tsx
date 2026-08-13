import { AuthGate } from "@/features/auth/components/AuthGate";

export const metadata = {
  title: "Kairo | Personalized AI Assistant",
  description: "Enterprise-grade personalized AI agent powered by FastAPI & LangGraph",
};

export default function HomePage() {
  return <AuthGate />;
}
