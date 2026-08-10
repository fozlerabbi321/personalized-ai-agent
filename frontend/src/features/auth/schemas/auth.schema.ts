import { z } from "zod";

export const UserSchema = z.object({
  user_id: z.string(),
  email: z.string().email(),
});

export const TokenResponseSchema = z.object({
  access_token: z.string(),
  token_type: z.string().default("bearer"),
});

export const LoginRequestSchema = z.object({
  email: z.string().email(),
  password: z.string().min(1, "Password is required"),
});

export const RegisterRequestSchema = z.object({
  email: z.string().email("Invalid email address"),
  password: z.string().min(6, "Password must be at least 6 characters"),
});
