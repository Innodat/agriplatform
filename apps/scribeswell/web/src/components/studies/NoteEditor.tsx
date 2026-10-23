import {useLayoutEffect,useRef,useState} from 'react';
import {useStudies} from '@/context/StudiesContext';
import type {NoteValue} from '@/lib/personal-notes';
type Block=NoteValue['document']['blocks'][number];
type Paragraph=Extract<Block,{type:'paragraph'}>;
type Inline=Paragraph['content'][number];
function safeUrl(raw:string){
 try{
  const url=new URL(raw),authority=raw.match(/^https?:\/\/([^/?#]+)/i)?.[1];
  if(!authority||authority.includes('@')||!['http:','https:'].includes(url.protocol)||url.username||url.password||new TextEncoder().encode(raw).length>2048||/[\s\\\u0000-\u001f\u007f-\u009f]/u.test(raw)||/%(?![0-9a-f]{2})|%(?:0[0-9a-f]|1[0-9a-f]|7f|5c)/i.test(raw)||url.port==='0')return false;
  if(/^\d+\.\d+\.\d+\.\d+$/.test(url.hostname)&&authority.replace(/:\d+$/,'')!==url.hostname)return false;
  if(!url.hostname.startsWith('[')&&(url.hostname.length>253||url.hostname.replace(/\.$/,'').split('.').some(label=>! /^[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?$/.test(label))))return false;
  return true;
 }catch{return false;}
}
function appendInline(parent:HTMLElement,inlines:Inline[]){for(const inline of inlines){if(inline.type==='external_link'){if(!safeUrl(inline.url))throw Error();const link=document.createElement('a');link.href=inline.url;link.rel='noopener noreferrer';link.target='_blank';appendInline(link,inline.content);parent.append(link);}else{let node:Node=document.createTextNode(inline.text);for(const mark of [...inline.marks].reverse()){const wrapper=document.createElement(mark==='bold'?'strong':'em');wrapper.append(node);node=wrapper;}parent.append(node);}}}
function paragraph(value:Paragraph){const p=document.createElement('p');p.dir=value.direction;appendInline(p,value.content);if(!p.childNodes.length)p.append(document.createElement('br'));return p;}
function draw(root:HTMLElement,value:NoteValue){const nodes=value.document.blocks.map(block=>{if(block.type==='paragraph')return paragraph(block);const list=document.createElement(block.style==='bullet'?'ul':'ol');for(const item of block.items){const li=document.createElement('li');for(const p of item)li.append(paragraph(p));list.append(li);}return list;});root.replaceChildren(...nodes);}
function inlines(nodes:NodeListOf<ChildNode>|ChildNode[],marks:('bold'|'italic')[]=[],linked=false):Inline[]{
 const result:Inline[]=[];
 for(const node of nodes){if(node.nodeType===Node.TEXT_NODE){const text=node.textContent??'';const scalars=Array.from(text);for(let i=0;i<scalars.length;i+=4096){const chunk=scalars.slice(i,i+4096).join('');if(chunk)result.push({type:'text',text:chunk,marks:[...marks] as Extract<Inline,{type:'text'}>['marks']});}continue;}
  if(!(node instanceof HTMLElement))throw Error();
  const tag=node.tagName;
  if(tag==='BR'){if(node.parentNode?.textContent||node.previousSibling||node.nextSibling)result.push({type:'text',text:'\n',marks:[...marks] as Extract<Inline,{type:'text'}>['marks']});continue;}
  if(['B','STRONG','I','EM','SPAN'].includes(tag)){const next=([...new Set([...marks,...(['B','STRONG'].includes(tag)?['bold' as const]:['I','EM'].includes(tag)?['italic' as const]:[])])]).sort((a)=>a==='bold'?-1:1);result.push(...inlines(node.childNodes,next,linked));}
  else if(tag==='A'&&!linked){const url=node.getAttribute('href')??'';if(!safeUrl(url))throw Error();const content=inlines(node.childNodes,marks,true);if(content.some(n=>n.type!=='text')||!content.length)throw Error();result.push({type:'external_link',url,content:content as Extract<Inline,{type:'text'}>[]});}
  else throw Error();
 }
 return result;
}
function read(root:HTMLElement):NoteValue{
 const direction=(node:HTMLElement,fallback:Paragraph['direction']):Paragraph['direction']=>node.dir==='rtl'?'rtl':node.dir==='ltr'?'ltr':node.dir==='auto'?'auto':fallback;
 function blocksIn(container:HTMLElement,inherited:Paragraph['direction'],insideList=false):Block[]{
  const blocks:Block[]=[];let loose:ChildNode[]=[];const current=direction(container,inherited);
  const flush=()=>{if(loose.length){blocks.push({type:'paragraph',direction:current,content:inlines(loose)});loose=[];}};
  for(const node of container.childNodes){
   if(node instanceof HTMLElement&&['P','DIV','UL','OL'].includes(node.tagName)){
    flush();
    if(['UL','OL'].includes(node.tagName)){
     if(insideList)throw Error();
     const items:Paragraph[][]=[];
     for(const li of node.children){if(!(li instanceof HTMLElement)||li.tagName!=='LI')throw Error();const children=blocksIn(li,current,true);if(children.some(b=>b.type!=='paragraph'))throw Error();items.push(children.length?children as Paragraph[]:[{type:'paragraph',direction:current,content:[]}]);}
     if(items.length)blocks.push({type:'list',style:node.tagName==='UL'?'bullet':'ordered',items});
    }else if(node.querySelector('p,div,ul,ol'))blocks.push(...blocksIn(node,current,insideList));
    else blocks.push({type:'paragraph',direction:direction(node,current),content:inlines(node.childNodes)});
   }else loose.push(node);
  }
  flush();return blocks;
 }
 return {document:{version:1,blocks:blocksIn(root,'auto')},connections:[],highlights:[]};
}
export function NoteEditor(){
 const studies=useStudies(),lane=studies.lane,root=useRef<HTMLDivElement>(null);const [invalid,setInvalid]=useState(false),[link,setLink]=useState(''),[linking,setLinking]=useState(false),[linkError,setLinkError]=useState(''),[direction,setDirection]=useState('auto');const selection=useRef<Range|null>(null);
 useLayoutEffect(()=>{setInvalid(false);setLink('');setLinking(false);setLinkError('');selection.current=null;setDirection('auto');if(root.current)root.current.dir='auto';if(root.current&&lane)try{draw(root.current,lane.value);}catch{setInvalid(true);studies.invalidInput();}},[lane?.note.id]);
 if(!lane)return <p className="p-4">Select a note in Studies.</p>;
 function changed(){if(!root.current)return;try{studies.change(read(root.current));setInvalid(false);}catch{setInvalid(true);studies.invalidInput();}}
 function format(command:string){root.current?.focus();document.execCommand(command,false);changed();}
 return <section aria-label="Note editor" className="p-3 space-y-3">
  <h3 className="font-semibold">Notes</h3><p className="text-sm">{studies.study?.title}</p>
  <div role="toolbar" aria-label="Note formatting" className="flex flex-wrap gap-2 text-sm">
   <button onMouseDown={e=>e.preventDefault()} onClick={()=>format('bold')} aria-label="Bold" className="border rounded px-2 font-bold">B</button>
   <button onMouseDown={e=>e.preventDefault()} onClick={()=>format('italic')} aria-label="Italic" className="border rounded px-2 italic">I</button>
   <button onMouseDown={e=>e.preventDefault()} onClick={()=>format('insertUnorderedList')} className="border rounded px-2">Bullet list</button>
   <button onMouseDown={e=>e.preventDefault()} onClick={()=>format('insertOrderedList')} className="border rounded px-2">Numbered list</button>
   <button onMouseDown={e=>e.preventDefault()} onClick={()=>{const selected=window.getSelection();const range=selected?.rangeCount?selected.getRangeAt(0):null;selection.current=range&&root.current?.contains(range.commonAncestorContainer)?range.cloneRange():null;setLinkError('');setLinking(true);}} className="border rounded px-2">Link</button>
   <label>Direction <select aria-label="Paragraph direction" value={direction} onChange={e=>{setDirection(e.target.value);const selected=window.getSelection();const element=selected?.anchorNode?.parentElement?.closest('p,div[dir]');if(element&&root.current?.contains(element)){element.setAttribute('dir',e.target.value);changed();}else if(root.current){root.current.dir=e.target.value;changed();}}}><option value="auto">Auto</option><option value="ltr">Left to right</option><option value="rtl">Right to left</option></select></label>
  </div>
  {linking&&<form onSubmit={e=>{e.preventDefault();if(!safeUrl(link)){setLinkError('Enter a valid HTTP or HTTPS link with a valid hostname.');return;}if(!selection.current||!root.current?.contains(selection.current.commonAncestorContainer)){setLinkError('Select text in this note, then insert the link.');return;}root.current?.focus();if(selection.current){const selected=window.getSelection();selected?.removeAllRanges();selected?.addRange(selection.current);document.execCommand('createLink',false,link);}changed();setLinking(false);setLink('');setLinkError('');selection.current=null;}}><label>Link URL<input value={link} onChange={e=>{setLink(e.target.value);setLinkError('');}} className="border w-full" /></label>{linkError&&<p role="alert">{linkError}</p>}<button type="submit" className="underline m-2">Insert link</button><button type="button" className="underline" onClick={()=>setLinking(false)}>Cancel</button></form>}
  <div key={lane.note.id} ref={root} role="textbox" aria-label="Note text" aria-multiline="true" contentEditable suppressContentEditableWarning dir="auto" className="min-h-48 rounded border border-stone-300 bg-white p-3 outline-amber-600 whitespace-pre-wrap [&_ul]:list-disc [&_ol]:list-decimal [&_li]:ml-5 [&_p]:min-h-6 [&_a]:underline" onInput={changed} onCompositionStart={()=>studies.composition(true)} onCompositionEnd={()=>{changed();studies.composition(false);}} onPaste={e=>{e.preventDefault();document.execCommand('insertText',false,e.clipboardData.getData('text/plain'));changed();}} onDrop={e=>e.preventDefault()} onClick={e=>{if((e.target as HTMLElement).closest('a'))e.preventDefault();}} />
  <p role="status" aria-live="polite">{invalid||lane.status==='failed'||lane.status==='conflict'?'Changes not saved':lane.status==='saved'?'Draft saved':'Saving…'} {(lane.status==='failed'||invalid)&&<button className="underline" onClick={()=>{if(invalid)changed();else void studies.retry();}}>Retry</button>}</p>
  {lane.status==='conflict'&&<p role="alert">This note has changed. Your input is kept here. Return to Studies to reopen the latest saved note.</p>}
  <button className="underline" onClick={()=>studies.setTool('studies')}>Back to Studies</button>
 </section>;
}
