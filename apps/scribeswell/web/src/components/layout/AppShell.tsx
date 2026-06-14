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
    <div className="min-h-screen bg-stone-50 flex flex-col">
      <Topbar />
      <main className="flex-1 container mx-auto px-4 py-6 max-w-5xl">
        {children}
      </main>
    </div>
  );
}
