import { createRequire } from 'node:module';
import { spawnSync } from 'node:child_process';
import { readFileSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import assert from 'node:assert/strict';
const require = createRequire(import.meta.url);
const manifest = JSON.parse(readFileSync(new URL('../package.json', import.meta.url)));
assert.equal(process.version, 'v26.11.1');
function packagePath(name) {
  for (const search of require.resolve.paths(name) ?? []) {
    const candidate = resolve(search, name, 'package.json');
    try { if (JSON.parse(readFileSync(candidate)).name === name) return candidate; } catch {}
  }
  throw new Error(`Installed package not found: ${name}`);
}
for (const [name, version] of Object.entries({ ...manifest.dependencies, ...manifest.devDependencies })) {
  assert.equal(JSON.parse(readFileSync(packagePath(name))).version, version, name);
}
for (const [name, bin, args, expected] of [
  ['typescript', 'tsc', ['--version'], '7.0.2'],
  ['vite', 'vite', ['--version'], '8.3.4'],
  ['vitest', 'vitest', ['--version'], '5.0.4'],
  ['tsx', 'tsx', ['--version'], '4.23.15'],
  ['npm', 'npm', ['--version'], '12.2.0'],
  ['shadcn', 'shadcn', ['--version'], '4.21.4'],
  ['@playwright/test', 'playwright', ['--version'], '1.64.0'],
]) {
  const path = packagePath(name);
  const info = JSON.parse(readFileSync(path));
  const entry = typeof info.bin === 'string' ? info.bin : info.bin[bin];
  const result = spawnSync(process.execPath, [resolve(dirname(path), entry), ...args], { encoding: 'utf8', timeout: 30000 });
  assert.ifError(result.error);
  assert.equal(result.status, 0, result.stderr);
  assert.ok((result.stdout + result.stderr).includes(expected), `${name}: ${result.stdout}${result.stderr}`);
  console.log(`${name}: ${expected}`);
}
// Supabase npm postinstall downloads a binary. Lifecycle execution is disabled;
// qualify the matching already integrity-qualified publisher binary explicitly.
const supabase = process.env.ENV_SUPABASE_BINARY;
assert.ok(supabase, 'ENV_SUPABASE_BINARY must select qualified 2.120.0');
const result = spawnSync(supabase, ['--version'], { encoding: 'utf8', timeout: 30000 });
assert.ifError(result.error);
assert.equal(result.status, 0, result.stderr);
assert.equal(result.stdout.trim(), '2.120.0');
console.log('supabase: 2.120.0 (qualified binary; npm wrapper install scripts disabled)');
