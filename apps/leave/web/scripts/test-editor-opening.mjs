import test from 'node:test';import assert from 'node:assert/strict';
import {createDraftController} from '../src/draft-controller.ts';
import {createLeaveClient} from '../src/api/leave.ts';
import {emptyInput} from '../src/draft-input.ts';
import {createChoicesController} from '../src/choices-controller.ts';
import {createDraftEditorController} from '../src/draft-editor-controller.ts';
const org='11111111-1111-4111-8111-111111111111',draft='22222222-2222-4222-8222-222222222222',operation='33333333-3333-4333-8333-333333333333';
const context={status:'ready',org_id:org,employment_id:org,scope_generation:'0',active_draft:{draft_id:draft,revision:'1'},editability:{status:'editable'},setup_notices:[]};
const read={org_id:org,draft_id:draft,revision:'1',state:'active',input:emptyInput(),editability:{status:'editable'},setup_notices:[],updated_at:'2026-11-08T00:00:00Z'},choices={choices:[],next_cursor:null,selected:{status:'not_requested'}},opening={context,draft:read,choices};
const ok=value=>({ok:true,value});
function harness(overrides={}){const calls=[],states=[],abort=new AbortController();let live=true;const c=createDraftController({client:{draftContext:async()=>{calls.push('context');return ok(context);},editorOpen:async(_t,_s,o,d)=>{calls.push(['editor',o,d]);return ok(opening);},startDraft:async(_t,_s,_o,c)=>{calls.push(['start',c]);return ok({operation_id:operation,status:'committed',result:{command:'start',disposition:'created',draft_id:draft,revision:'1',scope_generation:'0'}});},draftOutcome:async()=>{throw Error('unexpected');},...overrides},acquire:()=>({session:{access_token:'synthetic'},signal:abort.signal,isCurrent:()=>live,release(){}}),publish:s=>states.push(s),newId:()=>operation});return{c,calls,states,revoke(){live=false;abort.abort();}};}
test('bookmarked active open uses exactly one complete read and carries background/options without discovery',async()=>{const h=harness();await h.c.load(org,draft);assert.deepEqual(h.calls,[['editor',org,draft]]);assert.equal(h.states.at(-1).kind,'opened');assert.equal(h.states.at(-1).choices,choices);assert.equal(h.states.at(-1).background,context);assert.equal(h.states.at(-1).firstChoiceEligible,false);h.c.dispose();});
test('committed created start opening failure retries same target without replaying start and retains provenance',async()=>{let opens=0;const h=harness({editorOpen:async()=>++opens===1?{ok:false,error_id:'dependency_unavailable'}:ok(opening)});await h.c.load(org);await h.c.apply();assert.equal(h.states.at(-1).kind,'unavailable');await h.c.retryOpen();assert.equal(h.states.at(-1).kind,'opened');assert.equal(h.states.at(-1).firstChoiceEligible,true);assert.equal(h.calls.filter(v=>Array.isArray(v)&&v[0]==='start').length,1);h.c.dispose();});
test('initial whole-open failure never publishes partial context/draft/options, and retry preserves target',async()=>{let count=0;const targets=[];const h=harness({editorOpen:async(_t,_s,o,d)=>{targets.push([o,d]);return ++count===1?{ok:false,error_id:'dependency_unavailable'}:ok(opening);}});await h.c.load(org,draft);assert.equal(h.states.at(-1).kind,'unavailable');assert.equal(h.states.some(s=>s.kind==='opened'||s.kind==='context'),false);await h.c.retryOpen();assert.deepEqual(targets,[[org,draft],[org,draft]]);h.c.dispose();});
test('late old scope/account/open responses cannot publish metadata or input',async()=>{let done;const h=harness({editorOpen:()=>new Promise(r=>done=r)});const p=h.c.load(org,draft);h.revoke();done(ok(opening));await p;assert.equal(h.states.at(-1).kind,'loading');h.c.dispose();});
test('strict opening client binds org/target/summary/selected shape and refuses impossible/unknown combinations',async()=>{
 const paths=[];const client=createLeaveClient(async path=>{paths.push(path);return Response.json(opening);});assert.equal((await client.editorOpen('s',new AbortController().signal,org,draft)).ok,true);assert.equal(paths[0],'/api/v1/organizations/'+org+'/drafts/'+draft+'/editor');
 for(const mutation of [v=>v.context.org_id=draft,v=>v.draft.draft_id=org,v=>v.context.active_draft.revision='2',v=>v.choices.selected={status:'obsolete'},v=>v.extra=true,v=>v.draft.editability={status:'read_only',reason:'permission_missing'},v=>delete v.choices]){const v=structuredClone(opening);mutation(v);const c=createLeaveClient(async()=>Response.json(v));assert.equal((await c.editorOpen('s',new AbortController().signal,org,draft)).ok,false);}
});
test('closed response permits only context and discarded shape; setup/denial stays guarded',async()=>{const closed={context:{...context,active_draft:null},draft:{org_id:org,draft_id:draft,revision:'2',state:'discarded',discarded_at:read.updated_at}};const client=createLeaveClient(async()=>Response.json(closed));assert.equal((await client.editorOpen('s',new AbortController().signal,org,draft)).ok,true);const h=harness({editorOpen:async()=>ok(closed)});await h.c.load(org,draft);assert.equal(h.states.at(-1).kind,'closed');h.c.dispose();for(const [error_id,kind] of [['access_denied','denied'],['leave.setup_required','setup_required']]){const h=harness({editorOpen:async()=>({ok:false,error_id})});await h.c.load(org,draft);assert.equal(h.states.at(-1).kind,kind);h.c.dispose();}});

