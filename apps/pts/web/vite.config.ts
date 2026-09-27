import {defineConfig,loadEnv} from 'vite';
import react from '@vitejs/plugin-react';
import path from 'node:path';
export default defineConfig(({mode})=>{
 const env=loadEnv(mode,process.env.RELEASE_ENV_DIR||__dirname,'VITE_');
 return {envDir:process.env.RELEASE_ENV_DIR||__dirname,plugins:[react()],resolve:{alias:{'@platform/app-directory-client':path.resolve(__dirname,'../../../platform/app-directory-client/src/index.ts'),'@platform/ui-business':path.resolve(__dirname,'../../../platform/ui-business/src/index.ts')}},server:{port:5179,fs:{allow:[path.resolve(__dirname,'../../../platform'),__dirname]},proxy:{'/scribeswell':{target:env.VITE_SCRIBESWELL_DEV_URL||'http://localhost:5174',ws:true,changeOrigin:false}}}};
});
