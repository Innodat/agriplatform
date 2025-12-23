// --- Secret Access ---
const ALLOWED_ORIGINS_SECRET = Deno.env.get("ALLOWED_ORIGINS");
const allowedOrigins = ALLOWED_ORIGINS_SECRET
  ? ALLOWED_ORIGINS_SECRET.split(',').map(s => s.trim()) // .trim() is important for whitespace safety!
  : [];

export const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers":
    "authorization, x-client-info, apikey, content-type",
  "Access-Control-Allow-Methods": "GET, POST, PUT, OPTIONS",
};

export function handleCors(req: Request): Response | null {
  const origin = req.headers.get("origin");
  const headers = { ...corsHeaders };
  if (origin) {
    if (allowedOrigins.includes(origin)) {
      headers["Access-Control-Allow-Origin"] = origin;
    } else {
      headers["Access-Control-Allow-Origin"] = "null";
    }
  }  // else Non-browser requests are allowed to proceed
  if (req.method === "OPTIONS") {
    return new Response("ok", { headers: headers });
  }
  return null;
}

export function mergeCorsHeaders(extra?: HeadersInit) {
  const resHeaders = new Headers(corsHeaders);
  if (extra) {
    new Headers(extra).forEach((value, key) => resHeaders.set(key, value));
  }
  return resHeaders;
}
