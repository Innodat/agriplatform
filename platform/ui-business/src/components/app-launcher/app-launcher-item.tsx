import type { AppEntry } from "@platform/app-directory-client";
import { BookOpen, Library, LayoutGrid, ArrowUpRight } from "lucide-react";

interface AppLauncherItemProps {
  app: AppEntry;
  onClose: () => void;
  current?: boolean;
}

export function AppLauncherItem({ app, onClose, current = false }: AppLauncherItemProps) {
  const Icon = app.icon === 'book-open' ? BookOpen : app.icon === 'library' ? Library : LayoutGrid;
  return (
    <a href={app.url} target="_blank" rel="noopener noreferrer" onClick={onClose}
      role="menuitem" tabIndex={-1} className="platform-app-link" aria-label={`Open ${app.name}`}
      aria-current={current ? 'page' : undefined}>
      <span className="platform-app-icon" aria-hidden="true"><Icon /></span>
      <span className="platform-app-copy">
        <span className="platform-app-title">{app.name}</span>
        <span className="platform-app-description">{app.description}</span>
        {current && <span className="platform-app-current">Current app</span>}
      </span>
      <ArrowUpRight className="platform-app-arrow" aria-hidden="true" />
    </a>
  );
}
