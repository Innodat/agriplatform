import {useLayoutEffect, useRef, useState} from 'react';
import {EntryScreen} from './EntryScreen';
import {createAuthEntry, type AuthEntryOptions} from './auth-entry';
import type {EntryState} from './entry';
export type AuthEntryProps = Omit<AuthEntryOptions,'publish'>;
/** Supply one stable owner Auth client and launch action. No provider configuration or navigation here. */
export function AuthEntry(props: AuthEntryProps) {
  const [state,setState]=useState<EntryState>({kind:'checking'});
  const bridge=useRef<ReturnType<typeof createAuthEntry> | null>(null);
  useLayoutEffect(()=>{
    const current=createAuthEntry({...props,publish:setState});bridge.current=current;
    setState(current.state());void current.start();
    return ()=>{bridge.current=null;current.dispose();};
  },[props.auth,props.org,props.beginSignIn,props.request,props.online,props.timeoutMs]);
  return <EntryScreen state={state} online={props.online??true}
    onSignIn={()=>{void bridge.current?.signIn();}} onRetry={()=>{void bridge.current?.retry();}}/>;
}
