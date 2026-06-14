/**
 * Topbar — brand + optional Sign In / user menu.
 */
import { BookOpen, LogIn, LogOut, User } from "lucide-react";
import { useState } from "react";
import { useAuth } from "@/context/AuthContext";
import { SignInDialog } from "@/components/auth/SignInDialog";

export function Topbar() {
  const { user, signOut, loading } = useAuth();
  const [showSignIn, setShowSignIn] = useState(false);

  return (
    <header className="bg-white border-b border-stone-200 shadow-sm">
      <div className="container mx-auto px-4 max-w-5xl h-14 flex items-center justify-between">
        {/* Brand */}
        <div className="flex items-center gap-2 text-stone-800">
          <BookOpen className="w-5 h-5 text-amber-600" aria-hidden="true" />
          <span className="font-semibold text-lg tracking-tight">
            Hebrew Bible
          </span>
        </div>

        {/* Auth */}
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

      {showSignIn && <SignInDialog onClose={() => setShowSignIn(false)} />}
    </header>
  );
}
