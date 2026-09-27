import path from "path";
import { defineConfig, loadEnv } from "vite";
import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react";

export default defineConfig(({mode}) => {
 const env=loadEnv(mode,process.env.RELEASE_ENV_DIR||__dirname,'VITE_');
 const base=env.VITE_APP_BASE||'/';
 const canonical=env.VITE_PLATFORM_ORIGIN?new URL(env.VITE_PLATFORM_ORIGIN):null;
 return {envDir:process.env.RELEASE_ENV_DIR||__dirname,
  base,
  plugins: [react(), tailwindcss(), {
    name:'canonical-reader-origin',
    configureServer(server){
      server.middlewares.use((req,res,next)=>{
        // Redirect browser documents from the standalone port, never API requests.
        // Gateway requests retain the canonical Host header.
        if(canonical&&req.headers.host!==canonical.host&&req.method==='GET'&&req.headers.accept?.includes('text/html')){
          const incoming=new URL(req.url||'/',canonical);
          const pathname=incoming.pathname===base.slice(0,-1)?base:incoming.pathname.startsWith(base)?incoming.pathname:base+incoming.pathname.replace(/^\//,'');
          res.writeHead(307,{Location:canonical.origin+pathname+incoming.search,'Cache-Control':'no-store'});res.end();return;
        }
        next();
      });
    },
  }],
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
      [base+"api"]: {
        target: env.VITE_API_BASE_URL||"http://localhost:8000",
        changeOrigin: true,
        rewrite: (url:string)=>base==='/'?url:url.slice(base.length-1),
      },
    },
  },
 };
});
