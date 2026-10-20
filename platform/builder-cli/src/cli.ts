import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { resolve } from 'node:path';
import { validateRecipe } from './recipe.ts';
const root = fileURLToPath(new URL('../../../', import.meta.url));
function fail(error: string): never {
  console.log(JSON.stringify({error}));
  process.exit(1);
}
const args = process.argv.slice(2);
if (args.length !== 2 || args[0] !== '--config' || !args[1] || args[1].startsWith('--')) fail('arguments_invalid');
let input: unknown;
// npm changes cwd to the workspace; INIT_CWD retains the command's caller.
// Direct Node execution keeps its own cwd even when launched by another npm script.
const configRoot = process.env.npm_lifecycle_event === 'validate:recipe' &&
  process.env.npm_package_name === '@platform/builder-cli' && process.env.INIT_CWD
  ? process.env.INIT_CWD : process.cwd();
try { input = JSON.parse(readFileSync(resolve(configRoot, args[1]), 'utf8')); }
catch { fail('config_unreadable'); }
try { if (!validateRecipe(input, root)) fail('recipe_invalid'); }
catch { fail('recipe_invalid'); }
console.log(JSON.stringify({recipe_valid:true, generation_ready:false}));
