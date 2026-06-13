import { createContext, useContext, useEffect, useState } from 'react'
import type { ReactNode } from 'react'
import type { User, Session } from '@supabase/supabase-js'
import { supabase, authHelpers } from '../lib/supabase/client'
import type { AppRole } from '../../../shared/schemas/zod/identity/user-roles.schema'

interface AuthContextType {
  user: User | null
  session: Session | null
  roles: AppRole[]
  loading: boolean
  signIn: (email: string, password: string) => Promise<{ error: Error | null }>
  signInWithMicrosoft: () => Promise<{ error: Error | null }>
  signOut: () => Promise<void>
  hasRole: (role: AppRole) => boolean
  isAdmin: boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

interface AuthProviderProps {
  children: ReactNode
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null)
  const [session, setSession] = useState<Session | null>(null)
  const [roles, setRoles] = useState<AppRole[]>([])
  const [loading, setLoading] = useState(true)

  /**
   * Fetch user roles from identity.user_roles table
   */
  const fetchUserRoles = async (userId: string): Promise<AppRole[]> => {
    try {
      // Call the database function to get user roles
      console.log("Get Roles...");
      const { data, error } = await supabase.rpc('get_user_roles')

      if (error) {
        console.error('Error fetching user roles:', error)
        return []
      }

      // data is an array of objects with 'role' property
      return (data || []).map((item: { role: string }) => item.role as AppRole)
    } catch (error) {
      console.error('Error fetching user roles:', error)
      return []
    }
  }

  /**
   * Initialize auth state on mount
   */
  useEffect(() => {
    // Check for existing session
    authHelpers.getSession().then(({ data: { session } }) => {
      setSession(session)
      setUser(session?.user ?? null)
      
      if (session?.user) {
        fetchUserRoles(session.user.id).then(setRoles)
      }
      
      setLoading(false)
    })

    // Listen for auth state changes
    const { data: { subscription } } = authHelpers.onAuthStateChange(
      async (event, session) => {
        console.log('Auth state changed:', event)
        console.log(session);
        setSession(session)
        setUser(session?.user ?? null)
        
        if (session?.user) {
          const userRoles = await fetchUserRoles(session.user.id)
          setRoles(userRoles)
        } else {
          setRoles([])
        }
        
        setLoading(false)
      }
    )

    return () => {
      subscription.unsubscribe()
    }
  }, [])

  /**
   * Sign in with email and password
   */
  const signIn = async (email: string, password: string) => {
    try {
      const { data, error } = await authHelpers.signIn(email, password)
      
      if (error) {
        return { error: new Error(error.message) }
      }

      if (data.user) {
        const userRoles = await fetchUserRoles(data.user.id)
        setRoles(userRoles)
      }

      return { error: null }
    } catch (error) {
      return { 
        error: error instanceof Error ? error : new Error('Failed to sign in') 
      }
    }
  }

  /**
   * Sign in with Microsoft OAuth
   */
  const signInWithMicrosoft = async () => {
    try {
      const { error } = await authHelpers.signInWithOAuth('azure')
      
      if (error) {
        return { error: new Error(error.message) }
      }

      return { error: null }
    } catch (error) {
      return { 
        error: error instanceof Error ? error : new Error('Failed to sign in with Microsoft') 
      }
    }
  }

  /**
   * Sign out current user
   */
  const signOut = async () => {
    await authHelpers.signOut()
    setUser(null)
    setSession(null)
    setRoles([])
  }

  /**
   * Check if user has a specific role
   */
  const hasRole = (role: AppRole): boolean => {
    return roles.includes(role)
  }

  /**
   * Check if user is an admin (admin or financeadmin)
   */
  const isAdmin = hasRole('admin') || hasRole('financeadmin')

  const value: AuthContextType = {
    user,
    session,
    roles,
    loading,
    signIn,
    signInWithMicrosoft,
    signOut,
    hasRole,
    isAdmin
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

/**
 * Hook to access auth context
 */
export function useAuth() {
  const context = useContext(AuthContext)
  
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  
  return context
}
