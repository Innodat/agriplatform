import { createClient } from '@supabase/supabase-js';

export const supabase = createClient(
  import.meta.env.VITE_SUPABASE_URL!,
  import.meta.env.VITE_SUPABASE_ANON_KEY!
);

/**
 * Authentication helper functions
 */
export const authHelpers = {
  /**
   * Sign in with email and password
   */
  signIn: async (email: string, password: string) => {
    return supabase.auth.signInWithPassword({ email, password })
  },
  
  /**
   * Sign in with OAuth provider (Microsoft)
   */
  signInWithOAuth: async (provider: 'azure') => {
    return supabase.auth.signInWithOAuth({
      provider,
      options: {
        scopes: 'openid email profile',
        redirectTo: `${window.location.origin}/auth/callback`
      }
    })
  },
  
  /**
   * Sign out current user
   */
  signOut: async () => {
    return supabase.auth.signOut()
  },
  
  /**
   * Get current session
   */
  getSession: async () => {
    return supabase.auth.getSession()
  },
  
  /**
   * Get current user
   */
  getUser: async () => {
    return supabase.auth.getUser()
  },
  
  /**
   * Send password reset email
   */
  resetPasswordForEmail: async (email: string) => {
    return supabase.auth.resetPasswordForEmail(email, {
      redirectTo: `${window.location.origin}/auth/reset-password`
    })
  },
  
  /**
   * Update user password
   */
  updatePassword: async (newPassword: string) => {
    return supabase.auth.updateUser({ password: newPassword })
  },
  
  /**
   * Listen for auth state changes
   */
  onAuthStateChange: (callback: (event: string, session: any) => void) => {
    return supabase.auth.onAuthStateChange(callback)
  }
}
