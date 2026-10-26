# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: personal-notes.spec.cjs >> review tabs B10 closed-origin title 401 retains safe account recovery without tool or focus takeover
- Location: tests/personal-notes.spec.cjs:1459:77

# Error details

```
Error: page.goto: Test ended.
Call log:
  - navigating to "http://127.0.0.1:5182/", waiting until "load"

```

# Test source

```ts
  58  |  await page.route('**/api/bible/**',r=>{const path=new URL(r.request().url()).pathname;const b={id:1,osis_id:'Gen',name_en:'Genesis',name_he:'בראשית',testament:'OT',book_order:1};const w={id:1,position:1,surface_he:'בְּרֵאשִׁית',display_he:'בְּרֵאשִׁית',lemma_strong:null,morph_code:null};return r.fulfill({json:path.endsWith('/books')?{data:[b],total:1}:path.endsWith('/books/Gen')?{...b,chapters:[{id:1,chapter_num:1}]}:path.includes('/words/')?{...w,morphemes:[]}:{data:[{id:1,verse_num:1,book_id:1,chapter_num:1,words:[w]}],total:1}});});
  59  |  const collection={study_id:study,revision:'1',items:[]};
  60  |  const metadata={title:'Untitled study',revision:'1'};
  61  |  let saved={document:{version:1,blocks:[]},connections:[],highlights:[]},created=false,noteCreated=false,revision='1',requests=[],operations=new Map();
  62  |  await page.route('**/api/operations/**',async r=>{if(options.beforeLookup)await options.beforeLookup();const id=new URL(r.request().url()).pathname.split('/').pop();return r.fulfill({json:options.unresolved?{status:'unresolved'}:operations.has(id)?{status:'committed',outcome:operations.get(id)}:{status:'unresolved'}});});
  63  |  await page.route('**/api/studies**',async r=>{
  64  |   const req=r.request(),url=new URL(req.url()),path=url.pathname,method=req.method(),payload=req.postDataJSON();requests.push({path,method,payload});
  65  |   let data;
  66  |   if(path.endsWith('/context-notes')){data={items:[],next_cursor:null};}
  67  |   else if(path.endsWith('/'+study)&&method==='PUT'){metadata.title=payload.title;metadata.introduction=payload.introduction;metadata.source_url=payload.source_url;metadata.revision=String(Number(metadata.revision)+1);data={operation_id:payload.operation_id,command:'study.details.replace',study_id:study,note_id:null,revision:metadata.revision};}
  68  |   else if(path.endsWith('/search')){if(options.search)return options.search(r,payload);data={items:created?[{...attribution,id:study,title:metadata.title,revision:metadata.revision}]:[],next_cursor:null};}
  69  |   else if(path.endsWith('/enrollment'))data={operation_id:payload.operation_id,status:'committed',result:{disposition:'created',account_id:account,actor_id:actor,permission:'scribeswell.studies.use'}};
  70  |   else if(path.endsWith('/passages')){
  71  |    if(method==='GET'){
  72  |     if(options.beforePassageRead)await options.beforePassageRead();
  73  |     if(options.failPassageRead)return r.fulfill({status:503,json:{code:'studies_storage_unavailable'}});
  74  |     data=collection;
  75  |    }else{
  76  |     if(options.beforePassagePut)await options.beforePassagePut();
  77  |     if(options.failPassages)return r.fulfill({status:options.failPassages,json:{code:options.failPassages===409?'passage_revision_conflict':options.failPassages===400?'scribeswell_personal_notes_input_invalid':options.failPassages===401?'authentication_required':options.failPassages===403?'studies_access_denied':options.failPassages===404?'resource_unavailable':'studies_storage_unavailable'}});
  78  |     if(operations.has(payload.operation_id))data=operations.get(payload.operation_id);
  79  |     else{if(payload.expected_revision!==collection.revision)return r.fulfill({status:409,json:{code:'passage_revision_conflict'}});if(JSON.stringify(payload.items)!==JSON.stringify(collection.items)){collection.items=payload.items;collection.revision=String(Number(collection.revision)+1);}data={operation_id:payload.operation_id,command:'study.passages.replace',study_id:study,note_id:null,revision:collection.revision};operations.set(payload.operation_id,data);}
  80  |     if(options.afterPassageCommit)options.afterPassageCommit();
  81  |     if(options.dropPassages){options.dropPassages=false;return r.abort('connectionreset');}
  82  |    }
  83  |   }
  84  |   else if(path.endsWith('/title')&&method==='PUT'){
  85  |    if(options.beforeRename)await options.beforeRename();
  86  |    if(options.failRename)return r.fulfill({status:options.failRename,json:{code:options.failRename===409?'study_revision_conflict':options.failRename===400?'scribeswell_personal_notes_input_invalid':options.failRename===401?'authentication_required':options.failRename===403?'studies_access_denied':'studies_storage_unavailable'}});
  87  |    if(operations.has(payload.operation_id))data=operations.get(payload.operation_id);
  88  |    else{if(metadata.title!==payload.title){metadata.title=payload.title;metadata.revision=String(Number(metadata.revision)+1);}data={operation_id:payload.operation_id,command:'study.rename',study_id:study,note_id:null,revision:metadata.revision};operations.set(payload.operation_id,data);}
  89  |    if(options.dropRename){options.dropRename=false;return r.abort('connectionreset');}
  90  |   }
  91  |   else if(path.endsWith('/'+study)&&method==='DELETE'){
  92  |    if(options.beforeStudyDelete)await options.beforeStudyDelete();
  93  |    if(options.failStudyDelete)return r.fulfill({status:options.failStudyDelete,json:{code:options.failStudyDeleteCode??(options.failStudyDelete===409?'study_revision_conflict':options.failStudyDelete===401?'authentication_required':options.failStudyDelete===403?'studies_access_denied':'studies_storage_unavailable')}});
  94  |    if(operations.has(payload.operation_id))data=operations.get(payload.operation_id);
  95  |    else{if(payload.expected_revision!==metadata.revision)return r.fulfill({status:409,json:{code:'study_revision_conflict'}});metadata.revision=String(Number(metadata.revision)+1);metadata.title='Deleted study';created=false;noteCreated=false;saved={document:{version:1,blocks:[]},connections:[],highlights:[]};collection.items=[];data={operation_id:payload.operation_id,command:'study.delete',study_id:study,note_id:null,revision:metadata.revision};operations.set(payload.operation_id,data);}
  96  |    if(options.dropStudyDelete){options.dropStudyDelete=false;return r.abort('connectionreset');}
  97  |   }
  98  |   else if(path.endsWith('/notes/'+note)&&method==='DELETE'){
  99  |    if(options.beforeDelete)await options.beforeDelete();
  100 |    if(options.failDelete)return r.fulfill({status:options.failDelete,json:{code:options.failDeleteCode??(options.failDelete===409?'note_revision_conflict':options.failDelete===401?'authentication_required':options.failDelete===403?'studies_access_denied':'studies_storage_unavailable')}});
  101 |    if(operations.has(payload.operation_id))data=operations.get(payload.operation_id);
  102 |    else{if(payload.expected_revision!==revision)return r.fulfill({status:409,json:{code:'note_revision_conflict'}});revision=String(Number(revision)+1);saved={document:{version:1,blocks:[]},connections:[],highlights:[]};noteCreated=false;data={operation_id:payload.operation_id,command:'note.delete',study_id:study,note_id:note,revision};operations.set(payload.operation_id,data);}
  103 |    if(options.dropDelete){options.dropDelete=false;return r.abort('connectionreset');}
  104 |   }
  105 |   else if(path.endsWith('/notes/'+note)&&method==='PUT'){if(options.beforePut)await options.beforePut();if(options.failPut)return r.fulfill({status:options.failPut,json:{code:options.failPutCode??(options.failPut===409?'note_revision_conflict':options.failPut===401?'authentication_required':options.failPut===403?'studies_access_denied':'studies_storage_unavailable')}});saved=payload.value;revision=String(Number(revision)+1);data={operation_id:payload.operation_id,command:'note.replace',study_id:study,note_id:note,revision};}
  106 |   else if(path.endsWith('/notes/'+note))data={...attribution,id:note,study_id:study,visibility:'study',value:saved,revision};
  107 |   else if(path.endsWith('/notes')&&method==='POST'){noteCreated=true;saved=options.noteValue??payload.value;data={operation_id:payload.operation_id,command:'note.create',study_id:study,note_id:note,revision};}
  108 |   else if(path.endsWith('/notes'))data={items:noteCreated?[{...attribution,id:note,study_id:study,visibility:'study',value:saved,revision}]:[],next_cursor:null};
  109 |   else if(method==='POST'){created=true;data={operation_id:payload.operation_id,command:'study.create',study_id:study,note_id:null,revision:'1'};}
  110 |   else if(path.endsWith('/'+study)){if(options.beforeStudyRead)await options.beforeStudyRead();data={...attribution,id:study,...metadata};}
  111 |   else data={items:created?[{...attribution,id:study,title:metadata.title,revision:metadata.revision}]:[],next_cursor:null};
  112 |   if(data.command)operations.set(data.operation_id,data);
  113 |   if(method==='PUT'&&options.dropPut){options.dropPut=false;return r.abort('connectionreset');}
  114 |   return r.fulfill({json:data,headers:{'cache-control':'private, no-store'}});
  115 |  });return {requests,metadata,collection,advanceNote:(value)=>{saved=value;revision=String(Number(revision)+1);}};
  116 | }
  117 | // Reload exercises the real device return: wait for acknowledged metadata, then
  118 | // current authorized hydration before any tool click can supersede that return.
  119 | async function waitForWorkspaceCheckpoint(page,{studyId=study,noteId=note,studySelected=true}={}){
  120 |  await expect(page.getByRole('tablist',{name:'Workspace tabs'})).toHaveAttribute('data-device-ready','true');
  121 |  await expect.poll(()=>page.evaluate(async({account,studyId,noteId,studySelected})=>{
  122 |   const {readWorkspace}=await import('/src/lib/workspace-storage.ts');
  123 |   const saved=await readWorkspace(account),key=document.querySelector('[data-workspace-tab][aria-selected="true"]')?.getAttribute('data-workspace-tab');
  124 |   const tab=saved.public?.tabs.find(tab=>tab.tabKey===key);
  125 |   if(!tab||saved.public.activeTabKey!==key)return false;
  126 |   const snapshot=history.state?.usr?.scribeswellReader;
  127 |   if(snapshot?.tabKey===key&&(tab.activePaneKey!==snapshot.activePaneKey||JSON.stringify(tab.panes.map(p=>[p.paneKey,p.ref]))!==JSON.stringify(snapshot.panes.map(p=>[p.paneKey,p.ref]))))return false;
  128 |   if(!studySelected)return true;
  129 |   const selected=saved.private?.tabs.find(row=>row.tabKey===key&&row.incarnation===tab.incarnation);
  130 |   return selected?.study===studyId&&(noteId===null?selected.note===undefined:selected.note===noteId);
  131 |  },{account,studyId,noteId,studySelected})).toBe(true);
  132 | }
  133 | async function reloadRememberedWorkspace(page,{title='Untitled study',studyId=study,noteId=note,studySelected=true}={}){
  134 |  await waitForWorkspaceCheckpoint(page,{studyId,noteId,studySelected});
  135 |  await page.reload();
  136 |  await expect(page.getByRole('tablist',{name:'Workspace tabs'})).toHaveAttribute('data-device-ready','true');
  137 |  if(studySelected){
  138 |   await expect(page.getByRole('navigation',{name:'Reader tools'})).toContainText(title);
  139 |   if(noteId!==null)await expect(page.locator('[aria-label="Note text"]')).toHaveCount(1);
  140 |  }
  141 | }
  142 | 
  143 | test('explicitly enroll, create, write Hebrew and reopen saved text after reload',async({page})=>{
  144 |  const {requests}=await setup(page);await page.goto('/');expect(requests).toHaveLength(0);
  145 |  await page.getByRole('button',{name:'Studies',exact:true}).click();
  146 |  await page.getByRole('button',{name:'Start a study',exact:true}).click();
  147 |  await page.getByRole('button',{name:'Create study',exact:true}).click();
  148 |  await expect(page.getByRole('heading',{name:'Untitled study',exact:true})).toBeVisible();
  149 |  await page.getByRole('button',{name:'Add note',exact:true}).click();
  150 |  await page.getByLabel('Note text',{exact:true}).fill('בְּרֵאשִׁית — personal observation');
  151 |  await expect(page.getByRole('status').filter({hasText:'Draft saved'})).toBeVisible();
  152 |  await reloadRememberedWorkspace(page);await page.getByRole('button',{name:'Studies',exact:true}).click();
  153 |  await page.getByRole('button',{name:/personal observation/}).click();
  154 |  await expect(page.getByLabel('Note text',{exact:true})).toContainText('בְּרֵאשִׁית — personal observation');
  155 |  expect(requests.filter(r=>r.path.endsWith('/enrollment'))).toHaveLength(1);
  156 | });
  157 | 
> 158 | async function firstNote(page){await page.goto('/');await expect(page.getByRole('tablist',{name:'Workspace tabs'})).toHaveAttribute('data-device-ready','true');await page.getByRole('button',{name:'Studies',exact:true}).click();await page.getByRole('button',{name:'Start a study',exact:true}).click();await page.getByRole('button',{name:'Create study',exact:true}).click();await page.getByRole('button',{name:'Add note',exact:true}).click();await expect(page.getByLabel('Note text',{exact:true})).toBeVisible();}
      |                                           ^ Error: page.goto: Test ended.
  159 | test('failed saves use inline Retry and exit-only Stay / Close anyway',async({page})=>{
  160 |  const options={failPut:503};await setup(page,options);await firstNote(page);await page.getByLabel('Note text',{exact:true}).fill('Unsaved Hebrew שָׁלוֹם');await expect(page.getByRole('status').filter({hasText:'Changes not saved'})).toBeVisible();await expect(page.getByRole('button',{name:'Keep editing'})).toHaveCount(0);await expect(page.getByRole('dialog')).toHaveCount(0);
  161 |  await page.getByRole('button',{name:'Sign out',exact:true}).click();await expect(page.getByRole('dialog',{name:'Changes not saved'})).toBeVisible();await page.getByRole('button',{name:'Stay',exact:true}).click();await expect(page.getByLabel('Note text',{exact:true})).toContainText('שָׁלוֹם');options.failPut=0;await page.getByRole('button',{name:'Retry',exact:true}).click();await expect(page.getByRole('status').filter({hasText:'Draft saved'})).toBeVisible();await page.getByRole('button',{name:'Sign out',exact:true}).click();await expect(page.getByRole('dialog',{name:'Changes not saved'})).toHaveCount(0);
  162 | });
  163 | test('delayed old acknowledgement cannot mark newer text saved',async({page})=>{
  164 |  let release;const options={beforePut:()=>new Promise(resolve=>release=resolve)};const {requests}=await setup(page,options);await firstNote(page);const editor=page.getByLabel('Note text',{exact:true});await editor.fill('first');await expect.poll(()=>Boolean(release)).toBe(true);await editor.fill('newer שָׁלוֹם');await expect(page.getByRole('status')).not.toHaveText('Draft saved');expect(requests.filter(r=>r.method==='PUT')).toHaveLength(1);options.beforePut=undefined;release();await expect(page.getByRole('status').filter({hasText:'Draft saved'})).toBeVisible();expect(requests.filter(r=>r.method==='PUT')).toHaveLength(2);await expect(editor).toContainText('newer שָׁלוֹם');
  165 | });
  166 | test('composition defers autosave until IME completion',async({page})=>{
  167 |  const {requests}=await setup(page);await firstNote(page);const editor=page.getByLabel('Note text',{exact:true});await editor.dispatchEvent('compositionstart');await editor.fill('עברית');await page.waitForTimeout(700);expect(requests.filter(r=>r.method==='PUT')).toHaveLength(0);await editor.dispatchEvent('compositionend');await expect.poll(()=>requests.filter(r=>r.method==='PUT').length).toBe(1);await expect(page.getByRole('status').filter({hasText:'Draft saved'})).toBeVisible();
  168 | });
  169 | for(const replacementToken of ['current','other-account'])test(`account replacement discards prior private UI and late saves (${replacementToken})`,async({page})=>{
  170 |  let release;await setup(page,{beforePut:()=>new Promise(resolve=>release=resolve)});await firstNote(page);await reviewTabRename(page,1,'Prior account private label');await page.getByLabel('Note text',{exact:true}).fill('prior-account private text');await expect.poll(()=>Boolean(release)).toBe(true);
  171 |  await page.route('**/auth/v1/token*',r=>r.fulfill({json:{...session,access_token:replacementToken,user:{...session.user,id:'10000000-0000-4000-8000-000000000002'}}}));
  172 |  await page.evaluate(async()=>{const {supabase}=await import('/src/lib/supabase.ts');await supabase.auth.signOut({scope:'local'});await supabase.auth.signInWithPassword({email:'other@example.invalid',password:'fixture'});});
  173 |  await expect(page.getByLabel('Note text',{exact:true})).toHaveCount(0);await expect(page.getByText('Prior account private label',{exact:true})).toHaveCount(0);release();await expect(page.getByText('prior-account private text')).toHaveCount(0);await expect(page.getByRole('button',{name:'Studies',exact:true})).toBeVisible();
  174 | });
  175 | test('native PostgreSQL browser reload returns the acknowledged aggregate',async({page})=>{
  176 |  test.skip(!process.env.SCRIBESWELL_NOTES_NATIVE_API,'Explicit owned native API fixture required');
  177 |  await setup(page);await page.unroute('**/api/studies**');const acknowledgements=[];
  178 |  for(const pattern of ['**/api/studies**','**/api/operations/**'])await page.route(pattern,async r=>{const target=process.env.SCRIBESWELL_NOTES_NATIVE_API+new URL(r.request().url()).pathname+new URL(r.request().url()).search;const response=await r.fetch({url:target});if(r.request().method()==='POST'){const result=await response.json();if(['study.create','note.create'].includes(result.command))acknowledgements.push(result);}await r.fulfill({response});});
  179 |  await firstNote(page);await page.getByLabel('Note text',{exact:true}).fill('Native persisted בְּרֵאשִׁית');await expect(page.getByRole('status').filter({hasText:'Draft saved'})).toBeVisible();
  180 |  const createdStudy=acknowledgements.find(result=>result.command==='study.create'),createdNote=acknowledgements.find(result=>result.command==='note.create');expect(createdStudy?.study_id).toMatch(/^[0-9a-f-]{36}$/);expect(createdNote?.study_id).toBe(createdStudy.study_id);expect(createdNote?.note_id).toMatch(/^[0-9a-f-]{36}$/);console.log('NATIVE_FIXTURE_ACK_IDS',JSON.stringify({study_id:createdStudy.study_id,note_id:createdNote.note_id,stub_study:study,stub_note:note}));
  181 |  await reloadRememberedWorkspace(page,{studyId:createdStudy.study_id,noteId:createdNote.note_id});await page.getByRole('button',{name:'Studies',exact:true}).click();await page.getByRole('button',{name:'Native persisted בְּרֵאשִׁית',exact:true}).click();await expect(page.getByLabel('Note text',{exact:true})).toContainText('Native persisted בְּרֵאשִׁית');
  182 |  // Drain actual API callbacks before Playwright tears down their request context.
  183 |  await page.unrouteAll({behavior:'wait'});
  184 | });
  185 | 
  186 | test('unknown response blocks newer snapshots and recovers the original operation',async({page})=>{
  187 |  let release;const options={dropPut:true,beforeLookup:()=>new Promise(resolve=>release=resolve)};const {requests}=await setup(page,options);await firstNote(page);const editor=page.getByLabel('Note text',{exact:true});await editor.fill('first unknown');await expect.poll(()=>Boolean(release)).toBe(true);await editor.fill('later snapshot');await page.waitForTimeout(700);expect(requests.filter(r=>r.method==='PUT')).toHaveLength(1);options.beforeLookup=undefined;release();await expect(page.getByRole('status').filter({hasText:'Draft saved'})).toBeVisible();expect(requests.filter(r=>r.method==='PUT')).toHaveLength(2);
  188 | });
  189 | test('revision conflict preserves input and guards study switching',async({page})=>{
  190 |  await setup(page,{failPut:409});await firstNote(page);await page.getByLabel('Note text',{exact:true}).fill('mine conflicts');await expect(page.getByRole('alert')).toContainText('This note has changed');await page.getByRole('button',{name:'Back to Studies',exact:true}).click();await page.getByRole('button',{name:'Leave study',exact:true}).click();await expect(page.getByRole('dialog',{name:'Changes not saved'})).toBeVisible();await expect(page.getByRole('button',{name:'Switch anyway',exact:true})).toBeVisible();await page.getByRole('button',{name:'Stay',exact:true}).click();await page.getByRole('button',{name:'Analysis',exact:true}).click();await expect(page.getByLabel('Note text',{exact:true})).toContainText('mine conflicts');
  191 | });
  192 | test('same-account reauthentication preserves input and requires explicit retry',async({page})=>{
  193 |  const options={failPut:401};const {requests}=await setup(page,options);await firstNote(page);await page.getByLabel('Note text',{exact:true}).fill('recoverable current input');await expect(page.getByRole('alert')).toContainText('Sign in');await expect(page.getByLabel('Note text',{exact:true})).toHaveCount(0);const count=requests.filter(r=>r.method==='PUT').length;
  194 |  await page.route('**/auth/v1/token*',r=>r.fulfill({json:{...session,access_token:'renewed-current'}}));await page.evaluate(async()=>{const {supabase}=await import('/src/lib/supabase.ts');await supabase.auth.signInWithPassword({email:'reader@example.invalid',password:'fixture'});});options.failPut=0;
  195 |  await page.getByRole('button',{name:'Retry Studies',exact:true}).click();await expect(page.getByLabel('Note text',{exact:true})).toContainText('recoverable current input');expect(requests.filter(r=>r.method==='PUT')).toHaveLength(count);await page.getByRole('button',{name:'Retry',exact:true}).click();await expect(page.getByRole('status').filter({hasText:'Draft saved'})).toBeVisible();
  196 | });
  197 | test('rich paragraphs directions lists marks and safe links survive saving and reopening',async({page})=>{
  198 |  const {requests}=await setup(page);await firstNote(page);const editor=page.getByLabel('Note text',{exact:true});await editor.evaluate(el=>{el.replaceChildren();const p=document.createElement('p');p.dir='rtl';const bold=document.createElement('strong');bold.textContent='שָׁלוֹם';p.append(bold);const link=document.createElement('a');link.href='https://example.org/source';link.textContent=' source';p.append(link);const list=document.createElement('ol');const li=document.createElement('li');const i=document.createElement('em');i.textContent='Second paragraph';li.append(i);list.append(li);el.append(p,list);el.dispatchEvent(new InputEvent('input',{bubbles:true}));});await expect(page.getByRole('status').filter({hasText:'Draft saved'})).toBeVisible();const saved=requests.filter(r=>r.method==='PUT').at(-1).payload.value;expect(saved.document.blocks[0].direction).toBe('rtl');expect(saved.document.blocks[0].content[0].marks).toEqual(['bold']);expect(saved.document.blocks[1].style).toBe('ordered');
  199 |  await reloadRememberedWorkspace(page);await page.getByRole('button',{name:'Studies',exact:true}).click();await page.getByRole('button',{name:/Second paragraph/}).click();await expect(editor.locator('strong')).toHaveText('שָׁלוֹם');await expect(editor.locator('ol li em')).toHaveText('Second paragraph');await expect(editor.locator('a')).toHaveAttribute('rel','noopener noreferrer');
  200 | });
  201 | test('editor toolbar actions persist direction marks lists and safe links',async({page})=>{
  202 |  const {requests}=await setup(page);await firstNote(page);const editor=page.getByLabel('Note text',{exact:true});await editor.fill('שָׁלוֹם');await editor.press('ControlOrMeta+A');await page.getByRole('button',{name:'Bold',exact:true}).click();await page.getByLabel('Paragraph direction').selectOption('rtl');await editor.press('ControlOrMeta+End');await editor.press('Enter');await editor.press('ControlOrMeta+B');await editor.press('ControlOrMeta+I');await editor.pressSequentially('Second paragraph source');await page.getByRole('button',{name:'Numbered list',exact:true}).click();await editor.press('ControlOrMeta+End');await editor.press('ControlOrMeta+Shift+ArrowLeft');await page.getByRole('button',{name:'Link',exact:true}).click();await page.getByLabel('Link URL',{exact:true}).fill('https://example.org/source');await page.getByRole('button',{name:'Insert link',exact:true}).click();await expect(page.getByRole('status').filter({hasText:'Draft saved'})).toBeVisible();
  203 |  const saved=requests.filter(r=>r.method==='PUT').at(-1).payload.value;expect(saved.document.blocks.some(b=>b.type==='paragraph'&&b.direction==='rtl')).toBe(true);expect(saved.document.blocks.some(b=>b.type==='list'&&b.style==='ordered')).toBe(true);expect(JSON.stringify(saved)).toContain('bold');expect(JSON.stringify(saved)).toContain('italic');expect(JSON.stringify(saved)).toContain('https://example.org/source');
  204 |  await reloadRememberedWorkspace(page);await page.getByRole('button',{name:'Studies',exact:true}).click();await page.getByRole('button',{name:/Second paragraph/}).click();await expect(editor.locator('ol')).toBeVisible();await expect(editor.locator('a')).toHaveAttribute('href','https://example.org/source');await expect(editor.locator('p[dir="rtl"]').filter({hasText:'שָׁלוֹם'})).toBeVisible();
  205 | });
  206 | 
  207 | test('word inspection and Notes return retain the shared edit lane',async({page,isMobile})=>{
  208 |  await setup(page);await firstNote(page);await page.getByLabel('Note text',{exact:true}).fill('Current note remains selected');if(isMobile||test.info().project.name==='mobile')await page.getByRole('button',{name:'Return to reader',exact:true}).click();await page.getByRole('button',{name:/Word:/}).first().click();await expect(page.getByRole('tab',{name:'Word',exact:true})).toBeVisible();await expect(page.getByRole('tab',{name:'Occurrences',exact:true})).toBeVisible();await page.getByRole('tab',{name:'Notes',exact:true}).click();await expect(page.getByLabel('Note text',{exact:true})).toContainText('Current note remains selected');expect(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth)).toBe(false);
  209 | });
  210 | test('unsupported current editor input stays unsaved and exit guarded until corrected',async({page})=>{
  211 |  await setup(page);await firstNote(page);const editor=page.getByLabel('Note text',{exact:true});await editor.evaluate(el=>{const table=document.createElement('table');table.textContent='Unsupported current input';el.replaceChildren(table);el.dispatchEvent(new InputEvent('input',{bubbles:true}));});await expect(page.getByRole('status')).toContainText('Changes not saved');await page.getByRole('button',{name:'Sign out',exact:true}).click();await expect(page.getByRole('dialog',{name:'Changes not saved'})).toBeVisible();await page.getByRole('button',{name:'Stay',exact:true}).click();await expect(editor).toContainText('Unsupported current input');await editor.fill('Corrected supported input');await page.getByRole('button',{name:'Retry',exact:true}).click();await expect(page.getByRole('status')).toContainText('Draft saved');
  212 | });
  213 | for(const surface of ['study title','link URL'])test('account replacement clears local '+surface+' input',async({page})=>{
  214 |  await setup(page);if(surface==='study title'){await page.goto('/');await page.getByRole('button',{name:'Studies',exact:true}).click();await page.getByRole('button',{name:'Start a study',exact:true}).click();await page.getByLabel('Study title (optional)').fill('Prior account title');}else{await firstNote(page);await page.getByRole('button',{name:'Link',exact:true}).click();await page.getByLabel('Link URL',{exact:true}).fill('https://private.example.invalid/prior-account');}
  215 |  await page.route('**/auth/v1/token*',r=>r.fulfill({json:{...session,access_token:'other-account',user:{...session.user,id:'10000000-0000-4000-8000-000000000002'}}}));await page.evaluate(async()=>{const {supabase}=await import('/src/lib/supabase.ts');await supabase.auth.signInWithPassword({email:'other@example.invalid',password:'fixture'});});await expect(page.getByLabel('Link URL',{exact:true})).toHaveCount(0);await expect(page.getByLabel('Study title (optional)')).toHaveCount(0);expect(await page.locator('body').innerText()).not.toContain('Prior account title');expect(await page.evaluate(()=>Array.from(document.querySelectorAll('input')).map(el=>el.value).join(' '))).not.toContain('prior-account');
  216 | });
  217 | test('review: rejected study title can be corrected without replaying invalid payload',async({page})=>{
  218 |  const {requests}=await setup(page);const rejected=[];
  219 |  await page.route('**/api/studies',r=>{if(r.request().method()==='POST'&&r.request().postDataJSON().title==='   '){rejected.push(r.request().postDataJSON());return r.fulfill({status:400,json:{code:'scribeswell_personal_notes_input_invalid'}});}return r.fallback();});
  220 |  await page.goto('/');await page.getByRole('button',{name:'Studies',exact:true}).click();await page.getByRole('button',{name:'Start a study',exact:true}).click();await page.getByLabel('Study title (optional)').fill('   ');await page.getByRole('button',{name:'Create study',exact:true}).click();await expect(page.getByRole('alert')).toBeVisible();await page.getByLabel('Study title (optional)').fill('Corrected title');await page.getByRole('button',{name:'Create study',exact:true}).click();await expect(page.getByRole('button',{name:'Add note',exact:true})).toBeVisible();const accepted=requests.find(r=>r.method==='POST'&&r.path==='/api/studies').payload;expect(accepted.title).toBe('Corrected title');expect(accepted.operation_id).not.toBe(rejected[0].operation_id);
  221 | });
  222 | test('review: reopening a conflicting lane preserves mine until explicit latest replacement',async({page})=>{
  223 |  const options={failPut:409};await setup(page,options);await firstNote(page);const editor=page.getByLabel('Note text',{exact:true});await editor.fill('My conflicting text');await expect(page.getByRole('alert')).toContainText('This note has changed');
  224 |  const latest={...attribution,id:note,study_id:study,visibility:'study',revision:'2',value:{document:{version:1,blocks:[{type:'paragraph',direction:'auto',content:[{type:'text',text:'Latest from server',marks:[]}]}]},connections:[],highlights:[]}};let reads=0;
  225 |  await page.route('**/api/studies/'+study+'/notes/'+note,r=>{if(r.request().method()==='GET'){reads++;return r.fulfill({json:latest});}return r.fallback();});
  226 |  await page.getByRole('button',{name:'Back to Studies',exact:true}).click();await page.getByRole('button',{name:'Empty note',exact:true}).click();
  227 |  await expect(editor).toContainText('My conflicting text');expect(reads).toBe(0);
  228 |  await page.getByRole('button',{name:'Review latest',exact:true}).click();await expect(page.getByRole('region',{name:'Current saved note'})).toContainText('Latest from server');
  229 |  await expect(editor).toContainText('My conflicting text');await page.getByRole('button',{name:'Use latest',exact:true}).click();await expect(editor).toContainText('Latest from server');expect(reads).toBe(1);
  230 | });
  231 | test('review: IME exit prompts responsively and Stay retains composing input',async({page})=>{
  232 |  await setup(page);await firstNote(page);const editor=page.getByLabel('Note text',{exact:true});await editor.dispatchEvent('compositionstart');await editor.fill('Still composing עברית');await page.getByRole('button',{name:'Sign out',exact:true}).click();await expect(page.getByRole('dialog',{name:'Changes not saved'})).toBeVisible({timeout:1000});await page.getByRole('button',{name:'Stay',exact:true}).click();await expect(editor).toContainText('Still composing עברית');await editor.dispatchEvent('compositionend');await expect(page.getByRole('status')).toContainText('Draft saved');
  233 | });
  234 | test('review: Shift Enter soft break survives save and reload',async({page})=>{
  235 |  const {requests}=await setup(page);await firstNote(page);const editor=page.getByLabel('Note text',{exact:true});await editor.fill('First line');await editor.press('End');await editor.press('Shift+Enter');await editor.pressSequentially('Second line');await expect(page.getByRole('status')).toContainText('Draft saved');const saved=requests.filter(r=>r.method==='PUT').at(-1).payload.value;expect(saved.document.blocks.map(b=>b.content.map(i=>i.text).join('')).join('\n')).toBe('First line\nSecond line');await reloadRememberedWorkspace(page);await page.getByRole('button',{name:'Studies',exact:true}).click();await page.getByRole('button',{name:/First line/}).click();await expect(editor).toHaveText('First line\nSecond line');
  236 | });
  237 | test('review: invalid DNS link remains correctable without changing note text',async({page})=>{
  238 |  await setup(page);await firstNote(page);const editor=page.getByLabel('Note text',{exact:true});await editor.fill('Selected source text');await editor.press('ControlOrMeta+A');await page.getByRole('button',{name:'Link',exact:true}).click();await page.getByLabel('Link URL',{exact:true}).fill('https://exa_mple.org');await page.getByRole('button',{name:'Insert link',exact:true}).click();await expect(page.getByRole('alert')).toContainText('valid hostname');await expect(editor).toHaveText('Selected source text');await page.getByLabel('Link URL',{exact:true}).fill('https://example.org');await page.getByRole('button',{name:'Insert link',exact:true}).click();await expect(editor.locator('a')).toHaveText('Selected source text');await expect(page.getByRole('status')).toContainText('Draft saved');
  239 | });
  240 | async function reviewLibrary(page,options={}){
  241 |  await setup(page);const otherStudy='30000000-0000-4000-8000-000000000002',otherNote='40000000-0000-4000-8000-000000000002';
  242 |  const value=text=>({document:{version:1,blocks:[{type:'paragraph',direction:'auto',content:[{type:'text',text,marks:[]}]}]},connections:[],highlights:[]});
  243 |  const studyView=id=>({...attribution,id,title:id===study?'Study A':'Study B',revision:'1'});
  244 |  const noteView=(parent,id,text)=>({...attribution,id,study_id:parent,visibility:'study',revision:'1',value:value(text)});
  245 |  await page.route('**/api/studies**',async r=>{if(r.request().method()==='PUT'||new URL(r.request().url()).pathname==='/api/studies/context-notes')return r.fallback();const url=new URL(r.request().url()),parts=url.pathname.split('/').filter(Boolean);let result;
  246 |   if(parts.length===2||parts[2]==='search')result={items:[studyView(study),studyView(otherStudy)],next_cursor:null};
  247 |   else if(parts.length===3)result=options.detail?await options.detail(parts[2],studyView):studyView(parts[2]);
  248 |   else if(parts.length===4){const parent=parts[2];result=options.notes?await options.notes(parent,url.searchParams.get('cursor'),noteView):{items:[noteView(parent,note,'A first'),noteView(parent,otherNote,'A second')],next_cursor:null};}
  249 |   else result=options.read?await options.read(parts[2],parts[4],noteView):noteView(parts[2],parts[4],parts[4]===note?'A first':'A second');
  250 |   return r.fulfill({json:result});
  251 |  });await page.goto('/');await page.getByRole('button',{name:'Studies',exact:true}).click();return {otherStudy,otherNote};
  252 | }
  253 | test('review: superseded study and note responses cannot replace newer navigation',async({page})=>{
  254 |  const gates=[];const options={detail:(id,view)=>new Promise(resolve=>gates.push({id,release:()=>resolve(view(id))}))};const {otherStudy}=await reviewLibrary(page,options);
  255 |  await page.getByRole('button',{name:'Study A',exact:true}).click();await expect.poll(()=>gates.length).toBe(1);await page.getByRole('button',{name:'Study B',exact:true}).click();await expect.poll(()=>gates.length).toBe(2);gates.find(g=>g.id===otherStudy).release();await expect(page.getByRole('heading',{name:'Study B',exact:true})).toBeVisible();const old=page.waitForResponse('**/api/studies/'+study);gates.find(g=>g.id===study).release();await old;await expect(page.getByRole('heading',{name:'Study B',exact:true})).toBeVisible();
  256 |  const noteGates=[];options.read=(parent,id,view)=>new Promise(resolve=>noteGates.push({id,release:()=>resolve(view(parent,id,id===note?'A first':'A second'))}));await page.getByRole('button',{name:'A first',exact:true}).click();await expect.poll(()=>noteGates.length).toBe(1);await page.getByRole('button',{name:'A second',exact:true}).click();await expect.poll(()=>noteGates.length).toBe(2);noteGates[1].release();await expect(page.getByLabel('Note text',{exact:true})).toHaveText('A second');const stale=page.waitForResponse('**/notes/'+note);noteGates[0].release();await stale;await expect(page.getByLabel('Note text',{exact:true})).toHaveText('A second');
  257 | });
  258 | test('review: More notes deduplicates its page and ignores a changed study parent',async({page})=>{
```