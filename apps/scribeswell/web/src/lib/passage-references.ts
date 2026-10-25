/** Offline source identity; availability belongs to actual reader requests. */
import catalogue from '@/generated/reference-catalogue.json';
import {toHebrewOrdinal} from './hebrew-ordinal';
export type Point={chapter:number;verse:number};
export type {PassageReference} from '@/generated/personal-notes/types.gen';
import type {PassageReference} from '@/generated/personal-notes/types.gen';
export const referenceCatalogue=catalogue;
export const referenceBooks=catalogue.books;
export function referenceBook(id:string){return referenceBooks.find(book=>book.book_id===id);}
export class ReferenceFailure extends Error{constructor(public code:string,public choices:string[]=[]){super(code);}}
function normalize(value:string){return value.normalize('NFC').replace(/[\u0591-\u05bd\u05bf\u05c1-\u05c2\u05c4-\u05c5\u05c7]/g,'').toLowerCase().trim().replace(/\s+/g,' ');}
const aliases=new Map<string,Set<string>>();for(const book of referenceBooks)for(const alias of book.aliases){const key=normalize(alias).replace(/\./g,'');const ids=aliases.get(key)??new Set<string>();ids.add(book.book_id);aliases.set(key,ids);}
function number(value:string){
 if(/^[1-9][0-9]*$/.test(value))return Number(value);
 const plain=value.replace(/[׳״'"]/g,'');
 for(let i=1;i<=999;i++)if(toHebrewOrdinal(i)===plain){const punct=plain.length===1?[plain+'׳',plain+"'"]:[plain.slice(0,-1)+'״'+plain.slice(-1),plain.slice(0,-1)+'"'+plain.slice(-1)];if(value===plain||punct.includes(value))return i;}
 throw new ReferenceFailure('reference_invalid');
}
export function validateReference(value:unknown):value is PassageReference{
 if(!value||typeof value!=='object'||Array.isArray(value))return false;const r=value as PassageReference;
 if(Object.keys(r).sort().join(',')!=='book_id,catalogue_id,catalogue_version,target,versification_id'||r.catalogue_id!==catalogue.catalogue_id||r.catalogue_version!==catalogue.catalogue_version)return false;
 const book=referenceBook(r.book_id);if(!book||r.versification_id!==book.versification_id||!r.target||typeof r.target!=='object')return false;
 const chapter=(c:number)=>Number.isInteger(c)&&c>0&&c<=book.chapter_verse_counts.length;
 const point=(p:Point)=>p&&Object.keys(p).sort().join(',')==='chapter,verse'&&chapter(p.chapter)&&Number.isInteger(p.verse)&&p.verse>0&&p.verse<=book.chapter_verse_counts[p.chapter-1];
 const t=r.target;if(t.kind==='chapter')return Object.keys(t).sort().join(',')==='chapter,kind'&&chapter(t.chapter);
 return t.kind==='verse_range'&&Object.keys(t).sort().join(',')==='end,kind,start'&&point(t.start)&&point(t.end)&&(t.start.chapter<t.end.chapter||t.start.chapter===t.end.chapter&&t.start.verse<=t.end.verse);
}
export function chapterReference(book_id:string,chapter:number):PassageReference{return makeReference(book_id,{kind:'chapter',chapter});}
export function makeReference(book_id:string,target:PassageReference['target']):PassageReference{
 const book=referenceBook(book_id);const value={catalogue_id:catalogue.catalogue_id,catalogue_version:catalogue.catalogue_version,versification_id:book?.versification_id??'',book_id,target};if(!validateReference(value))throw new ReferenceFailure('reference_invalid');return value;
}
export function parseReference(text:string):PassageReference{
 if(text.length>300)throw new ReferenceFailure('reference_invalid');text=normalize(text);
 const matches=[...aliases.entries()].flatMap(([alias,ids])=>{const pattern=[...alias].map(char=>char===' '?'\\s+':char.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')+'\\.*').join('');const match=text.match(new RegExp('^'+pattern));return match&&text.slice(match[0].length).trim()?[[alias,ids,text.slice(match[0].length).trim()] as const]:[];}).sort((a,b)=>b[0].length-a[0].length);
 if(!matches.length)throw new ReferenceFailure('reference_unknown_book');const [,ids,tail]=matches[0];if(ids.size!==1)throw new ReferenceFailure('reference_ambiguous',[...ids]);
 const id=[...ids][0],parts=tail.split(/\s*[-–—]\s*/);if(parts.length>2)throw new ReferenceFailure('reference_invalid');
 const start=parts[0].split(':').map(n=>number(n.trim()));if(start.length===1&&parts.length===1)return chapterReference(id,start[0]);if(start.length!==2)throw new ReferenceFailure('reference_invalid');
 let end=parts.length===2?parts[1].split(':').map(n=>number(n.trim())):start;if(end.length===1)end=[start[0],end[0]];if(end.length!==2)throw new ReferenceFailure('reference_invalid');
 return makeReference(id,{kind:'verse_range',start:{chapter:start[0],verse:start[1]},end:{chapter:end[0],verse:end[1]}});
}
export function referenceLabel(reference:PassageReference){const name=referenceBook(reference.book_id)?.name_en??reference.book_id,t=reference.target;if(t.kind==='chapter')return `${name} ${t.chapter}`;const start=`${name} ${t.start.chapter}:${t.start.verse}`;return t.start.chapter===t.end.chapter?(t.start.verse===t.end.verse?start:`${start}–${t.end.verse}`):`${start}–${t.end.chapter}:${t.end.verse}`;}
export function referenceStart(reference:PassageReference){return reference.target.kind==='chapter'?{chapter:reference.target.chapter,verse:undefined}:reference.target.start;}
export function referenceKey(reference:PassageReference){return referenceLabel(reference)+'|'+reference.catalogue_version+'|'+reference.versification_id;}
