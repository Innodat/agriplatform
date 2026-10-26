# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: personal-notes.spec.cjs >> note links review: Bullet list across an owned atom survives save reload
- Location: tests/personal-notes.spec.cjs:561:70

# Error details

```
Error: locator.click: Error: strict mode violation: getByRole('list', { name: 'Notes', exact: true }).getByRole('button') resolved to 2 elements:
    1) <button class="my-2 text-left underline">Before Genesis 1 after</button> aka getByRole('button', { name: 'Before Genesis 1 after' })
    2) <button class="block underline text-sm">Genesis 1</button> aka getByRole('button', { name: 'Genesis 1', exact: true })

Call log:
  - waiting for getByRole('list', { name: 'Notes', exact: true }).getByRole('button')

```

# Page snapshot

```yaml
- generic [ref=f1e3]:
  - banner [ref=f1e5]:
    - generic [ref=f1e6]:
      - generic [ref=f1e7]: Scribes' Well
      - generic [ref=f1e13]:
        - generic [ref=f1e14]: reader@example.invalid
        - button "Sign out" [ref=f1e18]
  - main [ref=f1e22]:
    - generic [ref=f1e23]:
      - generic [ref=f1e24]:
        - tablist "Workspace tabs" [ref=f1e25]:
          - generic [ref=f1e26]:
            - tab "Genesis 1" [selected] [ref=f1e27]
            - button "Rename tab 1" [ref=f1e28]: Rename
        - button "New workspace tab" [ref=f1e29]: + New tab
      - generic [ref=f1e30]:
        - button "Add reader pane" [ref=f1e31]
        - button "Enter focus mode" [ref=f1e34]: Focus mode
      - navigation "Reader tools" [ref=f1e40]:
        - button "Studies" [active] [pressed] [ref=f1e41]
        - button "Analysis" [ref=f1e42]
        - generic [ref=f1e43]: Untitled study
      - generic [ref=f1e44]:
        - tabpanel "Genesis 1" [ref=f1e45]:
          - region "Passage 1" [ref=f1e46]:
            - generic [ref=f1e47]:
              - button "Previous chapter" [disabled] [ref=f1e48]
              - 'button "Navigate: Genesis, chapter 1. Open selector." [ref=f1e52]': Genesis א
              - button "Next chapter" [disabled] [ref=f1e55]
            - region "Chapter text" [ref=f1e58]:
              - paragraph [ref=f1e59]:
                - generic [ref=f1e60]: "Current note: Before Genesis 1 after"
                - text: · Draft saved
              - list "Verses" [ref=f1e61]:
                - listitem [ref=f1e62]:
                  - generic "Verse 1" [ref=f1e63]: "1"
                  - paragraph [ref=f1e64]:
                    - 'button "Word: בְּרֵאשִׁית" [ref=f1e65] [cursor=pointer]': בְּרֵאשִׁית
        - complementary "Study tools" [ref=f1e66]:
          - region "My studies" [ref=f1e68]:
            - heading "My studies" [level=2] [ref=f1e69]
            - paragraph
            - button "Edit study details" [ref=f1e70]
            - heading "Untitled study" [level=3] [ref=f1e71]
            - button "Copy study" [ref=f1e72]
            - button "Delete study" [ref=f1e73]
            - button "Rename" [ref=f1e74]
            - button "Add note" [ref=f1e75]
            - list "Notes" [ref=f1e76]:
              - listitem [ref=f1e77]:
                - button "Before Genesis 1 after" [ref=f1e78]
                - button "Genesis 1" [ref=f1e79]
            - region "Collected passages" [ref=f1e80]:
              - heading "Passages" [level=4] [ref=f1e81]
              - button "Add passage" [ref=f1e83]
              - button "Add current passage" [ref=f1e87]
              - list "Passages"
            - button "Leave study" [ref=f1e90]
```

# Test source

