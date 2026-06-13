// lib/supabase-factory.ts (pure, no env access here)
import { createClient, type SupabaseClient, type SupabaseClientOptions } from '@supabase/supabase-js';

export function makeSupabase(
  url: string,
  key: string,
  options?: SupabaseClientOptions<'public'>
): SupabaseClient {
  return createClient(url, key, options);
}
