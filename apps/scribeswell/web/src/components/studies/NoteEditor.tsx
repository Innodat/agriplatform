import {useLayoutEffect,useRef,useState} from 'react';
import {useWorkspace,useTabState} from '@/context/ReaderWorkspaceContext';
import {type Lane,SavedNoteReview,useStudies} from '@/context/StudiesContext';
import {BookChapterSelector} from '@/components/bible/book-chapter-selector';
import {referenceLabel,validateReference,type PassageReference} from '@/lib/passage-references';
import type {NoteValue} from '@/lib/personal-notes';
import {aggregate,noteReferences} from '@/lib/own-highlights';
import {safeNoteUrl as safeUrl} from '@/lib/note-value';
type Block=NoteValue['document']['blocks'][number];
type Paragraph=Extract<Block,{type:'paragraph'}>;
type Inline=Paragraph['content'][number];

type PassageInline=Extract<Inline,{type:'passage_link'}>;
// Only nodes constructed by this editor carry authority; pasted/foreign metadata does not.
const passageNodes=new WeakMap<HTMLElement,PassageInline>();
// Native Undo/Redo rebuilds DOM nodes. Tokens identify only this editor's own
// immutable atoms; ordinary input never gains ownership from a copied token.
const passageRegistry=new WeakMap<HTMLElement,Map<string,PassageInline>>();
function registry(root:HTMLElement){let entries=passageRegistry.get(root);if(!entries){entries=new Map();passageRegistry.set(root,entries);}return entries;}
function bindNativeAtoms(root:HTMLElement){const entries=registry(root),seen=new Set<string>();for(const node of root.querySelectorAll<HTMLElement>('[data-note-passage]')){const token=node.dataset.notePassage??'',inline=entries.get(token);if(!inline||seen.has(token))throw Error();seen.add(token);passageNodes.set(node,inline);passageValue(node);}}

