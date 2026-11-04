import {useEffect,useId,useRef,useState,type ReactNode,type RefObject} from 'react';

/** A disclosure of ordinary buttons: Tab keeps its native order. */
export function ActionDisclosure({label,children,triggerRef,compact=false}:{label:string;children:ReactNode;triggerRef?:RefObject<HTMLButtonElement|null>;compact?:boolean}){
 const contentId=useId();
 const [open,setOpen]=useState(false),root=useRef<HTMLDivElement>(null),local=useRef<HTMLButtonElement>(null),trigger=triggerRef??local;
 useEffect(()=>{if(!open)return;const outside=(event:PointerEvent)=>{if(!root.current?.contains(event.target as Node))setOpen(false);};document.addEventListener('pointerdown',outside);return()=>document.removeEventListener('pointerdown',outside);},[open]);
 return <div ref={root} className={`sw-disclosure ${compact?'sw-disclosure-end':''}`} onKeyDown={event=>{if(open&&event.key==='Escape'){event.preventDefault();event.stopPropagation();setOpen(false);trigger.current?.focus();}}} onBlur={event=>{if(!event.currentTarget.contains(event.relatedTarget as Node|null))setOpen(false);}}>
  <button ref={trigger} type="button" className="sw-button sw-secondary" aria-label={label} title={compact?label:undefined} aria-controls={contentId} aria-expanded={open} onClick={()=>setOpen(!open)}>{compact?<span aria-hidden="true">•••</span>:<>{label}<span aria-hidden="true">⌄</span></>}</button>
  <div id={contentId} hidden={!open} className="sw-action-list" onClickCapture={event=>{if((event.target as HTMLElement).closest('button:not(:disabled)')){setOpen(false);trigger.current?.focus({preventScroll:true});}}}>{children}</div>
 </div>;
}
