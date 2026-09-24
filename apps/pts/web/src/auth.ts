import {createClient} from '@supabase/supabase-js';
export const configured=Boolean(import.meta.env.VITE_SUPABASE_URL && import.meta.env.VITE_SUPABASE_ANON_KEY);
export const auth=createClient(import.meta.env.VITE_SUPABASE_URL || 'https://unconfigured.invalid',import.meta.env.VITE_SUPABASE_ANON_KEY || 'unconfigured',{auth:{storageKey:'pts-auth'}}).auth;
export type Identity={id:string;token:string};
