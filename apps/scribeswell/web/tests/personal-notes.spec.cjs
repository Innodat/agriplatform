// Project the new public wire into coordinates for existing behavioral assertions.
// Deliberate navigation now emits only reader; incoming legacy links stay covered.
function readerParams(href) {
  const params = new URL(href).searchParams;
  if (!params.has('reader')) return params;
  const layout = JSON.parse(params.get('reader')),
    out = new URLSearchParams();
  layout.panes.forEach(({
    ref
  }, index) => {
    const start = ref.target.kind === 'chapter' ? {
        chapter: ref.target.chapter
      } : ref.target.start,
      prefix = index ? 'compare' : '';
    out.set(index ? 'compareBook' : 'book', ref.book_id);
    out.set(index ? 'compareChapter' : 'chapter', String(start.chapter));
    if (start.verse) {
      out.set(index ? 'compareVerse' : 'verse', String(start.verse));
      out.set(prefix + 'EndChapter', String(ref.target.end.chapter));
      out.set(prefix + 'EndVerse', String(ref.target.end.verse));
    }
  });
  return out;
}
async function addReader(page) {
  const tool = (await page.getByRole('button', {
    name: 'Analysis',
    exact: true
  }).getAttribute('aria-pressed')) === 'true' ? 'Analysis' : (await page.getByRole('button', {
    name: 'Studies',
    exact: true
  }).getAttribute('aria-pressed')) === 'true' ? 'Studies' : null;
  await page.getByRole('button', {
    name: 'Add reader pane',
    exact: true
  }).click();
  await page.getByRole('dialog', {
    name: 'Book and chapter selector'
  }).getByRole('button', {
    name: 'Cancel',
    exact: true
  }).click();
  if (tool && page.viewportSize().width < 768) await page.getByRole('button', {
    name: tool,
    exact: true
  }).click();
}
const {test,expect}=require('@playwright/test');
const account='10000000-0000-4000-8000-000000000001',actor='20000000-0000-4000-8000-000000000001';
const study='30000000-0000-4000-8000-000000000001',note='40000000-0000-4000-8000-000000000001';
const session={access_token:'current',refresh_token:'fixture',expires_at:Date.now()/1000+3600,expires_in:3600,token_type:'bearer',user:{id:account,email:'reader@example.invalid',aud:'authenticated',app_metadata:{},user_metadata:{}}};
const attribution={owner_account_id:account,created_at:'2026-10-23T10:00:00.000000Z',updated_at:'2026-10-23T10:00:00.000000Z',created_by_actor_id:actor,updated_by_actor_id:actor};
async function setup(page,options={}){
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
  if(path.endsWith('/search')){if(options.search)return options.search(r,payload);data={items:created?[{...attribution,id:study,title:metadata.title,revision:metadata.revision}]:[],next_cursor:null};}
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
  else if(path.endsWith('/'+study)){if(options.beforeStudyRead)await options.beforeStudyRead();data={...attribution,id:study,title:metadata.title,revision:metadata.revision};}
  else data={items:created?[{...attribution,id:study,title:metadata.title,revision:metadata.revision}]:[],next_cursor:null};
  if(data.command)operations.set(data.operation_id,data);
  if(method==='PUT'&&options.dropPut){options.dropPut=false;return r.abort('connectionreset');}
  return r.fulfill({json:data,headers:{'cache-control':'private, no-store'}});
 });return {requests,metadata,collection,advanceNote:(value)=>{saved=value;revision=String(Number(revision)+1);}};
}
test('explicitly enroll, create, write Hebrew and reopen saved text after reload',async({page})=>{
 const {requests}=await setup(page);await page.goto('/');expect(requests).toHaveLength(0);
 await page.getByRole('button',{name:'Studies',exact:true}).click();
 await page.getByRole('button',{name:'Start a study',exact:true}).click();
 await page.getByRole('button',{name:'Create study',exact:true}).click();
 await expect(page.getByRole('heading',{name:'Untitled study',exact:true})).toBeVisible();
 await page.getByRole('button',{name:'Add note',exact:true}).click();
 await page.getByLabel('Note text',{exact:true}).fill('בְּרֵאשִׁית — personal observation');
 await expect(page.getByRole('status').filter({hasText:'Draft saved'})).toBeVisible();
 await page.reload();await page.getByRole('button',{name:'Studies',exact:true}).click();
 await page.getByRole('button',{name:'Untitled study',exact:true}).click();
 await page.getByRole('button',{name:/personal observation/}).click();
 await expect(page.getByLabel('Note text',{exact:true})).toContainText('בְּרֵאשִׁית — personal observation');
 expect(requests.filter(r=>r.path.endsWith('/enrollment'))).toHaveLength(1);
});

async function firstNote(page){await page.goto('/');await page.getByRole('button',{name:'Studies',exact:true}).click();await page.getByRole('button',{name:'Start a study',exact:true}).click();await page.getByRole('button',{name:'Create study',exact:true}).click();await page.getByRole('button',{name:'Add note',exact:true}).click();await expect(page.getByLabel('Note text',{exact:true})).toBeVisible();}
test('failed saves use inline Retry and exit-only Stay / Close anyway',async({page})=>{
 const options={failPut:503};await setup(page,options);await firstNote(page);await page.getByLabel('Note text',{exact:true}).fill('Unsaved Hebrew שָׁלוֹם');await expect(page.getByRole('status').filter({hasText:'Changes not saved'})).toBeVisible();await expect(page.getByRole('button',{name:'Keep editing'})).toHaveCount(0);await expect(page.getByRole('dialog')).toHaveCount(0);
 await page.getByRole('button',{name:'Sign out',exact:true}).click();await expect(page.getByRole('dialog',{name:'Changes not saved'})).toBeVisible();await page.getByRole('button',{name:'Stay',exact:true}).click();await expect(page.getByLabel('Note text',{exact:true})).toContainText('שָׁלוֹם');options.failPut=0;await page.getByRole('button',{name:'Retry',exact:true}).click();await expect(page.getByRole('status').filter({hasText:'Draft saved'})).toBeVisible();await page.getByRole('button',{name:'Sign out',exact:true}).click();await expect(page.getByRole('dialog',{name:'Changes not saved'})).toHaveCount(0);
});
test('delayed old acknowledgement cannot mark newer text saved',async({page})=>{
 let release;const options={beforePut:()=>new Promise(resolve=>release=resolve)};const {requests}=await setup(page,options);await firstNote(page);const editor=page.getByLabel('Note text',{exact:true});await editor.fill('first');await expect.poll(()=>Boolean(release)).toBe(true);await editor.fill('newer שָׁלוֹם');await expect(page.getByRole('status')).not.toHaveText('Draft saved');expect(requests.filter(r=>r.method==='PUT')).toHaveLength(1);options.beforePut=undefined;release();await expect(page.getByRole('status').filter({hasText:'Draft saved'})).toBeVisible();expect(requests.filter(r=>r.method==='PUT')).toHaveLength(2);await expect(editor).toContainText('newer שָׁלוֹם');
});
test('composition defers autosave until IME completion',async({page})=>{
 const {requests}=await setup(page);await firstNote(page);const editor=page.getByLabel('Note text',{exact:true});await editor.dispatchEvent('compositionstart');await editor.fill('עברית');await page.waitForTimeout(700);expect(requests.filter(r=>r.method==='PUT')).toHaveLength(0);await editor.dispatchEvent('compositionend');await expect.poll(()=>requests.filter(r=>r.method==='PUT').length).toBe(1);await expect(page.getByRole('status').filter({hasText:'Draft saved'})).toBeVisible();
});
test('account replacement discards prior private UI and late saves',async({page})=>{
 let release;await setup(page,{beforePut:()=>new Promise(resolve=>release=resolve)});await firstNote(page);await page.getByLabel('Note text',{exact:true}).fill('prior-account private text');await expect.poll(()=>Boolean(release)).toBe(true);
 await page.route('**/auth/v1/token*',r=>r.fulfill({json:{...session,user:{...session.user,id:'10000000-0000-4000-8000-000000000002'}}}));
 await page.evaluate(async()=>{const {supabase}=await import('/src/lib/supabase.ts');await supabase.auth.signOut({scope:'local'});await supabase.auth.signInWithPassword({email:'other@example.invalid',password:'fixture'});});
 await expect(page.getByLabel('Note text',{exact:true})).toHaveCount(0);release();await expect(page.getByText('prior-account private text')).toHaveCount(0);await expect(page.getByRole('button',{name:'Studies',exact:true})).toBeVisible();
});
test('native PostgreSQL browser reload returns the acknowledged aggregate',async({page})=>{
 test.skip(!process.env.SCRIBESWELL_NOTES_NATIVE_API,'Explicit owned native API fixture required');
 await setup(page);await page.unroute('**/api/studies**');
 for(const pattern of ['**/api/studies**','**/api/operations/**'])await page.route(pattern,async r=>{const target=process.env.SCRIBESWELL_NOTES_NATIVE_API+new URL(r.request().url()).pathname+new URL(r.request().url()).search;const response=await r.fetch({url:target});await r.fulfill({response});});
 await firstNote(page);await page.getByLabel('Note text',{exact:true}).fill('Native persisted בְּרֵאשִׁית');await expect(page.getByRole('status').filter({hasText:'Draft saved'})).toBeVisible();
 await page.reload();await page.getByRole('button',{name:'Studies',exact:true}).click();await page.getByRole('button',{name:'Untitled study',exact:true}).click();await page.getByRole('button',{name:'Native persisted בְּרֵאשִׁית',exact:true}).click();await expect(page.getByLabel('Note text',{exact:true})).toContainText('Native persisted בְּרֵאשִׁית');
});

test('unknown response blocks newer snapshots and recovers the original operation',async({page})=>{
 let release;const options={dropPut:true,beforeLookup:()=>new Promise(resolve=>release=resolve)};const {requests}=await setup(page,options);await firstNote(page);const editor=page.getByLabel('Note text',{exact:true});await editor.fill('first unknown');await expect.poll(()=>Boolean(release)).toBe(true);await editor.fill('later snapshot');await page.waitForTimeout(700);expect(requests.filter(r=>r.method==='PUT')).toHaveLength(1);options.beforeLookup=undefined;release();await expect(page.getByRole('status').filter({hasText:'Draft saved'})).toBeVisible();expect(requests.filter(r=>r.method==='PUT')).toHaveLength(2);
});
test('revision conflict preserves input and guards study switching',async({page})=>{
 await setup(page,{failPut:409});await firstNote(page);await page.getByLabel('Note text',{exact:true}).fill('mine conflicts');await expect(page.getByRole('alert')).toContainText('This note has changed');await page.getByRole('button',{name:'Back to Studies',exact:true}).click();await page.getByRole('button',{name:'Leave study',exact:true}).click();await expect(page.getByRole('dialog',{name:'Changes not saved'})).toBeVisible();await expect(page.getByRole('button',{name:'Switch anyway',exact:true})).toBeVisible();await page.getByRole('button',{name:'Stay',exact:true}).click();await page.getByRole('button',{name:'Analysis',exact:true}).click();await expect(page.getByLabel('Note text',{exact:true})).toContainText('mine conflicts');
});
test('same-account reauthentication preserves input and requires explicit retry',async({page})=>{
 const options={failPut:401};const {requests}=await setup(page,options);await firstNote(page);await page.getByLabel('Note text',{exact:true}).fill('recoverable current input');await expect(page.getByRole('alert')).toContainText('Sign in');await expect(page.getByLabel('Note text',{exact:true})).toHaveCount(0);const count=requests.filter(r=>r.method==='PUT').length;
 await page.route('**/auth/v1/token*',r=>r.fulfill({json:{...session,access_token:'renewed-current'}}));await page.evaluate(async()=>{const {supabase}=await import('/src/lib/supabase.ts');await supabase.auth.signInWithPassword({email:'reader@example.invalid',password:'fixture'});});options.failPut=0;
 await page.getByRole('button',{name:'Retry Studies',exact:true}).click();await expect(page.getByLabel('Note text',{exact:true})).toContainText('recoverable current input');expect(requests.filter(r=>r.method==='PUT')).toHaveLength(count);await page.getByRole('button',{name:'Retry',exact:true}).click();await expect(page.getByRole('status').filter({hasText:'Draft saved'})).toBeVisible();
});
test('rich paragraphs directions lists marks and safe links survive saving and reopening',async({page})=>{
 const {requests}=await setup(page);await firstNote(page);const editor=page.getByLabel('Note text',{exact:true});await editor.evaluate(el=>{el.replaceChildren();const p=document.createElement('p');p.dir='rtl';const bold=document.createElement('strong');bold.textContent='שָׁלוֹם';p.append(bold);const link=document.createElement('a');link.href='https://example.org/source';link.textContent=' source';p.append(link);const list=document.createElement('ol');const li=document.createElement('li');const i=document.createElement('em');i.textContent='Second paragraph';li.append(i);list.append(li);el.append(p,list);el.dispatchEvent(new InputEvent('input',{bubbles:true}));});await expect(page.getByRole('status').filter({hasText:'Draft saved'})).toBeVisible();const saved=requests.filter(r=>r.method==='PUT').at(-1).payload.value;expect(saved.document.blocks[0].direction).toBe('rtl');expect(saved.document.blocks[0].content[0].marks).toEqual(['bold']);expect(saved.document.blocks[1].style).toBe('ordered');
 await page.reload();await page.getByRole('button',{name:'Studies',exact:true}).click();await page.getByRole('button',{name:'Untitled study',exact:true}).click();await page.getByRole('button',{name:/Second paragraph/}).click();await expect(editor.locator('strong')).toHaveText('שָׁלוֹם');await expect(editor.locator('ol li em')).toHaveText('Second paragraph');await expect(editor.locator('a')).toHaveAttribute('rel','noopener noreferrer');
});
test('editor toolbar actions persist direction marks lists and safe links',async({page})=>{
 const {requests}=await setup(page);await firstNote(page);const editor=page.getByLabel('Note text',{exact:true});await editor.fill('שָׁלוֹם');await editor.press('ControlOrMeta+A');await page.getByRole('button',{name:'Bold',exact:true}).click();await page.getByLabel('Paragraph direction').selectOption('rtl');await editor.press('ControlOrMeta+End');await editor.press('Enter');await editor.press('ControlOrMeta+B');await editor.press('ControlOrMeta+I');await editor.pressSequentially('Second paragraph source');await page.getByRole('button',{name:'Numbered list',exact:true}).click();await editor.press('ControlOrMeta+End');await editor.press('ControlOrMeta+Shift+ArrowLeft');await page.getByRole('button',{name:'Link',exact:true}).click();await page.getByLabel('Link URL',{exact:true}).fill('https://example.org/source');await page.getByRole('button',{name:'Insert link',exact:true}).click();await expect(page.getByRole('status').filter({hasText:'Draft saved'})).toBeVisible();
 const saved=requests.filter(r=>r.method==='PUT').at(-1).payload.value;expect(saved.document.blocks.some(b=>b.type==='paragraph'&&b.direction==='rtl')).toBe(true);expect(saved.document.blocks.some(b=>b.type==='list'&&b.style==='ordered')).toBe(true);expect(JSON.stringify(saved)).toContain('bold');expect(JSON.stringify(saved)).toContain('italic');expect(JSON.stringify(saved)).toContain('https://example.org/source');
 await page.reload();await page.getByRole('button',{name:'Studies',exact:true}).click();await page.getByRole('button',{name:'Untitled study',exact:true}).click();await page.getByRole('button',{name:/Second paragraph/}).click();await expect(editor.locator('ol')).toBeVisible();await expect(editor.locator('a')).toHaveAttribute('href','https://example.org/source');await expect(editor.locator('p[dir="rtl"]').filter({hasText:'שָׁלוֹם'})).toBeVisible();
});

test('word inspection and Notes return retain the shared edit lane',async({page,isMobile})=>{
 await setup(page);await firstNote(page);await page.getByLabel('Note text',{exact:true}).fill('Current note remains selected');if(isMobile||test.info().project.name==='mobile')await page.getByRole('button',{name:'Return to reader',exact:true}).click();await page.getByRole('button',{name:/Word:/}).first().click();await expect(page.getByRole('tab',{name:'Word',exact:true})).toBeVisible();await expect(page.getByRole('tab',{name:'Occurrences',exact:true})).toBeVisible();await page.getByRole('tab',{name:'Notes',exact:true}).click();await expect(page.getByLabel('Note text',{exact:true})).toContainText('Current note remains selected');expect(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth)).toBe(false);
});
test('unsupported current editor input stays unsaved and exit guarded until corrected',async({page})=>{
 await setup(page);await firstNote(page);const editor=page.getByLabel('Note text',{exact:true});await editor.evaluate(el=>{const table=document.createElement('table');table.textContent='Unsupported current input';el.replaceChildren(table);el.dispatchEvent(new InputEvent('input',{bubbles:true}));});await expect(page.getByRole('status')).toContainText('Changes not saved');await page.getByRole('button',{name:'Sign out',exact:true}).click();await expect(page.getByRole('dialog',{name:'Changes not saved'})).toBeVisible();await page.getByRole('button',{name:'Stay',exact:true}).click();await expect(editor).toContainText('Unsupported current input');await editor.fill('Corrected supported input');await page.getByRole('button',{name:'Retry',exact:true}).click();await expect(page.getByRole('status')).toContainText('Draft saved');
});
for(const surface of ['study title','link URL'])test('account replacement clears local '+surface+' input',async({page})=>{
 await setup(page);if(surface==='study title'){await page.goto('/');await page.getByRole('button',{name:'Studies',exact:true}).click();await page.getByRole('button',{name:'Start a study',exact:true}).click();await page.getByLabel('Study title (optional)').fill('Prior account title');}else{await firstNote(page);await page.getByRole('button',{name:'Link',exact:true}).click();await page.getByLabel('Link URL',{exact:true}).fill('https://private.example.invalid/prior-account');}
 await page.route('**/auth/v1/token*',r=>r.fulfill({json:{...session,access_token:'other-account',user:{...session.user,id:'10000000-0000-4000-8000-000000000002'}}}));await page.evaluate(async()=>{const {supabase}=await import('/src/lib/supabase.ts');await supabase.auth.signInWithPassword({email:'other@example.invalid',password:'fixture'});});await expect(page.getByLabel('Link URL',{exact:true})).toHaveCount(0);await expect(page.getByLabel('Study title (optional)')).toHaveCount(0);expect(await page.locator('body').innerText()).not.toContain('Prior account title');expect(await page.evaluate(()=>Array.from(document.querySelectorAll('input')).map(el=>el.value).join(' '))).not.toContain('prior-account');
});
test('review: rejected study title can be corrected without replaying invalid payload',async({page})=>{
 const {requests}=await setup(page);const rejected=[];
 await page.route('**/api/studies',r=>{if(r.request().method()==='POST'&&r.request().postDataJSON().title==='   '){rejected.push(r.request().postDataJSON());return r.fulfill({status:400,json:{code:'scribeswell_personal_notes_input_invalid'}});}return r.fallback();});
 await page.goto('/');await page.getByRole('button',{name:'Studies',exact:true}).click();await page.getByRole('button',{name:'Start a study',exact:true}).click();await page.getByLabel('Study title (optional)').fill('   ');await page.getByRole('button',{name:'Create study',exact:true}).click();await expect(page.getByRole('alert')).toBeVisible();await page.getByLabel('Study title (optional)').fill('Corrected title');await page.getByRole('button',{name:'Create study',exact:true}).click();await expect(page.getByRole('button',{name:'Add note',exact:true})).toBeVisible();const accepted=requests.find(r=>r.method==='POST'&&r.path==='/api/studies').payload;expect(accepted.title).toBe('Corrected title');expect(accepted.operation_id).not.toBe(rejected[0].operation_id);
});
test('review: confirmed conflict discard reopens latest while Stay preserves mine',async({page})=>{
 const options={failPut:409};await setup(page,options);await firstNote(page);const editor=page.getByLabel('Note text',{exact:true});await editor.fill('My conflicting text');await expect(page.getByRole('alert')).toContainText('This note has changed');
 const latest={...attribution,id:note,study_id:study,visibility:'study',revision:'2',value:{document:{version:1,blocks:[{type:'paragraph',direction:'auto',content:[{type:'text',text:'Latest from server',marks:[]}]}]},connections:[],highlights:[]}};let reads=0;
 await page.route('**/api/studies/'+study+'/notes/'+note,r=>{if(r.request().method()==='GET'){reads++;return r.fulfill({json:latest});}return r.fallback();});
 await page.getByRole('button',{name:'Back to Studies',exact:true}).click();await page.getByRole('button',{name:'Empty note',exact:true}).click();await page.getByRole('button',{name:'Stay',exact:true}).click();await page.getByRole('button',{name:'Analysis',exact:true}).click();await expect(editor).toContainText('My conflicting text');expect(reads).toBe(0);
 await page.getByRole('button',{name:'Back to Studies',exact:true}).click();await page.getByRole('button',{name:'Empty note',exact:true}).click();await page.getByRole('button',{name:'Switch anyway',exact:true}).click();await expect(editor).toContainText('Latest from server');expect(reads).toBe(1);
});
test('review: IME exit prompts responsively and Stay retains composing input',async({page})=>{
 await setup(page);await firstNote(page);const editor=page.getByLabel('Note text',{exact:true});await editor.dispatchEvent('compositionstart');await editor.fill('Still composing עברית');await page.getByRole('button',{name:'Sign out',exact:true}).click();await expect(page.getByRole('dialog',{name:'Changes not saved'})).toBeVisible({timeout:1000});await page.getByRole('button',{name:'Stay',exact:true}).click();await expect(editor).toContainText('Still composing עברית');await editor.dispatchEvent('compositionend');await expect(page.getByRole('status')).toContainText('Draft saved');
});
test('review: Shift Enter soft break survives save and reload',async({page})=>{
 const {requests}=await setup(page);await firstNote(page);const editor=page.getByLabel('Note text',{exact:true});await editor.fill('First line');await editor.press('End');await editor.press('Shift+Enter');await editor.pressSequentially('Second line');await expect(page.getByRole('status')).toContainText('Draft saved');const saved=requests.filter(r=>r.method==='PUT').at(-1).payload.value;expect(saved.document.blocks.map(b=>b.content.map(i=>i.text).join('')).join('\n')).toBe('First line\nSecond line');await page.reload();await page.getByRole('button',{name:'Studies',exact:true}).click();await page.getByRole('button',{name:'Untitled study',exact:true}).click();await page.getByRole('button',{name:/First line/}).click();await expect(editor).toHaveText('First line\nSecond line');
});
test('review: invalid DNS link remains correctable without changing note text',async({page})=>{
 await setup(page);await firstNote(page);const editor=page.getByLabel('Note text',{exact:true});await editor.fill('Selected source text');await editor.press('ControlOrMeta+A');await page.getByRole('button',{name:'Link',exact:true}).click();await page.getByLabel('Link URL',{exact:true}).fill('https://exa_mple.org');await page.getByRole('button',{name:'Insert link',exact:true}).click();await expect(page.getByRole('alert')).toContainText('valid hostname');await expect(editor).toHaveText('Selected source text');await page.getByLabel('Link URL',{exact:true}).fill('https://example.org');await page.getByRole('button',{name:'Insert link',exact:true}).click();await expect(editor.locator('a')).toHaveText('Selected source text');await expect(page.getByRole('status')).toContainText('Draft saved');
});
async function reviewLibrary(page,options={}){
 await setup(page);const otherStudy='30000000-0000-4000-8000-000000000002',otherNote='40000000-0000-4000-8000-000000000002';
 const value=text=>({document:{version:1,blocks:[{type:'paragraph',direction:'auto',content:[{type:'text',text,marks:[]}]}]},connections:[],highlights:[]});
 const studyView=id=>({...attribution,id,title:id===study?'Study A':'Study B',revision:'1'});
 const noteView=(parent,id,text)=>({...attribution,id,study_id:parent,visibility:'study',revision:'1',value:value(text)});
 await page.route('**/api/studies**',async r=>{if(r.request().method()==='PUT')return r.fallback();const url=new URL(r.request().url()),parts=url.pathname.split('/').filter(Boolean);let result;
  if(parts.length===2||parts[2]==='search')result={items:[studyView(study),studyView(otherStudy)],next_cursor:null};
  else if(parts.length===3)result=options.detail?await options.detail(parts[2],studyView):studyView(parts[2]);
  else if(parts.length===4){const parent=parts[2];result=options.notes?await options.notes(parent,url.searchParams.get('cursor'),noteView):{items:[noteView(parent,note,'A first'),noteView(parent,otherNote,'A second')],next_cursor:null};}
  else result=options.read?await options.read(parts[2],parts[4],noteView):noteView(parts[2],parts[4],parts[4]===note?'A first':'A second');
  return r.fulfill({json:result});
 });await page.goto('/');await page.getByRole('button',{name:'Studies',exact:true}).click();return {otherStudy,otherNote};
}
test('review: superseded study and note responses cannot replace newer navigation',async({page})=>{
 const gates=[];const options={detail:(id,view)=>new Promise(resolve=>gates.push({id,release:()=>resolve(view(id))}))};const {otherStudy}=await reviewLibrary(page,options);
 await page.getByRole('button',{name:'Study A',exact:true}).click();await expect.poll(()=>gates.length).toBe(1);await page.getByRole('button',{name:'Study B',exact:true}).click();await expect.poll(()=>gates.length).toBe(2);gates.find(g=>g.id===otherStudy).release();await expect(page.getByRole('heading',{name:'Study B',exact:true})).toBeVisible();const old=page.waitForResponse('**/api/studies/'+study);gates.find(g=>g.id===study).release();await old;await expect(page.getByRole('heading',{name:'Study B',exact:true})).toBeVisible();
 const noteGates=[];options.read=(parent,id,view)=>new Promise(resolve=>noteGates.push({id,release:()=>resolve(view(parent,id,id===note?'A first':'A second'))}));await page.getByRole('button',{name:'A first',exact:true}).click();await expect.poll(()=>noteGates.length).toBe(1);await page.getByRole('button',{name:'A second',exact:true}).click();await expect.poll(()=>noteGates.length).toBe(2);noteGates[1].release();await expect(page.getByLabel('Note text',{exact:true})).toHaveText('A second');const stale=page.waitForResponse('**/notes/'+note);noteGates[0].release();await stale;await expect(page.getByLabel('Note text',{exact:true})).toHaveText('A second');
});
test('review: More notes deduplicates its page and ignores a changed study parent',async({page})=>{
 const pages=[];const {otherStudy}=await reviewLibrary(page,{notes:(parent,cursor,view)=>cursor?new Promise(resolve=>pages.push({parent,release:()=>resolve({items:[view(parent,'40000000-0000-4000-8000-000000000003','Older A page')],next_cursor:null})})):{items:[view(parent,note,parent===study?'A first':'B first')],next_cursor:parent===study?'page-two':null}});
 await page.getByRole('button',{name:'Study A',exact:true}).click();await page.getByRole('button',{name:'More notes',exact:true}).click();await expect.poll(()=>pages.length).toBe(1);await page.getByRole('button',{name:'More notes',exact:true}).click();await page.waitForTimeout(100);expect(pages).toHaveLength(1);pages[0].release();await expect(page.getByRole('button',{name:'Older A page',exact:true})).toHaveCount(1);
 await page.getByRole('button',{name:'Leave study',exact:true}).click();await page.getByRole('button',{name:'Study A',exact:true}).click();await page.getByRole('button',{name:'More notes',exact:true}).click();await expect.poll(()=>pages.length).toBe(2);await page.getByRole('button',{name:'Leave study',exact:true}).click();await page.getByRole('button',{name:'Study B',exact:true}).click();await expect(page.getByRole('heading',{name:'Study B',exact:true})).toBeVisible();const stale=page.waitForResponse('**/api/studies/'+study+'/notes?cursor=page-two');pages[1].release();await stale;await expect(page.getByRole('button',{name:'Older A page',exact:true})).toHaveCount(0);await expect(page.getByRole('button',{name:'B first',exact:true})).toBeVisible();expect(otherStudy).not.toBe(study);
});
test('review: note changes reset link range URL form and direction control',async({page})=>{
 await reviewLibrary(page);await page.getByRole('button',{name:'Study A',exact:true}).click();await page.getByRole('button',{name:'A first',exact:true}).click();const editor=page.getByLabel('Note text',{exact:true});await editor.press('ControlOrMeta+A');await page.getByLabel('Paragraph direction').selectOption('rtl');await expect(page.getByRole('status')).toContainText('Draft saved');await editor.press('ControlOrMeta+A');await page.getByRole('button',{name:'Link',exact:true}).click();await page.getByLabel('Link URL',{exact:true}).fill('https://prior-note.invalid');await page.getByRole('button',{name:'Back to Studies',exact:true}).click();await page.getByRole('button',{name:'A second',exact:true}).click();await expect(editor).toHaveText('A second');await expect(page.getByLabel('Link URL',{exact:true})).toHaveCount(0);await expect(page.getByLabel('Paragraph direction')).toHaveValue('auto');await page.evaluate(()=>window.getSelection().removeAllRanges());await page.getByRole('button',{name:'Link',exact:true}).click();await expect(page.getByLabel('Link URL',{exact:true})).toHaveValue('');await page.getByLabel('Link URL',{exact:true}).fill('https://example.org');await page.getByRole('button',{name:'Insert link',exact:true}).click();await expect(page.getByRole('alert')).toContainText('Select text in this note');await expect(editor).toHaveText('A second');
});
test('review: unknown study create preserves original operation and frozen title',async({page})=>{
 await setup(page);const attempts=[];await page.route('**/api/studies',r=>{if(r.request().method()!=='POST')return r.fallback();attempts.push(r.request().postDataJSON());if(attempts.length===1)return r.abort('connectionreset');return r.fallback();});await page.goto('/');await page.getByRole('button',{name:'Studies',exact:true}).click();await page.getByRole('button',{name:'Start a study',exact:true}).click();await page.getByLabel('Study title (optional)').fill('Original uncertain title');await page.getByRole('button',{name:'Create study',exact:true}).click();await expect(page.getByRole('alert')).toBeVisible();await page.getByLabel('Study title (optional)').fill('Later typed title');await page.getByRole('button',{name:'Create study',exact:true}).click();await expect(page.getByRole('button',{name:'Add note',exact:true})).toBeVisible();expect(attempts).toHaveLength(2);expect(attempts[1]).toEqual(attempts[0]);
});


