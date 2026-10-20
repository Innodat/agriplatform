import assert from 'node:assert/strict';
import { readFileSync, lstatSync } from 'node:fs';
import { test } from 'node:test';
import { jsonSchema, patternIds } from '../src/recipe.ts';
const root = new URL('../../../', import.meta.url);
test('exported schema matches authoritative Zod source', () => {
  assert.equal(readFileSync(new URL('../schema/scaffold-v1.json',import.meta.url),'utf8'),`${JSON.stringify(jsonSchema(),null,2)}\n`);
});
test('catalogue has exactly six candidates with actual contract/preflight test references',()=>{
 const catalogue=JSON.parse(readFileSync(new URL('../schema/patterns-v1.json',import.meta.url),'utf8'));
 assert.equal(catalogue.status,'candidate');assert.equal(catalogue.generation_ready,false);
 assert.deepEqual(catalogue.patterns.map(p=>p.id),[...patternIds]);
 for(const pattern of catalogue.patterns){
  assert.equal(pattern.status,'candidate');assert.equal(pattern.template_version,'1-candidate');
  assert.ok(pattern.contracts.length>0 && pattern.tests.length>0);
  for(const ref of [...pattern.contracts,...pattern.tests]) assert.ok(lstatSync(new URL(ref,root)).isFile());
 }
});
