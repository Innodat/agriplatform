// Qualification diagnostics contain only source locations/status, never vendor
// errors, browser console payloads, locator details or signed callback URLs.
class SafeReporter {
 onTestEnd(test,result){process.stdout.write(JSON.stringify({event:'browser-case',line:test.location.line,status:result.status,duration_ms:result.duration})+'\n');}
 onError(){process.stdout.write(JSON.stringify({event:'browser-global-failure'})+'\n');}
 onEnd(result){process.stdout.write(JSON.stringify({event:'browser-finished',status:result.status,duration_ms:result.duration})+'\n');}
}
async function safeCall(body){
 try{return await body();}catch{throw new Error('Owner integration browser case failed; inspect safe stage and source references.');}
}
function safeScenario(body){return async ({browser,page})=>safeCall(()=>body({browser,page}));}
module.exports=SafeReporter;
module.exports.safeScenario=safeScenario;

module.exports.safeCall=safeCall;
