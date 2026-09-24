import {defineConfig} from 'vite';
import react from '@vitejs/plugin-react';
import path from 'node:path';
export default defineConfig({plugins:[react()],resolve:{alias:{'@platform/app-directory-client':path.resolve(__dirname,'../../../platform/app-directory-client/src/index.ts'),'@platform/ui-business':path.resolve(__dirname,'../../../platform/ui-business/src/index.ts')}},server:{port:5179,fs:{allow:[path.resolve(__dirname,'../../../platform'),__dirname]}}});
