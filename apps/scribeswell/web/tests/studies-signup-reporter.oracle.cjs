const assert=require('node:assert/strict');
const path=require('node:path');
const Reporter=require('./studies-owner-reporter.cjs');
const source=path.join(__dirname,'studies-signup.integration.cjs');
const secret='http://localhost:55491/auth/v1/verify?token=private-synthetic-token';
const error=new Error(secret);error.stack=`Error: ${secret}\n    at callback (${source}:40:8)`;
const diagnostic={event:'browser-source-failure',name:'Error',source:'studies-signup.integration.cjs',line:40,column:8};
assert.deepEqual(Reporter.safeDiagnostic(error),diagnostic);
const reporter=new Reporter(),write=process.stdout.write;let output='';
try{
 process.stdout.write=chunk=>{output+=chunk;return true;};
 reporter.onStdOut(secret+'\n');reporter.onStdOut(JSON.stringify({...diagnostic,payload:secret})+'\n');
 reporter.onStdOut(JSON.stringify({...diagnostic,source:secret})+'\n');
 reporter.onStdOut(JSON.stringify(diagnostic)+'\n');
}finally{process.stdout.write=write;}
assert.equal(output,JSON.stringify(diagnostic)+'\n');assert.ok(!output.includes(secret));
process.stdout.write('signup-safe-source-oracle-passed\n');
