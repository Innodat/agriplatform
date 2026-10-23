import { readFileSync } from 'node:fs';
import {renderAuthPattern} from './auth-pattern.ts';
import { validateRecipe, recipeSchema } from './recipe.ts';
import { renderHttpFiles, type ServiceFile } from './service-renderer.ts';
const templates = [
 ['README.md','generated'], ['AGENTS.md','generated'], ['web/index.html','generated'],
 ['web/package.json','generated'], ['web/tsconfig.json','generated'], ['web/vite.config.ts','generated'],
 ['web/src/App.tsx','seed'], ['web/src/api/health.ts','seed'], ['web/scripts/test-health.mjs','generated'], ['web/src/main.tsx','seed'], ['web/src/styles.css','seed'],
 ['web/scripts/browser-smoke.mjs','generated'], ['web/scripts/proof-support.mjs','generated'],
] as const;
// Internal, pure candidate renderer. No output target, template execution or bypass flag.
export function renderApplication(input: unknown, root: string): Record<string, ServiceFile> {
 if (!validateRecipe(input,root)) throw new Error('application_bootstrap_unsupported');
 const recipe=recipeSchema.parse(input);
 if(recipe.owner_kind!=='application'||recipe.extensions.length!==0) throw new Error('application_bootstrap_unsupported');
 const files: Record<string,ServiceFile>=Object.fromEntries(templates.map(([path,classification])=>[path,{
  classification,content:readFileSync(new URL(`../templates/application/${path}`,import.meta.url),'utf8').replaceAll('{{OWNER}}',recipe.owner_id),
 }]));
 Object.assign(files,renderAuthPattern());
 for(const [path,file] of Object.entries(renderHttpFiles(recipe.owner_id))) files[`api/${path}`]=file;
 return files;
}