test('rename: explicit Save Cancel and reload preserve independent note and reader',async({page})=>{
 const {requests}=await setup(page);await firstNote(page);const editor=page.getByLabel('Note text',{exact:true});await editor.fill('Acknowledged note שָׁלוֹם');await expect(page.getByRole('status')).toContainText('Draft saved');
 await page.getByRole('button',{name:'Back to Studies',exact:true}).click();await page.getByRole('button',{name:'Rename',exact:true}).click();await page.getByLabel('Title',{exact:true}).fill('Cancelled candidate');await expect(page.getByRole('heading',{name:'Untitled study',exact:true})).toBeVisible();await page.getByRole('button',{name:'Cancel',exact:true}).click();expect(requests.filter(r=>r.path.endsWith('/title'))).toHaveLength(0);
 await page.getByRole('button',{name:'Rename',exact:true}).click();await page.getByLabel('Title',{exact:true}).fill('English שלום');await page.getByRole('button',{name:'Save',exact:true}).click();await expect(page.getByRole('heading',{name:'English שלום',exact:true})).toBeVisible();
 await page.getByRole('button',{name:'Acknowledged note שָׁלוֹם',exact:true}).click();await expect(editor).toHaveText('Acknowledged note שָׁלוֹם');await expect(page.getByText('בְּרֵאשִׁית',{exact:true}).first()).toBeAttached();
 await page.reload();await page.getByRole('button',{name:'Studies',exact:true}).click();await page.getByRole('button',{name:'English שלום',exact:true}).click();await page.getByRole('button',{name:'Acknowledged note שָׁלוֹם',exact:true}).click();await expect(editor).toHaveText('Acknowledged note שָׁלוֹם');expect(requests.filter(r=>r.path.includes('/notes/')&&r.method==='PUT')).toHaveLength(1);expect(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth)).toBe(false);
});
test('rename: conflict retains candidate and current reload requires new explicit Save',async({page})=>{
 const options={failRename:409};const {requests,metadata}=await setup(page,options);await firstNote(page);await page.getByRole('button',{name:'Back to Studies',exact:true}).click();await page.getByRole('button',{name:'Rename',exact:true}).click();await page.getByLabel('Title',{exact:true}).fill('My candidate');await page.getByRole('button',{name:'Save',exact:true}).click();await expect(page.getByRole('alert')).toContainText('title changed elsewhere');await expect(page.getByLabel('Title',{exact:true})).toHaveValue('My candidate');metadata.title='Elsewhere';metadata.revision='2';options.failRename=0;await page.getByRole('button',{name:'Load current title',exact:true}).click();await expect(page.getByRole('heading',{name:'Elsewhere',exact:true})).toBeVisible();await expect(page.getByLabel('Title',{exact:true})).toHaveValue('My candidate');expect(requests.filter(r=>r.path.endsWith('/title'))).toHaveLength(1);await page.getByRole('button',{name:'Save',exact:true}).click();await expect(page.getByRole('heading',{name:'My candidate',exact:true})).toBeVisible();const attempts=requests.filter(r=>r.path.endsWith('/title'));expect(attempts[1].payload.expected_revision).toBe('2');expect(attempts[1].payload.operation_id).not.toBe(attempts[0].payload.operation_id);
});
test('rename: unknown outcome survives closing and retries frozen original without overtaking',async({page})=>{
 const options={dropRename:true,unresolved:true};const {requests}=await setup(page,options);await firstNote(page);await page.getByRole('button',{name:'Back to Studies',exact:true}).click();await page.getByRole('button',{name:'Rename',exact:true}).click();await page.getByLabel('Title',{exact:true}).fill('Original frozen title');await page.getByRole('button',{name:'Save',exact:true}).click();await expect(page.getByRole('alert')).toContainText('Title not saved');await expect(page.getByLabel('Title',{exact:true})).toHaveAttribute('readonly','');await page.getByRole('button',{name:'Cancel',exact:true}).click();await page.getByRole('button',{name:'Rename',exact:true}).click();await expect(page.getByLabel('Title',{exact:true})).toHaveValue('Original frozen title');options.unresolved=false;await page.getByRole('button',{name:'Retry rename',exact:true}).click();await expect(page.getByRole('heading',{name:'Original frozen title',exact:true})).toBeVisible();const attempts=requests.filter(r=>r.path.endsWith('/title'));expect(attempts).toHaveLength(2);expect(attempts[1].payload).toEqual(attempts[0].payload);
});
test('rename: invalid input is editable and corrected with a new operation',async({page})=>{
 const options={failRename:400};const {requests}=await setup(page,options);await firstNote(page);await page.getByRole('button',{name:'Back to Studies',exact:true}).click();await page.getByRole('button',{name:'Rename',exact:true}).click();await page.getByLabel('Title',{exact:true}).fill('   ');await page.getByRole('button',{name:'Save',exact:true}).click();await expect(page.getByRole('alert')).toContainText('1–200');options.failRename=0;await page.getByLabel('Title',{exact:true}).fill('Corrected');await page.getByRole('button',{name:'Save',exact:true}).click();await expect(page.getByRole('heading',{name:'Corrected',exact:true})).toBeVisible();const attempts=requests.filter(r=>r.path.endsWith('/title'));expect(attempts[0].payload.operation_id).not.toBe(attempts[1].payload.operation_id);
});
test('rename: closing executing title keeps operation and stale acknowledgement reads current metadata',async({page})=>{
 let release;const gate=new Promise(resolve=>release=resolve);const {metadata}=await setup(page,{beforeRename:()=>gate});await firstNote(page);await page.getByRole('button',{name:'Back to Studies',exact:true}).click();await page.getByRole('button',{name:'Rename',exact:true}).click();await page.getByLabel('Title',{exact:true}).fill('Candidate');await page.getByRole('button',{name:'Save',exact:true}).click();await expect(page.getByRole('status')).toContainText('Saving title');await page.getByRole('button',{name:'Cancel',exact:true}).click();await page.getByRole('button',{name:'Rename',exact:true}).click();await expect(page.getByLabel('Title',{exact:true})).toHaveAttribute('readonly','');
 await page.route('**/api/studies/'+study,async r=>{if(r.request().method()!=='GET')return r.fallback();metadata.title='Newer current title';metadata.revision='3';return r.fulfill({json:{...attribution,id:study,...metadata}});});release();await expect(page.getByRole('heading',{name:'Newer current title',exact:true})).toBeVisible();
});
test('rename: navigation and account replacement reject late private responses',async({page})=>{
 let release;const gate=new Promise(resolve=>release=resolve);await setup(page,{beforeRename:()=>gate});await firstNote(page);await page.getByRole('button',{name:'Back to Studies',exact:true}).click();await page.getByRole('button',{name:'Rename',exact:true}).click();await page.getByLabel('Title',{exact:true}).fill('Prior private candidate');await page.getByRole('button',{name:'Save',exact:true}).click();await expect(page.getByRole('status')).toContainText('Saving title');await page.getByRole('button',{name:'Leave study',exact:true}).click();release();await expect(page.getByRole('heading',{name:'Prior private candidate',exact:true})).toHaveCount(0);
 await page.getByRole('button',{name:'Prior private candidate',exact:true}).click();await page.getByRole('button',{name:'Rename',exact:true}).click();await page.getByLabel('Title',{exact:true}).fill('Unsubmitted prior input');await page.route('**/auth/v1/token*',r=>r.fulfill({json:{...session,access_token:'other-account',user:{...session.user,id:'10000000-0000-4000-8000-000000000002'}}}));await page.evaluate(async()=>{const {supabase}=await import('/src/lib/supabase.ts');await supabase.auth.signInWithPassword({email:'other@example.invalid',password:'fixture'});});await expect(page.getByLabel('Title',{exact:true})).toHaveCount(0);expect(await page.locator('body').innerText()).not.toContain('Unsubmitted prior input');
});

test('rename: account replacement during executing command rejects its late reply',async({page})=>{
 let release;const gate=new Promise(resolve=>release=resolve);await setup(page,{beforeRename:()=>gate});await firstNote(page);await page.getByRole('button',{name:'Back to Studies',exact:true}).click();await page.getByRole('button',{name:'Rename',exact:true}).click();await page.getByLabel('Title',{exact:true}).fill('Late prior-account title');const reply=page.waitForResponse('**/api/studies/'+study+'/title');await page.getByRole('button',{name:'Save',exact:true}).click();await expect(page.getByRole('status')).toContainText('Saving title');
 await page.route('**/auth/v1/token*',r=>r.fulfill({json:{...session,access_token:'other-account',user:{...session.user,id:'10000000-0000-4000-8000-000000000002'}}}));await page.evaluate(async()=>{const {supabase}=await import('/src/lib/supabase.ts');await supabase.auth.signInWithPassword({email:'other@example.invalid',password:'fixture'});});await expect(page.getByLabel('Title',{exact:true})).toHaveCount(0);release();await reply;await expect(page.getByRole('heading',{name:'Late prior-account title',exact:true})).toHaveCount(0);expect(await page.locator('body').innerText()).not.toContain('Late prior-account title');
});
for(const status of [401,403])test('rename: '+status+' hides private state and preserves public reading',async({page})=>{
 const options={failRename:status};const {requests}=await setup(page,options);await firstNote(page);await page.getByRole('button',{name:'Back to Studies',exact:true}).click();await page.getByRole('button',{name:'Rename',exact:true}).click();await page.getByLabel('Title',{exact:true}).fill('Recoverable title');await page.getByRole('button',{name:'Save',exact:true}).click();await expect(page.getByRole('alert')).toContainText(status===401?'Sign in':'access is unavailable');await expect(page.getByLabel('Title',{exact:true})).toHaveCount(0);await expect(page.getByText('בְּרֵאשִׁית',{exact:true}).first()).toBeAttached();
 if(status===401){const original=requests.find(r=>r.path.endsWith('/title')).payload;await page.route('**/auth/v1/token*',r=>r.fulfill({json:{...session,access_token:'renewed-current'}}));await page.evaluate(async()=>{const {supabase}=await import('/src/lib/supabase.ts');await supabase.auth.signInWithPassword({email:'reader@example.invalid',password:'fixture'});});options.failRename=0;await page.getByRole('button',{name:'Retry',exact:true}).click();await expect(page.getByLabel('Title',{exact:true})).toHaveValue('Recoverable title');expect(requests.filter(r=>r.path.endsWith('/title'))).toHaveLength(1);await page.getByRole('button',{name:'Retry rename',exact:true}).click();await expect(page.getByRole('heading',{name:'Recoverable title',exact:true})).toBeVisible();expect(requests.filter(r=>r.path.endsWith('/title'))[1].payload).toEqual(original);}
});

for(const surface of ['begin','conflict reload'])test('rename: late '+surface+' metadata cannot reopen a departed title editor',async({page})=>{
 const options={failRename:409};await setup(page,options);await firstNote(page);await page.getByRole('button',{name:'Back to Studies',exact:true}).click();
 if(surface==='conflict reload'){await page.getByRole('button',{name:'Rename',exact:true}).click();await page.getByLabel('Title',{exact:true}).fill('Kept candidate');await page.getByRole('button',{name:'Save',exact:true}).click();await expect(page.getByRole('alert')).toContainText('title changed elsewhere');}
 let release;const gate=new Promise(resolve=>release=resolve);await page.route('**/api/studies/'+study,async r=>{await gate;return r.fallback();});const response=page.waitForResponse('**/api/studies/'+study);
 await page.getByRole('button',{name:surface==='begin'?'Rename':'Load current title',exact:true}).click();await page.getByRole('button',{name:'Leave study',exact:true}).click();release();await response;await expect(page.getByLabel('Title',{exact:true})).toHaveCount(0);await expect(page.getByRole('button',{name:'Untitled study',exact:true})).toBeVisible();
});

test('rename: failed dirty note lane remains independent and recoverable',async({page})=>{
 const options={failPut:503};const {requests}=await setup(page,options);await firstNote(page);const editor=page.getByLabel('Note text',{exact:true});await editor.fill('Dirty note retained while renaming');await expect(page.getByRole('status')).toContainText('Changes not saved');const noteAttempt=requests.find(r=>r.path.includes('/notes/')&&r.method==='PUT').payload;
 await page.getByRole('button',{name:'Back to Studies',exact:true}).click();await page.getByRole('button',{name:'Rename',exact:true}).click();await page.getByLabel('Title',{exact:true}).fill('Independent metadata');await page.getByRole('button',{name:'Save',exact:true}).click();await expect(page.getByRole('heading',{name:'Independent metadata',exact:true})).toBeVisible();await page.getByRole('button',{name:'Analysis',exact:true}).click();await expect(editor).toHaveText('Dirty note retained while renaming');await expect(page.getByRole('status')).toContainText('Changes not saved');options.failPut=0;await page.getByRole('button',{name:'Retry',exact:true}).click();await expect(page.getByRole('status')).toContainText('Draft saved');const notes=requests.filter(r=>r.path.includes('/notes/')&&r.method==='PUT');expect(notes).toHaveLength(2);expect(notes[1].payload).toEqual(noteAttempt);
});

async function patchRename(page,options={}){const fixture=await setup(page,options);await firstNote(page);await page.getByRole('button',{name:'Back to Studies',exact:true}).click();await page.getByRole('button',{name:'Rename',exact:true}).click();return fixture;}
test('rename patch: opening a note during rename still reconciles its study heading',async({page})=>{
 let release;const gate=new Promise(resolve=>release=resolve);await patchRename(page,{beforeRename:()=>gate});await page.getByLabel('Title',{exact:true}).fill('Renamed with note open');await page.getByRole('button',{name:'Save',exact:true}).click();await page.getByRole('button',{name:'Empty note',exact:true}).click();release();await expect(page.getByLabel('Note text',{exact:true})).toBeVisible();await page.getByRole('button',{name:'Back to Studies',exact:true}).click();await expect(page.getByRole('heading',{name:'Renamed with note open',exact:true})).toBeVisible();
});
test('rename patch: confirmed PUT retries only a failed metadata read',async({page})=>{
 const {requests}=await patchRename(page);let reads=0;await page.route('**/api/studies/'+study,r=>{reads++;return reads===1?r.fulfill({status:503,json:{code:'studies_storage_unavailable'}}):r.fallback();});await page.getByLabel('Title',{exact:true}).fill('Confirmed title');await page.getByRole('button',{name:'Save',exact:true}).click();await expect(page.getByRole('alert')).toContainText('Title saved');await page.getByRole('button',{name:'Retry title refresh',exact:true}).click();await expect(page.getByRole('heading',{name:'Confirmed title',exact:true})).toBeVisible();expect(requests.filter(r=>r.path.endsWith('/title'))).toHaveLength(1);expect(reads).toBe(2);
});
test('rename patch: two hundred supplementary scalars remain intact and focus returns',async({page})=>{
 const {requests}=await patchRename(page);const title='𐐀'.repeat(200);await page.getByLabel('Title',{exact:true}).fill(title);await expect(page.getByLabel('Title',{exact:true})).toHaveValue(title);await page.getByLabel('Title',{exact:true}).press('Tab');await page.getByRole('button',{name:'Save',exact:true}).press('Enter');await expect(page.getByRole('heading',{name:title,exact:true})).toBeVisible();expect(requests.find(r=>r.path.endsWith('/title')).payload.title).toBe(title);await expect(page.getByRole('button',{name:'Rename',exact:true})).toBeFocused();await page.getByRole('button',{name:'Rename',exact:true}).press('Enter');await expect(page.getByLabel('Title',{exact:true})).toBeFocused();await page.getByLabel('Title',{exact:true}).press('Tab');await page.getByRole('button',{name:'Cancel',exact:true}).press('Enter');await expect(page.getByRole('button',{name:'Rename',exact:true})).toBeFocused();
});
test('rename patch: reversed conflict reloads keep newest base revision',async({page})=>{
 const options={failRename:409};const {requests}=await patchRename(page,options);await page.getByLabel('Title',{exact:true}).fill('Mine');await page.getByRole('button',{name:'Save',exact:true}).click();await expect(page.getByRole('button',{name:'Load current title',exact:true})).toBeVisible();const gates=[];await page.route('**/api/studies/'+study,r=>new Promise(resolve=>gates.push({release:async revision=>{await r.fulfill({json:{...attribution,id:study,title:'Current '+revision,revision}});resolve();}})));await page.getByRole('button',{name:'Load current title',exact:true}).click();await page.getByRole('button',{name:'Load current title',exact:true}).click();await expect.poll(()=>gates.length).toBe(2);await gates[1].release('3');await expect(page.getByRole('heading',{name:'Current 3',exact:true})).toBeVisible();const older=page.waitForResponse('**/api/studies/'+study);await gates[0].release('2');await older;options.failRename=0;await page.unroute('**/api/studies/'+study);await page.getByRole('button',{name:'Save',exact:true}).click();await expect.poll(()=>requests.filter(r=>r.path.endsWith('/title')).length).toBe(2);expect(requests.filter(r=>r.path.endsWith('/title'))[1].payload.expected_revision).toBe('3');
});
for(const status of [401,403])test('rename patch: late reload '+status+' after departure does not revoke current context',async({page})=>{
 await patchRename(page,{failRename:409});await page.getByLabel('Title',{exact:true}).fill('Mine');await page.getByRole('button',{name:'Save',exact:true}).click();await expect(page.getByRole('button',{name:'Load current title',exact:true})).toBeVisible();let release;const gate=new Promise(resolve=>release=resolve);await page.route('**/api/studies/'+study,async r=>{await gate;return r.fulfill({status,json:{code:status===401?'authentication_required':'studies_access_denied'}});});const response=page.waitForResponse('**/api/studies/'+study);await page.getByRole('button',{name:'Load current title',exact:true}).click();await page.getByRole('button',{name:'Leave study',exact:true}).click();await expect(page.getByRole('button',{name:'Untitled study',exact:true})).toBeVisible();release();await response;await expect(page.getByRole('alert')).toHaveCount(0);await expect(page.getByRole('button',{name:'Untitled study',exact:true})).toBeVisible();
});
test('rename patch: delayed old library keeps newer renamed metadata',async({page})=>{
 let releaseRename;const renameGate=new Promise(resolve=>releaseRename=resolve);const {metadata}=await setup(page,{beforeRename:()=>renameGate});await firstNote(page);await page.getByRole('button',{name:'Back to Studies',exact:true}).click();await page.getByRole('button',{name:'Leave study',exact:true}).click();await page.getByRole('button',{name:'Untitled study',exact:true}).click();await page.getByRole('button',{name:'Rename',exact:true}).click();await page.getByLabel('Title',{exact:true}).fill('Newest library title');let releaseList;const listGate=new Promise(resolve=>releaseList=resolve);await page.route('**/api/studies/search',async r=>{await listGate;return r.fulfill({json:{items:[{...attribution,id:study,title:'Untitled study',revision:'1'}],next_cursor:null}});});await page.getByRole('button',{name:'Save',exact:true}).click();await page.getByRole('button',{name:'Leave study',exact:true}).click();const currentRead=page.waitForResponse('**/api/studies/'+study);releaseRename();await currentRead;await expect.poll(()=>metadata.revision).toBe('2');const oldList=page.waitForResponse('**/api/studies/search');releaseList();await oldList;await expect(page.getByRole('button',{name:'Newest library title',exact:true})).toBeVisible();
});
for(const phase of ['executing','unknown'])test('rename patch: beforeunload warns for '+phase+' title operation',async({page})=>{
 let release;const gate=new Promise(resolve=>release=resolve);const options=phase==='executing'?{beforeRename:()=>gate}:{dropRename:true,unresolved:true};await patchRename(page,options);await page.getByLabel('Title',{exact:true}).fill('Pending unload');await page.getByRole('button',{name:'Save',exact:true}).click();await expect(page.getByRole(phase==='executing'?'status':'alert')).toContainText(phase==='executing'?'Saving title':'Title not saved');await page.getByRole('button',{name:'Cancel',exact:true}).click();const prevented=await page.evaluate(()=>{const event=new Event('beforeunload',{cancelable:true});window.dispatchEvent(event);return event.defaultPrevented;});expect(prevented).toBe(true);release();
});
test('rename patch: slow begin shows loading and prevents duplicate start',async({page})=>{
 await setup(page);await firstNote(page);await page.getByRole('button',{name:'Back to Studies',exact:true}).click();let release;const gate=new Promise(resolve=>release=resolve);let reads=0;await page.route('**/api/studies/'+study,async r=>{reads++;await gate;return r.fallback();});await page.getByRole('button',{name:'Rename',exact:true}).click();await expect(page.getByRole('status')).toContainText('Loading Studies');await expect(page.getByRole('button',{name:'Rename',exact:true})).toBeDisabled();expect(reads).toBe(1);release();await expect(page.getByLabel('Title',{exact:true})).toBeVisible();
});
test('rename patch: overlapping same-study metadata cannot lower heading revision',async({page})=>{
 const {metadata}=await setup(page);await firstNote(page);await page.getByRole('button',{name:'Back to Studies',exact:true}).click();let release;const gate=new Promise(resolve=>release=resolve);let reads=0;await page.route('**/api/studies/'+study,async r=>{if(++reads!==1)return r.fallback();await gate;return r.fulfill({json:{...attribution,id:study,title:'Older metadata',revision:'1'}});});await page.getByRole('button',{name:'Rename',exact:true}).click();await page.getByRole('button',{name:'Leave study',exact:true}).click();metadata.title='Newest metadata';metadata.revision='3';await expect(page.getByRole('button',{name:'Untitled study',exact:true})).toBeVisible();await page.getByRole('button',{name:'Untitled study',exact:true}).click();await expect(page.getByRole('heading',{name:'Newest metadata',exact:true})).toBeVisible();const older=page.waitForResponse('**/api/studies/'+study);release();await older;await expect(page.getByRole('heading',{name:'Newest metadata',exact:true})).toBeVisible();
});

test('rename patch: opening a note during initial read releases loading without reopening title',async({page})=>{
 await setup(page);await firstNote(page);await page.getByRole('button',{name:'Back to Studies',exact:true}).click();let release;const gate=new Promise(resolve=>release=resolve);await page.route('**/api/studies/'+study,async r=>{await gate;return r.fallback();});await page.getByRole('button',{name:'Rename',exact:true}).click();await expect(page.getByRole('status')).toContainText('Loading Studies');await page.getByRole('button',{name:'Empty note',exact:true}).click();await expect(page.getByLabel('Note text',{exact:true})).toBeVisible();const read=page.waitForResponse('**/api/studies/'+study);release();await read;await page.getByRole('button',{name:'Back to Studies',exact:true}).click();await expect(page.getByLabel('Title',{exact:true})).toHaveCount(0);await expect(page.getByRole('button',{name:'Rename',exact:true})).toBeEnabled();await expect(page.getByRole('button',{name:'Add note',exact:true})).toBeEnabled();await expect(page.getByRole('status')).toHaveCount(0);
});

test('collected passage keeps dirty writing and opens only explicitly',async({page})=>{
 const {requests}=await setup(page,{failPut:503});await firstNote(page);
 await page.getByLabel('Note text',{exact:true}).fill('Dirty collection observation עברית');
 await page.getByRole('button',{name:'Back to Studies',exact:true}).click();
 await page.getByRole('button',{name:'Add passage',exact:true}).click();
 await page.getByLabel('Passage reference',{exact:true}).fill('Genesis1:31–2:3');
 await page.getByLabel('Passage reference',{exact:true}).press('Enter');
 await expect(page.getByRole('list',{name:'Passages',exact:true})).toContainText('Genesis 1:31–2:3');
 expect(readerParams(page.url()).get('chapter')).toBe(null);
 await page.getByRole('button',{name:'Analysis',exact:true}).click();await expect(page.getByLabel('Note text',{exact:true})).toContainText('Dirty collection observation');
 expect(requests.filter(r=>r.path.endsWith('/passages')&&r.method==='PUT')).toHaveLength(1);
});

async function collectionStudy(page){await page.goto('/');await page.getByRole('button',{name:'Studies',exact:true}).click();await page.getByRole('button',{name:'Start a study',exact:true}).click();await page.getByRole('button',{name:'Create study',exact:true}).click();await expect(page.getByRole('button',{name:'Add passage',exact:true})).toBeEnabled();}
async function addReference(page,text,label='Add passage'){await page.getByRole('button',{name:label,exact:true}).click();await page.getByLabel('Passage reference',{exact:true}).fill(text);await page.getByLabel('Passage reference',{exact:true}).press('Enter');}

test('collected passages persist chapters Hebrew ranges overlap and duplicate IDs without navigation',async({page})=>{
 const {requests,collection,metadata}=await setup(page);await collectionStudy(page);
 for(const text of ['בראשית א','תהילים קי:1','Ps 110:1–3','Genesis1:31–2:3','Matthew26:63–64']){await addReference(page,text);await expect(page.getByRole('button',{name:'Add passage',exact:true})).toBeEnabled();}
 const list=page.getByRole('list',{name:'Passages',exact:true});await expect(list.locator('li')).toHaveCount(5);expect(collection.items[0].reference.target).toEqual({kind:'chapter',chapter:1});const original=JSON.stringify(collection),writes=requests.filter(r=>r.path.endsWith('/passages')&&r.method==='PUT').length;
 await addReference(page,'Genesis 1');await expect(page.getByRole('alert')).toContainText('Already in this study');await expect(page.getByLabel('Passage reference',{exact:true})).toHaveValue('Genesis 1');await expect(page.getByLabel('Passage reference',{exact:true})).toBeEditable();await page.getByRole('button',{name:'Cancel',exact:true}).click();expect(JSON.stringify(collection)).toBe(original);expect(requests.filter(r=>r.path.endsWith('/passages')&&r.method==='PUT')).toHaveLength(writes);expect(metadata.revision).toBe('1');expect(readerParams(page.url()).has('verse')).toBe(false);
 await page.reload();await page.getByRole('button',{name:'Studies',exact:true}).click();await page.getByRole('button',{name:'Untitled study',exact:true}).click();await expect(list.locator('li')).toHaveCount(5);await expect(list).toContainText('Genesis 1:31–2:3');
 await page.getByRole('button',{name:'Open Matthew 26:63–64',exact:true}).click();await expect(page.getByText(/Matthew 26:63–64 — Text unavailable/)).toBeVisible();expect(readerParams(page.url()).get('verse')).toBe('63');expect(readerParams(page.url()).get('EndVerse')).toBe('64');await expect(page.getByRole('button',{name:/Word:/})).toHaveCount(0);await page.getByRole('button',{name:'Next chapter',exact:true}).click();expect(readerParams(page.url()).get('chapter')).toBe('27');await page.goBack();await expect(page.getByText(/Matthew 26:63–64 — Text unavailable/)).toBeVisible();
 await page.getByRole('button',{name:'Studies',exact:true}).click();await page.getByRole('button',{name:'Remove Psalms 110:1–3',exact:true}).click();await expect(list.locator('li')).toHaveCount(4);await expect(list).toContainText('Psalms 110:1');
});

test('collected picker cancels restores focus rejects bad numbering and clears range on another chapter',async({page})=>{
 const {requests}=await setup(page);await collectionStudy(page);const add=page.getByRole('button',{name:'Add passage',exact:true});await add.click();const input=page.getByLabel('Passage reference',{exact:true});
 for(const text of ['Ps2:10–13','Genesis 1.1','Ps 11.0:1','Gen 1:3–1','unknown1']){await input.fill(text);await input.press('Enter');await expect(input).toBeVisible();await expect(page.getByText('Enter a valid book and chapter, verse or range.')).toBeVisible();}
 await input.fill('Genesis1:31–2:3');await expect(page.getByRole('button',{name:'Chapter 1 of Genesis',exact:true})).toHaveAttribute('aria-current','page');await input.press('Escape');await expect(add).toBeFocused();expect(requests.filter(r=>r.method==='PUT')).toHaveLength(0);
 await add.click();await input.fill('Genesis1:31–2:3');await page.getByRole('button',{name:'Chapter 2 of Genesis',exact:true}).click();await expect(page.getByRole('list',{name:'Passages',exact:true})).toContainText('Genesis 2');expect(requests.find(r=>r.method==='PUT').payload.items[0].reference.target).toEqual({kind:'chapter',chapter:2});
 await page.getByRole('button',{name:'Add current passage',exact:true}).click();await expect(input).toHaveValue('Genesis 1');await page.getByRole('button',{name:'Cancel',exact:true}).click();await expect(page.getByRole('button',{name:'Add current passage',exact:true})).toBeFocused();
});

test('collected passages conflict keeps candidate and requires current-list review and explicit new action',async({page})=>{
 const options={failPassages:409};const {requests,collection}=await setup(page,options);await collectionStudy(page);await addReference(page,'Ps110:1–3');await expect(page.getByRole('alert')).toContainText('Passages changed elsewhere');await expect(page.getByText('Intended change: Add Psalms 110:1–3')).toBeVisible();const first=requests.find(r=>r.method==='PUT').payload;
 const concurrent={id:'50000000-0000-4000-8000-000000000001',reference:first.items[0].reference};concurrent.reference=JSON.parse(JSON.stringify(concurrent.reference));concurrent.reference.book_id='Gen';concurrent.reference.target={kind:'chapter',chapter:2};collection.items=[concurrent];collection.revision='2';
 options.failPassages=0;await page.getByRole('button',{name:'Load current passages',exact:true}).click();await expect(page.getByRole('button',{name:'Apply reviewed change',exact:true})).toBeVisible();expect(requests.filter(r=>r.method==='PUT')).toHaveLength(1);await expect(page.getByRole('list',{name:'Passages',exact:true})).toContainText('Genesis 2');await page.getByRole('button',{name:'Apply reviewed change',exact:true}).click();await expect(page.getByRole('list',{name:'Passages',exact:true})).toContainText('Psalms 110:1–3');const second=requests.filter(r=>r.method==='PUT').at(-1).payload;expect(second.operation_id).not.toBe(first.operation_id);expect(second.expected_revision).toBe('2');expect(second.items).toHaveLength(2);expect(second.items[0]).toEqual(concurrent);expect(second.items[1].reference).toEqual(first.items[0].reference);await expect(page.getByRole('list',{name:'Passages',exact:true})).toContainText('Genesis 2');
});

test('collected uncertain operation freezes its snapshot and retries original identity',async({page})=>{
 const options={dropPassages:true,unresolved:true};const {requests,collection}=await setup(page,options);await collectionStudy(page);await addReference(page,'Gen1:31–2:3');await expect(page.getByRole('button',{name:'Retry passage change',exact:true})).toBeVisible();await expect(page.getByRole('button',{name:'Add passage',exact:true})).toBeDisabled();const first=requests.find(r=>r.method==='PUT').payload;expect(collection.items).toHaveLength(1);
 const warned=await page.evaluate(()=>{const event=new Event('beforeunload',{cancelable:true});window.dispatchEvent(event);return event.defaultPrevented;});expect(warned).toBe(true);
 options.unresolved=false;await page.getByRole('button',{name:'Retry passage change',exact:true}).click();await expect(page.getByRole('list',{name:'Passages',exact:true})).toContainText('Genesis 1:31–2:3');expect(requests.filter(r=>r.method==='PUT').map(r=>r.payload)).toEqual([first,first]);expect(collection.revision).toBe('2');
});

test('collected acknowledged success retries only current read after refresh failure',async({page})=>{
 const options={afterPassageCommit:()=>{options.failPassageRead=true;}};const {requests}=await setup(page,options);await collectionStudy(page);await addReference(page,'Gen1');await expect(page.getByRole('alert')).toContainText('Passages saved. Current list could not be refreshed');const writes=requests.filter(r=>r.method==='PUT').length;expect(await page.evaluate(()=>{const event=new Event('beforeunload',{cancelable:true});window.dispatchEvent(event);return event.defaultPrevented;})).toBe(false);
 options.failPassageRead=false;await page.getByRole('button',{name:'Retry passages refresh',exact:true}).click();await expect(page.getByRole('list',{name:'Passages',exact:true})).toContainText('Genesis 1');expect(requests.filter(r=>r.method==='PUT')).toHaveLength(writes);
});

test('collected late account response cannot repopulate another account',async({page})=>{
 let release;const options={beforePassagePut:()=>new Promise(resolve=>release=resolve)};await setup(page,options);await collectionStudy(page);await addReference(page,'Ps110');await expect.poll(()=>Boolean(release)).toBe(true);
 await page.route('**/auth/v1/token*',r=>r.fulfill({json:{...session,access_token:'other-account',user:{...session.user,id:'10000000-0000-4000-8000-000000000002'}}}));await page.evaluate(async()=>{const {supabase}=await import('/src/lib/supabase.ts');await supabase.auth.signInWithPassword({email:'other@example.invalid',password:'fixture'});});release();await expect(page.getByRole('list',{name:'Passages',exact:true})).toHaveCount(0);await expect(page.getByText('Psalms 110',{exact:true})).toHaveCount(0);await expect(page.getByRole('button',{name:'Studies',exact:true})).toBeVisible();
});

for(const status of [401,403,404])test(`collected current access or lifecycle refusal ${status} keeps public reader usable`,async({page})=>{
 await setup(page,{failPassages:status});await collectionStudy(page);await addReference(page,'Gen1');if(status===404)await expect(page.getByRole('button',{name:'Retry passage change',exact:true})).toBeVisible();else await expect(page.getByRole('alert')).toContainText(status===401?'Sign in':'Studies access');await page.getByRole('button',{name:'Studies',exact:true}).click();await expect(page.getByRole('region',{name:'Chapter text',exact:true})).toBeVisible();await expect(page.getByRole('button',{name:/Word:/})).toBeVisible();
});

test('collected reference parser Python and browser accept the same canonical examples',async({page})=>{
 await setup(page);await page.goto('/');const samples=['Psalm110:1','Ps 110:1–3','תהילים קי:1','Genesis1:31–2:3','Matthew26:63–64','בראשית ט״ו','1 Samuel 2','Psalm קטו:1','Psalm קטז:1','Ps 119:קטו–קטז','I. Samuel 2'];const actual=await page.evaluate(async samples=>{const {parseReference}=await import('/src/lib/passage-references.ts');return samples.map(parseReference);},samples);
 const {execFileSync}=require('node:child_process'),path=require('node:path');const script="import json,sys;from apps.scribeswell.backend.passage_references import parse_reference;print(json.dumps([parse_reference(s) for s in json.loads(sys.argv[1])]))";const expected=JSON.parse(execFileSync(process.env.SCRIBESWELL_TEST_PYTHON||'python3',['-c',script,JSON.stringify(samples)],{cwd:path.resolve(__dirname,'../../../..'),encoding:'utf8'}));expect(actual).toEqual(expected);
});

