/** Native file transport only: the owning application's auth client owns refresh/logout. */
export type NativeFileIdentity={token:string};
export type NativeFilePresentation='open'|'download';
export type NativeFileBinding={account_id:string;session_id:string};
export type NativeFileCleanup=NativeFileBinding&{status:'cleared';provider_session:'present'|'absent'};
type Options={fileOrigin:string;frontendOrigin:string;fetch?:typeof fetch};

export function createNativeFileClient(options:Options){
 const request=options.fetch||globalThis.fetch;
 function endpoint(path:string){
  const file=new URL(options.fileOrigin),web=new URL(options.frontendOrigin);
  if(file.protocol!=='https:'||web.protocol!=='https:'||file.origin!==options.fileOrigin||web.origin!==options.frontendOrigin||!file.hostname.endsWith('.'+web.hostname)||file.port!==web.port)throw Object.assign(new Error('file_origin_unavailable'),{code:'file_origin_unavailable'});
  return options.fileOrigin+path;
 }
 async function post(path:string,identity:NativeFileIdentity){
  const response=await request(endpoint(path),{method:'POST',credentials:'include',headers:{Authorization:'Bearer '+identity.token},cache:'no-store',signal:AbortSignal.timeout(10000)});
  if(!response.ok)throw Object.assign(new Error('file_request_failed'),{code:'file_request_failed',status:response.status});
  return response;
 }
 return {
  async prepare(identity:NativeFileIdentity){
   const response=await post('/api/file-session/prepare',identity);const result=await response.json();
   if(result.status!=='prepared'||!validUUID(result.account_id)||!validUUID(result.session_id))throw new Error('file_cleanup_unavailable');
   return result as NativeFileBinding&{status:'prepared'};
  },
  async establish(identity:NativeFileIdentity){await post('/api/file-session',identity);},
  async clear(identity:NativeFileIdentity):Promise<NativeFileCleanup|undefined>{
   if(!options.fileOrigin)return;
   const response=await post('/api/file-session/clear',identity);const result=await response.json();
   if(result.status!=='cleared'||!validUUID(result.account_id)||!validUUID(result.session_id)||!['present','absent'].includes(result.provider_session))throw new Error('file_cleanup_unavailable');
   return result;
  },
  async context(reference:string,presentation:NativeFilePresentation,identity:NativeFileIdentity){
   if(!['open','download'].includes(presentation))throw new Error('file_context_unavailable');
   const response=await post('/api/file-contexts/'+encodeURIComponent(reference)+'?presentation='+presentation,identity);
   const result=await response.json();const url=new URL(result.url);
   if(url.origin!==options.fileOrigin||!/^\/api\/files\/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/.test(url.pathname)||url.search||url.hash)throw Object.assign(new Error('file_context_unavailable'),{code:'file_context_unavailable'});
   return url.href;
  },
 };
}
function validUUID(value:unknown):value is string{return typeof value==='string'&&/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/.test(value)&&value!=='00000000-0000-0000-0000-000000000000';}
