# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: personal-notes.spec.cjs >> review: reopening a conflicting lane preserves mine until explicit latest replacement
- Location: tests/personal-notes.spec.cjs:222:1

# Error details

```
Test timeout of 30000ms exceeded.
```

```
Error: locator.click: Test timeout of 30000ms exceeded.
Call log:
  - waiting for getByRole('button', { name: 'Review latest', exact: true })

```

# Page snapshot

```yaml
- generic [ref=e2]:
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
          - button "Studies" [pressed] [ref=e41]
          - button "Analysis" [ref=e42]
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
                  - generic [ref=e60]: "Current note: My conflicting text"
                  - text: · Changes not saved
                - list "Verses" [ref=e61]:
                  - listitem [ref=e62]:
                    - generic "Verse 1" [ref=e63]: "1"
                    - paragraph [ref=e64]:
                      - 'button "Word: בְּרֵאשִׁית" [ref=e65] [cursor=pointer]': בְּרֵאשִׁית
          - complementary "Study tools" [ref=e66]:
            - region "My studies" [ref=e68]:
              - heading "My studies" [level=2] [ref=e69]
              - paragraph
              - button "Edit study details" [ref=e70]
              - heading "Untitled study" [level=3] [ref=e71]
              - button "Copy study" [ref=e72]
              - button "Delete study" [ref=e73]
              - button "Rename" [ref=e74]
              - button "Add note" [ref=e75]
              - list "Notes" [ref=e76]:
                - listitem [ref=e77]:
                  - button "Empty note" [ref=e78]
              - region "Collected passages" [ref=e79]:
                - heading "Passages" [level=4] [ref=e80]
                - button "Add passage" [ref=e82]
                - button "Add current passage" [ref=e86]
                - list "Passages"
              - button "Leave study" [ref=e89]
  - dialog "Changes not saved" [ref=e90]:
    - paragraph [ref=e91]: Changes not saved
    - button "Stay" [active] [ref=e92]
    - button "Switch anyway" [ref=e93]
```

# Test source

