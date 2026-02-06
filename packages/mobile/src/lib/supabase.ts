import 'react-native-url-polyfill/auto';
import { createClient } from '@supabase/supabase-js';
import AsyncStorage from '@react-native-async-storage/async-storage';

const SUPABASE_URL = "http://10.0.0.140:54321"
const SUPABASE_ANON_KEY = "sb_publishable_ACJWlzQHlZjBrEguHvfOxg_3BJgxAaH"

if (!SUPABASE_URL || !SUPABASE_ANON_KEY) {
  // Helpful error to catch misconfig early
  throw new Error(
    'Missing SUPABASE_URL or SUPABASE_ANON_KEY. Check your .env and native build config.'
  );
}

export const supabaseUrl = SUPABASE_URL;

export const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY, {
  auth: {
    storage: AsyncStorage,
    autoRefreshToken: true,
    persistSession: true,
    detectSessionInUrl: false,
  },
});
