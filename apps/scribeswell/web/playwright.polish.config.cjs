const config=require('./playwright.config.cjs');
module.exports={...config,testMatch:'workspace-polish.spec.cjs',use:{...config.use,baseURL:'http://127.0.0.1:5186'},webServer:{command:'npm run preview -- --host 127.0.0.1 --port 5186 --strictPort',url:'http://127.0.0.1:5186',reuseExistingServer:false,env:{VITE_APP_BASE:'/',VITE_PLATFORM_ORIGIN:''}}};
