import { WidgetPayload } from "@/features/widgets/types";

export interface Message {
  id: string;
  role: "human" | "assistant";
  content: string;
  widget_json?: WidgetPayload | Record<string, unknown>;
  isStreaming?: boolean;
  timestamp?: string;
}

export type SSEEventType = "token" | "widget" | "done" | "error";

export interface SSETokenPayload {
  type: "token";
  content: string;
}

export interface SSEWidgetPayload {
  type: "widget";
  widget_json: WidgetPayload | Record<string, unknown>;
}

export interface SSEDonePayload {
  type: "done";
  session_id: string;
}

export interface SSEErrorPayload {
  type: "error";
  message: string;
}
