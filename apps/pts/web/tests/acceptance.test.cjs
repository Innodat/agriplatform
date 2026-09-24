const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
test('reader shell exists without embedding restricted catalogue',()=>{
 const html=fs.readFileSync('apps/pts/web/index.html','utf8');
 assert.match(html,/root/);
 assert.doesNotMatch(html,/SWA-001|library.json|library-data/);
});
