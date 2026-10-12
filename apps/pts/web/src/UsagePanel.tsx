import React from 'react';
import type {ResearchAssessment} from './contracts';

export const researchPurpose='Private team research to train AI to generate Psalms.';
export function UsageBadge({usage}:{usage?:ResearchAssessment}){
 const status=usage?.status||'review';
 return <span className={'usage-badge usage-'+status}>{usage?.label||'Rights need review'}</span>;
}
export function UsagePanel({usage}:{usage?:ResearchAssessment}){
 return <section className="usage-panel" aria-label="Private project usage">
  <h3>Use for our private Psalm project</h3><UsageBadge usage={usage}/>
  <p>{usage?.summary||'Permission for this private training purpose has not yet been assessed.'}</p>
  {usage?.conditions?.length?<ul>{usage.conditions.map((s,i)=><li key={i}>{s}</li>)}</ul>:<p>A different purpose, public sharing or release needs a new rights assessment.</p>}
 </section>;
}
export function TextBadge({poem}:{poem:Record<string,any>}){
 const checked=poem.quality?.text_status==='checked_transcription'&&poem.quality?.complete_in_witness===true;
 return <span className={'text-badge '+(checked?'text-checked':'text-review')}>{!poem.text?'Text not collected':checked?'Text checked against source':'Text needs proofreading'}</span>;
}
