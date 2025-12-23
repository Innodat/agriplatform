import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const supabaseUrl = Deno.env.get("SUPABASE_URL");
const supabaseServiceKey = Deno.env.get("SUPABASE_SECRET_KEY") || Deno.env.get("SUPABASE_ANON_KEY");

if (!supabaseUrl) {
  // throw new Error("Missing SUPABASE_URL environment variable");
  console.warn("Missing SUPABASE_URL environment variable");
}
if (!supabaseServiceKey) {
  // throw new Error("Missing SUPABASE_SECRET_KEY environment variable");
  console.warn("Missing SUPABASE_SECRET_KEY environment variable");
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