for(const status of [401,403])test(`collected late initial read ${status} after study departure cannot revoke current context`,async({page})=>{
 await reviewLibrary(page);let release;let first=true;
 await page.route('**/api/studies/*/passages',async r=>{const parent=new URL(r.request().url()).pathname.split('/')[3];if(parent===study&&first){first=false;await new Promise(resolve=>release=resolve);return r.fulfill({status,json:{code:status===401?'authentication_required':'studies_access_denied'}});}return r.fulfill({json:{study_id:parent,revision:'1',items:[]}});});
 await page.getByRole('button',{name:'Study A',exact:true}).click();await expect.poll(()=>Boolean(release)).toBe(true);await page.getByRole('button',{name:'Leave study',exact:true}).click();await page.getByRole('button',{name:'Study B',exact:true}).click();await expect(page.getByRole('button',{name:'Add passage',exact:true})).toBeEnabled();release();await page.waitForTimeout(100);await expect(page.getByRole('heading',{name:'Study B',exact:true})).toBeVisible();await expect(page.getByRole('alert')).toHaveCount(0);
});

test('collected obsolete initial read cannot change executing lane status',async({page})=>{
 let releaseRead,releasePut,reads=0;const options={beforePassageRead:()=>{reads++;if(reads===2)return new Promise(resolve=>releaseRead=resolve);},beforePassagePut:()=>new Promise(resolve=>releasePut=resolve)};await setup(page,options);await collectionStudy(page);await page.getByRole('button',{name:'Leave study',exact:true}).click();await page.getByRole('button',{name:'Untitled study',exact:true}).click();await expect.poll(()=>Boolean(releaseRead)).toBe(true);await page.getByRole('button',{name:'Add passage',exact:true}).click();await page.getByLabel('Passage reference',{exact:true}).fill('Ps110');await page.getByLabel('Passage reference',{exact:true}).press('Enter');await expect.poll(()=>Boolean(releasePut)).toBe(true);releaseRead();await page.waitForTimeout(100);await expect(page.getByRole('status').filter({hasText:'Saving passages…'})).toHaveCount(1);options.beforePassagePut=undefined;releasePut();await expect(page.getByRole('list',{name:'Passages',exact:true})).toContainText('Psalms 110');
});

test('collected server input rejection keeps editable candidate and correction uses fresh operation',async({page})=>{
 const options={failPassages:400};const {requests}=await setup(page,options);await collectionStudy(page);await addReference(page,'Ps110:1–3');const input=page.getByLabel('Passage reference',{exact:true});await expect(input).toHaveValue('Ps110:1–3');await expect(input).toBeEditable();options.failPassages=0;await input.fill('Genesis1');await input.press('Enter');await expect(input).toHaveCount(0);await expect(page.getByRole('list',{name:'Passages',exact:true})).toContainText('Genesis 1');const puts=requests.filter(r=>r.method==='PUT');expect(puts).toHaveLength(2);expect(puts[0].payload.operation_id).not.toBe(puts[1].payload.operation_id);
});

test('collected matching chapter confirms complete range and explicit Open preserves dirty note and other pane',async({page})=>{
 await setup(page,{failPut:503});await firstNote(page);await page.getByLabel('Note text',{exact:true}).fill('Dirty while opening a range');await expect(page.getByRole('status').filter({hasText:'Changes not saved'})).toBeVisible();await addReader(page);await page.getByRole('button',{name:'Back to Studies',exact:true}).click();await page.getByRole('button',{name:'Add passage',exact:true}).click();await page.getByLabel('Passage reference',{exact:true}).fill('Genesis1:31–2:3');await page.getByRole('button',{name:'Chapter 1 of Genesis',exact:true}).click();await expect(page.getByRole('list',{name:'Passages',exact:true})).toContainText('Genesis 1:31–2:3');expect(readerParams(page.url()).has('compareVerse')).toBe(false);await page.getByRole('button',{name:'Open Genesis 1:31–2:3',exact:true}).click();const url=new URL(page.url());expect(readerParams(url.href).get('chapter')).toBe('1');expect(readerParams(url.href).get('compareVerse')).toBe('31');expect(readerParams(url.href).get('compareEndChapter')).toBe('2');expect(readerParams(url.href).get('compareEndVerse')).toBe('3');await page.getByRole('button',{name:'Analysis',exact:true}).click();await expect(page.getByLabel('Note text',{exact:true})).toContainText('Dirty while opening a range');
});

test('collected supported source outage retains reference and offers truthful chapter Retry',async({page})=>{
 await setup(page);await page.route('**/api/bible/books/Ps/chapters/110/verses*',r=>r.fulfill({status:503,json:{code:'unavailable'}}));await collectionStudy(page);await addReference(page,'Ps110');await page.getByRole('button',{name:'Open Psalms 110',exact:true}).click();await expect(page.getByRole('button',{name:'Retry chapter',exact:true})).toBeVisible();await expect(page.getByText('Text unavailable',{exact:false})).toHaveCount(0);await page.getByRole('button',{name:'Studies',exact:true}).click();await expect(page.getByRole('list',{name:'Passages',exact:true})).toContainText('Psalms 110');
});

// Focused corrections from independent delivery review.
test('passage review parser rejects numeric Hebrew punctuation with Python browser parity',async({page})=>{
 await setup(page);await page.goto('/');const samples=['Gen . 1','Gen 1׃1','Gen 1׀1','Gen 1.1','Genesis 1:1׃2','Ps 11.0:1','I. Samuel 2','II. Samuel 2','Ps. 110:1'];
 const actual=await page.evaluate(async samples=>{const {parseReference}=await import('/src/lib/passage-references.ts');return samples.map(text=>{try{return parseReference(text);}catch{return null;}});},samples);
 const {execFileSync}=require('node:child_process'),path=require('node:path');const script="import json,sys;from apps.scribeswell.backend.passage_references import parse_reference,ReferenceError\ndef parse(s):\n try:return parse_reference(s)\n except ReferenceError:return None\nprint(json.dumps([parse(s) for s in json.loads(sys.argv[1])]))";const expected=JSON.parse(execFileSync(process.env.SCRIBESWELL_TEST_PYTHON||'python3',['-c',script,JSON.stringify(samples)],{cwd:path.resolve(__dirname,'../../../..'),encoding:'utf8'}));expect(actual).toEqual(expected);expect(actual.slice(0,6)).toEqual([null,null,null,null,null,null]);expect(actual[6].book_id).toBe('1Sam');
});

for(const query of ['chapter=0','chapter=bad','chapter=1.5','chapter=51','verse=0','verse=bad','verse=32','verse=1&EndChapter=0','verse=1&EndChapter=bad','verse=1&EndChapter=51','verse=1&EndVerse=0','verse=1&EndVerse=bad','verse=1&EndVerse=32','EndVerse=2','verse=2&EndVerse=1'])test(`passage review malformed current coordinates stay uncollectable ${query}`,async({page})=>{
 await setup(page);await page.goto('/?book=Gen&'+query);const original=new URL(page.url()).search;await page.getByRole('button',{name:'Studies',exact:true}).click();await page.getByRole('button',{name:'Start a study',exact:true}).click();await page.getByRole('button',{name:'Create study',exact:true}).click();await expect(page.getByRole('button',{name:'Add passage',exact:true})).toBeEnabled();await expect(page.getByRole('button',{name:'Add current passage',exact:true})).toHaveCount(0);expect(new URL(page.url()).search).toBe(original);
});
for(const query of ['chapter=1&verse=2','chapter=1&verse=2&EndChapter=1','chapter=1&verse=2&EndVerse=3','verse=2'])test(`passage review absent endpoints alone may default ${query}`,async({page})=>{
 await setup(page);await page.goto('/?book=Gen&'+query);await page.getByRole('button',{name:'Studies',exact:true}).click();await page.getByRole('button',{name:'Start a study',exact:true}).click();await page.getByRole('button',{name:'Create study',exact:true}).click();await page.getByRole('button',{name:'Add current passage',exact:true}).click();await expect(page.getByLabel('Passage reference',{exact:true})).toHaveValue(query.includes('EndVerse=3')?'Genesis 1:2–3':'Genesis 1:2');await page.getByRole('button',{name:'Cancel',exact:true}).click();
});

test('passage review Stay retains pending initial collection read',async({page})=>{
 let release;const options={failPut:503,beforePassageRead:()=>new Promise(resolve=>release=resolve)};await setup(page,options);await firstNote(page);await expect.poll(()=>Boolean(release)).toBe(true);await page.getByLabel('Note text',{exact:true}).fill('Dirty retained study');await expect(page.getByRole('status').filter({hasText:'Changes not saved'})).toBeVisible();await page.getByRole('button',{name:'Back to Studies',exact:true}).click();await page.getByRole('button',{name:'Leave study',exact:true}).click();await page.getByRole('button',{name:'Stay',exact:true}).click();options.beforePassageRead=undefined;release();await expect(page.getByRole('button',{name:'Add passage',exact:true})).toBeEnabled();await page.getByRole('button',{name:'Analysis',exact:true}).click();await expect(page.getByLabel('Note text',{exact:true})).toContainText('Dirty retained study');
});

test('passage review remove conflict identifies original reference after concurrent deletion',async({page})=>{
 const options={};const {collection}=await setup(page,options);await collectionStudy(page);await addReference(page,'Ps110:1–3');await expect(page.getByRole('button',{name:'Add passage',exact:true})).toBeEnabled();options.failPassages=409;await page.getByRole('button',{name:'Remove Psalms 110:1–3',exact:true}).click();await expect(page.getByText('Intended change: Remove Psalms 110:1–3',{exact:true})).toBeVisible();collection.items=[];collection.revision='3';options.failPassages=0;await page.getByRole('button',{name:'Load current passages',exact:true}).click();await expect(page.getByRole('list',{name:'Passages',exact:true}).locator('li')).toHaveCount(0);await expect(page.getByText('Intended change: Remove Psalms 110:1–3',{exact:true})).toBeVisible();
});

for(const destination of ['focus','reopen'])test(`passage review dismissed executing picker never steals ${destination}`,async({page})=>{
 let release;const options={beforePassagePut:()=>new Promise(resolve=>release=resolve)};await setup(page,options);await collectionStudy(page);await addReference(page,'Gen1');await expect.poll(()=>Boolean(release)).toBe(true);expect(await page.evaluate(()=>{const event=new Event('beforeunload',{cancelable:true});window.dispatchEvent(event);return event.defaultPrevented;})).toBe(true);await page.getByRole('button',{name:'Cancel',exact:true}).click();
 if(destination==='focus'){await page.getByRole('button',{name:'Rename',exact:true}).click();await page.getByLabel('Title',{exact:true}).fill('Focused after cancellation');}
 else{if(test.info().project.name==='mobile')await page.getByRole('button',{name:'Return to reader',exact:true}).click();await page.getByRole('button',{name:/Navigate:/}).first().click();await page.getByLabel('Passage reference',{exact:true}).fill('Ps110');}
 options.beforePassagePut=undefined;release();await expect(page.locator('ul[aria-label="Passages"]')).toContainText('Genesis 1');
 if(destination==='focus')await expect(page.getByLabel('Title',{exact:true})).toBeFocused();else{await expect(page.getByLabel('Passage reference',{exact:true})).toHaveValue('Ps110');await expect(page.getByLabel('Passage reference',{exact:true})).toBeFocused();}
});

test('note links: insert at caret retains writing and format2 after final deletion',async({page})=>{
 const {requests}=await setup(page);await firstNote(page);const editor=page.getByLabel('Note text',{exact:true});await editor.fill('Before שלום after');await editor.evaluate(el=>{el.focus();const range=document.createRange();range.setStart(el.firstChild,7);range.collapse(true);getSelection().removeAllRanges();getSelection().addRange(range);});
 await page.getByRole('button',{name:'Insert passage reference',exact:true}).click();await page.getByLabel('Passage reference',{exact:true}).fill('Genesis 1:31–2:3');await page.getByLabel('Passage reference',{exact:true}).press('Enter');await expect(editor).toContainText('Before Genesis 1:31–2:3שלום after');
 await expect(page.getByRole('status').filter({hasText:'Draft saved'})).toBeVisible();const put=requests.filter(r=>r.method==='PUT'&&r.path.endsWith('/notes/'+note)).at(-1);expect(put.payload.value.document.version).toBe(2);expect(put.payload.value.document.blocks[0].content.find(i=>i.type==='passage_link').reference.target.end).toEqual({chapter:2,verse:3});expect(requests.filter(r=>r.method==='PUT'&&r.path.endsWith('/passages'))).toHaveLength(0);
 await editor.locator('[data-note-passage]').evaluate(el=>el.remove());await editor.dispatchEvent('input');await expect.poll(()=>requests.filter(r=>r.method==='PUT'&&r.path.endsWith('/notes/'+note)).at(-1).payload.value.document.blocks[0].content.some(i=>i.type==='passage_link')).toBe(false);expect(requests.filter(r=>r.method==='PUT'&&r.path.endsWith('/notes/'+note)).at(-1).payload.value.document.version).toBe(2);
});

async function insertNoteReference(page,text){await page.getByRole('button',{name:'Insert passage reference',exact:true}).click();await page.getByLabel('Passage reference',{exact:true}).fill(text);await page.getByLabel('Passage reference',{exact:true}).press('Enter');}
for(const [input,label] of [['תהילים קי:1','Psalms 110:1'],['Genesis 2','Genesis 2'],['Matthew26:63–64','Matthew 26:63–64']])test(`note links: canonical insertion ${input} preserves current reader and note`,async({page})=>{
 const {requests}=await setup(page);await firstNote(page);const url=page.url(),editor=page.getByLabel('Note text',{exact:true});await editor.fill('My explanation שָׁלוֹם');await editor.evaluate(el=>{el.focus();const r=document.createRange();r.selectNodeContents(el);getSelection().removeAllRanges();getSelection().addRange(r);});await insertNoteReference(page,input);await expect(editor).toContainText('My explanation שָׁלוֹם'+label);expect(page.url()).toBe(url);await expect(editor.locator('[data-note-passage]')).toHaveCount(1);await expect(page.getByRole('status').filter({hasText:'Draft saved'})).toBeVisible();expect(requests.filter(r=>r.method==='POST'&&r.path.endsWith('/notes'))).toHaveLength(1);expect(requests.filter(r=>r.method==='PUT'&&r.path.endsWith('/passages'))).toHaveLength(0);
});
test('note links: cancel invalid IME and stale input preserve writing and useful reference input',async({page})=>{
 const {requests}=await setup(page);await firstNote(page);const editor=page.getByLabel('Note text',{exact:true});await editor.fill('Useful שָׁלוֹם');await expect(page.getByRole('status').filter({hasText:'Draft saved'})).toBeVisible();const before=requests.filter(r=>r.method==='PUT').length;
 await page.getByRole('button',{name:'Insert passage reference',exact:true}).click();const input=page.getByLabel('Passage reference',{exact:true});await input.fill('Ps 2:10–13');await input.press('Enter');await expect(input).toHaveValue('Ps 2:10–13');await expect(editor.locator('[data-note-passage]')).toHaveCount(0);await page.getByRole('button',{name:'Cancel',exact:true}).click();await expect(editor).toBeFocused();expect(requests.filter(r=>r.method==='PUT')).toHaveLength(before);
 await editor.dispatchEvent('compositionstart');await expect(page.getByRole('button',{name:'Insert passage reference',exact:true})).toBeDisabled();await expect(page.getByRole('button',{name:'Read note',exact:true})).toBeDisabled();await editor.dispatchEvent('compositionend');
 await page.getByRole('button',{name:'Insert passage reference',exact:true}).click();await input.fill('Gen 1');await editor.evaluate(el=>{el.append(document.createTextNode(' later'));el.dispatchEvent(new InputEvent('input',{bubbles:true}));});await input.press('Enter');await expect(input).toHaveValue('Gen 1');await expect(page.getByText('Place the caret in this note, then try inserting the reference again.',{exact:true})).toBeVisible();await expect(editor).toContainText('Useful שָׁלוֹם later');await expect(editor.locator('[data-note-passage]')).toHaveCount(0);await page.getByRole('button',{name:'Cancel',exact:true}).click();await page.getByRole('button',{name:'Insert passage reference',exact:true}).click();await expect(input).toHaveValue('Gen 1');await page.getByRole('button',{name:'Cancel',exact:true}).click();
});
test('note links: edit click offers Open read click navigates active pane with full range and same lane',async({page})=>{
 const {requests}=await setup(page);await firstNote(page);const editor=page.getByLabel('Note text',{exact:true});await editor.fill('Context ');await insertNoteReference(page,'Matthew26:63–64');const atom=editor.locator('[data-note-passage]'),url=page.url();await atom.click();expect(page.url()).toBe(url);await expect(page.getByRole('button',{name:'Open passage',exact:true})).toBeVisible();await page.getByRole('button',{name:'Open passage',exact:true}).click();await expect(page.getByText('Matthew 26:63–64 — Text unavailable',{exact:true})).toBeVisible();if(page.viewportSize().width<768)await page.getByRole('button',{name:'Analysis',exact:true}).click();await expect(editor).toContainText('Context Matthew 26:63–64');const opened=page.url();await page.getByRole('button',{name:'Read note',exact:true}).click();expect(page.url()).toBe(opened);await expect(editor).toHaveAttribute('aria-readonly','true');await atom.click();expect(page.url()).toBe(opened);if(page.viewportSize().width<768)await page.getByRole('button',{name:'Analysis',exact:true}).click();await page.getByRole('button',{name:'Edit note',exact:true}).click();await expect(editor).toHaveAttribute('contenteditable','true');expect(requests.filter(r=>r.method==='POST'&&r.path.endsWith('/notes'))).toHaveLength(1);expect(requests.filter(r=>r.method==='PUT'&&r.path.endsWith('/passages'))).toHaveLength(0);
});
test('note links: links source marks lists direction plain paste and reload roundtrip',async({page})=>{
 const {requests}=await setup(page);await firstNote(page);const editor=page.getByLabel('Note text',{exact:true});await editor.fill('Mixed עברית');await editor.press('ControlOrMeta+End');await page.getByLabel('Paragraph direction',{exact:true}).selectOption('rtl');await page.getByRole('button',{name:'Bullet list',exact:true}).click();await insertNoteReference(page,'Gen 1:31–2:3');await editor.press('End');await editor.press('ControlOrMeta+b');await editor.press('ArrowRight');await editor.press('ControlOrMeta+b');
 // Use a native clipboard event with HTML and a distinct plain-text value.
 await editor.evaluate(el=>{el.focus();const d=new DataTransfer();d.setData('text/html','<span data-note-passage="true">forged</span>');d.setData('text/plain',' plain');el.dispatchEvent(new ClipboardEvent('paste',{bubbles:true,clipboardData:d}));});
 await expect(page.getByRole('status').filter({hasText:'Draft saved'})).toBeVisible();const saved=structuredClone(requests.filter(r=>r.method==='PUT'&&r.path.endsWith('/notes/'+note)).at(-1).payload.value);expect(saved.document.version).toBe(2);expect(saved.document.blocks.some(b=>b.type==='list')).toBe(true);await page.reload();await page.getByRole('button',{name:'Studies',exact:true}).click();await page.getByRole('button',{name:'Untitled study',exact:true}).click();await page.getByRole('list',{name:'Notes',exact:true}).getByRole('button').click();await expect(editor.locator('[data-note-passage]')).toHaveCount(1);await expect(editor).toContainText('Genesis 1:31–2:3');await editor.press('End');await editor.press(' ');await expect(page.getByRole('status').filter({hasText:'Draft saved'})).toBeVisible();expect(requests.filter(r=>r.method==='PUT'&&r.path.endsWith('/notes/'+note)).at(-1).payload.value.document.version).toBe(2);
});
test('note links: corrupt and foreign atoms stay unsaved and cannot switch to stale reading',async({page})=>{
 const {requests}=await setup(page);await firstNote(page);const editor=page.getByLabel('Note text',{exact:true});await insertNoteReference(page,'Gen 1');await expect(page.getByRole('status').filter({hasText:'Draft saved'})).toBeVisible();const before=requests.filter(r=>r.method==='PUT').length;await editor.locator('[data-note-passage]').evaluate(el=>{el.textContent='corrupt';el.parentElement.dispatchEvent(new InputEvent('input',{bubbles:true}));});await expect(page.getByRole('status')).toContainText('Changes not saved');await expect(page.getByRole('button',{name:'Read note',exact:true})).toBeDisabled();await page.waitForTimeout(650);expect(requests.filter(r=>r.method==='PUT')).toHaveLength(before);await editor.evaluate(el=>{el.replaceChildren();const s=document.createElement('span');s.dataset.notePassage='true';s.textContent='foreign';s.contentEditable='false';el.append(s);el.dispatchEvent(new InputEvent('input',{bubbles:true}));});await expect(page.getByRole('status')).toContainText('Changes not saved');await page.waitForTimeout(650);expect(requests.filter(r=>r.method==='PUT')).toHaveLength(before);
});
test('note links: terminal format refusal pauses saves and retains whole local note',async({page})=>{
 const options={failPut:409,failPutCode:'note_format_unsupported'};const {requests}=await setup(page,options);await firstNote(page);const editor=page.getByLabel('Note text',{exact:true});await insertNoteReference(page,'Gen 1');await expect(page.getByRole('alert')).toContainText('Reload to continue editing.');const count=requests.filter(r=>r.method==='PUT').length;await editor.press('End');await editor.press('x');await page.waitForTimeout(650);expect(requests.filter(r=>r.method==='PUT')).toHaveLength(count);await expect(editor).toContainText('Genesis 1');await expect(page.getByRole('status')).toContainText('Changes not saved');await expect(page.getByRole('button',{name:'Retry',exact:true})).toHaveCount(0);
});

test('note links: keyboard edit offers Open and keyboard read opens range in active pane only',async({page})=>{
 const {requests}=await setup(page);await firstNote(page);await addReader(page);const editor=page.getByLabel('Note text',{exact:true});await editor.fill('Keep same note ');await insertNoteReference(page,'Gen 1:31–2:3');const atom=editor.locator('[data-note-passage]'),before=new URL(page.url());await atom.focus();await atom.press('Enter');expect(page.url()).toBe(before.href);await expect(page.getByRole('button',{name:'Open passage',exact:true})).toBeVisible();await page.getByRole('button',{name:'Read note',exact:true}).click();await atom.focus();await atom.press('Space');await expect.poll(()=>readerParams(page.url()).get('compareEndVerse')).toBe('3');const url=new URL(page.url());expect(readerParams(url.href).get('compareVerse')).toBe('31');expect(readerParams(url.href).get('compareEndChapter')).toBe('2');expect(readerParams(url.href).get('book')).toBe(readerParams(before.href).get('book'));expect(readerParams(url.href).get('chapter')).toBe(readerParams(before.href).get('chapter'));if(page.viewportSize().width<768)await page.getByRole('button',{name:'Analysis',exact:true}).click();await expect(editor).toContainText('Keep same note Genesis 1:31–2:3');expect(requests.filter(r=>r.method==='POST'&&r.path.endsWith('/notes'))).toHaveLength(1);
});
test('note links: unknown original operation and delayed acknowledgement preserve coherent newer value in Read',async({page})=>{
 let release;const options={dropPut:true,beforeLookup:()=>new Promise(resolve=>release=resolve)};const {requests}=await setup(page,options);await firstNote(page);const editor=page.getByLabel('Note text',{exact:true});await insertNoteReference(page,'Gen 1');await expect.poll(()=>Boolean(release)).toBe(true);const first=structuredClone(requests.filter(r=>r.method==='PUT').at(-1).payload);await editor.press('End');await editor.press('x');await page.getByRole('button',{name:'Read note',exact:true}).click();await expect(editor).toContainText('Genesis 1x');await expect(page.getByRole('status')).not.toHaveText('Draft saved');expect(requests.filter(r=>r.method==='PUT')).toHaveLength(1);options.beforeLookup=undefined;release();await expect(page.getByRole('status').filter({hasText:'Draft saved'})).toBeVisible();const puts=requests.filter(r=>r.method==='PUT');expect(puts).toHaveLength(2);expect(puts[0].payload).toEqual(first);expect(puts[1].payload.value.document.version).toBe(2);expect(puts[1].payload.operation_id).not.toBe(first.operation_id);await expect(editor.locator('[data-note-passage]')).toHaveCount(1);
});
for(const key of ['Backspace','Delete'])test(`note links: ${key} removes atomic inline and retains version2`,async({page})=>{
 const {requests}=await setup(page);await firstNote(page);const editor=page.getByLabel('Note text',{exact:true});await insertNoteReference(page,'Gen 1');await editor.locator('[data-note-passage]').evaluate((el,key)=>{const r=document.createRange();if(key==='Backspace')r.setStartAfter(el);else r.setStartBefore(el);r.collapse(true);el.parentElement.focus();getSelection().removeAllRanges();getSelection().addRange(r);},key);await editor.press(key);await expect(editor.locator('[data-note-passage]')).toHaveCount(0);await expect(page.getByRole('status').filter({hasText:'Draft saved'})).toBeVisible();expect(requests.filter(r=>r.method==='PUT').at(-1).payload.value.document.version).toBe(2);
});
test('note links: account replacement clears picker and pending insertion without leaking prior writing',async({page})=>{
 await setup(page);await firstNote(page);await page.getByLabel('Note text',{exact:true}).fill('Private prior note');await page.getByRole('button',{name:'Insert passage reference',exact:true}).click();await page.getByLabel('Passage reference',{exact:true}).fill('Gen 1');await page.route('**/auth/v1/token*',r=>r.fulfill({json:{...session,user:{...session.user,id:'10000000-0000-4000-8000-000000000002'}}}));await page.evaluate(async()=>{const {supabase}=await import('/src/lib/supabase.ts');await supabase.auth.signOut({scope:'local'});await supabase.auth.signInWithPassword({email:'other@example.invalid',password:'fixture'});});await expect(page.getByLabel('Passage reference',{exact:true})).toHaveCount(0);await expect(page.getByText('Private prior note',{exact:true})).toHaveCount(0);
});
test('note links: note switch cancels picker without inserting into replacement note',async({page})=>{
 const {requests}=await setup(page);await firstNote(page);const editor=page.getByLabel('Note text',{exact:true});await editor.fill('First note writing');await expect(page.getByRole('status').filter({hasText:'Draft saved'})).toBeVisible();await page.getByRole('button',{name:'Insert passage reference',exact:true}).click();await page.getByLabel('Passage reference',{exact:true}).fill('Gen 1');
 const nextNote='40000000-0000-4000-8000-000000000002';await page.route(`**/api/studies/${study}/notes`,r=>r.request().method()==='POST'?r.fulfill({json:{operation_id:r.request().postDataJSON().operation_id,command:'note.create',study_id:study,note_id:nextNote,revision:'1'}}):r.fallback());await page.route(`**/api/studies/${study}/notes/${nextNote}`,r=>r.fulfill({json:{...attribution,id:nextNote,study_id:study,visibility:'study',revision:'1',value:{document:{version:1,blocks:[]},connections:[],highlights:[]}}}));
 await page.getByRole('button',{name:'Back to Studies',exact:true}).evaluate(el=>el.click());await page.getByRole('button',{name:'Add note',exact:true}).evaluate(el=>el.click());await expect(page.getByLabel('Passage reference',{exact:true})).toHaveCount(0);await expect(editor).toHaveText('');await expect(editor.locator('[data-note-passage]')).toHaveCount(0);expect(requests.filter(r=>r.method==='PUT')).toHaveLength(1);
});
for(const position of [0,6,14])test(`note links: insertion inside source at ${position} preserves source text marks and URL`,async({page})=>{
 const {requests}=await setup(page);await firstNote(page);const editor=page.getByLabel('Note text',{exact:true});await editor.fill('source writing');await editor.press('ControlOrMeta+a');await page.getByRole('button',{name:'Bold',exact:true}).click();await page.getByRole('button',{name:'Link',exact:true}).click();await page.getByLabel('Link URL',{exact:true}).fill('https://example.org');await page.getByRole('button',{name:'Insert link',exact:true}).click();await editor.locator('a').evaluate((el,position)=>{const r=document.createRange();r.setStart(document.createTreeWalker(el,NodeFilter.SHOW_TEXT).nextNode(),position);r.collapse(true);getSelection().removeAllRanges();getSelection().addRange(r);},position);await insertNoteReference(page,'Gen 1');await expect(page.getByRole('status').filter({hasText:'Draft saved'})).toBeVisible();const content=requests.filter(r=>r.method==='PUT').at(-1).payload.value.document.blocks[0].content;expect(content.map(i=>i.type)).toEqual(position===0?['passage_link','external_link']:position===14?['external_link','passage_link']:['external_link','passage_link','external_link']);const sources=content.filter(i=>i.type==='external_link');expect(sources.flatMap(i=>i.content).map(i=>i.text).join('')).toBe('source writing');expect(sources.every(i=>i.url==='https://example.org'&&i.content.every(t=>JSON.stringify(t.marks)==='["bold"]'))).toBe(true);
});
test('note links: caret inside an existing atom resolves after it without corrupting its label',async({page})=>{
 await setup(page);await firstNote(page);const editor=page.getByLabel('Note text',{exact:true});await insertNoteReference(page,'Gen 1');await editor.locator('[data-note-passage]').evaluate(el=>{const r=document.createRange();r.setStart(el.firstChild,3);r.collapse(true);getSelection().removeAllRanges();getSelection().addRange(r);});await insertNoteReference(page,'Gen 2');await expect(editor.locator('[data-note-passage]')).toHaveCount(2);await expect(editor.locator('[data-note-passage]').nth(0)).toHaveText('Genesis 1');await expect(editor.locator('[data-note-passage]').nth(1)).toHaveText('Genesis 2');await expect(page.getByRole('status').filter({hasText:'Draft saved'})).toBeVisible();
});
test('note links: Read Edit restores caret and keeps ordinary notes in format1',async({page})=>{
 const {requests}=await setup(page);await firstNote(page);const editor=page.getByLabel('Note text',{exact:true});await editor.fill('before after');await editor.evaluate(el=>{const r=document.createRange();r.setStart(el.firstChild,7);r.collapse(true);getSelection().removeAllRanges();getSelection().addRange(r);});const url=page.url();await page.getByRole('button',{name:'Read note',exact:true}).click();await page.getByRole('button',{name:'Edit note',exact:true}).click();await editor.press('x');await expect(editor).toHaveText('before xafter');expect(page.url()).toBe(url);await expect(page.getByRole('status').filter({hasText:'Draft saved'})).toBeVisible();expect(requests.filter(r=>r.method==='PUT').at(-1).payload.value.document.version).toBe(1);
});

test('note links patch: direction after atomic insertion targets the actual paragraph',async({page})=>{
 const {requests}=await setup(page);await firstNote(page);await insertNoteReference(page,'Gen 1');await page.getByLabel('Paragraph direction',{exact:true}).selectOption('rtl');await expect(page.getByRole('status').filter({hasText:'Draft saved'})).toBeVisible();await expect.poll(()=>requests.filter(r=>r.method==='PUT').at(-1).payload.value.document.blocks[0].direction).toBe('rtl');
});
test('note links patch: deliberate external focus is retained when picker closes',async({page})=>{
 await setup(page);await firstNote(page);await page.getByRole('button',{name:'Insert passage reference',exact:true}).click();await page.getByLabel('Passage reference',{exact:true}).fill('Gen 1');const direction=page.getByLabel('Paragraph direction',{exact:true});await direction.focus();await expect(page.getByLabel('Passage reference',{exact:true})).toHaveCount(0);await expect(direction).toBeFocused();
});
test('note links patch: atomic label isolates direction inside opposite-direction text',async({page})=>{
 await setup(page);await firstNote(page);await page.getByLabel('Paragraph direction',{exact:true}).selectOption('rtl');await insertNoteReference(page,'תהילים קי:1');const atom=page.getByLabel('Note text',{exact:true}).locator('[data-note-passage]');await expect(atom).toHaveAttribute('dir','auto');await expect(atom).toHaveCSS('unicode-bidi','isolate');
});
test('note links patch: queued insertion does not steal a deliberately changed focus',async({page})=>{
 await setup(page);await firstNote(page);await page.getByRole('button',{name:'Insert passage reference',exact:true}).click();const input=page.getByLabel('Passage reference',{exact:true});await input.fill('Gen 1');await input.evaluate(el=>{el.form.requestSubmit();queueMicrotask(()=>document.querySelector('[aria-label="Paragraph direction"]').focus());});await expect(page.getByLabel('Note text',{exact:true}).locator('[data-note-passage]')).toHaveCount(1);await expect(page.getByLabel('Paragraph direction',{exact:true})).toBeFocused();
});
test('note links patch: Read hides source-link form and Edit restores its candidate without writing',async({page})=>{
 const {requests}=await setup(page);await firstNote(page);const editor=page.getByLabel('Note text',{exact:true});await editor.fill('Source selection');await expect(page.getByRole('status').filter({hasText:'Draft saved'})).toBeVisible();await editor.press('ControlOrMeta+a');await page.getByRole('button',{name:'Link',exact:true}).click();await page.getByLabel('Link URL',{exact:true}).fill('https://example.org/source');const before=requests.filter(r=>r.method==='PUT').length;await page.getByRole('button',{name:'Read note',exact:true}).click();await expect(page.getByLabel('Link URL',{exact:true})).toHaveCount(0);await expect(page.getByRole('button',{name:'Insert link',exact:true})).toHaveCount(0);expect(requests.filter(r=>r.method==='PUT')).toHaveLength(before);await page.getByRole('button',{name:'Edit note',exact:true}).click();await expect(page.getByLabel('Link URL',{exact:true})).toHaveValue('https://example.org/source');await page.getByRole('button',{name:'Insert link',exact:true}).click();await expect(editor.locator('a')).toHaveText('Source selection');await expect(page.getByRole('status').filter({hasText:'Draft saved'})).toBeVisible();
});

