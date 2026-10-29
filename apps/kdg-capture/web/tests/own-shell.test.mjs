import test from 'node:test';
import assert from 'node:assert/strict';
import {ownShellBuild} from '../scripts/own-shell-build.mjs';
test('built shell emits a revisioned public allowlist without protected navigation',()=>{
 const files={
  'index.html':{type:'asset',source:'<html>public config</html>'},
  'assets/main-abc.js':{type:'chunk',code:'export const own=true'},
  'assets/main-def.css':{type:'asset',source:'body{}'},
 };
 const emitted=[];ownShellBuild().generateBundle.call({emitFile:item=>emitted.push(item)}, {}, files);
 const sw=emitted.find(item=>item.fileName==='sw.js');assert.ok(sw);
 assert.match(sw.source,/REVISION="[a-f0-9]{24}"/);
 assert.match(sw.source,/\/assets\/main-abc.js/);
 assert.ok(!sw.source.includes('skipWaiting(); // automatic'));
 assert.ok(!sw.source.includes('cache.delete')&&!sw.source.includes('caches.delete'));
 const manifest=JSON.parse(emitted.find(item=>item.fileName==='manifest.webmanifest').source);
 assert.equal(manifest.theme_color,'#171717','inherit the neutral shadcn primary');
 assert.equal(manifest.background_color,'#ffffff');
 assert.match(emitted.find(item=>item.fileName==='icon.svg').source,/<title>Observation document<\/title>/,'generic observation document icon');
});
