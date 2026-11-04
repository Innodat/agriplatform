const {test,expect}=require('@playwright/test');
test.setTimeout(12000);
const account='10000000-0000-4000-8000-000000000001',actor='20000000-0000-4000-8000-000000000001';
const study='30000000-0000-4000-8000-000000000001',note='40000000-0000-4000-8000-000000000001';
const session={access_token:'current',refresh_token:'fixture',expires_at:Date.now()/1000+3600,expires_in:3600,token_type:'bearer',user:{id:account,email:'reader@example.invalid',aud:'authenticated',app_metadata:{},user_metadata:{}}};
const attribution={owner_account_id:account,created_at:'2026-10-23T10:00:00.000000Z',updated_at:'2026-10-23T10:00:00.000000Z',created_by_actor_id:actor,updated_by_actor_id:actor};
async function setup(page,options={}){
 await page.route('**/auth/v1/user*',r=>{const token=r.request().headers().authorization?.replace(/^Bearer /,''),sameOwner=['current','renewed-current','fresh-same-account','renewed-study-review'].includes(token),user=token==='other-account'?{...session.user,id:'10000000-0000-4000-8000-000000000002'}:sameOwner?session.user:null;return r.fulfill(user?{json:user}:{status:401,json:{error_code:'session_not_found',msg:'Synthetic session unavailable'}});});
 await page.route('**/auth/v1/logout*',r=>r.fulfill({json:{}}));
 await page.addInitScript(s=>localStorage.setItem('pts-auth',JSON.stringify(s)),session);
 await page.route('http://127.0.0.1:8001/**',r=>r.fulfill({json:[]}));
 await page.route('**/api/bible/**',r=>{const path=new URL(r.request().url()).pathname;const b={id:1,osis_id:'Gen',name_en:'Genesis',name_he:'בראשית',testament:'OT',book_order:1};const w={id:1,position:1,surface_he:'בְּרֵאשִׁית',display_he:'בְּרֵאשִׁית',lemma_strong:null,morph_code:null};return r.fulfill({json:path.endsWith('/books')?{data:[b],total:1}:path.endsWith('/books/Gen')?{...b,chapters:[{id:1,chapter_num:1}]}:path.includes('/words/')?{...w,morphemes:[]}:{data:[{id:1,verse_num:1,book_id:1,chapter_num:1,words:[w]}],total:1}});});
 const collection={study_id:study,revision:'1',items:[]};
 const metadata={title:'Untitled study',revision:'1'};
 let saved={document:{version:1,blocks:[]},connections:[],highlights:[]},created=false,noteCreated=false,revision='1',requests=[],operations=new Map();
 await page.route('**/api/operations/**',async r=>{if(options.beforeLookup)await options.beforeLookup();const id=new URL(r.request().url()).pathname.split('/').pop();return r.fulfill({json:options.unresolved?{status:'unresolved'}:operations.has(id)?{status:'committed',outcome:operations.get(id)}:{status:'unresolved'}});});
 await page.route('**/api/studies**',async r=>{
  const req=r.request(),url=new URL(req.url()),path=url.pathname,method=req.method(),payload=req.postDataJSON();requests.push({path,method,payload});
  let data;
  if(path.endsWith('/context-notes')){data={items:[],next_cursor:null};}
  else if(path.endsWith('/'+study)&&method==='PUT'){metadata.title=payload.title;metadata.introduction=payload.introduction;metadata.source_url=payload.source_url;metadata.revision=String(Number(metadata.revision)+1);data={operation_id:payload.operation_id,command:'study.details.replace',study_id:study,note_id:null,revision:metadata.revision};}
  else if(path.endsWith('/search')){if(options.search)return options.search(r,payload);data={items:created?[{...attribution,id:study,title:metadata.title,revision:metadata.revision}]:[],next_cursor:null};}
  else if(path.endsWith('/enrollment'))data={operation_id:payload.operation_id,status:'committed',result:{disposition:'created',account_id:account,actor_id:actor,permission:'scribeswell.studies.use'}};
  else if(path.endsWith('/passages')){
   if(method==='GET'){
    if(options.beforePassageRead)await options.beforePassageRead();
    if(options.failPassageRead)return r.fulfill({status:503,json:{code:'studies_storage_unavailable'}});
    data=collection;
   }else{
    if(options.beforePassagePut)await options.beforePassagePut();
    if(options.failPassages)return r.fulfill({status:options.failPassages,json:{code:options.failPassages===409?'passage_revision_conflict':options.failPassages===400?'scribeswell_personal_notes_input_invalid':options.failPassages===401?'authentication_required':options.failPassages===403?'studies_access_denied':options.failPassages===404?'resource_unavailable':'studies_storage_unavailable'}});
    if(operations.has(payload.operation_id))data=operations.get(payload.operation_id);
    else{if(payload.expected_revision!==collection.revision)return r.fulfill({status:409,json:{code:'passage_revision_conflict'}});if(JSON.stringify(payload.items)!==JSON.stringify(collection.items)){collection.items=payload.items;collection.revision=String(Number(collection.revision)+1);}data={operation_id:payload.operation_id,command:'study.passages.replace',study_id:study,note_id:null,revision:collection.revision};operations.set(payload.operation_id,data);}
    if(options.afterPassageCommit)options.afterPassageCommit();
    if(options.dropPassages){options.dropPassages=false;return r.abort('connectionreset');}
   }
  }
  else if(path.endsWith('/title')&&method==='PUT'){
   if(options.beforeRename)await options.beforeRename();
   if(options.failRename)return r.fulfill({status:options.failRename,json:{code:options.failRename===409?'study_revision_conflict':options.failRename===400?'scribeswell_personal_notes_input_invalid':options.failRename===401?'authentication_required':options.failRename===403?'studies_access_denied':'studies_storage_unavailable'}});
   if(operations.has(payload.operation_id))data=operations.get(payload.operation_id);
   else{if(metadata.title!==payload.title){metadata.title=payload.title;metadata.revision=String(Number(metadata.revision)+1);}data={operation_id:payload.operation_id,command:'study.rename',study_id:study,note_id:null,revision:metadata.revision};operations.set(payload.operation_id,data);}
   if(options.dropRename){options.dropRename=false;return r.abort('connectionreset');}
  }
  else if(path.endsWith('/'+study)&&method==='DELETE'){
   if(options.beforeStudyDelete)await options.beforeStudyDelete();
   if(options.failStudyDelete)return r.fulfill({status:options.failStudyDelete,json:{code:options.failStudyDeleteCode??(options.failStudyDelete===409?'study_revision_conflict':options.failStudyDelete===401?'authentication_required':options.failStudyDelete===403?'studies_access_denied':'studies_storage_unavailable')}});
   if(operations.has(payload.operation_id))data=operations.get(payload.operation_id);
   else{if(payload.expected_revision!==metadata.revision)return r.fulfill({status:409,json:{code:'study_revision_conflict'}});metadata.revision=String(Number(metadata.revision)+1);metadata.title='Deleted study';created=false;noteCreated=false;saved={document:{version:1,blocks:[]},connections:[],highlights:[]};collection.items=[];data={operation_id:payload.operation_id,command:'study.delete',study_id:study,note_id:null,revision:metadata.revision};operations.set(payload.operation_id,data);}
   if(options.dropStudyDelete){options.dropStudyDelete=false;return r.abort('connectionreset');}
  }
  else if(path.endsWith('/notes/'+note)&&method==='DELETE'){
   if(options.beforeDelete)await options.beforeDelete();
   if(options.failDelete)return r.fulfill({status:options.failDelete,json:{code:options.failDeleteCode??(options.failDelete===409?'note_revision_conflict':options.failDelete===401?'authentication_required':options.failDelete===403?'studies_access_denied':'studies_storage_unavailable')}});
   if(operations.has(payload.operation_id))data=operations.get(payload.operation_id);
   else{if(payload.expected_revision!==revision)return r.fulfill({status:409,json:{code:'note_revision_conflict'}});revision=String(Number(revision)+1);saved={document:{version:1,blocks:[]},connections:[],highlights:[]};noteCreated=false;data={operation_id:payload.operation_id,command:'note.delete',study_id:study,note_id:note,revision};operations.set(payload.operation_id,data);}
   if(options.dropDelete){options.dropDelete=false;return r.abort('connectionreset');}
  }
  else if(path.endsWith('/notes/'+note)&&method==='PUT'){if(options.beforePut)await options.beforePut();if(options.failPut)return r.fulfill({status:options.failPut,json:{code:options.failPutCode??(options.failPut===409?'note_revision_conflict':options.failPut===401?'authentication_required':options.failPut===403?'studies_access_denied':'studies_storage_unavailable')}});saved=payload.value;revision=String(Number(revision)+1);data={operation_id:payload.operation_id,command:'note.replace',study_id:study,note_id:note,revision};}
  else if(path.endsWith('/notes/'+note))data={...attribution,id:note,study_id:study,visibility:'study',value:saved,revision};
  else if(path.endsWith('/notes')&&method==='POST'){noteCreated=true;saved=options.noteValue??payload.value;data={operation_id:payload.operation_id,command:'note.create',study_id:study,note_id:note,revision};}
  else if(path.endsWith('/notes'))data={items:noteCreated?[{...attribution,id:note,study_id:study,visibility:'study',value:saved,revision}]:[],next_cursor:null};
  else if(method==='POST'){created=true;data={operation_id:payload.operation_id,command:'study.create',study_id:study,note_id:null,revision:'1'};}
  else if(path.endsWith('/'+study)){if(options.beforeStudyRead)await options.beforeStudyRead();data={...attribution,id:study,...metadata};}
  else data={items:created?[{...attribution,id:study,title:metadata.title,revision:metadata.revision}]:[],next_cursor:null};
  if(data.command)operations.set(data.operation_id,data);
  if(method==='PUT'&&options.dropPut){options.dropPut=false;return r.abort('connectionreset');}
  return r.fulfill({json:data,headers:{'cache-control':'private, no-store'}});
 });return {requests,metadata,collection,advanceNote:(value)=>{saved=value;revision=String(Number(revision)+1);}};
}
// Reload exercises the real device return: wait for acknowledged metadata, then
// current authorized hydration before any tool click can supersede that return.
async function firstNote(page){await page.goto('/');await expect(page.getByRole('tablist',{name:'Workspace tabs'})).toHaveAttribute('data-device-ready','true');await page.getByRole('button',{name:'Studies',exact:true}).click();await page.getByRole('button',{name:'Start a study',exact:true}).click();await page.getByRole('button',{name:'Create study',exact:true}).click();await page.getByRole('button',{name:'Add note',exact:true}).click();await expect(page.getByLabel('Note text',{exact:true})).toBeVisible();}

