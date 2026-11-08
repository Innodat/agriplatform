/** Constrain the existing auth owner's explicit refresh to the original session. */
type Original={id:string;token:string;refreshToken?:string;sessionId?:string;revocationToken?:string};
export type RefreshedCleanupIdentity={id:string;token:string;refreshToken:string};
type Owner={revoke:(token:string)=>Promise<void>;refresh:(refresh:string)=>Promise<RefreshedCleanupIdentity>;claims:(token:string)=>Promise<{sub?:unknown;session_id?:unknown}>;retain:(original:Original,refreshed:RefreshedCleanupIdentity)=>Promise<void>};
export async function revokeOriginalSession(identity:Original,owner:Owner){
 try{await owner.revoke(identity.revocationToken||identity.token);return;}
 catch(error){if(![401,403].includes((error as {status:number}).status)||!identity.refreshToken)throw error;}
 const refreshed=await owner.refresh(identity.refreshToken!);
 if(refreshed.id!==identity.id)throw new Error('cleanup_session_mismatch');
 if(identity.sessionId){
  const verified=await owner.claims(refreshed.token);
  if(verified.sub!==identity.id||verified.session_id!==identity.sessionId)throw new Error('cleanup_session_mismatch');
 }
 await owner.retain(identity,refreshed);
 await owner.revoke(refreshed.token);
}
