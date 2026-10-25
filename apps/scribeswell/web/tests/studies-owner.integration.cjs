// Actual Auth and private HTTP throughout. No routes, fabricated sessions or tokens.
const {test,expect}=require('@playwright/test');
const {safeScenario}=require('./studies-owner-reporter.cjs');
const {credentialInspection}=require('./studies-owner-privacy.cjs');
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const fixture=JSON.parse(fs.readFileSync(process.env.SCRIBESWELL_OWNER_FIXTURE,'utf8'));
const proof=path.dirname(process.env.SCRIBESWELL_OWNER_FIXTURE);
function stage(name){fs.appendFileSync(path.join(proof,'browser-stages.jsonl'),JSON.stringify({stage:name})+'\n',{mode:0o600});}
const text='בְּרֵאשִׁית — e\u0301 שָׁלוֹם';
async function checkpoint(name){
 fs.writeFileSync(path.join(proof,name+'-check.json'),JSON.stringify({ready:true}),{flag:'wx',mode:0o600});
 const deadline=Date.now()+30000;
 while(!fs.existsSync(path.join(proof,name+'-observed.json'))){if(Date.now()>deadline)throw Error('Independent SQL observation unavailable');await new Promise(resolve=>setTimeout(resolve,50));}
}
function inspection(){return credentialInspection([fixture.service_key_sentinel,fixture.provider_service_sentinel]);}
async function request(page,route,method='GET',body){
 const response=await page.evaluate(async({route,method,body})=>{
  const {supabase}=await import('/src/lib/supabase.ts');const {data}=await supabase.auth.getSession();
  const response=await fetch(route,{method,headers:{Authorization:'Bearer '+data.session.access_token,'Content-Type':'application/json'},...(body?{body:JSON.stringify(body)}:{})});
  return {status:response.status,body:await response.json(),cache:response.headers.get('cache-control')};
 },{route,method,body});
 const known=['authentication_required','studies_access_denied','studies_access_unavailable','resource_unavailable','note_revision_conflict','operation_payload_mismatch','operation_unresolved','studies_storage_unavailable','request_deadline_exceeded','scribeswell_personal_notes_input_invalid'];
 fs.appendFileSync(path.join(proof,'http-observations.jsonl'),JSON.stringify({path:new URL(route,'http://localhost:5188').pathname,method,status:response.status,code:known.includes(response.body.code)?response.body.code:null})+'\n',{mode:0o600});
 return response;
}
async function login(page,account){
 const statuses=[];
 page.on('response',response=>{const u=new URL(response.url());if(['/auth/v1/verify','/auth/v1/user'].includes(u.pathname))statuses.push({path:u.pathname,status:response.status()});});
 try{
  try{await page.goto(account.link);}catch{throw Error('Provider callback navigation failed');}
  await expect(page.getByRole('button',{name:'Sign out',exact:true})).toBeVisible();
  await expect.poll(()=>new URL(page.url()).hash==='').toBe(true);
  stage('provider-callback-confirmed');
 }catch{
  const u=new URL(page.url());
  const observation={stage:'provider-callback-failed',origin:u.origin,path:u.pathname,query_keys:[...new URLSearchParams(u.search).keys()],fragment_keys:[...new URLSearchParams(u.hash.slice(1)).keys()],statuses};
  // Only selected booleans and endpoint/status fields; never URLs with values,
  // provider error bodies, tokens, email, page DOM or session contents.
  observation.sign_in_visible=await page.getByRole('button',{name:'Sign in',exact:true}).first().isVisible().catch(()=>false);
  observation.callback_notice=await page.getByText(/This confirmation link is invalid/).isVisible().catch(()=>false);
  fs.appendFileSync(path.join(proof,'browser-stages.jsonl'),JSON.stringify(observation)+'\n',{mode:0o600});
  throw Error('Provider callback was not acknowledged');
 }
}

