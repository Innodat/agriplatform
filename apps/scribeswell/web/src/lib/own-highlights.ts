import type {AggregateNoteValue,HighlightAnchor,NoteHighlight,NoteValue} from '@/generated/personal-notes/types.gen';
import {referenceBook,referenceKey,validateReference,type PassageReference} from './passage-references';
export type {HighlightAnchor,NoteHighlight};
export type ReadyEvidence={version:1;status:'ready';source_id:string;source_revision:string;catalogue_version:string;versification_id:string;tokenization_version:string;book:string;chapter:number;verse:number;reference:PassageReference;verse_token_digest:string;observed_word_ids:string[];token_count:number};
export type Evidence=ReadyEvidence|{version:1;status:'unavailable'};
const object=(v:unknown):v is Record<string,unknown>=>!!v&&typeof v==='object'&&!Array.isArray(v);
const keys=(v:Record<string,unknown>,names:string)=>Object.keys(v).sort().join(',')===names.split(',').sort().join(',');
export const identifier=(v:unknown):v is string=>typeof v==='string'&&/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}(?![\s\S])/.test(v)&&v!=='00000000-0000-0000-0000-000000000000';
const label=(v:unknown)=>typeof v==='string'&&/^[A-Za-z0-9][A-Za-z0-9._:-]{0,63}(?![\s\S])/.test(v);
const decimal=(v:unknown):v is string=>typeof v==='string'&&/^[1-9][0-9]{0,18}(?![\s\S])/.test(v)&&BigInt(v)<=9223372036854775807n;
export function validAnchor(value:unknown):value is HighlightAnchor{
 if(!object(value)||!keys(value,'version,source_id,source_revision,catalogue_version,versification_id,tokenization_version,segments')||value.version!==1||!identifier(value.source_revision)||!['source_id','catalogue_version','versification_id','tokenization_version'].every(key=>label(value[key]))||!Array.isArray(value.segments)||value.segments.length<1||value.segments.length>128)return false;
 let book='',previous:{chapter:number;verse:number}|undefined;const ids:string[]=[];
 for(const s of value.segments){
  if(!object(s)||!keys(s,'reference,start_position,end_position,observed_word_ids,verse_token_digest')||!validateReference(s.reference)||s.reference.target.kind!=='verse_range'||JSON.stringify(s.reference.target.start)!==JSON.stringify(s.reference.target.end)||s.reference.versification_id!=='oshb-hebrew-json-c2d8e9e5'||s.reference.catalogue_version!==value.catalogue_version||s.reference.versification_id!==value.versification_id||typeof s.verse_token_digest!=='string'||! /^[0-9a-f]{64}(?![\s\S])/.test(s.verse_token_digest)||!Number.isInteger(s.start_position)||!Number.isInteger(s.end_position)||Number(s.start_position)<1||Number(s.end_position)>512||Number(s.end_position)<Number(s.start_position)||!Array.isArray(s.observed_word_ids)||s.observed_word_ids.length!==Number(s.end_position)-Number(s.start_position)+1||!s.observed_word_ids.every(decimal))return false;
  if(book&&book!==s.reference.book_id)return false;book=s.reference.book_id;
  const p=s.reference.target.start;
  if(previous){const count=referenceBook(book)!.chapter_verse_counts[previous.chapter-1];const next=previous.verse<count?{chapter:previous.chapter,verse:previous.verse+1}:{chapter:previous.chapter+1,verse:1};if(p.chapter!==next.chapter||p.verse!==next.verse||s.start_position!==1)return false;}
  previous=p;ids.push(...s.observed_word_ids);
 }
 return new Set(ids).size===ids.length;
}
export function readableEvidence(value:unknown):value is Evidence{
 if(!object(value)||value.version!==1)return false;
 if(value.status==='unavailable')return keys(value,'version,status');
 if(value.status!=='ready'||!identifier(value.source_revision)||!['source_id','catalogue_version','versification_id','tokenization_version'].every(key=>label(value[key]))||!validateReference(value.reference)||value.reference.target.kind!=='verse_range'||JSON.stringify(value.reference.target.start)!==JSON.stringify(value.reference.target.end)||!Array.isArray(value.observed_word_ids)||!value.observed_word_ids.every(decimal)||new Set(value.observed_word_ids).size!==value.observed_word_ids.length||value.token_count!==value.observed_word_ids.length||value.observed_word_ids.length<1||value.observed_word_ids.length>512||typeof value.verse_token_digest!=='string'||! /^[0-9a-f]{64}(?![\s\S])/.test(value.verse_token_digest))return false;
 return value.reference.book_id===value.book&&value.reference.catalogue_version===value.catalogue_version&&value.reference.versification_id===value.versification_id&&value.reference.target.start.chapter===value.chapter&&value.reference.target.start.verse===value.verse;
}
export function validAggregate(value:Record<string,unknown>){
 if(value.format_version!==3||!keys(value,'format_version,document,connections,highlights')||!Array.isArray(value.connections)||value.connections.length>128||!Array.isArray(value.highlights)||value.highlights.length>64)return false;
 const ids=new Set<string>();
 for(const c of value.connections){if(!object(c)||!keys(c,'id,reference')||!identifier(c.id)||ids.has(c.id)||!validateReference(c.reference))return false;ids.add(c.id);}
 ids.clear();let segments=0,words=0;
 for(const h of value.highlights){if(!object(h)||!keys(h,'id,colour,anchor')||!identifier(h.id)||ids.has(h.id)||typeof h.colour!=='string'||!/^#[0-9A-F]{6}(?![\s\S])/.test(h.colour)||!validAnchor(h.anchor))return false;ids.add(h.id);segments+=h.anchor.segments.length;for(const s of h.anchor.segments)words+=s.observed_word_ids.length;}
 return segments<=128&&words<=4096;
}
export function aggregate(value:NoteValue):AggregateNoteValue{return {...value,format_version:3,connections:'format_version'in value?[...value.connections]:[],highlights:'format_version'in value?[...value.highlights]:[]};}
export function noteReferences(value:NoteValue){
 const full=aggregate(value),refs:PassageReference[]=[...full.connections.map(c=>c.reference),...full.highlights.flatMap(h=>h.anchor.segments.map(s=>s.reference))];
 for(const block of value.document.blocks)for(const p of block.type==='paragraph'?[block]:block.items.flat())for(const i of p.content)if(i.type==='passage_link')refs.push(i.reference);
 return [...new Map(refs.map(ref=>[referenceKey(ref),ref])).values()];
}
export function referencesOverlap(a:PassageReference,b:PassageReference){
 if(a.catalogue_id!==b.catalogue_id||a.catalogue_version!==b.catalogue_version||a.versification_id!==b.versification_id||a.book_id!==b.book_id)return false;
 const bounds=(ref:PassageReference)=>ref.target.kind==='chapter'?[[ref.target.chapter,1],[ref.target.chapter,referenceBook(ref.book_id)!.chapter_verse_counts[ref.target.chapter-1]]]:[[ref.target.start.chapter,ref.target.start.verse],[ref.target.end.chapter,ref.target.end.verse]];
 const [as,ae]=bounds(a),[bs,be]=bounds(b),le=(x:number[],y:number[])=>x[0]<y[0]||x[0]===y[0]&&x[1]<=y[1];return le(as,be)&&le(bs,ae);
}
export function status(anchor:HighlightAnchor,evidence:Evidence|undefined,segment:HighlightAnchor['segments'][number]):'valid'|'needs_review'|'unavailable'{
 if(!evidence||evidence.status!=='ready')return 'unavailable';
 const ref=segment.reference;if(ref.target.kind!=='verse_range')return 'needs_review';const point=ref.target.start;
 return ['source_id','catalogue_version','versification_id','tokenization_version'].every(key=>anchor[key as keyof HighlightAnchor]===evidence[key as keyof ReadyEvidence])&&ref.book_id===evidence.book&&point.chapter===evidence.chapter&&point.verse===evidence.verse&&segment.verse_token_digest===evidence.verse_token_digest&&segment.end_position<=evidence.token_count?'valid':'needs_review';
}