async function actions(page,name){await page.getByRole('button',{name,exact:true}).click();}
test('polish: confirmations are centered and bounded',async({page})=>{await setup(page);await firstNote(page);await actions(page,'Note actions');await page.getByRole('button',{name:'Delete note',exact:true}).click();const dialog=page.getByRole('dialog',{name:'Delete this note?'});await expect(dialog).toBeVisible();const rect=await dialog.boundingBox(),v=page.viewportSize();expect(Math.abs(rect.x+rect.width/2-v.width/2)).toBeLessThan(3);expect(Math.abs(rect.y+rect.height/2-v.height/2)).toBeLessThan(3);expect(rect.height).toBeLessThan(v.height);await dialog.getByRole('button',{name:'Cancel',exact:true}).click();await expect(page.getByRole('button',{name:'Note actions',exact:true})).toBeFocused();});
test('polish: secondary actions dismiss and preserve writing',async({page})=>{await setup(page,{failPut:503});await firstNote(page);const editor=page.getByLabel('Note text',{exact:true});await editor.fill('Keep this unfinished thought');await actions(page,'Note actions');await expect(page.getByRole('button',{name:'Duplicate note',exact:true})).toBeVisible();await expect(page.getByRole('button',{name:'Delete study',exact:true})).toBeHidden();await page.keyboard.press('Escape');await expect(page.getByRole('button',{name:'Duplicate note',exact:true})).toBeHidden();await expect(editor).toHaveText('Keep this unfinished thought');await expect(page.getByRole('button',{name:'Note actions',exact:true})).toBeFocused();await actions(page,'Note actions');await page.getByRole('heading',{name:'Notes',exact:true}).click();await expect(page.getByRole('button',{name:'Duplicate note',exact:true})).toBeHidden();});
test('polish: mobile editor and save feedback appear early',async({page})=>{test.skip(page.viewportSize().width>=768);await setup(page,{failPut:503});await firstNote(page);const editor=page.getByLabel('Note text',{exact:true}),rect=await editor.boundingBox();expect(rect.y).toBeLessThan(565);await editor.fill('Visible retry');const status=page.getByRole('status').filter({hasText:'Changes not saved'});await expect(status).toBeVisible();expect((await status.boundingBox()).y).toBeLessThan((await editor.boundingBox()).y);await expect(status.getByRole('button',{name:'Retry',exact:true})).toBeVisible();});
test('polish: opening Analysis shows the selected word and retains deliberate Notes',async({page})=>{await setup(page);await page.goto('/');await page.getByRole('button',{name:/Word:/}).first().click();await page.getByRole('button',{name:'Analysis',exact:true}).click();const tabs=page.getByRole('tablist',{name:'Analysis',exact:true});await expect(tabs.getByRole('tab',{name:'Word',exact:true})).toHaveAttribute('aria-selected','true');await tabs.getByRole('tab',{name:'Notes',exact:true}).click();await expect(tabs.getByRole('tab',{name:'Notes',exact:true})).toHaveAttribute('aria-selected','true');await page.getByRole('button',{name:'Analysis',exact:true}).click();await page.getByRole('button',{name:'Analysis',exact:true}).click();await expect(tabs.getByRole('tab',{name:'Word',exact:true})).toHaveAttribute('aria-selected','true');});