if(!process.env.SCRIBESWELL_OWNER_DENIED){
 test('actual owner enrollment, lost completed replies, editor autosave, reload and second-account isolation',safeScenario(async({browser,page})=>{
  const privacy=inspection();privacy.inspect(page.context());
  stage('first-provider-callback');await login(page,fixture.accounts[0]);
  stage('public-reader');await expect(page.getByText('בְּרֵאשִׁית',{exact:true}).first()).toBeVisible();
  stage('before-enrollment-denial');const denied=await request(page,'/api/studies');expect(denied.status).toBe(503);expect(denied.body.code).toBe('studies_access_unavailable');
  await checkpoint('pre-enrollment');
  await page.getByRole('button',{name:'Studies',exact:true}).click();
  stage('ui-enrollment-create');
  const enrollmentReply=page.waitForResponse(response=>new URL(response.url()).pathname==='/api/studies/enrollment'&&response.request().method()==='POST');
  await page.getByRole('button',{name:'Start a study',exact:true}).click();
  const uiEnrollment=await(await enrollmentReply).json();expect(uiEnrollment.result.disposition).toBe('created');
  await page.getByLabel('Study title (optional)').fill('UI study');
  const createReply=page.waitForResponse(response=>new URL(response.url()).pathname==='/api/studies'&&response.request().method()==='POST');
  await page.getByRole('button',{name:'Create study',exact:true}).click();
  const uiCreated=await(await createReply).json();const study=uiCreated.study_id;
  await expect(page.getByRole('button',{name:'Add note',exact:true})).toBeVisible();
  // A completed HTTP response is deliberately discarded, then original operation retried.
  stage('enrollment-completed-reply-retry');const enrollment={operation_id:crypto.randomUUID()};
  expect((await request(page,'/api/studies/enrollment','POST',enrollment)).status).toBe(200);
  const replay=await request(page,'/api/studies/enrollment','POST',enrollment);expect(replay.status).toBe(200);expect(replay.body.operation_id).toBe(enrollment.operation_id);expect(replay.body.result.disposition).toBe('unchanged');
  stage('create-completed-reply-retry');const create={operation_id:crypto.randomUUID(),title:'Lost reply study'};
  expect((await request(page,'/api/studies','POST',create)).status).toBe(200);
  const retried=await request(page,'/api/studies','POST',create);expect(retried.status).toBe(200);
  expect(retried.body.operation_id).toBe(create.operation_id);const retryStudy=retried.body.study_id;expect(retryStudy===study).toBe(false);
  await page.reload();await page.getByRole('button',{name:'Studies',exact:true}).click();
  await page.getByRole('button',{name:'UI study',exact:true}).click();
  await page.getByRole('button',{name:'Add note',exact:true}).click();
  stage('editor-autosave');const editor=page.getByLabel('Note text',{exact:true});await editor.fill(text);
  await expect(page.getByRole('status').filter({hasText:'Draft saved'})).toBeVisible();
  const notes=await request(page,`/api/studies/${study}/notes`);expect(notes.status).toBe(200);expect(notes.body.items.length===1).toBe(true);
  const note=notes.body.items[0];expect(JSON.stringify(note.value).includes(text)).toBe(true);
  await page.reload();await page.getByRole('button',{name:'Studies',exact:true}).click();await page.getByRole('button',{name:'UI study',exact:true}).click();
  await page.getByRole('button',{name:text,exact:true}).click();expect(await editor.textContent()===text).toBe(true);
  stage('rename-preserves-note');await checkpoint('rename-before');
  await page.getByRole('button',{name:'Back to Studies',exact:true}).click();await page.getByRole('button',{name:'Rename',exact:true}).click();
  await page.getByLabel('Title',{exact:true}).fill('Renamed English שָׁלוֹם');
  const renameReply=page.waitForResponse(response=>new URL(response.url()).pathname===`/api/studies/${study}/title`&&response.request().method()==='PUT');
  await page.getByRole('button',{name:'Save',exact:true}).click();const renameAck=await(await renameReply).json();expect(renameAck.command).toBe('study.rename');expect(renameAck.revision).toBe('2');
  await expect(page.getByRole('heading',{name:'Renamed English שָׁלוֹם',exact:true})).toBeVisible();
  const afterRename=await request(page,`/api/studies/${study}/notes/${note.id}`);expect(JSON.stringify(afterRename.body)===JSON.stringify(note)).toBe(true);
  fs.writeFileSync(path.join(proof,'rename-result.json'),JSON.stringify({study,title:'Renamed English שָׁלוֹם',operation:renameAck.operation_id}),{flag:'wx',mode:0o600});await checkpoint('rename-after');
  await page.reload();await page.getByRole('button',{name:'Studies',exact:true}).click();await page.getByRole('button',{name:'Renamed English שָׁלוֹם',exact:true}).click();
  await page.getByRole('button',{name:text,exact:true}).click();expect(await editor.textContent()===text).toBe(true);
  stage('collect-reopen-remove-passages');await checkpoint('passages-before');
  await page.getByRole('button',{name:'Back to Studies',exact:true}).click();
  const passageOperations=[];
  for(const reference of ['Genesis1','Matthew26:63–64']){
   await page.getByRole('button',{name:'Add passage',exact:true}).click();await page.getByLabel('Passage reference',{exact:true}).fill(reference);
   const response=page.waitForResponse(reply=>new URL(reply.url()).pathname===`/api/studies/${study}/passages`&&reply.request().method()==='PUT');await page.getByLabel('Passage reference',{exact:true}).press('Enter');passageOperations.push((await(await response).json()).operation_id);
   await expect(page.getByRole('button',{name:'Add passage',exact:true})).toBeEnabled();
  }
  await page.getByRole('button',{name:'Add passage',exact:true}).click();await page.getByLabel('Passage reference',{exact:true}).fill('Genesis1');await page.getByLabel('Passage reference',{exact:true}).press('Enter');await expect(page.getByRole('alert')).toContainText('Already in this study');await page.getByRole('button',{name:'Cancel',exact:true}).click();
  const removal=page.waitForResponse(reply=>new URL(reply.url()).pathname===`/api/studies/${study}/passages`&&reply.request().method()==='PUT');await page.getByRole('button',{name:'Remove Genesis 1',exact:true}).click();passageOperations.push((await(await removal).json()).operation_id);
  await expect(page.getByRole('list',{name:'Passages',exact:true}).locator('li')).toHaveCount(1);
  const collected=await request(page,`/api/studies/${study}/passages`);expect(collected.status).toBe(200);expect(collected.body.revision).toBe('4');const passageItem=collected.body.items[0];
  fs.writeFileSync(path.join(proof,'passages-result.json'),JSON.stringify({study,operations:passageOperations,item:passageItem}),{flag:'wx',mode:0o600});await checkpoint('passages-after');
  await page.reload();await page.getByRole('button',{name:'Studies',exact:true}).click();await page.getByRole('button',{name:'Renamed English שָׁלוֹם',exact:true}).click();await expect(page.getByRole('list',{name:'Passages',exact:true})).toContainText('Matthew 26:63–64');
  await page.getByRole('button',{name:'Open Matthew 26:63–64',exact:true}).click();await expect(page.getByText('Matthew 26:63–64 — Text unavailable',{exact:true})).toBeVisible();
  expect((await request(page,`/api/studies/${study}/notes/${note.id}`)).body).toEqual(note);
  stage('second-account-isolation');const context=await browser.newContext();privacy.inspect(context);const other=await context.newPage();await login(other,fixture.accounts[1]);
  const otherEnrollment=crypto.randomUUID();const otherAck=await request(other,'/api/studies/enrollment','POST',{operation_id:otherEnrollment});expect(otherAck.status).toBe(200);
  await checkpoint('foreign-before');
  for(const route of [`/api/studies/${study}/passages`,`/api/studies/${study}`,`/api/studies/${study}/notes/${note.id}`])expect((await request(other,route)).status).toBe(404);
  expect((await request(other,`/api/studies/${study}/passages`,'PUT',{operation_id:crypto.randomUUID(),expected_revision:'4',items:[]})).status).toBe(404);
  expect((await request(other,`/api/operations/${passageOperations[0]}?command=study.passages.replace`)).body.status).toBe('unresolved');
  expect((await request(other,`/api/studies/${study}/notes`)).status).toBe(404);
  expect((await request(other,`/api/studies/${study}/title`,'PUT',{operation_id:crypto.randomUUID(),expected_revision:'2',title:'Forbidden rename'})).status).toBe(404);
  expect((await request(other,`/api/operations/${renameAck.operation_id}?command=study.rename`)).body.status).toBe('unresolved');
  expect((await request(other,`/api/studies/${study}/notes`,'POST',{operation_id:crypto.randomUUID(),value:note.value})).status).toBe(404);
  expect((await request(other,`/api/studies/${study}/notes/${note.id}`,'PUT',{operation_id:crypto.randomUUID(),expected_revision:note.revision,value:note.value})).status).toBe(404);
  expect((await request(other,`/api/operations/${create.operation_id}?command=study.create`)).body.status).toBe('unresolved');
  expect((await request(other,'/api/studies')).body.items.length===0).toBe(true);
  await checkpoint('foreign-after');
  await privacy.settle();
  const stored=await context.storageState();fs.writeFileSync(path.join(proof,'other-context-private.json'),JSON.stringify(stored),{flag:'wx',mode:0o600});await context.close();
  fs.writeFileSync(path.join(proof,'owner-context-private.json'),JSON.stringify(await page.context().storageState()),{flag:'wx',mode:0o600});
  const result={study,passage_operations:passageOperations,passage_item:passageItem,rename_operation:renameAck.operation_id,rename_title:'Renamed English שָׁלוֹם',retry_study:retryStudy,note:note.id,operation:create.operation_id,ui_operation:uiCreated.operation_id,enrollment:enrollment.operation_id,ui_enrollment:uiEnrollment.operation_id,other_enrollment:otherEnrollment,account_actors:{[fixture.accounts[0].account_id]:uiEnrollment.result.actor_id,[fixture.accounts[1].account_id]:otherAck.body.result.actor_id},value:note.value,credential_inspection:await privacy.settle()};
  fs.writeFileSync(path.join(proof,'browser-result.json'),JSON.stringify(result),{flag:'wx',mode:0o600});
 }));
}else{
 test('disabled authority refuses read write lookup and enrollment replay; public reading works',safeScenario(async({browser})=>{
  stage('disabled-authority');const result=JSON.parse(fs.readFileSync(path.join(proof,'browser-result.json'),'utf8'));
  const privacy=inspection();
  const context=await browser.newContext({storageState:path.join(proof,'owner-context-private.json')});privacy.inspect(context);const page=await context.newPage();await page.goto('/');
  for(const route of ['/api/studies',`/api/studies/${result.study}`,`/api/operations/${result.operation}?command=study.create`])expect((await request(page,route)).status).toBe(403);
  expect((await request(page,`/api/studies/${result.study}/passages`)).status).toBe(403);
  expect((await request(page,`/api/studies/${result.study}/passages`,'PUT',{operation_id:crypto.randomUUID(),expected_revision:'4',items:[]})).status).toBe(403);
  expect((await request(page,`/api/operations/${result.passage_operations[0]}?command=study.passages.replace`)).status).toBe(403);
  expect((await request(page,`/api/studies/${result.study}/title`,'PUT',{operation_id:result.rename_operation,expected_revision:'1',title:result.rename_title})).status).toBe(403);
  expect((await request(page,`/api/operations/${result.rename_operation}?command=study.rename`)).status).toBe(403);
  expect((await request(page,'/api/studies','POST',{operation_id:result.operation,title:'Lost reply study'})).status).toBe(403);
  expect((await request(page,`/api/studies/${result.study}/notes/${result.note}`,'PUT',{operation_id:crypto.randomUUID(),expected_revision:'2',value:result.value})).status).toBe(403);
  expect((await request(page,'/api/studies/enrollment','POST',{operation_id:result.enrollment})).status).toBe(403);
  stage('public-reader');await expect(page.getByText('בְּרֵאשִׁית',{exact:true}).first()).toBeVisible();
  const anonymous=await browser.newContext();privacy.inspect(anonymous);const publicPage=await anonymous.newPage();await publicPage.goto('/');
  await expect(publicPage.getByRole('button',{name:'Sign in',exact:true})).toBeVisible();await expect(publicPage.getByText('בְּרֵאשִׁית',{exact:true}).first()).toBeVisible();
  await privacy.settle();await anonymous.close();await context.close();
  fs.writeFileSync(path.join(proof,'browser-denial-result.json'),JSON.stringify({read_write_lookup_enrollment_denied:true,public_reader_available:true,anonymous_public_reader_available:true,credential_inspection:{leaked:false,complete:true}}),{flag:'wx',mode:0o600});
 }));
}
