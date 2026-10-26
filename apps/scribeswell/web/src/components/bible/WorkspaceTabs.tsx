import {useEffect,useRef,useState} from 'react';
import {useStudies} from '@/context/StudiesContext';
import {useWorkspace} from '@/context/ReaderWorkspaceContext';
import {workspaceTabId} from '@/lib/reader-layout';
import {referenceLabel} from '@/lib/passage-references';
export function WorkspaceTabs(){
 const studies=useStudies(),controller=useWorkspace(),{workspace,tabs}=controller;
 const [focus,setFocus]=useState(workspace.tabKey),[editing,setEditing]=useState<string|null>(null),[candidate,setCandidate]=useState(''),[error,setError]=useState('');
 const rename=useRef<HTMLDialogElement>(null),restore=useRef<HTMLDialogElement>(null);
 useEffect(()=>{setFocus(workspace.tabKey);document.getElementById(workspaceTabId(workspace.tabKey))?.scrollIntoView({block:'nearest',inline:'nearest'});},[workspace.tabKey]);
 useEffect(()=>{if(editing&&!studies.searchMasked)rename.current?.showModal();},[editing,studies.searchMasked]);
 useEffect(()=>{if(controller.pendingRestore)restore.current?.showModal();},[controller.pendingRestore]);
 const label=(tab:typeof workspace)=>(!studies.searchMasked?tab.label:undefined)??`${referenceLabel(tab.panes[0].ref)}${tab.panes.length>1?` +${tab.panes.length-1}`:''}`;
 function move(event:React.KeyboardEvent,index:number){
  const next=event.key==='Home'?0:event.key==='End'?tabs.length-1:event.key==='ArrowLeft'?(index+tabs.length-1)%tabs.length:event.key==='ArrowRight'?(index+1)%tabs.length:undefined;
  if(next===undefined)return;event.preventDefault();setFocus(tabs[next].tabKey);const node=document.getElementById(workspaceTabId(tabs[next].tabKey));node?.focus();node?.scrollIntoView({block:'nearest',inline:'nearest'});
 }
 return <div className="shrink-0 min-w-0">
 <div role="tablist" aria-label="Workspace tabs" className="flex max-w-full overflow-x-auto gap-1 items-center">
 {tabs.map((tab,index)=><div key={tab.tabKey} className="flex shrink-0 items-center border rounded">
 <button role="tab" id={workspaceTabId(tab.tabKey)} data-workspace-tab={tab.tabKey} aria-controls="workspace-panel" aria-selected={workspace.tabKey===tab.tabKey} tabIndex={focus===tab.tabKey?0:-1} onFocus={()=>setFocus(tab.tabKey)} onKeyDown={e=>move(e,index)} className="px-3 py-2 max-w-48 truncate" dir="auto" onClick={()=>controller.activateTab(tab.tabKey)}>{label(tab)}</button>
 <button disabled={studies.searchMasked} aria-describedby={studies.searchMasked?'rename-access-reason':undefined} className="p-2 disabled:opacity-40" aria-label={`Rename tab ${index+1}`} onClick={()=>{setEditing(tab.tabKey);setCandidate(tab.label??'');setError('');}}>Rename</button>
 {tabs.length>1&&<button data-close-tab className="p-2" aria-label={`Close tab ${index+1}`} onClick={()=>controller.closeTab(tab.tabKey)}>×</button>}
 </div>)}
 </div>
 {studies.searchMasked&&<span id="rename-access-reason" className="sr-only">Sign in and restore Studies access to rename tabs.</span>}
 <button className="underline py-1" aria-label="New workspace tab" onClick={()=>controller.newTab()}>+ New tab</button>
 {controller.historyHeld&&!controller.pendingRestore&&<p role="status">The current arrangement remains displayed. <button className="underline" onClick={controller.retryRestore}>Choose tab to close and restore</button></p>}
 {controller.notice&&<p role="status">{controller.notice}</p>}
 {editing&&!studies.searchMasked&&<dialog ref={rename} aria-label="Rename workspace tab" onCancel={()=>setEditing(null)} className="rounded p-4 max-w-[calc(100vw-2rem)]"><form onSubmit={e=>{e.preventDefault();if(controller.renameTab(editing,candidate))setEditing(null);else setError('Enter 1–80 characters without control characters.');}}><label>Tab name<input autoFocus dir="auto" className="border block" value={candidate} onChange={e=>setCandidate(e.target.value)}/></label>{error&&<p role="alert">{error}</p>}<button className="underline p-2">Save</button><button type="button" className="underline p-2" onClick={()=>setEditing(null)}>Cancel</button><button type="button" className="underline p-2" onClick={()=>{controller.renameTab(editing);setEditing(null);}}>Reset name</button></form></dialog>}
 {controller.pendingRestore&&<dialog ref={restore} aria-label="Choose tab to close and restore" onCancel={()=>controller.cancelRestore()} className="rounded p-4 max-w-[calc(100vw-2rem)]"><p>Choose tab to close and restore. The current arrangement remains displayed.</p>{tabs.map((tab,index)=><button key={tab.tabKey} className="underline block p-2" onClick={()=>controller.restoreReplacing(tab.tabKey)}>Close tab {index+1}: {label(tab)}</button>)}<button autoFocus className="underline p-2" onClick={()=>controller.cancelRestore()}>Cancel</button></dialog>}
 </div>;
}
