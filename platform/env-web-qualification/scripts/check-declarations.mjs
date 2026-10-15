import { writeFileSync } from 'node:fs';
import { createRequire } from 'node:module';
import { spawnSync } from 'node:child_process';
import assert from 'node:assert/strict';
import { dirname, resolve } from 'node:path';
const require = createRequire(import.meta.url);
// Keep the exact upstream conflict visible; skipLibCheck is limited to declarations
// in the normal strict source check, never a claim of clean upstream declarations.
const result = spawnSync(process.execPath, [resolve(dirname(require.resolve('typescript/package.json')), 'bin/tsc'), '--noEmit', '--skipLibCheck', 'false', '--pretty', 'false'], { encoding: 'utf8', timeout: 30000 });
assert.ifError(result.error);
writeFileSync('declaration-diagnostics.log', result.stdout + result.stderr);
assert.equal(result.status, 1, result.stdout + result.stderr);
assert.equal((result.stdout.match(/error TS\d+:/g) ?? []).length, 1, result.stdout);
assert.match(result.stdout, /@supabase\/auth-js\/dist\/module\/lib\/webauthn\.dom\.d\.ts\(501,18\): error TS2430:/);
assert.match(result.stdout, /PublicKeyCredentialFuture/);
assert.match(result.stdout, /ArrayBuffer.*undefined/);
assert.match(result.stdout, /string.*undefined/);
console.log('Known upstream TS2430: auth-js2.117.3 WebAuthn toJSON largeBlob ArrayBuffer conflicts with TS7 DOM JSON string; declaration-only exclusion recorded');
