import {createContext,useContext,useEffect,useRef,useState,type ReactNode,type SetStateAction,type MutableRefObject} from 'react';
import {useReaderWorkspace} from '@/hooks/useReaderWorkspace';
type Fields=Map<string,unknown>;
type Controller=ReturnType<typeof useReaderWorkspace>;
const Context=createContext<(Controller&{root:React.RefObject<HTMLDivElement|null>;views:Map<string,Fields>;redraw:()=>void;latest:MutableRefObject<Controller>})|null>(null);
export function ReaderWorkspaceProvider({children}:{children:ReactNode}){
 const root=useRef<HTMLDivElement>(null),controller=useReaderWorkspace(root),views=useRef(new Map<string,Fields>()),[,render]=useState(0),latest=useRef(controller);latest.current=controller;
 controller.removed.current=key=>{views.current.delete(key);};
 useEffect(()=>{const live=new Set(controller.tabs.map(tab=>tab.tabKey));for(const key of views.current.keys())if(!live.has(key))views.current.delete(key);for(const key of controller.inherited.current.keys())if(!live.has(key))controller.inherited.current.delete(key);},[controller.tabs]);
 return <Context.Provider value={{...controller,root,views:views.current,redraw:()=>render(n=>n+1),latest}}>{children}</Context.Provider>;
}
export function useWorkspace(){const value=useContext(Context);if(!value)throw Error('ReaderWorkspaceProvider required');return value;}
/** Setters belong to the originating live view, including after an intentional switch. */
export function useTabState<T>(name:string,initial:T|(()=>T),inherit=false):[T,(value:SetStateAction<T>)=>void]{
 const owner=useWorkspace(),key=owner.workspace.tabKey;
 let fields=owner.views.get(key);if(!fields){fields=new Map();owner.views.set(key,fields);}
 if(!fields.has(name)){
  const origin=owner.inherited.current.get(key),source=origin?owner.views.get(origin):undefined;
  fields.set(name,inherit&&source?.has(name)?source.get(name):typeof initial==='function'?(initial as ()=>T)():initial);
 }
 const captured=fields;
 return [fields.get(name) as T,value=>{
  if(owner.views.get(key)!==captured||!owner.latest.current.tabs.some(tab=>tab.tabKey===key))return;
  captured.set(name,typeof value==='function'?(value as (prior:T)=>T)(captured.get(name) as T):value);owner.redraw();
 }];
}
export function useTabRef<T>(name:string,initial:T):MutableRefObject<T>{return useTabState(`ref:${name}`,()=>({current:initial}))[0];}