test('opening refuses obsolete selection still offered by the same choices snapshot',async()=>{const value=structuredClone(opening);value.draft.input.leave_type_id=org;value.choices.choices=[{type_id:org,version_id:draft,name:'Still offered',revision:'1',permitted_modes:['full_days']}];value.choices.selected={status:'obsolete'};const client=createLeaveClient(async()=>Response.json(value));const result=await client.editorOpen('s',new AbortController().signal,org,draft);assert.equal(result.ok,false);});

function maximumUnicodeOpening(){
 const value=structuredClone(opening),maximumRevision='9223372036854775807';
 value.context.active_draft.revision=maximumRevision;value.draft.revision=maximumRevision;
 const input=value.draft.input;input.note='😀'.repeat(4000);input.leave_type_id=org;input.duration_mode='hours';
 for(const date of [input.full_days.start,input.full_days.end,input.half_day.date,input.hours.date])date.text='😀'.repeat(64);
 input.hours.duration.text='😀'.repeat(32);
 const choice={type_id:org,version_id:operation,name:'😀'.repeat(120),revision:maximumRevision,permitted_modes:['full_days','half_day','hours']};
 value.choices={choices:Array.from({length:100},(_,n)=>({...choice,type_id:`00000000-0000-4000-8000-${String(n+1).padStart(12,'0')}`})),next_cursor:null,selected:{status:'available',choice}};
 return value;
}
test('composed opening accepts maximum Unicode input and choice page beyond the ordinary64KiB bound',async()=>{
 const value=maximumUnicodeOpening(),bytes=new TextEncoder().encode(JSON.stringify(value)).length;
 assert.ok(bytes>65536&&bytes<196608);
 assert.deepEqual(await createLeaveClient(async()=>Response.json(value)).editorOpen('s',new AbortController().signal,org,draft),ok(value));
});
test('composed opening accepts exactly196608UTF8bytes and rejects196609bytes',async()=>{
 const value=maximumUnicodeOpening(),raw=JSON.stringify(value),bytes=new TextEncoder().encode(raw).length;
 const padded=limit=>raw+' '.repeat(limit-bytes);
 assert.equal(new TextEncoder().encode(padded(196608)).length,196608);
 assert.equal(new TextEncoder().encode(padded(196609)).length,196609);
 assert.deepEqual(await createLeaveClient(async()=>new Response(padded(196608))).editorOpen('s',new AbortController().signal,org,draft),ok(value));
 assert.deepEqual(await createLeaveClient(async()=>new Response(padded(196609))).editorOpen('s',new AbortController().signal,org,draft),{ok:false,error_id:'api_unavailable'});
});

