/**
 * App Directory client — singleton for this app.
 *
 * Wraps @platform/app-directory-client with the app's Supabase session token.
 * Import this instead of creating the client directly in components.
 */
import { createAppDirectoryClient } from "@platform/app-directory-client";
import { supabase } from "./supabase";

export const appDirectoryClient = createAppDirectoryClient({
  baseUrl: import.meta.env.VITE_APP_DIRECTORY_URL ?? "http://localhost:8001",
  getToken: async () => {
    const { data } = await supabase.auth.getSession();
    return data.session?.access_token ?? null;
  },
});
