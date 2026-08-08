export interface Message {
  id: string;
  role: "human" | "assistant";
  content: string;
  widget_json?: any;
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
  widget_json: any;
}

export interface SSEDonePayload {
  type: "done";
  session_id: string;
}

export interface SSEErrorPayload {
  type: "error";
  message: string;
}
