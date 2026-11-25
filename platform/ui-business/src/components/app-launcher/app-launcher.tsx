/** Data-driven app switcher. Ships its own styles; no Tailwind setup required. */
import { useState, useRef, useLayoutEffect, useId } from "react";
import { LayoutGrid, ChevronDown } from "lucide-react";
import type { AppEntry } from "@platform/app-directory-client";
import type { LauncherStatus } from "../../hooks/use-current-apps";
import { AppLauncherItem } from "./app-launcher-item";
import './app-launcher.css';

export interface AppLauncherProps {
  status?: LauncherStatus;
  onRetry?: () => void;
  onRefresh?: () => void;
  onSignIn?: () => void;
  apps: AppEntry[];
  isLoading?: boolean;
  label?: string;
  currentAppId?: string;
  /** Compact trigger; accessible name and touch target are retained. */
  iconOnly?: boolean;
}

export function AppLauncher({apps, isLoading = false, label = 'App launcher', currentAppId, iconOnly = false, status, onRetry, onRefresh, onSignIn}: AppLauncherProps) {
  const state=status??(isLoading?'loading':'complete');
  const visibleApps=state==='complete'?apps:[];
  const [open, setOpen] = useState(false);
  const container = useRef<HTMLDivElement>(null);
  const trigger = useRef<HTMLButtonElement>(null);
  const menu = useRef<HTMLDivElement>(null);
  const initialFocus = useRef(0);
  const menuId = useId();
  function closeAndFocus(){setOpen(false);trigger.current?.focus();}
  useLayoutEffect(()=>{
    if(!open)return;
    const links=menu.current?.querySelectorAll<HTMLElement>('[role=menuitem]');
    if(links?.length)links[initialFocus.current<0?links.length-1:0]?.focus();
    else menu.current?.querySelector<HTMLElement>('[role=status]')?.focus();
    function outside(e:PointerEvent){if(!container.current?.contains(e.target as Node))setOpen(false);}
    document.addEventListener('pointerdown',outside);
    return ()=>document.removeEventListener('pointerdown',outside);
  },[open,state,visibleApps.length]);

  return <div className="platform-app-launcher" ref={container}
    onBlur={e=>{if(!e.currentTarget.contains(e.relatedTarget as Node))setOpen(false);}}
    onKeyDown={e=>{if(e.key==='Tab'&&open){if(e.shiftKey)e.preventDefault();closeAndFocus();return;}if(e.key==='Escape'&&open){e.preventDefault();e.stopPropagation();closeAndFocus();}}}>
    <button ref={trigger} type="button" className="platform-app-trigger" aria-label={label} title={iconOnly?label:undefined}
      aria-expanded={open} aria-haspopup="menu" aria-controls={open?menuId:undefined}
      onClick={()=>{initialFocus.current=0;if(!open)onRefresh?.();setOpen(v=>!v);}}
      onKeyDown={e=>{if(e.key==='ArrowDown'||e.key==='ArrowUp'){e.preventDefault();initialFocus.current=e.key==='ArrowUp'?-1:0;if(!open)onRefresh?.();setOpen(true);}}}>
      <LayoutGrid aria-hidden="true"/>{!iconOnly&&<><span>Apps</span><ChevronDown className="platform-app-chevron" aria-hidden="true"/></>}
    </button>
    {open&&<div ref={menu} id={menuId} role="menu" aria-label="Available apps" className="platform-app-menu"
      onKeyDown={e=>{
        const items=Array.from(e.currentTarget.querySelectorAll<HTMLElement>('[role=menuitem]'));
        if(!items.length)return;
        const index=items.indexOf(document.activeElement as HTMLElement);
        let next:number;
        if(e.key==='ArrowDown')next=(index+1)%items.length;
        else if(e.key==='ArrowUp')next=(index-1+items.length)%items.length;
        else if(e.key==='Home')next=0;
        else if(e.key==='End')next=items.length-1;
        else return;
        e.preventDefault();items[next]?.focus();
      }}>
      <div className="platform-app-heading">Your apps</div>
      {state==='loading'&&<p className="platform-app-loading" role="status" tabIndex={0}>Checking your apps…</p>}
      {state==='complete'&&visibleApps.length===0&&<p className="platform-app-loading" role="status" tabIndex={0}>No apps are currently available to your account.</p>}
      {visibleApps.map(app=><AppLauncherItem key={app.id} app={app} current={app.id===currentAppId} onClose={closeAndFocus}/>)}
      {state==='unavailable'&&<><p className="platform-app-loading" role="status" tabIndex={onRetry?undefined:0}>We could not check your apps.</p>{onRetry&&<button type="button" role="menuitem" tabIndex={-1} className="platform-app-action" onClick={onRetry}>Retry</button>}</>}
      {(state==='sign_in_required'||state==='authentication_required')&&<><p className="platform-app-loading" role="status" tabIndex={onSignIn?undefined:0}>{state==='sign_in_required'?'Sign in to see your apps.':'Your session has expired. Sign in again to see your apps.'}</p>{onSignIn&&<button type="button" role="menuitem" tabIndex={-1} className="platform-app-action" onClick={()=>{closeAndFocus();onSignIn();}}>Sign in</button>}</>}
      {state==='access_denied'&&<p className="platform-app-loading" role="status" tabIndex={0}>Your current account cannot access apps.</p>}
      <p className="platform-app-hint">Apps open in a new tab.</p>
    </div>}
  </div>;
}
