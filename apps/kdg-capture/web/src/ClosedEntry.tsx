import {useLayoutEffect,useRef} from 'react';
import type {BrowserEntryState} from './auth/lifecycle';
export function ClosedEntry({state,failed}:{state:BrowserEntryState;failed:boolean}){
 const main=useRef<HTMLElement>(null);
 useLayoutEffect(()=>{main.current?.focus();},[state.route,failed]);
 const title=state.route!=='entry'?'Page unavailable':failed?'Could not open KDG Capture':'Connect to the internet';
 return <div className="kdg-entry" lang="en"><a className="kdg-entry-skip" href="#kdg-entry-content">Skip to content</a>
  <main ref={main} id="kdg-entry-content" tabIndex={-1}><h1>KDG Capture</h1><p className="kdg-entry-organization">Khula Development Group</p>
   <div role="status" aria-live="polite"><h2>{title}</h2><p>{state.route!=='entry'?'Open the start page to continue.':failed?'Please try opening the app again.':'Online sign-in is required.'}</p></div>
   <a className="kdg-entry-start" href="/">Go to start</a>
  </main></div>;
}
