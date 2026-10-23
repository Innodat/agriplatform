// Build-time source map only. Generated application code never imports this owner.
import {readFileSync} from 'node:fs';
import type {ServiceFile} from './service-renderer.ts';
export const authPatternPaths = ['web/src/auth/lifecycle.ts','web/src/auth/use-lifecycle.ts','web/scripts/test-auth-lifecycle.mjs'] as const;
export function renderAuthPattern(): Record<string,ServiceFile> {
 return Object.fromEntries(authPatternPaths.map(path=>[path,{classification:'generated',content:readFileSync(new URL(`../templates/application/${path}`,import.meta.url),'utf8')}]));
}
