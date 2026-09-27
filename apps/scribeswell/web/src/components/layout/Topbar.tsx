/**
 * Topbar — brand + AppLauncher (burger) + Sign In / user menu.
 */
import { BookOpen, LogIn, LogOut, User } from "lucide-react";
import { useEffect, useState } from "react";
import { useAuth } from "@/context/AuthContext";
import { SignInDialog } from "@/components/auth/SignInDialog";
import { AppLauncher } from "@/components/layout/AppLauncher";
import { useMyApps } from "@/hooks/useMyApps";

export function Topbar() {
  const { user, signOut, loading } = useAuth();
  const [signOutError,setSignOutError]=useState('');
  const [showSignIn, setShowSignIn] = useState(false);
  const { apps, loading: appsLoading } = useMyApps();
  useEffect(()=>{if(user){setShowSignIn(false);setSignOutError('');}},[user?.id]);

  return (
    <header className="shrink-0 bg-white border-b border-stone-200 shadow-sm">
      <div className="container mx-auto px-4 max-w-5xl h-14 flex items-center justify-between">
        {/* Left: AppLauncher + Brand */}
        <div className="flex items-center gap-2">
          <AppLauncher apps={apps} isLoading={appsLoading} currentAppId="scribeswell" iconOnly />

          <div className="flex items-center gap-2 text-stone-800">
            <BookOpen className="hidden sm:block w-5 h-5 text-amber-600" aria-hidden="true" />
            <span className="font-semibold text-sm sm:text-lg tracking-tight">
              Scribes' Well
            </span>
          </div>
        </div>

        {/* Right: Auth */}
        {!loading && (
          <div className="flex items-center gap-2">
            {user ? (
              <>
                <span className="hidden sm:flex text-sm text-stone-500 items-center gap-1 max-w-48 truncate">
                  <User className="w-4 h-4" aria-hidden="true" />
                  {user.email}
                </span>
                <button
                  onClick={async()=>{setSignOutError('');try{await signOut();}catch{setSignOutError('We could not sign you out. Please try again.');}}}
                  className="flex items-center gap-1 text-sm text-stone-600 hover:text-stone-900 px-3 py-1.5 rounded-md hover:bg-stone-100 transition-colors"
                  aria-label="Sign out"
                >
                  <LogOut className="w-4 h-4" aria-hidden="true" />
                  Sign out
                </button>
              </>
            ) : (
              <button
                onClick={() => setShowSignIn(true)}
                className="flex items-center gap-1 text-sm text-stone-600 hover:text-stone-900 px-3 py-1.5 rounded-md hover:bg-stone-100 transition-colors"
                aria-label="Sign in"
              >
                <LogIn className="w-4 h-4" aria-hidden="true" />
                Sign in
              </button>
            )}
          </div>
        )}
      </div>

      {signOutError&&<p role="alert" className="px-4 py-2 text-red-700">{signOutError}</p>}
      {showSignIn && !user && <SignInDialog onClose={() => setShowSignIn(false)} />}
    </header>
  );
}
