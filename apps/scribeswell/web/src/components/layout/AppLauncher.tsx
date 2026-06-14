/**
 * AppLauncher — app-local copy of the platform/ui-business AppLauncher.
 *
 * Vendored from platform/ui-business/src/components/app-launcher/
 * Per silo rules: no runtime import from platform/*.
 *
 * Generic, data-driven burger menu. Receives `apps` as props.
 * Data comes from useMyApps() hook in the consuming component.
 */
import { useState, useRef, useEffect } from "react";
import { LayoutGrid, ExternalLink } from "lucide-react";
import type { AppEntry } from "@platform/app-directory-client";

// ── AppLauncherItem ───────────────────────────────────────────────────────────

interface AppLauncherItemProps {
  app: AppEntry;
  onClose: () => void;
}

function AppLauncherItem({ app, onClose }: AppLauncherItemProps) {
  return (
    <a
      href={app.url}
      target="_blank"
      rel="noopener noreferrer"
      onClick={onClose}
      className="flex items-start gap-3 px-3 py-2.5 rounded-md hover:bg-stone-100 transition-colors group"
      aria-label={`Open ${app.name}`}
    >
      <span
        className="mt-0.5 w-8 h-8 rounded-md bg-stone-200 flex items-center justify-center text-stone-500 text-xs font-bold shrink-0"
        aria-hidden="true"
      >
        {app.name.slice(0, 2).toUpperCase()}
      </span>
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-1">
          <span className="text-sm font-medium text-stone-800 truncate">
            {app.name}
          </span>
          <ExternalLink
            className="w-3 h-3 text-stone-400 opacity-0 group-hover:opacity-100 transition-opacity shrink-0"
            aria-hidden="true"
          />
        </div>
        <p className="text-xs text-stone-500 truncate">{app.description}</p>
      </div>
    </a>
  );
}

// ── AppLauncher ───────────────────────────────────────────────────────────────

interface AppLauncherProps {
  apps: AppEntry[];
  isLoading?: boolean;
  label?: string;
}

export function AppLauncher({
  apps,
  isLoading = false,
  label = "App launcher",
}: AppLauncherProps) {
  const [open, setOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!open) return;
    function handleClick(e: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, [open]);

  useEffect(() => {
    if (!open) return;
    function handleKey(e: KeyboardEvent) {
      if (e.key === "Escape") setOpen(false);
    }
    document.addEventListener("keydown", handleKey);
    return () => document.removeEventListener("keydown", handleKey);
  }, [open]);

  if (!isLoading && apps.length === 0) return null;

  return (
    <div ref={containerRef} className="relative">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        aria-label={label}
        aria-expanded={open}
        aria-haspopup="menu"
        className="flex items-center justify-center w-8 h-8 rounded-md text-stone-500 hover:text-stone-800 hover:bg-stone-100 transition-colors"
      >
        <LayoutGrid className="w-5 h-5" aria-hidden="true" />
      </button>

      {open && (
        <div
          role="menu"
          aria-label="Available apps"
          className="absolute left-0 top-full mt-1 w-72 bg-white border border-stone-200 rounded-lg shadow-lg z-50 py-1 overflow-hidden"
        >
          {isLoading ? (
            <div className="px-3 py-4 space-y-2">
              {[1, 2, 3].map((i) => (
                <div key={i} className="flex items-center gap-3 animate-pulse">
                  <div className="w-8 h-8 rounded-md bg-stone-200 shrink-0" />
                  <div className="flex-1 space-y-1">
                    <div className="h-3 bg-stone-200 rounded w-24" />
                    <div className="h-2 bg-stone-100 rounded w-40" />
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <>
              <p className="px-3 pt-2 pb-1 text-xs font-medium text-stone-400 uppercase tracking-wide">
                Apps
              </p>
              {apps.map((app) => (
                <div key={app.id} role="menuitem">
                  <AppLauncherItem app={app} onClose={() => setOpen(false)} />
                </div>
              ))}
            </>
          )}
        </div>
      )}
    </div>
  );
}
