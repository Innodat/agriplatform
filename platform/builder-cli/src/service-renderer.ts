import { readFileSync } from 'node:fs';
import { validateRecipe, recipeSchema } from './recipe.ts';

export type ServiceFile = { classification: 'seed' | 'generated'; content: string };
const templates = [
  ['main.py', 'seed'], ['safe_errors.py', 'generated'], ['pyproject.toml', 'generated'],
  ['tests/test_runtime.py', 'generated'], ['README.md', 'generated'], ['AGENTS.md', 'generated'],
] as const;
// Internal candidate renderer only. Literal substitution, no template execution or writes.
export function renderService(input: unknown, root: string): Record<string, ServiceFile> {
  if (!validateRecipe(input, root)) throw new Error('service_bootstrap_unsupported');
  const recipe = recipeSchema.parse(input);
  if (recipe.owner_kind !== 'service' || recipe.extensions.length !== 0) throw new Error('service_bootstrap_unsupported');
  return renderHttpFiles(recipe.owner_id);
}

// Shared HTTP templates only; candidate callers validate their own complete recipes.
export function renderHttpFiles(owner: string): Record<string, ServiceFile> {
  return Object.fromEntries(templates.map(([path, classification]) => [path, {
    classification,
    content: readFileSync(new URL(`../templates/service/${path}`, import.meta.url), 'utf8')
      .replaceAll('{{OWNER}}', owner)
      .replaceAll('{{PACKAGE_NAME}}', owner.replaceAll('_', '-').replace(/-+$/u, '')),
  }]));
}
