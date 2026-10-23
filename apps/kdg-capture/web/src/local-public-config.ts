import {validateKdgEmailAuthConfig} from './auth-public-input.js';
export type KdgLocalPublicConfig=Readonly<{org:string;url:string;publicKey:string}>;
const loopback=(url:URL)=>['http:','https:'].includes(url.protocol)&&['localhost','127.0.0.1','[::1]'].includes(url.hostname);
/** Deliberately local/CI only. No URL, environment or browser-store fallbacks. */
export function parseKdgLocalPublicConfig(input:unknown,pageOrigin:string):KdgLocalPublicConfig|null{
 try{
  const page=new URL(pageOrigin);if(!loopback(page)||page.origin!==pageOrigin)return null;
  if(!input||typeof input!=='object'||Array.isArray(input))return null;
  const value=input as Record<string,unknown>;
  if(Object.keys(value).sort().join(',')!==['schema_version','environment_kind','org_id','auth_url','auth_public_key'].sort().join(','))return null;
  if(value.schema_version!==1||(typeof value.environment_kind!=='string'||!['local_disposable','ci_disposable'].includes(value.environment_kind)))return null;
  if(typeof value.org_id!=='string'||value.org_id.trim()!==value.org_id||!/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/.test(value.org_id)||value.org_id==='00000000-0000-0000-0000-000000000000')return null;
  if(typeof value.auth_url!=='string'||typeof value.auth_public_key!=='string'||!loopback(new URL(value.auth_url)))return null;
  validateKdgEmailAuthConfig({url:value.auth_url,publicKey:value.auth_public_key});
  return Object.freeze({org:value.org_id,url:value.auth_url,publicKey:value.auth_public_key});
 }catch{return null;}
}
