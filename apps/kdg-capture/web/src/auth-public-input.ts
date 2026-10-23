/** Public URL/key validation without SDK construction or storage access. */
export function validateKdgEmailAuthConfig({url,publicKey}:Readonly<{url:string;publicKey:string}>):void {
 try{
  const parsed=new URL(url);
  if(parsed.username||parsed.password||parsed.pathname!=='/'||parsed.search||parsed.hash||!(parsed.protocol==='https:'||(parsed.protocol==='http:'&&['localhost','127.0.0.1','[::1]'].includes(parsed.hostname))))throw new Error();
  let publicOnly=/^sb_publishable_[A-Za-z0-9_-]{10,}$/.test(publicKey);
  if(!publicOnly){const parts=publicKey.split('.');publicOnly=parts.length===3&&JSON.parse(atob(parts[1].replace(/-/g,'+').replace(/_/g,'/'))).role==='anon';}
  if(!publicOnly)throw new Error();
 }catch{throw new Error('auth_configuration_invalid');}
}
