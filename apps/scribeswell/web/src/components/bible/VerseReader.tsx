import {useEffect,useMemo,useRef,useState} from 'react';
import {useStudies} from '@/context/StudiesContext';
import {useWorkspace} from '@/context/ReaderWorkspaceContext';
import {OwnHighlightActions,paintFor,type Phrase} from './OwnHighlightActions';
/**
 * VerseReader — renders verses with clickable Hebrew words.
 * Clicking a word triggers morphology lookup.
 *
 * Layout per verse row (CSS grid, dir="ltr" on the row):
 *   col 1 (w-6, left)  : verse number
 *   col 2 (flex-1, right): Hebrew text block (dir="rtl" internally)
 *
 * Using an explicit LTR grid guarantees col 1 is always on the left
 * regardless of any inherited direction context.
 */
import type {
  VerseWithWordsResponse,
  WordResponse,
} from "@/schemas/bible.schema";

const NO_HIGHLIGHTS:import('@/lib/own-highlights').NoteHighlight[]=[];
interface VerseReaderProps {
  book:string;
  active?:boolean;
  verses: VerseWithWordsResponse[];
  origin?:string;
  matchKey?: string|null;
  onPreview?: (word:WordResponse|null)=>void;
  selectedWordId: number | null;
  onWordClick: (word: WordResponse, verse: number, retain?:boolean) => void;
}

