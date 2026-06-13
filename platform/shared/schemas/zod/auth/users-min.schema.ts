import { z } from "zod";

// Minimal auth.users schema for FK validation at boundaries
// Only includes fields needed for purchase.user_id validation
export const authUserIdSchema = z.object({
  id: z.string().uuid(),
});
export type AuthUserId = z.infer<typeof authUserIdSchema>;