for(const position of [null,0,6,14])test(`note links review: native insertion Undo Redo preserves writing and source at ${position}`,async({page})=>{
 const {requests}=await setup(page);await firstNote(page);const editor=page.getByLabel('Note text',{exact:true});await editor.pressSequentially('source writing');await editor.press('ControlOrMeta+z');await expect(editor).toHaveText('');await editor.press('ControlOrMeta+Shift+z');await expect(editor).toHaveText('source writing');if(position!==null){await editor.press('ControlOrMeta+a');await page.getByRole('button',{name:'Link',exact:true}).click();await page.getByLabel('Link URL',{exact:true}).fill('https://example.org/source');await page.getByRole('button',{name:'Insert link',exact:true}).click();await editor.locator('a').evaluate((el,position)=>{const r=document.createRange();r.setStart(document.createTreeWalker(el,NodeFilter.SHOW_TEXT).nextNode(),position);r.collapse(true);getSelection().removeAllRanges();getSelection().addRange(r);},position);}else await editor.press('End');await insertNoteReference(page,'Gen 1');await expect(editor.locator('[data-note-passage]')).toHaveCount(1);await editor.press('ControlOrMeta+z');await expect(editor).toHaveText('source writing');await expect(editor.locator('[data-note-passage]')).toHaveCount(0);if(position!==null)await expect(editor.locator('a')).toHaveText('source writing');await editor.press('ControlOrMeta+Shift+z');await expect(editor.locator('[data-note-passage]')).toHaveCount(1);await expect(editor).toContainText('Genesis 1');await editor.press('End');await editor.press('!');await expect(editor).toContainText('!');await editor.press('ControlOrMeta+z');await expect(editor).not.toContainText('!');await expect(editor.locator('[data-note-passage]')).toHaveCount(1);await editor.press('ControlOrMeta+Shift+z');await expect(editor).toContainText('!');await expect(page.getByRole('status').filter({hasText:'Draft saved'})).toBeVisible();expect(requests.filter(r=>r.method==='PUT').at(-1).payload.value.document.version).toBe(2);
});
test('note links review: no-caret insertion follows trailing DIV and loose text',async({page})=>{
 await setup(page);await firstNote(page);const editor=page.getByLabel('Note text',{exact:true});await editor.evaluate(el=>{const p=document.createElement('p');p.textContent='First';const div=document.createElement('div');div.textContent='Last block';el.replaceChildren(p,div,document.createTextNode(' trailing'));el.dispatchEvent(new InputEvent('input',{bubbles:true}));getSelection().removeAllRanges();});await insertNoteReference(page,'Gen 1');await expect(editor).toHaveText('FirstLast block trailingGenesis 1');
});
test('note links review: interrupted composition replacement accepts insertion only in new lane',async({page})=>{
 const {requests}=await setup(page);await firstNote(page);const editor=page.getByLabel('Note text',{exact:true});await editor.dispatchEvent('compositionstart');await editor.fill('Unfinished old composition');await page.getByRole('button',{name:'Back to Studies',exact:true}).click();const next='40000000-0000-4000-8000-000000000002';await page.route(`**/api/studies/${study}/notes`,r=>r.request().method()==='POST'?r.fulfill({json:{operation_id:r.request().postDataJSON().operation_id,command:'note.create',study_id:study,note_id:next,revision:'1'}}):r.fallback());await page.route(`**/api/studies/${study}/notes/${next}`,r=>r.request().method()==='PUT'?r.fulfill({json:{operation_id:r.request().postDataJSON().operation_id,command:'note.replace',study_id:study,note_id:next,revision:'2'}}):r.fulfill({json:{...attribution,id:next,study_id:study,visibility:'study',revision:'1',value:{document:{version:1,blocks:[]},connections:[],highlights:[]}}}));await page.getByRole('button',{name:'Add note',exact:true}).click();await page.getByRole('button',{name:'Switch anyway',exact:true}).click();await expect(editor).toHaveText('');await insertNoteReference(page,'Gen 1');await expect(editor.locator('[data-note-passage]')).toHaveCount(1);expect(requests.filter(r=>r.method==='PUT'&&r.path.endsWith('/notes/'+note))).toHaveLength(0);
});
test('note links review: source link refuses selection containing owned atom before mutation',async({page})=>{
 const {requests}=await setup(page);await firstNote(page);const editor=page.getByLabel('Note text',{exact:true});await editor.fill('Explanation ');await insertNoteReference(page,'Gen 1');await expect(page.getByRole('status').filter({hasText:'Draft saved'})).toBeVisible();const before=await editor.innerHTML(),writes=requests.filter(r=>r.method==='PUT').length;await editor.press('ControlOrMeta+a');await page.getByRole('button',{name:'Link',exact:true}).click();await page.getByLabel('Link URL',{exact:true}).fill('https://example.org/source');await page.getByRole('button',{name:'Insert link',exact:true}).click();await expect(page.getByRole('alert')).toContainText('Select ordinary text');await expect(page.getByLabel('Link URL',{exact:true})).toHaveValue('https://example.org/source');expect(await editor.innerHTML()).toBe(before);expect(requests.filter(r=>r.method==='PUT')).toHaveLength(writes);
});
test('note links review: inline boundary refuses insertion without changing writing or closing candidate',async({page})=>{
 await setup(page);await firstNote(page);const editor=page.getByLabel('Note text',{exact:true});await editor.evaluate(el=>{const p=document.createElement('p');for(let i=0;i<256;i++){const span=document.createElement('span');span.textContent='x';p.append(span);}el.replaceChildren(p);el.dispatchEvent(new InputEvent('input',{bubbles:true}));getSelection().removeAllRanges();});await expect(page.getByRole('status').filter({hasText:'Draft saved'})).toBeVisible();const before=await editor.innerHTML();await page.getByRole('button',{name:'Insert passage reference',exact:true}).click();const input=page.getByLabel('Passage reference',{exact:true});await input.fill('Gen 1');await input.press('Enter');await expect(input).toHaveValue('Gen 1');const feedbackId=await input.getAttribute('aria-describedby');expect(feedbackId).toBeTruthy();await expect(page.locator('[id="'+feedbackId+'"]')).toHaveAttribute('aria-live','polite');expect(await editor.innerHTML()).toBe(before);await expect(editor.locator('[data-note-passage]')).toHaveCount(0);await expect(page.getByRole('status').filter({hasText:'Draft saved'})).toBeVisible();
});
test('note links review: retained reference reopens at its candidate book and rejection is accessible',async({page})=>{
 await setup(page);await firstNote(page);await page.getByRole('button',{name:'Insert passage reference',exact:true}).click();const input=page.getByLabel('Passage reference',{exact:true});await input.fill('Ps 110:1');await page.getByRole('button',{name:'Cancel',exact:true}).click();await page.getByRole('button',{name:'Insert passage reference',exact:true}).click();await expect(input).toHaveValue('Ps 110:1');await expect(page.getByRole('group',{name:'Chapters of Psalms',exact:true})).toBeVisible();await input.fill('Ps 2:13');await expect(input).toHaveAttribute('aria-invalid','true');const errorId=await input.getAttribute('aria-describedby');expect(errorId).toBeTruthy();await expect(page.locator('[id="'+errorId+'"]')).toHaveAttribute('role','alert');await expect(page.locator('[id="'+errorId+'"]')).toContainText('Enter a valid');
});
for(const command of ['Bold','Italic','Bullet list','Numbered list'])test(`note links review: ${command} across an owned atom survives save reload`,async({page})=>{
 const {requests}=await setup(page);await firstNote(page);const editor=page.getByLabel('Note text',{exact:true});await editor.fill('Before ');await insertNoteReference(page,'Gen 1');await editor.press('End');await editor.pressSequentially(' after');await editor.press('ControlOrMeta+a');await page.getByRole('button',{name:command,exact:true}).click();await expect(page.getByRole('status').filter({hasText:'Draft saved'})).toBeVisible();const saved=requests.filter(r=>r.method==='PUT').at(-1).payload.value;expect(JSON.stringify(saved)).toContain('passage_link');await page.reload();await page.getByRole('button',{name:'Studies',exact:true}).click();await page.getByRole('button',{name:'Untitled study',exact:true}).click();await page.getByRole('list',{name:'Notes',exact:true}).getByRole('button').click();await expect(editor).toHaveText('Before Genesis 1 after');await expect(editor.locator('[data-note-passage]')).toHaveCount(1);if(command==='Bold'||command==='Italic'){const paragraphs=saved.document.blocks.flatMap(b=>b.type==='paragraph'?[b]:b.items.flat());expect(paragraphs.flatMap(p=>p.content).filter(i=>i.type==='text').every(i=>i.marks.includes(command.toLowerCase()))).toBe(true);}else expect(saved.document.blocks[0].type).toBe('list');
});
test('note links review: passage-only saved Notes preview reopens with plain reference label',async({page})=>{
 await setup(page);await firstNote(page);await insertNoteReference(page,'Gen 1');await expect(page.getByRole('status').filter({hasText:'Draft saved'})).toBeVisible();await page.getByRole('button',{name:'Back to Studies',exact:true}).click();const button=page.getByRole('list',{name:'Notes',exact:true}).getByRole('button');await expect(button).toHaveText('Genesis 1');await button.click();await expect(page.getByLabel('Note text',{exact:true}).locator('[data-note-passage]')).toHaveText('Genesis 1');
});
test('note links review: noncanonical stored Unicode HTML-looking label stays plain and exact',async({page})=>{
 const catalogue=require('../src/generated/reference-catalogue.json'),label='שָׁלוֹם 😀 <b>stored</b> e\u0301',reference={catalogue_id:catalogue.catalogue_id,catalogue_version:catalogue.catalogue_version,versification_id:catalogue.books.find(b=>b.book_id==='Gen').versification_id,book_id:'Gen',target:{kind:'chapter',chapter:1}},noteValue={document:{version:2,blocks:[{type:'paragraph',direction:'rtl',content:[{type:'passage_link',reference,label}]}]},connections:[],highlights:[]};const {requests}=await setup(page,{noteValue});await firstNote(page);const editor=page.getByLabel('Note text',{exact:true}),atom=editor.locator('[data-note-passage]');await expect(atom).toHaveText(label);await expect(atom.locator('b')).toHaveCount(0);await page.getByRole('button',{name:'Read note',exact:true}).click();await expect(atom).toHaveText(label);await page.getByRole('button',{name:'Edit note',exact:true}).click();await editor.press('End');await editor.press('!');await expect(page.getByRole('status').filter({hasText:'Draft saved'})).toBeVisible();const saved=requests.filter(r=>r.method==='PUT').at(-1).payload.value;expect(saved.document.blocks[0].content.find(i=>i.type==='passage_link')).toEqual({type:'passage_link',reference,label});
});
test('note links review: ordinary copied metadata never acquires native-history ownership',async({page})=>{
 const {requests}=await setup(page);await firstNote(page);const editor=page.getByLabel('Note text',{exact:true});await insertNoteReference(page,'Gen 1');await expect(page.getByRole('status').filter({hasText:'Draft saved'})).toBeVisible();const before=requests.filter(r=>r.method==='PUT').length;await editor.locator('[data-note-passage]').evaluate(el=>{el.replaceWith(el.cloneNode(true));document.querySelector('[aria-label="Note text"]').dispatchEvent(new InputEvent('input',{bubbles:true}));});await expect(page.getByRole('status')).toContainText('Changes not saved');await expect(page.getByRole('button',{name:'Read note',exact:true})).toBeDisabled();await page.waitForTimeout(600);expect(requests.filter(r=>r.method==='PUT')).toHaveLength(before);
});
for(const method of ['paste','keyless input'])test(`note links review: ${method} at final atom uses editable caret boundary`,async({page})=>{
 await setup(page);await firstNote(page);const editor=page.getByLabel('Note text',{exact:true});await insertNoteReference(page,'Gen 1');await editor.press('ControlOrMeta+z');await editor.press('ControlOrMeta+Shift+z');await editor.press('End');if(method==='paste')await editor.evaluate(el=>{const data=new DataTransfer();data.setData('text/plain',' pasted');el.dispatchEvent(new ClipboardEvent('paste',{bubbles:true,clipboardData:data}));});else await page.keyboard.insertText(' keyless');await expect(editor).toHaveText('Genesis 1'+(method==='paste'?' pasted':' keyless'));await expect(page.getByRole('status').filter({hasText:'Draft saved'})).toBeVisible();
});

for(const prefix of ['', 'Keep'])for(const action of ['Backspace','Delete','beforeinput backward'])test(`note links deletion: ${action} on ${prefix||'empty'} removes one owned atom and native Undo Redo retains version2`,async({page})=>{
 const {requests}=await setup(page);await firstNote(page);const editor=page.getByLabel('Note text',{exact:true});if(prefix)await editor.pressSequentially(prefix);await insertNoteReference(page,'Gen 1');await editor.locator('[data-note-passage]').evaluate((atom,action)=>{const editor=document.querySelector('[aria-label="Note text"]'),range=document.createRange();if(action==='Delete')range.setStartBefore(atom);else range.setStartAfter(atom);range.collapse(true);editor.focus();getSelection().removeAllRanges();getSelection().addRange(range);if(action==='beforeinput backward'){editor.dataset.backwardInputs='0';editor.addEventListener('keydown',event=>event.stopImmediatePropagation(),{capture:true,once:true});editor.addEventListener('beforeinput',event=>{if(event.inputType==='deleteContentBackward')editor.dataset.backwardInputs=String(Number(editor.dataset.backwardInputs)+1);});}},action);await editor.press(action==='Delete'?'Delete':'Backspace');await expect(editor.locator('[data-note-passage]')).toHaveCount(0);await expect(editor).toHaveText(prefix);if(action==='beforeinput backward')await expect(editor).toHaveAttribute('data-backward-inputs','1');await expect(page.getByRole('status').filter({hasText:'Draft saved'})).toBeVisible();expect(requests.filter(r=>r.method==='PUT').at(-1).payload.value.document.version).toBe(2);
 await editor.press('ControlOrMeta+z');await expect(editor.locator('[data-note-passage]')).toHaveText('Genesis 1');await expect(editor).toHaveText(prefix+'Genesis 1');await expect(page.getByRole('status').filter({hasText:'Draft saved'})).toBeVisible();expect(requests.filter(r=>r.method==='PUT').at(-1).payload.value.document.version).toBe(2);await editor.press('ControlOrMeta+Shift+z');await expect(editor.locator('[data-note-passage]')).toHaveCount(0);await expect(editor).toHaveText(prefix);await expect(page.getByRole('status').filter({hasText:'Draft saved'})).toBeVisible();expect(requests.filter(r=>r.method==='PUT').at(-1).payload.value.document.version).toBe(2);
});

test('library search finds saved results beyond the first page and returns at loaded depth',async({page})=>{
 await setup(page);
 const reads=[];
 await page.route('**/api/studies/search',async r=>{
  const body=r.request().postDataJSON();reads.push(body);
  const items=body.query==='שלום'?[{...attribution,id:study,title:'Saved Hebrew study',revision:'1'}]:[{...attribution,id:study,title:'Untitled study',revision:'1'}];
  await r.fulfill({json:{items,next_cursor:body.cursor?null:'search-page-two'}});
 });
 await page.goto('/');await page.getByRole('button',{name:'Studies',exact:true}).click();
 await page.getByRole('textbox',{name:'Search studies',exact:true}).fill('שלום');
 await page.getByRole('button',{name:'Search',exact:true}).click();
 await expect(page.getByRole('button',{name:'Saved Hebrew study',exact:true})).toBeVisible();
 await page.getByRole('button',{name:'More studies',exact:true}).click();
 await expect(page.getByRole('button',{name:'More studies',exact:true})).toHaveCount(0);
 await expect(page.getByRole('button',{name:'Saved Hebrew study',exact:true})).toHaveCount(1);
 await page.getByRole('button',{name:'Saved Hebrew study',exact:true}).click();
 await page.getByRole('button',{name:'Leave study',exact:true}).click();
 await expect(page.getByRole('textbox',{name:'Search studies',exact:true})).toHaveValue('שלום');
 await expect.poll(()=>reads.filter(x=>x.query==='שלום').length).toBe(4);
 expect(reads.filter(x=>x.query==='שלום').map(x=>x.cursor??null)).toEqual([null,'search-page-two',null,'search-page-two']);
 expect(new URL(page.url()).search).not.toContain('שלום');
 expect(await page.evaluate(()=>JSON.stringify(localStorage)+JSON.stringify(sessionStorage))).not.toContain('שלום');
});

test('library search candidate Enter Clear and literal Unicode terms stay in read bodies',async({page})=>{
 const reads=[];await setup(page,{search:async(r,body)=>{reads.push(body);return r.fulfill({json:{items:[{...attribution,id:study,title:body.query||'Whole library',revision:'1'}],next_cursor:null}});}});
 await page.goto('/');await page.getByRole('button',{name:'Studies',exact:true}).click();
 const input=page.getByRole('textbox',{name:'Search studies',exact:true});
 await expect(page.getByRole('button',{name:'Whole library',exact:true})).toBeVisible();
 for(const query of ['Genesis 1:31–2:3','בראשית א:לא–ב:ג','Matthew','café 100% _ \\ "']){
  const count=reads.length;await input.fill(query);expect(reads.length).toBe(count);await input.press('Enter');await expect(page.getByRole('list',{name:'Studies',exact:true})).toContainText(query);
 }
 await page.getByRole('button',{name:'Clear',exact:true}).click();await expect(input).toHaveValue('');await expect(page.getByRole('button',{name:'Whole library',exact:true})).toBeVisible();
 expect(reads.every(body=>Object.keys(body).sort().join(',')==='cursor,query')).toBe(true);
 expect(await page.evaluate(()=>JSON.stringify(localStorage)+JSON.stringify(sessionStorage))).not.toContain('café');
 expect(new URL(page.url()).search).not.toContain('query');
});

for(const late of ['success','denial'])test(`library search ignores late old-query ${late} and loading finalizers`,async({page})=>{
 let release;await setup(page,{search:async(r,body)=>{
  if(body.query==='old'){await new Promise(resolve=>release=resolve);return r.fulfill(late==='denial'?{status:403,json:{code:'studies_access_denied'}}:{json:{items:[{...attribution,id:study,title:'Old private title',revision:'1'}],next_cursor:null}});}
  return r.fulfill({json:{items:body.query?[{...attribution,id:study,title:'Current title',revision:'1'}]:[],next_cursor:null}});
 }});
 await page.goto('/');await page.getByRole('button',{name:'Studies',exact:true}).click();const input=page.getByRole('textbox',{name:'Search studies',exact:true});
 await input.fill('old');await input.press('Enter');await expect.poll(()=>!!release).toBe(true);
 await input.fill('current');await input.press('Enter');await expect(page.getByRole('button',{name:'Current title',exact:true})).toBeVisible();release();
 await page.waitForTimeout(100);await expect(page.getByRole('button',{name:'Current title',exact:true})).toBeVisible();await expect(page.getByText('Old private title',{exact:true})).toHaveCount(0);await expect(page.getByText('Studies access is unavailable for this account.',{exact:false})).toHaveCount(0);
});

test('library search hides unavailable pages retries applied input and clears on denial',async({page})=>{
 let failure=0;const reads=[];await setup(page,{search:async(r,body)=>{reads.push(body.query);return r.fulfill(failure?{status:failure,json:{code:failure===403?'studies_access_denied':'studies_access_unavailable'}}:{json:{items:[{...attribution,id:study,title:'Verified title',revision:'1'}],next_cursor:'next'}});}});
 await page.goto('/');await page.getByRole('button',{name:'Studies',exact:true}).click();const input=page.getByRole('textbox',{name:'Search studies',exact:true});await input.fill('applied');await input.press('Enter');await expect(page.getByRole('button',{name:'Verified title',exact:true})).toBeVisible();
 failure=503;await page.getByRole('button',{name:'More studies',exact:true}).click();await expect(page.getByRole('button',{name:'Verified title',exact:true})).toHaveCount(0);await expect(input).toHaveValue('applied');
 await input.fill('candidate only');failure=0;await page.getByRole('button',{name:'Retry search',exact:true}).click();await expect(page.getByRole('button',{name:'Verified title',exact:true})).toBeVisible();expect(reads.at(-1)).toBe('applied');await expect(input).toHaveValue('candidate only');
 failure=403;await page.getByRole('button',{name:'More studies',exact:true}).click();await expect(input).toHaveValue('');await expect(page.getByRole('button',{name:'Verified title',exact:true})).toHaveCount(0);
});

test('library search deduplicates More and rejects a late page after query change',async({page})=>{
 let release;const reads=[];await setup(page,{search:async(r,body)=>{reads.push(body);if(body.cursor){await new Promise(resolve=>release=resolve);return r.fulfill({json:{items:[{...attribution,id:study,title:'Late page',revision:'1'}],next_cursor:null}});}return r.fulfill({json:{items:[{...attribution,id:study,title:body.query||'First page',revision:'1'}],next_cursor:'next'}});}});
 await page.goto('/');await page.getByRole('button',{name:'Studies',exact:true}).click();await page.getByRole('button',{name:'More studies',exact:true}).dblclick();await expect.poll(()=>!!release).toBe(true);expect(reads.filter(x=>x.cursor).length).toBe(1);
 await page.getByRole('textbox',{name:'Search studies',exact:true}).fill('New query');await page.getByRole('button',{name:'Search',exact:true}).click();await expect(page.getByRole('button',{name:'New query',exact:true})).toBeVisible();release();await page.waitForTimeout(100);await expect(page.getByRole('button',{name:'Late page',exact:true})).toHaveCount(0);
});

test('library search restores multi-page scroll and stable result focus after refreshed return',async({page})=>{
 let reads=0;await setup(page,{search:async(r,body)=>{reads++;const offset=body.cursor?20:0;const items=Array.from({length:20},(_,index)=>{const n=offset+index;return {...attribution,id:n===35?study:`30000000-0000-4000-8000-${String(n+10).padStart(12,'0')}`,title:`Result ${n}`,revision:'1'};});return r.fulfill({json:{items,next_cursor:body.cursor?null:'second'}});}});
 await page.goto('/');await page.getByRole('button',{name:'Studies',exact:true}).click();await page.getByRole('button',{name:'More studies',exact:true}).click();const result=page.getByRole('button',{name:'Result 35',exact:true});await result.scrollIntoViewIfNeeded();await result.focus();const before=await page.getByRole('complementary',{name:'Study tools',exact:true}).evaluate(el=>el.scrollTop);expect(before).toBeGreaterThan(0);await result.click();await page.getByRole('button',{name:'Leave study',exact:true}).click();
 await expect.poll(()=>reads).toBe(4);await expect(result).toBeFocused();await expect.poll(()=>page.getByRole('complementary',{name:'Study tools',exact:true}).evaluate(el=>el.scrollTop)).toBeGreaterThan(before-50);
});

test('library search account replacement clears candidates pages and rejects late denial',async({page})=>{
 let release;await setup(page,{search:async(r,body)=>{if(body.query){await new Promise(resolve=>release=resolve);return r.fulfill({status:403,json:{code:'studies_access_denied'}});}return r.fulfill({json:{items:[],next_cursor:null}});}});
 await page.goto('/');await page.getByRole('button',{name:'Studies',exact:true}).click();await page.getByRole('textbox',{name:'Search studies',exact:true}).fill('old private writing');await page.getByRole('button',{name:'Search',exact:true}).click();await expect.poll(()=>!!release).toBe(true);
 await page.route('**/auth/v1/token*',r=>r.fulfill({json:{...session,access_token:'other-account',user:{...session.user,id:'10000000-0000-4000-8000-000000000002'}}}));await page.evaluate(async()=>{const {supabase}=await import('/src/lib/supabase.ts');await supabase.auth.signInWithPassword({email:'other@example.invalid',password:'fixture'});});
 await expect(page.getByRole('button',{name:'Studies',exact:true})).toHaveAttribute('aria-pressed','false');await expect(page.getByRole('button',{name:'Analysis',exact:true})).toHaveAttribute('aria-pressed','false');await expect(page.getByRole('textbox',{name:'Search studies',exact:true})).toHaveCount(0);await page.getByRole('button',{name:'Studies',exact:true}).click();await expect(page.getByRole('textbox',{name:'Search studies',exact:true})).toHaveValue('');await page.getByRole('button',{name:'Search',exact:true}).click();await expect(page.getByText('No saved studies found.',{exact:true})).toBeVisible();release();await page.waitForTimeout(100);await expect(page.getByText('Studies access is unavailable for this account.',{exact:false})).toHaveCount(0);
});

test('library search old completion cannot stop current loading',async({page})=>{
 const releases={};await setup(page,{search:async(r,body)=>{if(body.query)await new Promise(resolve=>releases[body.query]=resolve);return r.fulfill({json:{items:[],next_cursor:null}});}});
 await page.goto('/');await page.getByRole('button',{name:'Studies',exact:true}).click();const input=page.getByRole('textbox',{name:'Search studies',exact:true});await input.fill('old');await input.press('Enter');await expect.poll(()=>!!releases.old).toBe(true);await input.fill('new');await input.press('Enter');await expect.poll(()=>!!releases.new).toBe(true);releases.old();await page.waitForTimeout(100);await expect(page.getByRole('status').filter({hasText:'Loading studies…'})).toBeVisible();releases.new();await expect(page.getByRole('status').filter({hasText:'Loading studies…'})).toHaveCount(0);
});

test('library search preserves unacknowledged note input and reader position in its independent lane',async({page})=>{
 const {requests}=await setup(page);await firstNote(page);await reviewTabAdd(page);await expect(page.getByRole('tablist',{name:'Workspace tabs'}).getByRole('tab')).toHaveCount(2);await page.getByRole('button',{name:'Analysis',exact:true}).click();const editor=page.getByLabel('Note text',{exact:true});await editor.dispatchEvent('compositionstart');await editor.fill('Unacknowledged personal writing');const location=page.url();await page.getByRole('button',{name:'Back to Studies',exact:true}).click();await page.getByRole('button',{name:'Leave study',exact:true}).click();await expect(page.getByRole('dialog',{name:'Changes not saved'})).toHaveCount(0);await page.getByRole('textbox',{name:'Search studies',exact:true}).fill('saved reference');await page.getByRole('button',{name:'Search',exact:true}).click();await page.getByRole('button',{name:'Untitled study',exact:true}).click();await page.getByRole('list',{name:'Notes',exact:true}).getByRole('button').click();await expect(editor).toContainText('Unacknowledged personal writing');expect(page.url()).toBe(location);expect(requests.filter(r=>r.method==='PUT')).toHaveLength(0);expect(requests.filter(r=>r.path.endsWith('/search')).every(r=>!JSON.stringify(r.payload).includes('Unacknowledged personal writing'))).toBe(true);
});

test('library search authentication failure stops loading and successful same-account retry clears sign-in error',async({page})=>{
 let failure=false;await setup(page,{search:async r=>r.fulfill(failure?{status:401,json:{code:'authentication_required'}}:{json:{items:[{...attribution,id:study,title:'Authorized again',revision:'1'}],next_cursor:null}})});
 await page.goto('/');await page.getByRole('button',{name:'Studies',exact:true}).click();await expect(page.getByRole('button',{name:'Authorized again',exact:true})).toBeVisible();await page.getByRole('textbox',{name:'Search studies',exact:true}).fill('retained private candidate');failure=true;await page.getByRole('button',{name:'Search',exact:true}).click();await expect(page.getByRole('alert').filter({hasText:'Sign in to use My studies.'}).first()).toBeVisible();await expect(page.getByRole('status').filter({hasText:'Loading studies…'})).toHaveCount(0);await expect(page.getByRole('textbox',{name:'Search studies',exact:true})).toHaveValue('');failure=false;await page.getByRole('button',{name:'Retry search',exact:true}).click();await expect(page.getByRole('button',{name:'Authorized again',exact:true})).toBeVisible();await expect(page.getByRole('alert')).toHaveCount(0);await expect(page.getByRole('textbox',{name:'Search studies',exact:true})).toHaveValue('retained private candidate');
});


test('library search invalid input retains editable candidate and corrected Enter recovers',async({page})=>{
 await setup(page,{search:async(r,body)=>r.fulfill(body.query.length>200?{status:400,json:{code:'scribeswell_personal_notes_input_invalid'}}:{json:{items:[],next_cursor:null}})});
 await page.goto('/');await page.getByRole('button',{name:'Studies',exact:true}).click();const input=page.getByRole('textbox',{name:'Search studies',exact:true});const oversized='x'.repeat(201);await input.fill(oversized);await input.press('Enter');await expect(page.getByRole('alert')).toContainText('Enter a valid search');await expect(input).toHaveValue(oversized);await expect(input).toBeEditable();await input.fill('corrected');await input.press('Enter');await expect(page.getByRole('alert')).toHaveCount(0);await expect(page.getByText('No saved studies found.',{exact:true})).toBeVisible();
});

test('library review: composing Enter and submit preserve candidate until normal Enter',async({page})=>{
 const reads=[];await setup(page,{search:async(r,body)=>{reads.push(body.query);return r.fulfill({json:{items:[],next_cursor:null}});}});await page.goto('/');await page.getByRole('button',{name:'Studies',exact:true}).click();await expect.poll(()=>reads.length).toBe(1);const input=page.getByRole('textbox',{name:'Search studies',exact:true});await input.dispatchEvent('compositionstart');await input.fill('שלום');await input.press('Enter');await input.evaluate(el=>el.form.requestSubmit());await page.waitForTimeout(100);expect(reads).toEqual(['']);await expect(input).toHaveValue('שלום');await input.dispatchEvent('compositionend');await input.press('Enter');await expect.poll(()=>reads.length).toBe(2);expect(reads[1]).toBe('שלום');
});

test('library review: masked candidate refuses editing and restores exact private input',async({page})=>{
 let failure=false;await setup(page,{search:async r=>r.fulfill(failure?{status:401,json:{code:'authentication_required'}}:{json:{items:[],next_cursor:null}})});await page.goto('/');await page.getByRole('button',{name:'Studies',exact:true}).click();const input=page.getByRole('textbox',{name:'Search studies',exact:true});await input.fill('private candidate שלום');failure=true;await input.press('Enter');await expect(input).toHaveValue('');await expect(input).toBeDisabled();await input.evaluate(el=>{Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(el,'overwrite');el.dispatchEvent(new Event('input',{bubbles:true}));});failure=false;await page.getByRole('button',{name:'Retry search',exact:true}).click();await expect(input).toBeEnabled();await expect(input).toHaveValue('private candidate שלום');
});

test('library review: More completion leaves newly focused search input alone',async({page})=>{
 let release;await setup(page,{search:async(r,body)=>{if(body.cursor)await new Promise(resolve=>release=resolve);return r.fulfill({json:{items:[{...attribution,id:study,title:'Saved result',revision:'1'}],next_cursor:body.cursor?null:'next'}});}});await page.goto('/');await page.getByRole('button',{name:'Studies',exact:true}).click();await page.getByRole('button',{name:'Saved result',exact:true}).focus();await page.getByRole('button',{name:'More studies',exact:true}).click();await expect.poll(()=>!!release).toBe(true);const input=page.getByRole('textbox',{name:'Search studies',exact:true});await input.fill('candidate only');release();await expect(page.getByRole('button',{name:'More studies',exact:true})).toHaveCount(0);await expect(input).toBeFocused();
});

