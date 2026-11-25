// Owner seed: ordinary SDK transport; cancellation belongs to the managed Auth execution.
// Buffer the bounded response before exposing it to the SDK, so late body completion
// cannot mutate SDK session storage after the owning execution has been cancelled.
export async function fetchProviderResponse(request:typeof fetch,input:RequestInfo|URL,init:RequestInit|undefined,signal:AbortSignal):Promise<Response>{
 const failure=()=>new Error('provider_request_unavailable');
 if(signal.aborted||init?.signal?.aborted)throw failure();
 const controller=new AbortController();let cancel!:(reason:Error)=>void;
 const stopped=new Promise<never>((_resolve,reject)=>{cancel=reject;});
 const abort=()=>{controller.abort();cancel(failure());};signal.addEventListener('abort',abort,{once:true});init?.signal?.addEventListener('abort',abort,{once:true});
 const execution=(async()=>{
  try{
   const response=await request(input,{...init,signal:controller.signal});
   if(controller.signal.aborted){void response.body?.cancel().catch(()=>{});throw failure();}
   if(response.headers.get('content-length')&&Number(response.headers.get('content-length'))>65536)throw failure();
   const reader=response.body?.getReader();if(!reader)return response;
   const chunks:Uint8Array[]=[];let size=0;
   try{while(true){const chunk=await reader.read();if(chunk.done)break;if(controller.signal.aborted)throw failure();size+=chunk.value.byteLength;if(size>65536)throw failure();chunks.push(chunk.value);}}
   finally{void reader.cancel().catch(()=>{});}
   if(controller.signal.aborted)throw failure();
   const bytes=new Uint8Array(size);let offset=0;for(const chunk of chunks){bytes.set(chunk,offset);offset+=chunk.byteLength;}
   return new Response(bytes,{status:response.status,statusText:response.statusText,headers:response.headers});
  }catch{throw failure();}
 })();
 try{return await Promise.race([execution,stopped]);}
 finally{signal.removeEventListener('abort',abort);init?.signal?.removeEventListener('abort',abort);controller.abort();}
}
