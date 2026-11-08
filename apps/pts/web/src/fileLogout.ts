/** Both cleanup owners get a bounded attempt, including after either partial order. */
export async function completeFileLogout<T>(identity:T,operations:{clear:(identity:T)=>Promise<{provider_session:'present'|'absent'}|undefined>;revoke:(identity:T)=>Promise<void>}){
 const attempts=await Promise.allSettled([operations.clear(identity),operations.revoke(identity)]);
 // A file-origin outage never prevents the independent provider-local attempt.
 // Recheck exact-session absence after that attempt; a generic401 is failure.
 let proof;
 try{proof=await operations.clear(identity);}
 catch{throw new Error('file_cleanup_incomplete');}
 // Exact original absence does not repair failed durable replacement custody.
 // Keep this one local recovery failure visible after both owners' attempts;
 // ordinary already-revoked/provider failures still use the absence proof below.
 const revoke=attempts[1];
 if(revoke.status==='rejected'&&revoke.reason?.code==='file_cleanup_replacement_unavailable')throw revoke.reason;
 if(proof?.provider_session==='absent')return;
 throw new Error('provider_cleanup_incomplete');
}
