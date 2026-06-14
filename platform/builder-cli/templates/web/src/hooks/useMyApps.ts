/**
 * useMyApps — fetches the current user's available apps from the app-directory service.
 * Returns an empty list when the user is not signed in (anonymous).
 * Silently swallows errors (service unavailable = no launcher shown).
 */
import { useState, useEffect } from "react";
import type { AppEntry } from "@platform/app-directory-client";
import { appDirectoryClient } from "@/lib/app-directory";
import { useAuth } from "@/context/AuthContext";

interface UseMyAppsResult {
  apps: AppEntry[];
  loading: boolean;
}

export function useMyApps(): UseMyAppsResult {
  const { user, loading: authLoading } = useAuth();
  const [apps, setApps] = useState<AppEntry[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (authLoading) return;
    let cancelled = false;
    setLoading(true);
    appDirectoryClient
      .getMyApps()
      .then(({ apps: fetchedApps }) => {
        if (!cancelled) setApps(fetchedApps);
      })
      .catch(() => {
        if (!cancelled) setApps([]);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => { cancelled = true; };
  }, [user, authLoading]);

  return { apps, loading };
}
