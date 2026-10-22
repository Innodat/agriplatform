/**
 * Supabase client — Auth only (no data CRUD).
 * Data always flows through FastAPI → /api/bible/*
 */
import { createClient } from "@supabase/supabase-js";
import { consumeCallbackError, hasAccountCallback, scrubAccountCallback } from './account-entry';

const callbackPresent = hasAccountCallback();
export const callbackFailed = consumeCallbackError();
let verifyingCallback = callbackPresent && !callbackFailed;
const authFetch: typeof fetch = async (input, init) => {
  const deadline = AbortSignal.timeout(15000);
  const caller = init?.signal || (input instanceof Request ? input.signal : undefined);
  try {
    const response = await fetch(input, {...init, signal: caller ? AbortSignal.any([caller, deadline]) : deadline});
    if (verifyingCallback && new URL(input instanceof Request ? input.url : String(input)).pathname.endsWith('/auth/v1/user') && !response.ok) {
      // The SDK removes the stored session for session_not_found, even when
      // verifying a different callback JWT. Keep this startup failure separate
      // from ordinary session errors; never restore old storage after sign-out.
      return new Response(JSON.stringify({error_code: 'callback_invalid', msg: 'Authentication callback could not be verified.'}), {status: response.status, headers: {'Content-Type': 'application/json'}});
    }
    return response;
  } catch {
    // Auth SDK logs transport exceptions before mapping them. Never pass through
    // a transport's message, request body or callback data to that diagnostic path.
    throw new Error('Authentication service request failed.');
  }
};

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL as string;
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY as string;

if (!supabaseUrl || !supabaseAnonKey) {
  console.warn(
    "[scribeswell] VITE_SUPABASE_URL or VITE_SUPABASE_ANON_KEY not set — Auth features disabled"
  );
}

export const supabase = createClient(
  supabaseUrl ?? "https://placeholder.supabase.co",
  supabaseAnonKey ?? "placeholder",
  // Retain the existing PtS key so already signed-in users keep their session.
  // Apps must use the same browser origin and Supabase project.
  {auth:{storageKey:'pts-auth'},global:{fetch:authFetch}}
);

export const callbackRecovery = supabase.auth.initialize().then(({error}) => {
  if (callbackPresent) scrubAccountCallback();
  return callbackFailed || (callbackPresent && Boolean(error));
}).catch(() => {
  if (callbackPresent) scrubAccountCallback();
  return callbackPresent;
}).finally(() => {verifyingCallback = false;});
