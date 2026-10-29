// Protected-surface adapter for the isolated Auth/email harness only.
// The separate actual-index build uses the real OwnWorkspace without this alias.
import {AuthEntry} from '../../src/AuthEntry';
import {EntryScreen} from '../../src/EntryScreen';
import type {EntryAuth} from '../../src/auth-entry';
export function OwnWorkspace(props:{org:string;auth?:EntryAuth;request?:typeof fetch;online?:boolean;beginSignIn?:()=>Promise<void>}){
 return props.auth?<AuthEntry {...props} auth={props.auth} beginSignIn={props.beginSignIn??(async()=>{})}/>:
  <EntryScreen state={{kind:'signed_out'}} online={props.online??true} onSignIn={()=>{void props.beginSignIn?.();}} onRetry={()=>{}}/>;
}
