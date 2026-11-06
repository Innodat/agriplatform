// Owner seed: the current provider-backed, currently admitted session only.
import {useSyncExternalStore} from 'react';
import type {LauncherSession} from '@platform/ui-business';
import {leaveSession} from './leave-session';
export function useLauncherSession():{session:LauncherSession|null;loading:boolean}{
 const snapshot=useSyncExternalStore(leaveSession.subscribe,leaveSession.snapshot);
 const lease=leaveSession.acquire();
 if(!lease)return{session:null,loading:snapshot.state.kind==='checking'};
 try{return{session:{accessToken:lease.session.access_token,accountId:lease.session.account_id},loading:false};}
 finally{lease.release();}
}
