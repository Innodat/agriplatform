// Create-once owner seed: application shell and owner API boundary.
import {useEffect, useState} from 'react';
import {getHealth} from './api/health';
export function App() {
 const [health,setHealth]=useState('Checking API…');
 useEffect(()=>{let active=true;void getHealth().then(result=>{if(active)setHealth(result.ok?'API available':'API unavailable');});return ()=>{active=false;};},[]);
 return <><a className="skip-link" href="#main">Skip to content</a><header><span className="brand">{{OWNER}}</span><nav aria-label="Main"><a href="/" aria-current="page">Home</a></nav></header><main id="main" tabIndex={-1}><h1>Welcome</h1><p>Your application starts here.</p><p role="status">{health}</p></main></>;
}
