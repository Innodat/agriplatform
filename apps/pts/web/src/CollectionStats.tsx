import React from 'react';
import type {ResearchAssessment} from './contracts';
type Poem=Record<string,any>;
export function textLength(p:Poem){
 const text=typeof p.text==='string'?p.text:'';
 const lines=text.split(/\r?\n/).filter(s=>s.trim()&&!/^[\d\s.()\[\]:-]+$/.test(s.trim())).length;
 const words=(text.match(/[\p{L}]+(?:['’][\p{L}]+)*/gu)||[]).length;
 return {lines,words,band:!lines?'missing':lines<=12?'short':lines<40?'medium':'substantial'};
}
const checked=(p:Poem)=>Boolean(p.text)&&p.quality?.text_status==='checked_transcription'&&p.quality?.complete_in_witness===true;
const names:Record<string,string>={short:'Short text',medium:'Medium text',substantial:'Substantial text'};
export function PoemLength({poem:p}:{poem:Poem}){
 const m=textLength(p);if(m.band==='missing')return null;
 const completeness=p.quality?.complete_in_witness===false?'Excerpt / incomplete':p.quality?.complete_in_witness!==true?'Completeness unconfirmed':'';
 return <p className="poem-length">{names[m.band]} · {m.lines} lines · {m.words} words{completeness&&<> · <strong>{completeness}</strong></>}</p>;
}
export function CollectionStats({poems,usage}:{poems:Poem[];usage?:Record<string,ResearchAssessment>}){
 const unique=new Map<string,Poem>();
 const ready=(p:Poem)=>checked(p)&&usage?.[p.id]?.eligible_for_private_training===true;
 for(const p of poems){const key=p.work_id||p.id,old=unique.get(key);const score=(x:Poem)=>[Number(ready(x)),Number(checked(x)),textLength(x).words];
  const before=old&&score(old),now=score(p);
  if(!old||now[0]>before![0]||now[0]===before![0]&&(now[1]>before![1]||now[1]===before![1]&&now[2]>before![2]))unique.set(key,p);
 }
 const counts:Record<string,number>={short:0,medium:0,substantial:0,missing:0,ready:0};let words=0;
 for(const p of unique.values()){const m=textLength(p);counts[m.band]++;words+=m.words;if(ready(p))counts.ready++;}
 return <section className="collection-summary panel" aria-label="Results summary">
 <h2>{unique.size} distinct {unique.size===1?'work':'works'} in these results</h2>
 <div className="summary-counts">{[['ready','Ready for team research'],['short','Short texts'],['medium','Medium texts'],['substantial','Substantial texts'],['missing','Text not collected']].map(([key,label])=><div key={key}><strong data-stat={key}>{counts[key]}</strong><span>{label}</span></div>)}</div>
 <p className="quality-note">{words.toLocaleString()} words of collected text · {poems.length} record {poems.length===1?'version':'versions'}. Alternate versions count once.</p>
 <details><summary>How these counts work</summary><p>Short: up to 12 lines. Medium: 13–39 lines. Substantial: 40 or more lines. These describe the collected text’s length; an excerpt is not a complete short poem. Stored line breaks, including half-lines, can affect the category.</p><p>“Ready” requires a complete text checked against its published source and recorded rights supporting this private Psalm project. Assistant source checks are separate from expert Swahili review. For each work, counts favour a ready version, then a checked version, then the longest collected text.</p></details>
 </section>;
}
