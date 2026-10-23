// Narrow internal adoption of new Auth managed paths; no existing-file adoption or arbitrary target.
import {createHash} from 'node:crypto';
import {readFileSync} from 'node:fs';
import {join} from 'node:path';
import {renderAuthPattern} from './auth-pattern.ts';
import {checkScaffold,installScaffold} from './scaffold-install.ts';
const hash=(value:string)=>createHash('sha256').update(value).digest('hex');
const spec={owner:'kdg_capture',pattern:'auth-lifecycle-v1-candidate',paths:['src/auth/lifecycle.ts','src/auth/use-lifecycle.ts','scripts/test-auth-lifecycle.mjs']};
export function kdgAuthFiles() {
 return Object.fromEntries(Object.entries(renderAuthPattern()).map(([path,file])=>[path.slice('web/'.length),file]));
}
export function checkKdgAuthPattern(root:string) {
 const output=join(root,'apps/kdg-capture/web');checkScaffold(output);
 const manifest=JSON.parse(readFileSync(join(output,'.generated-files.json'),'utf8'));
 if(manifest.identity.generator!=='builder-v1'||manifest.identity.template!==spec.pattern||manifest.identity.recipe!==hash(JSON.stringify(spec))||
   Object.keys(manifest.files).sort().join(',')!==[...spec.paths].sort().join(',')||
   Object.values(manifest.files).some(file=>(file as {classification:string}).classification!=='generated'))throw new Error('kdg_auth_manifest_invalid');
 for(const [path,file] of Object.entries(kdgAuthFiles())) {
  if(readFileSync(join(output,path),'utf8')!==file.content)throw new Error('kdg_auth_template_drift');
 }
 if(manifest.identity.source!==hash(JSON.stringify(kdgAuthFiles())))throw new Error('kdg_auth_manifest_invalid');
}
export function syncKdgAuthPattern(root:string) {
 const files=kdgAuthFiles();
 installScaffold(join(root,'apps/kdg-capture/web'),files,{generator:'builder-v1',template:spec.pattern,recipe:hash(JSON.stringify(spec)),source:hash(JSON.stringify(files))});
 checkKdgAuthPattern(root);
}
