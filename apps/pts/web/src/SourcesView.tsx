import React,{useState} from 'react';
import type {SourcesResponse} from './contracts';
import {UsagePanel,UsageBadge} from './UsagePanel';

type RecordData=Record<string,any>;
const link=(value:unknown)=>typeof value==='string'&&/^https?:\/\//i.test(value)?value:undefined;
const label=(key:string)=>key.replaceAll('_',' ').replace(/^./,c=>c.toUpperCase());
function Value({value}:{value:unknown}):React.ReactNode{
 if(value===null||value===undefined||value==='')return null;
 if(Array.isArray(value))return <ul>{value.map((v,i)=><li key={i}><Value value={v}/></li>)}</ul>;
 if(typeof value==='object')return <dl>{Object.entries(value).map(([k,v])=><React.Fragment key={k}><dt>{label(k)}</dt><dd><Value value={v}/></dd></React.Fragment>)}</dl>;
 const url=link(value);return url?<a href={url} target="_blank" rel="noreferrer">{String(value)}</a>:<span>{String(value)}</span>;
}
export function RecordFields({record,keys}:{record:RecordData;keys:string[]}){return <dl>{keys.filter(k=>record[k]!=null&&record[k]!=='').map(k=><React.Fragment key={k}><dt>{label(k)}</dt><dd><Value value={record[k]}/></dd></React.Fragment>)}</dl>;}
function Online({url}:{url:unknown}){const href=link(url);return href?<a href={href} target="_blank" rel="noreferrer">{/\.pdf(?:[?#]|$)/i.test(href)?'Open online PDF':'Visit online source'}</a>:null;}
function Document({document:d,onOpen}:{document:RecordData;onOpen:(id:string)=>void}){return <section className="source-document" aria-label={d.title}>
 <h4>{d.title}</h4><p className="metadata">{label(String(d.status||'Status not recorded'))}{d.pdf_pages?` · ${d.pdf_pages} pages`:''}</p>
 <div className="source-actions">{d.local_path&&<button onClick={()=>onOpen(d.id)}>{/\.pdf$/i.test(d.local_path)?'Download PDF':'Download document (HTML)'}</button>}<Online url={d.url}/></div>
 <details><summary>Document details and notices</summary><RecordFields record={d} keys={Object.keys(d)}/></details>
 </section>;}
function Acquisition({plan:p}:{plan?:RecordData}){
 if(!p)return null;const email=typeof p.contact?.email==='string'&&/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(p.contact.email)?p.contact.email:null;
 return <div className="acquisition-plan"><span className={'priority-badge priority-'+p.priority}>{p.priority==='high'?'High priority':'Promising'}</span>
 <p>{p.reason}</p>{p.origin&&<p className="metadata">{p.origin}</p>}
 <p><b>Access:</b> {p.access}</p><p><b>Next step:</b> {p.next_step}</p>{p.rights_note&&<p className="quality-note">{p.rights_note}</p>}
 {p.contact?<p className="source-contact"><b>Contact route:</b> {p.contact.name}{email&&<> · <a href={'mailto:'+email}>{email}</a></>}{link(p.contact.url)&&<> · <a href={link(p.contact.url)} target="_blank" rel="noreferrer">Contact / evidence page</a></>}<br/><small>Checked {p.contact.verified_on}. This contact may help route a request; their authority to grant rights must be confirmed.</small></p>:<p className="quality-note">Direct contact not yet found.</p>}
 <details><summary>Priority evidence</summary>{link(p.source_url)&&<a href={link(p.source_url)} target="_blank" rel="noreferrer">Original collection reference</a>}{p.extent&&<p>{p.extent}</p>}<p>Assessed {p.assessed_on||'2026-10-12'} · {p.assessment_by||'Assistant research assessment'}</p></details></div>;
}
export function SourcesView({data,onOpenDocument}:{data:SourcesResponse;onOpenDocument:(id:string)=>void}){
 const [priorityOnly,setPriorityOnly]=useState(false),[search,setSearch]=useState('');
 const rank=(p?:RecordData)=>p?.priority==='high'?0:p?.priority==='promising'?1:2;
 const matches=(s:RecordData,p?:RecordData)=>(!priorityOnly||rank(p)<2)&&[s.title,p?.origin,p?.reason].join(' ').toLowerCase().includes(search.trim().toLowerCase());
 const sources=data.sources.filter(s=>matches(s,data.acquisition?.[s.id])).sort((x,y)=>rank(data.acquisition?.[x.id])-rank(data.acquisition?.[y.id]));
 const leads=(data.acquisition_leads||[]).filter(s=>matches(s,s)).sort((x,y)=>rank(x)-rank(y));
 return <section className="sources-view" aria-label="Source catalogue">
 <div className="panel source-search"><label>Find a source<input type="search" placeholder="Title, origin or reason to pursue" value={search} onChange={e=>setSearch(e.target.value)}/></label><label className="check-label"><input type="checkbox" checked={priorityOnly} onChange={e=>setPriorityOnly(e.target.checked)}/>Priority sources and access leads only</label></div>
 <p>{sources.length} catalogued sources · {leads.length} acquisition leads shown</p>
 <details><summary>How sources are prioritised</summary><p>High priority means strong relevance to the Psalm project, a promising collection size or useful local poetic forms. Promising sources need more evidence. Ratings are research judgements, with reasons and next steps. They do not grant access or AI permission. Collection leads do not add to poem counts.</p></details>
 {leads.length>0&&<section aria-label="Collection acquisition leads"><h2>Collections worth acquiring</h2>{leads.map(s=><article key={s.id}><h3>{s.title}</h3><Acquisition plan={s}/></article>)}</section>}
 {!sources.length&&!leads.length&&<p>No sources match these filters.</p>}<p className="quality-note">Usage labels apply to this private team’s Psalm AI-training purpose. Other uses need a new assessment.</p>
 {sources.map(s=>{const rights=data.rights.find(r=>r.id===s.rights_id);const docs=data.source_documents.filter(d=>d.source_id===s.id||d.id===s.document_id);return <article key={s.id}>
 <h2>{s.title}</h2><Acquisition plan={data.acquisition?.[s.id]}/><RecordFields record={s} keys={['collector_editor','publication_year','publisher','completeness']}/>
 <UsageBadge usage={data.research_usage?.[s.id]}/><p className="metadata">{data.research_usage?.[s.id]?.summary||'Private-project rights need review.'}</p>
 <details><summary>Project use conditions</summary><UsagePanel usage={data.research_usage?.[s.id]}/></details>
 <Online url={s.repository_url}/>
 <details><summary>Licence and evidence</summary>{rights?<RecordFields record={rights} keys={Object.keys(rights).filter(k=>!['id','source_id','title'].includes(k))}/>:<p>No rights assessment recorded.</p>}</details>
 <h3>Documents and online references</h3>{docs.length?docs.map(d=><Document key={d.id} document={d} onOpen={onOpenDocument}/>):<p>No document recorded.</p>}
 <details><summary>Source background</summary><RecordFields record={s} keys={['author_role_note','publication_place','languages','digital_repository','historical_context','original_provenance','scan_page_note']}/></details>
 <details><summary>Technical source record</summary><RecordFields record={s} keys={Object.keys(s)}/></details>
 </article>;})}
 <section aria-label="Collection references"><details><summary>Background references</summary><p>Background references and recorded rights guidance.</p>{data.source_documents.filter(d=>!d.source_id).map(d=><div className="panel" key={d.id}><Document document={d} onOpen={onOpenDocument}/></div>)}</details></section>
 </section>;
}
