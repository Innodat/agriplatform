// GENERATED E1-CHOICES: input preservation, lease freshness and typed private reads.
import {test} from 'node:test';
import assert from 'node:assert/strict';
import {emptyInput,isDraftInput} from '../src/draft-input.ts';
import {chooseType,repairChoices} from '../src/choice-selection.ts';
import {createChoicesController} from '../src/choices-controller.ts';
import {createLeaveClient} from '../src/api/leave.ts';
const org='11111111-1111-4111-8111-111111111111',type='22222222-2222-4222-8222-222222222222',other='33333333-3333-4333-8333-333333333333';
const choice={type_id:type,version_id:other,name:'Annual',revision:'1',permitted_modes:['full_days','half_day','hours']};
const available={choices:[choice],next_cursor:null,selected:{status:'available',choice}};
function input(){const v=emptyInput();v.full_days.start.text='24/09/';v.half_day.date.text=' 1/1/2020 ';v.hours.duration.text='1.';v.note='😀 e\u0301\nindependent';return v;}
test('canonical input-v1 empty shape and Unicode bounds',()=>{const v=input();assert.ok(isDraftInput(v));assert.equal(v.duration_mode,null);assert.equal(v.leave_type_id,null);assert.ok(isDraftInput({...v,note:'😀'.repeat(4000)}));for(const invalid of [{...v,note:'😀'.repeat(4001)},{...v,input_version:2},{...v,extra:true},{...v,note:'\u0000'}])assert.equal(isDraftInput(invalid),false);});
test('only transient first new choice can initialize full days',()=>{
 const v=input(),first=chooseType(v,choice,true);assert.equal(first.input.duration_mode,'full_days');assert.equal(first.firstChoiceEligible,false);assert.deepEqual({...first.input,leave_type_id:null,duration_mode:null},v);
 assert.equal(chooseType(v,choice,false).input.duration_mode,null);
 assert.equal(chooseType(v,{...choice,permitted_modes:['hours']},true).input.duration_mode,null);
 assert.equal(chooseType({...v,duration_mode:'hours'},choice,true).input.duration_mode,'hours');
});
test('repair clears only definitive obsolete selection or disallowed mode; read-only preserves',()=>{
 const v={...input(),leave_type_id:type,duration_mode:'hours'};
 const obsolete=repairChoices(v,{choices:[],next_cursor:null,selected:{status:'obsolete'}},true);assert.deepEqual(obsolete.input,{...v,leave_type_id:null,duration_mode:null});assert.match(obsolete.notice,/choose a leave type again/);
 const restricted=repairChoices(v,{...available,selected:{status:'available',choice:{...choice,permitted_modes:['full_days']}}},true);assert.deepEqual(restricted.input,{...v,duration_mode:null});
 assert.deepEqual(repairChoices(v,{choices:[],next_cursor:null,selected:{status:'not_requested'}},true).input,v);
 assert.deepEqual(repairChoices(v,{choices:[],next_cursor:null,selected:{status:'obsolete'}},false).input,v);
});
function fixture(client){let current=true;const abort=new AbortController(),states=[];let released=0;const controller=createChoicesController({client,acquire:()=>({session:{account_id:other,access_token:'private'},signal:abort.signal,isCurrent:()=>current,release(){released++;}}),publish:s=>states.push(s)});return {controller,states,released:()=>released,revoke(){current=false;abort.abort();}};}
test('input generation, newer refresh, account invalidation and disposal drop delayed metadata',async()=>{
 for(const action of ['input','refresh','account','dispose']){let finish;let calls=0;const f=fixture({choices:async()=>++calls===1?new Promise(r=>finish=r):{ok:true,value:available}});const old=f.controller.load(org,type,0);if(action==='input')f.controller.invalidate();if(action==='refresh')await f.controller.load(org,type,1);if(action==='account')f.revoke();if(action==='dispose')f.controller.dispose();finish({ok:true,value:available});await old;assert.equal(f.states.filter(s=>s.kind==='resolved').length,action==='refresh'?1:0);assert.equal(f.released(),action==='refresh'?2:1);}
});
test('outage preserves current input and retry obtains a fresh observation',async()=>{let calls=0;const f=fixture({choices:async()=>++calls===1?{ok:false,error_id:'dependency_unavailable'}:{ok:true,value:available}});await f.controller.load(org,type,0);assert.equal(f.states.at(-1).kind,'unavailable');await f.controller.load(org,type,0);assert.equal(f.states.at(-1).kind,'resolved');});
test('client validates private closed scoped choice pages, selected independent of page',async()=>{
 let request;const c=createLeaveClient(async(url,options)=>{request={url,options};return Response.json({...available,choices:[]});});const result=await c.choices('private',new AbortController().signal,org,type,null);assert.equal(result.ok,true);assert.equal(request.url,'/api/v1/organizations/'+org+'/draft-choices?selected_type_id='+type);assert.equal(request.options.cache,'no-store');
 for(const invalid of [{...available,extra:true},{...available,choices:[{...choice,permitted_modes:[]}]},{...available,selected:{status:'available',choice:{...choice,type_id:other}}},{...available,choices:[{...choice,name:'bad\nname'}]},{...available,choices:[{...choice,revision:'0'}]}])assert.equal((await createLeaveClient(async()=>Response.json(invalid)).choices('x',new AbortController().signal,org,type,null)).ok,false);
});
test('every nonempty permitted-mode subset preserves independent and inactive values',()=>{
 const modes=['full_days','half_day','hours'];
 for(let mask=1;mask<8;mask++){
  const permitted_modes=modes.filter((_,index)=>mask&(1<<index));const configured={...choice,permitted_modes};
  const v=input();const first=chooseType(v,configured,true);assert.equal(first.input.duration_mode,permitted_modes.includes('full_days')?'full_days':null);
  for(const duration_mode of modes){const existing={...v,leave_type_id:type,duration_mode};const repair=repairChoices(existing,{...available,selected:{status:'available',choice:configured}},true);assert.deepEqual(repair.input,{...existing,duration_mode:permitted_modes.includes(duration_mode)?duration_mode:null});}
 }
});
test('selected available metadata does not depend on list membership or present date',()=>{const v={...input(),leave_type_id:type,duration_mode:'hours'};assert.equal(repairChoices(v,{...available,choices:[]},true).input,v);});
test('valid maximum Unicode choice page fits the Choices-specific response bound',async()=>{
 const page={choices:Array.from({length:100},(_,index)=>({...choice,type_id:'00000000-0000-4000-8000-'+String(index+1).padStart(12,'0'),name:'😀'.repeat(120),revision:'9223372036854775807'})),next_cursor:null,selected:{status:'not_requested'}};
 assert.ok(new TextEncoder().encode(JSON.stringify(page)).length>65536);
 const result=await createLeaveClient(async()=>Response.json(page)).choices('private',new AbortController().signal,org,null,null);assert.equal(result.ok,true);assert.deepEqual(result.value,page);
});
test('Choices accepts exactly128KiB and rejects larger bodies while other reads retain64KiB',async()=>{
 const page={choices:[],next_cursor:null,selected:{status:'not_requested'}};
 const padded=(value,limit)=>{const raw=JSON.stringify(value);return raw+' '.repeat(limit-new TextEncoder().encode(raw).length);};
 assert.deepEqual(await createLeaveClient(async()=>new Response(padded(page,131072))).choices('private',new AbortController().signal,org,null,null),{ok:true,value:page});
 assert.deepEqual(await createLeaveClient(async()=>new Response(padded(page,131073))).choices('private',new AbortController().signal,org,null,null),{ok:false,error_id:'api_unavailable'});
 const language={preferred_locale:'en',revision:'1'};
 assert.deepEqual(await createLeaveClient(async()=>new Response(padded(language,65536))).language('private',new AbortController().signal),{ok:true,value:language});
 assert.deepEqual(await createLeaveClient(async()=>new Response(padded(language,65537))).language('private',new AbortController().signal),{ok:false,error_id:'api_unavailable'});
});
test('duration input cancels pending refresh into the retained observation without stale repair or another request',async()=>{
 let finish,calls=0;const f=fixture({choices:async()=>++calls===1?{ok:true,value:available}:new Promise(r=>finish=r)});
 await f.controller.load(org,type,0);const pending=f.controller.load(org,type,0);assert.equal(f.states.at(-1).kind,'loading');
 f.controller.invalidate();assert.equal(f.states.at(-1).kind,'retained');assert.equal(f.states.at(-1).value,available);assert.equal(calls,2);
 finish({ok:true,value:{choices:[],next_cursor:null,selected:{status:'obsolete'}}});await pending;
 assert.equal(f.states.at(-1).kind,'retained');assert.equal(f.states.filter(s=>s.kind==='resolved').length,1);
});
test('type and duration reset guidance survives settled automatic observations until the relevant choice resolves it',async()=>{
 const {selectionNotice}=await import('../src/choices-controller.ts');
 for(const [message,value,repaired] of [['Please choose a leave type again.',{...input(),leave_type_id:null,duration_mode:null},{...input(),leave_type_id:type,duration_mode:null}],['Please choose a duration again.',{...input(),leave_type_id:type,duration_mode:null},{...input(),leave_type_id:type,duration_mode:'hours'}]]){
  assert.equal(selectionNotice(message,null,value),message);assert.equal(selectionNotice(message,null,value),message);assert.equal(selectionNotice(message,null,repaired),null);
 }
});
test('FEFF remains a valid name character and Python boundary whitespace is rejected by the API client',async()=>{
 for(const [name,ok] of [['\ufeffAnnual\ufeff',true],['\u00a0Annual',false],['Annual\u00a0',false],['\u2003Annual',false],['Annual\u200b',true]]){
  const value={...available,choices:[{...choice,name}],selected:{status:'available',choice:{...choice,name}}};assert.equal((await createLeaveClient(async()=>Response.json(value)).choices('private',new AbortController().signal,org,type,null)).ok,ok,name);
 }
});