test('seeded pagination retains newer input and choice while autosave completes independently of its delayed page',async()=>{
 const offered=Array.from({length:100},(_,n)=>({type_id:`00000000-0000-4000-8000-${String(n+1).padStart(12,'0')}`,version_id:operation,name:`Type ${n}`,revision:'1',permitted_modes:['hours']}));
 const cursor=Buffer.from(JSON.stringify({after:offered.at(-1).type_id,org_id:org,version:1})).toString('base64url');
 const seed={choices:offered,next_cursor:cursor,selected:{status:'available',choice:offered[0]}},input={...emptyInput(),leave_type_id:offered[0].type_id,duration_mode:'hours',note:'Saved before paging'};
 const states=[],requests=[],saves=[],lease=new AbortController();let finishPage,pageSignal;
 const client=createLeaveClient(async(url,options)=>{
  requests.push(url);
  if(url.endsWith('/input')){const command=JSON.parse(options.body);saves.push(command);return Response.json({operation_id:command.operation_id,status:'committed',result:{command:'save',draft_id:draft,revision:String(BigInt(command.expected_revision)+1n),scope_generation:'0',disposition:'saved'}});}
  const query=new URL(url,'http://leave').searchParams;
  if(query.has('cursor')){pageSignal=options.signal;return new Promise(resolve=>finishPage=value=>resolve(Response.json(value)));}
  return Response.json({...seed,selected:{status:'available',choice:offered[1]}});
 });
 const acquire=()=>({session:{access_token:'synthetic'},signal:lease.signal,isCurrent:()=>true,release(){}});
 const editor=createDraftEditorController({org,initial:{...read,input},client,acquire,publish(){},newId:()=>operation});
 const catalogue=createChoicesController({client,acquire,initial:seed,publish:state=>states.push(state)});
 try{
  editor.change({...input,note:'Unsaved before paging'});assert.equal(editor.snapshot().status,'dirty');
  const page=catalogue.load(org,input.leave_type_id,editor.snapshot().generation,seed.next_cursor);
  const query=new URL(requests[0],'http://leave').searchParams;assert.equal(query.get('cursor'),cursor);assert.equal(query.get('selected_type_id'),input.leave_type_id);
  const newer={...input,leave_type_id:offered[1].type_id,note:'Unsaved newer choice and independent note'};editor.change(newer);catalogue.invalidate();
  assert.equal(pageSignal.aborted,true);assert.equal(states.at(-1).kind,'retained');assert.equal(states.at(-1).value,seed);
  await catalogue.load(org,newer.leave_type_id,editor.snapshot().generation);
  assert.equal(editor.snapshot().status,'dirty');assert.deepEqual(editor.snapshot().input,newer);
  await new Promise(resolve=>setTimeout(resolve,1100));
  assert.equal(saves.length,1);assert.deepEqual(saves[0].input,newer);assert.equal(editor.snapshot().status,'saved');assert.deepEqual(editor.snapshot().input,newer);
  const published=states.length;
  finishPage({choices:[],next_cursor:null,selected:{status:'obsolete'}});await page;
  assert.equal(states.length,published);assert.equal(states.at(-1).value.selected.choice.type_id,newer.leave_type_id);assert.deepEqual(editor.snapshot().input,newer);assert.equal(editor.snapshot().revision,'2');
 }finally{catalogue.dispose();editor.dispose();}
});
