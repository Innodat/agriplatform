import {test} from 'node:test';
import assert from 'node:assert/strict';
import {createDraftEditorController,inputProblems} from '../src/draft-editor-controller.ts';
import {emptyInput} from '../src/draft-input.ts';
const org='6a88b25b-b457-4f9b-a9df-68fa17ac62d1',draft='66ebcf3c-9280-4b9d-8cb7-86e305210349';
const initial=()=>({org_id:org,draft_id:draft,revision:'1',state:'active',input:emptyInput(),editability:{status:'editable'},setup_notices:[],updated_at:'2026-11-08T00:00:00Z'});
const ok=value=>({ok:true,value});
const deferred=()=>{let resolve;return{promise:new Promise(r=>resolve=r),resolve:value=>resolve(value)};};
const settle=async()=>{for(let i=0;i<30;i++)await Promise.resolve();};
function harness(overrides={},read=initial()){
 let time=0,sequence=0,live=true,available=true;const timers=new Map(),commands=[],states=[],abort=new AbortController();
 const receipt=command=>ok({operation_id:command.operation_id,status:'committed',result:{command:'save',draft_id:draft,revision:String(BigInt(command.expected_revision)+1n),scope_generation:'0',disposition:'saved'}});
 const client={saveDraft:async(_t,_s,_o,_d,c)=>{commands.push(c);return receipt(c);},draftOutcome:async()=>ok({operation_id:commands.at(-1).operation_id,status:'unresolved'}),readDraft:async()=>ok(read),...overrides};
 const c=createDraftEditorController({org,initial:read,client,acquire:()=>available?({session:{access_token:'synthetic'},signal:abort.signal,isCurrent:()=>live,release(){}}):null,publish:s=>states.push(s),newId:()=>`00000000-0000-4000-8000-${String(++sequence).padStart(12,'0')}`,clock:{now:()=>time,setTimeout:(f,ms)=>{const id=++sequence;timers.set(id,{f,at:time+ms});return id;},clearTimeout:id=>timers.delete(id)}});
 return{c,commands,states,receipt,get state(){return states.at(-1);},setAvailable(value){available=value;},edit(note){c.change({...c.snapshot().input,note});},async advance(ms){const end=time+ms;while(true){const next=[...timers].filter(([,t])=>t.at<=end).sort((a,b)=>a[1].at-b[1].at)[0];if(!next)break;time=next[1].at;timers.delete(next[0]);next[1].f();await settle();}time=end;await settle();},revoke(){live=false;abort.abort();}};
}
test('idle coalesces exact complete input, acknowledgements never replace newer typing',async()=>{
 const save=deferred();let first;const h=harness({saveDraft:async(_t,_s,_o,_d,c)=>{first=c;return save.promise;}});
 h.edit(' 😀 e\u0301 \n');await h.advance(999);assert.equal(first,undefined);await h.advance(1);assert.equal(first.input.note,' 😀 e\u0301 \n');h.edit('later');assert.equal(h.state.status,'saving');save.resolve(h.receipt(first));await settle();assert.equal(h.state.revision,'2');assert.equal(h.state.input.note,'later');assert.equal(h.state.status,'dirty');h.c.dispose();
});
test('continuous input dispatches at five seconds and due typing flushes immediately after acknowledgement',async()=>{
 const first=deferred();let calls=0;const commands=[];const h=harness({saveDraft:async(_t,_s,_o,_d,c)=>{commands.push(c);return ++calls===1?first.promise:h.receipt(c);}});
 for(let n=0;n<7;n++){h.edit(String(n));await h.advance(800);}assert.equal(calls,1);assert.equal(commands[0].input.note,'6');h.edit('latest');await h.advance(1200);assert.equal(calls,1);first.resolve(h.receipt(commands[0]));await settle();assert.equal(calls,2);assert.equal(commands[1].expected_revision,'2');assert.equal(h.state.status,'saved');h.c.dispose();
});
test('uncertain save retains immutable command: lookup first, three lookups and one identical retry per bounded cycle',async()=>{
 const trace=[],commands=[];let resolve=false;const h=harness({saveDraft:async(_t,_s,_o,_d,c)=>{trace.push('save');commands.push(c);return{ok:false,error_id:'api_unavailable'};},draftOutcome:async()=>{trace.push('lookup');return resolve?h.receipt(commands[0]):ok({operation_id:commands[0].operation_id,status:'unresolved'});}});
 h.edit('original');await h.advance(1000);assert.deepEqual(trace,['save','lookup','save','lookup','lookup']);assert.equal(commands[0],commands[1]);assert.ok(Object.isFrozen(commands[0].input));assert.equal(h.state.status,'failed');h.edit('new typing');await h.advance(20000);assert.equal(commands.length,2);await h.c.close();assert.equal(h.state.exit,'confirm');h.c.stay();resolve=true;await h.c.retry();await h.advance(1000);assert.equal(h.state.input.note,'new typing');assert.equal(commands[2].expected_revision,'2');h.c.dispose();
});
test('Close immediately flushes and waits through later typing, saved Close finishes synchronously',async()=>{
 const pending=deferred();let original,calls=0;const h=harness({saveDraft:async(_t,_s,_o,_d,c)=>{calls++;original??=c;return calls===1?pending.promise:h.receipt(c);}});
 h.edit('one');const closing=h.c.close();assert.equal(h.state.exit,'waiting');h.edit('two');pending.resolve(h.receipt(original));await closing;assert.equal(calls,2);assert.equal(h.state.exit,'closed');assert.equal(h.state.input.note,'two');h.c.dispose();const saved=harness();saved.c.close();assert.equal(saved.state.exit,'closed');saved.c.dispose();
});
test('conflicts and lifecycle pause without guard-changing retry; explicit authorized review replaces local input',async()=>{
 for(const [error_id,status] of [['leave.draft_revision_conflict','conflict'],['leave.draft_discarded','closed'],['leave.draft_read_only','read_only'],['leave.setup_required','setup_required'],['authentication_required','auth_required']]){
  let calls=0;const h=harness({saveDraft:async()=>{calls++;return{ok:false,error_id};}});h.edit('local');await h.advance(1000);assert.equal(h.state.status,status);assert.equal(h.state.input.note,'local');await h.c.retry();assert.equal(calls,1);if(status==='conflict'){await h.c.review();assert.equal(h.state.input.note,'');assert.equal(h.state.status,'saved');await h.advance(10000);assert.equal(calls,1);}h.c.dispose();
 }
});
test('denial removes content, stale lease/disposed response cannot publish; review outage retains edits',async()=>{
 const denied=harness({saveDraft:async()=>({ok:false,error_id:'access_denied'})});denied.edit('secret');await denied.advance(1000);assert.equal(denied.state.input,null);denied.c.dispose();
 for(const revoke of [false,true]){const pending=deferred();let command;const h=harness({saveDraft:async(_t,_s,_o,_d,c)=>{command=c;return pending.promise;}});h.edit('old');await h.advance(1000);const count=h.states.length;if(revoke)h.revoke();else h.c.dispose();pending.resolve(h.receipt(command));await settle();assert.equal(h.states.length,count);h.c.dispose();}
 const h=harness({saveDraft:async()=>({ok:false,error_id:'leave.draft_revision_conflict'}),readDraft:async()=>({ok:false,error_id:'api_unavailable'})});h.edit('keep');await h.advance(1000);await h.c.review();assert.equal(h.state.input.note,'keep');assert.equal(h.state.status,'conflict');h.c.dispose();
});
test('command/target/operation mismatch is terminal and cannot advance revision',async()=>{
 for(const wrong of ['command','draft_id','operation_id']){let command;const h=harness({saveDraft:async(_t,_s,_o,_d,c)=>{command=c;return{ok:false,error_id:'api_unavailable'};},draftOutcome:async()=>{const r=h.receipt(command);if(wrong==='operation_id')r.value.operation_id=org;else r.value.result[wrong]=wrong==='command'?'start':org;return r;}});h.edit('x');await h.advance(1000);assert.equal(h.state.revision,'1');assert.equal(h.state.status,'conflict');h.c.dispose();}
});
test('bounds count codepoints, never truncate, preserve all inactive values and invalid domain input',async()=>{
 const h=harness();const input=emptyInput();input.note='😀'.repeat(4000);input.full_days.start.text='31/02/2026';input.full_days.end.text='24/09/';input.hours.duration.text='1,5';assert.deepEqual(inputProblems(input),[]);h.c.change(input);await h.advance(1000);assert.deepEqual(h.commands[0].input,input);h.c.change({...input,note:input.note+'x'});await h.advance(1000);assert.equal(h.commands.length,1);assert.equal(h.state.input.note.length,8001);assert.equal(h.state.status,'failed');assert.equal(inputProblems(h.state.input)[0].path,'note');h.c.dispose();
});
test('read-only initial load never writes or infers new-request defaults',async()=>{const read=initial();read.editability={status:'read_only',reason:'permission_missing'};const h=harness({},read);h.edit('not editable');await h.advance(10000);assert.equal(h.commands.length,0);assert.equal(h.state.status,'read_only');assert.equal(h.state.input.note,'');h.c.dispose();});
test('hung mutation and hung lookup are cancelled at 12 plus 15 seconds without deadline reset',async()=>{
 const signals=[];const h=harness({saveDraft:(_t,signal)=>{signals.push(signal);return new Promise(()=>{});},draftOutcome:(_t,signal)=>{signals.push(signal);return new Promise(()=>{});}});
 h.edit('pending');await h.advance(1000);await h.advance(12000);assert.equal(signals[0].aborted,true);assert.equal(h.state.status,'saving');await h.advance(15000);assert.equal(h.state.status,'failed');assert.ok(signals.every(s=>s.aborted));h.c.dispose();
});
test('saved read-only and denied Close do not acquire an unnecessary exit confirmation',async()=>{
 const read=initial();read.editability={status:'read_only',reason:'employment_ended'};const h=harness({},read);await h.c.close();assert.equal(h.state.exit,'closed');h.c.dispose();const denied=harness();denied.c.protectedFailure('access_denied');await denied.c.close();assert.equal(denied.state.exit,'closed');denied.c.dispose();
});
test('metadata denial aborts an active sequence without a late failure repopulating its state',async()=>{const pending=deferred();const h=harness({saveDraft:()=>pending.promise});h.edit('private');await h.advance(1000);h.c.protectedFailure('access_denied');await settle();assert.equal(h.state.status,'denied');assert.equal(h.state.input,null);h.c.dispose();});
test('only matching fresh created receipt plus same current revision permits first-choice initialization',async()=>{
 const {createDraftController}=await import('../src/draft-controller.ts');
 for(const [disposition,revision,expected] of [['created','1',true],['created','2',false],['resumed','1',false]]){const states=[];const abort=new AbortController(),operation='00000000-0000-4000-8000-000000000001';const controller=createDraftController({client:{draftContext:async()=>ok({status:'ready',org_id:org,employment_id:org,scope_generation:'0',active_draft:null,editability:{status:'editable'},setup_notices:[]}),startDraft:async()=>ok({operation_id:operation,status:'committed',result:{command:'start',disposition,revision:'1',scope_generation:'0',draft_id:draft}}),draftOutcome:async()=>{throw Error('unexpected');},editorOpen:async()=>ok({context:{status:'ready',org_id:org,employment_id:org,scope_generation:'0',active_draft:{draft_id:draft,revision},editability:{status:'editable'},setup_notices:[]},draft:{...initial(),revision},choices:{choices:[],next_cursor:null,selected:{status:'not_requested'}}})},acquire:()=>({session:{access_token:'s'},signal:abort.signal,isCurrent:()=>true,release(){}}),publish:s=>states.push(s),newId:()=>operation});await controller.load(org);await controller.apply();assert.equal(states.at(-1).firstChoiceEligible,expected);controller.dispose();}
});
test('first catalogue cancellation stays loading and stale response cannot repair newer input',async()=>{
 const {createChoicesController}=await import('../src/choices-controller.ts');const states=[],pending=deferred();let calls=0;const lease=new AbortController();
 const choice={choices:[],next_cursor:null,selected:{status:'obsolete'}};const c=createChoicesController({client:{choices:async()=>{calls++;return calls===1?pending.promise:{ok:true,value:choice};}},acquire:()=>({session:{access_token:'synthetic'},signal:lease.signal,isCurrent:()=>true,release(){}}),publish:s=>states.push(s)});
 const old=c.load(org,null,0);assert.equal(c.invalidate(),true);assert.equal(states.at(-1).kind,'loading');assert.equal(c.invalidate(),false);pending.resolve({ok:true,value:choice});await old;assert.equal(states.filter(s=>s.kind==='resolved').length,0);assert.equal(calls,1);
 await c.load(org,null,2);assert.equal(states.at(-1).inputGeneration,2);assert.equal(states.at(-1).kind,'resolved');c.dispose();
});
test('first catalogue real outage stays manual Retry and established catalogue edits retain metadata',async()=>{
 const {createChoicesController}=await import('../src/choices-controller.ts');const states=[],pending=deferred();let calls=0;const value={choices:[],next_cursor:null,selected:{status:'not_requested'}};const c=createChoicesController({client:{choices:async()=>++calls===1?{ok:false,error_id:'dependency_unavailable'}:calls===2?{ok:true,value}:pending.promise},acquire:()=>({session:{access_token:'synthetic'},signal:new AbortController().signal,isCurrent:()=>true,release(){}}),publish:s=>states.push(s)});
 await c.load(org,null,0);assert.equal(states.at(-1).kind,'unavailable');assert.equal(c.invalidate(),false);assert.equal(calls,1);await c.load(org,null,1);const old=c.load(org,null,1);assert.equal(c.invalidate(),false);assert.equal(states.at(-1).kind,'retained');pending.resolve({ok:true,value:{...value,selected:{status:'obsolete'}}});await old;assert.equal(states.at(-1).kind,'retained');assert.equal(calls,3);c.dispose();
});

