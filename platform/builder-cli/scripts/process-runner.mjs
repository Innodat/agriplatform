// Private harness primitive; no public timeout or process-control interface.
import { spawnSync } from 'node:child_process';
export function runBounded(executable, args, {cwd, env, timeoutMs=120000}) {
 const result=spawnSync(executable,args,{cwd,env,encoding:'utf8',timeout:timeoutMs,
  killSignal:'SIGKILL',detached:true,maxBuffer:2*1024*1024});
 let groupTermination='not_required';
 if (result.error && result.pid) {
  try { process.kill(-result.pid,'SIGKILL'); groupTermination='signalled'; }
  catch (error) { groupTermination=error.code==='ESRCH'?'already_exited':'failed'; }
 }
 return {...result,groupTermination};
}
