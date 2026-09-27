const {defineConfig}=require('@playwright/test');
const path=require('node:path');
const env={VITE_SUPABASE_URL:'https://pts-browser-test.supabase.co',VITE_SUPABASE_ANON_KEY:'test-public-key',VITE_APP_DIRECTORY_URL:'http://127.0.0.1:8001'};
module.exports=defineConfig({testDir:'tests',testMatch:'*.integration.cjs',use:{baseURL:'http://localhost:5183',headless:true},workers:1,webServer:[
 {command:'node tests/session-api-fixture.cjs',cwd:__dirname,url:'http://127.0.0.1:5185/health',reuseExistingServer:false},
 {command:'npm run dev -- --host localhost --port 5184',cwd:__dirname,url:'http://localhost:5184/scribeswell/',reuseExistingServer:false,env:{...env,VITE_API_BASE_URL:'http://127.0.0.1:5185',VITE_APP_BASE:'/scribeswell/',VITE_PLATFORM_ORIGIN:'http://localhost:5183'}},
 {command:'npm run dev -- --host localhost --port 5183',cwd:path.resolve(__dirname,'../../pts/web'),url:'http://localhost:5183',reuseExistingServer:false,env:{...env,VITE_PTS_API_URL:'http://127.0.0.1:8010',VITE_SCRIBESWELL_DEV_URL:'http://localhost:5184'}}
]});
