const {defineConfig}=require('@playwright/test');
const original=require('./playwright.config.cjs');
module.exports=defineConfig({...original,grep:/bounded rollout/,outputDir:'/tmp/scribeswell-bounded-browser-results',
 use:{...original.use,baseURL:'http://127.0.0.1:5197'},
 webServer:{...original.webServer,command:'npm run dev -- --host 127.0.0.1 --port 5197 --strictPort',url:'http://127.0.0.1:5197',
  env:{...original.webServer.env,VITE_STUDIES_PREGRANTED:'true',VITE_STUDIES_API_URL:'https://bounded-api.example.invalid/scribeswell'}},
 projects:original.projects.map(project=>({...project,metadata:{boundedStudies:true}}))});
