// src/lib/supabase.ts
import 'dotenv/config'; // loads .env.test
import { createClient } from '@supabase/supabase-js';

// These should be exposed to the client via Vite (VITE_ prefix) if used in the browser.
// For server-only routes, you can use non-VITE_ envs in Node.
const url = import.meta.env.VITE_SUPABASE_URL!;
const anon = import.meta.env.VITE_SUPABASE_ANON_KEY!;

export const supabase = createClient(url, anon, {
  auth: {
    persistSession: true,
    autoRefreshToken: true,
    detectSessionInUrl: true,
  },
});