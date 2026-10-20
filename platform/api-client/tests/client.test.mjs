import assert from 'node:assert/strict';
import {test} from 'node:test';
import {mkdtempSync,readFileSync,writeFileSync,mkdirSync,symlinkSync,rmSync,readdirSync,readlinkSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {generateClient} from '../src/generate.mjs';
import {compatibilityResolution,qualifyTool} from '../src/tooling.mjs';
import {pathToFileURL} from 'node:url';
const schema={openapi:'3.1.0',info:{title:'owner',version:'1'},servers:[{url:'/api'}],paths:{'/health':{get:{operationId:'health',responses:{200:{description:'ok',content:{'application/json':{schema:{$ref:'#/components/schemas/Health'}}}}}}}},components:{schemas:{Health:{type:'object',properties:{status:{type:'string'}},required:['status']}}}};
function fixture(){const root=mkdtempSync(join(tmpdir(),'api-client-test-'));const input=join(root,'openapi.json');writeFileSync(input,JSON.stringify(schema));return {root,schema:input,output:join(root,'generated')};}
test('actual pinned CLI produces deterministic types; check detects drift without writes and regeneration preserves owner code',()=>{
 const f=fixture();generateClient(f);generateClient({...f,check:true});
 const before=readFileSync(join(f.output,'types.gen.ts'),'utf8');assert.match(before,/export type Health/);
 const owner=join(f.root,'client.ts');writeFileSync(owner,'owner custom');
 const edited=structuredClone(schema);edited.components.schemas.Health.properties.optional_note={type:'string'};writeFileSync(f.schema,JSON.stringify(edited));
 assert.throws(()=>generateClient({...f,check:true}),{message:'api_client_stale'});assert.equal(readFileSync(join(f.output,'types.gen.ts'),'utf8'),before);
 generateClient(f);generateClient({...f,check:true});assert.match(readFileSync(join(f.output,'types.gen.ts'),'utf8'),/optional_note\?/);assert.equal(readFileSync(owner,'utf8'),'owner custom');
 writeFileSync(join(f.output,'types.gen.ts'),'TAMPERED');assert.throws(()=>generateClient(f),{message:'scaffold_conflict'});assert.equal(readFileSync(join(f.output,'types.gen.ts'),'utf8'),'TAMPERED');
});
test('invalid schema and external refs refuse without modifying existing output',()=>{
 const f=fixture();generateClient(f);const before=readFileSync(join(f.output,'types.gen.ts'),'utf8');
 for(const invalid of [{...schema,components:{schemas:{Remote:{$ref:'https://secret.example/private'}}}}, {...schema,paths:{'/health':{$ref:'other.json'}}}, {openapi:'3.1.0'}, 'SECRET']) {
  writeFileSync(f.schema,JSON.stringify(invalid));assert.throws(()=>generateClient(f),{message:'api_client_schema_invalid'});assert.equal(readFileSync(join(f.output,'types.gen.ts'),'utf8'),before);
 }
 writeFileSync(f.schema,JSON.stringify(schema));const link=join(f.root,'linked.json');symlinkSync(f.schema,link);assert.throws(()=>generateClient({...f,schema:link}),{message:'api_client_input_invalid'});
});
test('missing output check and incomplete state refuse without installing or recovering',()=>{
 const f=fixture();assert.throws(()=>generateClient({...f,check:true}),{message:'api_client_stale'});generateClient(f);
 mkdirSync(join(f.output,'.scaffold-install-state'));assert.throws(()=>generateClient(f),{message:'scaffold_recovery_required'});
});

test('compatibility compiler is restricted to the qualified upstream child; invalid owner compiler refuses',()=>{
 const qualified=qualifyTool();
 assert.equal(compatibilityResolution('typescript',pathToFileURL(join(qualified.toolRoot,'dist/init.mjs')).href,qualified),qualified.compilerURL);
 assert.equal(compatibilityResolution('typescript',pathToFileURL(join(qualified.toolRoot+'-foreign','init.mjs')).href,qualified),null);
 assert.equal(compatibilityResolution('typescript',pathToFileURL('/tmp/application/src.ts').href,qualified),null);
 assert.equal(compatibilityResolution('other',pathToFileURL(join(qualified.toolRoot,'dist/init.mjs')).href,qualified),null);
 const f=fixture();writeFileSync(join(f.root,'package.json'),'{}');
 assert.throws(()=>qualifyTool(pathToFileURL(join(f.root,'package.json'))),{message:'api_client_tool_invalid'});
});

function outputSnapshot(directory){return Object.fromEntries(readdirSync(directory).sort().map(name=>[name,readFileSync(join(directory,name))]));}
test('output symlink refuses both modes and preserves linked owner bytes',()=>{
 const f=fixture(),target=join(f.root,'linked-output');mkdirSync(target);
 writeFileSync(join(target,'sentinel.txt'),'SENSITIVE linked owner bytes');
 symlinkSync(target,f.output);const before=outputSnapshot(target);
 for(const check of [false,true]) {
  assert.throws(()=>generateClient({...f,check}),{message:'api_client_input_invalid'});
  assert.equal(readlinkSync(f.output),target);assert.deepEqual(outputSnapshot(target),before);
 }
});
test('missing manifest and edited generated index refuse without changing any target or sentinel bytes',()=>{
 for(const scenario of ['missing-manifest','edited-index']) {
  const f=fixture();generateClient(f);writeFileSync(join(f.output,'sentinel.txt'),'SENSITIVE owner bytes');
  if(scenario==='missing-manifest')rmSync(join(f.output,'.generated-files.json'));
  else writeFileSync(join(f.output,'index.ts'),'SENSITIVE edited generated index');
  const before=outputSnapshot(f.output),identifier=scenario==='missing-manifest'?'scaffold_manifest_invalid':'scaffold_conflict';
  for(const check of [false,true]) {
   assert.throws(()=>generateClient({...f,check}),{message:identifier});
   assert.deepEqual(outputSnapshot(f.output),before);
  }
 }
});
test('oversized and excessive-depth schemas refuse before touching installed output',()=>{
 const f=fixture();generateClient(f);writeFileSync(join(f.output,'sentinel.txt'),'SENSITIVE owner bytes');
 const before=outputSnapshot(f.output),deep=structuredClone(schema);let nested=deep;
 for(let depth=0;depth<101;depth++){nested['x-nested']={};nested=nested['x-nested'];}
 for(const invalid of [{...schema,'x-padding':'x'.repeat(8*1024*1024)},deep]) {
  const input=JSON.stringify(invalid);writeFileSync(f.schema,input);
  for(const check of [false,true]) {
   assert.throws(()=>generateClient({...f,check}),{message:'api_client_schema_invalid'});
   assert.deepEqual(outputSnapshot(f.output),before);assert.equal(readFileSync(f.schema,'utf8'),input);
  }
 }
});
