/**
 * App Directory — Zod schemas + inferred TypeScript types.
 *
 * These mirror the Pydantic schemas in:
 *   services/app-directory/schemas/app_schemas.py
 *
 * Keep in sync. If you change a field, update both.
 */
import { z } from "zod";

// ── AppEntry ──────────────────────────────────────────────────────────────────

export const AppEntrySchema = z.object({
  id: z.string(),
  name: z.string(),
  url: z.string().url(),
  icon: z.string(),          // lucide-react icon name, e.g. "book-open"
  description: z.string(),
  enabled: z.boolean(),
});

export type AppEntry = z.infer<typeof AppEntrySchema>;

// ── MeContext ─────────────────────────────────────────────────────────────────

export const MeContextSchema = z.object({
  org_id: z.string().nullable(),
  member_id: z.number().nullable(),
  roles: z.array(z.string()),
});

export type MeContext = z.infer<typeof MeContextSchema>;

// ── MeAppsResponse ────────────────────────────────────────────────────────────

export const MeAppsResponseSchema = z.object({
  apps: z.array(AppEntrySchema),
  context: MeContextSchema,
});

export type MeAppsResponse = z.infer<typeof MeAppsResponseSchema>;
