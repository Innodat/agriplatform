import path from "path";
import { defineConfig } from "vite";
import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: {
      "@platform/ui-business": path.resolve(__dirname, "../../../platform/ui-business/src/index.ts"),
      "@": path.resolve(__dirname, "./src"),
      "@platform/app-directory-client": path.resolve(
        __dirname,
        "../../../platform/app-directory-client/src/index.ts"
      ),
    },
  },
  server: {
    port: 5174,
    fs: {allow: [__dirname, path.resolve(__dirname, "../../../platform"), path.resolve(__dirname, "../../../node_modules/@fontsource/noto-serif-hebrew")]},
    proxy: {
      // Proxy API calls to FastAPI backend during development
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },
});