export function VerseReader({
  book,active=true,verses, matchKey, onPreview,origin='',
  selectedWordId,
  onWordClick,
}: VerseReaderProps) {
  const studies=useStudies(),workspace=useWorkspace(),root=useRef<HTMLDivElement>(null),[phrase,setPhrase]=useState<Phrase|null>(null),base=useRef<number|null>(null);
  const mouseDrag=useRef<{start:number;end:number;x:number;y:number;moved:boolean}|null>(null),ignoreNative=useRef(false),ignoreClick=useRef(false);
  const live=useRef({origin,account:studies.accountKey,tab:workspace.workspace.tabKey});live.current={origin,account:studies.accountKey,tab:workspace.workspace.tabKey};
  useEffect(()=>{setPhrase(null);base.current=null;mouseDrag.current=null;ignoreNative.current=false;ignoreClick.current=false;},[origin,workspace.workspace.tabKey,studies.accountKey]);
  useEffect(()=>{
   const selected=()=>{
    if(ignoreNative.current||mouseDrag.current)return;
    const selection=window.getSelection(),range=selection?.rangeCount?selection.getRangeAt(0):null;
    if(!range||range.collapsed)return;
    if(!root.current?.contains(range.startContainer)||!root.current.contains(range.endContainer)){setPhrase(null);return;}
    const words=[...root.current.querySelectorAll('[data-phrase-index]')];const touched=words.flatMap((node,index)=>range.intersectsNode(node)?[index]:[]);
    if(touched.length)setPhrase({start:touched[0],end:touched[touched.length-1]});
   };
   const finish=(event:PointerEvent)=>{const drag=mouseDrag.current;mouseDrag.current=null;if(!drag?.moved)return;if(!root.current?.contains(event.target as Node)){setPhrase(null);return;}ignoreNative.current=true;setTimeout(()=>{ignoreNative.current=false;},0);ignoreClick.current=true;setPhrase({start:Math.min(drag.start,drag.end),end:Math.max(drag.start,drag.end)});};
   document.addEventListener('pointerup',finish);document.addEventListener('selectionchange',selected);return()=>{document.removeEventListener('selectionchange',selected);document.removeEventListener('pointerup',finish);};
  },[]);
  useEffect(()=>{if(!active)setPhrase(null);},[active]);
  const highlights=studies.lane&&'format_version'in studies.lane.value?studies.lane.value.highlights:NO_HIGHLIGHTS;
  const indices=useMemo(()=>new Map(verses.flatMap(v=>v.words).map((word,index)=>[word,index])),[verses]);
  const paint=useMemo(()=>paintFor(verses,highlights),[verses,highlights]);
  if (!verses.length) {
    return (
      <p className="text-stone-400 text-sm italic">No verses found.</p>
    );
  }

  return (
    <><OwnHighlightActions book={book} verses={verses} phrase={phrase} origin={origin} clear={()=>{ignoreNative.current=false;setPhrase(null);window.getSelection()?.removeAllRanges();}}/><div ref={root} className="space-y-0" role="list" aria-label="Verses" onPointerDown={event=>{ignoreNative.current=false;ignoreClick.current=false;if(event.pointerType!=='mouse'||event.button!==0||event.shiftKey)return;const target=(event.target as HTMLElement).closest<HTMLElement>('[data-phrase-index]');if(target){const index=Number(target.dataset.phraseIndex);mouseDrag.current={start:index,end:index,x:event.clientX,y:event.clientY,moved:false};}}} onPointerMove={event=>{const drag=mouseDrag.current;if(!drag||event.pointerType!=='mouse'||!(event.buttons&1))return;if(Math.abs(event.clientX-drag.x)+Math.abs(event.clientY-drag.y)>4)drag.moved=true;const target=(event.target as HTMLElement).closest<HTMLElement>('[data-phrase-index]');if(target&&root.current?.contains(target))drag.end=Number(target.dataset.phraseIndex);}} onPointerCancel={()=>{mouseDrag.current=null;}} onContextMenu={e=>{if((e.nativeEvent as PointerEvent).pointerType==='touch')return;const target=(e.target as HTMLElement).closest<HTMLElement>('[data-phrase-index]');if(target){e.preventDefault();if(!phrase){const index=Number(target.dataset.phraseIndex);setPhrase({start:index,end:index});}}}}>
      {verses.map((verse) => (
        <div
          key={verse.id}
          data-verse={verse.verse_num}
          role="listitem"
          // dir="ltr" on the row so grid columns are always left=col1, right=col2.
          // The Hebrew <p> inside col2 overrides direction back to RTL.
          dir="rtl"
          className="grid items-baseline"
          style={{ gridTemplateColumns: "1.5rem 1fr" }}
        >
          {/* Col 1: verse number — always on the left */}
          <span
            className="text-xs text-stone-400 font-mono select-none text-right pr-1 pt-px"
            aria-label={`Verse ${verse.verse_num}`}
          >
            {verse.verse_num}
          </span>

          {/* Col 2: Hebrew text — RTL within its column */}
          <p
            className="verse-line text-xl"
            style={{ lineHeight: "1.9" }}
            dir="rtl"
            lang="he"
          >
            {verse.words.map((word) => {const index=indices.get(word)!,mark=paint.get(`${verse.id}:${word.position}`);return (
              <span role="button" tabIndex={0}
                key={word.id}
                data-word-position={word.position}
                data-phrase-index={index}
                data-own-highlight={mark?.id}
                style={{userSelect:'text',WebkitUserSelect:'text',...(mark?{backgroundColor:mark.colour}:{}),...(phrase&&index>=phrase.start&&index<=phrase.end?{outline:'1px solid #78716c'}:{})}}
                onPointerEnter={event=>{if(event.pointerType!=='touch')onPreview?.(word);}}
                onPointerLeave={()=>onPreview?.(null)}
                onPointerCancel={()=>onPreview?.(null)}
                onFocus={()=>onPreview?.(word)}
                onBlur={()=>onPreview?.(null)}
                onKeyDown={event=>{ignoreNative.current=false;if(event.key==='Enter'||event.key===' '){event.preventDefault();if(event.shiftKey&&base.current!==null){setPhrase({start:Math.min(base.current,index),end:Math.max(base.current,index)});return;}ignoreClick.current=false;event.currentTarget.click();}}}
                onClick={event=>{
                  if(ignoreClick.current){ignoreClick.current=false;return;}
                  if(event.shiftKey&&base.current!==null){setPhrase({start:Math.min(base.current,index),end:Math.max(base.current,index)});return;}
                  if(window.getSelection()?.toString())return;
                  base.current=index;setPhrase(null);
                  if(mark&&studies.lane){onWordClick(word,verse.verse_num,true);studies.setTool('analysis');studies.setAnalysisTab('Notes');return;}
                  onWordClick(word, verse.verse_num);
                }}
                className={`word-token inline-block mx-0.5 ${
                  selectedWordId === word.id ? "selected" : matchKey && word.match_key===matchKey ? "related bg-amber-100 rounded" : ""
                }`}
                aria-label={`Word: ${word.display_he}${word.lemma_strong ? ` (${word.lemma_strong})` : ""}`}
                aria-pressed={selectedWordId === word.id}
              >
                {word.display_he}
              </span>
            );})}
          </p>
        </div>
      ))}
    </div></>
  );
}
