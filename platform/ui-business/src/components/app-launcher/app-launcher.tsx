/** Data-driven app switcher. Ships its own styles; no Tailwind setup required. */
import { useState, useRef, useEffect, useId } from "react";
import { LayoutGrid, ChevronDown } from "lucide-react";
import type { AppEntry } from "@platform/app-directory-client";
import { AppLauncherItem } from "./app-launcher-item";
import './app-launcher.css';

interface AppLauncherProps {
  apps: AppEntry[];
  isLoading?: boolean;
  label?: string;
  currentAppId?: string;
  /** Compact trigger; accessible name and touch target are retained. */
  iconOnly?: boolean;
}

export function AppLauncher({apps, isLoading = false, label = 'App launcher', currentAppId, iconOnly = false}: AppLauncherProps) {
  const [open, setOpen] = useState(false);
  const container = useRef<HTMLDivElement>(null);
  const trigger = useRef<HTMLButtonElement>(null);
  const menu = useRef<HTMLDivElement>(null);
  const initialFocus = useRef(0);
  const menuId = useId();
  function closeAndFocus(){setOpen(false);trigger.current?.focus();}
  useEffect(()=>{
    if(!open)return;
    const links=menu.current?.querySelectorAll<HTMLAnchorElement>('[role=menuitem]');
    links?.[initialFocus.current<0?links.length-1:0]?.focus();
    function outside(e:PointerEvent){if(!container.current?.contains(e.target as Node))setOpen(false);}
    document.addEventListener('pointerdown',outside);
    return ()=>document.removeEventListener('pointerdown',outside);
  },[open,isLoading]);
  if(!isLoading&&!apps.length)return null;
  return <div className="platform-app-launcher" ref={container}
    onBlur={e=>{if(!e.currentTarget.contains(e.relatedTarget as Node))setOpen(false);}}
    onKeyDown={e=>{if(e.key==='Escape'&&open){e.preventDefault();e.stopPropagation();closeAndFocus();}}}>
    <button ref={trigger} type="button" className="platform-app-trigger" aria-label={label} title={iconOnly?label:undefined}
      aria-expanded={open} aria-haspopup="menu" aria-controls={open?menuId:undefined}
      onClick={()=>{initialFocus.current=0;setOpen(v=>!v);}}
      onKeyDown={e=>{if(e.key==='ArrowDown'||e.key==='ArrowUp'){e.preventDefault();initialFocus.current=e.key==='ArrowUp'?-1:0;setOpen(true);}}}>
      <LayoutGrid aria-hidden="true"/>{!iconOnly&&<><span>Apps</span><ChevronDown className="platform-app-chevron" aria-hidden="true"/></>}
    </button>
    {open&&<div ref={menu} id={menuId} role="menu" aria-label="Available apps" className="platform-app-menu"
      onKeyDown={e=>{
        const items=Array.from(e.currentTarget.querySelectorAll<HTMLAnchorElement>('[role=menuitem]'));
        const index=items.indexOf(document.activeElement as HTMLAnchorElement);
        let next:number;
        if(e.key==='ArrowDown')next=(index+1)%items.length;
        else if(e.key==='ArrowUp')next=(index-1+items.length)%items.length;
        else if(e.key==='Home')next=0;
        else if(e.key==='End')next=items.length-1;
        else if(e.key==='Tab'){if(e.shiftKey)e.preventDefault();closeAndFocus();return;}
        else return;
        e.preventDefault();items[next]?.focus();
      }}>
      <div className="platform-app-heading">Your apps</div>
      {isLoading?<p className="platform-app-loading" role="status">Loading apps…</p>:
        apps.map(app=><AppLauncherItem key={app.id} app={app} current={app.id===currentAppId} onClose={closeAndFocus}/>)}
      <p className="platform-app-hint">Apps open in a new tab.</p>
    </div>}
  </div>;
}
