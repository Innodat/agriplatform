import { readFileSync, writeFileSync } from 'node:fs';
import { jsonSchema } from './recipe.ts';
const target = new URL('../schema/scaffold-v1.json', import.meta.url);
const expected = `${JSON.stringify(jsonSchema(), null, 2)}\n`;
const args = process.argv.slice(2);
if (args.length === 0) writeFileSync(target, expected);
else if (args.length === 1 && args[0] === '--check') {
  try {
    if (readFileSync(target, 'utf8') !== expected) throw new Error();
    console.log('schema_current');
  } catch { console.error('schema_drift'); process.exitCode = 1; }
} else { console.error('arguments_invalid'); process.exitCode = 1; }