async function boundedDialog(page,dialog){
 await expect(dialog).toBeVisible();const box=await dialog.boundingBox(),v=page.viewportSize();
 expect(Math.abs(box.x+box.width/2-v.width/2)).toBeLessThan(3);
 expect(Math.abs(box.y+box.height/2-v.height/2)).toBeLessThan(3);
 expect(box.x).toBeGreaterThanOrEqual(15);expect(box.y).toBeGreaterThanOrEqual(15);
 expect(box.height).toBeLessThanOrEqual(v.height-30);
}
test('polish: short narrow screen keeps study actions and confirmations reachable',async({page})=>{
 await page.setViewportSize({width:320,height:568});await setup(page,{failPut:503});await firstNote(page);
 const editor=page.getByLabel('Note text',{exact:true});await editor.fill('Retain this narrow-screen draft');
 await actions(page,'Study actions');const command=page.getByRole('button',{name:'Delete study',exact:true});
 const menu=await command.locator('..').boundingBox(),inspector=page.getByRole('complementary',{name:'Study tools',exact:true}),panel=await inspector.boundingBox();
 expect(menu.x).toBeGreaterThanOrEqual(panel.x);expect(menu.x+menu.width).toBeLessThanOrEqual(panel.x+panel.width);
 expect(await inspector.evaluate(node=>node.scrollWidth-node.clientWidth)).toBe(0);
 await command.click();const deletion=page.getByRole('dialog',{name:'Delete this study?',exact:true});await boundedDialog(page,deletion);
 await deletion.getByRole('button',{name:'Cancel',exact:true}).click();await expect(page.getByRole('button',{name:'Study actions',exact:true})).toBeFocused();
 await page.getByRole('button',{name:'Sign out',exact:true}).click();const exit=page.getByRole('dialog',{name:'Changes not saved',exact:true});await boundedDialog(page,exit);
 await exit.getByRole('button',{name:'Stay',exact:true}).click();await expect(editor).toHaveText('Retain this narrow-screen draft');
 expect(await page.evaluate(()=>document.documentElement.scrollWidth)).toBe(320);
});
for(const mode of ['Sign in','Create account'])test('polish: anonymous Studies opens '+mode+' directly and restores focus',async({page})=>{
 await setup(page);await page.addInitScript(()=>localStorage.removeItem('pts-auth'));await page.goto('/');await actions(page,'Studies');
 const panel=page.getByRole('region',{name:'My studies',exact:true});await expect(panel.getByRole('alert')).toHaveCount(0);await expect(panel.getByRole('button',{name:'Retry',exact:true})).toHaveCount(0);
 const trigger=panel.getByRole('button',{name:mode,exact:true});await trigger.click();await expect(page.getByRole('dialog',{name:mode,exact:true})).toBeVisible();await expect(page.getByLabel('Email',{exact:true})).toBeFocused();await page.keyboard.press('Escape');await expect(trigger).toBeFocused();
});

