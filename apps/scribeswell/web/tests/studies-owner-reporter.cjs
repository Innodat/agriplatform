// Qualification diagnostics contain only source locations/status, never vendor
// errors, browser console payloads, locator details or signed callback URLs.
class SafeReporter {
 constructor(){this.stdoutLine='';this.discardLine=false;}
 onStdOut(chunk){
  // Worker output is untrusted. Forward only this closed sanitized event, and
  // retain at most one bounded line while accommodating split worker chunks.
  for(const part of String(chunk).split(/(?<=\n)/)){
   if(!this.discardLine){this.stdoutLine+=part;if(this.stdoutLine.length>1024){this.stdoutLine='';this.discardLine=true;}}
   if(!part.endsWith('\n'))continue;
   if(!this.discardLine){
    try{
     const value=JSON.parse(this.stdoutLine);
     const names=['Error','AssertionError','TimeoutError','TypeError','RangeError','ReferenceError','SyntaxError','AggregateError'];
     const sources=['studies-owner.integration.cjs','studies-owner-privacy.cjs','studies-owner-reporter.oracle.cjs'];
     const fields=Object.keys(value).sort().join(',');
     const location=fields==='column,event,line,name,source'&&sources.includes(value.source)&&
      [value.line,value.column].every(n=>Number.isInteger(n)&&n>0&&n<=9999999);
     if(value.event==='browser-source-failure'&&names.includes(value.name)&&(fields==='event,name'||location)){
      const safe={event:'browser-source-failure',name:value.name};
      if(location)Object.assign(safe,{source:value.source,line:value.line,column:value.column});
      process.stdout.write(JSON.stringify(safe)+'\n');
     }
    }catch{}
   }
   this.stdoutLine='';this.discardLine=false;
  }
 }
 onTestEnd(test,result){process.stdout.write(JSON.stringify({event:'browser-case',line:test.location.line,status:result.status,duration_ms:result.duration})+'\n');}
 onError(){process.stdout.write(JSON.stringify({event:'browser-global-failure'})+'\n');}
 onEnd(result){process.stdout.write(JSON.stringify({event:'browser-finished',status:result.status,duration_ms:result.duration})+'\n');}
}
function safeDiagnostic(error){
 const names=new Set(['Error','AssertionError','TimeoutError','TypeError','RangeError','ReferenceError','SyntaxError','AggregateError']);
 const diagnostic={event:'browser-source-failure',name:names.has(error?.name)?error.name:'Error'};
 // Never emit arbitrary filenames or any part of a message. Parse only bounded
 // stack frames pointing to these known local sources, after the message line.
 const sources=['studies-owner.integration.cjs','studies-owner-privacy.cjs','studies-owner-reporter.oracle.cjs'];
 if(typeof error?.stack!=='string')return diagnostic;
 for(const frame of error.stack.slice(0,65536).split('\n').slice(1,65)){
  if(!/^\s+at /.test(frame))continue;
  for(const source of sources){
   const prefix=require('path').join(__dirname,source)+':';
   const index=frame.lastIndexOf(prefix);if(index<0)continue;
   const position=frame.slice(index+prefix.length).match(/^([1-9]\d{0,6}):([1-9]\d{0,6})\)?$/);
   if(position)return {...diagnostic,source,line:Number(position[1]),column:Number(position[2])};
  }
 }
 return diagnostic;
}
async function safeCall(body){
 try{return await body();}catch(error){
  process.stdout.write(JSON.stringify(safeDiagnostic(error))+'\n');
  throw new Error('Owner integration browser case failed; inspect safe stage and source references.');
 }
}
function safeScenario(body){return async ({browser,page})=>safeCall(()=>body({browser,page}));}
module.exports=SafeReporter;
module.exports.safeScenario=safeScenario;

module.exports.safeCall=safeCall;

module.exports.safeDiagnostic=safeDiagnostic;
