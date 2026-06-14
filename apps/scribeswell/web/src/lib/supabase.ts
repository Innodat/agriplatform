/**
 * Supabase client — Auth only (no data CRUD).
 * Data always flows through FastAPI → /api/bible/*
 */
import { createClient } from "@supabase/supabase-js";

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL as string;
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY as string;

if (!supabaseUrl || !supabaseAnonKey) {
  console.warn(
    "[scribeswell] VITE_SUPABASE_URL or VITE_SUPABASE_ANON_KEY not set — Auth features disabled"
  );
}

export const supabase = createClient(
  supabaseUrl ?? "https://placeholder.supabase.co",
  supabaseAnonKey ?? "placeholder"
);
