export interface Session {
  session_id: string;
  title: string;
  created_at: string;
  updated_at: string;
  message_count: number;
}

export interface SessionListResponse {
  sessions: Session[];
  total: number;
}

export interface SavedMessage {
  message_id: string;
  role: "human" | "assistant";
  content: string;
  widget_json: any | null;
  created_at: string;
}

export interface SessionMessagesResponse {
  session_id: string;
  messages: SavedMessage[];
}
