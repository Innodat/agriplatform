# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: personal-notes.spec.cjs >> native PostgreSQL browser reload returns the acknowledged aggregate
- Location: tests/personal-notes.spec.cjs:175:1

# Error details

```
Error: expect(received).toBe(expected) // Object.is equality

Expected: true
Received: false

Call Log:
- Timeout 5000ms exceeded while waiting on the predicate
```

# Page snapshot

```yaml
- generic [ref=e3]:
  - banner [ref=e5]:
    - generic [ref=e6]:
      - generic [ref=e7]: Scribes' Well
      - generic [ref=e13]:
        - generic [ref=e14]: reader@example.invalid
        - button "Sign out" [ref=e18]
  - main [ref=e22]:
    - generic [ref=e23]:
      - generic [ref=e24]:
        - tablist "Workspace tabs" [ref=e25]:
          - generic [ref=e26]:
            - tab "Genesis 1" [selected] [ref=e27]
            - button "Rename tab 1" [ref=e28]: Rename
        - button "New workspace tab" [ref=e29]: + New tab
      - generic [ref=e30]:
        - button "Add reader pane" [ref=e31]
        - button "Enter focus mode" [ref=e34]: Focus mode
      - navigation "Reader tools" [ref=e40]:
        - button "Studies" [ref=e41]
        - button "Analysis" [pressed] [ref=e42]
        - generic [ref=e43]: Untitled study
      - generic [ref=e44]:
        - tabpanel "Genesis 1" [ref=e45]:
          - region "Passage 1" [ref=e46]:
            - generic [ref=e47]:
              - button "Previous chapter" [disabled] [ref=e48]
              - 'button "Navigate: Genesis, chapter 1. Open selector." [ref=e52]': Genesis א
              - button "Next chapter" [disabled] [ref=e55]
            - region "Chapter text" [ref=e58]:
              - paragraph [ref=e59]:
                - generic [ref=e60]: "Current note: Native persisted בְּרֵאשִׁית"
                - text: · Draft saved
              - list "Verses" [ref=e61]:
                - listitem [ref=e62]:
                  - generic "Verse 1" [ref=e63]: "1"
                  - paragraph [ref=e64]:
                    - 'button "Word: בְּרֵאשִׁית" [ref=e65] [cursor=pointer]': בְּרֵאשִׁית
        - complementary "Study tools" [ref=e66]:
          - generic [ref=e67]:
            - tablist "Analysis" [ref=e68]:
              - tab "Word" [disabled] [ref=e69]
              - tab "Occurrences" [disabled] [ref=e70]
              - tab "Notes" [selected] [ref=e71]
            - generic [ref=e72]:
              - region "Relevant own notes" [ref=e73]:
                - heading "Relevant own notes" [level=3] [ref=e74]
                - paragraph [ref=e75]: Genesis 1 · Only you
                - paragraph [ref=e76]: No relevant saved notes.
                - list
              - region "Note editor" [ref=e78]:
                - heading "Notes" [level=3] [ref=e79]
                - button "Duplicate note" [ref=e80]
                - button "Delete note" [ref=e81]
                - button "Delete study" [ref=e82]
                - paragraph [ref=e83]: Untitled study
                - button "Read note" [ref=e84]
                - toolbar "Note formatting" [ref=e85]:
                  - button "Bold" [ref=e86]: B
                  - button "Italic" [ref=e87]: I
                  - button "Bullet list" [ref=e88]
                  - button "Numbered list" [ref=e89]
                  - button "Link" [ref=e90]
                  - button "Insert passage reference" [ref=e93]
                  - generic [ref=e96]:
                    - text: Direction
                    - combobox "Paragraph direction" [ref=e97]:
                      - option "Auto" [selected]
                      - option "Left to right"
                      - option "Right to left"
                - textbox "Note text" [active] [ref=e98]
                - status [ref=e99]: Draft saved
                - button "Back to Studies" [ref=e100]
```

# Test source

