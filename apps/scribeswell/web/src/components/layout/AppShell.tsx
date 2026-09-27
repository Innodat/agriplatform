/**
 * AppShell — top-level layout: Topbar + main content area.
 * Sidebar is omitted for the reader (single-domain app).
 */
import type { ReactNode } from "react";
import { Topbar } from "./Topbar";

interface AppShellProps {
  children: ReactNode;
}

export function AppShell({ children }: AppShellProps) {
  return (
    <div className="h-dvh bg-stone-50 flex flex-col">
      <Topbar />
      <main className="flex-1 min-h-0 w-full mx-auto px-4 py-4 max-w-5xl">
        {children}
      </main>
    </div>
  );
}
