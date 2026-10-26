/** Readability guard for the existing note wire versions, before UI attachment.
 * This does not authorize resources or replace server command validation. */
import type {NoteValue} from '@/generated/personal-notes/types.gen';
import {validAggregate} from './own-highlights';
import {validateReference} from './passage-references';

export function safeNoteUrl(raw:string){
 try{
  const url=new URL(raw),authority=raw.match(/^https?:\/\/([^/?#]+)/i)?.[1];
  if(!authority||authority.includes('@')||!['http:','https:'].includes(url.protocol)||url.username||url.password||new TextEncoder().encode(raw).length>2048||/[\s\\\u0000-\u001f\u007f-\u009f]/u.test(raw)||/%(?![0-9a-f]{2})|%(?:0[0-9a-f]|1[0-9a-f]|7f|5c)/i.test(raw)||url.port==='0')return false;
  if(/^\d+\.\d+\.\d+\.\d+$/.test(url.hostname)&&authority.replace(/:\d+$/,'')!==url.hostname)return false;
  if(!url.hostname.startsWith('[')&&(url.hostname.length>253||url.hostname.replace(/\.$/,'').split('.').some(label=>! /^[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?$/.test(label))))return false;
  return true;
 }catch{return false;}
}

const object=(value:unknown):value is Record<string,unknown>=>!!value&&typeof value==='object'&&!Array.isArray(value);
const text=(value:unknown,max:number,min=1):value is string=>typeof value==='string'&&!/[\u0000\uD800-\uDFFF]/u.test(value)&&Array.from(value).length>=min&&Array.from(value).length<=max;
/** The fixed grammar bounds traversal; unknown versions/node kinds are not guessed. */
export function isReadableNoteValue(value:unknown):value is NoteValue {
 if(!object(value)||!object(value.document)||!Array.isArray(value.connections)||!Array.isArray(value.highlights))return false;
 if('format_version'in value? !validAggregate(value):value.connections.length!==0||value.highlights.length!==0)return false;
 if(new TextEncoder().encode(JSON.stringify(value)).length>262144)return false;
 const document=value.document;
 if(document.version!==1&&document.version!==2||!Array.isArray(document.blocks)||document.blocks.length>256)return false;
 let nodes=1,characters=0;
 const take=(count=1,size=0)=>{nodes+=count;characters+=size;return nodes<=2048&&characters<=50000;};
 const plain=(inline:unknown):boolean=>{
  if(!object(inline)||inline.type!=='text'||!text(inline.text,4096)||!Array.isArray(inline.marks)||inline.marks.length>2||inline.marks.some(mark=>mark!=='bold'&&mark!=='italic')||!['','bold','italic','bold,italic'].includes(inline.marks.join(',')))return false;
  return take(1,Array.from(inline.text).length);
 };
 const inline=(item:unknown):boolean=>{
  if(!object(item))return false;
  if(item.type==='text')return plain(item);
  if(item.type==='external_link'){
   if(!take())return false;return typeof item.url==='string'&&safeNoteUrl(item.url)&&Array.isArray(item.content)&&item.content.length>=1&&item.content.length<=64&&item.content.every(plain);
  }
  if(item.type==='passage_link'){
   if(document.version!==2||!text(item.label,200)||!validateReference(item.reference))return false;
   return take(item.reference.target.kind==='chapter'?3:5,Array.from(item.label).length);
  }
  return false;
 };
 const paragraph=(item:unknown):boolean=>{
  if(!object(item)||item.type!=='paragraph'||!['auto','ltr','rtl'].includes(item.direction as string)||!Array.isArray(item.content)||item.content.length>256)return false;
  return take()&&item.content.every(inline);
 };
 for(const block of document.blocks){
  if(!object(block))return false;
  if(block.type==='paragraph'){if(!paragraph(block))return false;}
  else if(block.type==='list'){
   if(!take())return false;if(!['bullet','ordered'].includes(block.style as string)||!Array.isArray(block.items)||block.items.length<1||block.items.length>128||!block.items.every(item=>Array.isArray(item)&&item.length>=1&&item.length<=16&&item.every(paragraph)))return false;
  }else return false;
  if(nodes>2048||characters>50000)return false;
 }
 return true;
}
