// Synthetic Auth/session host only. This is not a product provider or application entrypoint.
import {createRoot} from 'react-dom/client';
import {EntryScreen} from '../../src/EntryScreen';
import {createEntryBoundary, type EntryState, type Session} from '../../src/entry';
import '../../src/entry-screen.css';
const ORG='33333333-3333-4333-8333-333333333333';
let state: EntryState={kind:'signed_out'}, online=true, current: Session | null=null, signIns=0, retries=0;
const root=createRoot(document.getElementById('root')!);
const gate=createEntryBoundary(ORG,next=>{state=next;render();});
const signIn=()=>{signIns++;current={account_id:'11111111-1111-4111-8111-111111111111',access_token:'synthetic-entry'};void gate.check(current);};
const retry=()=>{retries++;void gate.check(current);};
function render(){root.render(<EntryScreen state={state} online={online} onSignIn={signIn} onRetry={retry}/>);}
const fixture={
  check:async(account:string)=>{current={account_id:account,access_token:'synthetic-'+account};return gate.check(current);},
  clear:()=>{current=null;gate.clear();},
  online:(value:boolean)=>{online=value;render();},
  snapshot:()=>({kind:gate.state().kind,signIns,retries}),
};
Object.assign(window,{fixture});render();