```ts
  462 |  else{if(test.info().project.name==='mobile')await page.getByRole('button',{name:'Return to reader',exact:true}).click();await page.getByRole('button',{name:/Navigate:/}).first().click();await page.getByLabel('Passage reference',{exact:true}).fill('Ps110');}
  463 |  options.beforePassagePut=undefined;release();await expect(page.locator('ul[aria-label="Passages"]')).toContainText('Genesis 1');
  464 |  if(destination==='focus')await expect(page.getByLabel('Title',{exact:true})).toBeFocused();else{await expect(page.getByLabel('Passage reference',{exact:true})).toHaveValue('Ps110');await expect(page.getByLabel('Passage reference',{exact:true})).toBeFocused();}
  465 | });
  466 | 
  467 | test('note links: insert at caret retains writing and format2 after final deletion',async({page})=>{
  468 |  const {requests}=await setup(page);await firstNote(page);const editor=page.getByLabel('Note text',{exact:true});await editor.fill('Before שלום after');await editor.evaluate(el=>{el.focus();const range=document.createRange();range.setStart(el.firstChild,7);range.collapse(true);getSelection().removeAllRanges();getSelection().addRange(range);});
  469 |  await page.getByRole('button',{name:'Insert passage reference',exact:true}).click();await page.getByLabel('Passage reference',{exact:true}).fill('Genesis 1:31–2:3');await page.getByLabel('Passage reference',{exact:true}).press('Enter');await expect(editor).toContainText('Before Genesis 1:31–2:3שלום after');
  470 |  await expect(page.getByRole('status').filter({hasText:'Draft saved'})).toBeVisible();const put=requests.filter(r=>r.method==='PUT'&&r.path.endsWith('/notes/'+note)).at(-1);expect(put.payload.value.document.version).toBe(2);expect(put.payload.value.document.blocks[0].content.find(i=>i.type==='passage_link').reference.target.end).toEqual({chapter:2,verse:3});expect(requests.filter(r=>r.method==='PUT'&&r.path.endsWith('/passages'))).toHaveLength(0);
  471 |  await editor.locator('[data-note-passage]').evaluate(el=>el.remove());await editor.dispatchEvent('input');await expect.poll(()=>requests.filter(r=>r.method==='PUT'&&r.path.endsWith('/notes/'+note)).at(-1).payload.value.document.blocks[0].content.some(i=>i.type==='passage_link')).toBe(false);expect(requests.filter(r=>r.method==='PUT'&&r.path.endsWith('/notes/'+note)).at(-1).payload.value.document.version).toBe(2);
  472 | });
  473 | 
  474 | async function insertNoteReference(page,text){await page.getByRole('button',{name:'Insert passage reference',exact:true}).click();await page.getByLabel('Passage reference',{exact:true}).fill(text);await page.getByLabel('Passage reference',{exact:true}).press('Enter');}
  475 | for(const [input,label] of [['תהילים קי:1','Psalms 110:1'],['Genesis 2','Genesis 2'],['Matthew26:63–64','Matthew 26:63–64']])test(`note links: canonical insertion ${input} preserves current reader and note`,async({page})=>{
  476 |  const {requests}=await setup(page);await firstNote(page);const url=page.url(),editor=page.getByLabel('Note text',{exact:true});await editor.fill('My explanation שָׁלוֹם');await editor.evaluate(el=>{el.focus();const r=document.createRange();r.selectNodeContents(el);getSelection().removeAllRanges();getSelection().addRange(r);});await insertNoteReference(page,input);await expect(editor).toContainText('My explanation שָׁלוֹם'+label);expect(page.url()).toBe(url);await expect(editor.locator('[data-note-passage]')).toHaveCount(1);await expect(page.getByRole('status').filter({hasText:'Draft saved'})).toBeVisible();expect(requests.filter(r=>r.method==='POST'&&r.path.endsWith('/notes'))).toHaveLength(1);expect(requests.filter(r=>r.method==='PUT'&&r.path.endsWith('/passages'))).toHaveLength(0);
  477 | });
  478 | test('note links: cancel invalid IME and stale input preserve writing and useful reference input',async({page})=>{
  479 |  const {requests}=await setup(page);await firstNote(page);const editor=page.getByLabel('Note text',{exact:true});await editor.fill('Useful שָׁלוֹם');await expect(page.getByRole('status').filter({hasText:'Draft saved'})).toBeVisible();const before=requests.filter(r=>r.method==='PUT').length;
  480 |  await page.getByRole('button',{name:'Insert passage reference',exact:true}).click();const input=page.getByLabel('Passage reference',{exact:true});await input.fill('Ps 2:10–13');await input.press('Enter');await expect(input).toHaveValue('Ps 2:10–13');await expect(editor.locator('[data-note-passage]')).toHaveCount(0);await page.getByRole('button',{name:'Cancel',exact:true}).click();await expect(editor).toBeFocused();expect(requests.filter(r=>r.method==='PUT')).toHaveLength(before);
  481 |  await editor.dispatchEvent('compositionstart');await expect(page.getByRole('button',{name:'Insert passage reference',exact:true})).toBeDisabled();await expect(page.getByRole('button',{name:'Read note',exact:true})).toBeDisabled();await editor.dispatchEvent('compositionend');
  482 |  await page.getByRole('button',{name:'Insert passage reference',exact:true}).click();await input.fill('Gen 1');await editor.evaluate(el=>{el.append(document.createTextNode(' later'));el.dispatchEvent(new InputEvent('input',{bubbles:true}));});await input.press('Enter');await expect(input).toHaveValue('Gen 1');await expect(page.getByText('Place the caret in this note, then try inserting the reference again.',{exact:true})).toBeVisible();await expect(editor).toContainText('Useful שָׁלוֹם later');await expect(editor.locator('[data-note-passage]')).toHaveCount(0);await page.getByRole('button',{name:'Cancel',exact:true}).click();await page.getByRole('button',{name:'Insert passage reference',exact:true}).click();await expect(input).toHaveValue('Gen 1');await page.getByRole('button',{name:'Cancel',exact:true}).click();
  483 | });
  484 | test('note links: edit click offers Open read click navigates active pane with full range and same lane',async({page})=>{
  485 |  const {requests}=await setup(page);await firstNote(page);const editor=page.getByLabel('Note text',{exact:true});await editor.fill('Context ');await insertNoteReference(page,'Matthew26:63–64');const atom=editor.locator('[data-note-passage]'),url=page.url();await atom.click();expect(page.url()).toBe(url);await expect(page.getByRole('button',{name:'Open passage',exact:true})).toBeVisible();await page.getByRole('button',{name:'Open passage',exact:true}).click();await expect(page.getByText('Matthew 26:63–64 — Text unavailable',{exact:true})).toBeVisible();if(page.viewportSize().width<768)await page.getByRole('button',{name:'Analysis',exact:true}).click();await expect(editor).toContainText('Context Matthew 26:63–64');const opened=page.url();await page.getByRole('button',{name:'Read note',exact:true}).click();expect(page.url()).toBe(opened);await expect(editor).toHaveAttribute('aria-readonly','true');await atom.click();expect(page.url()).toBe(opened);if(page.viewportSize().width<768)await page.getByRole('button',{name:'Analysis',exact:true}).click();await page.getByRole('button',{name:'Edit note',exact:true}).click();await expect(editor).toHaveAttribute('contenteditable','true');expect(requests.filter(r=>r.method==='POST'&&r.path.endsWith('/notes'))).toHaveLength(1);expect(requests.filter(r=>r.method==='PUT'&&r.path.endsWith('/passages'))).toHaveLength(0);
  486 | });
  487 | test('note links: links source marks lists direction plain paste and reload roundtrip',async({page})=>{
  488 |  const {requests}=await setup(page);await firstNote(page);const editor=page.getByLabel('Note text',{exact:true});await editor.fill('Mixed עברית');await editor.press('ControlOrMeta+End');await page.getByLabel('Paragraph direction',{exact:true}).selectOption('rtl');await page.getByRole('button',{name:'Bullet list',exact:true}).click();await insertNoteReference(page,'Gen 1:31–2:3');await editor.press('End');await editor.press('ControlOrMeta+b');await editor.press('ArrowRight');await editor.press('ControlOrMeta+b');
  489 |  // Use a native clipboard event with HTML and a distinct plain-text value.
  490 |  await editor.evaluate(el=>{el.focus();const d=new DataTransfer();d.setData('text/html','<span data-note-passage="true">forged</span>');d.setData('text/plain',' plain');el.dispatchEvent(new ClipboardEvent('paste',{bubbles:true,clipboardData:d}));});
  491 |  await expect(page.getByRole('status').filter({hasText:'Draft saved'})).toBeVisible();const saved=structuredClone(requests.filter(r=>r.method==='PUT'&&r.path.endsWith('/notes/'+note)).at(-1).payload.value);expect(saved.document.version).toBe(2);expect(saved.document.blocks.some(b=>b.type==='list')).toBe(true);await reloadRememberedWorkspace(page);await page.getByRole('button',{name:'Studies',exact:true}).click();await page.getByRole('list',{name:'Notes',exact:true}).getByRole('button').click();await expect(editor.locator('[data-note-passage]')).toHaveCount(1);await expect(editor).toContainText('Genesis 1:31–2:3');await editor.press('End');await editor.press(' ');await expect(page.getByRole('status').filter({hasText:'Draft saved'})).toBeVisible();expect(requests.filter(r=>r.method==='PUT'&&r.path.endsWith('/notes/'+note)).at(-1).payload.value.document.version).toBe(2);
  492 | });
  493 | test('note links: corrupt and foreign atoms stay unsaved and cannot switch to stale reading',async({page})=>{
  494 |  const {requests}=await setup(page);await firstNote(page);const editor=page.getByLabel('Note text',{exact:true});await insertNoteReference(page,'Gen 1');await expect(page.getByRole('status').filter({hasText:'Draft saved'})).toBeVisible();const before=requests.filter(r=>r.method==='PUT').length;await editor.locator('[data-note-passage]').evaluate(el=>{el.textContent='corrupt';el.parentElement.dispatchEvent(new InputEvent('input',{bubbles:true}));});await expect(page.getByRole('status')).toContainText('Changes not saved');await expect(page.getByRole('button',{name:'Read note',exact:true})).toBeDisabled();await page.waitForTimeout(650);expect(requests.filter(r=>r.method==='PUT')).toHaveLength(before);await editor.evaluate(el=>{el.replaceChildren();const s=document.createElement('span');s.dataset.notePassage='true';s.textContent='foreign';s.contentEditable='false';el.append(s);el.dispatchEvent(new InputEvent('input',{bubbles:true}));});await expect(page.getByRole('status')).toContainText('Changes not saved');await page.waitForTimeout(650);expect(requests.filter(r=>r.method==='PUT')).toHaveLength(before);
  495 | });
  496 | test('note links: terminal format refusal pauses saves and retains whole local note',async({page})=>{
  497 |  const options={failPut:409,failPutCode:'note_format_unsupported'};const {requests}=await setup(page,options);await firstNote(page);const editor=page.getByLabel('Note text',{exact:true});await insertNoteReference(page,'Gen 1');await expect(page.getByRole('alert')).toContainText('Reload to continue editing.');const count=requests.filter(r=>r.method==='PUT').length;await editor.press('End');await editor.press('x');await page.waitForTimeout(650);expect(requests.filter(r=>r.method==='PUT')).toHaveLength(count);await expect(editor).toContainText('Genesis 1');await expect(page.getByRole('status')).toContainText('Changes not saved');await expect(page.getByRole('button',{name:'Retry',exact:true})).toHaveCount(0);
  498 | });
  499 | 
  500 | test('note links: keyboard edit offers Open and keyboard read opens range in active pane only',async({page})=>{
  501 |  const {requests}=await setup(page);await firstNote(page);await addReader(page);const editor=page.getByLabel('Note text',{exact:true});await editor.fill('Keep same note ');await insertNoteReference(page,'Gen 1:31–2:3');const atom=editor.locator('[data-note-passage]'),before=new URL(page.url());await atom.focus();await atom.press('Enter');expect(page.url()).toBe(before.href);await expect(page.getByRole('button',{name:'Open passage',exact:true})).toBeVisible();await page.getByRole('button',{name:'Read note',exact:true}).click();await atom.focus();await atom.press('Space');await expect.poll(()=>readerParams(page.url()).get('compareEndVerse')).toBe('3');const url=new URL(page.url());expect(readerParams(url.href).get('compareVerse')).toBe('31');expect(readerParams(url.href).get('compareEndChapter')).toBe('2');expect(readerParams(url.href).get('book')).toBe(readerParams(before.href).get('book'));expect(readerParams(url.href).get('chapter')).toBe(readerParams(before.href).get('chapter'));if(page.viewportSize().width<768)await page.getByRole('button',{name:'Analysis',exact:true}).click();await expect(editor).toContainText('Keep same note Genesis 1:31–2:3');expect(requests.filter(r=>r.method==='POST'&&r.path.endsWith('/notes'))).toHaveLength(1);
  502 | });
  503 | test('note links: unknown original operation and delayed acknowledgement preserve coherent newer value in Read',async({page})=>{
  504 |  let release;const options={dropPut:true,beforeLookup:()=>new Promise(resolve=>release=resolve)};const {requests}=await setup(page,options);await firstNote(page);const editor=page.getByLabel('Note text',{exact:true});await insertNoteReference(page,'Gen 1');await expect.poll(()=>Boolean(release)).toBe(true);const first=structuredClone(requests.filter(r=>r.method==='PUT').at(-1).payload);await editor.press('End');await editor.press('x');await page.getByRole('button',{name:'Read note',exact:true}).click();await expect(editor).toContainText('Genesis 1x');await expect(page.getByRole('status')).not.toHaveText('Draft saved');expect(requests.filter(r=>r.method==='PUT')).toHaveLength(1);options.beforeLookup=undefined;release();await expect(page.getByRole('status').filter({hasText:'Draft saved'})).toBeVisible();const puts=requests.filter(r=>r.method==='PUT');expect(puts).toHaveLength(2);expect(puts[0].payload).toEqual(first);expect(puts[1].payload.value.document.version).toBe(2);expect(puts[1].payload.operation_id).not.toBe(first.operation_id);await expect(editor.locator('[data-note-passage]')).toHaveCount(1);
  505 | });
  506 | for(const key of ['Backspace','Delete'])test(`note links: ${key} removes atomic inline and retains version2`,async({page})=>{
  507 |  const {requests}=await setup(page);await firstNote(page);const editor=page.getByLabel('Note text',{exact:true});await insertNoteReference(page,'Gen 1');await editor.locator('[data-note-passage]').evaluate((el,key)=>{const r=document.createRange();if(key==='Backspace')r.setStartAfter(el);else r.setStartBefore(el);r.collapse(true);el.parentElement.focus();getSelection().removeAllRanges();getSelection().addRange(r);},key);await editor.press(key);await expect(editor.locator('[data-note-passage]')).toHaveCount(0);await expect(page.getByRole('status').filter({hasText:'Draft saved'})).toBeVisible();expect(requests.filter(r=>r.method==='PUT').at(-1).payload.value.document.version).toBe(2);
  508 | });
  509 | test('note links: account replacement clears picker and pending insertion without leaking prior writing',async({page})=>{
  510 |  await setup(page);await firstNote(page);await page.getByLabel('Note text',{exact:true}).fill('Private prior note');await page.getByRole('button',{name:'Insert passage reference',exact:true}).click();await page.getByLabel('Passage reference',{exact:true}).fill('Gen 1');await page.route('**/auth/v1/token*',r=>r.fulfill({json:{...session,access_token:'other-account',user:{...session.user,id:'10000000-0000-4000-8000-000000000002'}}}));await page.evaluate(async()=>{const {supabase}=await import('/src/lib/supabase.ts');await supabase.auth.signOut({scope:'local'});await supabase.auth.signInWithPassword({email:'other@example.invalid',password:'fixture'});});await expect(page.getByLabel('Passage reference',{exact:true})).toHaveCount(0);await expect(page.getByText('Private prior note',{exact:true})).toHaveCount(0);
  511 | });
  512 | test('note links: note switch cancels picker without inserting into replacement note',async({page})=>{
  513 |  const {requests}=await setup(page);await firstNote(page);const editor=page.getByLabel('Note text',{exact:true});await editor.fill('First note writing');await expect(page.getByRole('status').filter({hasText:'Draft saved'})).toBeVisible();await page.getByRole('button',{name:'Insert passage reference',exact:true}).click();await page.getByLabel('Passage reference',{exact:true}).fill('Gen 1');
  514 |  const nextNote='40000000-0000-4000-8000-000000000002';await page.route(`**/api/studies/${study}/notes`,r=>r.request().method()==='POST'?r.fulfill({json:{operation_id:r.request().postDataJSON().operation_id,command:'note.create',study_id:study,note_id:nextNote,revision:'1'}}):r.fallback());await page.route(`**/api/studies/${study}/notes/${nextNote}`,r=>r.fulfill({json:{...attribution,id:nextNote,study_id:study,visibility:'study',revision:'1',value:{document:{version:1,blocks:[]},connections:[],highlights:[]}}}));
  515 |  await page.getByRole('button',{name:'Back to Studies',exact:true}).evaluate(el=>el.click());await page.getByRole('button',{name:'Add note',exact:true}).evaluate(el=>el.click());await expect(page.getByLabel('Passage reference',{exact:true})).toHaveCount(0);await expect(editor).toHaveText('');await expect(editor.locator('[data-note-passage]')).toHaveCount(0);expect(requests.filter(r=>r.method==='PUT')).toHaveLength(1);
  516 | });
  517 | for(const position of [0,6,14])test(`note links: insertion inside source at ${position} preserves source text marks and URL`,async({page})=>{
  518 |  const {requests}=await setup(page);await firstNote(page);const editor=page.getByLabel('Note text',{exact:true});await editor.fill('source writing');await editor.press('ControlOrMeta+a');await page.getByRole('button',{name:'Bold',exact:true}).click();await page.getByRole('button',{name:'Link',exact:true}).click();await page.getByLabel('Link URL',{exact:true}).fill('https://example.org');await page.getByRole('button',{name:'Insert link',exact:true}).click();await editor.locator('a').evaluate((el,position)=>{const r=document.createRange();r.setStart(document.createTreeWalker(el,NodeFilter.SHOW_TEXT).nextNode(),position);r.collapse(true);getSelection().removeAllRanges();getSelection().addRange(r);},position);await insertNoteReference(page,'Gen 1');await expect(page.getByRole('status').filter({hasText:'Draft saved'})).toBeVisible();const content=requests.filter(r=>r.method==='PUT').at(-1).payload.value.document.blocks[0].content;expect(content.map(i=>i.type)).toEqual(position===0?['passage_link','external_link']:position===14?['external_link','passage_link']:['external_link','passage_link','external_link']);const sources=content.filter(i=>i.type==='external_link');expect(sources.flatMap(i=>i.content).map(i=>i.text).join('')).toBe('source writing');expect(sources.every(i=>i.url==='https://example.org'&&i.content.every(t=>JSON.stringify(t.marks)==='["bold"]'))).toBe(true);
  519 | });
  520 | test('note links: caret inside an existing atom resolves after it without corrupting its label',async({page})=>{
  521 |  await setup(page);await firstNote(page);const editor=page.getByLabel('Note text',{exact:true});await insertNoteReference(page,'Gen 1');await editor.locator('[data-note-passage]').evaluate(el=>{const r=document.createRange();r.setStart(el.firstChild,3);r.collapse(true);getSelection().removeAllRanges();getSelection().addRange(r);});await insertNoteReference(page,'Gen 2');await expect(editor.locator('[data-note-passage]')).toHaveCount(2);await expect(editor.locator('[data-note-passage]').nth(0)).toHaveText('Genesis 1');await expect(editor.locator('[data-note-passage]').nth(1)).toHaveText('Genesis 2');await expect(page.getByRole('status').filter({hasText:'Draft saved'})).toBeVisible();
  522 | });
  523 | test('note links: Read Edit restores caret and keeps ordinary notes in format1',async({page})=>{
  524 |  const {requests}=await setup(page);await firstNote(page);const editor=page.getByLabel('Note text',{exact:true});await editor.fill('before after');await editor.evaluate(el=>{const r=document.createRange();r.setStart(el.firstChild,7);r.collapse(true);getSelection().removeAllRanges();getSelection().addRange(r);});const url=page.url();await page.getByRole('button',{name:'Read note',exact:true}).click();await page.getByRole('button',{name:'Edit note',exact:true}).click();await editor.press('x');await expect(editor).toHaveText('before xafter');expect(page.url()).toBe(url);await expect(page.getByRole('status').filter({hasText:'Draft saved'})).toBeVisible();expect(requests.filter(r=>r.method==='PUT').at(-1).payload.value.document.version).toBe(1);
  525 | });
  526 | 
  527 | test('note links patch: direction after atomic insertion targets the actual paragraph',async({page})=>{
  528 |  const {requests}=await setup(page);await firstNote(page);await insertNoteReference(page,'Gen 1');await page.getByLabel('Paragraph direction',{exact:true}).selectOption('rtl');await expect(page.getByRole('status').filter({hasText:'Draft saved'})).toBeVisible();await expect.poll(()=>requests.filter(r=>r.method==='PUT').at(-1).payload.value.document.blocks[0].direction).toBe('rtl');
  529 | });
  530 | test('note links patch: deliberate external focus is retained when picker closes',async({page})=>{
  531 |  await setup(page);await firstNote(page);await page.getByRole('button',{name:'Insert passage reference',exact:true}).click();await page.getByLabel('Passage reference',{exact:true}).fill('Gen 1');const direction=page.getByLabel('Paragraph direction',{exact:true});await direction.focus();await expect(page.getByLabel('Passage reference',{exact:true})).toHaveCount(0);await expect(direction).toBeFocused();
  532 | });
  533 | test('note links patch: atomic label isolates direction inside opposite-direction text',async({page})=>{
  534 |  await setup(page);await firstNote(page);await page.getByLabel('Paragraph direction',{exact:true}).selectOption('rtl');await insertNoteReference(page,'תהילים קי:1');const atom=page.getByLabel('Note text',{exact:true}).locator('[data-note-passage]');await expect(atom).toHaveAttribute('dir','auto');await expect(atom).toHaveCSS('unicode-bidi','isolate');
  535 | });
  536 | test('note links patch: queued insertion does not steal a deliberately changed focus',async({page})=>{
  537 |  await setup(page);await firstNote(page);await page.getByRole('button',{name:'Insert passage reference',exact:true}).click();const input=page.getByLabel('Passage reference',{exact:true});await input.fill('Gen 1');await input.evaluate(el=>{el.form.requestSubmit();queueMicrotask(()=>document.querySelector('[aria-label="Paragraph direction"]').focus());});await expect(page.getByLabel('Note text',{exact:true}).locator('[data-note-passage]')).toHaveCount(1);await expect(page.getByLabel('Paragraph direction',{exact:true})).toBeFocused();
  538 | });
  539 | test('note links patch: Read hides source-link form and Edit restores its candidate without writing',async({page})=>{
  540 |  const {requests}=await setup(page);await firstNote(page);const editor=page.getByLabel('Note text',{exact:true});await editor.fill('Source selection');await expect(page.getByRole('status').filter({hasText:'Draft saved'})).toBeVisible();await editor.press('ControlOrMeta+a');await page.getByRole('button',{name:'Link',exact:true}).click();await page.getByLabel('Link URL',{exact:true}).fill('https://example.org/source');const before=requests.filter(r=>r.method==='PUT').length;await page.getByRole('button',{name:'Read note',exact:true}).click();await expect(page.getByLabel('Link URL',{exact:true})).toHaveCount(0);await expect(page.getByRole('button',{name:'Insert link',exact:true})).toHaveCount(0);expect(requests.filter(r=>r.method==='PUT')).toHaveLength(before);await page.getByRole('button',{name:'Edit note',exact:true}).click();await expect(page.getByLabel('Link URL',{exact:true})).toHaveValue('https://example.org/source');await page.getByRole('button',{name:'Insert link',exact:true}).click();await expect(editor.locator('a')).toHaveText('Source selection');await expect(page.getByRole('status').filter({hasText:'Draft saved'})).toBeVisible();
  541 | });
  542 | 
  543 | for(const position of [null,0,6,14])test(`note links review: native insertion Undo Redo preserves writing and source at ${position}`,async({page})=>{
  544 |  const {requests}=await setup(page);await firstNote(page);const editor=page.getByLabel('Note text',{exact:true});await editor.pressSequentially('source writing');await editor.press('ControlOrMeta+z');await expect(editor).toHaveText('');await editor.press('ControlOrMeta+Shift+z');await expect(editor).toHaveText('source writing');if(position!==null){await editor.press('ControlOrMeta+a');await page.getByRole('button',{name:'Link',exact:true}).click();await page.getByLabel('Link URL',{exact:true}).fill('https://example.org/source');await page.getByRole('button',{name:'Insert link',exact:true}).click();await editor.locator('a').evaluate((el,position)=>{const r=document.createRange();r.setStart(document.createTreeWalker(el,NodeFilter.SHOW_TEXT).nextNode(),position);r.collapse(true);getSelection().removeAllRanges();getSelection().addRange(r);},position);}else await editor.press('End');await insertNoteReference(page,'Gen 1');await expect(editor.locator('[data-note-passage]')).toHaveCount(1);await editor.press('ControlOrMeta+z');await expect(editor).toHaveText('source writing');await expect(editor.locator('[data-note-passage]')).toHaveCount(0);if(position!==null)await expect(editor.locator('a')).toHaveText('source writing');await editor.press('ControlOrMeta+Shift+z');await expect(editor.locator('[data-note-passage]')).toHaveCount(1);await expect(editor).toContainText('Genesis 1');await editor.press('End');await editor.press('!');await expect(editor).toContainText('!');await editor.press('ControlOrMeta+z');await expect(editor).not.toContainText('!');await expect(editor.locator('[data-note-passage]')).toHaveCount(1);await editor.press('ControlOrMeta+Shift+z');await expect(editor).toContainText('!');await expect(page.getByRole('status').filter({hasText:'Draft saved'})).toBeVisible();expect(requests.filter(r=>r.method==='PUT').at(-1).payload.value.document.version).toBe(2);
  545 | });
  546 | test('note links review: no-caret insertion follows trailing DIV and loose text',async({page})=>{
  547 |  await setup(page);await firstNote(page);const editor=page.getByLabel('Note text',{exact:true});await editor.evaluate(el=>{const p=document.createElement('p');p.textContent='First';const div=document.createElement('div');div.textContent='Last block';el.replaceChildren(p,div,document.createTextNode(' trailing'));el.dispatchEvent(new InputEvent('input',{bubbles:true}));getSelection().removeAllRanges();});await insertNoteReference(page,'Gen 1');await expect(editor).toHaveText('FirstLast block trailingGenesis 1');
  548 | });
  549 | test('note links review: interrupted composition replacement accepts insertion only in new lane',async({page})=>{
  550 |  const {requests}=await setup(page);await firstNote(page);const editor=page.getByLabel('Note text',{exact:true});await editor.dispatchEvent('compositionstart');await editor.fill('Unfinished old composition');await page.getByRole('button',{name:'Back to Studies',exact:true}).click();const next='40000000-0000-4000-8000-000000000002';await page.route(`**/api/studies/${study}/notes`,r=>r.request().method()==='POST'?r.fulfill({json:{operation_id:r.request().postDataJSON().operation_id,command:'note.create',study_id:study,note_id:next,revision:'1'}}):r.fallback());await page.route(`**/api/studies/${study}/notes/${next}`,r=>r.request().method()==='PUT'?r.fulfill({json:{operation_id:r.request().postDataJSON().operation_id,command:'note.replace',study_id:study,note_id:next,revision:'2'}}):r.fulfill({json:{...attribution,id:next,study_id:study,visibility:'study',revision:'1',value:{document:{version:1,blocks:[]},connections:[],highlights:[]}}}));await page.getByRole('button',{name:'Add note',exact:true}).click();await page.getByRole('button',{name:'Switch anyway',exact:true}).click();await expect(editor).toHaveText('');await insertNoteReference(page,'Gen 1');await expect(editor.locator('[data-note-passage]')).toHaveCount(1);expect(requests.filter(r=>r.method==='PUT'&&r.path.endsWith('/notes/'+note))).toHaveLength(0);
  551 | });
  552 | test('note links review: source link refuses selection containing owned atom before mutation',async({page})=>{
  553 |  const {requests}=await setup(page);await firstNote(page);const editor=page.getByLabel('Note text',{exact:true});await editor.fill('Explanation ');await insertNoteReference(page,'Gen 1');await expect(page.getByRole('status').filter({hasText:'Draft saved'})).toBeVisible();const before=await editor.innerHTML(),writes=requests.filter(r=>r.method==='PUT').length;await editor.press('ControlOrMeta+a');await page.getByRole('button',{name:'Link',exact:true}).click();await page.getByLabel('Link URL',{exact:true}).fill('https://example.org/source');await page.getByRole('button',{name:'Insert link',exact:true}).click();await expect(page.getByRole('alert')).toContainText('Select ordinary text');await expect(page.getByLabel('Link URL',{exact:true})).toHaveValue('https://example.org/source');expect(await editor.innerHTML()).toBe(before);expect(requests.filter(r=>r.method==='PUT')).toHaveLength(writes);
  554 | });
  555 | test('note links review: inline boundary refuses insertion without changing writing or closing candidate',async({page})=>{
  556 |  await setup(page);await firstNote(page);const editor=page.getByLabel('Note text',{exact:true});await editor.evaluate(el=>{const p=document.createElement('p');for(let i=0;i<256;i++){const span=document.createElement('span');span.textContent='x';p.append(span);}el.replaceChildren(p);el.dispatchEvent(new InputEvent('input',{bubbles:true}));getSelection().removeAllRanges();});await expect(page.getByRole('status').filter({hasText:'Draft saved'})).toBeVisible();const before=await editor.innerHTML();await page.getByRole('button',{name:'Insert passage reference',exact:true}).click();const input=page.getByLabel('Passage reference',{exact:true});await input.fill('Gen 1');await input.press('Enter');await expect(input).toHaveValue('Gen 1');const feedbackId=await input.getAttribute('aria-describedby');expect(feedbackId).toBeTruthy();await expect(page.locator('[id="'+feedbackId+'"]')).toHaveAttribute('aria-live','polite');expect(await editor.innerHTML()).toBe(before);await expect(editor.locator('[data-note-passage]')).toHaveCount(0);await expect(page.getByRole('status').filter({hasText:'Draft saved'})).toBeVisible();
  557 | });
  558 | test('note links review: retained reference reopens at its candidate book and rejection is accessible',async({page})=>{
  559 |  await setup(page);await firstNote(page);await page.getByRole('button',{name:'Insert passage reference',exact:true}).click();const input=page.getByLabel('Passage reference',{exact:true});await input.fill('Ps 110:1');await page.getByRole('button',{name:'Cancel',exact:true}).click();await page.getByRole('button',{name:'Insert passage reference',exact:true}).click();await expect(input).toHaveValue('Ps 110:1');await expect(page.getByRole('group',{name:'Chapters of Psalms',exact:true})).toBeVisible();await input.fill('Ps 2:13');await expect(input).toHaveAttribute('aria-invalid','true');const errorId=await input.getAttribute('aria-describedby');expect(errorId).toBeTruthy();await expect(page.locator('[id="'+errorId+'"]')).toHaveAttribute('role','alert');await expect(page.locator('[id="'+errorId+'"]')).toContainText('Enter a valid');
  560 | });
  561 | for(const command of ['Bold','Italic','Bullet list','Numbered list'])test(`note links review: ${command} across an owned atom survives save reload`,async({page})=>{
> 562 |  const {requests}=await setup(page);await firstNote(page);const editor=page.getByLabel('Note text',{exact:true});await editor.fill('Before ');await insertNoteReference(page,'Gen 1');await editor.press('End');await editor.pressSequentially(' after');await editor.press('ControlOrMeta+a');await page.getByRole('button',{name:command,exact:true}).click();await expect(page.getByRole('status').filter({hasText:'Draft saved'})).toBeVisible();const saved=requests.filter(r=>r.method==='PUT').at(-1).payload.value;expect(JSON.stringify(saved)).toContain('passage_link');await reloadRememberedWorkspace(page);await page.getByRole('button',{name:'Studies',exact:true}).click();await page.getByRole('list',{name:'Notes',exact:true}).getByRole('button').click();await expect(editor).toHaveText('Before Genesis 1 after');await expect(editor.locator('[data-note-passage]')).toHaveCount(1);if(command==='Bold'||command==='Italic'){const paragraphs=saved.document.blocks.flatMap(b=>b.type==='paragraph'?[b]:b.items.flat());expect(paragraphs.flatMap(p=>p.content).filter(i=>i.type==='text').every(i=>i.marks.includes(command.toLowerCase()))).toBe(true);}else expect(saved.document.blocks[0].type).toBe('list');
      |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        ^ Error: locator.click: Error: strict mode violation: getByRole('list', { name: 'Notes', exact: true }).getByRole('button') resolved to 2 elements:
  563 | });
  564 | test('note links review: passage-only saved Notes preview reopens with plain reference label',async({page})=>{
  565 |  await setup(page);await firstNote(page);await insertNoteReference(page,'Gen 1');await expect(page.getByRole('status').filter({hasText:'Draft saved'})).toBeVisible();await page.getByRole('button',{name:'Back to Studies',exact:true}).click();const button=page.getByRole('list',{name:'Notes',exact:true}).getByRole('button');await expect(button).toHaveText('Genesis 1');await button.click();await expect(page.getByLabel('Note text',{exact:true}).locator('[data-note-passage]')).toHaveText('Genesis 1');
  566 | });
  567 | test('note links review: noncanonical stored Unicode HTML-looking label stays plain and exact',async({page})=>{
  568 |  const catalogue=require('../src/generated/reference-catalogue.json'),label='שָׁלוֹם 😀 <b>stored</b> e\u0301',reference={catalogue_id:catalogue.catalogue_id,catalogue_version:catalogue.catalogue_version,versification_id:catalogue.books.find(b=>b.book_id==='Gen').versification_id,book_id:'Gen',target:{kind:'chapter',chapter:1}},noteValue={document:{version:2,blocks:[{type:'paragraph',direction:'rtl',content:[{type:'passage_link',reference,label}]}]},connections:[],highlights:[]};const {requests}=await setup(page,{noteValue});await firstNote(page);const editor=page.getByLabel('Note text',{exact:true}),atom=editor.locator('[data-note-passage]');await expect(atom).toHaveText(label);await expect(atom.locator('b')).toHaveCount(0);await page.getByRole('button',{name:'Read note',exact:true}).click();await expect(atom).toHaveText(label);await page.getByRole('button',{name:'Edit note',exact:true}).click();await editor.press('End');await editor.press('!');await expect(page.getByRole('status').filter({hasText:'Draft saved'})).toBeVisible();const saved=requests.filter(r=>r.method==='PUT').at(-1).payload.value;expect(saved.document.blocks[0].content.find(i=>i.type==='passage_link')).toEqual({type:'passage_link',reference,label});
  569 | });
  570 | test('note links review: ordinary copied metadata never acquires native-history ownership',async({page})=>{
  571 |  const {requests}=await setup(page);await firstNote(page);const editor=page.getByLabel('Note text',{exact:true});await insertNoteReference(page,'Gen 1');await expect(page.getByRole('status').filter({hasText:'Draft saved'})).toBeVisible();const before=requests.filter(r=>r.method==='PUT').length;await editor.locator('[data-note-passage]').evaluate(el=>{el.replaceWith(el.cloneNode(true));document.querySelector('[aria-label="Note text"]').dispatchEvent(new InputEvent('input',{bubbles:true}));});await expect(page.getByRole('status')).toContainText('Changes not saved');await expect(page.getByRole('button',{name:'Read note',exact:true})).toBeDisabled();await page.waitForTimeout(600);expect(requests.filter(r=>r.method==='PUT')).toHaveLength(before);
  572 | });
  573 | for(const method of ['paste','keyless input'])test(`note links review: ${method} at final atom uses editable caret boundary`,async({page})=>{
  574 |  await setup(page);await firstNote(page);const editor=page.getByLabel('Note text',{exact:true});await insertNoteReference(page,'Gen 1');await editor.press('ControlOrMeta+z');await editor.press('ControlOrMeta+Shift+z');await editor.press('End');if(method==='paste')await editor.evaluate(el=>{const data=new DataTransfer();data.setData('text/plain',' pasted');el.dispatchEvent(new ClipboardEvent('paste',{bubbles:true,clipboardData:data}));});else await page.keyboard.insertText(' keyless');await expect(editor).toHaveText('Genesis 1'+(method==='paste'?' pasted':' keyless'));await expect(page.getByRole('status').filter({hasText:'Draft saved'})).toBeVisible();
  575 | });
  576 | 
  577 | for(const prefix of ['', 'Keep'])for(const action of ['Backspace','Delete','beforeinput backward'])test(`note links deletion: ${action} on ${prefix||'empty'} removes one owned atom and native Undo Redo retains version2`,async({page})=>{
  578 |  const {requests}=await setup(page);await firstNote(page);const editor=page.getByLabel('Note text',{exact:true});if(prefix)await editor.pressSequentially(prefix);await insertNoteReference(page,'Gen 1');await editor.locator('[data-note-passage]').evaluate((atom,action)=>{const editor=document.querySelector('[aria-label="Note text"]'),range=document.createRange();if(action==='Delete')range.setStartBefore(atom);else range.setStartAfter(atom);range.collapse(true);editor.focus();getSelection().removeAllRanges();getSelection().addRange(range);if(action==='beforeinput backward'){editor.dataset.backwardInputs='0';editor.addEventListener('keydown',event=>event.stopImmediatePropagation(),{capture:true,once:true});editor.addEventListener('beforeinput',event=>{if(event.inputType==='deleteContentBackward')editor.dataset.backwardInputs=String(Number(editor.dataset.backwardInputs)+1);});}},action);await editor.press(action==='Delete'?'Delete':'Backspace');await expect(editor.locator('[data-note-passage]')).toHaveCount(0);await expect(editor).toHaveText(prefix);if(action==='beforeinput backward')await expect(editor).toHaveAttribute('data-backward-inputs','1');await expect(page.getByRole('status').filter({hasText:'Draft saved'})).toBeVisible();expect(requests.filter(r=>r.method==='PUT').at(-1).payload.value.document.version).toBe(2);
  579 |  await editor.press('ControlOrMeta+z');await expect(editor.locator('[data-note-passage]')).toHaveText('Genesis 1');await expect(editor).toHaveText(prefix+'Genesis 1');await expect(page.getByRole('status').filter({hasText:'Draft saved'})).toBeVisible();expect(requests.filter(r=>r.method==='PUT').at(-1).payload.value.document.version).toBe(2);await editor.press('ControlOrMeta+Shift+z');await expect(editor.locator('[data-note-passage]')).toHaveCount(0);await expect(editor).toHaveText(prefix);await expect(page.getByRole('status').filter({hasText:'Draft saved'})).toBeVisible();expect(requests.filter(r=>r.method==='PUT').at(-1).payload.value.document.version).toBe(2);
  580 | });
  581 | 
  582 | test('library search finds saved results beyond the first page and returns at loaded depth',async({page})=>{
  583 |  await setup(page);
  584 |  const reads=[];
  585 |  await page.route('**/api/studies/search',async r=>{
  586 |   const body=r.request().postDataJSON();reads.push(body);
  587 |   const items=body.query==='שלום'?[{...attribution,id:study,title:'Saved Hebrew study',revision:'1'}]:[{...attribution,id:study,title:'Untitled study',revision:'1'}];
  588 |   await r.fulfill({json:{items,next_cursor:body.cursor?null:'search-page-two'}});
  589 |  });
  590 |  await page.goto('/');await page.getByRole('button',{name:'Studies',exact:true}).click();
  591 |  await page.getByRole('textbox',{name:'Search studies',exact:true}).fill('שלום');
  592 |  await page.getByRole('button',{name:'Search',exact:true}).click();
  593 |  await expect(page.getByRole('button',{name:'Saved Hebrew study',exact:true})).toBeVisible();
  594 |  await page.getByRole('button',{name:'More studies',exact:true}).click();
  595 |  await expect(page.getByRole('button',{name:'More studies',exact:true})).toHaveCount(0);
  596 |  await expect(page.getByRole('button',{name:'Saved Hebrew study',exact:true})).toHaveCount(1);
  597 |  await page.getByRole('button',{name:'Saved Hebrew study',exact:true}).click();
  598 |  await page.getByRole('button',{name:'Leave study',exact:true}).click();
  599 |  await expect(page.getByRole('textbox',{name:'Search studies',exact:true})).toHaveValue('שלום');
  600 |  await expect.poll(()=>reads.filter(x=>x.query==='שלום').length).toBe(4);
  601 |  expect(reads.filter(x=>x.query==='שלום').map(x=>x.cursor??null)).toEqual([null,'search-page-two',null,'search-page-two']);
  602 |  expect(new URL(page.url()).search).not.toContain('שלום');
  603 |  expect(await page.evaluate(()=>JSON.stringify(localStorage)+JSON.stringify(sessionStorage))).not.toContain('שלום');
  604 | });
  605 | 
  606 | test('library search candidate Enter Clear and literal Unicode terms stay in read bodies',async({page})=>{
  607 |  const reads=[];await setup(page,{search:async(r,body)=>{reads.push(body);return r.fulfill({json:{items:[{...attribution,id:study,title:body.query||'Whole library',revision:'1'}],next_cursor:null}});}});
  608 |  await page.goto('/');await page.getByRole('button',{name:'Studies',exact:true}).click();
  609 |  const input=page.getByRole('textbox',{name:'Search studies',exact:true});
  610 |  await expect(page.getByRole('button',{name:'Whole library',exact:true})).toBeVisible();
  611 |  for(const query of ['Genesis 1:31–2:3','בראשית א:לא–ב:ג','Matthew','café 100% _ \\ "']){
  612 |   const count=reads.length;await input.fill(query);expect(reads.length).toBe(count);await input.press('Enter');await expect(page.getByRole('list',{name:'Studies',exact:true})).toContainText(query);
  613 |  }
  614 |  await page.getByRole('button',{name:'Clear',exact:true}).click();await expect(input).toHaveValue('');await expect(page.getByRole('button',{name:'Whole library',exact:true})).toBeVisible();
  615 |  expect(reads.every(body=>Object.keys(body).sort().join(',')==='cursor,query')).toBe(true);
  616 |  expect(await page.evaluate(()=>JSON.stringify(localStorage)+JSON.stringify(sessionStorage))).not.toContain('café');
  617 |  expect(new URL(page.url()).search).not.toContain('query');
  618 | });
  619 | 
  620 | for(const late of ['success','denial'])test(`library search ignores late old-query ${late} and loading finalizers`,async({page})=>{
  621 |  let release;await setup(page,{search:async(r,body)=>{
  622 |   if(body.query==='old'){await new Promise(resolve=>release=resolve);return r.fulfill(late==='denial'?{status:403,json:{code:'studies_access_denied'}}:{json:{items:[{...attribution,id:study,title:'Old private title',revision:'1'}],next_cursor:null}});}
  623 |   return r.fulfill({json:{items:body.query?[{...attribution,id:study,title:'Current title',revision:'1'}]:[],next_cursor:null}});
  624 |  }});
  625 |  await page.goto('/');await page.getByRole('button',{name:'Studies',exact:true}).click();const input=page.getByRole('textbox',{name:'Search studies',exact:true});
  626 |  await input.fill('old');await input.press('Enter');await expect.poll(()=>!!release).toBe(true);
  627 |  await input.fill('current');await input.press('Enter');await expect(page.getByRole('button',{name:'Current title',exact:true})).toBeVisible();release();
  628 |  await page.waitForTimeout(100);await expect(page.getByRole('button',{name:'Current title',exact:true})).toBeVisible();await expect(page.getByText('Old private title',{exact:true})).toHaveCount(0);await expect(page.getByText('Studies access is unavailable for this account.',{exact:false})).toHaveCount(0);
  629 | });
  630 | 
  631 | test('library search hides unavailable pages retries applied input and clears on denial',async({page})=>{
  632 |  let failure=0;const reads=[];await setup(page,{search:async(r,body)=>{reads.push(body.query);return r.fulfill(failure?{status:failure,json:{code:failure===403?'studies_access_denied':'studies_access_unavailable'}}:{json:{items:[{...attribution,id:study,title:'Verified title',revision:'1'}],next_cursor:'next'}});}});
  633 |  await page.goto('/');await page.getByRole('button',{name:'Studies',exact:true}).click();const input=page.getByRole('textbox',{name:'Search studies',exact:true});await input.fill('applied');await input.press('Enter');await expect(page.getByRole('button',{name:'Verified title',exact:true})).toBeVisible();
  634 |  failure=503;await page.getByRole('button',{name:'More studies',exact:true}).click();await expect(page.getByRole('button',{name:'Verified title',exact:true})).toHaveCount(0);await expect(input).toHaveValue('applied');
  635 |  await input.fill('candidate only');failure=0;await page.getByRole('button',{name:'Retry search',exact:true}).click();await expect(page.getByRole('button',{name:'Verified title',exact:true})).toBeVisible();expect(reads.at(-1)).toBe('applied');await expect(input).toHaveValue('candidate only');
  636 |  failure=403;await page.getByRole('button',{name:'More studies',exact:true}).click();await expect(input).toHaveValue('');await expect(page.getByRole('button',{name:'Verified title',exact:true})).toHaveCount(0);
  637 | });
  638 | 
  639 | test('library search deduplicates More and rejects a late page after query change',async({page})=>{
  640 |  let release;const reads=[];await setup(page,{search:async(r,body)=>{reads.push(body);if(body.cursor){await new Promise(resolve=>release=resolve);return r.fulfill({json:{items:[{...attribution,id:study,title:'Late page',revision:'1'}],next_cursor:null}});}return r.fulfill({json:{items:[{...attribution,id:study,title:body.query||'First page',revision:'1'}],next_cursor:'next'}});}});
  641 |  await page.goto('/');await page.getByRole('button',{name:'Studies',exact:true}).click();await page.getByRole('button',{name:'More studies',exact:true}).dblclick();await expect.poll(()=>!!release).toBe(true);expect(reads.filter(x=>x.cursor).length).toBe(1);
  642 |  await page.getByRole('textbox',{name:'Search studies',exact:true}).fill('New query');await page.getByRole('button',{name:'Search',exact:true}).click();await expect(page.getByRole('button',{name:'New query',exact:true})).toBeVisible();release();await page.waitForTimeout(100);await expect(page.getByRole('button',{name:'Late page',exact:true})).toHaveCount(0);
  643 | });
  644 | 
  645 | test('library search restores multi-page scroll and stable result focus after refreshed return',async({page})=>{
  646 |  let reads=0;await setup(page,{search:async(r,body)=>{reads++;const offset=body.cursor?20:0;const items=Array.from({length:20},(_,index)=>{const n=offset+index;return {...attribution,id:n===35?study:`30000000-0000-4000-8000-${String(n+10).padStart(12,'0')}`,title:`Result ${n}`,revision:'1'};});return r.fulfill({json:{items,next_cursor:body.cursor?null:'second'}});}});
  647 |  await page.goto('/');await page.getByRole('button',{name:'Studies',exact:true}).click();await page.getByRole('button',{name:'More studies',exact:true}).click();const result=page.getByRole('button',{name:'Result 35',exact:true});await result.scrollIntoViewIfNeeded();await result.focus();const before=await page.getByRole('complementary',{name:'Study tools',exact:true}).evaluate(el=>el.scrollTop);expect(before).toBeGreaterThan(0);await result.click();await page.getByRole('button',{name:'Leave study',exact:true}).click();
  648 |  await expect.poll(()=>reads).toBe(4);await expect(result).toBeFocused();await expect.poll(()=>page.getByRole('complementary',{name:'Study tools',exact:true}).evaluate(el=>el.scrollTop)).toBeGreaterThan(before-50);
  649 | });
  650 | 
  651 | test('library search account replacement clears candidates pages and rejects late denial',async({page})=>{
  652 |  let release;await setup(page,{search:async(r,body)=>{if(body.query){await new Promise(resolve=>release=resolve);return r.fulfill({status:403,json:{code:'studies_access_denied'}});}return r.fulfill({json:{items:[],next_cursor:null}});}});
  653 |  await page.goto('/');await page.getByRole('button',{name:'Studies',exact:true}).click();await page.getByRole('textbox',{name:'Search studies',exact:true}).fill('old private writing');await page.getByRole('button',{name:'Search',exact:true}).click();await expect.poll(()=>!!release).toBe(true);
  654 |  await page.route('**/auth/v1/token*',r=>r.fulfill({json:{...session,access_token:'other-account',user:{...session.user,id:'10000000-0000-4000-8000-000000000002'}}}));await page.evaluate(async()=>{const {supabase}=await import('/src/lib/supabase.ts');await supabase.auth.signInWithPassword({email:'other@example.invalid',password:'fixture'});});
  655 |  await expect(page.getByRole('button',{name:'Studies',exact:true})).toHaveAttribute('aria-pressed','false');await expect(page.getByRole('button',{name:'Analysis',exact:true})).toHaveAttribute('aria-pressed','false');await expect(page.getByRole('textbox',{name:'Search studies',exact:true})).toHaveCount(0);await page.getByRole('button',{name:'Studies',exact:true}).click();await expect(page.getByRole('textbox',{name:'Search studies',exact:true})).toHaveValue('');await page.getByRole('button',{name:'Search',exact:true}).click();await expect(page.getByText('No saved studies found.',{exact:true})).toBeVisible();release();await page.waitForTimeout(100);await expect(page.getByText('Studies access is unavailable for this account.',{exact:false})).toHaveCount(0);
  656 | });
  657 | 
  658 | test('library search old completion cannot stop current loading',async({page})=>{
  659 |  const releases={};await setup(page,{search:async(r,body)=>{if(body.query)await new Promise(resolve=>releases[body.query]=resolve);return r.fulfill({json:{items:[],next_cursor:null}});}});
  660 |  await page.goto('/');await page.getByRole('button',{name:'Studies',exact:true}).click();const input=page.getByRole('textbox',{name:'Search studies',exact:true});await input.fill('old');await input.press('Enter');await expect.poll(()=>!!releases.old).toBe(true);await input.fill('new');await input.press('Enter');await expect.poll(()=>!!releases.new).toBe(true);releases.old();await page.waitForTimeout(100);await expect(page.getByRole('status').filter({hasText:'Loading studies…'})).toBeVisible();releases.new();await expect(page.getByRole('status').filter({hasText:'Loading studies…'})).toHaveCount(0);
  661 | });
  662 | 
```