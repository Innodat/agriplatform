import { BrowserRouter, Routes, Route } from "react-router-dom";
import { StudiesProvider } from "@/context/StudiesContext";
import { AuthProvider } from "@/context/AuthContext";
import { AppShell } from "@/components/layout/AppShell";
import { ReaderPage } from "@/pages/ReaderPage";

export default function App() {
  return (
    <BrowserRouter basename={import.meta.env.BASE_URL}>
      <AuthProvider>
        <StudiesProvider><AppShell>
          <Routes>
            <Route path="/" element={<ReaderPage />} />
          </Routes>
        </AppShell></StudiesProvider>
      </AuthProvider>
    </BrowserRouter>
  );
}