test('polish: keyboard traversal closes actions when focus leaves',async({page})=>{
 await setup(page);await firstNote(page);const trigger=page.getByRole('button',{name:'Note actions',exact:true});await trigger.focus();await page.keyboard.press('Enter');
 await page.keyboard.press('Tab');await expect(page.getByRole('button',{name:'Duplicate note',exact:true})).toBeFocused();await page.keyboard.press('Tab');await expect(page.getByRole('button',{name:'Delete note',exact:true})).toBeFocused();
 await page.keyboard.press('Tab');await expect(page.getByRole('button',{name:'Bold',exact:true})).toBeFocused();await expect(trigger).toHaveAttribute('aria-expanded','false');
 await trigger.focus();await page.keyboard.press('Enter');await page.keyboard.press('Tab');await page.keyboard.press('Shift+Tab');await expect(trigger).toBeFocused();await expect(trigger).toHaveAttribute('aria-expanded','true');await page.keyboard.press('Shift+Tab');await expect(page.getByRole('button',{name:'Read note',exact:true})).toBeFocused();await expect(trigger).toHaveAttribute('aria-expanded','false');
});
test('polish: Analysis retains recovery for a failed selected-word lookup',async({page})=>{
 await setup(page);let failed=true;await page.route('**/api/bible/words/**',r=>failed?r.fulfill({status:503,json:{code:'unavailable'}}):r.fallback());await page.goto('/');await page.getByRole('button',{name:/Word:/}).first().click();await expect(page.getByRole('alert')).toContainText('Could not load word analysis');await actions(page,'Analysis');
 const inspector=page.getByRole('complementary',{name:'Study tools',exact:true});await expect(inspector.getByRole('alert')).toContainText('Could not load word analysis');failed=false;await inspector.getByRole('button',{name:'Retry word analysis',exact:true}).click();await expect(inspector.getByLabel('Dictionary inspector',{exact:true})).toBeVisible();await expect(inspector.getByRole('alert')).toHaveCount(0);await expect(inspector.getByRole('tab',{name:'Word',exact:true})).toHaveAttribute('aria-selected','true');
});
