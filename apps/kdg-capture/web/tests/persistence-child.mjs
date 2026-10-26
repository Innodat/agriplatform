// Local proof process ownership only; errors are safe identifiers, never payloads.
export function watchChild(child) {
 const state={exited:false,code:null,signal:null,spawn_error:false};
 const exit=new Promise(resolve=>{
  child.once('error',()=>{state.spawn_error=true;state.exited=true;resolve();});
  child.once('exit',(code,signal)=>{state.exited=true;state.code=code;state.signal=signal;resolve();});
 });
 return {state,exit};
}
export async function readyChild(child,owner,timeoutMs=10000) {
 let raw='',timer,onData;
 const line=new Promise((resolve,reject)=>{
  onData=bytes=>{raw+=bytes;if(raw.includes('\n')){try{resolve(JSON.parse(raw.split('\n')[0]));}catch{reject(Error('fixture_ready_invalid'));}}};
  child.stdout.on('data',onData);
  timer=setTimeout(()=>reject(Error('fixture_start_timeout')),timeoutMs);
 });
 try{return await Promise.race([line,owner.exit.then(()=>{throw Error(owner.state.spawn_error?'fixture_spawn_error':'fixture_early_exit');})]);}
 finally{clearTimeout(timer);child.stdout.removeListener('data',onData);}
}
async function bounded(work,ms) {
 let timer;
 try{return await Promise.race([work,new Promise((_,reject)=>{timer=setTimeout(()=>reject(Error('fixture_stop_timeout')),ms);})]);}
 finally{clearTimeout(timer);}
}
export async function stopChild(child,owner,origin,{request=fetch,timeoutMs=10000,fallbackMs=1000}={}) {
 const result={forced_stop:false,stop_signal:null,shutdown_failed:false};
 if(owner.state.exited)return result;
 const controller=new AbortController();
 try {
  await bounded((async()=>{
   if(!origin)throw Error('fixture_origin_missing');
   const response=await request(origin+'/__fixture/stop',{signal:controller.signal});
   if(!response.ok)throw Error('fixture_stop_refused');
   await owner.exit;
  })(),timeoutMs);
 }catch {
  result.shutdown_failed=true;
  for(const signal of ['SIGTERM','SIGKILL']){
   if(owner.state.exited)break;
   result.forced_stop=true;result.stop_signal=signal;
   try{child.kill(signal);}catch{}
   try{await bounded(owner.exit,fallbackMs);}catch{}
  }
 }finally{controller.abort();}
 return result;
}
