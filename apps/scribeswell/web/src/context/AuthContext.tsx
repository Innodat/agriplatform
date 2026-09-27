/**
 * AuthContext — optional Supabase Auth.
 * Reader works fully signed-out; sign-in enables future user settings.
 */
import {
  createContext,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";
import type { Session, User } from "@supabase/supabase-js";
import { supabase } from "@/lib/supabase";

interface AuthContextValue {
  session: Session | null;
  user: User | null;
  loading: boolean;
  signIn: (email: string, password: string) => Promise<{ error: string | null }>;
  signOut: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [session, setSession] = useState<Session | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active=true,revision=0;
    const {data:listener}=supabase.auth.onAuthStateChange((_event,next)=>{
      revision++;
      if(active){setSession(next);setLoading(false);}
    });
    const initialRevision=revision;
    supabase.auth.getSession().then(({data})=>{
      if(active&&initialRevision===revision){setSession(data.session);setLoading(false);}
    }).catch(()=>{
      if(active&&initialRevision===revision){setSession(null);setLoading(false);}
    });
    return ()=>{active=false;listener.subscription.unsubscribe();};
  }, []);

  async function signIn(email: string, password: string) {
    const { error } = await supabase.auth.signInWithPassword({ email, password });
    return { error: error?.message ?? null };
  }

  async function signOut() {
    const {error}=await supabase.auth.signOut({scope:'local'});
    if(error)throw new Error('We could not sign you out. Please try again.');
  }

  return (
    <AuthContext.Provider
      value={{ session, user: session?.user ?? null, loading, signIn, signOut }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
