import assert from 'node:assert/strict';
import {test} from 'node:test';
import {mkdtempSync,readFileSync,copyFileSync,rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {generateClient} from '../src/generate.mjs';

test('discovery fixture preserves bigint strings, nullable positions and mixed scope arrays through actual generation',()=>{
 const root=mkdtempSync(join(tmpdir(),'discovery-client-'));
 try {
  const schema=join(root,'openapi.json'),output=join(root,'generated');
  copyFileSync(new URL('./fixtures/discovery.openapi.json',import.meta.url),schema);
  generateClient({schema,output});generateClient({schema,output,check:true});
  const types=readFileSync(join(output,'types.gen.ts'),'utf8');
  assert.match(types,/membership_id: string/);assert.match(types,/next_cursor: string \| null/);
  assert.match(types,/eligible_scope_kinds: Array<'account' \| 'organization'>/);
  assert.match(types,/contexts: Array<Context>/);assert.match(types,/checked_at: string/);
 } finally {rmSync(root,{recursive:true,force:true});}
});