test('library review: delayed hidden refresh leaves Analysis focus and shared scroll untouched',async({page})=>{
 let release,reads=0;await setup(page,{search:async r=>{if(++reads===2)await new Promise(resolve=>release=resolve);return r.fulfill({json:{items:Array.from({length:30},(_,n)=>({...attribution,id:`30000000-0000-4000-8000-${String(n+10).padStart(12,'0')}`,title:`Scroll result ${n}`,revision:'1'})),next_cursor:null}});}});await page.goto('/');await page.getByRole('button',{name:'Studies',exact:true}).click();const result=page.getByRole('button',{name:'Scroll result 20',exact:true});await result.scrollIntoViewIfNeeded();await result.focus();await page.getByRole('button',{name:'Studies',exact:true}).click();await page.getByRole('button',{name:'Studies',exact:true}).click();await expect.poll(()=>!!release).toBe(true);await page.getByRole('button',{name:'Analysis',exact:true}).click();const surface=page.getByRole('complementary',{name:'Study tools',exact:true});await surface.evaluate(el=>{const spacer=document.createElement('div');spacer.style.height='3000px';el.appendChild(spacer);el.scrollTop=143;});await page.getByRole('tab',{name:'Notes',exact:true}).focus();await surface.evaluate(el=>el.scrollTop=143);release();await page.waitForTimeout(150);await expect(page.getByRole('tab',{name:'Notes',exact:true})).toBeFocused();expect(await surface.evaluate(el=>el.scrollTop)).toBe(143);
});

test('library review: input error association and query-free completed results announcement',async({page})=>{
 await setup(page,{search:async(r,body)=>r.fulfill(body.query==='invalid'?{status:400,json:{code:'scribeswell_personal_notes_input_invalid'}}:{json:{items:[{...attribution,id:study,title:'Saved result',revision:'1'}],next_cursor:null}})});await page.goto('/');await page.getByRole('button',{name:'Studies',exact:true}).click();const input=page.getByRole('textbox',{name:'Search studies',exact:true});await input.fill('invalid');await input.press('Enter');await expect(input).toHaveAttribute('aria-invalid','true');await expect(input).toHaveAttribute('aria-describedby',/study-search-error/);await expect(page.locator('#study-search-error')).toContainText('Enter a valid search');await input.fill('private query');await input.press('Enter');await expect(input).toHaveAttribute('aria-invalid','false');await expect(page.getByRole('status').filter({hasText:'1 study loaded.'})).toBeVisible();await expect(page.getByRole('status').filter({hasText:'private query'})).toHaveCount(0);
});

test('library review: stale old-token401 cannot remask restored same-account search',async({page})=>{
 let release;await setup(page,{search:async(r,body)=>{if(r.request().headers().authorization==='Bearer current'&&body.query){if(body.query==='old token request')await new Promise(resolve=>release=resolve);return r.fulfill({status:401,json:{code:'authentication_required'}});}return r.fulfill({json:{items:body.query?[{...attribution,id:study,title:'Fresh verified result',revision:'1'}]:[],next_cursor:null}});}});
 await page.goto('/');await page.getByRole('button',{name:'Studies',exact:true}).click();const input=page.getByRole('textbox',{name:'Search studies',exact:true});await input.fill('old token request');await input.press('Enter');await expect.poll(()=>!!release).toBe(true);await input.fill('retained candidate שלום');await input.press('Enter');await expect(input).toBeDisabled();await expect(input).toHaveValue('');
 await page.route('**/auth/v1/token*',r=>r.fulfill({json:{...session,access_token:'fresh-same-account'}}));await page.evaluate(async()=>{const {supabase}=await import('/src/lib/supabase.ts');await supabase.auth.signInWithPassword({email:'reader@example.invalid',password:'fixture'});});await page.getByRole('button',{name:'Retry search',exact:true}).click();await expect(page.getByRole('button',{name:'Fresh verified result',exact:true})).toBeVisible();await expect(input).toHaveValue('retained candidate שלום');const stale=page.waitForResponse(response=>new URL(response.url()).pathname.endsWith('/api/studies/search')&&response.request().postDataJSON()?.query==='old token request');release();await stale;await expect(input).toBeEnabled();await expect(input).toHaveValue('retained candidate שלום');await expect(page.getByRole('button',{name:'Fresh verified result',exact:true})).toBeVisible();await expect(page.getByRole('alert')).toHaveCount(0);
});

test('library review: queued layout-collapse scroll preserves saved return anchor',async({page})=>{
 let reads=0;await setup(page,{search:async(r,body)=>{reads++;const offset=body.cursor?20:0;const items=Array.from({length:20},(_,index)=>{const n=offset+index;return {...attribution,id:n===35?study:`30000000-0000-4000-8000-${String(n+10).padStart(12,'0')}`,title:`Result ${n}`,revision:'1'};});return r.fulfill({json:{items,next_cursor:body.cursor?null:'second'}});}});
 await page.goto('/');await page.getByRole('button',{name:'Studies',exact:true}).click();await page.getByRole('button',{name:'More studies',exact:true}).click();const result=page.getByRole('button',{name:'Result 35',exact:true});await result.scrollIntoViewIfNeeded();await result.focus();const before=await page.getByRole('complementary',{name:'Study tools',exact:true}).evaluate(el=>el.scrollTop);expect(before).toBeGreaterThan(0);await page.evaluate(()=>{const panel=document.querySelector('[aria-label="My studies"]');const observer=new MutationObserver(()=>{if(!panel.querySelector('h3'))return;observer.disconnect();const surface=document.querySelector('aside[aria-label="Study tools"]');window.__libraryCollapseScroll=surface.scrollTop;surface.dispatchEvent(new Event('scroll'));});observer.observe(panel,{childList:true,subtree:true});});await result.click();await page.getByRole('button',{name:'Leave study',exact:true}).click();
 await expect.poll(()=>page.evaluate(()=>window.__libraryCollapseScroll)).toBe(0);await expect.poll(()=>reads).toBe(4);await expect(result).toBeFocused();await expect.poll(()=>page.getByRole('complementary',{name:'Study tools',exact:true}).evaluate(el=>el.scrollTop)).toBeGreaterThan(before-50);
});

test('library review: winning pending selection preserves latest return focus',async({page})=>{
 const gates=[];const {otherStudy}=await reviewLibrary(page,{detail:(id,view)=>new Promise(resolve=>gates.push({id,release:()=>resolve(view(id))}))});await page.getByRole('button',{name:'Study A',exact:true}).click();await expect.poll(()=>gates.length).toBe(1);await page.getByRole('button',{name:'Study B',exact:true}).click();await expect.poll(()=>gates.length).toBe(2);gates.find(g=>g.id===otherStudy).release();await expect(page.getByRole('heading',{name:'Study B',exact:true})).toBeVisible();const stale=page.waitForResponse('**/api/studies/'+study);gates.find(g=>g.id===study).release();await stale;await page.getByRole('button',{name:'Leave study',exact:true}).click();await expect(page.getByRole('button',{name:'Study B',exact:true})).toBeFocused();
});

test('library review: superseded queued refresh frame cannot restore into a newer query',async({page})=>{
 let reads=0;await setup(page,{search:async(r,body)=>{reads++;return r.fulfill({json:{items:body.query?[{...attribution,id:study,title:'New query result',revision:'1'}]:Array.from({length:40},(_,n)=>({...attribution,id:n===35?study:`30000000-0000-4000-8000-${String(n+10).padStart(12,'0')}`,title:`Frame result ${n}`,revision:'1'})),next_cursor:null}});}});await page.goto('/');await page.getByRole('button',{name:'Studies',exact:true}).click();const result=page.getByRole('button',{name:'Frame result 35',exact:true});await result.scrollIntoViewIfNeeded();await result.focus();await page.getByRole('button',{name:'Studies',exact:true}).click();
 await page.evaluate(()=>{const raf=window.requestAnimationFrame.bind(window),cancel=window.cancelAnimationFrame.bind(window);let next=-1;window.__originalLibraryRaf=raf;window.__heldLibraryFrames=new Map();window.__holdLibraryFrames=true;window.requestAnimationFrame=callback=>{if(!window.__holdLibraryFrames)return raf(callback);const id=next--;window.__heldLibraryFrames.set(id,callback);return id;};window.cancelAnimationFrame=id=>{if(window.__heldLibraryFrames.has(id)){window.__heldLibraryFrames.delete(id);return;}cancel(id);};window.__releaseLibraryFrames=()=>{window.__holdLibraryFrames=false;const callbacks=[...window.__heldLibraryFrames.values()];window.__heldLibraryFrames.clear();callbacks.forEach(callback=>raf(callback));};});
 await page.getByRole('button',{name:'Studies',exact:true}).evaluate(el=>el.click());await expect.poll(()=>page.evaluate(()=>window.__heldLibraryFrames.size)).toBeGreaterThan(0);const input=page.getByRole('textbox',{name:'Search studies',exact:true});await input.fill('new private query');await input.press('Enter');await expect(page.getByRole('button',{name:'New query result',exact:true})).toBeVisible();await expect(input).toBeFocused();const surface=page.getByRole('complementary',{name:'Study tools',exact:true}),before=await surface.evaluate(el=>el.scrollTop);await page.evaluate(()=>{window.__releaseLibraryFrames();return new Promise(resolve=>window.__originalLibraryRaf(()=>window.__originalLibraryRaf(resolve)));});await expect(input).toBeFocused();expect(await surface.evaluate(el=>el.scrollTop)).toBe(before);expect(reads).toBe(3);
});

test('library review: newer search supersedes an unfinished result selection',async({page})=>{
 let release;await reviewLibrary(page,{detail:(id,view)=>new Promise(resolve=>release=()=>resolve(view(id)))});await page.getByRole('button',{name:'Study A',exact:true}).click();await expect.poll(()=>!!release).toBe(true);const input=page.getByRole('textbox',{name:'Search studies',exact:true});await input.fill('newer private query');await input.press('Enter');await expect(input).toHaveValue('newer private query');const stale=page.waitForResponse('**/api/studies/'+study);release();await stale;await expect(page.getByRole('heading',{name:'Study A',exact:true})).toHaveCount(0);await expect(input).toBeVisible();await expect(input).toHaveValue('newer private query');
});

test('note deletion requires safe-focused confirmation and cancel preserves dirty writing',async({page})=>{
 const {requests}=await setup(page);await firstNote(page);
 await page.getByLabel('Note text',{exact:true}).fill('private unsent writing');
 await page.getByRole('button',{name:'Delete note',exact:true}).click();
 const dialog=page.getByRole('dialog',{name:'Delete this note?'});
 await expect(dialog).toBeVisible();await expect(dialog).toContainText('permanently');await expect(dialog).toContainText('cannot be undone');await expect(dialog.getByRole('button',{name:'Cancel',exact:true})).toBeFocused();
 await dialog.getByRole('button',{name:'Cancel',exact:true}).click();
 await expect(page.getByLabel('Note text',{exact:true})).toContainText('private unsent writing');
 expect(requests.filter(r=>r.method==='DELETE')).toHaveLength(0);
});


test('confirmed dirty note deletion erases just the target without saving unsent writing',async({page})=>{
 const {requests}=await setup(page);await firstNote(page);
 await page.getByLabel('Note text',{exact:true}).fill('do not save merely to erase');
 await page.getByRole('button',{name:'Delete note',exact:true}).click();
 await page.getByRole('dialog').getByRole('button',{name:'Delete note',exact:true}).click();
 await expect(page.getByRole('dialog')).toHaveCount(0);await expect(page.getByLabel('Note text',{exact:true})).toHaveCount(0);await expect(page.getByText('Select a note in Studies.',{exact:true})).toBeFocused();
 expect(requests.filter(r=>r.method==='DELETE')).toHaveLength(1);expect(requests.filter(r=>r.method==='PUT'&&r.path.endsWith('/notes/'+note))).toHaveLength(0);
 await page.getByRole('button',{name:'Studies',exact:true}).click();await expect(page.getByRole('heading',{name:'Untitled study',exact:true})).toBeVisible();await expect(page.getByRole('list',{name:'Notes',exact:true}).getByRole('button')).toHaveCount(0);
});

test('unknown delete retains frozen writing and explicitly retries the original operation',async({page})=>{
 const options={dropDelete:true,unresolved:true};const {requests}=await setup(page,options);await firstNote(page);
 await page.getByLabel('Note text',{exact:true}).fill('retained until acknowledgement');await page.getByRole('button',{name:'Delete note',exact:true}).click();
 await page.getByRole('dialog').getByRole('button',{name:'Delete note',exact:true}).click();
 await expect(page.getByRole('dialog')).toContainText('Deletion not confirmed');await expect(page.getByLabel('Note text',{exact:true})).toContainText('retained until acknowledgement');
 await page.getByRole('dialog').getByRole('button',{name:'Close',exact:true}).click();
 await expect(page.getByLabel('Note text',{exact:true})).toHaveAttribute('contenteditable','false');
 await page.getByRole('button',{name:'Delete note',exact:true}).click();await page.getByRole('button',{name:'Retry deletion',exact:true}).click();await expect(page.getByRole('dialog')).toHaveCount(0);
 const deletes=requests.filter(r=>r.method==='DELETE');expect(deletes).toHaveLength(2);expect(deletes[1].payload).toEqual(deletes[0].payload);
});

test('deletion waits for executing save and uses its confirmed revision',async({page})=>{
 let release;const options={beforePut:()=>new Promise(resolve=>{release=resolve;})};const {requests}=await setup(page,options);await firstNote(page);
 await page.getByLabel('Note text',{exact:true}).fill('executing save');await expect.poll(()=>!!release).toBe(true);
 await page.getByRole('button',{name:'Delete note',exact:true}).click();await expect(page.getByRole('dialog').getByRole('button',{name:'Delete note',exact:true})).toBeDisabled();expect(requests.filter(r=>r.method==='DELETE')).toHaveLength(0);
 release();await expect(page.getByRole('dialog').getByRole('button',{name:'Delete note',exact:true})).toBeEnabled();await page.getByRole('dialog').getByRole('button',{name:'Delete note',exact:true}).click();await expect(page.getByRole('dialog')).toHaveCount(0);
 expect(requests.find(r=>r.method==='DELETE').payload.expected_revision).toBe('2');
});

test('delete conflict preserves writing and requires review and a fresh explicit confirmation',async({page})=>{
 const options={failDelete:409};const {requests,advanceNote}=await setup(page,options);await firstNote(page);await page.getByLabel('Note text',{exact:true}).fill('local work');
 await page.getByRole('button',{name:'Delete note',exact:true}).click();await page.getByRole('dialog').getByRole('button',{name:'Delete note',exact:true}).click();await expect(page.getByRole('dialog')).toContainText('Deletion not confirmed');await expect(page.getByLabel('Note text',{exact:true})).toContainText('local work');
 options.failDelete=0;advanceNote({document:{version:1,blocks:[]},connections:[],highlights:[]});await page.getByRole('button',{name:'Review current note',exact:true}).click();await expect(page.getByRole('dialog')).toContainText('Current note loaded');expect(requests.filter(r=>r.method==='DELETE')).toHaveLength(1);
 await page.getByRole('dialog').getByRole('button',{name:'Delete note',exact:true}).click();await expect(page.getByRole('dialog')).toHaveCount(0);
 const deletes=requests.filter(r=>r.method==='DELETE');expect(deletes[0].payload.operation_id).not.toBe(deletes[1].payload.operation_id);expect(deletes[1].payload.expected_revision).toBe('2');await expect(page.getByLabel('Note text',{exact:true})).toHaveCount(0);
});

test('unknown previous save must recover before separately confirmed deletion',async({page})=>{
 const options={dropPut:true,unresolved:true};const {requests}=await setup(page,options);await firstNote(page);await page.getByLabel('Note text',{exact:true}).fill('unknown previous save');await expect(page.getByRole('button',{name:'Retry',exact:true})).toBeVisible();
 await page.getByRole('button',{name:'Delete note',exact:true}).click();await expect(page.getByRole('dialog')).toContainText('Recover that save first');expect(requests.filter(r=>r.method==='DELETE')).toHaveLength(0);
 options.unresolved=false;await page.getByRole('button',{name:'Recover previous save',exact:true}).click();await expect(page.getByRole('dialog').getByRole('button',{name:'Delete note',exact:true})).toBeEnabled();expect(requests.filter(r=>r.method==='DELETE')).toHaveLength(0);
 await page.getByRole('dialog').getByRole('button',{name:'Delete note',exact:true}).click();await expect(page.getByRole('dialog')).toHaveCount(0);
 const saves=requests.filter(r=>r.method==='PUT'&&r.path.endsWith('/notes/'+note));expect(saves).toHaveLength(2);expect(saves[0].payload).toEqual(saves[1].payload);
});

for(const late of ['success','denial'])test('note deletion account replacement rejects late '+late,async({page})=>{
 let release;const options={beforeDelete:()=>new Promise(resolve=>release=resolve),failDelete:late==='denial'?403:0};const {requests}=await setup(page,options);await firstNote(page);await page.getByLabel('Note text',{exact:true}).fill('old account private writing');
 await page.getByRole('button',{name:'Delete note',exact:true}).click();await page.getByRole('dialog').getByRole('button',{name:'Delete note',exact:true}).click();await expect.poll(()=>!!release).toBe(true);
 await page.route('**/auth/v1/token*',r=>r.fulfill({json:{...session,access_token:'other-account',user:{...session.user,id:'10000000-0000-4000-8000-000000000002'}}}));
 await page.evaluate(async()=>{const {supabase}=await import('/src/lib/supabase.ts');await supabase.auth.signInWithPassword({email:'other@example.invalid',password:'fixture'});});
 await expect(page.getByRole('dialog')).toHaveCount(0);await expect(page.getByLabel('Note text',{exact:true})).toHaveCount(0);const currentControl=page.getByRole('button',{name:'Studies',exact:true});await currentControl.focus();const lateReply=page.waitForResponse(r=>r.request().method()==='DELETE');release();await (await lateReply).finished();await page.evaluate(()=>new Promise(requestAnimationFrame));await expect(currentControl).toBeFocused();await expect(page.getByText('old account private writing')).toHaveCount(0);await expect(page.getByText('Studies access is unavailable for this account.')).toHaveCount(0);expect(requests.filter(r=>r.method==='DELETE')).toHaveLength(1);
});

test('note deletion navigation preserves an unknown operation and suppresses fresh saves',async({page})=>{
 const options={dropDelete:true,unresolved:true};const {requests}=await setup(page,options);await firstNote(page);
 await page.getByLabel('Note text',{exact:true}).fill('original private unsent writing');await page.getByRole('button',{name:'Delete note',exact:true}).click();await page.getByRole('dialog').getByRole('button',{name:'Delete note',exact:true}).click();await expect(page.getByRole('dialog')).toContainText('Deletion not confirmed');await page.getByRole('dialog').getByRole('button',{name:'Close',exact:true}).click();
 await page.getByRole('button',{name:'Back to Studies',exact:true}).click();await page.getByRole('button',{name:'Leave study',exact:true}).click();await page.getByRole('button',{name:'Untitled study',exact:true}).click();
 // The fixture has committed the tombstone and omits it from lists; the retained
 // target is still recoverable by returning to the current Analysis lane.
 await page.getByRole('button',{name:'Analysis',exact:true}).click();
 // Navigation clears selection, so reopen recovery through an explicit retained action.
 await expect(page.getByRole('button',{name:/^Recover deletion:/})).toBeVisible();await page.getByRole('button',{name:/^Recover deletion:/}).click();
 await page.getByRole('button',{name:'Retry deletion',exact:true}).click();await expect(page.getByRole('dialog')).toHaveCount(0);
 const deletes=requests.filter(r=>r.method==='DELETE');expect(deletes).toHaveLength(2);expect(deletes[0].payload).toEqual(deletes[1].payload);expect(requests.filter(r=>r.method==='PUT'&&r.path.endsWith('/notes/'+note))).toHaveLength(0);
});

test('note deletion captured target does not evict a different selected note after navigation',async({page})=>{
 let release;const {requests}=await setup(page,{beforeDelete:()=>new Promise(resolve=>release=resolve)});await firstNote(page);
 const other='40000000-0000-4000-8000-000000000002',otherValue={document:{version:1,blocks:[{type:'paragraph',direction:'auto',content:[{type:'text',text:'Other note survives',marks:[]}]}]},connections:[],highlights:[]};
 await page.route('**/api/studies/'+study+'/notes',r=>r.request().method()==='GET'?r.fulfill({json:{items:[{...attribution,id:other,study_id:study,visibility:'study',revision:'1',value:otherValue}],next_cursor:null}}):r.fallback());
 await page.route('**/api/studies/'+study+'/notes/'+other,r=>r.fulfill({json:{...attribution,id:other,study_id:study,visibility:'study',revision:'1',value:otherValue}}));
 await page.getByRole('button',{name:'Delete note',exact:true}).click();await page.getByRole('dialog').getByRole('button',{name:'Delete note',exact:true}).click();await expect.poll(()=>!!release).toBe(true);await page.getByRole('dialog').getByRole('button',{name:'Close',exact:true}).click();
 await page.getByRole('button',{name:'Back to Studies',exact:true}).click();await page.getByRole('button',{name:'Leave study',exact:true}).click();await page.getByRole('button',{name:'Untitled study',exact:true}).click();await page.getByRole('button',{name:'Other note survives',exact:true}).click();
 await page.getByLabel('Note text',{exact:true}).focus();const lateReply=page.waitForResponse(r=>r.request().method()==='DELETE');release();await (await lateReply).finished();await page.evaluate(()=>new Promise(requestAnimationFrame));await expect(page.getByLabel('Note text',{exact:true})).toContainText('Other note survives');await expect(page.getByLabel('Note text',{exact:true})).toBeFocused();expect(requests.find(r=>r.method==='DELETE').path).toBe('/api/studies/'+study+'/notes/'+note);
});

test('note deletion after a definitive prior-save conflict reviews current revision and clears only failed save identity',async({page})=>{
 const options={failPut:409};const {requests,advanceNote}=await setup(page,options);await firstNote(page);await page.getByLabel('Note text',{exact:true}).fill('my conflicting save');await expect(page.getByRole('alert')).toContainText('This note has changed');
 await page.getByRole('button',{name:'Delete note',exact:true}).click();await expect(page.getByRole('dialog')).toContainText('Review the current note');advanceNote({document:{version:1,blocks:[]},connections:[],highlights:[]});await page.getByRole('button',{name:'Review current note',exact:true}).click();await expect(page.getByRole('dialog')).toContainText('Current note loaded');await expect(page.getByLabel('Note text',{exact:true})).toContainText('my conflicting save');
 await page.getByRole('dialog').getByRole('button',{name:'Delete note',exact:true}).click();await expect(page.getByRole('dialog')).toHaveCount(0);expect(requests.filter(r=>r.method==='DELETE')).toHaveLength(1);expect(requests.find(r=>r.method==='DELETE').payload.expected_revision).toBe('2');await expect(page.getByLabel('Note text',{exact:true})).toHaveCount(0);expect(requests.filter(r=>r.method==='PUT'&&r.path.endsWith('/notes/'+note))).toHaveLength(1);
});

test('note deletion composing cancel preserves final composition through saving and reopen',async({page})=>{
 const {requests}=await setup(page);await firstNote(page);const editor=page.getByLabel('Note text',{exact:true});await editor.dispatchEvent('compositionstart');await editor.fill('initial composing text');await page.getByRole('button',{name:'Delete note',exact:true}).click();
 await editor.evaluate(el=>{el.textContent='final composed שָׁלוֹם';el.dispatchEvent(new CompositionEvent('compositionend',{bubbles:true}));});
 await page.getByRole('dialog').getByRole('button',{name:'Cancel',exact:true}).click();await expect(editor).toContainText('final composed שָׁלוֹם');await expect(page.getByRole('status').filter({hasText:'Draft saved'})).toBeVisible();
 expect(JSON.stringify(requests.filter(r=>r.method==='PUT').at(-1).payload.value)).toContain('final composed שָׁלוֹם');
 await page.reload();await page.getByRole('button',{name:'Studies',exact:true}).click();await page.getByRole('button',{name:'Untitled study',exact:true}).click();await page.getByRole('button',{name:'final composed שָׁלוֹם',exact:true}).click();await expect(editor).toContainText('final composed שָׁלוֹם');expect(requests.filter(r=>r.method==='DELETE')).toHaveLength(0);
});

test('note deletion bounded preparation keeps unresolved save and requires original recovery',async({page})=>{
 let release;const {requests}=await setup(page,{beforePut:()=>new Promise(resolve=>release=resolve)});await firstNote(page);await page.getByLabel('Note text',{exact:true}).fill('still saving');await expect.poll(()=>!!release).toBe(true);
 await page.getByRole('button',{name:'Delete note',exact:true}).click();await expect(page.getByRole('button',{name:'Recover previous save',exact:true})).toBeVisible({timeout:6500});expect(requests.filter(r=>r.method==='DELETE')).toHaveLength(0);
 release();await page.getByRole('button',{name:'Recover previous save',exact:true}).click();await expect(page.getByRole('dialog').getByRole('button',{name:'Delete note',exact:true})).toBeEnabled();expect(requests.filter(r=>r.method==='DELETE')).toHaveLength(0);expect(requests.filter(r=>r.method==='PUT'&&r.path.endsWith('/notes/'+note))).toHaveLength(1);
 await page.getByRole('dialog').getByRole('button',{name:'Cancel',exact:true}).click();await expect(page.getByLabel('Note text',{exact:true})).toContainText('still saving');
});

test('note deletion filters a stale notes page arriving after committed acknowledgement',async({page})=>{
 let releaseDelete,releasePage;await setup(page,{beforeDelete:()=>new Promise(resolve=>releaseDelete=resolve)});await firstNote(page);
 await page.route('**/api/studies/'+study+'/notes',async r=>{if(r.request().method()!=='GET')return r.fallback();const stale={items:[{...attribution,id:note,study_id:study,visibility:'study',revision:'1',value:{document:{version:1,blocks:[]},connections:[],highlights:[]}}],next_cursor:null};await new Promise(resolve=>releasePage=resolve);return r.fulfill({json:stale});});
 await page.getByRole('button',{name:'Delete note',exact:true}).click();await page.getByRole('dialog').getByRole('button',{name:'Delete note',exact:true}).click();await expect.poll(()=>!!releaseDelete).toBe(true);await page.getByRole('dialog').getByRole('button',{name:'Close',exact:true}).click();
 await page.getByRole('button',{name:'Back to Studies',exact:true}).click();await page.getByRole('button',{name:'Leave study',exact:true}).click();await page.getByRole('button',{name:'Untitled study',exact:true}).click();await expect.poll(()=>!!releasePage).toBe(true);
 const committed=page.waitForResponse(r=>r.request().method()==='DELETE');releaseDelete();await committed;releasePage();await expect(page.getByRole('heading',{name:'Untitled study',exact:true})).toBeVisible();await expect(page.getByRole('list',{name:'Notes',exact:true})).toBeAttached();await expect(page.getByRole('list',{name:'Notes',exact:true}).getByRole('button')).toHaveCount(0);
});

test('note deletion lost reply resolves through read-only original outcome lookup',async({page})=>{
 const {requests}=await setup(page,{dropDelete:true});await firstNote(page);await page.getByRole('button',{name:'Delete note',exact:true}).click();await page.getByRole('dialog').getByRole('button',{name:'Delete note',exact:true}).click();await expect(page.getByRole('dialog')).toHaveCount(0);await expect(page.getByLabel('Note text',{exact:true})).toHaveCount(0);expect(requests.filter(r=>r.method==='DELETE')).toHaveLength(1);
});

test('note deletion same-account authority recovery never automatically repeats deletion',async({page})=>{
 const options={failDelete:401};const {requests}=await setup(page,options);await firstNote(page);await page.getByLabel('Note text',{exact:true}).fill('recoverable private input');await page.getByRole('button',{name:'Delete note',exact:true}).click();await page.getByRole('dialog').getByRole('button',{name:'Delete note',exact:true}).click();await expect(page.getByRole('dialog')).toHaveCount(0);await expect(page.getByLabel('Note text',{exact:true})).toHaveCount(0);
 options.failDelete=0;await page.getByRole('button',{name:'Retry Studies',exact:true}).click();await expect(page.getByRole('button',{name:/^Recover deletion:/})).toBeVisible();expect(requests.filter(r=>r.method==='DELETE')).toHaveLength(1);
 await page.getByRole('button',{name:/^Recover deletion:/}).click();await page.getByRole('button',{name:'Retry deletion',exact:true}).click();await expect(page.getByRole('dialog')).toHaveCount(0);const deletes=requests.filter(r=>r.method==='DELETE');expect(deletes).toHaveLength(2);expect(deletes[0].payload).toEqual(deletes[1].payload);
});

for(const origin of ['save','delete'])test('note deletion review Cancel does not authorize stale autosave after '+origin+' conflict',async({page})=>{
 const options=origin==='save'?{failPut:409}:{failDelete:409};const {requests}=await setup(page,options);await firstNote(page);await page.getByLabel('Note text',{exact:true}).fill('my retained stale writing');if(origin==='save')await expect(page.getByRole('alert')).toContainText('This note has changed');
 await page.getByRole('button',{name:'Delete note',exact:true}).click();if(origin==='delete')await page.getByRole('dialog').getByRole('button',{name:'Delete note',exact:true}).click();
 const remote={document:{version:1,blocks:[{type:'paragraph',direction:'auto',content:[{type:'text',text:'Concurrent saved writing',marks:[]}]}]},connections:[],highlights:[]};
 await page.route('**/api/studies/'+study+'/notes/'+note,r=>r.request().method()==='GET'?r.fulfill({json:{...attribution,id:note,study_id:study,visibility:'study',revision:'2',value:remote}}):r.fallback());
 await page.getByRole('button',{name:'Review current note',exact:true}).click();await expect(page.getByRole('region',{name:'Current saved note',exact:true})).toContainText('Concurrent saved writing');const prior=requests.filter(r=>r.method==='PUT'&&r.path.endsWith('/notes/'+note)).length;
 await page.getByRole('dialog').getByRole('button',{name:'Cancel',exact:true}).click();await expect(page.getByLabel('Note text',{exact:true})).toContainText('my retained stale writing');await page.waitForTimeout(800);expect(requests.filter(r=>r.method==='PUT'&&r.path.endsWith('/notes/'+note))).toHaveLength(prior);
});

test('deletion review excludes overlapping same-target requests and keeps one confirmed revision',async({page})=>{
 const options={failDelete:409};const {requests,advanceNote}=await setup(page,options);await firstNote(page);await page.getByRole('button',{name:'Delete note',exact:true}).click();await page.getByRole('dialog').getByRole('button',{name:'Delete note',exact:true}).click();
 let release,reads=0;const remote={document:{version:1,blocks:[{type:'paragraph',direction:'auto',content:[{type:'text',text:'Reviewed saved writing',marks:[]}]}]},connections:[],highlights:[]};advanceNote(remote);
 await page.route('**/api/studies/'+study+'/notes/'+note,async r=>{if(r.request().method()!=='GET')return r.fallback();reads++;if(reads===1)await new Promise(resolve=>release=resolve);return r.fulfill({json:{...attribution,id:note,study_id:study,visibility:'study',revision:reads===1?'2':'3',value:remote}});});
 await page.getByRole('button',{name:'Review current note',exact:true}).evaluate(button=>{button.click();button.click();});await expect.poll(()=>!!release).toBe(true);await page.waitForTimeout(100);expect(reads).toBe(1);await expect(page.getByRole('button',{name:'Review current note',exact:true})).toBeDisabled();
 release();await expect(page.getByRole('region',{name:'Current saved note',exact:true})).toContainText('Reviewed saved writing');options.failDelete=0;await page.getByRole('dialog').getByRole('button',{name:'Delete note',exact:true}).click();await expect(page.getByRole('dialog')).toHaveCount(0);expect(requests.filter(r=>r.method==='DELETE').at(-1).payload.expected_revision).toBe('2');
});

test('deletion review shows list semantics formatting external destinations and canonical passage targets',async({page})=>{
 const options={failDelete:409};await setup(page,options);await firstNote(page);await page.getByRole('button',{name:'Delete note',exact:true}).click();await page.getByRole('dialog').getByRole('button',{name:'Delete note',exact:true}).click();
 const passage=await page.evaluate(async()=>{const {parseReference}=await import('/src/lib/passage-references.ts');return parseReference('Genesis 2:1');});
 const remote={document:{version:2,blocks:[{type:'list',style:'ordered',items:[[{type:'paragraph',direction:'rtl',content:[{type:'text',text:'First item',marks:['bold']},{type:'external_link',url:'https://example.org/new-destination',content:[{type:'text',text:'Same link label',marks:['italic']}]}]}],[{type:'paragraph',direction:'auto',content:[{type:'passage_link',label:'Same passage label',reference:passage}]}]]},{type:'list',style:'bullet',items:[[{type:'paragraph',direction:'auto',content:[{type:'text',text:'Bullet item',marks:[]}]}]]}]},connections:[],highlights:[]};
 await page.route('**/api/studies/'+study+'/notes/'+note,r=>r.request().method()==='GET'?r.fulfill({json:{...attribution,id:note,study_id:study,visibility:'study',revision:'2',value:remote}}):r.fallback());
 await page.getByRole('button',{name:'Review current note',exact:true}).click();const review=page.getByRole('region',{name:'Current saved note',exact:true});await expect(review.locator('ol>li')).toHaveCount(2);await expect(review.locator('ul>li')).toHaveCount(1);await expect(review.locator('p[dir="rtl"] strong')).toHaveText('First item');await expect(review.locator('em')).toHaveText('Same link label');await expect(review).toContainText('https://example.org/new-destination');await expect(review).toContainText('Same passage label');await expect(review).toContainText('Genesis 2:1');expect(await review.locator('a').count()).toBe(0);
});

