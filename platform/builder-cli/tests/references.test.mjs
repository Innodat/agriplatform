import assert from 'node:assert/strict';
import { test } from 'node:test';
import { mkdtempSync, mkdirSync, writeFileSync, rmSync, symlinkSync, lstatSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { validateRecipe } from '../src/recipe.ts';

test('manifest permits absent and regular owner-local files; refuses symlinks, directories and blocked ancestors', () => {
  const root = mkdtempSync(join(tmpdir(), 'scaffold-manifest-'));
  const recipe = {
    schema_version: 1, owner_id: 'fixture_owner', owner_kind: 'service',
    sources: ['source.md'], contracts: ['contract.md'],
    patterns: ['api.owner-http.v1', 'auth.service-owner.v1', 'errors.safe-envelope.v1', 'saving.none.v1'],
    extensions: [], deployment_manifest: 'services/fixture-owner/deployment/manifest.json',
  };
  try {
    writeFileSync(join(root, 'source.md'), 'authority');
    writeFileSync(join(root, 'contract.md'), 'contract');
    assert.equal(validateRecipe(recipe, root), true);
    for (const path of ['services', 'services/fixture-owner', 'services/fixture-owner/deployment', recipe.deployment_manifest]) {
      assert.throws(() => lstatSync(join(root, path)), { code: 'ENOENT' });
    }
    const deployment = join(root, 'services/fixture-owner/deployment');
    mkdirSync(deployment, { recursive: true });
    const manifest = join(deployment, 'manifest.json');
    assert.equal(validateRecipe(recipe, root), true);
    assert.throws(() => lstatSync(manifest), { code: 'ENOENT' });
    writeFileSync(manifest, '{}');
    assert.equal(validateRecipe(recipe, root), true);
    rmSync(manifest);
    mkdirSync(manifest);
    assert.equal(validateRecipe(recipe, root), false);
    rmSync(manifest, { recursive: true });
    symlinkSync(join(root, 'source.md'), manifest);
    assert.equal(validateRecipe(recipe, root), false);
    rmSync(manifest);
    rmSync(deployment, { recursive: true });
    symlinkSync(root, deployment);
    assert.equal(validateRecipe(recipe, root), false);
    rmSync(deployment);
    writeFileSync(deployment, 'not a directory');
    assert.equal(validateRecipe(recipe, root), false);
  } finally { rmSync(root, { recursive: true, force: true }); }
});
