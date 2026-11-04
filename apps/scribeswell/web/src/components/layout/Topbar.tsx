/**
 * Topbar — brand + AppLauncher (burger) + Sign In / user menu.
 */
import { BookOpen, LogIn, LogOut, User } from "lucide-react";
import { useEffect, useState } from "react";
import { useAuth } from "@/context/AuthContext";
import { SignInDialog, type AccountMode } from "@/components/auth/SignInDialog";
import { AppLauncher } from "@/components/layout/AppLauncher";
import { useMyApps } from "@/hooks/useMyApps";

import {useStudies} from "@/context/StudiesContext";

export function Topbar() {
  const studies=useStudies();
  const { user, signOut, loading, callbackFailed } = useAuth();
  const [signOutError,setSignOutError]=useState('');
  const [showSignIn, setShowSignIn] = useState(false);
  const [entryMode,setEntryMode]=useState<AccountMode>('signin');
  const [callbackNotice,setCallbackNotice]=useState(callbackFailed);
  useEffect(() => {if(callbackFailed)setCallbackNotice(true);}, [callbackFailed]);
  useEffect(()=>{const open=(event:Event)=>{setEntryMode((event as CustomEvent<{mode?:string}>).detail?.mode==='signup'?'signup':'signin');setShowSignIn(true);};window.addEventListener('scribeswell-account-entry',open);return()=>window.removeEventListener('scribeswell-account-entry',open);},[]);
  const { apps, loading: appsLoading } = useMyApps();
  useEffect(()=>{if(user){setShowSignIn(false);setSignOutError('');}},[user?.id]);

  return (
    <header className="shrink-0 bg-white border-b border-stone-200 shadow-sm">
      <div className="sw-topbar w-full px-4 max-[359px]:px-2 min-h-14 flex items-center justify-between gap-1">
        {/* Left: AppLauncher + Brand */}
        <div className="flex items-center gap-1 sm:gap-2">
          <AppLauncher apps={apps} isLoading={appsLoading} currentAppId="scribeswell" iconOnly />

          <div className="flex items-center gap-2 text-stone-800">
            <BookOpen className="hidden sm:block w-5 h-5 text-amber-600" aria-hidden="true" />
            <span className="scribeswell-wordmark font-semibold text-sm sm:text-lg tracking-tight">
              Scribes' Well
            </span>
          </div>
        </div>

        {/* Right: Auth */}
        {!loading && (
          <div className="flex items-center gap-1 sm:gap-2">
            {user ? (
              <>
                <span className="hidden sm:flex text-sm text-stone-500 items-center gap-1 max-w-48 truncate">
                  <User className="w-4 h-4" aria-hidden="true" />
                  {user.email}
                </span>
                <button
                  onClick={async()=>{setSignOutError('');try{await studies.exit(async()=>{try{await signOut();}catch{setSignOutError('We could not sign you out. Please try again.');}});}catch{setSignOutError('We could not sign you out. Please try again.');}}}
                  className="flex items-center gap-1 text-sm text-stone-600 hover:text-stone-900 px-1.5 sm:px-3 py-2 min-h-10 rounded-md hover:bg-stone-100 transition-colors"
                  aria-label="Sign out"
                >
                  <LogOut className="w-4 h-4" aria-hidden="true" />
                  Sign out
                </button>
              </>
            ) : (
              <>
              <button onClick={() => {setEntryMode('signup');setShowSignIn(true);}} className="sw-account-create text-xs sm:text-sm text-stone-600 hover:text-stone-900 rounded-md px-1.5 sm:px-2 py-2 min-h-10">Create account</button>
              <button
                onClick={() => {setEntryMode('signin');setShowSignIn(true);}}
                className="flex items-center gap-1 text-sm text-stone-600 hover:text-stone-900 px-1.5 sm:px-3 py-2 min-h-10 rounded-md hover:bg-stone-100 transition-colors"
                aria-label="Sign in"
              >
                <LogIn className="hidden sm:block w-4 h-4" aria-hidden="true" />
                Sign in
              </button>
              </>
            )}
          </div>
        )}
      </div>

      {callbackNotice && <div role="alert" className="px-4 py-2 text-sm text-stone-700">This confirmation link is invalid or has expired. You can continue reading. {!user && <button className="underline mx-2" onClick={() => {setEntryMode('signin');setShowSignIn(true);}}>Sign in</button>}<button className="underline" onClick={() => setCallbackNotice(false)}>Dismiss</button></div>}
      {signOutError&&<p role="alert" className="px-4 py-2 text-red-700">{signOutError}</p>}
      {showSignIn && !user && <SignInDialog initialMode={entryMode} onClose={() => setShowSignIn(false)} />}
    </header>
  );
}