test('deletion recovery labels distinguish two retained targets and recover their own operations',async({page})=>{
 const options={failDelete:503};const {requests}=await setup(page,options);await firstNote(page);await page.getByLabel('Note text',{exact:true}).fill('First target');await page.getByRole('button',{name:'Delete note',exact:true}).click();await page.getByRole('dialog').getByRole('button',{name:'Delete note',exact:true}).click();await expect(page.getByRole('dialog')).toContainText('Deletion not confirmed');await page.getByRole('dialog').getByRole('button',{name:'Close',exact:true}).click();await page.getByRole('button',{name:'Back to Studies',exact:true}).click();
 const other='40000000-0000-4000-8000-000000000002',secondValue={document:{version:1,blocks:[{type:'paragraph',direction:'auto',content:[{type:'text',text:'Second target',marks:[]}]}]},connections:[],highlights:[]};let recover=false;const secondDeletes=[];
 await page.route('**/api/studies/'+study+'/notes',r=>r.request().method()==='POST'?r.fulfill({json:{operation_id:r.request().postDataJSON().operation_id,command:'note.create',study_id:study,note_id:other,revision:'1'}}):r.fallback());
 await page.route('**/api/studies/'+study+'/notes/'+other,r=>{if(r.request().method()==='DELETE'){const payload=r.request().postDataJSON();secondDeletes.push(payload);return recover?r.fulfill({json:{operation_id:payload.operation_id,command:'note.delete',study_id:study,note_id:other,revision:'2'}}):r.fulfill({status:503,json:{code:'studies_storage_unavailable'}});}return r.fulfill({json:{...attribution,id:other,study_id:study,visibility:'study',revision:'1',value:secondValue}});});
 await page.getByRole('button',{name:'Add note',exact:true}).click();await page.getByRole('button',{name:'Delete note',exact:true}).click();await page.getByRole('dialog').getByRole('button',{name:'Delete note',exact:true}).click();await expect(page.getByRole('dialog')).toContainText('Deletion not confirmed');await page.getByRole('dialog').getByRole('button',{name:'Close',exact:true}).click();
 const first=page.getByRole('button',{name:/^Recover deletion:.*First target/}),second=page.getByRole('button',{name:/^Recover deletion:.*Second target/});await expect(first).toBeVisible();await expect(second).toBeVisible();expect(await first.textContent()).not.toBe(await second.textContent());
 recover=true;await second.click();await expect(page.getByRole('dialog')).toContainText('Second target');await page.getByRole('button',{name:'Retry deletion',exact:true}).click();await expect(page.getByRole('dialog')).toHaveCount(0);await expect(first).toBeVisible();options.failDelete=0;await first.click();await expect(page.getByRole('dialog')).toContainText('First target');await page.getByRole('button',{name:'Retry deletion',exact:true}).click();await expect(page.getByRole('dialog')).toHaveCount(0);
 const firstDeletes=requests.filter(r=>r.method==='DELETE');expect(firstDeletes).toHaveLength(2);expect(firstDeletes[0].payload).toEqual(firstDeletes[1].payload);expect(secondDeletes).toHaveLength(2);expect(secondDeletes[0]).toEqual(secondDeletes[1]);expect(secondDeletes[0].operation_id).not.toBe(firstDeletes[0].payload.operation_id);
});

test('deletion selected target acknowledgement focuses visible fallback when editor is hidden',async({page})=>{
 let release;await setup(page,{beforeDelete:()=>new Promise(resolve=>release=resolve)});await firstNote(page);await page.getByRole('button',{name:'Delete note',exact:true}).click();await page.getByRole('dialog').getByRole('button',{name:'Delete note',exact:true}).click();await expect.poll(()=>!!release).toBe(true);await page.getByRole('dialog').getByRole('button',{name:'Close',exact:true}).click();await page.getByRole('button',{name:'Back to Studies',exact:true}).click();
 const lateReply=page.waitForResponse(r=>r.request().method()==='DELETE');release();await (await lateReply).finished();await expect(page.getByText('Note deleted.',{exact:true})).toBeVisible();await expect(page.getByText('Note deleted.',{exact:true})).toBeFocused();await expect(page.getByRole('button',{name:'Add note',exact:true})).toBeVisible();
});

test('deletion review wraps the full long valid destination within desktop and mobile dialog width',async({page})=>{
 await setup(page,{failDelete:409});await firstNote(page);await page.getByRole('button',{name:'Delete note',exact:true}).click();await page.getByRole('dialog').getByRole('button',{name:'Delete note',exact:true}).click();
 const url='https://example.org/new-destination?query='+'a'.repeat(1900),remote={document:{version:1,blocks:[{type:'paragraph',direction:'auto',content:[{type:'external_link',url,content:[{type:'text',text:'Saved destination',marks:[]}]}]}]},connections:[],highlights:[]};
 await page.route('**/api/studies/'+study+'/notes/'+note,r=>r.request().method()==='GET'?r.fulfill({json:{...attribution,id:note,study_id:study,visibility:'study',revision:'2',value:remote}}):r.fallback());await page.getByRole('button',{name:'Review current note',exact:true}).click();const review=page.getByRole('region',{name:'Current saved note',exact:true});await expect(review).toContainText(url);
 const widths=await page.getByRole('dialog').evaluate(dialog=>{const content=dialog.querySelector('[aria-label="Current saved note"]');return {dialog:dialog.scrollWidth<=dialog.clientWidth,review:content.scrollWidth<=content.clientWidth,viewport:dialog.getBoundingClientRect().left>=0&&dialog.getBoundingClientRect().right<=innerWidth};});expect(widths).toEqual({dialog:true,review:true,viewport:true});
});

for(const destination of ['reader after tools close','surviving public control'])test('deletion acknowledgement preserves deliberate focus on '+destination,async({page})=>{
 let release;await setup(page,{beforeDelete:()=>new Promise(resolve=>release=resolve)});await firstNote(page);await page.getByRole('button',{name:'Delete note',exact:true}).click();await page.getByRole('dialog').getByRole('button',{name:'Delete note',exact:true}).click();await expect.poll(()=>!!release).toBe(true);await page.getByRole('dialog').getByRole('button',{name:'Close',exact:true}).click();
 const mobile=test.info().project.name==='mobile';
 if(destination==='reader after tools close')await page.getByRole('button',{name:mobile?'Return to reader':'Analysis',exact:true}).click();
 const control=destination==='surviving public control'&&mobile?page.getByRole('button',{name:'Add reader pane',exact:true}):page.getByRole('button',{name:/^Navigate: Genesis, chapter 1/});await expect(control).toBeVisible();await control.focus();await expect(control).toBeFocused();
 const acknowledgement=page.waitForResponse(r=>r.request().method()==='DELETE');release();await (await acknowledgement).finished();await expect(page.getByLabel('Note text',{exact:true})).toHaveCount(0);await page.evaluate(()=>new Promise(requestAnimationFrame));await expect(control).toBeFocused();await expect(page.getByText('Note deleted.',{exact:true})).toHaveCount(0);
});

test('whole-study deletion confirms captured owned scope and Cancel preserves unsent writing',async({page})=>{
 const {requests}=await setup(page);await firstNote(page);const editor=page.getByLabel('Note text',{exact:true});await editor.fill('Unsent study writing');const dialog=await openWholeDeletion(page);await expect(dialog.getByRole('button',{name:'Cancel',exact:true})).toBeFocused();await page.waitForTimeout(650);expect(requests.filter(r=>r.method==='PUT')).toHaveLength(0);await dialog.getByRole('button',{name:'Cancel',exact:true}).click();await expect(editor).toContainText('Unsent study writing');await expect.poll(()=>requests.filter(r=>r.method==='PUT').length).toBe(1);expect(requests.find(r=>r.method==='PUT').payload.value.document.blocks[0].content[0].text).toBe('Unsent study writing');expect(requests.filter(r=>r.method==='DELETE')).toHaveLength(0);
});

async function openWholeDeletion(page){await page.getByRole('button',{name:'Delete study',exact:true}).filter({visible:true}).click();return page.getByRole('dialog',{name:'Delete this study?',exact:true});}
async function confirmWholeDeletion(page){const dialog=await openWholeDeletion(page);await expect(dialog.getByRole('button',{name:'Delete study',exact:true})).toBeEnabled();await dialog.getByRole('button',{name:'Delete study',exact:true}).click();return dialog;}
async function firstNoteWithPausedClock(page){
 await page.clock.install();await firstNote(page);
 // Pause before editing: automation/render latency must not consume the
 // coordinator's budget. runFor exercises the application's real timer callbacks.
 await page.clock.pauseAt(await page.evaluate(()=>Date.now()+1000));
}


test('whole-study deletion discards dirty writing only after acknowledgement without save',async({page})=>{
 let release;const {requests}=await setup(page,{beforeStudyDelete:()=>new Promise(resolve=>release=resolve)});await firstNote(page);const editor=page.getByLabel('Note text',{exact:true});await editor.fill('Unsent private text');const dialog=await confirmWholeDeletion(page);await expect.poll(()=>!!release).toBe(true);expect(requests.filter(r=>r.method==='PUT')).toHaveLength(0);await expect(editor).toContainText('Unsent private text');release();await expect(dialog).toHaveCount(0);await expect(editor).toHaveCount(0);await expect(page.getByText('Study deleted.',{exact:true})).toBeFocused();expect(requests.filter(r=>r.method==='DELETE')).toHaveLength(1);
});

test('whole-study deletion composing Cancel preserves final IME and resumes original save policy',async({page})=>{
 const {requests}=await setup(page);await firstNote(page);const editor=page.getByLabel('Note text',{exact:true});await editor.dispatchEvent('compositionstart');await editor.fill('initial');const dialog=await openWholeDeletion(page);await editor.evaluate(node=>{node.textContent='Final עברית';node.dispatchEvent(new InputEvent('input',{bubbles:true,inputType:'insertCompositionText'}));node.dispatchEvent(new CompositionEvent('compositionend',{bubbles:true,data:'Final עברית'}));});await page.waitForTimeout(650);expect(requests.filter(r=>r.method==='PUT')).toHaveLength(0);await dialog.getByRole('button',{name:'Cancel',exact:true}).click();await expect(editor).toContainText('Final עברית');await expect.poll(()=>requests.filter(r=>r.method==='PUT').length).toBe(1);expect(requests.find(r=>r.method==='PUT').payload.value.document.blocks[0].content[0].text).toBe('Final עברית');
});

for(const lost of [false,true])test('whole-study deletion '+(lost?'lost reply resolves original receipt':'unknown retry retains original payload across navigation'),async({page})=>{
 const options=lost?{dropStudyDelete:true}:{failStudyDelete:503};const {requests}=await setup(page,options);await firstNote(page);const dialog=await confirmWholeDeletion(page);
 if(lost){await expect(dialog).toHaveCount(0);expect(requests.filter(r=>r.method==='DELETE')).toHaveLength(1);return;}
 await expect(dialog).toContainText('Deletion not confirmed');const first=requests.find(r=>r.method==='DELETE').payload;await dialog.getByRole('button',{name:'Close',exact:true}).click();await page.getByRole('button',{name:'Back to Studies',exact:true}).click();await page.getByRole('button',{name:'Leave study',exact:true}).click();await expect(page.getByRole('button',{name:/Recover study deletion:/})).toBeVisible();options.failStudyDelete=0;await page.getByRole('button',{name:/Recover study deletion:/}).click();await dialog.getByRole('button',{name:'Retry study deletion',exact:true}).click();await expect(dialog).toHaveCount(0);const attempts=requests.filter(r=>r.method==='DELETE');expect(attempts).toHaveLength(2);expect(attempts[1].payload).toEqual(first);
});

test('whole-study deletion current metadata conflict requires review and fresh explicit confirmation',async({page})=>{
 const {requests,metadata}=await setup(page);await firstNote(page);await page.getByLabel('Note text',{exact:true}).fill('Local writing stays');const dialog=await openWholeDeletion(page);await expect(dialog.getByRole('button',{name:'Delete study',exact:true})).toBeEnabled();metadata.revision='2';metadata.title='Remote current title';await dialog.getByRole('button',{name:'Delete study',exact:true}).click();await expect(dialog).toContainText('Review the current study');await dialog.getByRole('button',{name:'Review current study',exact:true}).click();await expect(dialog).toContainText('Current saved title: Remote current title');expect(requests.filter(r=>r.method==='DELETE')).toHaveLength(1);await expect(page.getByLabel('Note text',{exact:true})).toContainText('Local writing stays');await dialog.getByRole('button',{name:'Delete study',exact:true}).click();await expect(dialog).toHaveCount(0);const deletes=requests.filter(r=>r.method==='DELETE');expect(deletes[1].payload.expected_revision).toBe('2');expect(deletes[1].payload.operation_id).not.toBe(deletes[0].payload.operation_id);
});

for(const lane of ['save','title','collection','child deletion','creation'])test('whole-study deletion prepares executing '+lane+' before separate confirmation',async({page})=>{
 let release,armed=true;const wait=()=>armed?new Promise(resolve=>release=resolve):undefined;
 const options=lane==='save'?{beforePut:wait}:lane==='title'?{beforeRename:wait}:lane==='collection'?{beforePassagePut:wait}:lane==='child deletion'?{beforeDelete:wait}:{};
 const {requests}=await setup(page,options);await firstNote(page);
 if(lane==='save')await page.getByLabel('Note text',{exact:true}).fill('Executing save');
 else if(lane==='child deletion'){await page.getByRole('button',{name:'Delete note',exact:true}).click();await page.getByRole('dialog').getByRole('button',{name:'Delete note',exact:true}).click();await expect.poll(()=>!!release).toBe(true);await page.getByRole('dialog').getByRole('button',{name:'Close',exact:true}).click();}
 else {await page.getByRole('button',{name:'Back to Studies',exact:true}).click();
  if(lane==='title'){await page.getByRole('button',{name:'Rename',exact:true}).click();await page.getByLabel('Title',{exact:true}).fill('Executing title');await page.getByRole('button',{name:'Save',exact:true}).click();}
  if(lane==='collection')await addReference(page,'Gen1');
  if(lane==='creation'){await page.route('**/api/studies/'+study+'/notes',async r=>{if(r.request().method()==='POST'){await wait();return r.fulfill({json:{operation_id:r.request().postDataJSON().operation_id,command:'note.create',study_id:study,note_id:note,revision:'1'}});}return r.fallback();});await page.getByRole('button',{name:'Add note',exact:true}).click();}
 }
 await expect.poll(()=>!!release).toBe(true);const dialog=await openWholeDeletion(page);await expect(dialog.getByRole('button',{name:'Delete study',exact:true})).toBeDisabled();expect(requests.filter(r=>r.method==='DELETE'&&r.path==='/api/studies/'+study)).toHaveLength(0);armed=false;release();await expect(dialog.getByRole('button',{name:'Delete study',exact:true})).toBeEnabled();expect(requests.filter(r=>r.method==='DELETE'&&r.path==='/api/studies/'+study)).toHaveLength(0);await dialog.getByRole('button',{name:'Delete study',exact:true}).click();await expect(dialog).toHaveCount(0);
});

test('whole-study deletion bounds preparation and requires original save recovery first',async({page})=>{
 const options={failPut:503};const {requests}=await setup(page,options);await firstNote(page);await page.getByLabel('Note text',{exact:true}).fill('Keep until confirmed');await expect(page.getByRole('status').filter({hasText:'Changes not saved'})).toBeVisible();const original=requests.find(r=>r.method==='PUT').payload;const dialog=await openWholeDeletion(page);await expect(dialog.getByRole('button',{name:'Recover previous operations',exact:true})).toBeVisible();expect(requests.filter(r=>r.method==='DELETE')).toHaveLength(0);options.failPut=0;await dialog.getByRole('button',{name:'Recover previous operations',exact:true}).click();await expect(dialog.getByRole('button',{name:'Delete study',exact:true})).toBeEnabled();expect(requests.filter(r=>r.method==='PUT')[1].payload).toEqual(original);expect(requests.filter(r=>r.method==='DELETE')).toHaveLength(0);await dialog.getByRole('button',{name:'Delete study',exact:true}).click();await expect(dialog).toHaveCount(0);
});

test('whole-study deletion executing and unknown freeze visible editing and formatting after Close',async({page})=>{
 let release;const options={beforeStudyDelete:()=>new Promise(resolve=>release=resolve),failStudyDelete:503};await setup(page,options);await firstNote(page);const dialog=await confirmWholeDeletion(page);await expect.poll(()=>!!release).toBe(true);await dialog.getByRole('button',{name:'Close',exact:true}).click();const editor=page.getByLabel('Note text',{exact:true});await expect(editor).toHaveAttribute('contenteditable','false');await expect(page.getByRole('button',{name:'Bold',exact:true})).toBeDisabled();release();await expect(page.getByRole('button',{name:/Recover study deletion:/})).toBeVisible();await expect(editor).toHaveAttribute('contenteditable','false');
});

test('whole-study deletion definitive original save conflict leaves recovery and needs new explicit confirmation',async({page})=>{
 const options={failPut:503};const {requests}=await setup(page,options);await firstNote(page);await page.getByLabel('Note text',{exact:true}).fill('Retained conflict input');await expect(page.getByRole('status').filter({hasText:'Changes not saved'})).toBeVisible();const dialog=await openWholeDeletion(page);options.failPut=409;await dialog.getByRole('button',{name:'Recover previous operations',exact:true}).click();await expect(dialog.getByRole('button',{name:'Delete study',exact:true})).toBeEnabled();expect(requests.filter(r=>r.method==='DELETE')).toHaveLength(0);await dialog.getByRole('button',{name:'Cancel',exact:true}).click();await expect(page.getByLabel('Note text',{exact:true})).toContainText('Retained conflict input');expect(requests.filter(r=>r.method==='PUT')).toHaveLength(2);
});

test('whole-study deletion preparation has one five-second total wait for an executing save',async({page})=>{
 let release;const {requests}=await setup(page,{beforePut:()=>new Promise(resolve=>release=resolve)});await firstNoteWithPausedClock(page);await page.getByLabel('Note text',{exact:true}).fill('Executing original');await page.clock.runFor(500);await expect.poll(()=>!!release).toBe(true);
 const began=await page.evaluate(()=>Date.now()),dialog=await openWholeDeletion(page),recover=dialog.getByRole('button',{name:'Recover previous operations',exact:true});
 await page.clock.runFor(4999);await expect(recover).toHaveCount(0);await expect(dialog.getByRole('button',{name:'Delete study',exact:true})).toBeDisabled();
 await page.clock.runFor(1);await expect(recover).toBeVisible();expect(await page.evaluate(()=>Date.now())-began).toBe(5000);expect(requests.filter(r=>r.method==='DELETE')).toHaveLength(0);
 const response=page.waitForResponse(r=>r.request().method()==='PUT');release();await (await response).finished();await page.clock.runFor(0);await expect(recover).toBeVisible();await dialog.getByRole('button',{name:'Cancel',exact:true}).click();await expect(page.getByLabel('Note text',{exact:true})).toContainText('Executing original');
});

for(const code of [401,403])test('whole-study deletion current '+code+' masks private attempts without auto replay',async({page})=>{
 const {requests}=await setup(page,{failStudyDelete:code});await firstNote(page);await confirmWholeDeletion(page);await expect(page.getByRole('dialog')).toHaveCount(0);await expect(page.getByLabel('Note text',{exact:true})).toHaveCount(0);expect(requests.filter(r=>r.method==='DELETE')).toHaveLength(1);await page.waitForTimeout(150);expect(requests.filter(r=>r.method==='DELETE')).toHaveLength(1);
});

for(const reply of ['success','denial'])test('whole-study deletion account replacement rejects late '+reply,async({page})=>{
 let release;await setup(page,{beforeStudyDelete:()=>new Promise(resolve=>release=resolve),...(reply==='denial'?{failStudyDelete:403}:{})});await firstNote(page);await confirmWholeDeletion(page);await expect.poll(()=>!!release).toBe(true);await page.route('**/auth/v1/token*',r=>r.fulfill({json:{...session,user:{...session.user,id:'10000000-0000-4000-8000-000000000002'}}}));await page.evaluate(async()=>{const {supabase}=await import('/src/lib/supabase.ts');await supabase.auth.signOut({scope:'local'});await supabase.auth.signInWithPassword({email:'other@example.invalid',password:'fixture'});});release();await expect(page.getByRole('dialog')).toHaveCount(0);await expect(page.getByRole('button',{name:/Recover study deletion:/})).toHaveCount(0);await expect(page.getByLabel('Note text',{exact:true})).toHaveCount(0);await expect(page.getByText('Studies access is unavailable for this account.',{exact:true})).toHaveCount(0);
});

test('whole-study deletion acknowledgement preserves deliberate surviving public focus',async({page})=>{
 let release;await setup(page,{beforeStudyDelete:()=>new Promise(resolve=>release=resolve)});await firstNote(page);const dialog=await confirmWholeDeletion(page);await expect.poll(()=>!!release).toBe(true);await dialog.getByRole('button',{name:'Close',exact:true}).click();const control=test.info().project.name==='mobile'?page.getByRole('button',{name:'Add reader pane',exact:true}):page.getByRole('button',{name:/^Navigate: Genesis, chapter 1/});await control.focus();release();await expect(page.getByLabel('Note text',{exact:true})).toHaveCount(0);await expect(control).toBeFocused();await expect(page.getByText('Study deleted.',{exact:true})).toHaveCount(0);
});

for(const late of ['success','denial'])test('whole-study deletion rejects late collection read '+late+' after acknowledgement',async({page})=>{
 await setup(page);await firstNote(page);await page.getByRole('button',{name:'Back to Studies',exact:true}).click();await page.getByRole('button',{name:'Leave study',exact:true}).click();let release;
 await page.route('**/api/studies/'+study+'/passages',async r=>{await new Promise(resolve=>release=resolve);return r.fulfill(late==='denial'?{status:403,json:{code:'studies_access_denied'}}:{json:{study_id:study,revision:'1',items:[]}});});
 await page.getByRole('button',{name:'Untitled study',exact:true}).click();await expect.poll(()=>!!release).toBe(true);const dialog=await confirmWholeDeletion(page);await expect(dialog).toHaveCount(0);const response=page.waitForResponse(r=>r.url().endsWith('/passages'));release();await (await response).finished();await expect(page.getByRole('heading',{name:'Untitled study',exact:true})).toHaveCount(0);await expect(page.getByText('Studies access is unavailable for this account.',{exact:true})).toHaveCount(0);await expect(page.getByLabel('Search studies',{exact:true})).toBeEnabled();
});

test('whole-study deletion captured target acknowledgement preserves another selected study and writing',async({page})=>{
 let release;const {requests}=await setup(page,{beforeStudyDelete:()=>new Promise(resolve=>release=resolve)});await firstNote(page);
 const other='30000000-0000-4000-8000-000000000002',otherNote='40000000-0000-4000-8000-000000000002',otherValue={document:{version:1,blocks:[{type:'paragraph',direction:'auto',content:[{type:'text',text:'Other study writing',marks:[]}]}]},connections:[],highlights:[]};
 await page.route('**/api/studies/search',r=>r.fulfill({json:{items:[{...attribution,id:study,title:'Untitled study',revision:'1'},{...attribution,id:other,title:'Independent study',revision:'1'}],next_cursor:null}}));
 await page.route('**/api/studies/'+other+'**',r=>{const path=new URL(r.request().url()).pathname,payload=r.request().postDataJSON();return r.fulfill({json:path.endsWith('/passages')?{study_id:other,revision:'1',items:[]}:path.endsWith('/notes/'+otherNote)?(r.request().method()==='PUT'?{operation_id:payload.operation_id,command:'note.replace',study_id:other,note_id:otherNote,revision:'2'}:{...attribution,id:otherNote,study_id:other,visibility:'study',revision:'1',value:otherValue}):path.endsWith('/notes')?{items:[{...attribution,id:otherNote,study_id:other,visibility:'study',revision:'1',value:otherValue}],next_cursor:null}:{...attribution,id:other,title:'Independent study',revision:'1'}});});
 const dialog=await confirmWholeDeletion(page);await expect.poll(()=>!!release).toBe(true);await dialog.getByRole('button',{name:'Close',exact:true}).click();await page.getByRole('button',{name:'Back to Studies',exact:true}).click();await page.getByRole('button',{name:'Leave study',exact:true}).click();await page.getByRole('button',{name:'Independent study',exact:true}).click();await page.getByRole('button',{name:'Other study writing',exact:true}).click();const editor=page.getByLabel('Note text',{exact:true});await editor.fill('Independent unsent input');release();await expect(page.getByRole('button',{name:/Recover study deletion:/})).toHaveCount(0);await expect(editor).toContainText('Independent unsent input');expect(requests.filter(r=>r.method==='DELETE')).toHaveLength(1);await expect(page.getByText('Study deleted.',{exact:true})).toHaveCount(0);await page.getByRole('button',{name:'Back to Studies',exact:true}).click();await expect(page.getByRole('heading',{name:'Independent study',exact:true})).toBeVisible();
});

test('whole-study deletion long title remains readable within desktop and mobile confirmation',async({page})=>{
 const {metadata}=await setup(page);await firstNote(page);metadata.title='aא'.repeat(100);const dialog=await openWholeDeletion(page);await expect(dialog).toContainText(metadata.title);const bounds=await dialog.evaluate(node=>({content:node.scrollWidth<=node.clientWidth,viewport:node.getBoundingClientRect().left>=0&&node.getBoundingClientRect().right<=innerWidth}));expect(bounds).toEqual({content:true,viewport:true});
});

test('whole-study deletion known creation acknowledgement survives failed follow-up read without extra command',async({page})=>{
 const {requests}=await setup(page);await firstNote(page);await page.getByRole('button',{name:'Back to Studies',exact:true}).click();let fail=true;
 await page.route('**/api/studies/'+study+'/notes/'+note,r=>r.request().method()==='GET'&&fail?r.fulfill({status:503,json:{code:'studies_storage_unavailable'}}):r.fallback());
 const postsBefore=requests.filter(r=>r.method==='POST'&&r.path.endsWith('/notes')).length;await page.getByRole('button',{name:'Add note',exact:true}).click();await expect(page.getByRole('alert')).toContainText('Studies could not be loaded. Try again.');fail=false;await page.getByRole('button',{name:'Add note',exact:true}).click();await expect(page.getByLabel('Note text',{exact:true})).toBeVisible();expect(requests.filter(r=>r.method==='POST'&&r.path.endsWith('/notes'))).toHaveLength(postsBefore+1);const dialog=await openWholeDeletion(page);await expect(dialog.getByRole('button',{name:'Delete study',exact:true})).toBeEnabled();await dialog.getByRole('button',{name:'Cancel',exact:true}).click();
});

test('study deletion review recovery has one deadline and ignores late original-save outcomes',async({page})=>{
 const options={failPut:503};const {requests}=await setup(page,options);await firstNoteWithPausedClock(page);await page.getByLabel('Note text',{exact:true}).fill('Retain across recovery timeout');await page.clock.runFor(500);await expect(page.getByRole('status').filter({hasText:'Changes not saved'})).toBeVisible();
 const original=requests.find(r=>r.method==='PUT').payload,dialog=await openWholeDeletion(page),recover=dialog.getByRole('button',{name:'Recover previous operations',exact:true});await expect(recover).toBeVisible();let release;options.failPut=0;options.beforePut=()=>new Promise(resolve=>release=resolve);
 const began=await page.evaluate(()=>Date.now());await recover.click();await expect.poll(()=>!!release).toBe(true);await page.clock.runFor(4999);await expect(recover).toHaveCount(0);await expect(dialog.getByRole('button',{name:'Delete study',exact:true})).toBeDisabled();
 await page.clock.runFor(1);await expect(recover).toBeVisible();expect(await page.evaluate(()=>Date.now())-began).toBe(5000);
 const response=page.waitForResponse(r=>r.request().method()==='PUT');options.beforePut=undefined;release();await (await response).finished();await page.clock.runFor(0);await expect(recover).toBeVisible();expect(requests.filter(r=>r.method==='DELETE')).toHaveLength(0);
 await recover.click();await expect(dialog.getByRole('button',{name:'Delete study',exact:true})).toBeEnabled();const puts=requests.filter(r=>r.method==='PUT');expect(puts).toHaveLength(3);expect(puts[1].payload).toEqual(original);expect(puts[2].payload).toEqual(original);await dialog.getByRole('button',{name:'Cancel',exact:true}).click();await expect(page.getByLabel('Note text',{exact:true})).toContainText('Retain across recovery timeout');
});

for(const failure of ['note_revision_conflict','operation_payload_mismatch','resource_unavailable'])test('study deletion review classifies original child deletion '+failure,async({page})=>{
 const options={failDelete:503};const {requests}=await setup(page,options);await firstNote(page);await page.getByLabel('Note text',{exact:true}).fill('Child input survives');await page.getByRole('button',{name:'Delete note',exact:true}).click();await page.getByRole('dialog').getByRole('button',{name:'Delete note',exact:true}).click();await expect(page.getByRole('dialog')).toContainText('Deletion not confirmed');await page.getByRole('dialog').getByRole('button',{name:'Close',exact:true}).click();const dialog=await openWholeDeletion(page);await expect(dialog.getByRole('button',{name:'Recover previous operations',exact:true})).toBeVisible();options.failDelete=failure==='resource_unavailable'?404:409;options.failDeleteCode=failure;await dialog.getByRole('button',{name:'Recover previous operations',exact:true}).click();await expect(dialog.getByRole('button',{name:'Delete study',exact:true})).toBeEnabled();expect(requests.filter(r=>r.method==='DELETE'&&r.path==='/api/studies/'+study)).toHaveLength(0);await dialog.getByRole('button',{name:'Cancel',exact:true}).click();await expect(page.getByLabel('Note text',{exact:true})).toContainText('Child input survives');
});

test('study deletion review recovered save updates saved preview and preserves newer composing input on Cancel',async({page})=>{
 const options={failPut:503};const {requests}=await setup(page,options);await firstNote(page);const editor=page.getByLabel('Note text',{exact:true});await editor.fill('Acknowledged recovered writing');await expect(page.getByRole('status').filter({hasText:'Changes not saved'})).toBeVisible();await editor.dispatchEvent('compositionstart');await editor.fill('Newer local composition');const dialog=await openWholeDeletion(page);options.failPut=0;await dialog.getByRole('button',{name:'Recover previous operations',exact:true}).click();await expect(dialog.getByRole('button',{name:'Delete study',exact:true})).toBeEnabled();await dialog.getByRole('button',{name:'Cancel',exact:true}).click();await expect(editor).toContainText('Newer local composition');await page.getByRole('button',{name:'Back to Studies',exact:true}).click();await expect(page.getByRole('list',{name:'Notes',exact:true})).toContainText('Acknowledged recovered writing');expect(requests.filter(r=>r.method==='PUT')).toHaveLength(2);
});

test('study deletion review simultaneous save and collection must both settle before confirmation',async({page})=>{
 let releaseSave,releaseCollection;const {requests}=await setup(page,{beforePut:()=>new Promise(resolve=>releaseSave=resolve),beforePassagePut:()=>new Promise(resolve=>releaseCollection=resolve)});await firstNote(page);await page.getByLabel('Note text',{exact:true}).fill('Executing save');await expect.poll(()=>!!releaseSave).toBe(true);await page.getByRole('button',{name:'Back to Studies',exact:true}).click();await addReference(page,'Gen1');await expect.poll(()=>!!releaseCollection).toBe(true);const dialog=await openWholeDeletion(page);releaseSave();await page.waitForTimeout(100);await expect(dialog.getByRole('button',{name:'Delete study',exact:true})).toBeDisabled();releaseCollection();await expect(dialog.getByRole('button',{name:'Delete study',exact:true})).toBeEnabled();expect(requests.filter(r=>r.method==='DELETE')).toHaveLength(0);await dialog.getByRole('button',{name:'Delete study',exact:true}).click();await expect(dialog).toHaveCount(0);
});