test('returning exactly to acknowledged input starts a fresh idle window for later edits',async()=>{
 const h=harness();h.edit('temporary');await h.advance(500);h.edit('');assert.equal(h.state.status,'saved');await h.advance(6000);h.edit('new dirty period');await h.advance(999);assert.equal(h.commands.length,0);await h.advance(1);assert.equal(h.commands.length,1);assert.equal(h.commands[0].input.note,'new dirty period');h.c.dispose();
});
test('Review releases its busy flag after protected authentication invalidates execution, retaining exact input until explicit retry',async()=>{
 const late=deferred();let reads=0,saves=0;const h=harness({saveDraft:async()=>{saves++;return{ok:false,error_id:'leave.draft_revision_conflict'};},readDraft:()=>++reads===1?late.promise:Promise.resolve(ok(initial()))});
 const input={...emptyInput(),note:' retained 😀 e\u0301 ',hours:{date:{text:'24/09/',format:'dmy_numeric_v1'},duration:{text:'1,5',format:'decimal_hours_dot_v1'}}};h.c.change(input);await h.advance(1000);
 const reviewing=h.c.review();assert.equal(h.state.reviewing,true);h.c.protectedFailure('authentication_required');await reviewing;
 assert.equal(h.state.reviewing,false);assert.equal(h.state.status,'auth_required');assert.deepEqual(h.state.input,input);assert.equal(reads,1);
 late.resolve(ok({...initial(),input:{...emptyInput(),note:'stale response'}}));await settle();assert.deepEqual(h.state.input,input);assert.equal(h.state.status,'auth_required');await h.advance(20000);assert.equal(reads,1);assert.equal(saves,1);
 await h.c.review();assert.equal(reads,2);assert.equal(h.state.reviewing,false);assert.equal(h.state.status,'saved');assert.equal(h.state.input.note,'');h.c.dispose();
});
test('Review without acquisition releases its busy flag and rechecks only on explicit retry',async()=>{
 let reads=0,saves=0;const h=harness({saveDraft:async()=>{saves++;return{ok:false,error_id:'leave.draft_revision_conflict'};},readDraft:async()=>{reads++;return ok(initial());}});h.edit('keep exact local input');await h.advance(1000);h.setAvailable(false);await h.c.review();
 assert.equal(h.state.reviewing,false);assert.equal(h.state.status,'auth_required');assert.equal(h.state.input.note,'keep exact local input');assert.equal(reads,0);h.setAvailable(true);await h.advance(20000);assert.equal(reads,0);assert.equal(saves,1);
 await h.c.review();assert.equal(reads,1);assert.equal(h.state.status,'saved');assert.equal(h.state.reviewing,false);h.c.dispose();
});
test('Review completion after disposal publishes no state and never writes',async()=>{
 const late=deferred();let saves=0;const h=harness({saveDraft:async()=>{saves++;return{ok:false,error_id:'leave.draft_revision_conflict'};},readDraft:()=>late.promise});h.edit('local');await h.advance(1000);const reviewing=h.c.review();h.c.dispose();const count=h.states.length;late.resolve(ok(initial()));await reviewing;assert.equal(h.states.length,count);assert.equal(saves,1);
});
