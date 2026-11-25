import {test} from 'node:test';
import assert from 'node:assert/strict';
import {createLeaveClient} from '../src/api/leave.ts';
import {emptyInput} from '../src/draft-input.ts';
const org='6a88b25b-b457-4f9b-a9df-68fa17ac62d1',draft='66ebcf3c-9280-4b9d-8cb7-86e305210349',operation='3d2529ac-ce29-49f1-8d8d-e4abc9834438';
const committed={operation_id:operation,status:'committed',result:{command:'save',draft_id:draft,revision:'2',scope_generation:'0',disposition:'saved'}};
const response=(value,status=200)=>new Response(JSON.stringify(value),{status});
const command={operation_id:operation,expected_revision:'1',input:emptyInput()};
test('save uses owning PUT with complete exact input and compact save response',async()=>{
 let sent;const client=createLeaveClient(async(path,options)=>{sent={path,...options};return response(committed);});
 command.input.note=' 😀 e\u0301 \n';const r=await client.saveDraft('synthetic',new AbortController().signal,org,draft,command);
 assert.equal(r.ok,true);assert.equal(sent.path,'/api/v1/organizations/'+org+'/drafts/'+draft+'/input');assert.equal(sent.method,'PUT');assert.deepEqual(JSON.parse(sent.body),command);assert.equal(sent.cache,'no-store');
});
test('outcome lookup accepts either command while mutation endpoints bind command and target',async()=>{
 const client=createLeaveClient(async()=>response(committed)),signal=new AbortController().signal;
 assert.equal((await client.draftOutcome('s',signal,org,operation)).ok,true);
 assert.deepEqual(await client.startDraft('s',signal,org,{operation_id:operation,expected_scope_generation:'0'}),{ok:false,error_id:'invalid_response'});
 const start={...committed,result:{...committed.result,command:'start',disposition:'created'}};
 assert.deepEqual(await createLeaveClient(async()=>response(start)).saveDraft('s',signal,org,draft,command),{ok:false,error_id:'invalid_response'});
 assert.deepEqual(await client.saveDraft('s',signal,org,operation,command),{ok:false,error_id:'invalid_response'});
});
test('strict declared errors accept revision and fields, refuse unknown paths/rules/empty domain details',async()=>{
 for(const [error_id,details] of [['leave.draft_revision_conflict',{current_revision:'2'}],['leave.draft_discarded',{draft_id:draft}],['validation_failed',{fields:[{path:'input.note',rule:'too_long'}]}]]){
  const r=await createLeaveClient(async()=>response({error_id,error:'safe',details},409)).saveDraft('s',new AbortController().signal,org,draft,command);assert.deepEqual(r,{ok:false,error_id,details});
 }
 for(const details of [{},{current_revision:2},{current_revision:'0'}])assert.deepEqual(await createLeaveClient(async()=>response({error_id:'leave.draft_revision_conflict',error:'safe',details},409)).saveDraft('s',new AbortController().signal,org,draft,command),{ok:false,error_id:'invalid_response'});
 for(const fields of [[{path:'input.secret',rule:'too_long'}],[{path:'input.note',rule:'arbitrary'}],[{path:'input.note',rule:'too_long',input:'secret'}]])assert.deepEqual(await createLeaveClient(async()=>response({error_id:'validation_failed',error:'safe',details:{fields}},422)).saveDraft('s',new AbortController().signal,org,draft,command),{ok:false,error_id:'invalid_response'});
});
test('PUT mutation has the same 12-second transport bound as POST',async()=>{
 const original=setTimeout;let delay;globalThis.setTimeout=(fn,ms,...args)=>{delay=ms;return original(fn,ms,...args);};
 try{await createLeaveClient(async()=>response(committed)).saveDraft('s',new AbortController().signal,org,draft,command);assert.equal(delay,12000);}finally{globalThis.setTimeout=original;}
});

test('start recovery refuses a save acknowledgement from the generic operation lookup',async()=>{
 const {createDraftController}=await import('../src/draft-controller.ts');let reads=0;const states=[];const lease=new AbortController();
 const controller=createDraftController({client:{draftContext:async()=>({ok:true,value:{status:'ready',org_id:org,employment_id:org,scope_generation:'0',active_draft:null,editability:{status:'editable'},setup_notices:[]}}),startDraft:async()=>({ok:false,error_id:'api_unavailable'}),draftOutcome:async()=>({ok:true,value:committed}),editorOpen:async()=>{reads++;return{ok:false,error_id:'resource_not_found'};}},acquire:()=>({session:{access_token:'synthetic'},signal:lease.signal,isCurrent:()=>true,release(){}}),publish:value=>states.push(value),newId:()=>operation});
 try{await controller.load(org);await controller.apply();assert.equal(reads,0);assert.equal(states.at(-1).kind,'denied');}finally{controller.dispose();}
});
