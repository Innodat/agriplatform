const assert=require('node:assert/strict');
const path=require('node:path');
const {safeDiagnostic,safeCall}=require('./studies-owner-reporter.cjs');
const source=path.join(__dirname,'studies-owner.integration.cjs');
const secret='private-synthetic-token';
const signed='https://provider.invalid/verify?token='+secret;
const error=new Error(signed);
error.stack=`Error: ${source}:999:999 ${signed}\n    at callback (${signed}:3:4)\n    at scenario (${source}:125:87)\n    at other (${source}:140:2)`;
assert.deepEqual(safeDiagnostic(error),{event:'browser-source-failure',name:'Error',source:'studies-owner.integration.cjs',line:125,column:87});
error.name=signed;
error.stack=`Error: ${source}:999:999\n    at callback (${signed}:3:4)`;
assert.deepEqual(safeDiagnostic(error),{event:'browser-source-failure',name:'Error'});
error.stack=`Error: ${signed}\n    at scenario (${source}?token=${secret}:125:87)`;
assert.deepEqual(safeDiagnostic(error),{event:'browser-source-failure',name:'Error'});
(async()=>{
 const write=process.stdout.write;let output='';
 try{
  process.stdout.write=chunk=>{output+=chunk;return true;};
  await assert.rejects(()=>safeCall(async()=>{throw new TypeError(signed);}),failure=>{
   assert.equal(failure.message,'Owner integration browser case failed; inspect safe stage and source references.');
   return true;
  });
 }finally{process.stdout.write=write;}
 const diagnostic=JSON.parse(output);
 assert.equal(diagnostic.event,'browser-source-failure');assert.equal(diagnostic.name,'TypeError');
 assert.equal(diagnostic.source,'studies-owner-reporter.oracle.cjs');
 assert.equal(diagnostic.line,19);assert.ok(diagnostic.column>0);
 assert.ok(!output.includes(secret));assert.ok(!output.includes('https://'));assert.ok(!output.includes('?'));
 const Reporter=require('./studies-owner-reporter.cjs'),reporter=new Reporter();let forwarded='';
 try{
  process.stdout.write=chunk=>{forwarded+=chunk;return true;};
  reporter.onStdOut(signed+'\n');
  reporter.onStdOut(JSON.stringify({...diagnostic,message:signed})+'\n');
  reporter.onStdOut(JSON.stringify({...diagnostic,source:signed})+'\n');
  reporter.onStdOut('x'.repeat(2048));reporter.onStdOut('\n');
  const valid=JSON.stringify(diagnostic)+'\n';reporter.onStdOut(valid.slice(0,20));reporter.onStdOut(valid.slice(20));
 }finally{process.stdout.write=write;}
 assert.deepEqual(forwarded,JSON.stringify(diagnostic)+'\n');
 assert.ok(!forwarded.includes(secret));
 process.stdout.write('safe-source-oracle-passed\n');
})().catch(()=>{process.stderr.write('safe-source-oracle-failed\n');process.exitCode=1;});
