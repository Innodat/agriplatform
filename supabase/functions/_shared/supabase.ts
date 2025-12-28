import { createClient, SupabaseClient } from "https://esm.sh/@supabase/supabase-js@2";

// When running locally via `supabase functions serve --env-file .env`,
// we expect these values to be present.
// When running via Supabase gateway (e.g. integration tests hitting
// http://localhost:54321/functions/v1/*), function runtime still has access
// to Supabase internal network, so defaulting SUPABASE_URL to localhost
// keeps admin client working even if env injection is misconfigured.

const url = Deno.env.get("SUPABASE_URL") ?? "http://localhost:54321";
const key = Deno.env.get("SUPABASE_SECRET_KEY") || Deno.env.get("SUPABASE_SERVICE_ROLE_KEY");

if (!url) {
  console.warn("Missing SUPABASE_URL environment variable");
}
if (!key) {
  throw new Error("Missing SUPABASE_SECRET_KEY environment variable for admin operations");
}

export const supabaseAdmin: SupabaseClient = createClient(url, key, {
  auth: {
    persistSession: false,
  },
});

export function getAccessToken(req: Request) {
  const authHeader =
    req.headers.get("Authorization") ?? req.headers.get("authorization");
  if (!authHeader) return null;
  const token = authHeader.replace(/Bearer\s+/i, "").trim();
  return token || null;
}