```ts
  31  |     exact: true
  32  |   }).getAttribute('aria-pressed')) === 'true' ? 'Studies' : null;
  33  |   await page.getByRole('button', {
  34  |     name: 'Add reader pane',
  35  |     exact: true
  36  |   }).click();
  37  |   await page.getByRole('dialog', {
  38  |     name: 'Book and chapter selector'
  39  |   }).getByRole('button', {
  40  |     name: 'Cancel',
  41  |     exact: true
  42  |   }).click();
  43  |   if (tool && page.viewportSize().width < 768) await page.getByRole('button', {
  44  |     name: tool,
  45  |     exact: true
  46  |   }).click();
  47  | }
  48  | const {test,expect}=require('@playwright/test');
  49  | const account='10000000-0000-4000-8000-000000000001',actor='20000000-0000-4000-8000-000000000001';
  50  | const study='30000000-0000-4000-8000-000000000001',note='40000000-0000-4000-8000-000000000001';
  51  | const session={access_token:'current',refresh_token:'fixture',expires_at:Date.now()/1000+3600,expires_in:3600,token_type:'bearer',user:{id:account,email:'reader@example.invalid',aud:'authenticated',app_metadata:{},user_metadata:{}}};
  52  | const attribution={owner_account_id:account,created_at:'2026-10-23T10:00:00.000000Z',updated_at:'2026-10-23T10:00:00.000000Z',created_by_actor_id:actor,updated_by_actor_id:actor};
  53  | async function setup(page,options={}){
  54  |  await page.route('**/auth/v1/user*',r=>{const token=r.request().headers().authorization?.replace(/^Bearer /,''),sameOwner=['current','renewed-current','fresh-same-account','renewed-study-review'].includes(token),user=token==='other-account'?{...session.user,id:'10000000-0000-4000-8000-000000000002'}:sameOwner?session.user:null;return r.fulfill(user?{json:user}:{status:401,json:{error_code:'session_not_found',msg:'Synthetic session unavailable'}});});
  55  |  await page.route('**/auth/v1/logout*',r=>r.fulfill({json:{}}));
  56  |  await page.addInitScript(s=>localStorage.setItem('pts-auth',JSON.stringify(s)),session);
  57  |  await page.route('http://127.0.0.1:8001/**',r=>r.fulfill({json:[]}));
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
  119 | async function waitForWorkspaceCheckpoint(page,{noteId=note,studySelected=true}={}){
  120 |  await expect(page.getByRole('tablist',{name:'Workspace tabs'})).toHaveAttribute('data-device-ready','true');
  121 |  await expect.poll(()=>page.evaluate(async({account,study,noteId,studySelected})=>{
  122 |   const {readWorkspace}=await import('/src/lib/workspace-storage.ts');
  123 |   const saved=await readWorkspace(account),key=document.querySelector('[data-workspace-tab][aria-selected="true"]')?.getAttribute('data-workspace-tab');
  124 |   const tab=saved.public?.tabs.find(tab=>tab.tabKey===key);
  125 |   if(!tab||saved.public.activeTabKey!==key)return false;
  126 |   const snapshot=history.state?.usr?.scribeswellReader;
  127 |   if(snapshot?.tabKey===key&&(tab.activePaneKey!==snapshot.activePaneKey||JSON.stringify(tab.panes.map(p=>[p.paneKey,p.ref]))!==JSON.stringify(snapshot.panes.map(p=>[p.paneKey,p.ref]))))return false;
  128 |   if(!studySelected)return true;
  129 |   const selected=saved.private?.tabs.find(row=>row.tabKey===key&&row.incarnation===tab.incarnation);
  130 |   return selected?.study===study&&(noteId===null?selected.note===undefined:selected.note===noteId);
> 131 |  },{account,study,noteId,studySelected})).toBe(true);
      |                                           ^ Error: expect(received).toBe(expected) // Object.is equality
  132 | }
  133 | async function reloadRememberedWorkspace(page,{title='Untitled study',noteId=note,studySelected=true}={}){
  134 |  await waitForWorkspaceCheckpoint(page,{noteId,studySelected});
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
  158 | async function firstNote(page){await page.goto('/');await expect(page.getByRole('tablist',{name:'Workspace tabs'})).toHaveAttribute('data-device-ready','true');await page.getByRole('button',{name:'Studies',exact:true}).click();await page.getByRole('button',{name:'Start a study',exact:true}).click();await page.getByRole('button',{name:'Create study',exact:true}).click();await page.getByRole('button',{name:'Add note',exact:true}).click();await expect(page.getByLabel('Note text',{exact:true})).toBeVisible();}
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
  177 |  await setup(page);await page.unroute('**/api/studies**');
  178 |  for(const pattern of ['**/api/studies**','**/api/operations/**'])await page.route(pattern,async r=>{const target=process.env.SCRIBESWELL_NOTES_NATIVE_API+new URL(r.request().url()).pathname+new URL(r.request().url()).search;const response=await r.fetch({url:target});await r.fulfill({response});});
  179 |  await firstNote(page);await page.getByLabel('Note text',{exact:true}).fill('Native persisted בְּרֵאשִׁית');await expect(page.getByRole('status').filter({hasText:'Draft saved'})).toBeVisible();
  180 |  await reloadRememberedWorkspace(page);await page.getByRole('button',{name:'Studies',exact:true}).click();await page.getByRole('button',{name:'Native persisted בְּרֵאשִׁית',exact:true}).click();await expect(page.getByLabel('Note text',{exact:true})).toContainText('Native persisted בְּרֵאשִׁית');
  181 | });
  182 | 
  183 | test('unknown response blocks newer snapshots and recovers the original operation',async({page})=>{
  184 |  let release;const options={dropPut:true,beforeLookup:()=>new Promise(resolve=>release=resolve)};const {requests}=await setup(page,options);await firstNote(page);const editor=page.getByLabel('Note text',{exact:true});await editor.fill('first unknown');await expect.poll(()=>Boolean(release)).toBe(true);await editor.fill('later snapshot');await page.waitForTimeout(700);expect(requests.filter(r=>r.method==='PUT')).toHaveLength(1);options.beforeLookup=undefined;release();await expect(page.getByRole('status').filter({hasText:'Draft saved'})).toBeVisible();expect(requests.filter(r=>r.method==='PUT')).toHaveLength(2);
  185 | });
  186 | test('revision conflict preserves input and guards study switching',async({page})=>{
  187 |  await setup(page,{failPut:409});await firstNote(page);await page.getByLabel('Note text',{exact:true}).fill('mine conflicts');await expect(page.getByRole('alert')).toContainText('This note has changed');await page.getByRole('button',{name:'Back to Studies',exact:true}).click();await page.getByRole('button',{name:'Leave study',exact:true}).click();await expect(page.getByRole('dialog',{name:'Changes not saved'})).toBeVisible();await expect(page.getByRole('button',{name:'Switch anyway',exact:true})).toBeVisible();await page.getByRole('button',{name:'Stay',exact:true}).click();await page.getByRole('button',{name:'Analysis',exact:true}).click();await expect(page.getByLabel('Note text',{exact:true})).toContainText('mine conflicts');
  188 | });
  189 | test('same-account reauthentication preserves input and requires explicit retry',async({page})=>{
  190 |  const options={failPut:401};const {requests}=await setup(page,options);await firstNote(page);await page.getByLabel('Note text',{exact:true}).fill('recoverable current input');await expect(page.getByRole('alert')).toContainText('Sign in');await expect(page.getByLabel('Note text',{exact:true})).toHaveCount(0);const count=requests.filter(r=>r.method==='PUT').length;
  191 |  await page.route('**/auth/v1/token*',r=>r.fulfill({json:{...session,access_token:'renewed-current'}}));await page.evaluate(async()=>{const {supabase}=await import('/src/lib/supabase.ts');await supabase.auth.signInWithPassword({email:'reader@example.invalid',password:'fixture'});});options.failPut=0;
  192 |  await page.getByRole('button',{name:'Retry Studies',exact:true}).click();await expect(page.getByLabel('Note text',{exact:true})).toContainText('recoverable current input');expect(requests.filter(r=>r.method==='PUT')).toHaveLength(count);await page.getByRole('button',{name:'Retry',exact:true}).click();await expect(page.getByRole('status').filter({hasText:'Draft saved'})).toBeVisible();
  193 | });
  194 | test('rich paragraphs directions lists marks and safe links survive saving and reopening',async({page})=>{
  195 |  const {requests}=await setup(page);await firstNote(page);const editor=page.getByLabel('Note text',{exact:true});await editor.evaluate(el=>{el.replaceChildren();const p=document.createElement('p');p.dir='rtl';const bold=document.createElement('strong');bold.textContent='שָׁלוֹם';p.append(bold);const link=document.createElement('a');link.href='https://example.org/source';link.textContent=' source';p.append(link);const list=document.createElement('ol');const li=document.createElement('li');const i=document.createElement('em');i.textContent='Second paragraph';li.append(i);list.append(li);el.append(p,list);el.dispatchEvent(new InputEvent('input',{bubbles:true}));});await expect(page.getByRole('status').filter({hasText:'Draft saved'})).toBeVisible();const saved=requests.filter(r=>r.method==='PUT').at(-1).payload.value;expect(saved.document.blocks[0].direction).toBe('rtl');expect(saved.document.blocks[0].content[0].marks).toEqual(['bold']);expect(saved.document.blocks[1].style).toBe('ordered');
  196 |  await reloadRememberedWorkspace(page);await page.getByRole('button',{name:'Studies',exact:true}).click();await page.getByRole('button',{name:/Second paragraph/}).click();await expect(editor.locator('strong')).toHaveText('שָׁלוֹם');await expect(editor.locator('ol li em')).toHaveText('Second paragraph');await expect(editor.locator('a')).toHaveAttribute('rel','noopener noreferrer');
  197 | });
  198 | test('editor toolbar actions persist direction marks lists and safe links',async({page})=>{
  199 |  const {requests}=await setup(page);await firstNote(page);const editor=page.getByLabel('Note text',{exact:true});await editor.fill('שָׁלוֹם');await editor.press('ControlOrMeta+A');await page.getByRole('button',{name:'Bold',exact:true}).click();await page.getByLabel('Paragraph direction').selectOption('rtl');await editor.press('ControlOrMeta+End');await editor.press('Enter');await editor.press('ControlOrMeta+B');await editor.press('ControlOrMeta+I');await editor.pressSequentially('Second paragraph source');await page.getByRole('button',{name:'Numbered list',exact:true}).click();await editor.press('ControlOrMeta+End');await editor.press('ControlOrMeta+Shift+ArrowLeft');await page.getByRole('button',{name:'Link',exact:true}).click();await page.getByLabel('Link URL',{exact:true}).fill('https://example.org/source');await page.getByRole('button',{name:'Insert link',exact:true}).click();await expect(page.getByRole('status').filter({hasText:'Draft saved'})).toBeVisible();
  200 |  const saved=requests.filter(r=>r.method==='PUT').at(-1).payload.value;expect(saved.document.blocks.some(b=>b.type==='paragraph'&&b.direction==='rtl')).toBe(true);expect(saved.document.blocks.some(b=>b.type==='list'&&b.style==='ordered')).toBe(true);expect(JSON.stringify(saved)).toContain('bold');expect(JSON.stringify(saved)).toContain('italic');expect(JSON.stringify(saved)).toContain('https://example.org/source');
  201 |  await reloadRememberedWorkspace(page);await page.getByRole('button',{name:'Studies',exact:true}).click();await page.getByRole('button',{name:/Second paragraph/}).click();await expect(editor.locator('ol')).toBeVisible();await expect(editor.locator('a')).toHaveAttribute('href','https://example.org/source');await expect(editor.locator('p[dir="rtl"]').filter({hasText:'שָׁלוֹם'})).toBeVisible();
  202 | });
  203 | 
  204 | test('word inspection and Notes return retain the shared edit lane',async({page,isMobile})=>{
  205 |  await setup(page);await firstNote(page);await page.getByLabel('Note text',{exact:true}).fill('Current note remains selected');if(isMobile||test.info().project.name==='mobile')await page.getByRole('button',{name:'Return to reader',exact:true}).click();await page.getByRole('button',{name:/Word:/}).first().click();await expect(page.getByRole('tab',{name:'Word',exact:true})).toBeVisible();await expect(page.getByRole('tab',{name:'Occurrences',exact:true})).toBeVisible();await page.getByRole('tab',{name:'Notes',exact:true}).click();await expect(page.getByLabel('Note text',{exact:true})).toContainText('Current note remains selected');expect(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth)).toBe(false);
  206 | });
  207 | test('unsupported current editor input stays unsaved and exit guarded until corrected',async({page})=>{
  208 |  await setup(page);await firstNote(page);const editor=page.getByLabel('Note text',{exact:true});await editor.evaluate(el=>{const table=document.createElement('table');table.textContent='Unsupported current input';el.replaceChildren(table);el.dispatchEvent(new InputEvent('input',{bubbles:true}));});await expect(page.getByRole('status')).toContainText('Changes not saved');await page.getByRole('button',{name:'Sign out',exact:true}).click();await expect(page.getByRole('dialog',{name:'Changes not saved'})).toBeVisible();await page.getByRole('button',{name:'Stay',exact:true}).click();await expect(editor).toContainText('Unsupported current input');await editor.fill('Corrected supported input');await page.getByRole('button',{name:'Retry',exact:true}).click();await expect(page.getByRole('status')).toContainText('Draft saved');
  209 | });
  210 | for(const surface of ['study title','link URL'])test('account replacement clears local '+surface+' input',async({page})=>{
  211 |  await setup(page);if(surface==='study title'){await page.goto('/');await page.getByRole('button',{name:'Studies',exact:true}).click();await page.getByRole('button',{name:'Start a study',exact:true}).click();await page.getByLabel('Study title (optional)').fill('Prior account title');}else{await firstNote(page);await page.getByRole('button',{name:'Link',exact:true}).click();await page.getByLabel('Link URL',{exact:true}).fill('https://private.example.invalid/prior-account');}
  212 |  await page.route('**/auth/v1/token*',r=>r.fulfill({json:{...session,access_token:'other-account',user:{...session.user,id:'10000000-0000-4000-8000-000000000002'}}}));await page.evaluate(async()=>{const {supabase}=await import('/src/lib/supabase.ts');await supabase.auth.signInWithPassword({email:'other@example.invalid',password:'fixture'});});await expect(page.getByLabel('Link URL',{exact:true})).toHaveCount(0);await expect(page.getByLabel('Study title (optional)')).toHaveCount(0);expect(await page.locator('body').innerText()).not.toContain('Prior account title');expect(await page.evaluate(()=>Array.from(document.querySelectorAll('input')).map(el=>el.value).join(' '))).not.toContain('prior-account');
  213 | });
  214 | test('review: rejected study title can be corrected without replaying invalid payload',async({page})=>{
  215 |  const {requests}=await setup(page);const rejected=[];
  216 |  await page.route('**/api/studies',r=>{if(r.request().method()==='POST'&&r.request().postDataJSON().title==='   '){rejected.push(r.request().postDataJSON());return r.fulfill({status:400,json:{code:'scribeswell_personal_notes_input_invalid'}});}return r.fallback();});
  217 |  await page.goto('/');await page.getByRole('button',{name:'Studies',exact:true}).click();await page.getByRole('button',{name:'Start a study',exact:true}).click();await page.getByLabel('Study title (optional)').fill('   ');await page.getByRole('button',{name:'Create study',exact:true}).click();await expect(page.getByRole('alert')).toBeVisible();await page.getByLabel('Study title (optional)').fill('Corrected title');await page.getByRole('button',{name:'Create study',exact:true}).click();await expect(page.getByRole('button',{name:'Add note',exact:true})).toBeVisible();const accepted=requests.find(r=>r.method==='POST'&&r.path==='/api/studies').payload;expect(accepted.title).toBe('Corrected title');expect(accepted.operation_id).not.toBe(rejected[0].operation_id);
  218 | });
  219 | test('review: reopening a conflicting lane preserves mine until explicit latest replacement',async({page})=>{
  220 |  const options={failPut:409};await setup(page,options);await firstNote(page);const editor=page.getByLabel('Note text',{exact:true});await editor.fill('My conflicting text');await expect(page.getByRole('alert')).toContainText('This note has changed');
  221 |  const latest={...attribution,id:note,study_id:study,visibility:'study',revision:'2',value:{document:{version:1,blocks:[{type:'paragraph',direction:'auto',content:[{type:'text',text:'Latest from server',marks:[]}]}]},connections:[],highlights:[]}};let reads=0;
  222 |  await page.route('**/api/studies/'+study+'/notes/'+note,r=>{if(r.request().method()==='GET'){reads++;return r.fulfill({json:latest});}return r.fallback();});
  223 |  await page.getByRole('button',{name:'Back to Studies',exact:true}).click();await page.getByRole('button',{name:'Empty note',exact:true}).click();
  224 |  await expect(editor).toContainText('My conflicting text');expect(reads).toBe(0);
  225 |  await page.getByRole('button',{name:'Review latest',exact:true}).click();await expect(page.getByRole('region',{name:'Current saved note'})).toContainText('Latest from server');
  226 |  await expect(editor).toContainText('My conflicting text');await page.getByRole('button',{name:'Use latest',exact:true}).click();await expect(editor).toContainText('Latest from server');expect(reads).toBe(1);
  227 | });
  228 | test('review: IME exit prompts responsively and Stay retains composing input',async({page})=>{
  229 |  await setup(page);await firstNote(page);const editor=page.getByLabel('Note text',{exact:true});await editor.dispatchEvent('compositionstart');await editor.fill('Still composing עברית');await page.getByRole('button',{name:'Sign out',exact:true}).click();await expect(page.getByRole('dialog',{name:'Changes not saved'})).toBeVisible({timeout:1000});await page.getByRole('button',{name:'Stay',exact:true}).click();await expect(editor).toContainText('Still composing עברית');await editor.dispatchEvent('compositionend');await expect(page.getByRole('status')).toContainText('Draft saved');
  230 | });
  231 | test('review: Shift Enter soft break survives save and reload',async({page})=>{
```