# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: personal-notes.spec.cjs >> review tabs E3 distinct long note contexts restore their own inspector scroll without focus theft
- Location: tests/personal-notes.spec.cjs:1445:1

# Error details

```
Error: expect(received).toBeLessThan(expected)

Expected: < 3
Received:   10

Call Log:
- Timeout 5000ms exceeded while waiting on the predicate
```

# Page snapshot

```yaml
- generic [ref=e3]:
  - banner [ref=e5]:
    - generic [ref=e6]:
      - generic [ref=e7]: Scribes' Well
      - button "Sign out" [ref=e11]
  - main [ref=e15]:
    - generic [ref=e16]:
      - generic [ref=e17]:
        - tablist "Workspace tabs" [ref=e18]:
          - generic [ref=e19]:
            - tab "Genesis 1" [ref=e20]
            - button "Rename tab 1" [ref=e21]: Rename
            - button "Close tab 1" [ref=e22]: ×
          - generic [ref=e23]:
            - tab "Genesis 1" [active] [selected] [ref=e24]
            - button "Rename tab 2" [ref=e25]: Rename
            - button "Close tab 2" [ref=e26]: ×
        - button "New workspace tab" [ref=e27]: + New tab
      - generic [ref=e28]:
        - button "Add reader pane" [ref=e29]
        - button "Enter focus mode" [ref=e32]: Focus mode
      - navigation "Reader tools" [ref=e38]:
        - button "Studies" [ref=e39]
        - button "Analysis" [pressed] [ref=e40]
        - generic [ref=e41]: Study A
      - complementary "Study tools" [ref=e43]:
        - button "Return to reader" [ref=e44]
        - generic [ref=e45]:
          - tablist "Analysis" [ref=e46]:
            - tab "Word" [disabled] [ref=e47]
            - tab "Occurrences" [disabled] [ref=e48]
            - tab "Notes" [selected] [ref=e49]
          - region "Note editor" [ref=e52]:
            - heading "Notes" [level=3] [ref=e53]
            - button "Delete note" [ref=e54]
            - button "Delete study" [ref=e55]
            - paragraph [ref=e56]: Study A
            - button "Read note" [ref=e57]
            - toolbar "Note formatting" [ref=e58]:
              - button "Bold" [ref=e59]: B
              - button "Italic" [ref=e60]: I
              - button "Bullet list" [ref=e61]
              - button "Numbered list" [ref=e62]
              - button "Link" [ref=e63]
              - button "Insert passage reference" [ref=e66]
              - generic [ref=e69]:
                - text: Direction
                - combobox "Paragraph direction" [ref=e70]:
                  - option "Auto" [selected]
                  - option "Left to right"
                  - option "Right to left"
            - textbox "Note text" [ref=e71]:
              - paragraph [ref=e72]: 40000000-0000-4000-8000-000000000002 paragraph 0
              - paragraph [ref=e73]: 40000000-0000-4000-8000-000000000002 paragraph 1
              - paragraph [ref=e74]: 40000000-0000-4000-8000-000000000002 paragraph 2
              - paragraph [ref=e75]: 40000000-0000-4000-8000-000000000002 paragraph 3
              - paragraph [ref=e76]: 40000000-0000-4000-8000-000000000002 paragraph 4
              - paragraph [ref=e77]: 40000000-0000-4000-8000-000000000002 paragraph 5
              - paragraph [ref=e78]: 40000000-0000-4000-8000-000000000002 paragraph 6
              - paragraph [ref=e79]: 40000000-0000-4000-8000-000000000002 paragraph 7
              - paragraph [ref=e80]: 40000000-0000-4000-8000-000000000002 paragraph 8
              - paragraph [ref=e81]: 40000000-0000-4000-8000-000000000002 paragraph 9
              - paragraph [ref=e82]: 40000000-0000-4000-8000-000000000002 paragraph 10
              - paragraph [ref=e83]: 40000000-0000-4000-8000-000000000002 paragraph 11
              - paragraph [ref=e84]: 40000000-0000-4000-8000-000000000002 paragraph 12
              - paragraph [ref=e85]: 40000000-0000-4000-8000-000000000002 paragraph 13
              - paragraph [ref=e86]: 40000000-0000-4000-8000-000000000002 paragraph 14
              - paragraph [ref=e87]: 40000000-0000-4000-8000-000000000002 paragraph 15
              - paragraph [ref=e88]: 40000000-0000-4000-8000-000000000002 paragraph 16
              - paragraph [ref=e89]: 40000000-0000-4000-8000-000000000002 paragraph 17
              - paragraph [ref=e90]: 40000000-0000-4000-8000-000000000002 paragraph 18
              - paragraph [ref=e91]: 40000000-0000-4000-8000-000000000002 paragraph 19
              - paragraph [ref=e92]: 40000000-0000-4000-8000-000000000002 paragraph 20
              - paragraph [ref=e93]: 40000000-0000-4000-8000-000000000002 paragraph 21
              - paragraph [ref=e94]: 40000000-0000-4000-8000-000000000002 paragraph 22
              - paragraph [ref=e95]: 40000000-0000-4000-8000-000000000002 paragraph 23
              - paragraph [ref=e96]: 40000000-0000-4000-8000-000000000002 paragraph 24
              - paragraph [ref=e97]: 40000000-0000-4000-8000-000000000002 paragraph 25
              - paragraph [ref=e98]: 40000000-0000-4000-8000-000000000002 paragraph 26
              - paragraph [ref=e99]: 40000000-0000-4000-8000-000000000002 paragraph 27
              - paragraph [ref=e100]: 40000000-0000-4000-8000-000000000002 paragraph 28
              - paragraph [ref=e101]: 40000000-0000-4000-8000-000000000002 paragraph 29
              - paragraph [ref=e102]: 40000000-0000-4000-8000-000000000002 paragraph 30
              - paragraph [ref=e103]: 40000000-0000-4000-8000-000000000002 paragraph 31
              - paragraph [ref=e104]: 40000000-0000-4000-8000-000000000002 paragraph 32
              - paragraph [ref=e105]: 40000000-0000-4000-8000-000000000002 paragraph 33
              - paragraph [ref=e106]: 40000000-0000-4000-8000-000000000002 paragraph 34
              - paragraph [ref=e107]: 40000000-0000-4000-8000-000000000002 paragraph 35
              - paragraph [ref=e108]: 40000000-0000-4000-8000-000000000002 paragraph 36
              - paragraph [ref=e109]: 40000000-0000-4000-8000-000000000002 paragraph 37
              - paragraph [ref=e110]: 40000000-0000-4000-8000-000000000002 paragraph 38
              - paragraph [ref=e111]: 40000000-0000-4000-8000-000000000002 paragraph 39
              - paragraph [ref=e112]: 40000000-0000-4000-8000-000000000002 paragraph 40
              - paragraph [ref=e113]: 40000000-0000-4000-8000-000000000002 paragraph 41
              - paragraph [ref=e114]: 40000000-0000-4000-8000-000000000002 paragraph 42
              - paragraph [ref=e115]: 40000000-0000-4000-8000-000000000002 paragraph 43
              - paragraph [ref=e116]: 40000000-0000-4000-8000-000000000002 paragraph 44
              - paragraph [ref=e117]: 40000000-0000-4000-8000-000000000002 paragraph 45
              - paragraph [ref=e118]: 40000000-0000-4000-8000-000000000002 paragraph 46
              - paragraph [ref=e119]: 40000000-0000-4000-8000-000000000002 paragraph 47
              - paragraph [ref=e120]: 40000000-0000-4000-8000-000000000002 paragraph 48
              - paragraph [ref=e121]: 40000000-0000-4000-8000-000000000002 paragraph 49
              - paragraph [ref=e122]: 40000000-0000-4000-8000-000000000002 paragraph 50
              - paragraph [ref=e123]: 40000000-0000-4000-8000-000000000002 paragraph 51
              - paragraph [ref=e124]: 40000000-0000-4000-8000-000000000002 paragraph 52
              - paragraph [ref=e125]: 40000000-0000-4000-8000-000000000002 paragraph 53
              - paragraph [ref=e126]: 40000000-0000-4000-8000-000000000002 paragraph 54
              - paragraph [ref=e127]: 40000000-0000-4000-8000-000000000002 paragraph 55
              - paragraph [ref=e128]: 40000000-0000-4000-8000-000000000002 paragraph 56
              - paragraph [ref=e129]: 40000000-0000-4000-8000-000000000002 paragraph 57
              - paragraph [ref=e130]: 40000000-0000-4000-8000-000000000002 paragraph 58
              - paragraph [ref=e131]: 40000000-0000-4000-8000-000000000002 paragraph 59
              - paragraph [ref=e132]: 40000000-0000-4000-8000-000000000002 paragraph 60
              - paragraph [ref=e133]: 40000000-0000-4000-8000-000000000002 paragraph 61
              - paragraph [ref=e134]: 40000000-0000-4000-8000-000000000002 paragraph 62
              - paragraph [ref=e135]: 40000000-0000-4000-8000-000000000002 paragraph 63
              - paragraph [ref=e136]: 40000000-0000-4000-8000-000000000002 paragraph 64
              - paragraph [ref=e137]: 40000000-0000-4000-8000-000000000002 paragraph 65
              - paragraph [ref=e138]: 40000000-0000-4000-8000-000000000002 paragraph 66
              - paragraph [ref=e139]: 40000000-0000-4000-8000-000000000002 paragraph 67
              - paragraph [ref=e140]: 40000000-0000-4000-8000-000000000002 paragraph 68
              - paragraph [ref=e141]: 40000000-0000-4000-8000-000000000002 paragraph 69
              - paragraph [ref=e142]: 40000000-0000-4000-8000-000000000002 paragraph 70
              - paragraph [ref=e143]: 40000000-0000-4000-8000-000000000002 paragraph 71
              - paragraph [ref=e144]: 40000000-0000-4000-8000-000000000002 paragraph 72
              - paragraph [ref=e145]: 40000000-0000-4000-8000-000000000002 paragraph 73
              - paragraph [ref=e146]: 40000000-0000-4000-8000-000000000002 paragraph 74
              - paragraph [ref=e147]: 40000000-0000-4000-8000-000000000002 paragraph 75
              - paragraph [ref=e148]: 40000000-0000-4000-8000-000000000002 paragraph 76
              - paragraph [ref=e149]: 40000000-0000-4000-8000-000000000002 paragraph 77
              - paragraph [ref=e150]: 40000000-0000-4000-8000-000000000002 paragraph 78
              - paragraph [ref=e151]: 40000000-0000-4000-8000-000000000002 paragraph 79
              - paragraph [ref=e152]: 40000000-0000-4000-8000-000000000002 paragraph 80
              - paragraph [ref=e153]: 40000000-0000-4000-8000-000000000002 paragraph 81
              - paragraph [ref=e154]: 40000000-0000-4000-8000-000000000002 paragraph 82
              - paragraph [ref=e155]: 40000000-0000-4000-8000-000000000002 paragraph 83
              - paragraph [ref=e156]: 40000000-0000-4000-8000-000000000002 paragraph 84
              - paragraph [ref=e157]: 40000000-0000-4000-8000-000000000002 paragraph 85
              - paragraph [ref=e158]: 40000000-0000-4000-8000-000000000002 paragraph 86
              - paragraph [ref=e159]: 40000000-0000-4000-8000-000000000002 paragraph 87
              - paragraph [ref=e160]: 40000000-0000-4000-8000-000000000002 paragraph 88
              - paragraph [ref=e161]: 40000000-0000-4000-8000-000000000002 paragraph 89
              - paragraph [ref=e162]: 40000000-0000-4000-8000-000000000002 paragraph 90
              - paragraph [ref=e163]: 40000000-0000-4000-8000-000000000002 paragraph 91
              - paragraph [ref=e164]: 40000000-0000-4000-8000-000000000002 paragraph 92
              - paragraph [ref=e165]: 40000000-0000-4000-8000-000000000002 paragraph 93
              - paragraph [ref=e166]: 40000000-0000-4000-8000-000000000002 paragraph 94
              - paragraph [ref=e167]: 40000000-0000-4000-8000-000000000002 paragraph 95
              - paragraph [ref=e168]: 40000000-0000-4000-8000-000000000002 paragraph 96
              - paragraph [ref=e169]: 40000000-0000-4000-8000-000000000002 paragraph 97
              - paragraph [ref=e170]: 40000000-0000-4000-8000-000000000002 paragraph 98
              - paragraph [ref=e171]: 40000000-0000-4000-8000-000000000002 paragraph 99
              - paragraph [ref=e172]: 40000000-0000-4000-8000-000000000002 paragraph 100
              - paragraph [ref=e173]: 40000000-0000-4000-8000-000000000002 paragraph 101
              - paragraph [ref=e174]: 40000000-0000-4000-8000-000000000002 paragraph 102
              - paragraph [ref=e175]: 40000000-0000-4000-8000-000000000002 paragraph 103
              - paragraph [ref=e176]: 40000000-0000-4000-8000-000000000002 paragraph 104
              - paragraph [ref=e177]: 40000000-0000-4000-8000-000000000002 paragraph 105
              - paragraph [ref=e178]: 40000000-0000-4000-8000-000000000002 paragraph 106
              - paragraph [ref=e179]: 40000000-0000-4000-8000-000000000002 paragraph 107
              - paragraph [ref=e180]: 40000000-0000-4000-8000-000000000002 paragraph 108
              - paragraph [ref=e181]: 40000000-0000-4000-8000-000000000002 paragraph 109
              - paragraph [ref=e182]: 40000000-0000-4000-8000-000000000002 paragraph 110
              - paragraph [ref=e183]: 40000000-0000-4000-8000-000000000002 paragraph 111
              - paragraph [ref=e184]: 40000000-0000-4000-8000-000000000002 paragraph 112
              - paragraph [ref=e185]: 40000000-0000-4000-8000-000000000002 paragraph 113
              - paragraph [ref=e186]: 40000000-0000-4000-8000-000000000002 paragraph 114
              - paragraph [ref=e187]: 40000000-0000-4000-8000-000000000002 paragraph 115
              - paragraph [ref=e188]: 40000000-0000-4000-8000-000000000002 paragraph 116
              - paragraph [ref=e189]: 40000000-0000-4000-8000-000000000002 paragraph 117
              - paragraph [ref=e190]: 40000000-0000-4000-8000-000000000002 paragraph 118
              - paragraph [ref=e191]: 40000000-0000-4000-8000-000000000002 paragraph 119
            - status [ref=e192]: Draft saved
            - button "Back to Studies" [ref=e193]
```

