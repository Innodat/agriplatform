import {mountAdminPortalPreview} from '../../src/admin-portal-preview.js';
import type {ProviderSession} from '../../src/auth/lifecycle.js';
const A='aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa',O='bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb';
let session:ProviderSession|null={user:{id:A},access_token:'synthetic'},callback:(event:string,value:ProviderSession|null)=>void=()=>{},ignoreAbort=false;
const auth={getSession:async()=>({data:{session},error:null}),refreshSession:async()=>({data:{session},error:null}),signOut:async()=>({error:null}),onAuthStateChange(fn:typeof callback){callback=fn;return{data:{subscription:{unsubscribe(){callback=()=>{};}}}};}};
const host=mountAdminPortalPreview(document.getElementById('root')!,{auth,org_id:O,from_date:'2026-10-01',to_date:'2026-10-28',beginSignIn:async()=>{},request:(url,init)=>fetch(url,ignoreAbort?{...init,signal:undefined}:init)});
const fixture={portal:host.portal,event(name:string,account:string|null=A){session=account?{user:{id:account},access_token:'synthetic'}:null;callback(name,session);},ignoreAbort(value:boolean){ignoreAbort=value;},dispose:host.dispose};
(window as unknown as {fixture:typeof fixture}).fixture=fixture;
