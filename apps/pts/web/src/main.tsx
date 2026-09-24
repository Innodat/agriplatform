import React,{useEffect,useRef,useState} from 'react';
import {createRoot} from 'react-dom/client';
import {AppLauncher} from '@platform/ui-business';
import {createAppDirectoryClient,type AppEntry} from '@platform/app-directory-client';
import {auth,clearPasswordFlow,passwordFlowFor,consumePasswordReturn,type Identity,type PasswordFlow} from './auth';
import type {AuthChangeEvent,Session} from '@supabase/supabase-js';
import {LoginForm} from './LoginForm';
import type {CollectionResponse,PoemResponse,DocumentResponse,Selection} from './contracts';
import './style.css';

type Filters={search:string;availability:string;source:string;genre:string;origin:string;dialect:string;status:string};
const defaults:Filters={search:'',availability:'text',source:'',genre:'',origin:'',dialect:'',status:''};
const base=import.meta.env.VITE_PTS_API_URL || 'http://localhost:8010';
const validOrg=(value:string|null)=>value&&/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(value)?value:'';
const safeLink=(value:unknown)=>typeof value==='string'&&/^https?:\/\//.test(value)?value:undefined;
const initial=new URLSearchParams(location.search);
const initialFilters={...defaults,...Object.fromEntries(Object.keys(defaults).filter(k=>initial.has(k)).map(k=>[k,initial.get(k)!]))};
function App(){
 const [identity,setIdentity]=useState<Identity|null>(null),[authReady,setAuthReady]=useState(false),[apps,setApps]=useState<AppEntry[]>([]);
 const [passwordFlow,setPasswordFlow]=useState<PasswordFlow|null>(null),[loginError,setLoginError]=useState('');
 const [org,setOrg]=useState(validOrg(initial.get('org')));
 const [applied,setApplied]=useState<Filters>(initialFilters),[draft,setDraft]=useState<Filters>(initialFilters);
 const [poemId,setPoemId]=useState(initial.get('poem')||''),[data,setData]=useState<CollectionResponse|null>(null),[single,setSingle]=useState<PoemResponse|null>(null);
 const [error,setError]=useState(''),[notice,setNotice]=useState(''),[loading,setLoading]=useState(false),[reload,setReload]=useState(0),[copyText,setCopyText]=useState(''),[documentUrl,setDocumentUrl]=useState('');
 const dialog=useRef<HTMLDialogElement>(null),copyDialog=useRef<HTMLDialogElement>(null),filterButton=useRef<HTMLButtonElement>(null);
 const pendingFilters=useRef<Filters|null>(null);
 const authorityEpoch=useRef(0);
 const generation=useRef(0),current=useRef<Identity|null>(null),lastUser=useRef(sessionStorage.getItem('pts-last-user'));
 function clear(){authorityEpoch.current++;generation.current++;setData(null);setSingle(null);setCopyText('');setDocumentUrl('');copyDialog.current?.close();setNotice('');}
 useEffect(()=>{
   let active=true,initialized=false,revision=0;
   function accept(session:Session|null,event?:AuthChangeEvent){
     revision++;
     const next=session?{id:session.user.id,token:session.access_token}:null;
     const flow=passwordFlowFor(session,event);
     if(current.current?.id!==next?.id||flow){clear();setApps([]);setError('');}
     if(next&&lastUser.current&&lastUser.current!==next.id){history.replaceState(null,'',location.pathname);setApplied(defaults);setDraft(defaults);setPoemId('');setOrg('');setNotice('Account changed. Choose your organization to continue.');}
     if(next&&flow==='recovery'){
       const restored=consumePasswordReturn(next.id);
       if(restored){setApplied({...defaults,...Object.fromEntries(Object.keys(defaults).filter(k=>restored.has(k)).map(k=>[k,restored.get(k)!]))});setDraft(defaults);setOrg(validOrg(restored.get('org')));setPoemId(restored.get('poem')||'');history.replaceState(null,'',location.pathname+'?'+restored);}
     }
     if(next){lastUser.current=next.id;sessionStorage.setItem('pts-last-user',next.id);}
     current.current=next;setIdentity(next);setPasswordFlow(flow);setLoginError('');setAuthReady(true);
   }
   const {data}=auth.onAuthStateChange((event,session)=>{if(active&&initialized&&event!=='INITIAL_SESSION')accept(session,event);});
   void (async()=>{
     const result=await auth.initialize();
     if(!active)return;
     initialized=true;
     if(result.error){clearPasswordFlow();history.replaceState(null,'',location.pathname+location.search);setLoginError('This sign-in link is invalid or has expired. Request a new reset link or sign in with your password.');setAuthReady(true);return;}
     const atStart=revision;
     const {data,error}=await auth.getSession();
     if(active&&revision===atStart){if(error){setLoginError('We could not restore your session. Please sign in again.');setAuthReady(true);}else accept(data.session);}
   })().catch(()=>{if(active){setLoginError('We could not restore your session. Please sign in again.');setAuthReady(true);}});
   return ()=>{active=false;data.subscription.unsubscribe();};
 },[]);
 function passwordSaved(){clearPasswordFlow();setPasswordFlow(null);setNotice('Password saved.');setReload(v=>v+1);}
 async function signOut(){
   clear();
   const {error}=await auth.signOut({scope:'local'});
   if(error){setLoginError('We could not sign you out. Please try again.');setError('We could not sign you out. Please try again.');return;}
   clearPasswordFlow();clear();current.current=null;setIdentity(null);setPasswordFlow(null);
 }

 useEffect(()=>{
   if(!identity||passwordFlow||!authReady)return;
   let active=true;
   const directory=createAppDirectoryClient({baseUrl:import.meta.env.VITE_APP_DIRECTORY_URL||'http://localhost:8001',getToken:async()=>identity.token});
   directory.getMyApps().then(result=>{if(active){setApps(result.apps);if(!org&&validOrg(result.context.org_id)) {setOrg(result.context.org_id!);}}}).catch(()=>{if(active)setApps([]);});
   return ()=>{active=false;};
 },[identity?.id,passwordFlow,authReady]);
 useEffect(()=>{const back=()=>{
   const wasFilter=dialog.current?.open;dialog.current?.close();
   if(pendingFilters.current){setApplied(pendingFilters.current);pendingFilters.current=null;filterButton.current?.focus();return;}
   if(wasFilter){filterButton.current?.focus();return;}
   const params=new URLSearchParams(location.search);
   clear();setReload(v=>v+1);setPoemId(params.get('poem')||'');setOrg(validOrg(params.get('org')));
   setApplied({...defaults,...Object.fromEntries(Object.keys(defaults).filter(k=>params.has(k)).map(k=>[k,params.get(k)!]))});
 };window.addEventListener('popstate',back);return ()=>window.removeEventListener('popstate',back);},[]);
 function navigatePoem(id:string){if(id===poemId)return;const params=new URLSearchParams(applied);params.set('org',org);if(id)params.set('poem',id);history.pushState(null,'','?'+params);clear();setPoemId(id);window.scrollTo(0,0);}

 function closeFilters(apply=false){if(apply)pendingFilters.current=draft;if(history.state?.ptsFilters)history.back();else{dialog.current?.close();if(apply){setApplied(draft);pendingFilters.current=null;}filterButton.current?.focus();}}
 async function request<T>(path:string):Promise<T>{
   if(!current.current)throw new Error('Please sign in again to continue.');
   const atStart=current.current.id, epoch=authorityEpoch.current;
   let response=await fetch(base+path,{headers:{Authorization:'Bearer '+current.current.token,'X-Org-ID':org},cache:'no-store'});
   if(response.status===401){
     const refreshed=await auth.refreshSession();
     if(refreshed.data.session&&refreshed.data.session.user.id===atStart){response=await fetch(base+path,{headers:{Authorization:'Bearer '+refreshed.data.session.access_token,'X-Org-ID':org},cache:'no-store'});}
   }
   if(current.current?.id!==atStart)throw new Error('Account changed. Please open the collection again.');
   if(!response.ok){
     if(response.status===401||response.status===403){clear();setLoading(false);if(response.status===401)setIdentity(null);}
     const messages:Record<number,string>={401:'Please sign in again to continue.',403:'You do not currently have access to this collection or action.',404:'This poem or document is unavailable.',503:'We could not verify access or complete this request. Please retry.'};
     throw new Error(messages[response.status]||'We could not complete this request. Please retry.');
   }
   const body=await ((response.headers.get('content-type')||'').includes('json')?response.json():response.text());
   if(current.current?.id!==atStart||authorityEpoch.current!==epoch)throw new Error('Session or access changed. Please try again.');
   return body as T;
 }
 const query=new URLSearchParams(applied).toString();
 useEffect(()=>{
   if(!identity||!org||passwordFlow||!authReady)return;
   const serial=++generation.current;setLoading(true);setError('');setData(null);setSingle(null);
   const path=poemId?'/api/poetry/'+encodeURIComponent(poemId):'/api/poetry?'+query;
   request<CollectionResponse|PoemResponse>(path).then(result=>{if(serial===generation.current){if(poemId)setSingle(result as PoemResponse);else setData(result as CollectionResponse);}}).catch(e=>{if(serial===generation.current)setError(e.message);else if(current.current)setError(e.message);}).finally(()=>{if(serial===generation.current)setLoading(false);});
   const params=new URLSearchParams(applied);params.set('org',org);if(poemId)params.set('poem',poemId);
   history.replaceState(history.state,'','?'+params);
   return ()=>{generation.current++;};
 },[identity?.id,identity?.token,org,query,poemId,reload,passwordFlow,authReady]);
 useEffect(()=>{const refresh=()=>{if(document.visibilityState==='visible'){clear();setReload(v=>v+1);}};window.addEventListener('focus',refresh);document.addEventListener('visibilitychange',refresh);return ()=>{window.removeEventListener('focus',refresh);document.removeEventListener('visibilitychange',refresh);};},[]);
 const selection:Selection|null=single?.evidence||data;
 const poems=single?[single.poem]:(data?.poems||[]);
 async function copy(id:string){const epoch=authorityEpoch.current;try{const result=await request<PoemResponse>('/api/poetry/'+encodeURIComponent(id));if(epoch!==authorityEpoch.current)return;try{await navigator.clipboard.writeText(result.citation);if(epoch!==authorityEpoch.current)return;setNotice('Copied poem with citation, quality and reuse notes.');}catch{if(epoch!==authorityEpoch.current)return;setCopyText(result.citation);copyDialog.current?.showModal();}}catch(e){setError((e as Error).message);}}
 async function exportResult(format:'json'|'text'){const epoch=authorityEpoch.current;try{const result=await request<unknown>('/api/exports?'+query+'&format='+format);if(epoch!==authorityEpoch.current)return;const blob=new Blob([format==='json'?JSON.stringify(result,null,2):String(result)],{type:format==='json'?'application/json':'text/plain'});const url=URL.createObjectURL(blob);const a=document.createElement('a');a.href=url;a.download='Swahili-poetry-selection.'+(format==='json'?'json':'txt');a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);setNotice('Exported current results with source rights and alternate witnesses.');}catch(e){setError((e as Error).message);}}
 async function openDocument(id:string){const epoch=authorityEpoch.current;try{const result=await request<DocumentResponse>('/api/documents/'+encodeURIComponent(id));if(epoch!==authorityEpoch.current)return;const url=safeLink(result.url);if(!url)throw new Error('The document link is unavailable.');setDocumentUrl(url);window.open(url,'_blank','noopener,noreferrer');setTimeout(()=>setDocumentUrl(''),Math.min(result.expires_in||300,300)*1000);setNotice(result.status==='link_only'?'Opened the original reference. No local copy is held.':'Opened private document. If the link expires, open it again.');}catch(e){setError((e as Error).message);}}
 function filterFields(values:Filters,update:(f:Filters)=>void,prefix:string){return <><label>Show poems<select value={values.availability} onChange={e=>update({...values,availability:e.target.value})}><option value="text">With text only</option><option value="all">All catalogue records</option><option value="checked">Checked transcriptions (complete)</option><option value="review">Needs text review</option></select></label>{(['source','genre','origin','dialect','status'] as const).map(key=><label key={key}>{key==='status'?'Text status':key[0].toUpperCase()+key.slice(1)}<select id={prefix+key} value={values[key]} onChange={e=>update({...values,[key]:e.target.value})}><option value="">All {key==='status'?'statuses':key+'s'}</option>{(data?.filters[key]||[]).map(v=><option key={v} value={v}>{v.replaceAll('_',' ')}</option>)}</select></label>)}</>;}
 const changed=Object.keys(defaults).filter(k=>applied[k as keyof Filters]!==defaults[k as keyof Filters]).length;
 return <><header className="shell"><AppLauncher apps={apps}/><a href="?" className="brand">PtS</a><span>Swahili Poetry</span>{identity&&<button className="signout" onClick={signOut}>Sign out</button>}</header><main>
 {!poemId&&<><h1>Swahili Poetry</h1><p className="intro">Read the collected poems, their source witnesses and the evidence behind them.</p></>}
 {!authReady?<p role="status">Checking your session…</p>:(!identity||passwordFlow)?<LoginForm key={(identity?.id||'signed-out')+':'+passwordFlow+':'+loginError} flow={passwordFlow} initialError={loginError} onPasswordSaved={passwordSaved}/>:<>
 {!org&&<p role="status">No organization is selected. Select your organization in the platform directory, then return to this collection.</p>}
 {org&&<>{!poemId&&<section aria-label="Collection filters" className="panel"><label>Search title, poet, place, form or dialect<input type="search" value={applied.search} onChange={e=>setApplied({...applied,search:e.target.value})}/></label><div className="desktop-filters">{filterFields(applied,setApplied,'desktop-')}<button onClick={()=>setApplied(defaults)}>Reset filters</button></div><button className="mobile-filters" ref={filterButton} onClick={()=>{setDraft(applied);history.pushState({ptsFilters:true},'',location.href);dialog.current?.showModal();}}>Filters{changed?' ('+changed+')':''}</button></section>}
 {!poemId&&<p className="quality-note">Checked transcriptions reflect assistant source checks and completeness in the cited witness. They do not establish independent human review, rights clearance or training readiness.</p>}
 {loading&&<p role="status">Loading poems…</p>}{error&&<div role="alert" className="error">{error} <button onClick={()=>{setError('');setLoading(false);setReload(v=>v+1);}}>Retry</button></div>}<p role="status">{notice}</p>{documentUrl&&<p><a href={documentUrl} target="_blank" rel="noreferrer">Open document in a new tab</a></p>}
 {poemId&&<button onClick={()=>navigatePoem('')}>Back to results</button>}
 {data&&<div className="result-tools"><p>{data.total} of {data.collection_total} records</p><button disabled={!data.total} onClick={()=>exportResult('json')}>Export results (JSON)</button><button disabled={!data.total} onClick={()=>exportResult('text')}>Export results (text)</button></div>}
 {data&&<details className="panel"><summary>Collection references and document notices</summary>{data.source_documents.filter(d=>!d.source_id).map(d=><section key={d.id}><h3>{d.title}</h3><p>{d.copying_basis}</p><button onClick={()=>openDocument(d.id)}>Open reference document</button></section>)}</details>}
 {!loading&&data&&poems.length===0&&<div className="panel"><p>No poems match these filters.</p><button onClick={()=>setApplied(defaults)}>Clear filters</button></div>}
 {poems.map(p=><article key={p.id} id={p.id}><h2><a href={'?'+new URLSearchParams({...applied,org,poem:p.id})} onClick={e=>{e.preventDefault();navigatePoem(p.id);}}>{p.title}</a></h2><p className="metadata"><b>Poet:</b> {p.creator?.name||'Unattributed'} · <b>Origin:</b> {p.geography?.origin_locality||'Not established'}<br/><b>Genre:</b> {p.classification?.genre||'Not established'} · <b>Dialect:</b> {p.geography?.dialect||'Not established'}</p><p className="badge">{String(p.quality?.text_status||'Unknown text status').replaceAll('_',' ')}</p>{p.text?<pre className="poem-text" lang="sw">{p.text}</pre>:<p>Text has not been collected for this record.</p>}{poemId&&<p className="quality-note">Assistant source checks do not establish independent human review, rights clearance or training readiness.</p>}<button onClick={()=>copy(p.id)}>Copy poem with citation</button>
 <details><summary>Evidence, witnesses and rights</summary><p>{p.quality?.reviewer_note}</p><h3>Citation</h3><p>{p.source?.citation} {p.source?.locator}</p>{safeLink(p.source?.url)&&<a href={p.source.url} target="_blank" rel="noreferrer">Original source reference</a>}
 {selection?.source_documents.filter(d=>d.source_id===p.source_id||selection.witnesses.some(w=>w.poem_id===p.id&&w.source_id===d.source_id)).map(d=><section key={d.id}><h3>{d.title}</h3><p>{d.copying_basis}</p><button onClick={()=>openDocument(d.id)}>{d.local_path?'Open source document':'Open source reference'}</button></section>)}
 <h3>Source rights</h3>{selection?.sources.filter(s=>s.id===p.source_id||selection.witnesses.some(w=>w.poem_id===p.id&&w.source_id===s.id)).map(s=><details key={s.id}><summary>{s.title}</summary><pre>{JSON.stringify(selection.rights.find(r=>r.id===s.rights_id),null,2)}</pre></details>)}
 <h3>Alternate witnesses</h3>{selection?.witnesses.filter(w=>w.poem_id===p.id).map(w=><details key={w.id}><summary>{w.id} · {w.source_id}</summary><pre>{JSON.stringify(w,null,2)}</pre></details>)}<details><summary>Full original record and history</summary><pre>{JSON.stringify(p,null,2)}</pre></details></details></article>)}</>}
 </>}
 </main><dialog ref={dialog} aria-labelledby="filter-title" onCancel={e=>{e.preventDefault();closeFilters();}}><div className="dialog-head"><h2 id="filter-title">Filters</h2><button onClick={()=>closeFilters()}>Close</button><button onClick={()=>setDraft(defaults)}>Reset filters</button></div><div className="dialog-body">{filterFields(draft,setDraft,'mobile-')}</div><div className="dialog-footer"><button onClick={()=>closeFilters(true)}>Apply filters</button></div></dialog>
 <dialog ref={copyDialog} aria-labelledby="copy-title"><h2 id="copy-title">Copy poem with citation</h2><p>Select and copy this text.</p><textarea aria-label="Poem and citation" value={copyText} readOnly onFocus={e=>e.target.select()}/><button onClick={()=>copyDialog.current?.close()}>Close</button></dialog></>;
}
createRoot(document.getElementById('root')!).render(<App/>);
