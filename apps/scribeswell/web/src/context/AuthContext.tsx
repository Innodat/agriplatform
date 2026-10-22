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
import { callbackFailed as initialCallbackFailed, callbackRecovery, supabase } from "@/lib/supabase";
import { accountError, publicAccountReturn } from "@/lib/account-entry";

export type SignupOutcome = { status: "authenticated" | "confirmation-pending"; error: null } | { status: "failed"; error: string };

interface AuthContextValue {
  session: Session | null;
  user: User | null;
  loading: boolean;
  callbackFailed: boolean;
  signIn: (email: string, password: string) => Promise<{ error: string | null }>;
  signUp: (email: string, password: string) => Promise<SignupOutcome>;
  signOut: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [session, setSession] = useState<Session | null>(null);
  const [loading, setLoading] = useState(true);
  const [callbackFailed, setCallbackFailed] = useState(initialCallbackFailed);

  useEffect(() => {
    let active=true,revision=0;
    const {data:listener}=supabase.auth.onAuthStateChange((_event,next)=>{
      revision++;
      if(active){setSession(next);setLoading(false);}
    });
    void callbackRecovery.then(failed => {if(active)setCallbackFailed(failed);});
    const initialRevision=revision;
    supabase.auth.getSession().then(({data})=>{
      if(active&&initialRevision===revision){setSession(data.session);setLoading(false);}
    }).catch(()=>{
      if(active&&initialRevision===revision){setSession(null);setLoading(false);}
    });
    return ()=>{active=false;listener.subscription.unsubscribe();};
  }, []);

  async function signIn(email: string, password: string) {
    try {
      const { error } = await supabase.auth.signInWithPassword({ email, password });
      return { error: error ? accountError(error, 'signin') : null };
    } catch (error) { return { error: accountError(error, 'signin') }; }
  }

  async function signUp(email: string, password: string): Promise<SignupOutcome> {
    try {
      const { data, error } = await supabase.auth.signUp({email, password, options: {emailRedirectTo: publicAccountReturn()}});
      if (error) return {status: 'failed', error: accountError(error, 'signup')};
      return {status: data.session ? 'authenticated' : 'confirmation-pending', error: null};
    } catch (error) { return {status: 'failed', error: accountError(error, 'signup')}; }
  }

  async function signOut() {
    const {error}=await supabase.auth.signOut({scope:'local'});
    if(error)throw new Error('We could not sign you out. Please try again.');
  }

  return (
    <AuthContext.Provider
      value={{ session, user: session?.user ?? null, loading, callbackFailed, signIn, signUp, signOut }}
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
