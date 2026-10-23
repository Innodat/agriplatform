// KDG-owned admission/UI composition; neutral React lifecycle is generated.
import {useCallback} from 'react';
import {EntryScreen} from './EntryScreen';
import {useSessionLifecycle} from './auth/use-lifecycle';
import {createEntryBoundary,type EntryContext} from './entry';
import type {BoundaryFactory} from './auth/lifecycle';
import type {AuthEntryOptions} from './auth-entry';
export type AuthEntryProps = Omit<AuthEntryOptions,'publish'>;
export function AuthEntry(props: AuthEntryProps) {
 const createBoundary=useCallback<BoundaryFactory<EntryContext>>(publish=>createEntryBoundary(props.org,publish,props.request),[props.org,props.request]);
 const {state,signIn,retry}=useSessionLifecycle<EntryContext>({...props,createBoundary});
 return <EntryScreen state={state} online={props.online??true} onSignIn={signIn} onRetry={retry}/>;
}
