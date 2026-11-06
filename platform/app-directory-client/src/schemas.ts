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

function safeAppUrl(value:string){
  try{const url=new URL(value);return !url.username&&!url.password&&!url.search&&!url.hash&&(url.protocol==='https:'||url.protocol==='http:'&&['localhost','127.0.0.1','[::1]'].includes(url.hostname));}catch{return false;}
}

/** A current observation; unavailable/anonymous responses can never carry links. */
export const CurrentAppsResponseSchema = z.object({
  apps: z.array(AppEntrySchema).max(128),
  protected_access_status: z.enum(['complete', 'sign_in_required', 'unavailable']),
}).strict().superRefine((value, context) => {
  if ((value.protected_access_status !== 'complete' && value.apps.length) ||
      new Set(value.apps.map(app => app.id)).size !== value.apps.length || value.apps.some(app => !app.enabled || !safeAppUrl(app.url))) {
    context.addIssue({code: z.ZodIssueCode.custom, message: 'Invalid discovery observation'});
  }
});
export type CurrentAppsResponse = z.infer<typeof CurrentAppsResponseSchema>;
