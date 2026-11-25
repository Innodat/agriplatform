import {fileURLToPath} from 'node:url';
import ownerConfig from '../../apps/leave/web/vite.config.ts';

export default async context => ({
  ...await ownerConfig(context),
  tsconfig: fileURLToPath(new URL('../../apps/leave/web/tsconfig.json', import.meta.url)),
});
