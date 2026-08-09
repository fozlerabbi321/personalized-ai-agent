import { z } from "zod";

export const MessageRoleSchema = z.enum(["human", "assistant"]);

export const MessageSchema = z.object({
  id: z.string(),
  role: MessageRoleSchema,
  content: z.string(),
  widget_json: z.record(z.string(), z.unknown()).nullable().optional(),
  isStreaming: z.boolean().optional(),
  timestamp: z.string().optional(),
});

export const SSETokenPayloadSchema = z.object({
  type: z.literal("token"),
  content: z.string(),
});

export const SSEWidgetPayloadSchema = z.object({
  type: z.literal("widget"),
  widget_json: z.record(z.string(), z.unknown()),
});

export const SSEDonePayloadSchema = z.object({
  type: z.literal("done"),
  session_id: z.string(),
});

export const SSEErrorPayloadSchema = z.object({
  type: z.literal("error"),
  message: z.string(),
});

export type MessageRole = z.infer<typeof MessageRoleSchema>;
export type Message = z.infer<typeof MessageSchema>;
