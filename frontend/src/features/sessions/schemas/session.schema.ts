import { z } from "zod";

export const SessionSchema = z.object({
  session_id: z.string(),
  title: z.string(),
  created_at: z.string(),
  updated_at: z.string(),
  message_count: z.number().default(0),
});

export const SessionListResponseSchema = z.object({
  sessions: z.array(SessionSchema),
  total: z.number(),
});

export const MessageResponseSchema = z.object({
  message_id: z.string(),
  role: z.enum(["human", "assistant"]),
  content: z.string(),
  widget_json: z.union([z.record(z.string(), z.unknown()), z.string()]).nullable().optional(),
  created_at: z.string(),
});

export const SessionMessagesResponseSchema = z.object({
  session_id: z.string(),
  messages: z.array(MessageResponseSchema),
});

export type Session = z.infer<typeof SessionSchema>;
export type SessionListResponse = z.infer<typeof SessionListResponseSchema>;
export type MessageResponse = z.infer<typeof MessageResponseSchema>;
export type SessionMessagesResponse = z.infer<typeof SessionMessagesResponseSchema>;