# Test source

```ts
  1346 |  const restore=page.getByRole('dialog',{name:'Choose tab to close and restore'});await expect(restore).toBeVisible();const idx=await page.evaluate(()=>history.state.idx);
  1347 |  await restore.getByRole('button',{name:/Close tab 1:/}).click();const consent=page.getByRole('dialog',{name:'Changes not saved'});await expect(consent).toBeVisible();await consent.getByRole('button',{name:'Stay',exact:true}).click();await expect(consent).toHaveCount(0);await expect(restore).toHaveCount(0);await expect(page.getByRole('tablist',{name:'Workspace tabs'}).getByRole('tab')).toHaveCount(12);expect(await page.evaluate(()=>history.state.idx)).toBe(idx);
  1348 |  const publicEntry=await page.evaluate(()=>JSON.stringify(history.state.usr.scribeswellReader));
  1349 |  await page.getByRole('button',{name:'Studies',exact:true}).click();await page.getByRole('button',{name:'Untitled study',exact:true}).click();await expect(page.getByRole('button',{name:'Add current passage',exact:true})).toHaveCount(0);await expect(page.getByRole('button',{name:'Add passage',exact:true})).toBeVisible();
  1350 |  await page.evaluate(()=>{const scroll=document.querySelector('[data-reader-scroll]');scroll.dispatchEvent(new WheelEvent('wheel',{bubbles:true}));scroll.dispatchEvent(new Event('scroll',{bubbles:true}));});await page.waitForTimeout(200);expect(await page.evaluate(()=>JSON.stringify(history.state.usr.scribeswellReader))).toBe(publicEntry);
  1351 |  await page.getByRole('button',{name:'Choose tab to close and restore',exact:true}).click();await expect(restore).toBeVisible();await restore.getByRole('button',{name:'Cancel',exact:true}).click();
  1352 |  await page.getByRole('tablist',{name:'Workspace tabs'}).getByRole('tab').first().click();await expect(page.getByRole('button',{name:'Choose tab to close and restore',exact:true})).toHaveCount(0);if(await page.getByRole('button',{name:'Analysis',exact:true}).getAttribute('aria-pressed')!=='true')await page.getByRole('button',{name:'Analysis',exact:true}).click();await expect(page.getByRole('textbox',{name:'Note text',exact:true})).toHaveText('sole unsaved context');
  1353 |  await page.goBack();await expect(restore).toBeVisible();const replayIndex=await page.evaluate(()=>history.state.idx);await restore.getByRole('button',{name:/Close tab 1:/}).click();await consent.getByRole('button',{name:'Close anyway',exact:true}).click();await expect(restore).toHaveCount(0);await expect(page.getByRole('tablist',{name:'Workspace tabs'}).getByRole('tab')).toHaveCount(12);expect(await page.evaluate(()=>history.state.idx)).toBe(replayIndex);await expect(page.getByRole('button',{name:'Analysis',exact:true})).toHaveAttribute('aria-pressed','false');await page.getByRole('button',{name:'Analysis',exact:true}).click();await expect(page.getByRole('textbox',{name:'Note text',exact:true})).toHaveCount(0);await expect(page.getByText('Select a note in Studies.',{exact:true})).toBeVisible();
  1354 | });
  1355 | 
  1356 | test('workspace tabs closed history never restores inherited private associations',async({page})=>{
  1357 |  await setup(page);await firstNote(page);await page.getByRole('textbox',{name:'Note text',exact:true}).fill('private lane remains A');await expect(page.getByRole('status').filter({hasText:'Draft saved'})).toBeVisible();
  1358 |  await page.getByRole('button',{name:'New workspace tab',exact:true}).click();await page.getByRole('dialog',{name:'Book and chapter selector'}).getByRole('button',{name:'Cancel',exact:true}).click();await page.getByRole('button',{name:'Close tab 2',exact:true}).click();await page.goBack();
  1359 |  await expect(page.getByRole('tablist',{name:'Workspace tabs'}).getByRole('tab')).toHaveCount(2);await expect(page.getByRole('button',{name:'Analysis',exact:true})).toHaveAttribute('aria-pressed','false');await page.getByRole('button',{name:'Analysis',exact:true}).click();await expect(page.getByRole('textbox',{name:'Note text',exact:true})).toHaveCount(0);await expect(page.getByText('Select a note in Studies.',{exact:true})).toBeVisible();
  1360 |  await page.getByRole('tablist',{name:'Workspace tabs'}).getByRole('tab').first().click();await expect(page.getByRole('textbox',{name:'Note text',exact:true})).toHaveText('private lane remains A');
  1361 | });
  1362 | 
  1363 | test('workspace tabs mask all private labels during authentication loss and clear them on account replacement',async({page})=>{
  1364 |  const options={failPut:401};await setup(page,options);await firstNote(page);const rename=async(index,label)=>{await page.getByRole('button',{name:`Rename tab ${index}`,exact:true}).click();await page.getByLabel('Tab name',{exact:true}).fill(label);await page.getByRole('dialog',{name:'Rename workspace tab'}).getByRole('button',{name:'Save',exact:true}).click();};
  1365 |  await rename(1,'private label A');await page.getByRole('button',{name:'New workspace tab',exact:true}).click();await page.getByRole('dialog',{name:'Book and chapter selector'}).getByRole('button',{name:'Cancel',exact:true}).click();await rename(2,'private label B');await page.getByRole('button',{name:'Analysis',exact:true}).click();await page.getByRole('textbox',{name:'Note text',exact:true}).fill('auth failure input');await expect(page.getByRole('alert')).toContainText('Sign in');await expect(page.getByText('private label A',{exact:true})).toHaveCount(0);await expect(page.getByText('private label B',{exact:true})).toHaveCount(0);
  1366 |  await page.route('**/auth/v1/token*',r=>r.fulfill({json:{...session,access_token:'renewed-current'}}));await page.evaluate(async()=>{const {supabase}=await import('/src/lib/supabase.ts');await supabase.auth.signInWithPassword({email:'reader@example.invalid',password:'fixture'});});options.failPut=0;await page.getByRole('button',{name:'Retry Studies',exact:true}).click();await expect(page.getByText('private label A',{exact:true})).toBeVisible();await expect(page.getByText('private label B',{exact:true})).toBeVisible();
  1367 |  await page.route('**/auth/v1/token*',r=>r.fulfill({json:{...session,user:{...session.user,id:'10000000-0000-4000-8000-000000000002'}}}));await page.evaluate(async()=>{const {supabase}=await import('/src/lib/supabase.ts');await supabase.auth.signOut({scope:'local'});await supabase.auth.signInWithPassword({email:'other@example.invalid',password:'fixture'});});await expect(page.getByText('private label A',{exact:true})).toHaveCount(0);await expect(page.getByText('private label B',{exact:true})).toHaveCount(0);await expect(page.getByText('auth failure input',{exact:true})).toHaveCount(0);await page.getByRole('button',{name:'Add reader pane',exact:true}).click();await page.getByRole('dialog',{name:'Book and chapter selector'}).getByRole('button',{name:'Cancel',exact:true}).click();await expect(page.getByText('private label A',{exact:true})).toHaveCount(0);await expect(page.getByText('private label B',{exact:true})).toHaveCount(0);
  1368 | });
  1369 | 
  1370 | test('workspace tabs last-context discard retains only the original unknown save for explicit recovery',async({page})=>{
  1371 |  const options={failPut:503};const {requests}=await setup(page,options);await firstNote(page);await page.getByRole('button',{name:'New workspace tab',exact:true}).click();await page.getByRole('dialog',{name:'Book and chapter selector'}).getByRole('button',{name:'Cancel',exact:true}).click();await page.getByRole('button',{name:'Studies',exact:true}).click();await page.getByRole('button',{name:'Leave study',exact:true}).click();await page.getByRole('tablist',{name:'Workspace tabs'}).getByRole('tab').first().click();
  1372 |  await page.getByRole('textbox',{name:'Note text',exact:true}).fill('original unknown payload');await expect(page.getByRole('status').filter({hasText:'Changes not saved'})).toBeVisible();const original=structuredClone(requests.filter(r=>r.method==='PUT').at(-1).payload);await page.getByRole('textbox',{name:'Note text',exact:true}).fill('newer input explicitly abandoned');
  1373 |  await page.getByRole('button',{name:'Close tab 1',exact:true}).click();await page.getByRole('dialog',{name:'Changes not saved'}).getByRole('button',{name:'Close anyway',exact:true}).click();await expect(page.getByRole('tablist',{name:'Workspace tabs'}).getByRole('tab')).toHaveCount(1);await expect(page.locator('[aria-label="Note text"]')).toHaveCount(0);await expect(page.getByRole('button',{name:'Recover note save 1',exact:true})).toBeVisible();options.failPut=0;await page.getByRole('button',{name:'Recover note save 1',exact:true}).click();await expect(page.getByRole('button',{name:'Recover note save 1',exact:true})).toHaveCount(0);expect(requests.filter(r=>r.method==='PUT')).toHaveLength(2);expect(requests.filter(r=>r.method==='PUT').at(-1).payload).toEqual(original);await expect(page.getByRole('tablist',{name:'Workspace tabs'}).getByRole('tab')).toHaveCount(1);await expect(page.locator('[aria-label="Note text"]')).toHaveCount(0);expect(requests.filter(r=>r.method==='DELETE')).toHaveLength(0);
  1374 | });
  1375 | 
  1376 | test('workspace tabs direct Open in new tab retains a complete range with no picker and inherits only note identity',async({page})=>{
  1377 |  const {collection,requests}=await setup(page);const catalogue=require('../src/generated/reference-catalogue.json');const reference={catalogue_id:catalogue.catalogue_id,catalogue_version:catalogue.catalogue_version,versification_id:catalogue.books[0].versification_id,book_id:'Gen',target:{kind:'verse_range',start:{chapter:1,verse:31},end:{chapter:2,verse:3}}};collection.items.push({id:'50000000-0000-4000-8000-000000000001',reference});await firstNote(page);await page.getByRole('textbox',{name:'Note text',exact:true}).fill('associated original lane');await expect(page.getByRole('status').filter({hasText:'Draft saved'})).toBeVisible();await page.getByRole('button',{name:'Back to Studies',exact:true}).click();await page.getByRole('button',{name:'Open Genesis 1:31–2:3 in new tab',exact:true}).click();await expect(page.getByRole('dialog')).toHaveCount(0);expect(await page.evaluate(()=>JSON.parse(new URL(location.href).searchParams.get('reader')).panes[0].ref)).toEqual(reference);await expect(page.getByRole('button',{name:'Analysis',exact:true})).toHaveAttribute('aria-pressed','false');await page.getByRole('button',{name:'Analysis',exact:true}).click();await expect(page.getByRole('textbox',{name:'Note text',exact:true})).toHaveText('associated original lane');expect(requests.filter(r=>r.method==='POST'&&r.path.endsWith('/notes'))).toHaveLength(1);
  1378 | });
  1379 | 
  1380 | for(const target of ['note','study'])test(`workspace tabs confirmed ${target} deletion clears every matching private association and retains public tabs`,async({page})=>{
  1381 |  const {requests}=await setup(page);await firstNote(page);await page.getByRole('textbox',{name:'Note text',exact:true}).fill('shared deleted resource');await expect(page.getByRole('status').filter({hasText:'Draft saved'})).toBeVisible();await page.getByRole('button',{name:'New workspace tab',exact:true}).click();await page.getByRole('dialog',{name:'Book and chapter selector'}).getByRole('button',{name:'Cancel',exact:true}).click();await page.getByRole('button',{name:'Analysis',exact:true}).click();await page.getByRole('button',{name:`Delete ${target}`,exact:true}).click();await page.getByRole('dialog').getByRole('button',{name:`Delete ${target}`,exact:true}).click();await expect(page.getByRole('dialog')).toHaveCount(0);await expect(page.locator('[aria-label="Note text"]')).toHaveCount(0);await page.getByRole('tablist',{name:'Workspace tabs'}).getByRole('tab').first().click();await expect(page.locator('[aria-label="Note text"]')).toHaveCount(0);await expect(page.getByRole('tablist',{name:'Workspace tabs'}).getByRole('tab')).toHaveCount(2);expect(requests.filter(r=>r.method==='DELETE')).toHaveLength(1);if(page.viewportSize().width<768)await page.getByRole('button',{name:'Return to reader',exact:true}).click();await expect(page.getByRole('button',{name:/Word: בְּרֵאשִׁית/})).toBeVisible();
  1382 | });
  1383 | 
  1384 | test('workspace tabs inherited study outlines retain independent pagination cursors',async({page})=>{
  1385 |  await reviewLibrary(page,{notes:async(parent,cursor,view)=>cursor?{items:[view(parent,'40000000-0000-4000-8000-000000000003','Older outline note')],next_cursor:null}:{items:[view(parent,note,'A first')],next_cursor:'page-two'}});await page.getByRole('button',{name:'Study A',exact:true}).click();await expect(page.getByRole('button',{name:'More notes',exact:true})).toBeVisible();await page.getByRole('button',{name:'New workspace tab',exact:true}).click();await page.getByRole('dialog',{name:'Book and chapter selector'}).getByRole('button',{name:'Cancel',exact:true}).click();await page.getByRole('button',{name:'Studies',exact:true}).click();await page.getByRole('button',{name:'More notes',exact:true}).click();await expect(page.getByRole('button',{name:'Older outline note',exact:true})).toBeVisible();await expect(page.getByRole('button',{name:'More notes',exact:true})).toHaveCount(0);await page.getByRole('tablist',{name:'Workspace tabs'}).getByRole('tab').first().click();await expect(page.getByRole('button',{name:'Older outline note',exact:true})).toHaveCount(0);await page.getByRole('button',{name:'More notes',exact:true}).click();await expect(page.getByRole('button',{name:'Older outline note',exact:true})).toBeVisible();
  1386 | });
  1387 | 
  1388 | test('workspace tabs reject stale layout consent and clear open consent on account replacement',async({page})=>{
  1389 |  const options={failPut:503};await setup(page,options);await firstNote(page);await page.getByRole('button',{name:'New workspace tab',exact:true}).click();await page.getByRole('dialog',{name:'Book and chapter selector'}).getByRole('button',{name:'Cancel',exact:true}).click();await page.getByRole('button',{name:'Studies',exact:true}).click();await page.getByRole('button',{name:'Leave study',exact:true}).click();await page.getByRole('tablist',{name:'Workspace tabs'}).getByRole('tab').first().click();await page.getByRole('textbox',{name:'Note text',exact:true}).fill('consent origin');await expect(page.getByRole('status').filter({hasText:'Changes not saved'})).toBeVisible();await page.getByRole('button',{name:'Close tab 1',exact:true}).click();await expect(page.getByRole('dialog',{name:'Changes not saved'})).toBeVisible();
  1390 |  await page.getByRole('tablist',{name:'Workspace tabs'}).getByRole('tab').nth(1).evaluate(el=>el.click());await page.getByRole('dialog',{name:'Changes not saved'}).getByRole('button',{name:'Close anyway',exact:true}).click();await expect(page.getByRole('tablist',{name:'Workspace tabs'}).getByRole('tab')).toHaveCount(2);await page.getByRole('tablist',{name:'Workspace tabs'}).getByRole('tab').first().click();await expect(page.getByRole('textbox',{name:'Note text',exact:true})).toHaveText('consent origin');await page.getByRole('button',{name:'Close tab 1',exact:true}).click();await expect(page.getByRole('dialog',{name:'Changes not saved'})).toBeVisible();
  1391 |  await page.route('**/auth/v1/token*',r=>r.fulfill({json:{...session,user:{...session.user,id:'10000000-0000-4000-8000-000000000002'}}}));await page.evaluate(async()=>{const {supabase}=await import('/src/lib/supabase.ts');await supabase.auth.signOut({scope:'local'});await supabase.auth.signInWithPassword({email:'other@example.invalid',password:'fixture'});});await expect(page.getByRole('dialog',{name:'Changes not saved'})).toHaveCount(0);await expect(page.locator('[aria-label="Note text"]')).toHaveCount(0);await expect(page.getByRole('tablist',{name:'Workspace tabs'}).getByRole('tab')).toHaveCount(2);
  1392 | });
  1393 | 
  1394 | test('workspace tabs recheck last-context departure after a delayed replacement read without background focus',async({page})=>{
  1395 |  let release;await reviewLibrary(page,{read:async(parent,id,view)=>{if(id!==note)await new Promise(resolve=>release=resolve);return view(parent,id,id===note?'A first':'A second');}});await page.route('**/api/studies/*/notes/*',r=>r.request().method()==='PUT'?r.fulfill({status:503,json:{code:'studies_storage_unavailable'}}):r.fallback());await page.getByRole('button',{name:'Study A',exact:true}).click();await page.getByRole('button',{name:'A first',exact:true}).click();await page.getByRole('textbox',{name:'Note text',exact:true}).fill('last-context race input');await expect(page.getByRole('status').filter({hasText:'Changes not saved'})).toBeVisible();await page.getByRole('button',{name:'New workspace tab',exact:true}).click();await page.getByRole('dialog',{name:'Book and chapter selector'}).getByRole('button',{name:'Cancel',exact:true}).click();await page.getByRole('tablist',{name:'Workspace tabs'}).getByRole('tab').first().click();await page.getByRole('button',{name:'Back to Studies',exact:true}).click();await page.getByRole('button',{name:'A second',exact:true}).click();await expect.poll(()=>!!release).toBe(true);await page.getByRole('tablist',{name:'Workspace tabs'}).getByRole('tab').nth(1).click();await page.getByRole('button',{name:'Studies',exact:true}).click();await page.getByRole('button',{name:'Leave study',exact:true}).click();const response=page.waitForResponse('**/notes/40000000-0000-4000-8000-000000000002');release();await response;await expect(page.getByRole('dialog',{name:'Changes not saved'})).toHaveCount(0);await page.getByRole('tablist',{name:'Workspace tabs'}).getByRole('tab').first().click();if(await page.getByRole('button',{name:'Analysis',exact:true}).getAttribute('aria-pressed')!=='true')await page.getByRole('button',{name:'Analysis',exact:true}).click();await expect(page.getByRole('textbox',{name:'Note text',exact:true})).toHaveText('last-context race input');
  1396 | });
  1397 | 
  1398 | test('workspace tabs libraries retain distinct applied queries and scroll when flags match',async({page})=>{
  1399 |  await setup(page,{search:async(r,body)=>r.fulfill({json:{items:Array.from({length:20},(_,i)=>({...attribution,id:`30000000-0000-4000-8000-${String(i+10).padStart(12,'0')}`,title:`${body.query||'initial'} result ${i}`,revision:'1'})),next_cursor:null}})});await page.goto('/');await page.getByRole('button',{name:'Studies',exact:true}).click();const query=page.getByRole('textbox',{name:'Search studies',exact:true}),surface=page.getByRole('complementary',{name:'Study tools',exact:true});await query.fill('alfa');await query.press('Enter');await expect(page.getByRole('button',{name:'alfa result 0',exact:true})).toBeVisible();const a=await surface.evaluate(el=>{el.scrollTop=200;return el.scrollTop;});expect(a).toBeGreaterThan(100);await page.waitForTimeout(100);await page.getByRole('button',{name:'New workspace tab',exact:true}).click();await page.getByRole('dialog',{name:'Book and chapter selector'}).getByRole('button',{name:'Cancel',exact:true}).click();await page.getByRole('button',{name:'Studies',exact:true}).click();await query.fill('beta');await query.press('Enter');await expect(page.getByRole('button',{name:'beta result 0',exact:true})).toBeVisible();const b=await surface.evaluate(el=>{el.scrollTop=400;return el.scrollTop;});expect(b).toBeGreaterThan(a+50);await page.waitForTimeout(100);await page.getByRole('tablist',{name:'Workspace tabs'}).getByRole('tab').first().click();await expect(query).toHaveValue('alfa');await expect.poll(async()=>Math.abs(await surface.evaluate(el=>el.scrollTop)-a)).toBeLessThan(3);await page.getByRole('tablist',{name:'Workspace tabs'}).getByRole('tab').nth(1).click();await expect(query).toHaveValue('beta');await expect.poll(async()=>Math.abs(await surface.evaluate(el=>el.scrollTop)-b)).toBeLessThan(3);
  1400 | });
  1401 | 
  1402 | test('workspace tabs delayed creation retains known recovery when new last-context input prevents attachment',async({page})=>{
  1403 |  const options={failPut:503};await setup(page,options);await firstNote(page);const other='40000000-0000-4000-8000-000000000002';let release,posts=0;
  1404 |  await page.route('**/api/studies/*/notes',async r=>{if(r.request().method()!=='POST')return r.fallback();posts++;await new Promise(resolve=>release=resolve);const body=r.request().postDataJSON();return r.fulfill({json:{operation_id:body.operation_id,command:'note.create',study_id:study,note_id:other,revision:'1'}});});
  1405 |  await page.route('**/notes/'+other,r=>r.fulfill({json:{...attribution,id:other,study_id:study,visibility:'study',revision:'1',value:{document:{version:1,blocks:[]},connections:[],highlights:[]}}}));await page.getByRole('button',{name:'Back to Studies',exact:true}).click();await page.getByRole('button',{name:'Add note',exact:true}).click();await expect.poll(()=>!!release).toBe(true);
  1406 |  await page.locator('[aria-label="Note text"]').evaluate(el=>{el.textContent='late composition input';el.dispatchEvent(new InputEvent('input',{bubbles:true}));});await page.waitForTimeout(700);release();const consent=page.getByRole('dialog',{name:'Changes not saved'});await expect(consent).toBeVisible();await consent.getByRole('button',{name:'Stay',exact:true}).click();await expect(page.getByRole('button',{name:'Open created note',exact:true})).toBeVisible();await page.getByRole('button',{name:'Analysis',exact:true}).click();await expect(page.getByRole('textbox',{name:'Note text',exact:true})).toHaveText('late composition input');expect(posts).toBe(1);
  1407 | });
  1408 | 
  1409 | test('workspace tabs retain malformed-origin URL and collection refusal after another tab navigates validly',async({page})=>{
  1410 |  await setup(page);const malformed='/?reader=%7B%7D&foreign=keep#reading';await page.goto(malformed);const original=page.url();await page.evaluate(()=>{const state=history.state;history.replaceState({...state,foreignOuter:'retained',usr:{...state.usr,foreignUser:'retained'}},'');});
  1411 |  await page.getByRole('button',{name:'Studies',exact:true}).click();await page.getByRole('button',{name:'Start a study',exact:true}).click();await page.getByRole('button',{name:'Create study',exact:true}).click();await expect(page.getByRole('button',{name:'Add current passage',exact:true})).toHaveCount(0);
  1412 |  await page.getByRole('button',{name:'New workspace tab',exact:true}).click();await page.getByRole('dialog',{name:'Book and chapter selector'}).getByRole('textbox',{name:'Passage reference',exact:true}).fill('Genesis 2');await page.getByRole('dialog',{name:'Book and chapter selector'}).getByRole('textbox',{name:'Passage reference',exact:true}).press('Enter');await expect(page.getByText('Invalid reading link',{exact:true})).toHaveCount(0);expect(new URL(page.url()).searchParams.get('reader')).not.toBe('{}');
  1413 |  await page.getByRole('tablist',{name:'Workspace tabs'}).getByRole('tab').first().click();expect(page.url()).toBe(original);await expect(page.getByText('Invalid reading link',{exact:true})).toBeVisible();await expect(page.getByRole('button',{name:'Add current passage',exact:true})).toHaveCount(0);await expect(page.getByRole('button',{name:'Add passage',exact:true})).toBeVisible();expect(await page.evaluate(()=>[history.state.foreignOuter,history.state.usr.foreignUser])).toEqual(['retained','retained']);
  1414 |  if(page.viewportSize().width<768)await page.getByRole('button',{name:'Return to reader',exact:true}).click();await page.getByRole('button',{name:/Navigate:/}).first().click();await page.getByRole('textbox',{name:'Passage reference',exact:true}).fill('Genesis 1');await page.getByRole('textbox',{name:'Passage reference',exact:true}).press('Enter');await expect(page.getByText('Invalid reading link',{exact:true})).toHaveCount(0);if(await page.getByRole('button',{name:'Studies',exact:true}).getAttribute('aria-pressed')!=='true')await page.getByRole('button',{name:'Studies',exact:true}).click();await expect(page.getByRole('button',{name:'Add current passage',exact:true})).toBeVisible();
  1415 | });
  1416 | 
  1417 | async function reviewTabAdd(page){await page.getByRole('button',{name:'New workspace tab',exact:true}).click();await page.getByRole('dialog',{name:'Book and chapter selector'}).getByRole('button',{name:'Cancel',exact:true}).click();}
  1418 | async function reviewTabRename(page,index,label){await page.getByRole('button',{name:`Rename tab ${index}`,exact:true}).click();await page.getByLabel('Tab name',{exact:true}).fill(label);await page.getByRole('dialog',{name:'Rename workspace tab'}).getByRole('button',{name:'Save',exact:true}).click();}
  1419 | async function reviewTwoNotes(page){await reviewLibrary(page);await page.getByRole('button',{name:'Study A',exact:true}).click();await page.getByRole('button',{name:'A first',exact:true}).click();await reviewTabAdd(page);await page.getByRole('button',{name:'Studies',exact:true}).click();await page.getByRole('button',{name:'A second',exact:true}).click();}
  1420 | test('review tabs B1 delayed denial clears labels renamed on newer inactive live tab records',async({page})=>{
  1421 |  let release;const options={beforeRename:()=>new Promise(resolve=>release=resolve),failRename:403};await setup(page,options);await firstNote(page);await reviewTabAdd(page);await page.getByRole('tablist',{name:'Workspace tabs'}).getByRole('tab').first().click();await page.getByRole('button',{name:'Back to Studies',exact:true}).click();await page.getByRole('button',{name:'Rename',exact:true}).click();await page.getByLabel('Title',{exact:true}).fill('denied');await page.getByRole('button',{name:'Save',exact:true}).click();await expect.poll(()=>!!release).toBe(true);await reviewTabRename(page,2,'newer inactive secret');const reply=page.waitForResponse('**/title');release();await reply;await expect(page.getByRole('alert').first()).toContainText('access is unavailable');options.failRename=0;await page.getByRole('button',{name:'Retry',exact:true}).click();await expect(page.getByText('newer inactive secret',{exact:true})).toHaveCount(0);
  1422 | });
  1423 | for(const operation of ['title','collection'])for(const status of [401,403])test(`review tabs B10 closed-origin ${operation} ${status} retains safe account recovery without tool or focus takeover`,async({page})=>{
  1424 |  let release;const options=operation==='title'?{beforeRename:()=>new Promise(resolve=>release=resolve),failRename:status}:{beforePassagePut:()=>new Promise(resolve=>release=resolve),failPassages:status};await setup(page,options);await firstNote(page);await reviewTabAdd(page);await reviewTabRename(page,2,'survivor private label');await page.getByRole('tablist',{name:'Workspace tabs'}).getByRole('tab').first().click();await page.getByRole('button',{name:'Back to Studies',exact:true}).click();if(operation==='title'){await page.getByRole('button',{name:'Rename',exact:true}).click();await page.getByLabel('Title',{exact:true}).fill('pending title');await page.getByRole('button',{name:'Save',exact:true}).click();}else await addReference(page,'Genesis 1');await expect.poll(()=>!!release).toBe(true);await page.getByRole('button',{name:'Close tab 1',exact:true}).click();const survivor=page.getByRole('tablist',{name:'Workspace tabs'}).getByRole('tab');await survivor.focus();const response=page.waitForResponse(operation==='title'?'**/title':'**/passages');release();await response;await expect(page.getByRole('button',{name:'Retry account access',exact:true})).toBeVisible();await expect(survivor).toBeFocused();await expect(page.getByRole('button',{name:'Studies',exact:true})).toHaveAttribute('aria-pressed','false');await expect(page.getByText('survivor private label',{exact:true})).toHaveCount(0);if(status===401){await page.route('**/auth/v1/token*',r=>r.fulfill({json:{...session,access_token:'renewed-current'}}));await page.evaluate(async()=>{const {supabase}=await import('/src/lib/supabase.ts');await supabase.auth.signInWithPassword({email:'reader@example.invalid',password:'fixture'});});}options.failRename=0;options.failPassages=0;await page.getByRole('button',{name:'Retry account access',exact:true}).click();await expect(page.getByRole('button',{name:'Retry account access',exact:true})).toHaveCount(0);await expect(page.getByRole('button',{name:'Studies',exact:true})).toHaveAttribute('aria-pressed','false');await expect(page.getByText('survivor private label',{exact:true})).toHaveCount(status===401?1:0);
  1425 | });
  1426 | test('review tabs B6 masked Rename is disabled with a reason while anonymous and authorized Rename remain usable',async({page})=>{
  1427 |  const options={failPut:401};await setup(page,options);await firstNote(page);await reviewTabRename(page,1,'authorized label');await page.getByRole('textbox',{name:'Note text',exact:true}).fill('mask');await expect(page.getByRole('alert')).toContainText('Sign in');const button=page.getByRole('button',{name:'Rename tab 1',exact:true});await expect(button).toBeDisabled();await expect(button).toHaveAccessibleDescription(/Sign in|access/i);
  1428 | });
  1429 | test('review tabs E1 sole conflicted note reopens latest only after guarded consent',async({page})=>{
  1430 |  const options={failPut:409};const {advanceNote}=await setup(page,options);await firstNote(page);await page.getByRole('textbox',{name:'Note text',exact:true}).fill('my conflicting input');await expect(page.getByRole('alert')).toContainText('This note has changed');advanceNote({document:{version:1,blocks:[{type:'paragraph',direction:'auto',content:[{type:'text',text:'latest server value',marks:[]}]}]},connections:[],highlights:[]});await page.getByRole('button',{name:'Back to Studies',exact:true}).click();await page.getByRole('list',{name:'Notes',exact:true}).getByRole('button').first().click();const dialog=page.getByRole('dialog',{name:'Changes not saved'});await expect(dialog).toBeVisible();await dialog.getByRole('button',{name:'Stay',exact:true}).click();await page.getByRole('list',{name:'Notes',exact:true}).getByRole('button').first().click();await dialog.getByRole('button',{name:'Switch anyway',exact:true}).click();await expect(page.getByRole('textbox',{name:'Note text',exact:true})).toHaveText('latest server value');
  1431 | });
  1432 | test('review tabs B4 delayed Edit mode restore cannot change selection in another exposed note host',async({page})=>{
  1433 |  await reviewTwoNotes(page);const tabs=page.getByRole('tablist',{name:'Workspace tabs'}).getByRole('tab');await tabs.first().click();const editor=page.getByRole('textbox',{name:'Note text',exact:true});await editor.evaluate(el=>{el.focus();const r=document.createRange();r.selectNodeContents(el);getSelection().removeAllRanges();getSelection().addRange(r);});await page.getByRole('button',{name:'Read note',exact:true}).click();await page.evaluate(()=>{window.modeRestore=[];window.originalTimeout=window.setTimeout;window.setTimeout=(callback,delay,...args)=>{if(delay===0){window.modeRestore.push(()=>callback(...args));return 987654;}return window.originalTimeout(callback,delay,...args);};});await page.getByRole('button',{name:'Edit note',exact:true}).click();await tabs.nth(1).click();await editor.focus();await editor.evaluate(el=>{const r=document.createRange();r.selectNodeContents(el);r.collapse(false);getSelection().removeAllRanges();getSelection().addRange(r);window.selectedOther=r.endContainer;window.selectedOffset=r.endOffset;});await page.evaluate(()=>{window.setTimeout=window.originalTimeout;window.modeRestore.splice(0).forEach(fn=>fn());});expect(await editor.evaluate(el=>{const r=getSelection().getRangeAt(0);return el.contains(r.startContainer)&&r.endContainer===window.selectedOther&&r.endOffset===window.selectedOffset;})).toBe(true);await expect(editor).toBeFocused();
  1434 | });
  1435 | for(const state of ['failed','composing'])test(`review tabs V1 sign-out guards ${state} background input while the active retained note is saved`,async({page})=>{
  1436 |  await reviewTwoNotes(page);const tabs=page.getByRole('tablist',{name:'Workspace tabs'}).getByRole('tab');await tabs.first().click();const editor=page.getByRole('textbox',{name:'Note text',exact:true});if(state==='failed')await page.route('**/api/studies/*/notes/*',r=>r.request().method()==='PUT'?r.fulfill({status:503,json:{code:'studies_storage_unavailable'}}):r.fallback());else await editor.dispatchEvent('compositionstart');await editor.fill('background private '+state);if(state==='failed')await expect(page.getByRole('status').filter({hasText:'Changes not saved'})).toBeVisible();await tabs.nth(1).click();await expect(editor).toHaveText('A second');await page.getByRole('button',{name:'Sign out',exact:true}).click();const prompt=page.getByRole('dialog',{name:'Changes not saved'});await expect(prompt).toBeVisible();await prompt.getByRole('button',{name:'Stay',exact:true}).click();await tabs.first().click();await expect(editor).toHaveText('background private '+state);
  1437 | });
  1438 | test('review tabs V1 sequential account consent is non-destructive when the second unresolved lane stays',async({page})=>{
  1439 |  await reviewTwoNotes(page);await page.route('**/api/studies/*/notes/*',r=>r.request().method()==='PUT'?r.fulfill({status:503,json:{code:'studies_storage_unavailable'}}):r.fallback());const tabs=page.getByRole('tablist',{name:'Workspace tabs'}).getByRole('tab'),editor=page.getByRole('textbox',{name:'Note text',exact:true});await editor.fill('lane B unresolved');await expect(page.getByRole('status').filter({hasText:'Changes not saved'})).toBeVisible();await tabs.first().click();await editor.fill('lane A unresolved');await expect(page.getByRole('status').filter({hasText:'Changes not saved'})).toBeVisible();await page.getByRole('button',{name:'Sign out',exact:true}).click();const prompt=page.getByRole('dialog',{name:'Changes not saved'});await prompt.getByRole('button',{name:'Close anyway',exact:true}).click();await expect(prompt).toBeVisible();await prompt.getByRole('button',{name:'Stay',exact:true}).click();await expect(editor).toHaveText('lane A unresolved');await tabs.nth(1).click();await expect(editor).toHaveText('lane B unresolved');await tabs.first().click();await page.getByRole('button',{name:'Sign out',exact:true}).click();await prompt.getByRole('button',{name:'Close anyway',exact:true}).click();await prompt.getByRole('button',{name:'Close anyway',exact:true}).click();await expect(page.getByRole('button',{name:'Sign out',exact:true})).toHaveCount(0);
  1440 | });
  1441 | 
  1442 | test('review tabs B3 word scroll survives hidden Notes scrolling without focus restoration',async({page})=>{
  1443 |  await setup(page,{noteValue:{document:{version:1,blocks:Array.from({length:100},(_,i)=>({type:'paragraph',direction:'auto',content:[{type:'text',text:'Long note '+i+' content',marks:[]}]}))},connections:[],highlights:[]}});await page.route('**/api/bible/words/**',r=>r.fulfill({json:{id:1,position:1,surface_he:'בְּרֵאשִׁית',display_he:'בְּרֵאשִׁית',lemma_strong:'4428',lexical_id:'4428',morph_code:null,morphemes:[]}}));await page.route('**/api/bible/lexicon/**',r=>r.fulfill({json:{status:'available',lexical_id:'4428',lemma:'king',bdb:[{kind:'text',text:'Long definition '.repeat(300)}]}}));await firstNote(page);if(page.viewportSize().width<768)await page.getByRole('button',{name:'Return to reader',exact:true}).click();await page.getByRole('button',{name:/Word: בְּרֵאשִׁית/}).click();await page.getByRole('button',{name:'Show more',exact:true}).click();const surface=page.getByRole('complementary',{name:'Study tools',exact:true});const position=await surface.evaluate(el=>{el.scrollTop=230;return el.scrollTop;});expect(position).toBeGreaterThan(100);await page.waitForTimeout(80);await page.getByRole('tab',{name:'Notes',exact:true}).click();await surface.evaluate(el=>el.scrollTop=600);await page.waitForTimeout(80);const word=page.getByRole('tab',{name:'Word',exact:true});await word.click();await expect(word).toBeFocused();await expect.poll(async()=>Math.abs(await surface.evaluate(el=>el.scrollTop)-position)).toBeLessThan(3);
  1444 | });
  1445 | test('review tabs E3 distinct long note contexts restore their own inspector scroll without focus theft',async({page})=>{
> 1446 |  await reviewLibrary(page,{read:(parent,id,view)=>({...view(parent,id,'long note'),value:{document:{version:1,blocks:Array.from({length:120},(_,i)=>({type:'paragraph',direction:'auto',content:[{type:'text',text:id+' paragraph '+i,marks:[]}]}))},connections:[],highlights:[]}})});await page.getByRole('button',{name:'Study A',exact:true}).click();await page.getByRole('button',{name:'A first',exact:true}).click();const surface=page.getByRole('complementary',{name:'Study tools',exact:true});const a=await surface.evaluate(el=>{el.scrollTop=220;return el.scrollTop;});await page.waitForTimeout(80);await reviewTabAdd(page);await page.getByRole('button',{name:'Studies',exact:true}).click();await page.getByRole('button',{name:'A second',exact:true}).click();const b=await surface.evaluate(el=>{el.scrollTop=650;return el.scrollTop;});await page.waitForTimeout(80);const tabs=page.getByRole('tablist',{name:'Workspace tabs'}).getByRole('tab');await tabs.first().click();await expect(tabs.first()).toBeFocused();await expect.poll(async()=>Math.abs(await surface.evaluate(el=>el.scrollTop)-a)).toBeLessThan(3);await tabs.nth(1).click();await expect(tabs.nth(1)).toBeFocused();await expect.poll(async()=>Math.abs(await surface.evaluate(el=>el.scrollTop)-b)).toBeLessThan(3);
       |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      ^ Error: expect(received).toBeLessThan(expected)
  1447 | });
  1448 | 
  1449 | test('review tabs V1 sign-out rechecks saved background lanes receiving late composition during consent',async({page})=>{
  1450 |  await reviewTwoNotes(page);const tabs=page.getByRole('tablist',{name:'Workspace tabs'}).getByRole('tab'),editor=page.getByRole('textbox',{name:'Note text',exact:true});await tabs.first().click();await editor.evaluate(el=>window.lateBackgroundEditor=el);await tabs.nth(1).click();await page.route('**/api/studies/*/notes/*',r=>r.request().method()==='PUT'?r.fulfill({status:503,json:{code:'studies_storage_unavailable'}}):r.fallback());await editor.fill('B needs consent');await expect(page.getByRole('status').filter({hasText:'Changes not saved'})).toBeVisible();await page.getByRole('button',{name:'Sign out',exact:true}).click();const prompt=page.getByRole('dialog',{name:'Changes not saved'});await expect(prompt).toBeVisible();await page.evaluate(()=>{const el=window.lateBackgroundEditor;el.dispatchEvent(new CompositionEvent('compositionstart',{bubbles:true}));el.textContent='A late composition';el.dispatchEvent(new InputEvent('input',{bubbles:true,isComposing:true}));});await prompt.getByRole('button',{name:'Close anyway',exact:true}).click();await expect(prompt).toBeVisible();await prompt.getByRole('button',{name:'Stay',exact:true}).click();await expect(page.getByRole('button',{name:'Sign out',exact:true})).toBeVisible();await tabs.first().click();await expect(editor).toHaveText('A late composition');
  1451 | });
  1452 | test('review tabs E1 shared conflicted lane cannot be replaced by reopening from another live context',async({page})=>{
  1453 |  const {requests}=await setup(page,{failPut:409});await firstNote(page);await reviewTabAdd(page);const editor=page.getByRole('textbox',{name:'Note text',exact:true});await page.getByRole('button',{name:'Analysis',exact:true}).click();await editor.fill('shared conflicting input');await expect(page.getByRole('alert')).toContainText('This note has changed');const reads=requests.filter(r=>r.path.endsWith('/notes/'+note)&&r.method==='GET').length;await page.getByRole('button',{name:'Back to Studies',exact:true}).click();await page.getByRole('list',{name:'Notes',exact:true}).getByRole('button').first().click();await expect(page.getByRole('dialog',{name:'Changes not saved'})).toHaveCount(0);await page.getByRole('button',{name:'Analysis',exact:true}).click();await expect(editor).toHaveText('shared conflicting input');expect(requests.filter(r=>r.path.endsWith('/notes/'+note)&&r.method==='GET')).toHaveLength(reads);
  1454 | });
  1455 | 
```