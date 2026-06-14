/**
 * App Directory — typed fetch client.
 *
 * Usage in any app:
 *   import { createAppDirectoryClient } from "@platform/app-directory-client";
 *
 *   const client = createAppDirectoryClient({
 *     baseUrl: import.meta.env.VITE_APP_DIRECTORY_URL,
 *     getToken: () => supabase.auth.getSession().then(s => s.data.session?.access_token),
 *   });
 *
 *   const { apps, context } = await client.getMyApps();
 */
import { MeAppsResponseSchema, MeContextSchema, AppEntrySchema } from "./schemas";
import type { MeAppsResponse, MeContext, AppEntry } from "./schemas";

export interface AppDirectoryClientOptions {
  /** Base URL of the app-directory service, e.g. "http://localhost:8001" */
  baseUrl: string;
  /**
   * Optional async function that returns the current user's Bearer token.
   * If omitted or returns undefined, requests are sent without Authorization header.
   */
  getToken?: () => Promise<string | undefined | null>;
}

async function fetchJson<T>(
  url: string,
  schema: { parse: (data: unknown) => T },
  token?: string | null
): Promise<T> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const res = await fetch(url, { headers });

  if (!res.ok) {
    let errorMessage = `App Directory request failed: ${res.status} ${res.statusText}`;
    try {
      const body = await res.json();
      if (body?.error) errorMessage = body.error;
    } catch {
      // ignore parse error
    }
    throw new Error(errorMessage);
  }

  const data = await res.json();
  return schema.parse(data);
}

export function createAppDirectoryClient(options: AppDirectoryClientOptions) {
  const { baseUrl, getToken } = options;
  const base = baseUrl.replace(/\/$/, "");

  async function token(): Promise<string | undefined | null> {
    return getToken ? getToken() : undefined;
  }

  return {
    /**
     * GET /api/me/apps
     * Returns apps available to the current user + identity context.
     */
    async getMyApps(): Promise<MeAppsResponse> {
      const t = await token();
      return fetchJson(`${base}/api/me/apps`, MeAppsResponseSchema, t);
    },

    /**
     * GET /api/me/context
     * Returns the current user's org_id, member_id, and roles.
     */
    async getMyContext(): Promise<MeContext> {
      const t = await token();
      return fetchJson(`${base}/api/me/context`, MeContextSchema, t);
    },

    /**
     * GET /api/apps
     * Returns the full catalog including disabled apps.
     */
    async getAllApps(): Promise<AppEntry[]> {
      const t = await token();
      return fetchJson(`${base}/api/apps`, AppEntrySchema.array(), t);
    },
  };
}

export type AppDirectoryClient = ReturnType<typeof createAppDirectoryClient>;
