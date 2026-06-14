import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AuthProvider } from "@/context/AuthContext";
import { AppShell } from "@/components/layout/AppShell";
import { ReaderPage } from "@/pages/ReaderPage";

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppShell>
          <Routes>
            <Route path="/" element={<ReaderPage />} />
            <Route path="/:osisId" element={<ReaderPage />} />
            <Route path="/:osisId/:chapter" element={<ReaderPage />} />
          </Routes>
        </AppShell>
      </AuthProvider>
    </BrowserRouter>
  );
}
