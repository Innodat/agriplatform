/**
 * AppLauncherItem — a single app link in the launcher dropdown.
 * Renders the app icon (lucide-react by name), name, and description.
 */
import type { AppEntry } from "@platform/app-directory-client";
import { ExternalLink } from "lucide-react";

interface AppLauncherItemProps {
  app: AppEntry;
  onClose: () => void;
}

export function AppLauncherItem({ app, onClose }: AppLauncherItemProps) {
  return (
    <a
      href={app.url}
      target="_blank"
      rel="noopener noreferrer"
      onClick={onClose}
      className="flex items-start gap-3 px-3 py-2.5 rounded-md hover:bg-stone-100 transition-colors group"
      aria-label={`Open ${app.name}`}
    >
      {/* Icon placeholder — apps use lucide icon names; render a generic grid icon */}
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