```ts
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
> 228 |  await page.getByRole('button',{name:'Review latest',exact:true}).click();await expect(page.getByRole('region',{name:'Current saved note'})).toContainText('Latest from server');
      |                                                                   ^ Error: locator.click: Test timeout of 30000ms exceeded.
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
  259 |  const pages=[];const {otherStudy}=await reviewLibrary(page,{notes:(parent,cursor,view)=>cursor?new Promise(resolve=>pages.push({parent,release:()=>resolve({items:[view(parent,'40000000-0000-4000-8000-000000000003','Older A page')],next_cursor:null})})):{items:[view(parent,note,parent===study?'A first':'B first')],next_cursor:parent===study?'page-two':null}});
  260 |  await page.getByRole('button',{name:'Study A',exact:true}).click();await page.getByRole('button',{name:'More notes',exact:true}).click();await expect.poll(()=>pages.length).toBe(1);await page.getByRole('button',{name:'More notes',exact:true}).click();await page.waitForTimeout(100);expect(pages).toHaveLength(1);pages[0].release();await expect(page.getByRole('button',{name:'Older A page',exact:true})).toHaveCount(1);
  261 |  await page.getByRole('button',{name:'Leave study',exact:true}).click();await page.getByRole('button',{name:'Study A',exact:true}).click();await page.getByRole('button',{name:'More notes',exact:true}).click();await expect.poll(()=>pages.length).toBe(2);await page.getByRole('button',{name:'Leave study',exact:true}).click();await page.getByRole('button',{name:'Study B',exact:true}).click();await expect(page.getByRole('heading',{name:'Study B',exact:true})).toBeVisible();const stale=page.waitForResponse('**/api/studies/'+study+'/notes?cursor=page-two');pages[1].release();await stale;await expect(page.getByRole('button',{name:'Older A page',exact:true})).toHaveCount(0);await expect(page.getByRole('button',{name:'B first',exact:true})).toBeVisible();expect(otherStudy).not.toBe(study);
  262 | });
  263 | test('review: note changes reset link range URL form and direction control',async({page})=>{
  264 |  await reviewLibrary(page);await page.getByRole('button',{name:'Study A',exact:true}).click();await page.getByRole('button',{name:'A first',exact:true}).click();const editor=page.getByLabel('Note text',{exact:true});await editor.press('ControlOrMeta+A');await page.getByLabel('Paragraph direction').selectOption('rtl');await expect(page.getByRole('status')).toContainText('Draft saved');await editor.press('ControlOrMeta+A');await page.getByRole('button',{name:'Link',exact:true}).click();await page.getByLabel('Link URL',{exact:true}).fill('https://prior-note.invalid');await page.getByRole('button',{name:'Back to Studies',exact:true}).click();await page.getByRole('button',{name:'A second',exact:true}).click();await expect(editor).toHaveText('A second');await expect(page.getByLabel('Link URL',{exact:true})).toHaveCount(0);await expect(page.getByLabel('Paragraph direction')).toHaveValue('auto');await page.evaluate(()=>window.getSelection().removeAllRanges());await page.getByRole('button',{name:'Link',exact:true}).click();await expect(page.getByLabel('Link URL',{exact:true})).toHaveValue('');await page.getByLabel('Link URL',{exact:true}).fill('https://example.org');await page.getByRole('button',{name:'Insert link',exact:true}).click();await expect(page.getByRole('alert')).toContainText('Select text in this note');await expect(editor).toHaveText('A second');
  265 | });
  266 | test('review: unknown study create preserves original operation and frozen title',async({page})=>{
  267 |  await setup(page);const attempts=[];await page.route('**/api/studies',r=>{if(r.request().method()!=='POST')return r.fallback();attempts.push(r.request().postDataJSON());if(attempts.length===1)return r.abort('connectionreset');return r.fallback();});const startup=[];page.on('pageerror',error=>startup.push({kind:'exception',name:error.name}));page.on('response',response=>{if(response.request().resourceType()==='script'&&startup.length<50)startup.push({kind:'script',pathname:new URL(response.url()).pathname,status:response.status()});});
  268 |  try{await page.goto('/');await page.getByRole('button',{name:'Studies',exact:true}).click();}catch(error){console.log('STARTUP_FIXTURE_DIAGNOSTIC',JSON.stringify({observations:startup,rootChildren:await page.locator('#root').evaluate(el=>el.childElementCount).catch(()=>null)}));throw error;}await page.getByRole('button',{name:'Start a study',exact:true}).click();await page.getByLabel('Study title (optional)').fill('Original uncertain title');await page.getByRole('button',{name:'Create study',exact:true}).click();await expect(page.getByRole('alert')).toBeVisible();await expect(page.getByLabel('Study title (optional)')).toHaveAttribute('readonly','');await expect(page.getByLabel('Study title (optional)')).toHaveValue('Original uncertain title');await page.getByRole('button',{name:'Retry original study creation',exact:true}).click();await expect(page.getByRole('button',{name:'Add note',exact:true})).toBeVisible();expect(attempts).toHaveLength(2);expect(attempts[1]).toEqual(attempts[0]);
  269 | });
  270 | 
  271 | 
  272 | test('rename: explicit Save Cancel and reload preserve independent note and reader',async({page})=>{
  273 |  const {requests}=await setup(page);await firstNote(page);const editor=page.getByLabel('Note text',{exact:true});await editor.fill('Acknowledged note שָׁלוֹם');await expect(page.getByRole('status')).toContainText('Draft saved');
  274 |  await page.getByRole('button',{name:'Back to Studies',exact:true}).click();await page.getByRole('button',{name:'Rename',exact:true}).click();await page.getByLabel('Title',{exact:true}).fill('Cancelled candidate');await expect(page.getByRole('heading',{name:'Untitled study',exact:true})).toBeVisible();await page.getByRole('button',{name:'Cancel',exact:true}).click();expect(requests.filter(r=>r.path.endsWith('/title'))).toHaveLength(0);
  275 |  await page.getByRole('button',{name:'Rename',exact:true}).click();await page.getByLabel('Title',{exact:true}).fill('English שלום');await page.getByRole('button',{name:'Save',exact:true}).click();await expect(page.getByRole('heading',{name:'English שלום',exact:true})).toBeVisible();
  276 |  await page.getByRole('button',{name:'Acknowledged note שָׁלוֹם',exact:true}).click();await expect(editor).toHaveText('Acknowledged note שָׁלוֹם');await expect(page.getByText('בְּרֵאשִׁית',{exact:true}).first()).toBeAttached();
  277 |  await reloadRememberedWorkspace(page,{title:'English שלום'});await page.getByRole('button',{name:'Studies',exact:true}).click();await page.getByRole('button',{name:'Acknowledged note שָׁלוֹם',exact:true}).click();await expect(editor).toHaveText('Acknowledged note שָׁלוֹם');expect(requests.filter(r=>r.path.includes('/notes/')&&r.method==='PUT')).toHaveLength(1);expect(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth)).toBe(false);
  278 | });
  279 | test('rename: conflict retains candidate and current reload requires new explicit Save',async({page})=>{
  280 |  const options={failRename:409};const {requests,metadata}=await setup(page,options);await firstNote(page);await page.getByRole('button',{name:'Back to Studies',exact:true}).click();await page.getByRole('button',{name:'Rename',exact:true}).click();await page.getByLabel('Title',{exact:true}).fill('My candidate');await page.getByRole('button',{name:'Save',exact:true}).click();await expect(page.getByRole('alert')).toContainText('title changed elsewhere');await expect(page.getByLabel('Title',{exact:true})).toHaveValue('My candidate');metadata.title='Elsewhere';metadata.revision='2';options.failRename=0;await page.getByRole('button',{name:'Load current title',exact:true}).click();await expect(page.getByRole('heading',{name:'Elsewhere',exact:true})).toBeVisible();await expect(page.getByLabel('Title',{exact:true})).toHaveValue('My candidate');expect(requests.filter(r=>r.path.endsWith('/title'))).toHaveLength(1);await page.getByRole('button',{name:'Save',exact:true}).click();await expect(page.getByRole('heading',{name:'My candidate',exact:true})).toBeVisible();const attempts=requests.filter(r=>r.path.endsWith('/title'));expect(attempts[1].payload.expected_revision).toBe('2');expect(attempts[1].payload.operation_id).not.toBe(attempts[0].payload.operation_id);
  281 | });
  282 | test('rename: unknown outcome survives closing and retries frozen original without overtaking',async({page})=>{
  283 |  const options={dropRename:true,unresolved:true};const {requests}=await setup(page,options);await firstNote(page);await page.getByRole('button',{name:'Back to Studies',exact:true}).click();await page.getByRole('button',{name:'Rename',exact:true}).click();await page.getByLabel('Title',{exact:true}).fill('Original frozen title');await page.getByRole('button',{name:'Save',exact:true}).click();await expect(page.getByRole('alert')).toContainText('Title not saved');await expect(page.getByLabel('Title',{exact:true})).toHaveAttribute('readonly','');await page.getByRole('button',{name:'Cancel',exact:true}).click();await page.getByRole('button',{name:'Rename',exact:true}).click();await expect(page.getByLabel('Title',{exact:true})).toHaveValue('Original frozen title');options.unresolved=false;await page.getByRole('button',{name:'Retry rename',exact:true}).click();await expect(page.getByRole('heading',{name:'Original frozen title',exact:true})).toBeVisible();const attempts=requests.filter(r=>r.path.endsWith('/title'));expect(attempts).toHaveLength(2);expect(attempts[1].payload).toEqual(attempts[0].payload);
  284 | });
  285 | test('rename: invalid input is editable and corrected with a new operation',async({page})=>{
  286 |  const options={failRename:400};const {requests}=await setup(page,options);await firstNote(page);await page.getByRole('button',{name:'Back to Studies',exact:true}).click();await page.getByRole('button',{name:'Rename',exact:true}).click();await page.getByLabel('Title',{exact:true}).fill('   ');await page.getByRole('button',{name:'Save',exact:true}).click();await expect(page.getByRole('alert')).toContainText('1–200');options.failRename=0;await page.getByLabel('Title',{exact:true}).fill('Corrected');await page.getByRole('button',{name:'Save',exact:true}).click();await expect(page.getByRole('heading',{name:'Corrected',exact:true})).toBeVisible();const attempts=requests.filter(r=>r.path.endsWith('/title'));expect(attempts[0].payload.operation_id).not.toBe(attempts[1].payload.operation_id);
  287 | });
  288 | test('rename: closing executing title keeps operation and stale acknowledgement reads current metadata',async({page})=>{
  289 |  let release;const gate=new Promise(resolve=>release=resolve);const {metadata}=await setup(page,{beforeRename:()=>gate});await firstNote(page);await page.getByRole('button',{name:'Back to Studies',exact:true}).click();await page.getByRole('button',{name:'Rename',exact:true}).click();await page.getByLabel('Title',{exact:true}).fill('Candidate');await page.getByRole('button',{name:'Save',exact:true}).click();await expect(page.getByRole('status')).toContainText('Saving title');await page.getByRole('button',{name:'Cancel',exact:true}).click();await page.getByRole('button',{name:'Rename',exact:true}).click();await expect(page.getByLabel('Title',{exact:true})).toHaveAttribute('readonly','');
  290 |  await page.route('**/api/studies/'+study,async r=>{if(r.request().method()!=='GET')return r.fallback();metadata.title='Newer current title';metadata.revision='3';return r.fulfill({json:{...attribution,id:study,...metadata}});});release();await expect(page.getByRole('heading',{name:'Newer current title',exact:true})).toBeVisible();
  291 | });
  292 | test('rename: navigation and account replacement reject late private responses',async({page})=>{
  293 |  let release;const gate=new Promise(resolve=>release=resolve);await setup(page,{beforeRename:()=>gate});await firstNote(page);await page.getByRole('button',{name:'Back to Studies',exact:true}).click();await page.getByRole('button',{name:'Rename',exact:true}).click();await page.getByLabel('Title',{exact:true}).fill('Prior private candidate');await page.getByRole('button',{name:'Save',exact:true}).click();await expect(page.getByRole('status')).toContainText('Saving title');await page.getByRole('button',{name:'Leave study',exact:true}).click();release();await expect(page.getByRole('heading',{name:'Prior private candidate',exact:true})).toHaveCount(0);
  294 |  await page.getByRole('button',{name:'Prior private candidate',exact:true}).click();await page.getByRole('button',{name:'Rename',exact:true}).click();await page.getByLabel('Title',{exact:true}).fill('Unsubmitted prior input');await page.route('**/auth/v1/token*',r=>r.fulfill({json:{...session,access_token:'other-account',user:{...session.user,id:'10000000-0000-4000-8000-000000000002'}}}));await page.evaluate(async()=>{const {supabase}=await import('/src/lib/supabase.ts');await supabase.auth.signInWithPassword({email:'other@example.invalid',password:'fixture'});});await expect(page.getByLabel('Title',{exact:true})).toHaveCount(0);expect(await page.locator('body').innerText()).not.toContain('Unsubmitted prior input');
  295 | });
  296 | 
  297 | test('rename: account replacement during executing command rejects its late reply',async({page})=>{
  298 |  let release;const gate=new Promise(resolve=>release=resolve);await setup(page,{beforeRename:()=>gate});await firstNote(page);await page.getByRole('button',{name:'Back to Studies',exact:true}).click();await page.getByRole('button',{name:'Rename',exact:true}).click();await page.getByLabel('Title',{exact:true}).fill('Late prior-account title');const reply=page.waitForResponse('**/api/studies/'+study+'/title');await page.getByRole('button',{name:'Save',exact:true}).click();await expect(page.getByRole('status')).toContainText('Saving title');
  299 |  await page.route('**/auth/v1/token*',r=>r.fulfill({json:{...session,access_token:'other-account',user:{...session.user,id:'10000000-0000-4000-8000-000000000002'}}}));await page.evaluate(async()=>{const {supabase}=await import('/src/lib/supabase.ts');await supabase.auth.signInWithPassword({email:'other@example.invalid',password:'fixture'});});await expect(page.getByLabel('Title',{exact:true})).toHaveCount(0);release();await reply;await expect(page.getByRole('heading',{name:'Late prior-account title',exact:true})).toHaveCount(0);expect(await page.locator('body').innerText()).not.toContain('Late prior-account title');
  300 | });
  301 | for(const status of [401,403])test('rename: '+status+' hides private state and preserves public reading',async({page})=>{
  302 |  const options={failRename:status};const {requests}=await setup(page,options);await firstNote(page);await page.getByRole('button',{name:'Back to Studies',exact:true}).click();await page.getByRole('button',{name:'Rename',exact:true}).click();await page.getByLabel('Title',{exact:true}).fill('Recoverable title');await page.getByRole('button',{name:'Save',exact:true}).click();await expect(page.getByRole('alert')).toContainText(status===401?'Sign in':'access is unavailable');await expect(page.getByLabel('Title',{exact:true})).toHaveCount(0);await expect(page.getByText('בְּרֵאשִׁית',{exact:true}).first()).toBeAttached();
  303 |  if(status===401){const original=requests.find(r=>r.path.endsWith('/title')).payload;await page.route('**/auth/v1/token*',r=>r.fulfill({json:{...session,access_token:'renewed-current'}}));await page.evaluate(async()=>{const {supabase}=await import('/src/lib/supabase.ts');await supabase.auth.signInWithPassword({email:'reader@example.invalid',password:'fixture'});});options.failRename=0;await page.getByRole('button',{name:'Retry',exact:true}).click();await expect(page.getByLabel('Title',{exact:true})).toHaveValue('Recoverable title');expect(requests.filter(r=>r.path.endsWith('/title'))).toHaveLength(1);await page.getByRole('button',{name:'Retry rename',exact:true}).click();await expect(page.getByRole('heading',{name:'Recoverable title',exact:true})).toBeVisible();expect(requests.filter(r=>r.path.endsWith('/title'))[1].payload).toEqual(original);}
  304 | });
  305 | 
  306 | for(const surface of ['begin','conflict reload'])test('rename: late '+surface+' metadata cannot reopen a departed title editor',async({page})=>{
  307 |  const options={failRename:409};await setup(page,options);await firstNote(page);await page.getByRole('button',{name:'Back to Studies',exact:true}).click();
  308 |  if(surface==='conflict reload'){await page.getByRole('button',{name:'Rename',exact:true}).click();await page.getByLabel('Title',{exact:true}).fill('Kept candidate');await page.getByRole('button',{name:'Save',exact:true}).click();await expect(page.getByRole('alert')).toContainText('title changed elsewhere');}
  309 |  let release;const gate=new Promise(resolve=>release=resolve);await page.route('**/api/studies/'+study,async r=>{await gate;return r.fallback();});const response=page.waitForResponse('**/api/studies/'+study);
  310 |  await page.getByRole('button',{name:surface==='begin'?'Rename':'Load current title',exact:true}).click();await page.getByRole('button',{name:'Leave study',exact:true}).click();release();await response;await expect(page.getByLabel('Title',{exact:true})).toHaveCount(0);await expect(page.getByRole('button',{name:'Untitled study',exact:true})).toBeVisible();
  311 | });
  312 | 
  313 | test('rename: failed dirty note lane remains independent and recoverable',async({page})=>{
  314 |  const options={failPut:503};const {requests}=await setup(page,options);await firstNote(page);const editor=page.getByLabel('Note text',{exact:true});await editor.fill('Dirty note retained while renaming');await expect(page.getByRole('status')).toContainText('Changes not saved');const noteAttempt=requests.find(r=>r.path.includes('/notes/')&&r.method==='PUT').payload;
  315 |  await page.getByRole('button',{name:'Back to Studies',exact:true}).click();await page.getByRole('button',{name:'Rename',exact:true}).click();await page.getByLabel('Title',{exact:true}).fill('Independent metadata');await page.getByRole('button',{name:'Save',exact:true}).click();await expect(page.getByRole('heading',{name:'Independent metadata',exact:true})).toBeVisible();await page.getByRole('button',{name:'Analysis',exact:true}).click();await expect(editor).toHaveText('Dirty note retained while renaming');await expect(page.getByRole('status')).toContainText('Changes not saved');options.failPut=0;await page.getByRole('button',{name:'Retry',exact:true}).click();await expect(page.getByRole('status')).toContainText('Draft saved');const notes=requests.filter(r=>r.path.includes('/notes/')&&r.method==='PUT');expect(notes).toHaveLength(2);expect(notes[1].payload).toEqual(noteAttempt);
  316 | });
  317 | 
  318 | async function patchRename(page,options={}){const fixture=await setup(page,options);await firstNote(page);await page.getByRole('button',{name:'Back to Studies',exact:true}).click();await page.getByRole('button',{name:'Rename',exact:true}).click();return fixture;}
  319 | test('rename patch: opening a note during rename still reconciles its study heading',async({page})=>{
  320 |  let release;const gate=new Promise(resolve=>release=resolve);await patchRename(page,{beforeRename:()=>gate});await page.getByLabel('Title',{exact:true}).fill('Renamed with note open');await page.getByRole('button',{name:'Save',exact:true}).click();await page.getByRole('button',{name:'Empty note',exact:true}).click();release();await expect(page.getByLabel('Note text',{exact:true})).toBeVisible();await page.getByRole('button',{name:'Back to Studies',exact:true}).click();await expect(page.getByRole('heading',{name:'Renamed with note open',exact:true})).toBeVisible();
  321 | });
  322 | test('rename patch: confirmed PUT retries only a failed metadata read',async({page})=>{
  323 |  const {requests}=await patchRename(page);let reads=0;await page.route('**/api/studies/'+study,r=>{reads++;return reads===1?r.fulfill({status:503,json:{code:'studies_storage_unavailable'}}):r.fallback();});await page.getByLabel('Title',{exact:true}).fill('Confirmed title');await page.getByRole('button',{name:'Save',exact:true}).click();await expect(page.getByRole('alert')).toContainText('Title saved');await page.getByRole('button',{name:'Retry title refresh',exact:true}).click();await expect(page.getByRole('heading',{name:'Confirmed title',exact:true})).toBeVisible();expect(requests.filter(r=>r.path.endsWith('/title'))).toHaveLength(1);expect(reads).toBe(2);
  324 | });
  325 | test('rename patch: two hundred supplementary scalars remain intact and focus returns',async({page})=>{
  326 |  const {requests}=await patchRename(page);const title='𐐀'.repeat(200);await page.getByLabel('Title',{exact:true}).fill(title);await expect(page.getByLabel('Title',{exact:true})).toHaveValue(title);await page.getByLabel('Title',{exact:true}).press('Tab');await page.getByRole('button',{name:'Save',exact:true}).press('Enter');await expect(page.getByRole('heading',{name:title,exact:true})).toBeVisible();expect(requests.find(r=>r.path.endsWith('/title')).payload.title).toBe(title);await expect(page.getByRole('button',{name:'Rename',exact:true})).toBeFocused();await page.getByRole('button',{name:'Rename',exact:true}).press('Enter');await expect(page.getByLabel('Title',{exact:true})).toBeFocused();await page.getByLabel('Title',{exact:true}).press('Tab');await page.getByRole('button',{name:'Cancel',exact:true}).press('Enter');await expect(page.getByRole('button',{name:'Rename',exact:true})).toBeFocused();
  327 | });
  328 | test('rename patch: reversed conflict reloads keep newest base revision',async({page})=>{
```