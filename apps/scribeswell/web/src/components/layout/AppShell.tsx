/**
 * AppShell — top-level layout: Topbar + main content area.
 * Sidebar is omitted for the reader (single-domain app).
 */
import { createContext, useContext, useState, type ReactNode } from "react";
import { Topbar } from "./Topbar";

const ReaderLayoutContext = createContext<{ focused: boolean; setFocused: (value: boolean) => void } | null>(null);

export function useReaderLayout() {
  const context = useContext(ReaderLayoutContext);
  if (!context) throw new Error("Reader layout requires AppShell");
  return context;
}

interface AppShellProps {
  children: ReactNode;
}

export function AppShell({ children }: AppShellProps) {
  const [focused, setFocused] = useState(false);
  return (
    <ReaderLayoutContext.Provider value={{ focused, setFocused }}>
    <div className="h-dvh bg-stone-50 flex flex-col">
      <div hidden={focused} className="shrink-0"><Topbar /></div>
      <main className="flex-1 min-h-0 w-full mx-auto px-4 py-4">
        {children}
      </main>
    </div>
    </ReaderLayoutContext.Provider>
  );
}
