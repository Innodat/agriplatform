import {useId,useLayoutEffect,useRef,useState,type ReactNode} from 'react';
import {createPortal} from 'react-dom';
import './task-surface.css';
const focusable='button:not(:disabled),a[href],input:not(:disabled),select:not(:disabled),textarea:not(:disabled),[tabindex="0"]';
/** Stable task mount; responsive presentation never remounts the caller's form. */
export function TaskSurface({title,onClose,children,footer,headerContent,confirmation,closeLabel='Close',backLabel='Back'}:{title:string;onClose:()=>void;children:ReactNode;footer:ReactNode;headerContent?:ReactNode;confirmation?:ReactNode;closeLabel?:string;backLabel?:string}){
 const root=useRef<HTMLDivElement>(null),heading=useRef<HTMLHeadingElement>(null),[narrow,setNarrow]=useState(()=>matchMedia('(max-width: 48rem)').matches);
 const close=useRef(onClose);close.current=onClose;
 useLayoutEffect(()=>{
  const opener=document.activeElement instanceof HTMLElement?document.activeElement:null,element=root.current!;
  const ancestors=[...document.body.children].filter(child=>child!==element&&child instanceof HTMLElement) as HTMLElement[];
  const previous=ancestors.map(child=>child.inert);for(const child of ancestors)child.inert=true;
  const overflow=document.body.style.overflow;document.body.style.overflow='hidden';heading.current?.focus();
  return()=>{document.body.style.overflow=overflow;ancestors.forEach((child,index)=>child.inert=previous[index]!);requestAnimationFrame(()=>{const focused=document.activeElement;if(focused&&focused!==document.body&&focused!==document.documentElement)return;if(opener?.isConnected&&!opener.closest('[inert]'))opener.focus();else{const fallback=document.querySelector<HTMLElement>('[data-task-return],main h1');if(fallback){fallback.tabIndex=-1;fallback.focus();}}});};
 },[]);
 useLayoutEffect(()=>{const media=matchMedia('(max-width: 48rem)'),change=()=>setNarrow(media.matches);media.addEventListener('change',change);return()=>media.removeEventListener('change',change);},[]);
 useLayoutEffect(()=>{const viewport=window.visualViewport,resize=()=>{root.current?.style.setProperty('--task-height',`${viewport?.height??window.innerHeight}px`);root.current?.style.setProperty('--task-top',`${viewport?.offsetTop??0}px`);};resize();viewport?.addEventListener('resize',resize);viewport?.addEventListener('scroll',resize);return()=>{viewport?.removeEventListener('resize',resize);viewport?.removeEventListener('scroll',resize);};},[]);
 return createPortal(<div className="task-overlay" ref={root} onKeyDown={event=>{
  if(event.key==='Escape'){event.preventDefault();event.stopPropagation();if(!confirmation)close.current();}
  if(event.key==='Tab'&&(!narrow||confirmation)){
   const area=confirmation?root.current?.querySelector('[role="alertdialog"]'):root.current;
   const items=[...(area?.querySelectorAll<HTMLElement>(focusable)??[])].filter(el=>el.getClientRects().length&&!el.closest('[inert]'));
   if(!items.length){event.preventDefault();if(confirmation)area?.querySelector<HTMLElement>('[tabindex="-1"]')?.focus();else heading.current?.focus();return;}
   if(event.shiftKey&&(!items.includes(document.activeElement as HTMLElement)||document.activeElement===items[0])){event.preventDefault();items.at(-1)?.focus();}
   else if(!event.shiftKey&&(!area?.contains(document.activeElement)||document.activeElement===items.at(-1))){event.preventDefault();items[0]?.focus();}
  }
 }}><section className={'task-surface'+(narrow?' task-page':'')} role={narrow?'region':'dialog'} aria-modal={narrow?undefined:true} aria-labelledby="task-title">
 <header className="task-header" inert={!!confirmation}><h2 id="task-title" ref={heading} tabIndex={-1}>{title}</h2><button type="button" onClick={onClose} aria-label={narrow?backLabel:closeLabel}>{narrow?'Back':'×'}</button>{headerContent&&<div className="task-header-content">{headerContent}</div>}</header>
 <div className="task-body" inert={!!confirmation}>{children}</div><footer className="task-footer" inert={!!confirmation}>{footer}</footer>{confirmation}
 </section></div>,document.body);
}
export function DraftSaveStatus({status,retry}:{status:'saved'|'dirty'|'saving'|'failed';retry:()=>void}){
 const [announcement,setAnnouncement]=useState(''),hadFailure=useRef(false);
 useLayoutEffect(()=>{if(status==='failed'){hadFailure.current=true;setAnnouncement('Changes not saved.');}else if(hadFailure.current&&status==='saved'){hadFailure.current=false;setAnnouncement('Draft saved.');}},[status]);
 return <><span className="draft-save-status">{status==='saved'?'Draft saved':status==='saving'?'Saving…':status==='failed'?'Changes not saved':'Unsaved changes'}</span>{status==='failed'&&<button type="button" onClick={retry}>Retry</button>}<span className="task-sr-only" role="status">{announcement}</span></>;
}
export function DraftExitConfirmation({
 stay,leave,question='Your latest changes may not be saved. Close anyway?',leaveLabel='Close anyway',stayLabel='Stay',description,destructive=false,
}:{stay?:()=>void;leave?:()=>void;question?:string;leaveLabel?:string;stayLabel?:string;description?:string;destructive?:boolean}){
 const label=useId(),details=useId(),safeButton=useRef<HTMLButtonElement>(null),action=useRef<HTMLButtonElement>(null),summary=useRef<HTMLParagraphElement>(null);
 useLayoutEffect(()=>{(safeButton.current??action.current??summary.current)?.focus();},[question]);
 return <div className="task-confirmation" role="alertdialog" aria-modal="true" aria-labelledby={label} aria-describedby={description?details:undefined}>
  <p id={label} ref={summary} tabIndex={-1}>{question}</p>
  {description&&<p id={details}>{description}</p>}
  {stay&&<button type="button" ref={safeButton} onClick={stay}>{stayLabel}</button>}
  {leave&&<button type="button" ref={action} data-destructive={destructive||undefined} onClick={leave}>{leaveLabel}</button>}
 </div>;
}
