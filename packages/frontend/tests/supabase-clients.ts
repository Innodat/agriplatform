// tests/supabase-clients.ts
import { createClient, type SupabaseClient } from '@supabase/supabase-js';

const url = process.env.SUPABASE_URL!;
const anon = process.env.SUPABASE_ANON_KEY!;
const service = process.env.SUPABASE_SERVICE_ROLE_KEY!;

export const serviceClient: SupabaseClient = createClient(url, service, {
  auth: { persistSession: false },
});
export const anonClient: SupabaseClient = createClient(url, anon, {
  auth: { persistSession: false },
});

export async function getUserClient(email: string, password: string) {
  const c = createClient(url, anon, { auth: { persistSession: false } });
  const { error } = await c.auth.signInWithPassword({ email, password });
  if (error) throw error;
  return c;
}