test('study deletion review metadata shares the original simultaneous-lane preparation deadline',async({page})=>{
 let releaseSave,releaseCollection,releaseMetadata;const options={beforePut:()=>new Promise(resolve=>releaseSave=resolve),beforePassagePut:()=>new Promise(resolve=>releaseCollection=resolve)};const {requests}=await setup(page,options);await firstNoteWithPausedClock(page);await page.getByLabel('Note text',{exact:true}).fill('Executing save');await page.clock.runFor(500);await expect.poll(()=>!!releaseSave).toBe(true);await page.getByRole('button',{name:'Back to Studies',exact:true}).click();await addReference(page,'Gen1');await expect.poll(()=>!!releaseCollection).toBe(true);
 options.beforeStudyRead=()=>new Promise(resolve=>releaseMetadata=resolve);const began=await page.evaluate(()=>Date.now()),dialog=await openWholeDeletion(page),recover=dialog.getByRole('button',{name:'Recover previous operations',exact:true});
 await page.clock.runFor(3800);releaseSave();releaseCollection();await expect.poll(()=>!!releaseMetadata).toBe(true);await page.clock.runFor(1199);await expect(recover).toHaveCount(0);await expect(dialog.getByRole('button',{name:'Delete study',exact:true})).toBeDisabled();
 await page.clock.runFor(1);await expect(recover).toBeVisible();expect(await page.evaluate(()=>Date.now())-began).toBe(5000);
 const response=page.waitForResponse(r=>r.request().method()==='GET'&&new URL(r.url()).pathname==='/api/studies/'+study);releaseMetadata();await (await response).finished();await page.clock.runFor(0);await expect(recover).toBeVisible();expect(requests.filter(r=>r.method==='DELETE')).toHaveLength(0);await dialog.getByRole('button',{name:'Cancel',exact:true}).click();
});

test('study deletion review explicit reopening after same-user authentication restarts interrupted preparation',async({page})=>{
 let release;const options={beforePut:()=>new Promise(resolve=>release=resolve),failPut:401};const {requests}=await setup(page,options);await firstNote(page);await page.getByLabel('Note text',{exact:true}).fill('Retained across sign-in');await expect.poll(()=>!!release).toBe(true);await openWholeDeletion(page);release();await expect(page.getByRole('dialog')).toHaveCount(0);await page.route('**/auth/v1/token*',r=>r.fulfill({json:{...session,access_token:'renewed-study-review'}}));await page.evaluate(async()=>{const {supabase}=await import('/src/lib/supabase.ts');await supabase.auth.signInWithPassword({email:'reader@example.invalid',password:'fixture'});});options.beforePut=undefined;options.failPut=0;await page.getByRole('button',{name:'Retry Studies',exact:true}).click();await expect(page.getByLabel('Note text',{exact:true})).toContainText('Retained across sign-in');const dialog=await openWholeDeletion(page);await expect(dialog.getByRole('button',{name:'Recover previous operations',exact:true})).toBeVisible();await dialog.getByRole('button',{name:'Recover previous operations',exact:true}).click();await expect(dialog.getByRole('button',{name:'Delete study',exact:true})).toBeEnabled();expect(requests.filter(r=>r.method==='DELETE')).toHaveLength(0);await dialog.getByRole('button',{name:'Cancel',exact:true}).click();
});

for(const failure of ['unknown','resource_unavailable'])test('study deletion review original creation '+failure+' keeps or retires its paired identity',async({page})=>{
 const {requests}=await setup(page);await firstNote(page);await page.getByRole('button',{name:'Back to Studies',exact:true}).click();let phase='unknown';const commands=[];
 await page.route('**/api/studies/'+study+'/notes',r=>{if(r.request().method()!=='POST')return r.fallback();const payload=r.request().postDataJSON();commands.push(payload);return r.fulfill({status:phase==='unavailable'?404:503,json:{code:phase==='unavailable'?'resource_unavailable':'studies_storage_unavailable'}});});
 await page.getByRole('button',{name:'Add note',exact:true}).click();await expect(page.getByRole('alert')).toContainText('Studies could not be loaded');const dialog=await openWholeDeletion(page);await expect(dialog.getByRole('button',{name:'Recover previous operations',exact:true})).toBeVisible();if(failure==='resource_unavailable')phase='unavailable';await dialog.getByRole('button',{name:'Recover previous operations',exact:true}).click();expect(commands).toHaveLength(2);expect(commands[1]).toEqual(commands[0]);expect(requests.filter(r=>r.method==='DELETE')).toHaveLength(0);
 if(failure==='unknown'){await expect(dialog.getByRole('button',{name:'Recover previous operations',exact:true})).toBeVisible();await dialog.getByRole('button',{name:'Cancel',exact:true}).click();await page.getByRole('button',{name:'Add note',exact:true}).click();expect(commands[2]).toEqual(commands[0]);}
 else{await expect(dialog.getByRole('button',{name:'Delete study',exact:true})).toBeEnabled();await dialog.getByRole('button',{name:'Cancel',exact:true}).click();phase='unknown';await page.getByRole('button',{name:'Add note',exact:true}).click();await expect.poll(()=>commands.length).toBe(3);expect(commands[2].operation_id).not.toBe(commands[0].operation_id);}
});

test('study deletion review recovered creation is visible after Cancel and next creations use fresh commands',async({page})=>{
 const {requests}=await setup(page);await firstNote(page);await page.getByRole('button',{name:'Back to Studies',exact:true}).click();const commands=[],otherNote='40000000-0000-4000-8000-000000000002',freshNote='40000000-0000-4000-8000-000000000003';let recover=false;
 await page.route('**/api/studies/'+study+'/notes',r=>{if(r.request().method()!=='POST')return r.fallback();const payload=r.request().postDataJSON();commands.push(payload);return recover?r.fulfill({json:{operation_id:payload.operation_id,command:'note.create',study_id:study,note_id:commands.length<3?otherNote:freshNote,revision:'1'}}):r.fulfill({status:503,json:{code:'studies_storage_unavailable'}});});
 for(const [id,text] of [[otherNote,'Recovered committed note'],[freshNote,'Distinct fresh note']])await page.route('**/api/studies/'+study+'/notes/'+id,r=>r.fulfill({json:{...attribution,id,study_id:study,visibility:'study',revision:'1',value:{document:{version:1,blocks:[{type:'paragraph',direction:'auto',content:[{type:'text',text,marks:[]}]}]},connections:[],highlights:[]}}}));
 await page.getByRole('button',{name:'Add note',exact:true}).click();await expect(page.getByRole('alert')).toContainText('Studies could not be loaded');const dialog=await openWholeDeletion(page);recover=true;await dialog.getByRole('button',{name:'Recover previous operations',exact:true}).click();await expect(dialog.getByRole('button',{name:'Delete study',exact:true})).toBeEnabled();await dialog.getByRole('button',{name:'Cancel',exact:true}).click();await expect(page.getByRole('list',{name:'Notes',exact:true})).toContainText('Recovered committed note');await page.getByRole('button',{name:'Add note',exact:true}).click();await expect(page.getByLabel('Note text',{exact:true})).toContainText('Distinct fresh note');expect(commands).toHaveLength(3);expect(commands[1]).toEqual(commands[0]);expect(commands[2].operation_id).not.toBe(commands[0].operation_id);
 const studiesBefore=requests.filter(request=>request.method==='POST'&&request.path==='/api/studies').length;await page.getByRole('button',{name:'Back to Studies',exact:true}).click();await page.getByRole('button',{name:'Leave study',exact:true}).click();await page.getByRole('button',{name:'Create study',exact:true}).click();await expect.poll(()=>requests.filter(request=>request.method==='POST'&&request.path==='/api/studies').length).toBe(studiesBefore+1);expect(requests.filter(request=>request.method==='POST'&&request.path==='/api/studies').at(-1).payload.operation_id).not.toBe(commands[0].operation_id);
});

for (const rangeMode of ['selection', 'caret']) test(`four-pane layout retains the same composing editor and owned passage atoms through add close and replay (${rangeMode})`, async ({
  page
}) => {
  const {
    requests
  } = await setup(page);
  await firstNote(page);
  const editor = page.getByLabel('Note text', {
    exact: true
  });
  await editor.fill('Original writing ');
  await insertNoteReference(page, 'Genesis 1:2–3');
  await expect(page.getByRole('status').filter({
    hasText: 'Draft saved'
  })).toBeVisible();
  await editor.evaluate(el => {
    window.__fourEditor = el;
    window.__fourAtom = el.querySelector('[data-note-passage]');
  });
  const writes = requests.filter(r => r.method === 'PUT').length;
  await editor.dispatchEvent('compositionstart');
  await editor.evaluate(el => {
    el.append(document.createTextNode(' composing עברית'));
    el.dispatchEvent(new InputEvent('input', {
      bubbles: true,
      inputType: 'insertCompositionText'
    }));
  });
  await editor.evaluate((el, rangeMode) => {
    const walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
    let text = walker.nextNode();
    while (text && text.parentElement.closest('[data-note-passage]')) text = walker.nextNode();
    const range = document.createRange();
    range.setStart(text, rangeMode === 'caret' ? 5 : 2);
    range.setEnd(text, rangeMode === 'caret' ? 5 : 8);
    getSelection().removeAllRanges();
    getSelection().addRange(range);
    window.__fourCaret = range.cloneRange();
  }, rangeMode);
  async function assertCaret() {
    await editor.focus();
    expect(await editor.evaluate(() => {
      const selection = getSelection(),
        range = selection.rangeCount ? selection.getRangeAt(0) : null,
        saved = window.__fourCaret;
      return range ? {
        sameStart: range.startContainer === saved.startContainer,
        start: range.startOffset,
        sameEnd: range.endContainer === saved.endContainer,
        end: range.endOffset
      } : null;
    })).toEqual({
      sameStart: true,
      start: rangeMode === 'caret' ? 5 : 2,
      sameEnd: true,
      end: rangeMode === 'caret' ? 5 : 8
    });
  }
  await addReader(page);
  await assertCaret();
  await page.goBack();
  await assertCaret();
  await page.goForward();
  await assertCaret();
  if (page.viewportSize().width < 768) await page.getByRole('button', {
    name: 'Return to reader',
    exact: true
  }).click();
  await page.getByRole('button', {
    name: 'Close passage 2',
    exact: true
  }).click();
  if (!(await editor.isVisible())) await page.getByRole('button', {
    name: 'Analysis',
    exact: true
  }).click();
  await expect(editor).toContainText('composing עברית');
  await assertCaret();
  expect(await editor.evaluate(el => el === window.__fourEditor && el.querySelector('[data-note-passage]') === window.__fourAtom)).toBe(true);
  await page.waitForTimeout(650);
  expect(requests.filter(r => r.method === 'PUT')).toHaveLength(writes);
  await editor.dispatchEvent('compositionend');
  await assertCaret();
  await expect(page.getByRole('status').filter({
    hasText: 'Draft saved'
  })).toBeVisible();
  await assertCaret();
  expect(requests.filter(r => r.method === 'POST' && r.path.endsWith('/notes'))).toHaveLength(1);
});
test('four-pane public transitions preserve an unknown original save operation', async ({
  page
}) => {
  const options = {
    failPut: 503
  };
  const {
    requests
  } = await setup(page, options);
  await firstNote(page);
  const editor = page.getByLabel('Note text', {
    exact: true
  });
  await editor.fill('Original frozen save');
  await expect(page.getByRole('status').filter({
    hasText: 'Changes not saved'
  })).toBeVisible();
  const original = structuredClone(requests.find(r => r.method === 'PUT').payload);
  await editor.evaluate(el => window.__fourEditor = el);
  await addReader(page);
  await page.goBack();
  await page.goForward();
  await expect(editor).toContainText('Original frozen save');
  expect(await editor.evaluate(el => el === window.__fourEditor)).toBe(true);
  options.failPut = 0;
  await page.getByRole('button', {
    name: 'Retry',
    exact: true
  }).click();
  await expect(page.getByRole('status').filter({
    hasText: 'Draft saved'
  })).toBeVisible();
  expect(requests.filter(r => r.method === 'PUT').map(r => r.payload)).toEqual([original, original]);
});
for (const malformed of ['?book=Gen&chapter=bad&other=keep#reading', '?reader=%7B%7D&book=Exod&other=keep#reading']) test(`review: malformed Add Cancel retains unresolved provenance across replay and refresh until valid choice ${malformed}`, async ({
  page
}) => {
  await setup(page);
  await page.goto('/' + malformed);
  const original = page.url();
  await page.getByRole('button', {
    name: 'Studies',
    exact: true
  }).click();
  await page.getByRole('button', {
    name: 'Start a study',
    exact: true
  }).click();
  await page.getByRole('button', {
    name: 'Create study',
    exact: true
  }).click();
  const idx = await page.evaluate(() => history.state.idx);
  await addReader(page);
  expect(page.url()).toBe(original);
  expect(await page.evaluate(() => history.state.idx)).toBe(idx + 1);
  await expect(page.locator('[data-reader-pane]')).toHaveCount(2);
  await expect(page.getByRole('button', {
    name: 'Add current passage',
    exact: true
  })).toHaveCount(0);
  await expect(page.getByRole('button', {
    name: 'Add passage',
    exact: true
  })).toBeEnabled();
  await page.goBack();
  await expect(page.locator('[data-reader-pane]')).toHaveCount(1);
  await page.goForward();
  await expect(page.locator('[data-reader-pane]')).toHaveCount(2);
  await expect(page.getByRole('button', {
    name: 'Add current passage',
    exact: true
  })).toHaveCount(0);
  await page.goBack();
  await expect(page.locator('[data-reader-pane]')).toHaveCount(1);
  await page.goForward();
  await expect(page.locator('[data-reader-pane]')).toHaveCount(2);
  await expect(page.getByRole('button', {
    name: 'Add current passage',
    exact: true
  })).toHaveCount(0);
  await page.reload();
  expect(page.url()).toBe(original);
  await expect(page.locator('[data-reader-pane]')).toHaveCount(2);
  await page.getByRole('button', {
    name: 'Studies',
    exact: true
  }).click();
  await page.getByRole('button', {
    name: 'Untitled study',
    exact: true
  }).click();
  await expect(page.getByRole('button', {
    name: 'Add current passage',
    exact: true
  })).toHaveCount(0);
  if (page.viewportSize().width < 768) await page.getByRole('button', {
    name: 'Return to reader',
    exact: true
  }).click();
  await page.locator('[data-reader-pane]').nth(1).getByRole('button', {
    name: /Navigate:/
  }).click();
  await page.getByLabel('Passage reference', {
    exact: true
  }).fill('Genesis 2');
  await page.getByLabel('Passage reference', {
    exact: true
  }).press('Enter');
  expect(new URL(page.url()).searchParams.has('reader')).toBe(true);
  expect(new URL(page.url()).searchParams.get('other')).toBe('keep');
  expect(new URL(page.url()).hash).toBe('#reading');
  if ((await page.getByRole('button', {
    name: 'Studies',
    exact: true
  }).getAttribute('aria-pressed')) !== 'true') await page.getByRole('button', {
    name: 'Studies',
    exact: true
  }).click();
  await expect(page.getByRole('button', {
    name: 'Add current passage',
    exact: true
  })).toBeVisible();
});
test('review: malformed capacity Add replacement Cancel still requires a valid passage choice', async ({
  page
}) => {
  await setup(page);
  await page.goto('/?chapter=bad');
  const original = page.url();
  for (let i = 0; i < 3; i++) await addReader(page);
  await page.getByRole('button', {
    name: 'Add reader pane',
    exact: true
  }).click();
  await page.getByRole('dialog', {
    name: 'Choose passage to replace'
  }).getByRole('button', {
    name: 'Replace passage 1: Genesis 1',
    exact: true
  }).click();
  await page.getByRole('dialog', {
    name: 'Book and chapter selector'
  }).getByRole('button', {
    name: 'Cancel',
    exact: true
  }).click();
  expect(page.url()).toBe(original);
  await page.reload();
  await expect(page.locator('[data-reader-pane]')).toHaveCount(4);
  await page.getByRole('button', {
    name: 'Studies',
    exact: true
  }).click();
  await page.getByRole('button', {
    name: 'Start a study',
    exact: true
  }).click();
  await page.getByRole('button', {
    name: 'Create study',
    exact: true
  }).click();
  await expect(page.getByRole('button', {
    name: 'Add current passage',
    exact: true
  })).toHaveCount(0);
  await expect(page.getByRole('button', {
    name: 'Add passage',
    exact: true
  })).toBeEnabled();
});

test('workspace tabs inherit note identity but retain independent tool and study contexts',async({page})=>{
 await setup(page);await firstNote(page);
 await page.getByLabel('Note text',{exact:true}).fill('Retained עברית');
 await page.getByRole('button',{name:'New workspace tab',exact:true}).click();
 await page.getByRole('dialog',{name:'Book and chapter selector'}).getByRole('button',{name:'Cancel',exact:true}).click();
 await expect(page.getByLabel('Note text',{exact:true})).not.toBeVisible();
 await page.getByRole('button',{name:'Analysis',exact:true}).click();
 await expect(page.getByLabel('Note text',{exact:true})).toContainText('Retained עברית');
 await page.getByRole('button',{name:'Back to Studies',exact:true}).click();
 await page.getByRole('button',{name:'Leave study',exact:true}).click();
 const tabs=page.getByRole('tablist',{name:'Workspace tabs'}).getByRole('tab');await tabs.first().click();
 await expect(page.getByLabel('Note text',{exact:true})).toBeVisible();
 await expect(page.getByLabel('Note text',{exact:true})).toContainText('Retained עברית');
});

test('workspace tabs retain distinct note DOM caret atoms and composition routing without cloning a shared lane',async({page})=>{
 const catalogue=require('../src/generated/reference-catalogue.json');
 const reference={catalogue_id:catalogue.catalogue_id,catalogue_version:catalogue.catalogue_version,versification_id:catalogue.books[0].versification_id,book_id:'Gen',target:{kind:'chapter',chapter:1}};
 await reviewLibrary(page,{read:(parent,id,view)=>{const item=view(parent,id,id===note?'A first':'A second');if(id===note)item.value={document:{version:2,blocks:[{type:'paragraph',direction:'auto',content:[{type:'text',text:'A first',marks:[]},{type:'passage_link',reference,label:'Genesis 1'},{type:'text',text:' suffix',marks:[]}]}]},connections:[],highlights:[]};return item;}});
 await page.getByRole('button',{name:'Study A',exact:true}).click();await page.getByRole('button',{name:'A first',exact:true}).click();
 const editor=page.getByRole('textbox',{name:'Note text',exact:true});
 await editor.dispatchEvent('compositionstart');
 await editor.evaluate(el=>{window.tabOriginalEditor=el;window.tabOriginalAtom=el.querySelector('[data-note-passage]');window.tabOriginalText=el.querySelector('p').firstChild;window.tabOriginalText.textContent='אחד composing';el.dispatchEvent(new InputEvent('input',{bubbles:true,isComposing:true}));el.focus();const range=document.createRange();range.setStart(window.tabOriginalText,2);range.setEnd(window.tabOriginalText,4);const selected=getSelection();selected.removeAllRanges();selected.addRange(range);});
 await page.getByRole('button',{name:'New workspace tab',exact:true}).click();await page.getByRole('dialog',{name:'Book and chapter selector'}).getByRole('button',{name:'Cancel',exact:true}).click();
 await page.getByRole('button',{name:'Studies',exact:true}).click();await page.getByRole('button',{name:'A second',exact:true}).click();await expect(editor).toHaveText('A second');
 await page.evaluate(()=>window.tabOriginalEditor.dispatchEvent(new CompositionEvent('compositionend',{bubbles:true,data:'אחד composing'})));
 await editor.fill('second note בלבד');await page.getByRole('tablist',{name:'Workspace tabs'}).getByRole('tab').first().click();
 await expect(editor).toHaveText('אחד composingGenesis 1 suffix');expect(await editor.evaluate(el=>el===window.tabOriginalEditor&&el.querySelector('[data-note-passage]')===window.tabOriginalAtom)).toBe(true);
 await editor.focus();expect(await editor.evaluate(()=>{const r=getSelection().getRangeAt(0);return {start:r.startContainer===window.tabOriginalText,end:r.endContainer===window.tabOriginalText,startOffset:r.startOffset,endOffset:r.endOffset};})).toEqual({start:true,end:true,startOffset:2,endOffset:4});
 await expect(page.locator('[aria-label="Note text"]')).toHaveCount(2);await editor.press('End');await editor.press('x');await expect(editor.locator('[data-note-passage]')).toHaveCount(1);await editor.press('ControlOrMeta+z');await expect(editor).not.toContainText(' suffixx');await expect(editor.locator('[data-note-passage]')).toHaveCount(1);await editor.press('ControlOrMeta+Shift+z');await expect(editor.locator('[data-note-passage]')).toHaveCount(1);await expect(page.getByRole('status').filter({hasText:'Draft saved'})).toBeVisible();
});

test('workspace tabs guard only the last live note context and reject changed-input consent',async({page})=>{
 const options={failPut:503};await setup(page,options);await firstNote(page);await page.getByRole('textbox',{name:'Note text',exact:true}).fill('unsaved original');
 await expect(page.getByRole('status').filter({hasText:'Changes not saved'})).toBeVisible();
 await page.getByRole('button',{name:'New workspace tab',exact:true}).click();await page.getByRole('dialog',{name:'Book and chapter selector'}).getByRole('button',{name:'Cancel',exact:true}).click();
 await page.getByRole('button',{name:'Close tab 1',exact:true}).click();await expect(page.getByRole('dialog',{name:'Changes not saved'})).toHaveCount(0);
 await page.getByRole('button',{name:'New workspace tab',exact:true}).click();await page.getByRole('dialog',{name:'Book and chapter selector'}).getByRole('button',{name:'Cancel',exact:true}).click();
 await page.getByRole('button',{name:'Studies',exact:true}).click();await page.getByRole('button',{name:'Leave study',exact:true}).click();
 await page.getByRole('tablist',{name:'Workspace tabs'}).getByRole('tab').first().click();
 await page.getByRole('button',{name:'Close tab 1',exact:true}).click();await expect(page.getByRole('dialog',{name:'Changes not saved'})).toBeVisible();
 await page.evaluate(()=>{const el=document.querySelector('[aria-label="Note text"]');el.textContent='newer input after consent';el.dispatchEvent(new InputEvent('input',{bubbles:true}));});
 await page.getByRole('button',{name:'Close anyway',exact:true}).click();await expect(page.getByRole('tablist',{name:'Workspace tabs'}).getByRole('tab')).toHaveCount(2);
 await page.getByRole('button',{name:'Analysis',exact:true}).click();await expect(page.getByRole('textbox',{name:'Note text',exact:true})).toHaveText('newer input after consent');
});

test('workspace tabs retain a closed-origin creation recovery item without hijacking the active tab',async({page})=>{
 const {requests}=await setup(page);let release;await page.route('**/api/studies',async r=>{if(r.request().method()!=='POST')return r.fallback();await new Promise(resolve=>release=resolve);return r.fallback();});
 await page.goto('/');await page.getByRole('button',{name:'Studies',exact:true}).click();await page.getByRole('button',{name:'Start a study',exact:true}).click();await page.getByRole('button',{name:'Create study',exact:true}).click();await expect.poll(()=>!!release).toBe(true);
 await page.getByRole('button',{name:'New workspace tab',exact:true}).click();await page.getByRole('dialog',{name:'Book and chapter selector'}).getByRole('button',{name:'Cancel',exact:true}).click();await page.getByRole('button',{name:'Close tab 1',exact:true}).click();release();
 await expect(page.getByRole('button',{name:'Open created study',exact:true})).toBeVisible();await expect(page.getByRole('button',{name:'Studies',exact:true})).toHaveAttribute('aria-pressed','false');expect(requests.filter(r=>r.path==='/api/studies'&&r.method==='POST')).toHaveLength(1);
 await page.getByRole('button',{name:'Open created study',exact:true}).click();await expect(page.getByRole('heading',{name:'Untitled study',exact:true})).toBeVisible();expect(requests.filter(r=>r.path==='/api/studies'&&r.method==='POST')).toHaveLength(1);
});

test('workspace tabs capacity replay guards the sole unresolved context and Stay cancels held restoration',async({page})=>{
 const options={failPut:503};await setup(page,options);await firstNote(page);await page.getByRole('textbox',{name:'Note text',exact:true}).fill('sole unsaved context');await expect(page.getByRole('status').filter({hasText:'Changes not saved'})).toBeVisible();
 const add=async()=>{await page.getByRole('button',{name:'New workspace tab',exact:true}).click();await page.getByRole('dialog',{name:'Book and chapter selector'}).getByRole('button',{name:'Cancel',exact:true}).click();};
 await add();await page.getByRole('button',{name:'Studies',exact:true}).click();await page.getByRole('button',{name:'Leave study',exact:true}).click();await page.getByRole('button',{name:'Close tab 2',exact:true}).click();
 await add();await page.getByRole('button',{name:'Studies',exact:true}).click();await page.getByRole('button',{name:'Leave study',exact:true}).click();
 for(let i=0;i<10;i++)await add();await page.evaluate(()=>history.go(-12));
 const restore=page.getByRole('dialog',{name:'Choose tab to close and restore'});await expect(restore).toBeVisible();const idx=await page.evaluate(()=>history.state.idx);
 await restore.getByRole('button',{name:/Close tab 1:/}).click();const consent=page.getByRole('dialog',{name:'Changes not saved'});await expect(consent).toBeVisible();await consent.getByRole('button',{name:'Stay',exact:true}).click();await expect(consent).toHaveCount(0);await expect(restore).toHaveCount(0);await expect(page.getByRole('tablist',{name:'Workspace tabs'}).getByRole('tab')).toHaveCount(12);expect(await page.evaluate(()=>history.state.idx)).toBe(idx);
 const publicEntry=await page.evaluate(()=>JSON.stringify(history.state.usr.scribeswellReader));
 await page.getByRole('button',{name:'Studies',exact:true}).click();await page.getByRole('button',{name:'Untitled study',exact:true}).click();await expect(page.getByRole('button',{name:'Add current passage',exact:true})).toHaveCount(0);await expect(page.getByRole('button',{name:'Add passage',exact:true})).toBeVisible();
 await page.evaluate(()=>{const scroll=document.querySelector('[data-reader-scroll]');scroll.dispatchEvent(new WheelEvent('wheel',{bubbles:true}));scroll.dispatchEvent(new Event('scroll',{bubbles:true}));});await page.waitForTimeout(200);expect(await page.evaluate(()=>JSON.stringify(history.state.usr.scribeswellReader))).toBe(publicEntry);
 await page.getByRole('button',{name:'Choose tab to close and restore',exact:true}).click();await expect(restore).toBeVisible();await restore.getByRole('button',{name:'Cancel',exact:true}).click();
 await page.getByRole('tablist',{name:'Workspace tabs'}).getByRole('tab').first().click();await expect(page.getByRole('button',{name:'Choose tab to close and restore',exact:true})).toHaveCount(0);if(await page.getByRole('button',{name:'Analysis',exact:true}).getAttribute('aria-pressed')!=='true')await page.getByRole('button',{name:'Analysis',exact:true}).click();await expect(page.getByRole('textbox',{name:'Note text',exact:true})).toHaveText('sole unsaved context');
 await page.goBack();await expect(restore).toBeVisible();const replayIndex=await page.evaluate(()=>history.state.idx);await restore.getByRole('button',{name:/Close tab 1:/}).click();await consent.getByRole('button',{name:'Close anyway',exact:true}).click();await expect(restore).toHaveCount(0);await expect(page.getByRole('tablist',{name:'Workspace tabs'}).getByRole('tab')).toHaveCount(12);expect(await page.evaluate(()=>history.state.idx)).toBe(replayIndex);await expect(page.getByRole('button',{name:'Analysis',exact:true})).toHaveAttribute('aria-pressed','false');await page.getByRole('button',{name:'Analysis',exact:true}).click();await expect(page.getByRole('textbox',{name:'Note text',exact:true})).toHaveCount(0);await expect(page.getByText('Select a note in Studies.',{exact:true})).toBeVisible();
});

test('workspace tabs closed history never restores inherited private associations',async({page})=>{
 await setup(page);await firstNote(page);await page.getByRole('textbox',{name:'Note text',exact:true}).fill('private lane remains A');await expect(page.getByRole('status').filter({hasText:'Draft saved'})).toBeVisible();
 await page.getByRole('button',{name:'New workspace tab',exact:true}).click();await page.getByRole('dialog',{name:'Book and chapter selector'}).getByRole('button',{name:'Cancel',exact:true}).click();await page.getByRole('button',{name:'Close tab 2',exact:true}).click();await page.goBack();
 await expect(page.getByRole('tablist',{name:'Workspace tabs'}).getByRole('tab')).toHaveCount(2);await expect(page.getByRole('button',{name:'Analysis',exact:true})).toHaveAttribute('aria-pressed','false');await page.getByRole('button',{name:'Analysis',exact:true}).click();await expect(page.getByRole('textbox',{name:'Note text',exact:true})).toHaveCount(0);await expect(page.getByText('Select a note in Studies.',{exact:true})).toBeVisible();
 await page.getByRole('tablist',{name:'Workspace tabs'}).getByRole('tab').first().click();await expect(page.getByRole('textbox',{name:'Note text',exact:true})).toHaveText('private lane remains A');
});

test('workspace tabs mask all private labels during authentication loss and clear them on account replacement',async({page})=>{
 const options={failPut:401};await setup(page,options);await firstNote(page);const rename=async(index,label)=>{await page.getByRole('button',{name:`Rename tab ${index}`,exact:true}).click();await page.getByLabel('Tab name',{exact:true}).fill(label);await page.getByRole('dialog',{name:'Rename workspace tab'}).getByRole('button',{name:'Save',exact:true}).click();};
 await rename(1,'private label A');await page.getByRole('button',{name:'New workspace tab',exact:true}).click();await page.getByRole('dialog',{name:'Book and chapter selector'}).getByRole('button',{name:'Cancel',exact:true}).click();await rename(2,'private label B');await page.getByRole('button',{name:'Analysis',exact:true}).click();await page.getByRole('textbox',{name:'Note text',exact:true}).fill('auth failure input');await expect(page.getByRole('alert')).toContainText('Sign in');await expect(page.getByText('private label A',{exact:true})).toHaveCount(0);await expect(page.getByText('private label B',{exact:true})).toHaveCount(0);
 await page.route('**/auth/v1/token*',r=>r.fulfill({json:{...session,access_token:'renewed-current'}}));await page.evaluate(async()=>{const {supabase}=await import('/src/lib/supabase.ts');await supabase.auth.signInWithPassword({email:'reader@example.invalid',password:'fixture'});});options.failPut=0;await page.getByRole('button',{name:'Retry Studies',exact:true}).click();await expect(page.getByText('private label A',{exact:true})).toBeVisible();await expect(page.getByText('private label B',{exact:true})).toBeVisible();
 await page.route('**/auth/v1/token*',r=>r.fulfill({json:{...session,user:{...session.user,id:'10000000-0000-4000-8000-000000000002'}}}));await page.evaluate(async()=>{const {supabase}=await import('/src/lib/supabase.ts');await supabase.auth.signOut({scope:'local'});await supabase.auth.signInWithPassword({email:'other@example.invalid',password:'fixture'});});await expect(page.getByText('private label A',{exact:true})).toHaveCount(0);await expect(page.getByText('private label B',{exact:true})).toHaveCount(0);await expect(page.getByText('auth failure input',{exact:true})).toHaveCount(0);await page.getByRole('button',{name:'Add reader pane',exact:true}).click();await page.getByRole('dialog',{name:'Book and chapter selector'}).getByRole('button',{name:'Cancel',exact:true}).click();await expect(page.getByText('private label A',{exact:true})).toHaveCount(0);await expect(page.getByText('private label B',{exact:true})).toHaveCount(0);
});

