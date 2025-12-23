import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

// When running locally via `supabase functions serve --env-file .env`,
// we expect these values to be present.
// When running via the Supabase gateway (e.g. integration tests hitting
// http://localhost:54321/functions/v1/*), the function runtime still has access
// to Supabase internal network, so defaulting SUPABASE_URL to localhost
// keeps the admin client working even if env injection is misconfigured.
const supabaseUrl = Deno.env.get("SUPABASE_URL") ?? "http://localhost:54321";
const supabaseServiceKey = Deno.env.get("SUPABASE_SECRET_KEY") || Deno.env.get("SUPABASE_SERVICE_ROLE_KEY");

const envVars = Deno.env.toObject();

// Print them to logs
console.log("Supabase Deno.env variables:", envVars);

if (!supabaseUrl) {
  console.warn("Missing SUPABASE_URL environment variable");
}
if (!supabaseServiceKey) {
  throw new Error("Missing SUPABASE_SECRET_KEY environment variable for admin operations");
}

export const supabaseAdmin = createClient(supabaseUrl ?? "http://localhost:54321", supabaseServiceKey!, {
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
