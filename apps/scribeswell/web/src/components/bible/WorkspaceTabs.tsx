import {useEffect,useRef,useState} from 'react';
import {Pencil,Plus,X} from 'lucide-react';
import {useStudies} from '@/context/StudiesContext';
import {useWorkspace} from '@/context/ReaderWorkspaceContext';
import {workspaceTabId} from '@/lib/reader-layout';
import {referenceLabel} from '@/lib/passage-references';
export function WorkspaceTabs(){
 const studies=useStudies(),controller=useWorkspace(),{workspace,tabs}=controller;
 const [focus,setFocus]=useState(workspace.tabKey),[editing,setEditing]=useState<string|null>(null),[candidate,setCandidate]=useState(''),[error,setError]=useState('');
 const rename=useRef<HTMLDialogElement>(null),restore=useRef<HTMLDialogElement>(null),device=useRef<HTMLDialogElement>(null);
 useEffect(()=>{setFocus(workspace.tabKey);document.getElementById(workspaceTabId(workspace.tabKey))?.scrollIntoView({block:'nearest',inline:'nearest'});},[workspace.tabKey]);
 useEffect(()=>{if(editing&&!studies.searchMasked)rename.current?.showModal();},[editing,studies.searchMasked]);
 useEffect(()=>{if(controller.devicePending&&device.current){if(!device.current.open)device.current.showModal();else if(document.activeElement===document.body)device.current.querySelector<HTMLElement>('button')?.focus({preventScroll:true});}},[controller.devicePending]);
 useEffect(()=>{if(controller.pendingRestore)restore.current?.showModal();},[controller.pendingRestore]);
 const label=(tab:typeof workspace)=>(!studies.searchMasked?tab.label:undefined)??`${referenceLabel(tab.panes[0].ref,'hebrew')}${tab.panes.length>1?` +${tab.panes.length-1}`:''}`;
 function move(event:React.KeyboardEvent,index:number){
  const next=event.key==='Home'?0:event.key==='End'?tabs.length-1:event.key==='ArrowLeft'?(index+tabs.length-1)%tabs.length:event.key==='ArrowRight'?(index+1)%tabs.length:undefined;
  if(next===undefined)return;event.preventDefault();setFocus(tabs[next].tabKey);const node=document.getElementById(workspaceTabId(tabs[next].tabKey));node?.focus();node?.scrollIntoView({block:'nearest',inline:'nearest'});
 }
 return <div className="shrink-0 min-w-0">
 <div className="flex min-w-0 items-center gap-1 border-b border-stone-200 pb-2">
 <div role="tablist" data-device-ready={controller.deviceReady} aria-label="Workspace tabs" className="flex min-w-0 max-w-full overflow-x-auto gap-1 items-center py-1">
 {tabs.map((tab,index)=><div key={tab.tabKey} className={`group flex shrink-0 items-center rounded-lg border transition-colors ${workspace.tabKey===tab.tabKey?'border-amber-300 bg-amber-50 text-amber-950 shadow-sm':'border-transparent text-stone-500 hover:bg-stone-100'}`}>
 <button role="tab" id={workspaceTabId(tab.tabKey)} data-workspace-tab={tab.tabKey} aria-controls="workspace-panel" aria-selected={workspace.tabKey===tab.tabKey} tabIndex={focus===tab.tabKey?0:-1} onFocus={()=>setFocus(tab.tabKey)} onKeyDown={e=>move(e,index)} className="px-3 py-2 max-w-44 truncate text-sm font-medium rounded-lg focus-visible:outline-2 focus-visible:outline-amber-600" dir="auto" onClick={()=>controller.activateTab(tab.tabKey)}>{label(tab)}</button>
 <button disabled={studies.searchMasked} aria-describedby={studies.searchMasked?'rename-access-reason':undefined} className="tab-rename inline-flex size-7 shrink-0 items-center justify-center rounded-md text-stone-400 hover:bg-stone-100 hover:text-stone-700 focus-visible:outline-2 focus-visible:outline-amber-600 disabled:opacity-40" title="Rename tab" aria-label={`Rename tab ${index+1}`} onClick={()=>{setEditing(tab.tabKey);setCandidate(tab.label??'');setError('');}}><Pencil size={13} aria-hidden="true"/></button>
 {tabs.length>1&&<button data-close-tab className="inline-flex size-7 shrink-0 items-center justify-center rounded-md mr-1 text-stone-400 hover:bg-stone-200 hover:text-stone-800 focus-visible:outline-2 focus-visible:outline-amber-600" title="Close tab" aria-label={`Close tab ${index+1}`} onClick={()=>controller.closeTab(tab.tabKey)}><X size={14} aria-hidden="true"/></button>}
 </div>)}
 </div>
 <button className="inline-flex size-9 shrink-0 items-center justify-center rounded-lg text-stone-500 hover:bg-stone-200 hover:text-stone-900 focus-visible:outline-2 focus-visible:outline-amber-600" title="New tab" aria-label="New workspace tab" onClick={()=>controller.newTab()}><Plus size={18} aria-hidden="true"/></button>
 </div>
 {studies.searchMasked&&<span id="rename-access-reason" className="sr-only">Sign in and restore Studies access to rename tabs.</span>}
 {controller.historyHeld&&!controller.pendingRestore&&<p role="status">The current arrangement remains displayed. <button className="underline" onClick={controller.retryRestore}>Choose tab to close and restore</button></p>}
 {controller.storageNotice&&<p role="status">{controller.storageNotice} <button className="underline" onClick={controller.retryStorage}>Retry</button></p>}
 {controller.devicePending&&<dialog ref={device} aria-label="Restore remembered reading setups" onCancel={()=>controller.cancelDevice()} className="sw-dialog"><p>The current setup remains displayed. {controller.devicePending.union.length>12?'Choose tabs to close until the remembered reading setups fit.':'Restore remembered reading setups alongside the current setup?'}</p>{controller.devicePending.union.length>12?controller.devicePending.union.map((tab,index)=>tab.tabKey!==controller.devicePending!.active&&<button key={tab.tabKey} className="underline block p-2" onClick={()=>controller.chooseDeviceVictim(tab.tabKey)}>Close {tabs.some(live=>live.tabKey===tab.tabKey)?'current':'remembered'} tab {index+1}: {referenceLabel(tab.panes[0].ref)}</button>):<button className="underline p-2" onClick={controller.acceptDevice}>Restore setups</button>}<button autoFocus className="underline p-2" onClick={()=>controller.cancelDevice()}>Cancel</button></dialog>}
 {controller.notice&&<p role="status">{controller.notice}</p>}
 {editing&&!studies.searchMasked&&<dialog ref={rename} aria-label="Rename workspace tab" onCancel={()=>setEditing(null)} className="m-auto w-80 max-w-[calc(100vw-2rem)] rounded-xl border border-stone-200 bg-white p-5 shadow-xl backdrop:bg-stone-900/20"><form onSubmit={e=>{e.preventDefault();if(controller.renameTab(editing,candidate))setEditing(null);else setError('Enter 1–80 characters without control characters.');}}><label className="text-sm font-medium text-stone-800">Tab name<input autoFocus dir="auto" className="mt-2 block w-full rounded-lg border border-stone-300 px-3 py-2 text-sm focus-visible:outline-2 focus-visible:outline-amber-600" value={candidate} onChange={e=>setCandidate(e.target.value)}/></label>{error&&<p role="alert" className="mt-2 text-sm text-red-700">{error}</p>}<div className="mt-4 flex items-center gap-2 text-sm"><button type="button" className="mr-auto rounded-lg px-2 py-2 text-stone-500 hover:bg-stone-100" onClick={()=>{controller.renameTab(editing);setEditing(null);}}>Reset name</button><button type="button" className="rounded-lg px-3 py-2 text-stone-600 hover:bg-stone-100" onClick={()=>setEditing(null)}>Cancel</button><button className="rounded-lg bg-amber-700 px-3 py-2 font-medium text-white hover:bg-amber-800">Save</button></div></form></dialog>}
 {controller.pendingRestore&&<dialog ref={restore} aria-label="Choose tab to close and restore" onCancel={()=>controller.cancelRestore()} className="sw-dialog"><p>Choose tab to close and restore. The current arrangement remains displayed.</p>{tabs.map((tab,index)=><button key={tab.tabKey} className="underline block p-2" onClick={()=>controller.restoreReplacing(tab.tabKey)}>Close tab {index+1}: {label(tab)}</button>)}<button autoFocus className="underline p-2" onClick={()=>controller.cancelRestore()}>Cancel</button></dialog>}
 </div>;
}
