import type {Session as SdkSession, SupabaseClient} from '@supabase/supabase-js';
import {createEntryBoundary, type EntryState, type Session} from './entry.js';

export type EntryAuth = Pick<SupabaseClient['auth'], 'getSession' | 'onAuthStateChange' | 'refreshSession' | 'signOut'>;
export type AuthEntryOptions = Readonly<{
  org: string; auth: EntryAuth; publish: (state: EntryState) => void;
  beginSignIn: () => Promise<void>; request?: typeof fetch; online?: boolean; timeoutMs?: number;
}>;
const pin=(session: SdkSession | null): Session | null=>session?Object.freeze({account_id:session.user.id,access_token:session.access_token}):null;

/** Auth owns sessions; only the existing KDG context boundary establishes app admission. */
export function createAuthEntry(options: AuthEntryOptions) {
  const {auth}=options, online=options.online??true, duration=options.timeoutMs??10000;
  let state: EntryState=Object.freeze({kind:'checking'}), epoch=0, disposed=false, started=false;
  let locked=false, seenLive=false, muted=false, session: Session | null=null, recovery: string | null=null;
  let subscription: {unsubscribe:()=>void} | undefined, timer: ReturnType<typeof setTimeout> | undefined;
  let finish: (()=>void) | undefined, pending: Promise<void>=Promise.resolve();
  const set=(next: EntryState)=>{if(!disposed){state=Object.freeze(next);options.publish(state);}};
  const gate=createEntryBoundary(options.org,next=>{if(!muted&&!locked&&online)set(next);},options.request);
  const valid=(execution: number)=>!disposed&&epoch===execution;
  function reset() {
    epoch++;if(timer!==undefined)clearTimeout(timer);timer=undefined;
    const previous=finish;finish=undefined;previous?.();
    muted=true;gate.clear();muted=false;
  }
  function fail(execution: number) {
    if(valid(execution)){locked=true;session=null;recovery=null;reset();set({kind:'authorization_unavailable'});}
  }
  function run(task: (execution: number)=>Promise<void>, kind: 'checking' | 'signed_out'='checking', allowOffline=false): Promise<void> {
    if(disposed)return Promise.resolve();
    reset();const execution=epoch;
    if(!Number.isFinite(duration)||duration<=0||duration>10000){locked=true;set({kind:'invalid_response'});return Promise.resolve();}
    if(!online&&!allowOffline){set({kind:'signed_out'});return Promise.resolve();}
    pending=new Promise(resolve=>{finish=resolve;});const result=pending;
    timer=setTimeout(()=>fail(execution),duration);
    set({kind});
    // Never return/await SDK-dependent work from an SDK event callback.
    void Promise.resolve().then(async()=>{if(valid(execution))await task(execution);})
      .catch(()=>fail(execution)).finally(()=>{
        if(valid(execution)){if(timer!==undefined)clearTimeout(timer);timer=undefined;const complete=finish;finish=undefined;complete?.();}
      });
    return result;
  }
  async function check(execution: number, current: Session | null, recover=false) {
    if(!valid(execution))return;
    session=current;
    if(!current){set({kind:'signed_out'});return;}
    const result=await gate.check(current);
    if(valid(execution)&&recover&&result.kind==='authentication_required'){
      session=null;set({kind:'checking'});await options.beginSignIn();if(valid(execution))set({kind:'authentication_required'});
    }
  }
  function event(eventName: string, value: SdkSession | null): void {
    if(disposed||locked)return;
    if(eventName==='INITIAL_SESSION'&&seenLive)return;
    if(eventName!=='INITIAL_SESSION')seenLive=true;
    if(eventName==='SIGNED_OUT'){
      locked=true;session=null;recovery=null;reset();set({kind:'signed_out'});return;
    }
    if(eventName==='PASSWORD_RECOVERY'){
      locked=true;session=null;recovery=null;reset();set({kind:'authentication_required'});return;
    }
    try {
      const current=pin(value);
      if(eventName==='TOKEN_REFRESHED'&&session&&current?.account_id!==session.account_id){
        locked=true;session=null;recovery=null;reset();set({kind:'authentication_required'});return;
      }
      const recover=eventName==='TOKEN_REFRESHED'&&current!==null&&recovery===current.account_id;
      if(recover||eventName!=='INITIAL_SESSION')recovery=null;
      session=current;void run(execution=>check(execution,current,recover));
    }
    catch {fail(epoch);}
  }
  function start(): Promise<void> {
    if(disposed||started)return pending;
    started=true;const before=epoch;
    try {
      const registered=auth.onAuthStateChange(event).data.subscription;
      if(disposed){try{registered.unsubscribe();}catch{}return Promise.resolve();}
      subscription=registered;
    }
    catch {fail(epoch);return Promise.resolve();}
    if(epoch!==before)return pending;
    return run(async execution=>{
      const result=await auth.getSession();if(!valid(execution))return;
      if(result.error){fail(execution);return;}
      await check(execution,pin(result.data.session));
    });
  }
  return {
    state:()=>state,
    start,
    retry(): Promise<void> {
      if(disposed)return Promise.resolve();
      if(state.kind==='checking')return pending;
      locked=false;recovery=null;seenLive=true;
      if(!subscription){started=false;return start();}
      return run(async execution=>{
        const result=await auth.getSession();if(!valid(execution))return;
        if(result.error){fail(execution);return;}
        await check(execution,pin(result.data.session));
      });
    },
    signIn(): Promise<void> {
      if(disposed||!online)return Promise.resolve();
      if(state.kind==='checking')return pending;
      if(!subscription){started=false;return start();}
      const previous=session;locked=false;seenLive=true;recovery=previous?.account_id??null;
      return run(async execution=>{
        if(previous){
          const result=await auth.refreshSession();if(!valid(execution))return;
          const current=result.error?null:pin(result.data.session);
          if(current){
            if(current.account_id!==previous.account_id){locked=true;session=null;recovery=null;set({kind:'authentication_required'});return;}
            recovery=null;await check(execution,current,true);return;
          }
        }
        session=null;recovery=null;await options.beginSignIn();
        if(valid(execution))set({kind:'authentication_required'});
      });
    },
    signOut(): Promise<void> {
      if(disposed)return Promise.resolve();
      locked=true;session=null;recovery=null;
      return run(async execution=>{
        const result=await auth.signOut({scope:'local'});if(!valid(execution))return;
        if(result.error){fail(execution);return;}
        set({kind:'signed_out'});
      },'signed_out',true);
    },
    dispose() {
      if(disposed)return;
      reset();disposed=true;locked=true;session=null;recovery=null;state=Object.freeze({kind:'signed_out'});gate.dispose();
      try{subscription?.unsubscribe();}catch{/* Closed locally even if the SDK cannot detach. */}
      subscription=undefined;
    },
  };
}
