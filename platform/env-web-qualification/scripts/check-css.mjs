import { readdirSync, readFileSync } from 'node:fs';
import assert from 'node:assert/strict';
const css = readdirSync('dist/assets').filter(x => x.endsWith('.css')).map(x => readFileSync(`dist/assets/${x}`, 'utf8')).join('');
assert.match(css, /\.p-4\s*\{/);
assert.doesNotMatch(css, /@import\s+["']tailwindcss/);
console.log('Native Tailwind CSS utility compiled');