function validLabel(label:string){return typeof label==='string'&&Array.from(label).length>0&&Array.from(label).length<=200&&!/[\u0000\uD800-\uDFFF]/u.test(label);}
function passageNode(inline:PassageInline,owner:HTMLElement){
 if(Object.keys(inline).sort().join(',')!=='label,reference,type'||inline.type!=='passage_link'||!validateReference(inline.reference)||!validLabel(inline.label))throw Error();
 const node=document.createElement('span');node.dataset.notePassage=crypto.randomUUID();node.dir='auto';node.style.unicodeBidi='isolate';node.contentEditable='false';node.setAttribute('role','link');node.tabIndex=0;node.className='underline text-amber-900 cursor-pointer';node.textContent=inline.label;const stored=structuredClone(inline);passageNodes.set(node,stored);registry(owner).set(node.dataset.notePassage!,stored);return node;
}
function passageValue(node:HTMLElement){const inline=passageNodes.get(node);if(!inline||!validateReference(inline.reference)||!validLabel(inline.label)||node.textContent!==inline.label||node.childNodes.length!==1||node.firstChild?.nodeType!==Node.TEXT_NODE||node.contentEditable!=='false')throw Error();return structuredClone(inline);}
function appendInline(parent:HTMLElement,inlines:Inline[],owner:HTMLElement){for(const inline of inlines){if(inline.type==='passage_link'){parent.append(passageNode(inline,owner));}else if(inline.type==='external_link'){if(!safeUrl(inline.url))throw Error();const link=document.createElement('a');link.href=inline.url;link.rel='noopener noreferrer';link.target='_blank';appendInline(link,inline.content,owner);parent.append(link);}else{let node:Node=document.createTextNode(inline.text);for(const mark of [...inline.marks].reverse()){const wrapper=document.createElement(mark==='bold'?'strong':'em');wrapper.append(node);node=wrapper;}parent.append(node);}}}
function paragraph(value:Paragraph,owner:HTMLElement){const p=document.createElement('p');p.dir=value.direction;appendInline(p,value.content,owner);if(!p.childNodes.length)p.append(document.createElement('br'));return p;}
function draw(root:HTMLElement,value:NoteValue){passageRegistry.set(root,new Map());if(![1,2].includes(value.document.version))throw Error();const nodes=value.document.blocks.map(block=>{if(block.type==='paragraph')return paragraph(block,root);const list=document.createElement(block.style==='bullet'?'ul':'ol');for(const item of block.items){const li=document.createElement('li');for(const p of item)li.append(paragraph(p,root));list.append(li);}return list;});root.replaceChildren(...nodes);}
function inlines(nodes:NodeListOf<ChildNode>|ChildNode[],marks:('bold'|'italic')[]=[],linked=false):Inline[]{
 const result:Inline[]=[];
 for(const node of nodes){if(node.nodeType===Node.TEXT_NODE){const text=node.textContent??'';if(/[\u0000\uD800-\uDFFF]/u.test(text))throw Error();const scalars=Array.from(text);for(let i=0;i<scalars.length;i+=4096){const chunk=scalars.slice(i,i+4096).join('');if(chunk)result.push({type:'text',text:chunk,marks:[...marks] as Extract<Inline,{type:'text'}>['marks']});}continue;}
  if(!(node instanceof HTMLElement))throw Error();
  const tag=node.tagName;
  if(node.hasAttribute('data-note-passage')){if(linked)throw Error();result.push(passageValue(node));continue;}
  if(node.contentEditable==='false'||node.hasAttribute('data-reference'))throw Error();
  if(tag==='BR'){if(node.parentNode?.textContent||node.previousSibling||node.nextSibling)result.push({type:'text',text:'\n',marks:[...marks] as Extract<Inline,{type:'text'}>['marks']});continue;}
  if(['B','STRONG','I','EM','SPAN'].includes(tag)){const next=([...new Set([...marks,...(['B','STRONG'].includes(tag)?['bold' as const]:['I','EM'].includes(tag)?['italic' as const]:[])])]).sort((a)=>a==='bold'?-1:1);result.push(...inlines(node.childNodes,next,linked));}
  else if(tag==='A'&&!linked){const url=node.getAttribute('href')??'';if(!safeUrl(url))throw Error();const content=inlines(node.childNodes,marks,true);if(content.some(n=>n.type!=='text')||!content.length)throw Error();result.push({type:'external_link',url,content:content as Extract<Inline,{type:'text'}>[]});}
  else throw Error();
 }
 return result;
}
function read(root:HTMLElement,version:1|2,base:NoteValue):NoteValue{
 const tokens=[...root.querySelectorAll<HTMLElement>('[data-note-passage]')].map(n=>n.dataset.notePassage);if(new Set(tokens).size!==tokens.length)throw Error();
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
 const blocks=blocksIn(root,'auto'),paragraphs=blocks.flatMap(block=>block.type==='paragraph'?[block]:block.items.flat());
 if(blocks.length>256||blocks.some(block=>block.type==='list'&&(block.items.length>128||block.items.some(item=>!item.length||item.length>16)))||paragraphs.some(p=>p.content.length>256))throw Error();
 let text=0,nodes=1;
 const count=(v:unknown)=>{if(Array.isArray(v)){v.forEach(count);}else if(v&&typeof v==='object'){nodes++;const item=v as Record<string,unknown>;if(item.type==='text')text+=Array.from(item.text as string).length;if(item.type==='passage_link')text+=Array.from(item.label as string).length;Object.values(item).forEach(count);}};blocks.forEach(count);
 if(nodes>2048||text>50000)throw Error();
 if(version===1&&paragraphs.some(p=>p.content.some(i=>i.type==='passage_link')))throw Error();
 return {...base,document:{version,blocks}};
}
export function NoteEditor({onOpen}:{onOpen?:(reference:PassageReference)=>void}){
 const studies=useStudies();
 return <>{!studies.lane&&<p data-note-empty-state tabIndex={-1} className="p-4">Select a note in Studies.</p>}{studies.editorLanes.map(lane=><div key={`${studies.accountKey}:${lane.note.id}`} hidden={lane!==studies.lane} inert={lane!==studies.lane}><BoundNoteEditor bound={lane} onOpen={onOpen}/></div>)}</>;
}
function BoundNoteEditor({bound,onOpen}:{bound:Lane;onOpen?:(reference:PassageReference)=>void}){
 const studies=useStudies(),lane=bound,root=useRef<HTMLDivElement>(null),picker=useRef<HTMLDivElement>(null);
 const owner=useWorkspace(),tab=owner.workspace.tabKey;
 const exposed=studies.lane===lane&&studies.tool==='analysis'&&studies.analysisTab==='Notes';
 const [scrollPosition,setScrollPosition]=useTabState<{note:string;scroll:number}|null>('noteScroll',null);
 const [reading,setReading]=useState(false),[passageError,setPassageError]=useState(''),[offered,setOffered]=useState<PassageInline|null>(null);
 const inputGeneration=useRef(0),version=useRef<1|2>(1),latest=useRef({lane,account:studies.accountKey,tab,exposed});latest.current={lane,account:studies.accountKey,tab,exposed};
 const insertion=useRef<{lane:typeof lane;account:string;generation:number;range:Range|null}|null>(null);
 const composing=useRef(false),nativeEditing=useRef(false),readSelection=useRef<Range|null>(null);
 const retainedSelection=useRef<{lane:typeof lane;account:string;generation:number;range:Range}|null>(null);
 const pointerFocus=useRef(false);
 function rememberSelection(){
  const selected=window.getSelection(),range=selected?.rangeCount?selected.getRangeAt(0):null;
  if(!latest.current.lane||!range||!root.current?.contains(range.startContainer)||!root.current.contains(range.endContainer))return;
  retainedSelection.current={...latest.current,generation:inputGeneration.current,range:range.cloneRange()};
 }
 function restoreSelection(){
  const saved=retainedSelection.current;
  if(pointerFocus.current){pointerFocus.current=false;return;}
  if(reading||!saved||saved.lane!==latest.current.lane||saved.account!==latest.current.account||saved.generation!==inputGeneration.current||
     !root.current?.contains(saved.range.startContainer)||!root.current.contains(saved.range.endContainer))return;
  const selected=window.getSelection();selected?.removeAllRanges();selected?.addRange(saved.range.cloneRange());
 }
 useLayoutEffect(()=>{
  const beforeFocus=(event:PointerEvent)=>{if(!root.current?.contains(event.target as Node))rememberSelection();};
  document.addEventListener('selectionchange',rememberSelection);
  document.addEventListener('pointerdown',beforeFocus,true);
  return()=>{document.removeEventListener('selectionchange',rememberSelection);document.removeEventListener('pointerdown',beforeFocus,true);};
 },[]);
 const [invalid,setInvalid]=useState(false),[link,setLink]=useState(''),[linking,setLinking]=useState(false),[linkError,setLinkError]=useState(''),[direction,setDirection]=useState('auto');const selection=useRef<Range|null>(null);
 useLayoutEffect(()=>{composing.current=lane?.composing??false;setReading(false);setOffered(null);setPassageError('');insertion.current=null;retainedSelection.current=null;pointerFocus.current=false;inputGeneration.current++;version.current=lane?.value.document.version===2?2:1;setInvalid(false);setLink('');setLinking(false);setLinkError('');selection.current=null;setDirection('auto');if(root.current)root.current.dir='auto';if(root.current&&lane)try{draw(root.current,lane.value);read(root.current,version.current,lane.value);}catch{setInvalid(true);studies.invalidInput(lane); }},[lane]);
 useLayoutEffect(()=>{
  const scroll=root.current?.closest<HTMLElement>('[data-inspector-scroll]');if(!scroll||!isExposed())return;
  scroll.scrollTop=scrollPosition?.note===lane.note.id?scrollPosition.scroll:0;
  const remember=()=>{if(isExposed())setScrollPosition({note:lane.note.id,scroll:scroll.scrollTop});};
  scroll.addEventListener('scroll',remember);return()=>scroll.removeEventListener('scroll',remember);
 },[tab,exposed,lane]);
 useLayoutEffect(()=>{const editor=root.current;if(!editor)return;const before=(event:InputEvent)=>{
  if(!event.isTrusted||event.isComposing||composing.current||nativeEditing.current)return;
  if(event.inputType==='deleteContentBackward'||event.inputType==='deleteContentForward'){
   const atom=deletionAtom(event.inputType==='deleteContentBackward');if(!atom)return;
   event.preventDefault();const range=document.createRange();range.selectNode(atom);const selected=window.getSelection();selected?.removeAllRanges();selected?.addRange(range);nativeCommand('delete');
  }else if(event.inputType.startsWith('insert'))prepareTyping();
 };editor.addEventListener('beforeinput',before);return()=>editor.removeEventListener('beforeinput',before);},[lane]);
 if(!lane)return <p data-note-empty-state tabIndex={-1} className="p-4">Select a note in Studies.</p>;
 function changed(event?:{nativeEvent:Event}){if(lane?.deletion?.attempt)return false;inputGeneration.current++;const saved=retainedSelection.current;if(saved&&root.current?.contains(saved.range.startContainer)&&root.current.contains(saved.range.endContainer))saved.generation=inputGeneration.current;setOffered(null);if(!root.current)return false;try{if(nativeEditing.current||event?.nativeEvent.isTrusted&&['historyUndo','historyRedo'].includes((event.nativeEvent as InputEvent).inputType))bindNativeAtoms(root.current);studies.change(read(root.current,version.current,lane.value),lane);setInvalid(false);return true;}catch{setInvalid(true);studies.invalidInput(lane);return false;}}
 function nativeCommand(command:string,value?:string){if(lane?.deletion?.attempt)return false;const editor=root.current;if(!editor)return false;try{read(editor,version.current,lane.value);nativeEditing.current=true;editor.focus();if(command==='insertText')prepareTyping();const accepted=document.execCommand(command,false,value);bindNativeAtoms(editor);return changed()&&accepted;}catch{setInvalid(true);studies.invalidInput(lane);return false;}finally{nativeEditing.current=false;}}

 function captureInsertion(){
  const selected=window.getSelection(),range=selected?.rangeCount?selected.getRangeAt(0):null;
  insertion.current={lane,account:studies.accountKey,generation:inputGeneration.current,range:range&&root.current?.contains(range.commonAncestorContainer)?range.cloneRange():null};setPassageError('');
 }
 function pickerHasFocus(){return document.activeElement===picker.current?.querySelector('button[aria-label="Insert passage reference"]');}
 function editableCaret(range:Range){
  if(!range.collapsed)return range;
  const inside=(range.startContainer instanceof HTMLElement?range.startContainer:range.startContainer.parentElement)?.closest<HTMLElement>('[data-note-passage]');
  if(inside){passageValue(inside);range.setStartAfter(inside);range.collapse(true);}
  const container=range.startContainer,previous=container.childNodes[range.startOffset-1];
  if(container instanceof HTMLElement&&previous instanceof HTMLElement&&previous.hasAttribute('data-note-passage')){
   passageValue(previous);let text=previous.nextSibling;if(text?.nodeType!==Node.TEXT_NODE){text=document.createTextNode('');previous.after(text);}range.setStart(text,0);range.collapse(true);
  }
  return range;
 }
 function isExposed(){return latest.current.exposed&&root.current?.isConnected&&!root.current.closest('[hidden],[inert]')&&!!root.current.getClientRects().length;}
 function restore(range:Range|null){if(!isExposed()||!root.current)return;root.current.focus();if(range&&root.current.contains(range.commonAncestorContainer)){const selected=window.getSelection();selected?.removeAllRanges();selected?.addRange(editableCaret(range));}}
 function prepareTyping(){
  const selected=window.getSelection(),range=selected?.rangeCount?selected.getRangeAt(0):null;if(!range?.collapsed||!root.current?.contains(range.commonAncestorContainer))return;
  const element=range.startContainer instanceof HTMLElement?range.startContainer:range.startContainer.parentElement,previous=range.startContainer.childNodes[range.startOffset-1];
  if(element?.closest('[data-note-passage]')||previous instanceof HTMLElement&&previous.hasAttribute('data-note-passage'))restore(range.cloneRange());
 }

 function deletionAtom(backward:boolean){
  const editor=root.current,selected=window.getSelection(),range=selected?.rangeCount?selected.getRangeAt(0):null;
  if(!editor||!range?.collapsed||!editor.contains(range.commonAncestorContainer))return null;
  const inline=(node:Node)=>node instanceof HTMLElement&&['B','STRONG','I','EM','SPAN'].includes(node.tagName);
  const adjacent=(from:Node):ChildNode|null=>{let node=from;while(node!==editor){const next=backward?node.previousSibling:node.nextSibling;if(next)return next;const parent=node.parentNode;if(!parent||!inline(parent))return null;node=parent;}return null;};
  const container=range.startContainer,element=container instanceof HTMLElement?container:container.parentElement;
  let candidate:Node|null=element?.closest('[data-note-passage]')??null;
  if(!candidate){
   if(container.nodeType===Node.TEXT_NODE){if(range.startOffset!==(backward?0:container.textContent?.length))return null;candidate=adjacent(container);}
   else candidate=container.childNodes[range.startOffset-(backward?1:0)]??adjacent(container);
   while(candidate){
    if(candidate.nodeType===Node.TEXT_NODE&&candidate.textContent===''){candidate=adjacent(candidate);continue;}
    if(inline(candidate)&&!(candidate as HTMLElement).hasAttribute('data-note-passage')){candidate=backward?candidate.lastChild:candidate.firstChild;continue;}break;
   }
  }
  if(!(candidate instanceof HTMLElement)||!candidate.hasAttribute('data-note-passage')||!passageNodes.has(candidate))return null;
  try{passageValue(candidate);read(editor,version.current,lane.value);return candidate;}catch{return null;}
 }

 function insertPassage(reference:PassageReference){
  if(lane?.deletion?.attempt)return false;
  const captured=insertion.current,editor=root.current;
  if(!captured||captured.lane!==latest.current.lane||captured.account!==latest.current.account||captured.generation!==inputGeneration.current||!editor||composing.current||lane?.composing||captured.range&&!editor.contains(captured.range.commonAncestorContainer)){
   setPassageError('Place the caret in this note, then try inserting the reference again.');return false;
  }
  try{
   read(editor,version.current,lane.value);if(!validateReference(reference))throw Error();
   // Validate on a detached copy first, leaving live writing and selection intact.
   const candidate=editor.cloneNode(true) as HTMLElement;passageRegistry.set(candidate,new Map(registry(editor)));bindNativeAtoms(candidate);
   const at=(node:Node)=>{const path:number[]=[];while(node!==editor){const parent=node.parentNode;if(!parent)throw Error();path.unshift(Array.prototype.indexOf.call(parent.childNodes,node));node=parent;}let mapped:Node=candidate;for(const index of path)mapped=mapped.childNodes[index];return mapped;};
   const range=document.createRange();if(captured.range){range.setStart(at(captured.range.endContainer),captured.range.endOffset);range.collapse(true);}else{
    if(!candidate.childNodes.length){const p=document.createElement('p');p.dir='auto';candidate.append(p);}
    let end:Node=candidate;while(end.lastChild&&!(end instanceof HTMLElement&&end.hasAttribute('data-note-passage')))end=end.lastChild;
    if(end instanceof HTMLElement&&end.hasAttribute('data-note-passage'))range.setStartAfter(end);else if(end instanceof HTMLElement&&end.tagName==='BR')range.setStartBefore(end);else range.selectNodeContents(end);range.collapse(false);
   }
   const existingAtom=(range.startContainer instanceof HTMLElement?range.startContainer:range.startContainer.parentElement)?.closest<HTMLElement>('[data-note-passage]');if(existingAtom){passageValue(existingAtom);range.setStartAfter(existingAtom);range.collapse(true);}
   const atom=passageNode({type:'passage_link',reference,label:referenceLabel(reference)},candidate);
   const source=(range.startContainer instanceof HTMLElement?range.startContainer:range.startContainer.parentElement)?.closest('a');
   if(source&&candidate.contains(source)){
    const tailRange=document.createRange();tailRange.selectNodeContents(source);tailRange.setStart(range.startContainer,range.startOffset);
    const tail=source.cloneNode(false) as HTMLElement;tail.append(tailRange.extractContents());source.after(atom);if(tail.textContent)atom.after(tail);if(!source.textContent)source.remove();
   }else range.insertNode(atom);
   const value=read(candidate,2,lane.value),payload={operation_id:'00000000-0000-4000-8000-000000000000',expected_revision:lane!.note.revision,value};
   if(new TextEncoder().encode(JSON.stringify(payload)).length>262144)throw Error();
   const pending:[unknown,number][]=[[payload,1]];let visited=0;while(pending.length){const [item,depth]=pending.pop()!;if(++visited>32768||depth>16)throw Error();if(item&&typeof item==='object')for(const child of Object.values(item))pending.push([child,depth+1]);}
   // One native transaction preserves surrounding writing and source fragments in
   // the browser's existing editing history, including Undo/Redo of rebuilt atoms.
   registry(editor).set(atom.dataset.notePassage!,passageValue(atom));version.current=2;
   const liveRange=document.createRange();liveRange.selectNodeContents(editor);restore(liveRange);
   if(!nativeCommand('insertHTML',candidate.innerHTML))throw Error();
   const inserted=editor.querySelector<HTMLElement>('[data-note-passage="'+atom.dataset.notePassage+'"]');if(!inserted)throw Error();
   const caret=document.createRange();caret.setStartAfter(inserted);caret.collapse(true);restore(caret);setPassageError('');insertion.current=null;return true;
  }catch{setPassageError('This reference could not be inserted. Your writing is kept here.');return false;}
 }
 function switchMode(){if(composing.current||lane?.composing||invalid)return;try{read(root.current!,version.current,lane.value);}catch{setInvalid(true);studies.invalidInput(lane);return;}if(!reading){const selected=window.getSelection();readSelection.current=selected?.rangeCount?selected.getRangeAt(0).cloneRange():null;}else{const captured={lane,account:studies.accountKey,tab,host:root.current};setTimeout(()=>{if(latest.current.lane===captured.lane&&latest.current.account===captured.account&&latest.current.tab===captured.tab&&root.current===captured.host&&isExposed())restore(readSelection.current);},0);}setOffered(null);setReading(!reading);}
 function activatePassage(target:HTMLElement){const node=target.closest<HTMLElement>('[data-note-passage]');if(!node||!root.current?.contains(node))return false;try{const inline=passageValue(node);if(reading)onOpen?.(inline.reference);else{const range=document.createRange();range.setStartAfter(node);range.collapse(true);restore(range);setOffered(inline);}return true;}catch{setInvalid(true);studies.invalidInput(lane);return true;}}
 function format(command:string){nativeCommand(command);}
 return <section aria-label="Note editor" className="p-3 space-y-3">
  <h3 className="font-semibold">Notes</h3><button className="underline" disabled={studies.busy||studies.studyDeletionPaused} onClick={()=>void studies.duplicateNote(lane)}>Duplicate note</button>{lane.note.copy_credit&&<p>Copied from: {lane.note.copy_credit.label}</p>}<button className="underline" disabled={studies.studyDeletionPaused} onClick={studies.beginDelete}>Delete note</button><button className="underline" onClick={studies.beginStudyDelete}>Delete study</button><p className="text-sm">{studies.study?.title}</p>{noteReferences(lane.value).map((reference,index)=><button key={index} className="underline text-sm mr-2" onClick={()=>onOpen?.(reference)}>{referenceLabel(reference)}</button>)}
  <button type="button" aria-pressed={reading} disabled={invalid||lane.composing||!!lane.deletion} className="underline" onClick={switchMode}>{reading?'Edit note':'Read note'}</button>
  <fieldset disabled={!!lane.deletion||studies.studyWritesFrozen} hidden={reading} role="toolbar" aria-label="Note formatting" className="flex flex-wrap gap-2 text-sm">
   <button onMouseDown={e=>e.preventDefault()} onClick={()=>format('bold')} aria-label="Bold" className="border rounded px-2 font-bold">B</button>
   <button onMouseDown={e=>e.preventDefault()} onClick={()=>format('italic')} aria-label="Italic" className="border rounded px-2 italic">I</button>
   <button onMouseDown={e=>e.preventDefault()} onClick={()=>format('insertUnorderedList')} className="border rounded px-2">Bullet list</button>
   <button onMouseDown={e=>e.preventDefault()} onClick={()=>format('insertOrderedList')} className="border rounded px-2">Numbered list</button>
   <button onMouseDown={e=>e.preventDefault()} onClick={()=>{const selected=window.getSelection();const range=selected?.rangeCount?selected.getRangeAt(0):null;selection.current=range&&root.current?.contains(range.commonAncestorContainer)?range.cloneRange():null;setLinkError('');setLinking(true);}} className="border rounded px-2">Link</button>
   <div ref={picker} onClickCapture={e=>{if(!insertion.current&&(e.target as HTMLElement).closest('button[aria-label="Insert passage reference"]'))captureInsertion();}} onMouseDownCapture={e=>{if((e.target as HTMLElement).closest('button[aria-label="Insert passage reference"]'))captureInsertion();}}><BookChapterSelector key={lane.note.id} retainInput label="Insert passage reference" selectedOsisId="Gen" selectedChapter={null} disabled={lane.composing} feedback={passageError} onReference={insertPassage} onCancel={(restoreFocus)=>{const captured=insertion.current;insertion.current=null;if(restoreFocus&&captured&&captured.lane===latest.current.lane&&captured.account===latest.current.account)setTimeout(()=>{if(captured.lane===latest.current.lane&&captured.account===latest.current.account&&pickerHasFocus())restore(captured.range);},0);}}/></div>
   <label>Direction <select aria-label="Paragraph direction" value={direction} onChange={e=>{setDirection(e.target.value);const selected=window.getSelection();const anchor=selected?.anchorNode,element=(anchor instanceof HTMLElement?anchor:anchor?.parentElement)?.closest('p,div[dir]');if(element&&root.current?.contains(element)){element.setAttribute('dir',e.target.value);changed();}else if(root.current){root.current.dir=e.target.value;changed();}}}><option value="auto">Auto</option><option value="ltr">Left to right</option><option value="rtl">Right to left</option></select></label>
  </fieldset>
  {!reading&&linking&&<form onSubmit={e=>{e.preventDefault();if(!safeUrl(link)){setLinkError('Enter a valid HTTP or HTTPS link with a valid hostname.');return;}if(!selection.current||!root.current?.contains(selection.current.commonAncestorContainer)){setLinkError('Select text in this note, then insert the link.');return;}if([...root.current.querySelectorAll('[data-note-passage]')].some(node=>selection.current!.intersectsNode(node))){setLinkError('Select ordinary text; passage references cannot be wrapped in a source link.');return;}root.current.focus();if(selection.current){const selected=window.getSelection();selected?.removeAllRanges();selected?.addRange(selection.current);if(!nativeCommand('createLink',link))return;}setLinking(false);setLink('');setLinkError('');selection.current=null;}}><label>Link URL<input value={link} onChange={e=>{setLink(e.target.value);setLinkError('');}} className="border w-full" /></label>{linkError&&<p role="alert">{linkError}</p>}<button type="submit" className="underline m-2">Insert link</button><button type="button" className="underline" onClick={()=>setLinking(false)}>Cancel</button></form>}
  <div key={lane.note.id} ref={root} role="textbox" aria-label="Note text" aria-multiline="true" contentEditable={!reading&&!lane.deletion&&!studies.studyWritesFrozen} aria-readonly={reading||!!lane.deletion||studies.studyWritesFrozen} suppressContentEditableWarning dir="auto" className="min-h-48 rounded border border-stone-300 bg-white p-3 outline-amber-600 whitespace-pre-wrap [&_ul]:list-disc [&_ol]:list-decimal [&_li]:ml-5 [&_p]:min-h-6 [&_a]:underline" onPointerDown={()=>{pointerFocus.current=document.activeElement!==root.current;}} onFocus={event=>{if(event.target===root.current)restoreSelection();}} onBlur={()=>{rememberSelection();pointerFocus.current=false;}} onInput={changed} onCompositionStart={()=>{composing.current=true;studies.composition(true,lane);}} onCompositionEnd={()=>{composing.current=false;changed();studies.composition(false,lane);}} onPaste={e=>{e.preventDefault();if(reading)return;nativeCommand('insertText',e.clipboardData.getData('text/plain'));}} onDrop={e=>e.preventDefault()} onKeyDown={e=>{if(!reading&&!composing.current&&!e.nativeEvent.isComposing&&!e.ctrlKey&&!e.metaKey&&!e.altKey&&Array.from(e.key).length===1)prepareTyping();if((e.key==='Enter'||e.key===' ')&&activatePassage(e.target as HTMLElement)){e.preventDefault();}}} onClick={e=>{if(activatePassage(e.target as HTMLElement))e.preventDefault();else if(!reading&&(e.target as HTMLElement).closest('a'))e.preventDefault();}} />
  {offered&&!reading&&<button className="underline" onClick={()=>onOpen?.(offered.reference)}>Open passage</button>}
  <p role="status" aria-live="polite">{invalid||lane.status==='failed'||lane.status==='conflict'?'Changes not saved':lane.status==='saved'?'Draft saved':'Saving…'} {(lane.status==='failed'||invalid)&&<button className="underline" onClick={()=>{if(invalid)changed();else void studies.retry(lane);}}>Retry</button>}</p>
  {lane.status==='conflict'&&<section aria-label="Note conflict"><p role="alert">{lane.formatUnsupported?'Reload to continue editing.':'This note has changed. Your input is kept here.'}</p><button className="underline mr-3" disabled={lane.reviewing} onClick={()=>void studies.reviewLatest(lane)}>Review latest</button><button className="underline" disabled={studies.busy||invalid||lane.composing||!!lane.deletion} onClick={()=>void studies.saveMine(lane)}>Save mine as a new note</button>{lane.latest&&<><SavedNoteReview value={lane.latest.value}/><p>Connections: {lane.latest.value.connections.length}; highlights: {lane.latest.value.highlights.length}</p>{aggregate(lane.latest.value).connections.map(connection=><p key={connection.id}>{referenceLabel(connection.reference)}</p>)}{aggregate(lane.latest.value).highlights.map(mark=><p key={mark.id}>Colour {mark.colour}: {mark.anchor.segments.map(segment=>referenceLabel(segment.reference)).join(', ')}</p>)}<button className="underline" disabled={lane.composing||studies.creationRecovery} onClick={()=>studies.useLatest(lane)}>Use latest</button></>}</section>}
  <button className="underline" onClick={()=>studies.setTool('studies')}>Back to Studies</button>
 </section>;
}
