import type {EntryState} from './entry';

export type EntryScreenProps = Readonly<{
  state: EntryState;
  online: boolean;
  onSignIn: () => void;
  onRetry: () => void;
}>;
type Presentation = Readonly<{title: string; message: string; action: 'signIn' | 'retry'; label: string}>;
const interrupted: Presentation={title:'Access check interrupted',message:'Check access again to continue.',action:'retry',label:'Retry'};
const states: Record<EntryState['kind'], Presentation> = {
  signed_out:{title:'Sign in to continue',message:'Sign in to check your current KDG Capture access.',action:'signIn',label:'Sign in'},
  authentication_required:{title:'Sign in again',message:'Sign in to check your current access again.',action:'signIn',label:'Sign in'},
  checking:{title:'Checking access',message:'Checking your current KDG Capture access.',action:'retry',label:'Checking access…'},
  authorized:{title:'Setup not completed',message:'Your current entry access is confirmed. Online setup is still required before observations are available.',action:'retry',label:'Check access again'},
  access_denied:{title:'Access denied',message:'This account does not currently have KDG Capture access.',action:'retry',label:'Check access again'},
  actor_setup_required:{title:'Account setup not completed',message:'Account setup is not yet complete. Check again after setup is available.',action:'retry',label:'Retry'},
  authorization_unavailable:{title:'Could not check access',message:'Access verification is unavailable. Retry when you are ready.',action:'retry',label:'Retry'},
  invalid_response:{title:'Could not verify access',message:'Access could not be verified. Retry when you are ready.',action:'retry',label:'Retry'},
  cancelled:interrupted,
  superseded:interrupted,
};
const offline: Presentation={title:'Connect to the internet',message:'Online sign-in and setup are required before observations are available on this device.',action:'retry',label:'Retry'};

/** Presentation only. Auth and the current-entry boundary own state and actions. Mount once per entry page. */
export function EntryScreen({state,online,onSignIn,onRetry}: EntryScreenProps) {
  const view=online?states[state.kind]:offline;
  const blocked=!online||state.kind==='checking';
  return <div className="kdg-entry" lang="en">
    <a className="kdg-entry-skip" href="#kdg-entry-content">Skip to content</a>
    <main id="kdg-entry-content" tabIndex={-1}>
      <h1>KDG Capture</h1>
      <p className="kdg-entry-organization">Khula Development Group</p>
      <section aria-label="Entry status">
        <div role="status" aria-live="polite" aria-atomic="true">
          <h2>{view.title}</h2>
          <p>{view.message}</p>
        </div>
        <button type="button" aria-busy={online&&state.kind==='checking'} aria-disabled={blocked||undefined} onClick={()=>{
          if(!blocked)(view.action==='signIn'?onSignIn:onRetry)();
        }}>{view.label}</button>
      </section>
    </main>
  </div>;
}
