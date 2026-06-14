/**
 * Topbar — brand + AppLauncher (burger) + Sign In / user menu.
 * Replace "{{APP_DISPLAY_NAME}}" with your app's display name.
 */
import { LogIn, LogOut, User } from "lucide-react";
import { useState } from "react";
import { useAuth } from "@/context/AuthContext";
import { AppLauncher } from "@/components/layout/AppLauncher";
import { useMyApps } from "@/hooks/useMyApps";

export function Topbar() {
  const { user, signOut, loading } = useAuth();
  const [showSignIn, setShowSignIn] = useState(false);
  const { apps, loading: appsLoading } = useMyApps();

  return (
    <header className="bg-white border-b border-stone-200 shadow-sm">
      <div className="container mx-auto px-4 max-w-5xl h-14 flex items-center justify-between">
        {/* Left: AppLauncher + Brand */}
        <div className="flex items-center gap-3">
          <AppLauncher apps={apps} isLoading={appsLoading} />
          <span className="font-semibold text-lg tracking-tight text-stone-800">
            {{APP_DISPLAY_NAME}}
          </span>
        </div>

        {/* Right: Auth */}
        {!loading && (
          <div className="flex items-center gap-2">
            {user ? (
              <>
                <span className="text-sm text-stone-500 flex items-center gap-1">
                  <User className="w-4 h-4" aria-hidden="true" />
                  {user.email}
                </span>
                <button
                  onClick={() => void signOut()}
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
      {/* TODO: add SignInDialog here */}
      {showSignIn && <div />}
    </header>
  );
}
