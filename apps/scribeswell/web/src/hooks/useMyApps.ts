/**
 * useMyApps — fetches the current user's available apps from the app-directory service.
 *
 * Anonymous readers see enabled public catalogue links; links grant no access.
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
    // Wait for auth to resolve before fetching
    if (authLoading) return;

    let cancelled = false;
    setApps([]);
    setLoading(true);

    const listing=user?appDirectoryClient.getMyApps().then(result=>result.apps):appDirectoryClient.getAllApps();
    listing.then(fetchedApps => {
        if (!cancelled) setApps(fetchedApps.filter(app=>app.enabled));
      })
      .catch(() => {
        // Service unavailable — silently show no launcher
        if (!cancelled) setApps([]);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [user, authLoading]); // re-fetch when auth state changes

  return { apps, loading };
}
