import { createClient } from "npm:@supabase/supabase-js@2.91.0";
import { getAccessToken, supabaseAdmin } from "./supabase.ts";

export class HttpError extends Error {
  constructor(message: string, public status = 400) {
    super(message);
    this.name = "HttpError";
  }
}

export interface AuthContext {
  userId: string;
  token: string;
  roles: string[];
  roleIds: number[];
  departmentIds: number[];
  payload: Record<string, unknown>;
}

function decodeJwtPayload(token: string): Record<string, unknown> {

  const segments = token.split(".");
  if (segments.length < 2) {
    throw new HttpError("Invalid access token", 401);
  }

  const base64 = segments[1].replace(/-/g, "+").replace(/_/g, "/");
  const padded = base64.padEnd(base64.length + (4 - (base64.length % 4)) % 4, "=");
  const decoded = atob(padded);
  try {
    return JSON.parse(decoded);
  } catch {
    throw new HttpError("Unable to parse access token", 401);
  }
}

function extractRoles(payload: Record<string, unknown>): string[] {
  const roles = new Set<string>();

  const primaryRole = payload["user_role"] ?? payload["role"] ?? payload["app_role"];
  if (typeof primaryRole === "string" && primaryRole.length > 0) {
    roles.add(primaryRole);
  }

  const roleList = payload["roles"];
  if (Array.isArray(roleList)) {
    roleList.forEach((role) => {
      if (typeof role === "string" && role.length > 0) {
        roles.add(role);
      }
    });
  }

  return Array.from(roles);
}

function extractNumberArray(value: unknown): number[] {
  if (!Array.isArray(value)) return [];
  return value
    .map((item) => {
      if (typeof item === "number") return item;
      if (typeof item === "string" && item.trim().length > 0) {
        const parsed = Number(item);
        return Number.isFinite(parsed) ? parsed : undefined;
      }
      return undefined;
    })
    .filter((item): item is number => typeof item === "number" && !Number.isNaN(item));
}


export async function requireAuth(req: Request): Promise<AuthContext> {
  const token = getAccessToken(req);
  if (!token || token.split(".").length !== 3) {
    throw new HttpError("Unauthorized", 401);
  }

  const SUPABASE_URL = Deno.env.get("SUPABASE_URL");
  const SUPABASE_ANON_KEY = Deno.env.get("SUPABASE_ANON_KEY");
  if (!SUPABASE_URL || !SUPABASE_ANON_KEY) {
    throw new HttpError("Server misconfigured", 500);
  }

  // Request-scoped client; forward the user's Authorization header
  const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY, {
    global: { headers: { Authorization: `Bearer ${token}` } },
  });

  // Let Supabase Auth validate the token
  const { data: { user }, error } = await supabase.auth.getUser();
  if (error || !user) throw new HttpError("Unauthorized", 401);

  // Your existing helpers
  const payload = decodeJwtPayload(token);
  const roles = extractRoles(payload);
  const roleIds = extractNumberArray(payload["role_ids"]);
  const departmentIds = extractNumberArray(payload["department_ids"]);

  return { userId: user.id, token, roles, roleIds, departmentIds, payload };
}


export function hasRole(auth: AuthContext, allowed: string | string[]): boolean {
  const allowedList = Array.isArray(allowed) ? allowed : [allowed];
  return allowedList.some((role) => auth.roles.includes(role));
}

export function requireRole(auth: AuthContext, allowed: string | string[]) {
  if (!hasRole(auth, allowed)) {
    throw new HttpError("Forbidden", 403);
  }
}
