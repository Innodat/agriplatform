import { z } from 'zod';
import { lstatSync } from 'node:fs';
import { join } from 'node:path';

export const patternIds = [
  'api.owner-http.v1', 'web.react-shell.v1',
  'auth.organization-account.fixed.v1', 'auth.service-owner.v1',
  'errors.safe-envelope.v1', 'saving.none.v1',
] as const;
const text = z.string().min(1).max(512);
// Portable, normalized paths only. Never normalize away an unsafe input.
const path = text.refine(value => !value.includes('\\') && !value.includes(':') &&
  !value.includes('\0') && value.split('/').every(part => part !== '' && part !== '.' && part !== '..'));
const unique = (values: string[]) => new Set(values).size === values.length;
const refs = z.array(path).min(1).max(100).refine(unique);
const overlaps = (a: string, b: string) => a === b || a.startsWith(`${b}/`) || b.startsWith(`${a}/`);
export const recipeSchema = z.strictObject({
  schema_version: z.literal(1),
  owner_id: z.string().regex(/^[a-z][a-z0-9_]{1,63}$/),
  owner_kind: z.enum(['application', 'service']),
  sources: refs,
  contracts: refs,
  patterns: z.array(z.enum(patternIds)).min(1).max(100).refine(unique),
  extensions: z.array(z.strictObject({source: path, destination: path})).max(100),
  deployment_manifest: path,
}).superRefine((recipe, ctx) => {
  const fail = () => ctx.addIssue({code:'custom', message:'recipe_invalid'});
  if (!unique([...recipe.sources, ...recipe.contracts])) fail();
  const required = ['api.owner-http.v1', 'errors.safe-envelope.v1', 'saving.none.v1',
    ...(recipe.owner_kind === 'application'
      ? ['web.react-shell.v1', 'auth.organization-account.fixed.v1']
      : ['auth.service-owner.v1'])];
  if (recipe.patterns.length !== required.length || required.some(id => !recipe.patterns.some(p => p === id))) fail();
  const ownerPaths = [recipe.owner_id, recipe.owner_id.replaceAll('_', '-')];
  const ownerRoot = recipe.owner_kind === 'application' ? 'apps' : 'services';
  if (!ownerPaths.some(owner => recipe.deployment_manifest.startsWith(`${ownerRoot}/${owner}/deployment/`))) fail();
  for (let i=0; i<recipe.extensions.length; i++) {
    for (const previous of recipe.extensions.slice(0, i)) {
      const current = recipe.extensions[i]!;
      if (overlaps(previous.source,current.source) || overlaps(previous.destination,current.destination)) fail();
    }
  }
});
export type Recipe = z.infer<typeof recipeSchema>;

// Inspect every existing component, including ancestors of an absent first manifest.
// Authority documents are stat'ed only; their content is never loaded.
function safeReference(root: string, reference: string, kind: 'file' | 'directory', allowAbsent=false): boolean {
  let current = root;
  const parts = reference.split('/');
  for (let i=0; i<parts.length; i++) {
    current = join(current, parts[i]!);
    try {
      const stat = lstatSync(current);
      if (stat.isSymbolicLink()) return false;
      if (i < parts.length-1 ? !stat.isDirectory() : kind === 'file' ? !stat.isFile() : !stat.isDirectory()) return false;
    } catch (error) {
      return allowAbsent && (error as NodeJS.ErrnoException).code === 'ENOENT';
    }
  }
  return true;
}
export function validateRecipe(input: unknown, root: string): boolean {
  const result = recipeSchema.safeParse(input);
  if (!result.success) return false;
  const recipe = result.data;
  return [...recipe.sources,...recipe.contracts].every(ref => safeReference(root,ref,'file')) &&
    recipe.extensions.every(ext => safeReference(root,ext.source,'directory')) &&
    safeReference(root,recipe.deployment_manifest,'file',true);
}
export function jsonSchema() {
  return {...z.toJSONSchema(recipeSchema, {target:'draft-2020-12'}),
    $id:'https://agriplatform.local/schema/scaffold-v1.json',
    title:'Scaffold recipe v1 (read-only candidate preflight)',
    description:'Zod refinements enforce pattern composition, distinct references, owner manifest scope and extension overlap; filesystem preflight additionally verifies paths. Validity never proves generation readiness.'};
}
