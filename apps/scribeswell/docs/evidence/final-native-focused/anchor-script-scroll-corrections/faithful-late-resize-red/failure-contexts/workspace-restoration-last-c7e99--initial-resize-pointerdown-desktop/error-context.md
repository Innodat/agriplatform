# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: workspace-restoration.spec.cjs >> last public scroll checkpoint survives tools hiding the pane before the durable write with delayed initial resize pointerdown
- Location: tests/workspace-restoration.spec.cjs:181:184

# Error details

```
Error: expect(received).toBeGreaterThan(expected)

Expected: > 3
Received:   3

Call Log:
- Timeout 5000ms exceeded while waiting on the predicate
```

# Page snapshot

```yaml
- generic [ref=f2e3]:
  - banner [ref=f2e5]:
    - generic [ref=f2e6]:
      - generic [ref=f2e7]: Scribes' Well
      - generic [ref=f2e13]:
        - button "Create account" [ref=f2e14]
        - button "Sign in" [ref=f2e15]
  - main [ref=f2e19]:
    - generic [ref=f2e20]:
      - generic [ref=f2e21]:
        - tablist "Workspace tabs" [ref=f2e22]:
          - generic [ref=f2e23]:
            - tab "Genesis 1" [selected] [ref=f2e24]
            - button "Rename tab 1" [ref=f2e25]: Rename
        - button "New workspace tab" [ref=f2e26]: + New tab
      - generic [ref=f2e27]:
        - button "Add reader pane" [ref=f2e28]
        - button "Enter focus mode" [ref=f2e31]: Focus mode
      - navigation "Reader tools" [ref=f2e37]:
        - button "Studies" [ref=f2e38]
        - button "Analysis" [ref=f2e39]
      - tabpanel "Genesis 1" [ref=f2e41]:
        - region "Passage 1" [ref=f2e42]:
          - generic [ref=f2e43]:
            - button "Previous chapter" [disabled] [ref=f2e44]
            - 'button "Navigate: Genesis, chapter 1. Open selector." [ref=f2e48]': Genesis א
            - button "Next chapter" [ref=f2e51]
          - region "Chapter text" [ref=f2e54]:
            - list "Verses" [ref=f2e55]:
              - listitem [ref=f2e56]:
                - generic "Verse 1" [ref=f2e57]: "1"
                - paragraph [ref=f2e58]:
                  - 'button "Word: בְּרֵאשִׁית" [ref=f2e59] [cursor=pointer]': בְּרֵאשִׁית
              - listitem [ref=f2e60]:
                - generic "Verse 2" [ref=f2e61]: "2"
                - paragraph [ref=f2e62]:
                  - 'button "Word: בְּרֵאשִׁית" [ref=f2e63] [cursor=pointer]': בְּרֵאשִׁית
              - listitem [ref=f2e64]:
                - generic "Verse 3" [ref=f2e65]: "3"
                - paragraph [ref=f2e66]:
                  - 'button "Word: בְּרֵאשִׁית" [ref=f2e67] [cursor=pointer]': בְּרֵאשִׁית
              - listitem [ref=f2e68]:
                - generic "Verse 4" [ref=f2e69]: "4"
                - paragraph [ref=f2e70]:
                  - 'button "Word: בְּרֵאשִׁית" [ref=f2e71] [cursor=pointer]': בְּרֵאשִׁית
              - listitem [ref=f2e72]:
                - generic "Verse 5" [ref=f2e73]: "5"
                - paragraph [ref=f2e74]:
                  - 'button "Word: בְּרֵאשִׁית" [ref=f2e75] [cursor=pointer]': בְּרֵאשִׁית
              - listitem [ref=f2e76]:
                - generic "Verse 6" [ref=f2e77]: "6"
                - paragraph [ref=f2e78]:
                  - 'button "Word: בְּרֵאשִׁית" [ref=f2e79] [cursor=pointer]': בְּרֵאשִׁית
              - listitem [ref=f2e80]:
                - generic "Verse 7" [ref=f2e81]: "7"
                - paragraph [ref=f2e82]:
                  - 'button "Word: בְּרֵאשִׁית" [ref=f2e83] [cursor=pointer]': בְּרֵאשִׁית
              - listitem [ref=f2e84]:
                - generic "Verse 8" [ref=f2e85]: "8"
                - paragraph [ref=f2e86]:
                  - 'button "Word: בְּרֵאשִׁית" [ref=f2e87] [cursor=pointer]': בְּרֵאשִׁית
              - listitem [ref=f2e88]:
                - generic "Verse 9" [ref=f2e89]: "9"
                - paragraph [ref=f2e90]:
                  - 'button "Word: בְּרֵאשִׁית" [ref=f2e91] [cursor=pointer]': בְּרֵאשִׁית
              - listitem [ref=f2e92]:
                - generic "Verse 10" [ref=f2e93]: "10"
                - paragraph [ref=f2e94]:
                  - 'button "Word: בְּרֵאשִׁית" [ref=f2e95] [cursor=pointer]': בְּרֵאשִׁית
              - listitem [ref=f2e96]:
                - generic "Verse 11" [ref=f2e97]: "11"
                - paragraph [ref=f2e98]:
                  - 'button "Word: בְּרֵאשִׁית" [ref=f2e99] [cursor=pointer]': בְּרֵאשִׁית
              - listitem [ref=f2e100]:
                - generic "Verse 12" [ref=f2e101]: "12"
                - paragraph [ref=f2e102]:
                  - 'button "Word: בְּרֵאשִׁית" [ref=f2e103] [cursor=pointer]': בְּרֵאשִׁית
              - listitem [ref=f2e104]:
                - generic "Verse 13" [ref=f2e105]: "13"
                - paragraph [ref=f2e106]:
                  - 'button "Word: בְּרֵאשִׁית" [ref=f2e107] [cursor=pointer]': בְּרֵאשִׁית
              - listitem [ref=f2e108]:
                - generic "Verse 14" [ref=f2e109]: "14"
                - paragraph [ref=f2e110]:
                  - 'button "Word: בְּרֵאשִׁית" [ref=f2e111] [cursor=pointer]': בְּרֵאשִׁית
              - listitem [ref=f2e112]:
                - generic "Verse 15" [ref=f2e113]: "15"
                - paragraph [ref=f2e114]:
                  - 'button "Word: בְּרֵאשִׁית" [ref=f2e115] [cursor=pointer]': בְּרֵאשִׁית
              - listitem [ref=f2e116]:
                - generic "Verse 16" [ref=f2e117]: "16"
                - paragraph [ref=f2e118]:
                  - 'button "Word: בְּרֵאשִׁית" [ref=f2e119] [cursor=pointer]': בְּרֵאשִׁית
              - listitem [ref=f2e120]:
                - generic "Verse 17" [ref=f2e121]: "17"
                - paragraph [ref=f2e122]:
                  - 'button "Word: בְּרֵאשִׁית" [ref=f2e123] [cursor=pointer]': בְּרֵאשִׁית
              - listitem [ref=f2e124]:
                - generic "Verse 18" [ref=f2e125]: "18"
                - paragraph [ref=f2e126]:
                  - 'button "Word: בְּרֵאשִׁית" [ref=f2e127] [cursor=pointer]': בְּרֵאשִׁית
              - listitem [ref=f2e128]:
                - generic "Verse 19" [ref=f2e129]: "19"
                - paragraph [ref=f2e130]:
                  - 'button "Word: בְּרֵאשִׁית" [ref=f2e131] [cursor=pointer]': בְּרֵאשִׁית
              - listitem [ref=f2e132]:
                - generic "Verse 20" [ref=f2e133]: "20"
                - paragraph [ref=f2e134]:
                  - 'button "Word: בְּרֵאשִׁית" [ref=f2e135] [cursor=pointer]': בְּרֵאשִׁית
              - listitem [ref=f2e136]:
                - generic "Verse 21" [ref=f2e137]: "21"
                - paragraph [ref=f2e138]:
                  - 'button "Word: בְּרֵאשִׁית" [ref=f2e139] [cursor=pointer]': בְּרֵאשִׁית
              - listitem [ref=f2e140]:
                - generic "Verse 22" [ref=f2e141]: "22"
                - paragraph [ref=f2e142]:
                  - 'button "Word: בְּרֵאשִׁית" [ref=f2e143] [cursor=pointer]': בְּרֵאשִׁית
              - listitem [ref=f2e144]:
                - generic "Verse 23" [ref=f2e145]: "23"
                - paragraph [ref=f2e146]:
                  - 'button "Word: בְּרֵאשִׁית" [ref=f2e147] [cursor=pointer]': בְּרֵאשִׁית
              - listitem [ref=f2e148]:
                - generic "Verse 24" [ref=f2e149]: "24"
                - paragraph [ref=f2e150]:
                  - 'button "Word: בְּרֵאשִׁית" [ref=f2e151] [cursor=pointer]': בְּרֵאשִׁית
              - listitem [ref=f2e152]:
                - generic "Verse 25" [ref=f2e153]: "25"
                - paragraph [ref=f2e154]:
                  - 'button "Word: בְּרֵאשִׁית" [ref=f2e155] [cursor=pointer]': בְּרֵאשִׁית
              - listitem [ref=f2e156]:
                - generic "Verse 26" [ref=f2e157]: "26"
                - paragraph [ref=f2e158]:
                  - 'button "Word: בְּרֵאשִׁית" [ref=f2e159] [cursor=pointer]': בְּרֵאשִׁית
              - listitem [ref=f2e160]:
                - generic "Verse 27" [ref=f2e161]: "27"
                - paragraph [ref=f2e162]:
                  - 'button "Word: בְּרֵאשִׁית" [ref=f2e163] [cursor=pointer]': בְּרֵאשִׁית
              - listitem [ref=f2e164]:
                - generic "Verse 28" [ref=f2e165]: "28"
                - paragraph [ref=f2e166]:
                  - 'button "Word: בְּרֵאשִׁית" [ref=f2e167] [cursor=pointer]': בְּרֵאשִׁית
              - listitem [ref=f2e168]:
                - generic "Verse 29" [ref=f2e169]: "29"
                - paragraph [ref=f2e170]:
                  - 'button "Word: בְּרֵאשִׁית" [ref=f2e171] [cursor=pointer]': בְּרֵאשִׁית
              - listitem [ref=f2e172]:
                - generic "Verse 30" [ref=f2e173]: "30"
                - paragraph [ref=f2e174]:
                  - 'button "Word: בְּרֵאשִׁית" [ref=f2e175] [cursor=pointer]': בְּרֵאשִׁית
              - listitem [ref=f2e176]:
                - generic "Verse 31" [ref=f2e177]: "31"
                - paragraph [ref=f2e178]:
                  - 'button "Word: בְּרֵאשִׁית" [ref=f2e179] [cursor=pointer]': בְּרֵאשִׁית
```

