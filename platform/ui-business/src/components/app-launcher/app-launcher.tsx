/**
 * AppLauncher — generic, data-driven burger menu / app switcher.
 *
 * Receives `apps` as props — knows no hardcoded apps.
 * Data comes from the app-directory service via useMyApps() in the consuming app.
 *
 * Usage:
 *   <AppLauncher apps={apps} isLoading={loading} />
 *
 * Accessibility:
 *   - Button has aria-label and aria-expanded
 *   - Dropdown has role="menu" with role="menuitem" children
 *   - Keyboard: Escape closes; click outside closes
 */
import { useState, useRef, useEffect } from "react";
import { LayoutGrid } from "lucide-react";
import type { AppEntry } from "@platform/app-directory-client";
import { AppLauncherItem } from "./app-launcher-item";

interface AppLauncherProps {
  /** Apps to display. Pass an empty array to hide the launcher. */
  apps: AppEntry[];
  /** Show a loading skeleton while apps are being fetched. */
  isLoading?: boolean;
  /** Optional label for the trigger button (default: "App launcher"). */
  label?: string;
}

export function AppLauncher({
  apps,
  isLoading = false,
  label = "App launcher",
}: AppLauncherProps) {
  const [open, setOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  // Close on click outside
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

  // Close on Escape
  useEffect(() => {
    if (!open) return;
    function handleKey(e: KeyboardEvent) {
      if (e.key === "Escape") setOpen(false);
    }
    document.addEventListener("keydown", handleKey);
    return () => document.removeEventListener("keydown", handleKey);
  }, [open]);

  // Don't render if no apps and not loading
  if (!isLoading && apps.length === 0) return null;

  return (
    <div ref={containerRef} className="relative">
      {/* Trigger */}
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

      {/* Dropdown */}
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
