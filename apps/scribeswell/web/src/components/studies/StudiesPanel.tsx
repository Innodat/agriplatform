import {useEffect,useState} from 'react';
import {useStudies} from '@/context/StudiesContext';
import {useAuth} from '@/context/AuthContext';
import type {NoteValue} from '@/lib/personal-notes';
export function preview(value:NoteValue){return value.document.blocks.flatMap(block=>block.type==='paragraph'?[block]:block.items.flat()).map(p=>p.content.map(i=>i.type==='text'?i.text:i.content.map(t=>t.text).join('')).join('')).join(' ').slice(0,120)||'Empty note';}
export function StudiesPanel(){const studies=useStudies(),{user}=useAuth();const [creating,setCreating]=useState(false),[title,setTitle]=useState('');useEffect(()=>{setCreating(false);setTitle('');},[user?.id]);
 return <section aria-label="My studies" className="p-3 space-y-3">
 <h2 className="font-semibold">My studies</h2>
 {studies.error&&<p role="alert">{studies.error} <button className="underline" onClick={()=>void studies.loadStudies()}>Retry</button></p>}
 {!user&&<p>Sign in or create an account from the header to start a study.</p>}
 {user&&studies.study?<><h3 className="font-semibold">{studies.study.title}</h3><button className="underline" disabled={studies.busy} onClick={()=>void studies.addNote()}>Add note</button><ul aria-label="Notes">{studies.notes.map(note=><li key={note.id}><button className="my-2 text-left underline" onClick={()=>void studies.openNote(note.id)}>{preview(note.value)}</button></li>)}</ul>{studies.notesCursor&&<button className="underline" onClick={()=>void studies.moreNotes()}>More notes</button>}<button className="underline block" onClick={()=>void studies.leave()}>Leave study</button></>:user&&<><ul aria-label="Studies">{studies.studies.map(study=><li key={study.id}><button className="underline py-2" onClick={()=>void studies.openStudy(study.id)}>{study.title}</button></li>)}</ul>{studies.studyCursor&&<button className="underline" onClick={()=>void studies.loadStudies(true)}>More studies</button>}{creating?<form onSubmit={e=>{e.preventDefault();void studies.create(title||null);}}><label>Study title (optional)<input maxLength={200} className="block border rounded p-2 w-full" value={title} onChange={e=>setTitle(e.target.value)} /></label><button className="underline my-2" disabled={studies.busy} type="submit">Create study</button></form>:<button className="underline" disabled={studies.busy} onClick={async()=>{if(await studies.start())setCreating(true);}}>Start a study</button>}</>}
 {studies.busy&&<p role="status">Loading Studies…</p>}
 </section>;
}