# Test source

```ts
  99  |  const third=await context.newPage();await setup(third);await settled(third);expect(await tabs(third).evaluateAll(nodes=>nodes.map(node=>node.dataset.workspaceTab))).toEqual(winner.tabs.map(t=>t.tabKey));await expect(third.locator(`[data-workspace-tab="${winner.activeTabKey}"]`)).toHaveAttribute('aria-selected','true');await second.close();await third.close();
  100 | });
  101 | test('cross-window future version prevents even a previously eligible writer from changing records',async({page,context})=>{
  102 |  await setup(page);await page.waitForTimeout(350);const second=await context.newPage();await setup(second);await second.waitForTimeout(350);const future={...publicSetup(),v:3};await seed(second,future);await add(page);await expect(page.getByRole('status').filter({hasText:'Reading setup not remembered.'})).toBeVisible();expect((await stored(page)).public).toEqual(future);await second.close();
  103 | });
  104 | test('delayed old identity401 cannot remove a newer SDK sign-in session',async({page})=>{
  105 |  await setup(page);let release,started=false;await page.route('**/auth/v1/user*',async r=>{if(r.request().headers().authorization==='Bearer stale-token'){started=true;await new Promise(resolve=>release=resolve);return r.fulfill({status:401,json:{error_code:'session_not_found',msg:'fixture'}});}return r.fulfill({json:session.user});});await page.route('**/auth/v1/token*',r=>r.fulfill({json:{...session,access_token:'newer-token'}}));
  106 |  await page.evaluate(()=>{window.oldVerification=import('/src/lib/supabase.ts').then(m=>m.verifyWorkspaceIdentity('stale-token'));});await expect.poll(()=>started).toBe(true);await page.evaluate(async()=>{const {supabase}=await import('/src/lib/supabase.ts');await supabase.auth.signInWithPassword({email:'fixture@example.invalid',password:'fixture'});});release();expect(await page.evaluate(()=>window.oldVerification)).toEqual({failure:'unauthenticated'});expect(await page.evaluate(()=>JSON.parse(localStorage.getItem('pts-auth')).access_token)).toBe('newer-token');await expect(page.getByRole('button',{name:'Sign out',exact:true})).toBeVisible();
  107 | });
  108 | test('changed intent during identity verification retains hidden candidates for explicit Retry',async({page})=>{
  109 |  await setup(page);await seed(page,publicSetup(),privateSetup());let release,held=true;await owner(page,{identity:async r=>{if(held)await new Promise(resolve=>release=resolve);return r.fulfill({json:session.user});}});await page.goto('/');await expect.poll(()=>!!release).toBe(true);await add(page);held=false;release();await expect(page.getByRole('status').filter({hasText:'Private reading context not restored.'})).toBeVisible();await expect(page.getByText('Private label 1',{exact:true})).toHaveCount(0);await page.waitForTimeout(400);expect((await stored(page))[`account:${account}`].tabs).toHaveLength(2);
  110 |  await page.getByRole('status').filter({hasText:'Private reading context not restored.'}).getByRole('button',{name:'Retry',exact:true}).click();const decision=page.getByRole('dialog',{name:'Restore remembered reading setups'});await expect(decision).toBeVisible();await decision.getByRole('button',{name:'Restore setups',exact:true}).click();await expect(tabs(page).first()).toHaveText('Private label 1');await expect(tabs(page)).toHaveCount(3);
  111 | });
  112 | for(const scenario of ['changed navigation','closed incarnation','account switch'])test(`late hydration ignores ${scenario} without focus or selection replacement`,async({page})=>{
  113 |  await setup(page);await seed(page,publicSetup(),privateSetup());let release,held=true,started=0;const gate=new Promise(resolve=>release=resolve);await owner(page,{read:async r=>{if(held){started++;await gate;}const path=new URL(r.request().url()).pathname;return r.fulfill({json:path.endsWith('/notes/'+note)?{id:note,study_id:study,owner_account_id:account,revision:'1',visibility:'study',value:{document:{version:1,blocks:[]},connections:[],highlights:[]}}:{id:study,owner_account_id:account,title:'Private study',revision:'1'}});}});await page.goto('/');await expect.poll(()=>started).toBeGreaterThan(0);
  114 |  if(scenario==='closed incarnation'){await page.getByRole('button',{name:'Close tab 1',exact:true}).click();}
  115 |  else if(scenario==='changed navigation'){await add(page);}
  116 |  else {await page.route('**/auth/v1/token*',r=>r.fulfill({json:{...session,user:{...session.user,id:other},access_token:'other-token'}}));await page.evaluate(async()=>{const {supabase}=await import('/src/lib/supabase.ts');await supabase.auth.signInWithPassword({email:'other@example.invalid',password:'fixture'});});}
  117 |  const active=await page.evaluate(()=>document.activeElement?.getAttribute('aria-label'));held=false;release();await page.waitForTimeout(450);await expect(page.getByText('Private label 1',{exact:true})).toHaveCount(0);expect(await page.evaluate(()=>document.activeElement?.getAttribute('aria-label'))).toBe(active);if(scenario==='closed incarnation')await expect(tabs(page)).toHaveCount(1);
  118 | });
  119 | async function delayStorageOpen(page,delay){await page.addInitScript(delay=>{const original=indexedDB.open.bind(indexedDB);window.restoreIDBOpen=original;indexedDB.open=(...args)=>{let request;const callbacks={},proxy={};for(const key of ['result','transaction','error'])Object.defineProperty(proxy,key,{get:()=>request?.[key]});for(const event of ['onsuccess','onerror','onblocked','onupgradeneeded'])Object.defineProperty(proxy,event,{set:fn=>{callbacks[event]=fn;},get:()=>callbacks[event]});setTimeout(()=>{request=original(...args);for(const event of ['onsuccess','onerror','onblocked','onupgradeneeded'])request[event]=e=>callbacks[event]?.call(proxy,e);},delay);return proxy;};},delay);}
  120 | test('late public read after new tab intent requires explicit installation and never drops current tabs',async({page})=>{
  121 |  await setup(page);await seed(page,publicSetup(12));await delayStorageOpen(page,1000);await page.goto('/');await add(page);const current=await tabs(page).evaluateAll(nodes=>nodes.map(node=>node.dataset.workspaceTab));const decision=page.getByRole('dialog',{name:'Restore remembered reading setups'});await expect(page.getByRole('status').filter({hasText:'Remembered reading setups are ready.'})).toBeVisible();await expect(decision).toHaveCount(0);await page.getByRole('status').filter({hasText:'Remembered reading setups are ready.'}).getByRole('button',{name:'Retry',exact:true}).click();await expect(decision).toBeVisible();expect(await tabs(page).evaluateAll(nodes=>nodes.map(node=>node.dataset.workspaceTab))).toEqual(current);
  122 |  await decision.getByRole('button',{name:/Close remembered tab 3:/}).click();await expect(decision).toBeVisible();await decision.getByRole('button',{name:/Close remembered tab 3:/}).click();await expect(tabs(page)).toHaveCount(12);for(const key of current)expect(await tabs(page).evaluateAll(nodes=>nodes.map(node=>node.dataset.workspaceTab))).toContain(key);
  123 | });
  124 | test('account intent invalidates a delayed public bootstrap even outside the reader root',async({page})=>{
  125 |  await setup(page);await seed(page,publicSetup());await delayStorageOpen(page,1000);await page.route('**/auth/v1/token*',r=>r.fulfill({json:session}));await page.goto('/');await expect(page.getByRole('button',{name:'Sign in',exact:true})).toBeVisible();await page.evaluate(async()=>{const {supabase}=await import('/src/lib/supabase.ts');await supabase.auth.signInWithPassword({email:'fixture@example.invalid',password:'fixture'});});await expect(page.getByRole('status').filter({hasText:'Remembered reading setups are ready.'})).toBeVisible();await expect(page.getByRole('dialog',{name:'Restore remembered reading setups'})).toHaveCount(0);await expect(tabs(page)).toHaveCount(1);
  126 | });
  127 | test('timed out open cannot later upgrade or install over intervening reading',async({page})=>{
  128 |  await delayStorageOpen(page,3600);await setup(page);await expect(page.getByRole('status').filter({hasText:'Reading setup not remembered.'})).toBeVisible({timeout:4500});await add(page);await expect(tabs(page)).toHaveCount(2);await page.waitForTimeout(800);const stores=await page.evaluate(()=>new Promise((resolve,reject)=>{const r=window.restoreIDBOpen('scribeswell-workspace:/',1);r.onsuccess=()=>{const db=r.result;const names=Array.from(db.objectStoreNames);db.close();resolve(names);};r.onerror=reject;}));expect(stores).toEqual([]);await expect(tabs(page)).toHaveCount(2);
  129 | });
  130 | test('wrong owner or parent responses never expose a stored private candidate',async({page})=>{
  131 |  await setup(page);await seed(page,publicSetup(),privateSetup());await owner(page,{read:r=>r.fulfill({json:{id:study,owner_account_id:other,title:'Foreign private title',revision:'1'}})});await page.goto('/');await expect(page.getByRole('status').filter({hasText:'Private reading context not restored.'})).toBeVisible();await expect(page.getByText('Private label 1',{exact:true})).toHaveCount(0);await page.waitForTimeout(400);expect((await stored(page))[`account:${account}`].tabs).toHaveLength(2);
  132 | });
  133 | test('anonymous closure and closed-key replay remain public when the owner returns',async({page})=>{
  134 |  await setup(page);await seed(page,publicSetup(),privateSetup());await owner(page);await page.goto('/');await expect(tabs(page).first()).toHaveText('Private label 1');await page.evaluate(async()=>{const {supabase}=await import('/src/lib/supabase.ts');await supabase.auth.signOut({scope:'local'});});await expect(tabs(page).first()).toHaveText('Genesis 1');await page.getByRole('button',{name:'Close tab 1',exact:true}).click();await page.goBack();await expect(tabs(page)).toHaveCount(2);await page.route('**/auth/v1/token*',r=>r.fulfill({json:session}));await page.evaluate(async()=>{const {supabase}=await import('/src/lib/supabase.ts');await supabase.auth.signInWithPassword({email:'fixture@example.invalid',password:'fixture'});});await page.waitForTimeout(500);await expect(page.getByText('Private label 1',{exact:true})).toHaveCount(0);await expect(page.getByText('Private label 2',{exact:true})).toBeVisible();
  135 | });
  136 | test('anonymous names stay memory-only and retained native refresh preserves matching incarnations',async({page})=>{
  137 |  await setup(page);await seed(page,publicSetup());await page.goto('/');await expect(tabs(page)).toHaveCount(2);await page.getByRole('button',{name:'Rename tab 1',exact:true}).click();await page.getByLabel('Tab name',{exact:true}).fill('Anonymous private label');await page.getByRole('dialog',{name:'Rename workspace tab'}).getByRole('button',{name:'Save',exact:true}).click();await page.waitForTimeout(450);const before=(await stored(page)).public;expect(JSON.stringify(await stored(page))).not.toContain('Anonymous private label');await page.reload();await expect(tabs(page)).toHaveCount(2);await expect(tabs(page).first()).toHaveText('Genesis 1');await settled(page);const after=(await stored(page)).public;expect(after.tabs.map(t=>[t.tabKey,t.incarnation])).toEqual(before.tabs.map(t=>[t.tabKey,t.incarnation]));
  138 | });
  139 | test('evicted storage loses remembered metadata safely while public reading remains usable',async({page})=>{
  140 |  await setup(page);await seed(page,publicSetup());await page.goto('/');await expect(tabs(page)).toHaveCount(2);await settled(page);await page.evaluate(async()=>{const {workspaceDatabase}=await import('/src/lib/workspace-storage.ts');await new Promise((resolve,reject)=>{const r=indexedDB.deleteDatabase(workspaceDatabase);r.onsuccess=resolve;r.onerror=reject;});});await expect(tabs(page)).toHaveCount(2);await page.goto('/__workspace-storage-fixture');await page.evaluate(async()=>{const {workspaceDatabase}=await import('/src/lib/workspace-storage.ts');await new Promise((resolve,reject)=>{const r=indexedDB.deleteDatabase(workspaceDatabase);r.onsuccess=resolve;r.onerror=reject;});});await page.goto('/');await expect(tabs(page)).toHaveCount(1);await expect(page.getByRole('button',{name:/Word: בְּרֵאשִׁית/})).toBeVisible();
  141 | });
  142 | test('denied storage Retry remembers current reading once storage becomes available',async({page})=>{
  143 |  await page.addInitScript(()=>{window.nativeIDBOpen=indexedDB.open.bind(indexedDB);indexedDB.open=()=>{throw new DOMException('fixture','SecurityError');};});await setup(page);await expect(page.getByRole('status').filter({hasText:'Reading setup not remembered.'})).toBeVisible();await add(page);await page.evaluate(()=>{indexedDB.open=window.nativeIDBOpen;});await page.getByRole('status').filter({hasText:'Reading setup not remembered.'}).getByRole('button',{name:'Retry',exact:true}).click();await settled(page);expect((await stored(page)).public.tabs).toHaveLength(2);
  144 | });
  145 | test('resource404 clears only the affected selection and keeps unrelated authorized context',async({page})=>{
  146 |  const secondStudy='30000000-0000-4000-8000-000000000002',secondNote='40000000-0000-4000-8000-000000000002';await setup(page);const priv=privateSetup();priv.tabs[1].study=secondStudy;priv.tabs[1].note=secondNote;await seed(page,publicSetup(),priv);await owner(page,{read:r=>{const path=new URL(r.request().url()).pathname;if(path.includes(study))return r.fulfill({status:404,json:{code:'resource_unavailable'}});return r.fulfill({json:path.endsWith(secondNote)?{id:secondNote,study_id:secondStudy,owner_account_id:account,revision:'1',visibility:'study',value:{document:{version:1,blocks:[]},connections:[],highlights:[]}}:{id:secondStudy,owner_account_id:account,title:'Second study',revision:'1'}});}});await page.goto('/');await expect(tabs(page).nth(1)).toHaveText('Private label 2');await expect(tabs(page).first()).toHaveText('Genesis 1');await page.waitForTimeout(500);expect((await stored(page))[`account:${account}`].tabs.map(t=>t.tabKey)).toEqual(['saved-1']);
  147 | });
  148 | test('unsent body never persists and reload refetches acknowledged content',async({page})=>{
  149 |  await setup(page);await seed(page,publicSetup(),privateSetup());await owner(page);await page.goto('/');await expect(tabs(page).first()).toHaveText('Private label 1');await page.getByRole('button',{name:'Analysis',exact:true}).click();await page.getByRole('textbox',{name:'Note text',exact:true}).fill('Unsent private input only');await page.waitForTimeout(600);expect(JSON.stringify(await stored(page))).not.toContain('Unsent private input only');page.once('dialog',dialog=>dialog.accept());await page.reload();await expect(tabs(page).first()).toHaveText('Private label 1');await page.getByRole('button',{name:'Analysis',exact:true}).click();await expect(page.getByRole('textbox',{name:'Note text',exact:true})).toContainText('Saved private body');await expect(page.getByRole('textbox',{name:'Note text',exact:true})).not.toContainText('Unsent private input only');
  150 | });
  151 | // Same-ID candidates: acknowledge the first hydration before releasing the
  152 | // second study response, so the pending note gate always belongs to candidate2.
  153 | test('late second candidate cannot overwrite a newer dirty shared note lane or expose its private label',async({page})=>{
  154 |  await setup(page);await seed(page,publicSetup(),privateSetup());let notes=0,release,studyReads=0,allowSecondStudy;const secondStudyGate=new Promise(resolve=>allowSecondStudy=resolve);const gate=new Promise(resolve=>release=resolve);await owner(page,{read:async r=>{const path=new URL(r.request().url()).pathname;if(path.endsWith('/notes/'+note)){notes++;if(notes===2)await gate;return r.fulfill({json:{id:note,study_id:study,owner_account_id:account,revision:'1',visibility:'study',value:{document:{version:1,blocks:[{type:'paragraph',direction:'auto',content:[{type:'text',text:'Saved body',marks:[]}]}]},connections:[],highlights:[]}}});}if(++studyReads===2)await secondStudyGate;return r.fulfill({json:{id:study,owner_account_id:account,title:'Private title',revision:'1'}});}});await page.goto('/');await expect(tabs(page).first()).toHaveText('Private label 1');allowSecondStudy();await expect.poll(()=>notes).toBe(2);await page.getByRole('button',{name:'Analysis',exact:true}).click();const editor=page.getByRole('textbox',{name:'Note text',exact:true});await editor.fill('New input belongs to this lane');release();await page.waitForTimeout(400);await expect(editor).toHaveText('New input belongs to this lane');await expect(page.getByText('Private label 2',{exact:true})).toHaveCount(0);await expect(page.locator('[aria-label="Note text"]')).toHaveCount(1);
  155 | });
  156 | test('surviving tabs retain owner-bound candidates across sign-out and require fresh verification on return',async({page})=>{
  157 |  await setup(page);await seed(page,publicSetup(),privateSetup());let identityReads=0;await owner(page,{identity:r=>{identityReads++;return r.fulfill({json:session.user});}});await page.goto('/');await expect(tabs(page).first()).toHaveText('Private label 1');const before=(await stored(page)).public.tabs.map(t=>[t.tabKey,t.incarnation]);await page.evaluate(async()=>{const {supabase}=await import('/src/lib/supabase.ts');await supabase.auth.signOut({scope:'local'});});await expect(tabs(page).first()).toHaveText('Genesis 1');await page.waitForTimeout(350);expect((await stored(page))[`account:${account}`].tabs).toHaveLength(2);await page.route('**/auth/v1/token*',r=>r.fulfill({json:{...session,access_token:'returned-token'}}));await page.evaluate(async()=>{const {supabase}=await import('/src/lib/supabase.ts');await supabase.auth.signInWithPassword({email:'fixture@example.invalid',password:'fixture'});});await expect(tabs(page).first()).toHaveText('Private label 1');await expect(tabs(page).nth(1)).toHaveText('Private label 2');expect(identityReads).toBe(2);expect((await stored(page)).public.tabs.map(t=>[t.tabKey,t.incarnation])).toEqual(before);
  158 | });
  159 | for(const scenario of ['unavailable','unauthenticated','different ID'])test(`identity ${scenario} retains hidden candidates and never triggers protected reads`,async({page})=>{
  160 |  await setup(page);await seed(page,publicSetup(),privateSetup());const calls=await owner(page,{identity:r=>scenario==='different ID'?r.fulfill({json:{...session.user,id:other}}):r.fulfill({status:scenario==='unauthenticated'?401:503,json:{error_code:'fixture'}})});await page.goto('/');await expect(tabs(page)).toHaveCount(2);await expect(page.getByRole('status').filter({hasText:'Private reading context not restored.'})).toBeVisible();expect(calls.reads()).toBe(0);await expect(page.getByText('Private label 1',{exact:true})).toHaveCount(0);expect((await stored(page))[`account:${account}`].tabs).toHaveLength(2);
  161 | });
  162 | for(const action of ['Rename','Reset'])test(`explicit ${action} while identity is pending preserves newer label intent and remembered resource IDs`,async({page})=>{
  163 |  await setup(page);await seed(page,publicSetup(),privateSetup());let release;await owner(page,{identity:async r=>{await new Promise(resolve=>release=resolve);return r.fulfill({json:session.user});}});await page.goto('/');await expect.poll(()=>!!release).toBe(true);await page.getByRole('button',{name:'Rename tab 1',exact:true}).click();const dialog=page.getByRole('dialog',{name:'Rename workspace tab'});if(action==='Rename'){await page.getByLabel('Tab name',{exact:true}).fill('New explicit label');await dialog.getByRole('button',{name:'Save',exact:true}).click();}else await dialog.getByRole('button',{name:'Reset name',exact:true}).click();release();await expect.poll(async()=>{const row=(await stored(page))[`account:${account}`]?.tabs.find(t=>t.tabKey==='saved-0');return row&&{study:row.study,note:row.note,label:row.label??null};}).toEqual({study,note,label:action==='Rename'?'New explicit label':null});await expect(tabs(page).first()).toHaveText(action==='Rename'?'New explicit label':'Genesis 1');
  164 | });
  165 | test('current admission403 clears already hydrated lanes after unrelated origin intent changes',async({page})=>{
  166 |  await setup(page);await seed(page,publicSetup(),privateSetup());let notes=0,release,studyReads=0,allowSecondStudy;const secondStudyGate=new Promise(resolve=>allowSecondStudy=resolve);const gate=new Promise(resolve=>release=resolve);await owner(page,{read:async r=>{const path=new URL(r.request().url()).pathname;if(path.endsWith('/notes/'+note)){notes++;if(notes===2){await gate;return r.fulfill({status:403,json:{code:'studies_access_denied'}});}return r.fulfill({json:{id:note,study_id:study,owner_account_id:account,revision:'1',visibility:'study',value:{document:{version:1,blocks:[{type:'paragraph',direction:'auto',content:[{type:'text',text:'Authorized saved body',marks:[]}]}]},connections:[],highlights:[]}}});}if(++studyReads===2)await secondStudyGate;return r.fulfill({json:{id:study,owner_account_id:account,title:'Private study',revision:'1'}});}});await page.goto('/');await expect(tabs(page).first()).toHaveText('Private label 1');allowSecondStudy();await expect.poll(()=>notes).toBe(2);await page.getByRole('button',{name:'Analysis',exact:true}).click();await expect(page.getByRole('textbox',{name:'Note text',exact:true})).toHaveText('Authorized saved body');release();await expect(page.getByRole('textbox',{name:'Note text',exact:true})).toHaveCount(0);await expect(page.getByText('Private label 1',{exact:true})).toHaveCount(0);await expect.poll(async()=>(await stored(page))[`account:${account}`].tabs).toEqual([]);await expect(tabs(page)).toHaveCount(2);
  167 | });
  168 | test('account pruning follows transaction completion when device-clock timestamps tie or go backwards',async({page})=>{
  169 |  await setup(page);await seed(page,publicSetup());await page.evaluate(async({pub,priv})=>{const m=await import('/src/lib/workspace-storage.ts'),original=Date.now,clock=original();Date.now=()=>clock;try{for(let i=1;i<=4;i++)await m.writeWorkspace({...pub,updated:Date.now()},{...priv,updated:Date.now(),account:`10000000-0000-4000-8000-00000000000${i}`});}finally{Date.now=original;}},{pub:publicSetup(),priv:privateSetup()});let records=await stored(page);expect(Object.keys(records).filter(k=>k.startsWith('account:')).sort()).toEqual([2,3,4].map(i=>`account:10000000-0000-4000-8000-00000000000${i}`));
  170 |  await page.evaluate(async({pub,priv})=>{const m=await import('/src/lib/workspace-storage.ts'),original=Date.now;Date.now=()=>1000;try{await m.writeWorkspace({...pub,updated:1000},{...priv,updated:1000,account:'10000000-0000-4000-8000-000000000005'});}finally{Date.now=original;}},{pub:publicSetup(),priv:privateSetup()});records=await stored(page);expect(Object.keys(records).filter(k=>k.startsWith('account:')).sort()).toEqual([3,4,5].map(i=>`account:10000000-0000-4000-8000-00000000000${i}`));expect([3,4,5].map(i=>records[`account:10000000-0000-4000-8000-00000000000${i}`].completed)).toEqual([3,4,5]);
  171 | });
  172 | test('private completion ordinal is storage-only bounded metadata and projections remain accepted',async({page})=>{
  173 |  await setup(page);const result=await page.evaluate(async priv=>{const {parsePrivate,parsePublic}=await import('/src/lib/workspace-storage.ts');return {projection:!!parsePrivate(priv),committed:!!parsePrivate({...priv,completed:Number.MAX_SAFE_INTEGER}),zero:!!parsePrivate({...priv,completed:0}),fraction:!!parsePrivate({...priv,completed:1.5}),overflow:!!parsePrivate({...priv,completed:Number.MAX_SAFE_INTEGER+1}),public:!!parsePublic({...priv,completed:1})};},privateSetup());expect(result).toEqual({projection:true,committed:true,zero:false,fraction:false,overflow:false,public:false});
  174 | });
  175 | test('accepted distinct tab keys sharing an incarnation keep independent private candidates',async({page})=>{
  176 |  await setup(page);const pub=publicSetup(3),priv=privateSetup(3);for(const tab of pub.tabs)tab.incarnation='shared-life';for(const tab of priv.tabs)tab.incarnation='shared-life';await seed(page,pub,priv);await owner(page);await page.goto('/');for(let i=0;i<3;i++)await expect(tabs(page).nth(i)).toHaveText(`Private label ${i+1}`);await expect.poll(async()=>(await stored(page))[`account:${account}`]?.tabs.length).toBe(3);
  177 | });
  178 | test('late automatic bootstrap never steals focus from a newer open selector',async({page})=>{
  179 |  await setup(page);await seed(page,publicSetup(12));await delayStorageOpen(page,1000);await page.goto('/');await page.getByRole('button',{name:'New workspace tab',exact:true}).click();await expect(page.getByRole('dialog',{name:'Book and chapter selector'})).toBeVisible();await page.waitForTimeout(1200);expect(await page.evaluate(()=>document.activeElement?.closest('[role=dialog],dialog')?.getAttribute('aria-label'))).toBe('Book and chapter selector');await expect(page.getByRole('dialog',{name:'Restore remembered reading setups'})).toHaveCount(0);
  180 | });
  181 | for(const {heldInitialResize,gesture} of [{heldInitialResize:false,gesture:'wheel'},...['wheel','touchmove','keydown','pointerdown'].map(gesture=>({heldInitialResize:true,gesture}))])test('last public scroll checkpoint survives tools hiding the pane before the durable write'+(heldInitialResize?' with delayed initial resize '+gesture:''),async({page})=>{
  182 | 
  183 |  await page.addInitScript(controlled=>{
  184 |   const events=[];window.scrollCheckpointObservations=events;let sequence=0;
  185 |   if(controlled){
  186 |    const NativeResizeObserver=window.ResizeObserver,held=[];let released=false;
  187 |    window.ResizeObserver=class extends NativeResizeObserver{constructor(callback){super((entries,observer)=>{if(!released&&entries.some(entry=>entry.target.matches?.('[data-reader-scroll]'))){held.push(()=>{if(!observer.fixtureDisconnected)callback(entries,observer);});return;}callback(entries,observer);});}disconnect(){this.fixtureDisconnected=true;super.disconnect();}};
  188 |    const seen=new WeakSet();new MutationObserver(()=>{for(const el of document.querySelectorAll('[data-reader-scroll]'))if(!seen.has(el)){seen.add(el);el.style.display='none';}}).observe(document,{subtree:true,childList:true});
  189 |    window.releaseControlledReaderResize=()=>{released=true;window.ResizeObserver=NativeResizeObserver;for(const callback of held.splice(0))callback();};
  190 |   }
  191 | 
  192 |   const state=()=>{const el=document.querySelector('[data-reader-scroll]'),snap=history.state?.usr?.scribeswellReader;return {sequence:++sequence,time:Math.round(performance.now()),pane:el?.dataset.paneKey,ready:el?.dataset.ready,deviceReady:document.querySelector('[aria-label="Workspace tabs"]')?.getAttribute('data-device-ready'),top:el?.scrollTop,height:el?.clientHeight,scrollHeight:el?.scrollHeight,entry:history.state?.key,tab:snap?.tabKey,revision:snap?.revision,anchor:snap?.panes[0]?.anchor};};
  193 |   const record=(event,extra={})=>{if(events.length<160)events.push({event,...state(),...extra});};
  194 |   const descriptor=Object.getOwnPropertyDescriptor(Element.prototype,'scrollTop');
  195 |   Object.defineProperty(Element.prototype,'scrollTop',{...descriptor,set(value){descriptor.set.call(this,value);if(this.matches?.('[data-reader-scroll]'))record('set-scrollTop',{requested:value});}});
  196 |   for(const name of ['wheel','touchmove','keydown','pointerdown','pointerup','scroll'])document.addEventListener(name,event=>{if(event.target?.matches?.('[data-reader-scroll]')){record(name);if(name==='wheel'){let frames=0;const frame=()=>{record('frame',{frame:++frames});if(frames<12)requestAnimationFrame(frame);};requestAnimationFrame(frame);}}},true);
  197 |   for(const name of ['pushState','replaceState']){const original=history[name];history[name]=function(...args){const result=original.apply(this,args);record(name);return result;};}
  198 |  },heldInitialResize);
> 199 |  try{await setup(page);const initial=publicSetup(1);initial.tabs[0].panes[0].anchor={chapter:1,verse:3,word:1,offset:0};await seed(page,initial);await page.route('**/api/bible/**/verses',r=>r.fulfill({json:{data:Array.from({length:31},(_,i)=>({id:i+1,verse_num:i+1,book_id:1,chapter_num:1,words:[{id:i+1,position:1,surface_he:'בְּרֵאשִׁית',display_he:'בְּרֵאשִׁית',lemma_strong:null,morph_code:null}]})),total:31}}));await page.goto('/');const scroll=page.locator('[data-reader-scroll]');await expect(scroll).toHaveAttribute('data-ready','true');await scroll.evaluate((el,gesture)=>{if(window.releaseControlledReaderResize)el.style.display='';el.dispatchEvent(gesture==='wheel'?new WheelEvent('wheel',{bubbles:true}):gesture==='keydown'?new KeyboardEvent('keydown',{key:'PageDown',bubbles:true}):gesture==='pointerdown'?new PointerEvent('pointerdown',{button:0,pointerId:91,bubbles:true}):new Event('touchmove',{bubbles:true}));el.scrollTop=350;el.dispatchEvent(new Event('scroll',{bubbles:true}));window.releaseControlledReaderResize?.();if(gesture==='pointerdown')window.dispatchEvent(new PointerEvent('pointerup',{button:0,pointerId:91,bubbles:true}));},gesture);await expect.poll(()=>page.evaluate(()=>history.state.usr?.scribeswellReader?.panes[0]?.anchor?.verse)).toBeGreaterThan(3);const anchor=await page.evaluate(()=>history.state.usr.scribeswellReader.panes[0].anchor);await expect.poll(async()=>(await stored(page)).public?.tabs[0]?.panes[0]?.anchor).toEqual(anchor);await page.getByRole('button',{name:'Analysis',exact:true}).click();await page.waitForTimeout(2100);expect((await stored(page)).public.tabs[0].panes[0].anchor).toEqual(anchor);
      |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       ^ Error: expect(received).toBeGreaterThan(expected)
  200 |  }finally{console.log('SCROLL_CHECKPOINT_DIAGNOSTIC',JSON.stringify(await page.evaluate(()=>window.scrollCheckpointObservations??[]).catch(()=>[])));}
  201 | });
  202 | test('real device reload restores four independent pane references anchors and active pane plus inactive tab position',async({page})=>{
  203 |  await setup(page);const pub=publicSetup();pub.tabs[0].panes=Array.from({length:4},(_,i)=>({paneKey:`four-${i}`,ref:{...reference,target:{kind:'chapter',chapter:i+1}},anchor:{chapter:i+1,verse:3+i*2,word:1,offset:0}}));pub.tabs[0].activePaneKey='four-2';pub.tabs[1].panes[0].ref={...reference,target:{kind:'chapter',chapter:5}};pub.tabs[1].panes[0].anchor={chapter:5,verse:10,word:1,offset:0};await seed(page,pub);
  204 |  await page.route('**/api/bible/**',r=>{const path=new URL(r.request().url()).pathname,b={id:1,osis_id:'Gen',name_en:'Genesis',name_he:'בראשית',testament:'OT',book_order:1},chapter=Number(path.match(/chapters\/(\d+)/)?.[1]??1);return r.fulfill({json:path.endsWith('/books')?{data:[b],total:1}:path.endsWith('/verses')?{data:Array.from({length:31},(_,i)=>({id:chapter*100+i+1,verse_num:i+1,book_id:1,chapter_num:chapter,words:[{id:chapter*100+i+1,position:1,surface_he:'בְּרֵאשִׁית',display_he:'בְּרֵאשִׁית',lemma_strong:null,morph_code:null}]})),total:31}:{...b,chapters:Array.from({length:5},(_,i)=>({id:i+1,chapter_num:i+1}))}});});
  205 |  async function positioned(key,verse,index){const switcher=page.getByRole('button',{name:new RegExp(`^Show passage ${index+1}:`)});if(await switcher.count())await switcher.click();const scroll=page.locator(`[data-reader-scroll][data-pane-key="${key}"]`);await expect(scroll).toBeVisible();await expect(scroll).toHaveAttribute('data-ready','true');await expect.poll(()=>scroll.evaluate((node,verse)=>{const word=node.querySelector(`[data-verse="${verse}"] [data-word-position="1"]`);return word?Math.abs(word.getBoundingClientRect().top-node.getBoundingClientRect().top):Infinity;},verse)).toBeLessThan(3);}
  206 |  await page.goto('/');await expect(tabs(page)).toHaveCount(2);await settled(page);await page.reload();await expect(tabs(page)).toHaveCount(2);await expect.poll(()=>page.evaluate(()=>history.state.usr?.scribeswellReader?.activePaneKey)).toBe('four-2');expect(await page.evaluate(()=>history.state.usr.scribeswellReader.panes.map(p=>p.ref.target.chapter))).toEqual([1,2,3,4]);
  207 |  for(let i=0;i<4;i++)await positioned(`four-${i}`,3+i*2,i);
  208 |  await tabs(page).nth(1).click();await positioned('pane-1',10,0);await tabs(page).first().click();for(let i=0;i<4;i++)await positioned(`four-${i}`,3+i*2,i);await settled(page);await page.reload();await expect(tabs(page)).toHaveCount(2);for(let i=0;i<4;i++)await positioned(`four-${i}`,3+i*2,i);await tabs(page).nth(1).click();await positioned('pane-1',10,0);
  209 | });
  210 | for(const scope of ['note','study'])test(`current ${scope}404 clears every affected live association after origin intent while preserving unrelated lanes`,async({page})=>{
  211 |  await setup(page);const pub=publicSetup(3),priv=privateSetup(3),otherNote='40000000-0000-4000-8000-000000000002',otherStudy=scope==='note'?study:'30000000-0000-4000-8000-000000000002';priv.tabs[2].note=otherNote;priv.tabs[2].study=otherStudy;await seed(page,pub,priv);let reads=0,release,studyReads=0,allowSecondStudy;const secondStudyGate=new Promise(resolve=>allowSecondStudy=resolve);const gate=new Promise(resolve=>release=resolve);
  212 |  await owner(page,{read:async r=>{const path=new URL(r.request().url()).pathname,isNote=path.includes('/notes/'),parent=path.split('/')[3],id=path.split('/').at(-1);if(scope==='note'&&!isNote&&parent===study&&++studyReads===2)await secondStudyGate;if((scope==='note'&&isNote&&id===note)||(scope==='study'&&!isNote&&id===study)){reads++;if(reads===2){await gate;return r.fulfill({status:404,json:{code:'resource_unavailable'}});}}return r.fulfill({json:isNote?{id,study_id:parent,owner_account_id:account,revision:'1',visibility:'study',value:{document:{version:1,blocks:[{type:'paragraph',direction:'auto',content:[{type:'text',text:id===note?'Saved note A':'Saved note B',marks:[]}]}]},connections:[],highlights:[]}}:{id,owner_account_id:account,title:'Authorized study',revision:'1'}});}});
  213 |  await page.goto('/');await expect(tabs(page).first()).toHaveText('Private label 1');allowSecondStudy();await expect(tabs(page).nth(2)).toHaveText('Private label 3');await page.getByRole('button',{name:'Analysis',exact:true}).click();await expect(page.getByRole('textbox',{name:'Note text',exact:true})).toHaveText('Saved note A');release();await expect(page.getByRole('textbox',{name:'Note text',exact:true})).toHaveCount(0);await expect(page.getByText('Private label 1',{exact:true})).toHaveCount(0);await expect(tabs(page).nth(2)).toHaveText('Private label 3');await tabs(page).nth(2).click();await page.getByRole('button',{name:'Analysis',exact:true}).click();await expect(page.getByRole('textbox',{name:'Note text',exact:true})).toHaveText('Saved note B');await expect(tabs(page)).toHaveCount(3);
  214 |  await expect.poll(async()=>{const rows=(await stored(page))[`account:${account}`]?.tabs;return rows?.filter(row=>row.note===note||row.study===study&&scope==='study').length;}).toBe(0);if(scope==='note')expect((await stored(page))[`account:${account}`].tabs.filter(row=>row.study===study&&!row.note)).toHaveLength(2);
  215 | });
  216 | test('current hydration401 masks all context and explicit fresh Retry retains dirty lane and original save command',async({page})=>{
  217 |  await setup(page);await seed(page,publicSetup(),privateSetup());let notes=0,release,writes=[],studyReads=0,allowSecondStudy;const secondStudyGate=new Promise(resolve=>allowSecondStudy=resolve);const gate=new Promise(resolve=>release=resolve);await owner(page,{read:async r=>{const path=new URL(r.request().url()).pathname;if(path.endsWith('/notes/'+note)){notes++;if(notes===2){await gate;return r.fulfill({status:401,json:{code:'authentication_required'}});}return r.fulfill({json:{id:note,study_id:study,owner_account_id:account,revision:notes>2?'2':'1',visibility:'study',value:{document:{version:1,blocks:[{type:'paragraph',direction:'auto',content:[{type:'text',text:notes>2?'New server acknowledgement':'Initial acknowledgement',marks:[]}]}]},connections:[],highlights:[]}}});}if(++studyReads===2)await secondStudyGate;return r.fulfill({json:{id:study,owner_account_id:account,title:'Owned study',revision:'1'}});}});await page.route(`**/api/studies/${study}/notes/${note}`,r=>{if(r.request().method()==='GET')return r.fallback();writes.push(r.request().postDataJSON());return r.fulfill({status:503,json:{code:'studies_storage_unavailable'}});});
  218 |  await page.goto('/');await expect(tabs(page).first()).toHaveText('Private label 1');allowSecondStudy();await expect.poll(()=>notes).toBe(2);await page.getByRole('button',{name:'Analysis',exact:true}).click();await page.getByRole('textbox',{name:'Note text',exact:true}).fill('Dirty input retains its original lane');await expect.poll(()=>writes.length).toBe(1);const original=structuredClone(writes[0]);release();await expect(page.getByRole('textbox',{name:'Note text',exact:true})).toHaveCount(0);await expect(page.getByText('Private label 1',{exact:true})).toHaveCount(0);expect((await stored(page))[`account:${account}`].tabs).toHaveLength(2);
  219 |  await page.getByRole('status').filter({hasText:'Private reading context not restored.'}).getByRole('button',{name:'Retry',exact:true}).click();const decision=page.getByRole('dialog',{name:'Restore remembered reading setups'});await expect(decision).toBeVisible();await decision.getByRole('button',{name:'Restore setups',exact:true}).click();await expect(tabs(page).first()).toHaveText('Private label 1');await expect(page.getByRole('textbox',{name:'Note text',exact:true})).toHaveText('Dirty input retains its original lane');expect(notes).toBeGreaterThan(2);expect(writes).toEqual([original]);expect(JSON.stringify(await stored(page))).not.toContain('Dirty input retains its original lane');
  220 | });
  221 | 
  222 | // Review loop 1: retain loop 0 assertions and add executable counterexamples.
  223 | for(const shape of ['null study','null note','wrong note ID','wrong note parent','wrong note owner'])test(`loop1 requested ${shape} never exposes a private label`,async({page})=>{
  224 |  await setup(page);await seed(page,publicSetup(1),privateSetup(1));
  225 |  await owner(page,{read:r=>{const isNote=new URL(r.request().url()).pathname.includes('/notes/');return r.fulfill({json:isNote?(shape==='null note'?null:{id:shape==='wrong note ID'?other:note,study_id:shape==='wrong note parent'?other:study,owner_account_id:shape==='wrong note owner'?other:account,revision:'1',visibility:'study',value:{document:{version:1,blocks:[]},connections:[],highlights:[]}}):(shape==='null study'?null:{id:study,owner_account_id:account,title:'Owned',revision:'1'})});}});
  226 |  await page.goto('/');await expect(page.getByRole('status').filter({hasText:'Private reading context not restored.'})).toBeVisible();await expect(tabs(page).first()).toHaveText('Genesis 1');expect((await stored(page))[`account:${account}`].tabs[0]).toMatchObject({study,note,label:'Private label 1'});
  227 | });
  228 | test('loop1 eviction Retry repopulates an unchanged successful live projection',async({page})=>{
  229 |  await setup(page);await add(page);await settled(page);const old=(await stored(page)).public;
  230 |  await page.evaluate(async old=>{const {workspaceDatabase}=await import('/src/lib/workspace-storage.ts');await new Promise((resolve,reject)=>{const r=indexedDB.open(workspaceDatabase,1);r.onsuccess=()=>{const db=r.result,tx=db.transaction('metadata','readwrite');tx.objectStore('metadata').put({...old,v:2},'public');tx.oncomplete=()=>{db.close();resolve();};tx.onerror=reject;};});},old);
  231 |  await add(page);await expect(page.getByRole('status').filter({hasText:'Reading setup not remembered.'})).toBeVisible();await page.getByRole('button',{name:'Close tab 3',exact:true}).click();
  232 |  await page.evaluate(async()=>{const {workspaceDatabase}=await import('/src/lib/workspace-storage.ts');await new Promise((resolve,reject)=>{const r=indexedDB.deleteDatabase(workspaceDatabase);r.onsuccess=resolve;r.onerror=reject;});});
  233 |  await page.getByRole('status').filter({hasText:'Reading setup not remembered.'}).getByRole('button',{name:'Retry',exact:true}).click();await settled(page);expect((await stored(page)).public.tabs.map(t=>t.tabKey)).toEqual(old.tabs.map(t=>t.tabKey));
  234 | });
  235 | test('loop1 alternating owners have bounded queued writes and truthful overload failure',async({page})=>{
  236 |  await setup(page);await settled(page);
  237 |  const result=await page.evaluate(async({pub,priv})=>{
  238 |   const m=await import('/src/lib/workspace-storage.ts'),original=IDBDatabase.prototype.transaction;let release;const gate=new Promise(resolve=>release=resolve);let held=false,transactions=0;
  239 |   IDBDatabase.prototype.transaction=function(...args){const tx=original.apply(this,args);if(args[1]==='readwrite')transactions++;if(args[1]==='readwrite'&&!held){held=true;const object=tx.objectStore('metadata');let keep=true;const pump=()=>{const req=object.get('hold');req.onsuccess=()=>{if(keep)pump();};};pump();gate.then(()=>{keep=false;});}return tx;};
  240 |   const writes=Array.from({length:200},(_,i)=>m.writeWorkspace(pub,{...priv,account:i%2?priv.account:'10000000-0000-4000-8000-000000000002'}).then(()=>({ok:true}),()=>({ok:false})));
  241 |   await new Promise(resolve=>setTimeout(resolve,100));release();const results=await Promise.all(writes);IDBDatabase.prototype.transaction=original;
  242 |   return {accepted:results.filter(r=>r.ok).length,rejected:results.filter(r=>!r.ok).length,first:results[0].ok,transactions};
  243 |  },{pub:publicSetup(),priv:privateSetup()});expect(result.first).toBe(true);expect(result.accepted).toBe(9);expect(result.transactions).toBe(9);expect(result.rejected).toBeGreaterThan(0);
  244 | });
  245 | const secondStudy='30000000-0000-4000-8000-000000000002',secondNote='40000000-0000-4000-8000-000000000002';
  246 | const ownedStudy=id=>({id,owner_account_id:account,title:id===study?'Study A':'Study B',revision:'1'});
  247 | const ownedNote=(id,parent=study)=>({id,study_id:parent,owner_account_id:account,visibility:'study',revision:'1',value:{document:{version:1,blocks:[{type:'paragraph',direction:'auto',content:[{type:'text',text:id===note?'Saved note A':'Saved note B',marks:[]}]}]},connections:[],highlights:[]}});
  248 | async function selectFirstNote(page){await page.getByRole('button',{name:'Studies',exact:true}).click();await page.getByRole('button',{name:'Study A',exact:true}).click();await page.getByRole('button',{name:'Saved note A',exact:true}).click();await expect(page.getByRole('textbox',{name:'Note text',exact:true})).toHaveText('Saved note A');}
  249 | function normalResources(r){const path=new URL(r.request().url()).pathname,parts=path.split('/'),parent=parts[3]==='search'?undefined:parts[3];return r.fulfill({json:path.endsWith('/passages')?{study_id:parent,revision:'1',items:[]}:path.endsWith('/notes')?{items:[ownedNote(note,parent),ownedNote(secondNote,parent)],next_cursor:null}:path.includes('/notes/')?ownedNote(parts.at(-1),parent):parent?ownedStudy(parent):{items:[ownedStudy(study),ownedStudy(secondStudy)],next_cursor:null}});}
  250 | for(const scope of ['study','note'])test(`loop1 delayed A ${scope} denial cannot clear newer live B selection or label`,async({page})=>{
  251 |  await setup(page);await seed(page,publicSetup(),privateSetup());let seen=0,release;const gate=new Promise(resolve=>release=resolve);
  252 |  await owner(page,{read:async r=>{const path=new URL(r.request().url()).pathname;if(path.endsWith(scope==='study'?'/'+study:'/notes/'+note)&&++seen===2){await gate;return r.fulfill({status:404,json:{code:'resource_unavailable'}});}return normalResources(r);}});
  253 |  await page.goto('/');await expect(tabs(page).first()).toHaveText('Private label 1');await expect.poll(()=>!!release).toBe(true);await tabs(page).nth(1).click();await page.getByRole('button',{name:'Studies',exact:true}).click();await page.getByRole('button',{name:scope==='study'?'Study B':'Study A',exact:true}).click();await page.getByRole('button',{name:'Saved note B',exact:true}).click();await page.getByRole('button',{name:'Rename tab 2',exact:true}).click();await page.getByLabel('Tab name',{exact:true}).fill('New live B label');await page.getByRole('dialog',{name:'Rename workspace tab'}).getByRole('button',{name:'Save',exact:true}).click();
  254 |  release();await page.waitForTimeout(450);await expect(tabs(page).nth(1)).toHaveText('New live B label');await expect(page.getByRole('textbox',{name:'Note text',exact:true})).toHaveText('Saved note B');await expect.poll(async()=>{const row=(await stored(page))[`account:${account}`]?.tabs.find(t=>t.tabKey==='saved-1');return row&&{study:row.study,note:row.note,label:row.label};}).toEqual({study:scope==='study'?secondStudy:study,note:secondNote,label:'New live B label'});
  255 | });
  256 | test('loop1 first acknowledged UI selection writes private IDs then automatically restores on reload',async({page})=>{
  257 |  await setup(page);await owner(page,{read:normalResources});await page.goto('/');await selectFirstNote(page);await expect.poll(async()=>{const rows=(await stored(page))[`account:${account}`]?.tabs;return rows?.map(t=>({study:t.study,note:t.note}));}).toEqual([{study,note}]);await page.reload();await expect(page.locator('[aria-label="Note text"]')).toHaveCount(1);await page.getByRole('button',{name:'Analysis',exact:true}).click();await expect(page.getByRole('textbox',{name:'Note text',exact:true})).toHaveText('Saved note A');
  258 | });
  259 | test('loop1 same-owner coalescing bounds retained waiters to64 per pending batch',async({page})=>{
  260 |  await setup(page);await settled(page);const result=await page.evaluate(async({pub,priv})=>{
  261 |  const m=await import('/src/lib/workspace-storage.ts'),original=IDBDatabase.prototype.transaction;let release,held=false;const gate=new Promise(resolve=>release=resolve);
  262 |  IDBDatabase.prototype.transaction=function(...args){const tx=original.apply(this,args);if(args[1]==='readwrite'&&!held){held=true;let keep=true;const pump=()=>{const r=tx.objectStore('metadata').get('hold');r.onsuccess=()=>{if(keep)pump();};};pump();gate.then(()=>keep=false);}return tx;};
  263 |  const writes=Array.from({length:200},()=>m.writeWorkspace(pub,priv).then(()=>true,()=>false));await new Promise(resolve=>setTimeout(resolve,80));release();const results=await Promise.all(writes);IDBDatabase.prototype.transaction=original;return {accepted:results.filter(Boolean).length,first:results[0]};
  264 |  },{pub:publicSetup(),priv:privateSetup()});expect(result).toEqual({accepted:65,first:true});
  265 | });
  266 | async function replacePublic(page,pub){await page.evaluate(async pub=>{const {workspaceDatabase}=await import('/src/lib/workspace-storage.ts');await new Promise((resolve,reject)=>{const r=indexedDB.open(workspaceDatabase,1);r.onsuccess=()=>{const db=r.result,tx=db.transaction('metadata','readwrite');tx.objectStore('metadata').put(pub,'public');tx.oncomplete=()=>{db.close();resolve();};tx.onerror=reject;};r.onerror=reject;});},pub);}
  267 | async function stageDirtyCurrentVictims(page,shared){
  268 |  await setup(page);await seed(page,publicSetup(shared?2:1),privateSetup(shared?2:1));await owner(page,{read:normalResources});await page.goto('/');await expect(tabs(page).first()).toHaveText('Private label 1');if(shared)await expect(tabs(page).nth(1)).toHaveText('Private label 2');
  269 |  await add(page);const newKey=await page.evaluate(()=>history.state.usr.scribeswellReader.tabKey);await page.getByRole('button',{name:'Studies',exact:true}).click();await page.getByRole('button',{name:'Leave study',exact:true}).click();await tabs(page).first().click();await page.getByRole('button',{name:'Analysis',exact:true}).click();await page.getByRole('textbox',{name:'Note text',exact:true}).fill('Dirty current-victim input');await expect(page.getByRole('status').filter({hasText:'Changes not saved'})).toBeVisible();await page.locator(`[data-workspace-tab="${newKey}"]`).click();await settled(page);await expect.poll(async()=>(await stored(page)).public.activeTabKey).toBe(newKey);
  270 |  const live=await tabs(page).evaluateAll(nodes=>nodes.map(node=>node.dataset.workspaceTab));await replacePublic(page,{...publicSetup(),v:2});await tabs(page).first().click();await expect(page.getByRole('status').filter({hasText:'Reading setup not remembered.'})).toBeVisible();await page.locator(`[data-workspace-tab="${newKey}"]`).click();
  271 |  const pub=publicSetup(12);pub.tabs=pub.tabs.map((tab,i)=>({...tab,tabKey:`remembered-${i}`,incarnation:`remembered-life-${i}`}));pub.activeTabKey='remembered-0';await replacePublic(page,pub);await page.getByRole('status').filter({hasText:'Reading setup not remembered.'}).getByRole('button',{name:'Retry',exact:true}).click();await expect(page.getByRole('dialog',{name:'Restore remembered reading setups'})).toBeVisible();return live;
  272 | }
  273 | test('loop1 intermediate sole dirty victim choice then Cancel preserves input and tabs',async({page})=>{
  274 |  const live=await stageDirtyCurrentVictims(page,false),dialog=page.getByRole('dialog',{name:'Restore remembered reading setups'});await dialog.getByRole('button',{name:/Close current tab 1:/}).click();await expect(page.getByRole('dialog',{name:'Changes not saved'})).toHaveCount(0);await dialog.getByRole('button',{name:'Cancel',exact:true}).click();expect(await tabs(page).evaluateAll(nodes=>nodes.map(node=>node.dataset.workspaceTab))).toEqual(live);await tabs(page).first().click();if(await page.getByRole('button',{name:'Analysis',exact:true}).getAttribute('aria-pressed')!=='true')await page.getByRole('button',{name:'Analysis',exact:true}).click();await expect(page.getByRole('textbox',{name:'Note text',exact:true})).toHaveText('Dirty current-victim input');
  275 | });
  276 | for(const decision of ['Stay','Close anyway'])test(`loop1 shared dirty staged victims guard final survivors once and ${decision}`,async({page})=>{
  277 |  const live=await stageDirtyCurrentVictims(page,true),dialog=page.getByRole('dialog',{name:'Restore remembered reading setups'});await dialog.getByRole('button',{name:/Close current tab/}).first().click();await expect(page.getByRole('dialog',{name:'Changes not saved'})).toHaveCount(0);await dialog.getByRole('button',{name:/Close current tab/}).first().click();await expect(page.getByRole('dialog',{name:'Changes not saved'})).toHaveCount(0);await dialog.getByRole('button',{name:/Close remembered tab/}).first().click();const exit=page.getByRole('dialog',{name:'Changes not saved'});await expect(exit).toBeVisible();await exit.getByRole('button',{name:decision,exact:true}).click();
  278 |  if(decision==='Stay'){expect(await tabs(page).evaluateAll(nodes=>nodes.map(node=>node.dataset.workspaceTab))).toEqual(live);await tabs(page).first().click();if(await page.getByRole('button',{name:'Analysis',exact:true}).getAttribute('aria-pressed')!=='true')await page.getByRole('button',{name:'Analysis',exact:true}).click();await expect(page.getByRole('textbox',{name:'Note text',exact:true})).toHaveText('Dirty current-victim input');}
  279 |  else {await expect(tabs(page)).toHaveCount(12);for(const key of [live[0],live[2]])await expect(page.locator(`[data-workspace-tab="${key}"]`)).toHaveCount(0);await expect(page.getByRole('button',{name:'Recover note save 1',exact:true})).toBeVisible();}
  280 | });
  281 | test('loop1 overall30s hydration deadline hides unfinished candidates and rejects late responses until Retry',async({page})=>{
  282 |  await setup(page);const priv=privateSetup(6);for(const row of priv.tabs){delete row.study;delete row.note;}await seed(page,publicSetup(6),priv);let requests=[],retry=false;
  283 |  await owner(page,{read:async r=>{if(!retry)await new Promise(resolve=>requests.push(resolve));return r.fulfill({json:{items:[],next_cursor:null}});}});const clockStart=Date.now();await page.clock.install({time:clockStart});await page.clock.pauseAt(clockStart+1000);await page.goto('/');await expect.poll(()=>requests.length).toBe(2);
  284 |  await page.clock.fastForward(14000);requests[0]();requests[1]();await expect(tabs(page).first()).toHaveText('Private label 1');await expect.poll(()=>requests.length).toBe(4);
  285 |  await page.clock.fastForward(14000);requests[2]();requests[3]();await expect(tabs(page).nth(3)).toHaveText('Private label 4');await expect.poll(()=>requests.length).toBe(6);
  286 |  await page.clock.fastForward(2100);await expect(page.getByRole('status').filter({hasText:'Private reading context not restored.'})).toBeVisible();requests[4]();requests[5]();await page.waitForTimeout(100);await expect(tabs(page).nth(4)).toHaveText('Genesis 1');await expect(tabs(page).nth(5)).toHaveText('Genesis 1');
  287 |  retry=true;await page.getByRole('status').filter({hasText:'Private reading context not restored.'}).getByRole('button',{name:'Retry',exact:true}).click();await page.getByRole('dialog',{name:'Restore remembered reading setups'}).getByRole('button',{name:'Restore setups',exact:true}).click();await expect(tabs(page).nth(4)).toHaveText('Private label 5');await expect(tabs(page).nth(5)).toHaveText('Private label 6');
  288 | });
  289 | for(const lifecycle of ['pagehide','visibilitychange'])test(`loop1 ${lifecycle} flushes latest eligible projection before debounce`,async({page})=>{
  290 |  await setup(page);await settled(page);await page.clock.install();await add(page);await page.evaluate(event=>(event==='pagehide'?window:document).dispatchEvent(new Event(event)),lifecycle);await expect.poll(async()=>(await stored(page)).public.tabs.length).toBe(2);
  291 | });
  292 | test('loop1 lifecycle flush is suppressed while a restoration decision is unresolved',async({page})=>{
  293 |  await setup(page);const pub=publicSetup(12);await seed(page,pub);await page.goto('/?book=Gen&chapter=2');await expect(page.getByRole('dialog',{name:'Restore remembered reading setups'})).toBeVisible();await page.evaluate(()=>{document.dispatchEvent(new Event('visibilitychange'));window.dispatchEvent(new Event('pagehide'));});await page.waitForTimeout(400);expect((await stored(page)).public).toEqual(pub);
  294 | });
  295 | test('loop1 actual blocked upgrade times out queued storage open and recovers after contention',async({page})=>{
  296 |  await setup(page);await seed(page);const result=await page.evaluate(async()=>{
  297 |  const m=await import('/src/lib/workspace-storage.ts'),open=()=>new Promise((resolve,reject)=>{const r=indexedDB.open(m.workspaceDatabase,1);r.onsuccess=()=>resolve(r.result);r.onerror=reject;});const blocker=await open();let blocked=false;
  298 |  const upgrade=new Promise((resolve,reject)=>{const r=indexedDB.open(m.workspaceDatabase,2);r.onblocked=()=>blocked=true;r.onerror=reject;r.onsuccess=()=>{r.result.close();resolve();};});
  299 |  while(!blocked)await new Promise(resolve=>setTimeout(resolve,10));let failed=false;try{await m.readWorkspace();}catch{failed=true;}blocker.close();await upgrade;
```