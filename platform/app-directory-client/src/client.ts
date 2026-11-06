/** Typed, bounded Directory observations. No observation is an authorization cache. */
import { MeAppsResponseSchema, MeContextSchema, AppEntrySchema, CurrentAppsResponseSchema } from './schemas';
import type { CurrentAppsResponse, MeAppsResponse, MeContext, AppEntry } from './schemas';

export type DirectoryErrorId = 'authentication_required' | 'access_denied' | 'discovery_unavailable' | 'request_cancelled';
export class AppDirectoryError extends Error {
  constructor(public readonly errorId:DirectoryErrorId, public readonly status?:number) {
    super(({authentication_required:'Please sign in again.',access_denied:'Your current account cannot access apps.',discovery_unavailable:'Apps could not be checked. Please retry.',request_cancelled:'Request cancelled.'})[errorId]);
    this.name='AppDirectoryError';
  }
}
export interface DirectoryRequestOptions { signal?:AbortSignal; token?:string|null; }
export interface AppDirectoryClientOptions {
  baseUrl:string;
  getToken?:()=>Promise<string|undefined|null>;
  /** Injection supports host fixtures without inventing authentication. */
  fetch?:typeof fetch;
  timeoutMs?:number;
}
export function createAppDirectoryClient(options:AppDirectoryClientOptions) {
  const base=options.baseUrl.replace(/\/$/,'');
  const transport=options.fetch??globalThis.fetch;
  const budget=Math.min(Math.max(options.timeoutMs??8000,1),8000);
  async function request<T>(path:string,schema:{parse:(data:unknown)=>T},input:DirectoryRequestOptions={}):Promise<T>{
    const controller=new AbortController();
    let timer:ReturnType<typeof setTimeout>|undefined;
    let cancel:()=>void=()=>{};
    const cancelled=new Promise<never>((_,reject)=>{
      cancel=()=>{controller.abort();reject(new AppDirectoryError('request_cancelled'));};
      input.signal?.addEventListener('abort',cancel,{once:true});
      if(input.signal?.aborted)cancel();
      timer=setTimeout(()=>{controller.abort();reject(new AppDirectoryError('discovery_unavailable'));},budget);
    });
    const execution=(async()=>{
      const token=Object.prototype.hasOwnProperty.call(input,'token')?input.token:await options.getToken?.();
      if(controller.signal.aborted)throw new AppDirectoryError(input.signal?.aborted?'request_cancelled':'discovery_unavailable');
      const headers:Record<string,string>={Accept:'application/json'};
      if(token)headers.Authorization=`Bearer ${token}`;
      const response=await transport(base+path,{headers,signal:controller.signal,cache:'no-store',redirect:'error'});
      if(!response.ok){
        // The English error/details are never exposed to callers or logged.
        const body:unknown=await response.json().catch(()=>null);
        const identifier=body&&typeof body==='object'&&'error_id' in body?body.error_id:null;
        throw new AppDirectoryError(response.status===401&&identifier==='authentication_required'?'authentication_required':response.status===403&&identifier==='access_denied'?'access_denied':'discovery_unavailable',response.status);
      }
      return schema.parse(await response.json());
    })();
    try{return await Promise.race([execution,cancelled]);}
    catch(error){if(error instanceof AppDirectoryError)throw error;throw new AppDirectoryError(input.signal?.aborted?'request_cancelled':'discovery_unavailable');}
    finally{clearTimeout(timer);input.signal?.removeEventListener('abort',cancel);}
  }
  return {
    getCurrentApps:(input?:DirectoryRequestOptions):Promise<CurrentAppsResponse>=>request('/api/v2/me/apps',CurrentAppsResponseSchema,input),
    getMyApps:(input?:DirectoryRequestOptions):Promise<MeAppsResponse>=>request('/api/me/apps',MeAppsResponseSchema,input),
    getMyContext:(input?:DirectoryRequestOptions):Promise<MeContext>=>request('/api/me/context',MeContextSchema,input),
    /** Retained source API; full-catalogue HTTP access was removed from public Directory. */
    getAllApps:(input?:DirectoryRequestOptions):Promise<AppEntry[]>=>request('/api/apps',AppEntrySchema.array(),input),
  };
}
export type AppDirectoryClient=ReturnType<typeof createAppDirectoryClient>;
