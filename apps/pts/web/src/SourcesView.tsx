import React from 'react';
import type {SourcesResponse} from './contracts';

type RecordData=Record<string,any>;
const link=(value:unknown)=>typeof value==='string'&&/^https?:\/\//i.test(value)?value:undefined;
const label=(key:string)=>key.replaceAll('_',' ').replace(/^./,c=>c.toUpperCase());
function Value({value}:{value:unknown}):React.ReactNode{
 if(value===null||value===undefined||value==='')return null;
 if(Array.isArray(value))return <ul>{value.map((v,i)=><li key={i}><Value value={v}/></li>)}</ul>;
 if(typeof value==='object')return <dl>{Object.entries(value).map(([k,v])=><React.Fragment key={k}><dt>{label(k)}</dt><dd><Value value={v}/></dd></React.Fragment>)}</dl>;
 const url=link(value);return url?<a href={url} target="_blank" rel="noreferrer">{String(value)}</a>:<span>{String(value)}</span>;
}
function Fields({record,keys}:{record:RecordData;keys:string[]}){return <dl>{keys.filter(k=>record[k]!=null&&record[k]!=='').map(k=><React.Fragment key={k}><dt>{label(k)}</dt><dd><Value value={record[k]}/></dd></React.Fragment>)}</dl>;}
function Online({url}:{url:unknown}){const href=link(url);return href?<a href={href} target="_blank" rel="noreferrer">{/\.pdf(?:[?#]|$)/i.test(href)?'Open online PDF':'Visit online source'}</a>:null;}
function Document({document:d,onOpen}:{document:RecordData;onOpen:(id:string)=>void}){return <section className="source-document" aria-label={d.title}>
 <h4>{d.title}</h4><p className="metadata">{label(String(d.status||'Status not recorded'))}{d.pdf_pages?` · ${d.pdf_pages} pages`:''}</p>
 <Fields record={d} keys={['copying_basis','changes','checked']}/>
 <div className="source-actions">{d.local_path&&<button onClick={()=>onOpen(d.id)}>{/\.pdf$/i.test(d.local_path)?'Download PDF':'Download document (HTML)'}</button>}<Online url={d.url}/></div>
 <details><summary>Document details and notices</summary><Fields record={d} keys={Object.keys(d)}/></details>
 </section>;}
export function SourcesView({data,onOpenDocument}:{data:SourcesResponse;onOpenDocument:(id:string)=>void}){
 return <section className="sources-view" aria-label="Source catalogue">
 <p>{data.sources.length} sources</p><p className="quality-note">These are the library’s recorded copyright and reuse assessments, not new rights clearance. Access or a download link does not itself grant reuse permission.</p>
 {data.sources.map(s=>{const rights=data.rights.find(r=>r.id===s.rights_id);const docs=data.source_documents.filter(d=>d.source_id===s.id||d.id===s.document_id);return <article key={s.id}>
 <h2>{s.title}</h2><Fields record={s} keys={['collector_editor','author_role_note','publication_year','publication_place','publisher','languages','digital_repository','historical_context','original_provenance','completeness','scan_page_note']}/>
 <Online url={s.repository_url}/>
 <h3>Recorded copyright and reuse assessment</h3>{rights?<Fields record={rights} keys={Object.keys(rights).filter(k=>!['id','source_id','title'].includes(k))}/>:<p>No rights assessment recorded.</p>}
 <h3>Documents and online references</h3>{docs.length?docs.map(d=><Document key={d.id} document={d} onOpen={onOpenDocument}/>):<p>No document recorded.</p>}
 <details><summary>Full source metadata</summary><Fields record={s} keys={Object.keys(s)}/></details>
 </article>;})}
 <section aria-label="Collection references"><h2>Collection references</h2><p>Background references and recorded rights guidance.</p>{data.source_documents.filter(d=>!d.source_id).map(d=><div className="panel" key={d.id}><Document document={d} onOpen={onOpenDocument}/></div>)}</section>
 </section>;
}