test('workspace tabs last-context discard retains only the original unknown save for explicit recovery',async({page})=>{
 const options={failPut:503};const {requests}=await setup(page,options);await firstNote(page);await page.getByRole('button',{name:'New workspace tab',exact:true}).click();await page.getByRole('dialog',{name:'Book and chapter selector'}).getByRole('button',{name:'Cancel',exact:true}).click();await page.getByRole('button',{name:'Studies',exact:true}).click();await page.getByRole('button',{name:'Leave study',exact:true}).click();await page.getByRole('tablist',{name:'Workspace tabs'}).getByRole('tab').first().click();
 await page.getByRole('textbox',{name:'Note text',exact:true}).fill('original unknown payload');await expect(page.getByRole('status').filter({hasText:'Changes not saved'})).toBeVisible();const original=structuredClone(requests.filter(r=>r.method==='PUT').at(-1).payload);await page.getByRole('textbox',{name:'Note text',exact:true}).fill('newer input explicitly abandoned');
 await page.getByRole('button',{name:'Close tab 1',exact:true}).click();await page.getByRole('dialog',{name:'Changes not saved'}).getByRole('button',{name:'Close anyway',exact:true}).click();await expect(page.getByRole('tablist',{name:'Workspace tabs'}).getByRole('tab')).toHaveCount(1);await expect(page.locator('[aria-label="Note text"]')).toHaveCount(0);await expect(page.getByRole('button',{name:'Recover note save 1',exact:true})).toBeVisible();options.failPut=0;await page.getByRole('button',{name:'Recover note save 1',exact:true}).click();await expect(page.getByRole('button',{name:'Recover note save 1',exact:true})).toHaveCount(0);expect(requests.filter(r=>r.method==='PUT')).toHaveLength(2);expect(requests.filter(r=>r.method==='PUT').at(-1).payload).toEqual(original);await expect(page.getByRole('tablist',{name:'Workspace tabs'}).getByRole('tab')).toHaveCount(1);await expect(page.locator('[aria-label="Note text"]')).toHaveCount(0);expect(requests.filter(r=>r.method==='DELETE')).toHaveLength(0);
});

test('workspace tabs direct Open in new tab retains a complete range with no picker and inherits only note identity',async({page})=>{
 const {collection,requests}=await setup(page);const catalogue=require('../src/generated/reference-catalogue.json');const reference={catalogue_id:catalogue.catalogue_id,catalogue_version:catalogue.catalogue_version,versification_id:catalogue.books[0].versification_id,book_id:'Gen',target:{kind:'verse_range',start:{chapter:1,verse:31},end:{chapter:2,verse:3}}};collection.items.push({id:'50000000-0000-4000-8000-000000000001',reference});await firstNote(page);await page.getByRole('textbox',{name:'Note text',exact:true}).fill('associated original lane');await expect(page.getByRole('status').filter({hasText:'Draft saved'})).toBeVisible();await page.getByRole('button',{name:'Back to Studies',exact:true}).click();await page.getByRole('button',{name:'Open Genesis 1:31–2:3 in new tab',exact:true}).click();await expect(page.getByRole('dialog')).toHaveCount(0);expect(await page.evaluate(()=>JSON.parse(new URL(location.href).searchParams.get('reader')).panes[0].ref)).toEqual(reference);await expect(page.getByRole('button',{name:'Analysis',exact:true})).toHaveAttribute('aria-pressed','false');await page.getByRole('button',{name:'Analysis',exact:true}).click();await expect(page.getByRole('textbox',{name:'Note text',exact:true})).toHaveText('associated original lane');expect(requests.filter(r=>r.method==='POST'&&r.path.endsWith('/notes'))).toHaveLength(1);
});

for(const target of ['note','study'])test(`workspace tabs confirmed ${target} deletion clears every matching private association and retains public tabs`,async({page})=>{
 const {requests}=await setup(page);await firstNote(page);await page.getByRole('textbox',{name:'Note text',exact:true}).fill('shared deleted resource');await expect(page.getByRole('status').filter({hasText:'Draft saved'})).toBeVisible();await page.getByRole('button',{name:'New workspace tab',exact:true}).click();await page.getByRole('dialog',{name:'Book and chapter selector'}).getByRole('button',{name:'Cancel',exact:true}).click();await page.getByRole('button',{name:'Analysis',exact:true}).click();await page.getByRole('button',{name:`Delete ${target}`,exact:true}).click();await page.getByRole('dialog').getByRole('button',{name:`Delete ${target}`,exact:true}).click();await expect(page.getByRole('dialog')).toHaveCount(0);await expect(page.locator('[aria-label="Note text"]')).toHaveCount(0);await page.getByRole('tablist',{name:'Workspace tabs'}).getByRole('tab').first().click();await expect(page.locator('[aria-label="Note text"]')).toHaveCount(0);await expect(page.getByRole('tablist',{name:'Workspace tabs'}).getByRole('tab')).toHaveCount(2);expect(requests.filter(r=>r.method==='DELETE')).toHaveLength(1);if(page.viewportSize().width<768)await page.getByRole('button',{name:'Return to reader',exact:true}).click();await expect(page.getByRole('button',{name:/Word: בְּרֵאשִׁית/})).toBeVisible();
});

test('workspace tabs inherited study outlines retain independent pagination cursors',async({page})=>{
 await reviewLibrary(page,{notes:async(parent,cursor,view)=>cursor?{items:[view(parent,'40000000-0000-4000-8000-000000000003','Older outline note')],next_cursor:null}:{items:[view(parent,note,'A first')],next_cursor:'page-two'}});await page.getByRole('button',{name:'Study A',exact:true}).click();await expect(page.getByRole('button',{name:'More notes',exact:true})).toBeVisible();await page.getByRole('button',{name:'New workspace tab',exact:true}).click();await page.getByRole('dialog',{name:'Book and chapter selector'}).getByRole('button',{name:'Cancel',exact:true}).click();await page.getByRole('button',{name:'Studies',exact:true}).click();await page.getByRole('button',{name:'More notes',exact:true}).click();await expect(page.getByRole('button',{name:'Older outline note',exact:true})).toBeVisible();await expect(page.getByRole('button',{name:'More notes',exact:true})).toHaveCount(0);await page.getByRole('tablist',{name:'Workspace tabs'}).getByRole('tab').first().click();await expect(page.getByRole('button',{name:'Older outline note',exact:true})).toHaveCount(0);await page.getByRole('button',{name:'More notes',exact:true}).click();await expect(page.getByRole('button',{name:'Older outline note',exact:true})).toBeVisible();
});

test('workspace tabs reject stale layout consent and clear open consent on account replacement',async({page})=>{
 const options={failPut:503};await setup(page,options);await firstNote(page);await page.getByRole('button',{name:'New workspace tab',exact:true}).click();await page.getByRole('dialog',{name:'Book and chapter selector'}).getByRole('button',{name:'Cancel',exact:true}).click();await page.getByRole('button',{name:'Studies',exact:true}).click();await page.getByRole('button',{name:'Leave study',exact:true}).click();await page.getByRole('tablist',{name:'Workspace tabs'}).getByRole('tab').first().click();await page.getByRole('textbox',{name:'Note text',exact:true}).fill('consent origin');await expect(page.getByRole('status').filter({hasText:'Changes not saved'})).toBeVisible();await page.getByRole('button',{name:'Close tab 1',exact:true}).click();await expect(page.getByRole('dialog',{name:'Changes not saved'})).toBeVisible();
 await page.getByRole('tablist',{name:'Workspace tabs'}).getByRole('tab').nth(1).evaluate(el=>el.click());await page.getByRole('dialog',{name:'Changes not saved'}).getByRole('button',{name:'Close anyway',exact:true}).click();await expect(page.getByRole('tablist',{name:'Workspace tabs'}).getByRole('tab')).toHaveCount(2);await page.getByRole('tablist',{name:'Workspace tabs'}).getByRole('tab').first().click();await expect(page.getByRole('textbox',{name:'Note text',exact:true})).toHaveText('consent origin');await page.getByRole('button',{name:'Close tab 1',exact:true}).click();await expect(page.getByRole('dialog',{name:'Changes not saved'})).toBeVisible();
 await page.route('**/auth/v1/token*',r=>r.fulfill({json:{...session,user:{...session.user,id:'10000000-0000-4000-8000-000000000002'}}}));await page.evaluate(async()=>{const {supabase}=await import('/src/lib/supabase.ts');await supabase.auth.signOut({scope:'local'});await supabase.auth.signInWithPassword({email:'other@example.invalid',password:'fixture'});});await expect(page.getByRole('dialog',{name:'Changes not saved'})).toHaveCount(0);await expect(page.locator('[aria-label="Note text"]')).toHaveCount(0);await expect(page.getByRole('tablist',{name:'Workspace tabs'}).getByRole('tab')).toHaveCount(2);
});

test('workspace tabs recheck last-context departure after a delayed replacement read without background focus',async({page})=>{
 let release;await reviewLibrary(page,{read:async(parent,id,view)=>{if(id!==note)await new Promise(resolve=>release=resolve);return view(parent,id,id===note?'A first':'A second');}});await page.route('**/api/studies/*/notes/*',r=>r.request().method()==='PUT'?r.fulfill({status:503,json:{code:'studies_storage_unavailable'}}):r.fallback());await page.getByRole('button',{name:'Study A',exact:true}).click();await page.getByRole('button',{name:'A first',exact:true}).click();await page.getByRole('textbox',{name:'Note text',exact:true}).fill('last-context race input');await expect(page.getByRole('status').filter({hasText:'Changes not saved'})).toBeVisible();await page.getByRole('button',{name:'New workspace tab',exact:true}).click();await page.getByRole('dialog',{name:'Book and chapter selector'}).getByRole('button',{name:'Cancel',exact:true}).click();await page.getByRole('tablist',{name:'Workspace tabs'}).getByRole('tab').first().click();await page.getByRole('button',{name:'Back to Studies',exact:true}).click();await page.getByRole('button',{name:'A second',exact:true}).click();await expect.poll(()=>!!release).toBe(true);await page.getByRole('tablist',{name:'Workspace tabs'}).getByRole('tab').nth(1).click();await page.getByRole('button',{name:'Studies',exact:true}).click();await page.getByRole('button',{name:'Leave study',exact:true}).click();const response=page.waitForResponse('**/notes/40000000-0000-4000-8000-000000000002');release();await response;await expect(page.getByRole('dialog',{name:'Changes not saved'})).toHaveCount(0);await page.getByRole('tablist',{name:'Workspace tabs'}).getByRole('tab').first().click();if(await page.getByRole('button',{name:'Analysis',exact:true}).getAttribute('aria-pressed')!=='true')await page.getByRole('button',{name:'Analysis',exact:true}).click();await expect(page.getByRole('textbox',{name:'Note text',exact:true})).toHaveText('last-context race input');
});

test('workspace tabs libraries retain distinct applied queries and scroll when flags match',async({page})=>{
 await setup(page,{search:async(r,body)=>r.fulfill({json:{items:Array.from({length:20},(_,i)=>({...attribution,id:`30000000-0000-4000-8000-${String(i+10).padStart(12,'0')}`,title:`${body.query||'initial'} result ${i}`,revision:'1'})),next_cursor:null}})});await page.goto('/');await page.getByRole('button',{name:'Studies',exact:true}).click();const query=page.getByRole('textbox',{name:'Search studies',exact:true}),surface=page.getByRole('complementary',{name:'Study tools',exact:true});await query.fill('alfa');await query.press('Enter');await expect(page.getByRole('button',{name:'alfa result 0',exact:true})).toBeVisible();const a=await surface.evaluate(el=>{el.scrollTop=200;return el.scrollTop;});expect(a).toBeGreaterThan(100);await page.waitForTimeout(100);await page.getByRole('button',{name:'New workspace tab',exact:true}).click();await page.getByRole('dialog',{name:'Book and chapter selector'}).getByRole('button',{name:'Cancel',exact:true}).click();await page.getByRole('button',{name:'Studies',exact:true}).click();await query.fill('beta');await query.press('Enter');await expect(page.getByRole('button',{name:'beta result 0',exact:true})).toBeVisible();const b=await surface.evaluate(el=>{el.scrollTop=400;return el.scrollTop;});expect(b).toBeGreaterThan(a+50);await page.waitForTimeout(100);await page.getByRole('tablist',{name:'Workspace tabs'}).getByRole('tab').first().click();await expect(query).toHaveValue('alfa');await expect.poll(async()=>Math.abs(await surface.evaluate(el=>el.scrollTop)-a)).toBeLessThan(3);await page.getByRole('tablist',{name:'Workspace tabs'}).getByRole('tab').nth(1).click();await expect(query).toHaveValue('beta');await expect.poll(async()=>Math.abs(await surface.evaluate(el=>el.scrollTop)-b)).toBeLessThan(3);
});

test('workspace tabs delayed creation retains known recovery when new last-context input prevents attachment',async({page})=>{
 const options={failPut:503};await setup(page,options);await firstNote(page);const other='40000000-0000-4000-8000-000000000002';let release,posts=0;
 await page.route('**/api/studies/*/notes',async r=>{if(r.request().method()!=='POST')return r.fallback();posts++;await new Promise(resolve=>release=resolve);const body=r.request().postDataJSON();return r.fulfill({json:{operation_id:body.operation_id,command:'note.create',study_id:study,note_id:other,revision:'1'}});});
 await page.route('**/notes/'+other,r=>r.fulfill({json:{...attribution,id:other,study_id:study,visibility:'study',revision:'1',value:{document:{version:1,blocks:[]},connections:[],highlights:[]}}}));await page.getByRole('button',{name:'Back to Studies',exact:true}).click();await page.getByRole('button',{name:'Add note',exact:true}).click();await expect.poll(()=>!!release).toBe(true);
 await page.locator('[aria-label="Note text"]').evaluate(el=>{el.textContent='late composition input';el.dispatchEvent(new InputEvent('input',{bubbles:true}));});await page.waitForTimeout(700);release();const consent=page.getByRole('dialog',{name:'Changes not saved'});await expect(consent).toBeVisible();await consent.getByRole('button',{name:'Stay',exact:true}).click();await expect(page.getByRole('button',{name:'Open created note',exact:true})).toBeVisible();await page.getByRole('button',{name:'Analysis',exact:true}).click();await expect(page.getByRole('textbox',{name:'Note text',exact:true})).toHaveText('late composition input');expect(posts).toBe(1);
});

test('workspace tabs retain malformed-origin URL and collection refusal after another tab navigates validly',async({page})=>{
 await setup(page);const malformed='/?reader=%7B%7D&foreign=keep#reading';await page.goto(malformed);const original=page.url();await page.evaluate(()=>{const state=history.state;history.replaceState({...state,foreignOuter:'retained',usr:{...state.usr,foreignUser:'retained'}},'');});
 await page.getByRole('button',{name:'Studies',exact:true}).click();await page.getByRole('button',{name:'Start a study',exact:true}).click();await page.getByRole('button',{name:'Create study',exact:true}).click();await expect(page.getByRole('button',{name:'Add current passage',exact:true})).toHaveCount(0);
 await page.getByRole('button',{name:'New workspace tab',exact:true}).click();await page.getByRole('dialog',{name:'Book and chapter selector'}).getByRole('textbox',{name:'Passage reference',exact:true}).fill('Genesis 2');await page.getByRole('dialog',{name:'Book and chapter selector'}).getByRole('textbox',{name:'Passage reference',exact:true}).press('Enter');await expect(page.getByText('Invalid reading link',{exact:true})).toHaveCount(0);expect(new URL(page.url()).searchParams.get('reader')).not.toBe('{}');
 await page.getByRole('tablist',{name:'Workspace tabs'}).getByRole('tab').first().click();expect(page.url()).toBe(original);await expect(page.getByText('Invalid reading link',{exact:true})).toBeVisible();await expect(page.getByRole('button',{name:'Add current passage',exact:true})).toHaveCount(0);await expect(page.getByRole('button',{name:'Add passage',exact:true})).toBeVisible();expect(await page.evaluate(()=>[history.state.foreignOuter,history.state.usr.foreignUser])).toEqual(['retained','retained']);
 if(page.viewportSize().width<768)await page.getByRole('button',{name:'Return to reader',exact:true}).click();await page.getByRole('button',{name:/Navigate:/}).first().click();await page.getByRole('textbox',{name:'Passage reference',exact:true}).fill('Genesis 1');await page.getByRole('textbox',{name:'Passage reference',exact:true}).press('Enter');await expect(page.getByText('Invalid reading link',{exact:true})).toHaveCount(0);if(await page.getByRole('button',{name:'Studies',exact:true}).getAttribute('aria-pressed')!=='true')await page.getByRole('button',{name:'Studies',exact:true}).click();await expect(page.getByRole('button',{name:'Add current passage',exact:true})).toBeVisible();
});

async function reviewTabAdd(page){await page.getByRole('button',{name:'New workspace tab',exact:true}).click();await page.getByRole('dialog',{name:'Book and chapter selector'}).getByRole('button',{name:'Cancel',exact:true}).click();}
async function reviewTabRename(page,index,label){await page.getByRole('button',{name:`Rename tab ${index}`,exact:true}).click();await page.getByLabel('Tab name',{exact:true}).fill(label);await page.getByRole('dialog',{name:'Rename workspace tab'}).getByRole('button',{name:'Save',exact:true}).click();}
async function reviewTwoNotes(page){await reviewLibrary(page);await page.getByRole('button',{name:'Study A',exact:true}).click();await page.getByRole('button',{name:'A first',exact:true}).click();await reviewTabAdd(page);await page.getByRole('button',{name:'Studies',exact:true}).click();await page.getByRole('button',{name:'A second',exact:true}).click();}
test('review tabs B1 delayed denial clears labels renamed on newer inactive live tab records',async({page})=>{
 let release;const options={beforeRename:()=>new Promise(resolve=>release=resolve),failRename:403};await setup(page,options);await firstNote(page);await reviewTabAdd(page);await page.getByRole('tablist',{name:'Workspace tabs'}).getByRole('tab').first().click();await page.getByRole('button',{name:'Back to Studies',exact:true}).click();await page.getByRole('button',{name:'Rename',exact:true}).click();await page.getByLabel('Title',{exact:true}).fill('denied');await page.getByRole('button',{name:'Save',exact:true}).click();await expect.poll(()=>!!release).toBe(true);await reviewTabRename(page,2,'newer inactive secret');const reply=page.waitForResponse('**/title');release();await reply;await expect(page.getByRole('alert').first()).toContainText('access is unavailable');options.failRename=0;await page.getByRole('button',{name:'Retry',exact:true}).click();await expect(page.getByText('newer inactive secret',{exact:true})).toHaveCount(0);
});
for(const operation of ['title','collection'])for(const status of [401,403])test(`review tabs B10 closed-origin ${operation} ${status} retains safe account recovery without tool or focus takeover`,async({page})=>{
 let release;const options=operation==='title'?{beforeRename:()=>new Promise(resolve=>release=resolve),failRename:status}:{beforePassagePut:()=>new Promise(resolve=>release=resolve),failPassages:status};await setup(page,options);await firstNote(page);await reviewTabAdd(page);await reviewTabRename(page,2,'survivor private label');await page.getByRole('tablist',{name:'Workspace tabs'}).getByRole('tab').first().click();await page.getByRole('button',{name:'Back to Studies',exact:true}).click();if(operation==='title'){await page.getByRole('button',{name:'Rename',exact:true}).click();await page.getByLabel('Title',{exact:true}).fill('pending title');await page.getByRole('button',{name:'Save',exact:true}).click();}else await addReference(page,'Genesis 1');await expect.poll(()=>!!release).toBe(true);await page.getByRole('button',{name:'Close tab 1',exact:true}).click();const survivor=page.getByRole('tablist',{name:'Workspace tabs'}).getByRole('tab');await survivor.focus();const response=page.waitForResponse(operation==='title'?'**/title':'**/passages');release();await response;await expect(page.getByRole('button',{name:'Retry account access',exact:true})).toBeVisible();await expect(survivor).toBeFocused();await expect(page.getByRole('button',{name:'Studies',exact:true})).toHaveAttribute('aria-pressed','false');await expect(page.getByText('survivor private label',{exact:true})).toHaveCount(0);if(status===401){await page.route('**/auth/v1/token*',r=>r.fulfill({json:{...session,access_token:'renewed-current'}}));await page.evaluate(async()=>{const {supabase}=await import('/src/lib/supabase.ts');await supabase.auth.signInWithPassword({email:'reader@example.invalid',password:'fixture'});});}options.failRename=0;options.failPassages=0;await page.getByRole('button',{name:'Retry account access',exact:true}).click();await expect(page.getByRole('button',{name:'Retry account access',exact:true})).toHaveCount(0);await expect(page.getByRole('button',{name:'Studies',exact:true})).toHaveAttribute('aria-pressed','false');await expect(page.getByText('survivor private label',{exact:true})).toHaveCount(status===401?1:0);
});
test('review tabs B6 masked Rename is disabled with a reason while anonymous and authorized Rename remain usable',async({page})=>{
 const options={failPut:401};await setup(page,options);await firstNote(page);await reviewTabRename(page,1,'authorized label');await page.getByRole('textbox',{name:'Note text',exact:true}).fill('mask');await expect(page.getByRole('alert')).toContainText('Sign in');const button=page.getByRole('button',{name:'Rename tab 1',exact:true});await expect(button).toBeDisabled();await expect(button).toHaveAccessibleDescription(/Sign in|access/i);
});
test('review tabs E1 sole conflicted note reopens latest only after guarded consent',async({page})=>{
 const options={failPut:409};const {advanceNote}=await setup(page,options);await firstNote(page);await page.getByRole('textbox',{name:'Note text',exact:true}).fill('my conflicting input');await expect(page.getByRole('alert')).toContainText('This note has changed');advanceNote({document:{version:1,blocks:[{type:'paragraph',direction:'auto',content:[{type:'text',text:'latest server value',marks:[]}]}]},connections:[],highlights:[]});await page.getByRole('button',{name:'Back to Studies',exact:true}).click();await page.getByRole('list',{name:'Notes',exact:true}).getByRole('button').first().click();const dialog=page.getByRole('dialog',{name:'Changes not saved'});await expect(dialog).toBeVisible();await dialog.getByRole('button',{name:'Stay',exact:true}).click();await page.getByRole('list',{name:'Notes',exact:true}).getByRole('button').first().click();await dialog.getByRole('button',{name:'Switch anyway',exact:true}).click();await expect(page.getByRole('textbox',{name:'Note text',exact:true})).toHaveText('latest server value');
});
test('review tabs B4 delayed Edit mode restore cannot change selection in another exposed note host',async({page})=>{
 await reviewTwoNotes(page);const tabs=page.getByRole('tablist',{name:'Workspace tabs'}).getByRole('tab');await tabs.first().click();const editor=page.getByRole('textbox',{name:'Note text',exact:true});await editor.evaluate(el=>{el.focus();const r=document.createRange();r.selectNodeContents(el);getSelection().removeAllRanges();getSelection().addRange(r);});await page.getByRole('button',{name:'Read note',exact:true}).click();await page.evaluate(()=>{window.modeRestore=[];window.originalTimeout=window.setTimeout;window.setTimeout=(callback,delay,...args)=>{if(delay===0){window.modeRestore.push(()=>callback(...args));return 987654;}return window.originalTimeout(callback,delay,...args);};});await page.getByRole('button',{name:'Edit note',exact:true}).click();await tabs.nth(1).click();await editor.focus();await editor.evaluate(el=>{const r=document.createRange();r.selectNodeContents(el);r.collapse(false);getSelection().removeAllRanges();getSelection().addRange(r);window.selectedOther=r.endContainer;window.selectedOffset=r.endOffset;});await page.evaluate(()=>{window.setTimeout=window.originalTimeout;window.modeRestore.splice(0).forEach(fn=>fn());});expect(await editor.evaluate(el=>{const r=getSelection().getRangeAt(0);return el.contains(r.startContainer)&&r.endContainer===window.selectedOther&&r.endOffset===window.selectedOffset;})).toBe(true);await expect(editor).toBeFocused();
});
for(const state of ['failed','composing'])test(`review tabs V1 sign-out guards ${state} background input while the active retained note is saved`,async({page})=>{
 await reviewTwoNotes(page);const tabs=page.getByRole('tablist',{name:'Workspace tabs'}).getByRole('tab');await tabs.first().click();const editor=page.getByRole('textbox',{name:'Note text',exact:true});if(state==='failed')await page.route('**/api/studies/*/notes/*',r=>r.request().method()==='PUT'?r.fulfill({status:503,json:{code:'studies_storage_unavailable'}}):r.fallback());else await editor.dispatchEvent('compositionstart');await editor.fill('background private '+state);if(state==='failed')await expect(page.getByRole('status').filter({hasText:'Changes not saved'})).toBeVisible();await tabs.nth(1).click();await expect(editor).toHaveText('A second');await page.getByRole('button',{name:'Sign out',exact:true}).click();const prompt=page.getByRole('dialog',{name:'Changes not saved'});await expect(prompt).toBeVisible();await prompt.getByRole('button',{name:'Stay',exact:true}).click();await tabs.first().click();await expect(editor).toHaveText('background private '+state);
});
test('review tabs V1 sequential account consent is non-destructive when the second unresolved lane stays',async({page})=>{
 await reviewTwoNotes(page);await page.route('**/api/studies/*/notes/*',r=>r.request().method()==='PUT'?r.fulfill({status:503,json:{code:'studies_storage_unavailable'}}):r.fallback());const tabs=page.getByRole('tablist',{name:'Workspace tabs'}).getByRole('tab'),editor=page.getByRole('textbox',{name:'Note text',exact:true});await editor.fill('lane B unresolved');await expect(page.getByRole('status').filter({hasText:'Changes not saved'})).toBeVisible();await tabs.first().click();await editor.fill('lane A unresolved');await expect(page.getByRole('status').filter({hasText:'Changes not saved'})).toBeVisible();await page.getByRole('button',{name:'Sign out',exact:true}).click();const prompt=page.getByRole('dialog',{name:'Changes not saved'});await prompt.getByRole('button',{name:'Close anyway',exact:true}).click();await expect(prompt).toBeVisible();await prompt.getByRole('button',{name:'Stay',exact:true}).click();await expect(editor).toHaveText('lane A unresolved');await tabs.nth(1).click();await expect(editor).toHaveText('lane B unresolved');await tabs.first().click();await page.getByRole('button',{name:'Sign out',exact:true}).click();await prompt.getByRole('button',{name:'Close anyway',exact:true}).click();await prompt.getByRole('button',{name:'Close anyway',exact:true}).click();await expect(page.getByRole('button',{name:'Sign out',exact:true})).toHaveCount(0);
});

test('review tabs B3 word scroll survives hidden Notes scrolling without focus restoration',async({page})=>{
 await setup(page,{noteValue:{document:{version:1,blocks:Array.from({length:100},(_,i)=>({type:'paragraph',direction:'auto',content:[{type:'text',text:'Long note '+i+' content',marks:[]}]}))},connections:[],highlights:[]}});await page.route('**/api/bible/words/**',r=>r.fulfill({json:{id:1,position:1,surface_he:'בְּרֵאשִׁית',display_he:'בְּרֵאשִׁית',lemma_strong:'4428',lexical_id:'4428',morph_code:null,morphemes:[]}}));await page.route('**/api/bible/lexicon/**',r=>r.fulfill({json:{status:'available',lexical_id:'4428',lemma:'king',bdb:[{kind:'text',text:'Long definition '.repeat(300)}]}}));await firstNote(page);if(page.viewportSize().width<768)await page.getByRole('button',{name:'Return to reader',exact:true}).click();await page.getByRole('button',{name:/Word: בְּרֵאשִׁית/}).click();await page.getByRole('button',{name:'Show more',exact:true}).click();const surface=page.getByRole('complementary',{name:'Study tools',exact:true});const position=await surface.evaluate(el=>{el.scrollTop=230;return el.scrollTop;});expect(position).toBeGreaterThan(100);await page.waitForTimeout(80);await page.getByRole('tab',{name:'Notes',exact:true}).evaluate(el=>el.focus({preventScroll:true}));await page.keyboard.press('Enter');await surface.evaluate(el=>el.scrollTop=600);await page.waitForTimeout(80);const word=page.getByRole('tab',{name:'Word',exact:true});await word.evaluate(el=>el.focus({preventScroll:true}));await page.keyboard.press('Enter');await expect(word).toBeFocused();await expect.poll(async()=>Math.abs(await surface.evaluate(el=>el.scrollTop)-position)).toBeLessThan(3);
});
test('review tabs E3 distinct long note contexts restore their own inspector scroll without focus theft',async({page})=>{
 let releaseSecond;
 const {otherNote}=await reviewLibrary(page,{read:async(parent,id,view)=>{
  // Hold the second note read so an outline click cannot masquerade as editor readiness.
  if(id!==note)await new Promise(resolve=>releaseSecond=resolve);
  return {...view(parent,id,'long note'),value:{document:{version:1,blocks:Array.from({length:120},(_,i)=>({type:'paragraph',direction:'auto',content:[{type:'text',text:id+' paragraph '+i,marks:[]}]}))},connections:[],highlights:[]}};
 }});
 await page.getByRole('button',{name:'Study A',exact:true}).click();
 await page.getByRole('button',{name:'A first',exact:true}).click();
 const editor=page.getByRole('textbox',{name:'Note text',exact:true});
 await expect(editor.locator('p').first()).toHaveText(note+' paragraph 0');
 const surface=page.getByRole('complementary',{name:'Study tools',exact:true});
 const a=await surface.evaluate(el=>{el.scrollTop=220;return el.scrollTop;});
 expect(a).toBe(220);
 await page.waitForTimeout(80);
 await reviewTabAdd(page);
 await page.getByRole('button',{name:'Studies',exact:true}).click();
 await page.getByRole('button',{name:'A second',exact:true}).click();
 await expect.poll(()=>!!releaseSecond).toBe(true);
 await expect(editor).toHaveCount(0);
 releaseSecond();
 await expect(editor.locator('p').first()).toHaveText(otherNote+' paragraph 0');
 const b=await surface.evaluate(el=>{el.scrollTop=650;return el.scrollTop;});
 expect(b).toBe(650);
 await page.waitForTimeout(80);
 const tabs=page.getByRole('tablist',{name:'Workspace tabs'}).getByRole('tab');
 await tabs.first().click();
 await expect(tabs.first()).toBeFocused();
 await expect.poll(async()=>Math.abs(await surface.evaluate(el=>el.scrollTop)-a)).toBeLessThan(3);
 await tabs.nth(1).click();
 await expect(tabs.nth(1)).toBeFocused();
 await expect.poll(async()=>Math.abs(await surface.evaluate(el=>el.scrollTop)-b)).toBeLessThan(3);
});

test('review tabs V1 sign-out rechecks saved background lanes receiving late composition during consent',async({page})=>{
 await reviewTwoNotes(page);const tabs=page.getByRole('tablist',{name:'Workspace tabs'}).getByRole('tab'),editor=page.getByRole('textbox',{name:'Note text',exact:true});await tabs.first().click();await editor.evaluate(el=>window.lateBackgroundEditor=el);await tabs.nth(1).click();await page.route('**/api/studies/*/notes/*',r=>r.request().method()==='PUT'?r.fulfill({status:503,json:{code:'studies_storage_unavailable'}}):r.fallback());await editor.fill('B needs consent');await expect(page.getByRole('status').filter({hasText:'Changes not saved'})).toBeVisible();await page.getByRole('button',{name:'Sign out',exact:true}).click();const prompt=page.getByRole('dialog',{name:'Changes not saved'});await expect(prompt).toBeVisible();await page.evaluate(()=>{const el=window.lateBackgroundEditor;el.dispatchEvent(new CompositionEvent('compositionstart',{bubbles:true}));el.textContent='A late composition';el.dispatchEvent(new InputEvent('input',{bubbles:true,isComposing:true}));});await prompt.getByRole('button',{name:'Close anyway',exact:true}).click();await expect(prompt).toBeVisible();await prompt.getByRole('button',{name:'Stay',exact:true}).click();await expect(page.getByRole('button',{name:'Sign out',exact:true})).toBeVisible();await tabs.first().click();await expect(editor).toHaveText('A late composition');
});
test('review tabs E1 shared conflicted lane cannot be replaced by reopening from another live context',async({page})=>{
 const {requests}=await setup(page,{failPut:409});await firstNote(page);await reviewTabAdd(page);const editor=page.getByRole('textbox',{name:'Note text',exact:true});await page.getByRole('button',{name:'Analysis',exact:true}).click();await editor.fill('shared conflicting input');await expect(page.getByRole('alert')).toContainText('This note has changed');const reads=requests.filter(r=>r.path.endsWith('/notes/'+note)&&r.method==='GET').length;await page.getByRole('button',{name:'Back to Studies',exact:true}).click();await page.getByRole('list',{name:'Notes',exact:true}).getByRole('button').first().click();await expect(page.getByRole('dialog',{name:'Changes not saved'})).toHaveCount(0);await page.getByRole('button',{name:'Analysis',exact:true}).click();await expect(editor).toHaveText('shared conflicting input');expect(requests.filter(r=>r.path.endsWith('/notes/'+note)&&r.method==='GET')).toHaveLength(reads);
});
