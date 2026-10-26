# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: workspace-tabs.spec.cjs >> tab activation closure and replay push exactly once and closed replay restores only public identity
- Location: tests/workspace-tabs.spec.cjs:12:1

# Error details

```
Error: page.evaluate: Test ended.
```

# Test source

```ts
  1   | const {test,expect}=require('@playwright/test');
  2   | async function setup(page){
  3   |  await page.route('http://127.0.0.1:8001/**',r=>r.fulfill({json:[]}));
  4   |  await page.route('**/api/bible/**',r=>{
  5   |   const path=new URL(r.request().url()).pathname,b={id:1,osis_id:'Gen',name_en:'Genesis',name_he:'בראשית',testament:'OT',book_order:1};
  6   |   return r.fulfill({json:path.endsWith('/books')?{data:[b],total:1}:path.endsWith('/verses')?{data:[{id:1,verse_num:1,book_id:1,chapter_num:1,words:[{id:1,position:1,surface_he:'בְּרֵאשִׁית',display_he:'בְּרֵאשִׁית',lemma_strong:null,morph_code:null}]}],total:1}:{...b,chapters:[{id:1,chapter_num:1},{id:2,chapter_num:2}]}});
  7   |  });
  8   |  await page.goto('/');
  9   | }
  10  | const tabs=page=>page.getByRole('tablist',{name:'Workspace tabs'}).getByRole('tab');
  11  | async function add(page){await page.getByRole('button',{name:'New workspace tab',exact:true}).click();await page.getByRole('dialog',{name:'Book and chapter selector'}).getByRole('button',{name:'Cancel',exact:true}).click();}
  12  | test('tab activation closure and replay push exactly once and closed replay restores only public identity',async({page})=>{
> 13  |  await setup(page);const initial=await page.evaluate(()=>history.state.idx);await add(page);
      |                                             ^ Error: page.evaluate: Test ended.
  14  |  const key=await page.evaluate(()=>history.state.usr.scribeswellReader.tabKey);expect(await page.evaluate(()=>history.state.idx)).toBe(initial+1);
  15  |  await tabs(page).first().click();expect(await page.evaluate(()=>history.state.idx)).toBe(initial+2);await tabs(page).first().click();expect(await page.evaluate(()=>history.state.idx)).toBe(initial+2);
  16  |  await page.getByRole('button',{name:'Close tab 2',exact:true}).click();expect(await page.evaluate(()=>history.state.idx)).toBe(initial+3);
  17  |  await page.goBack();await expect(tabs(page)).toHaveCount(1);await page.goBack();await expect(tabs(page)).toHaveCount(2);
  18  |  expect(await page.evaluate(()=>history.state.usr.scribeswellReader.tabKey)).toBe(key);expect(await page.evaluate(()=>history.state.idx)).toBe(initial+1);
  19  | });
  20  | test('tab labels stay out of public history and manual roving keys preserve activation',async({page})=>{
  21  |  await setup(page);await add(page);await page.getByRole('button',{name:'Rename tab 2',exact:true}).click();await page.getByLabel('Tab name',{exact:true}).fill('  עברית study  ');await page.getByRole('dialog',{name:'Rename workspace tab'}).getByRole('button',{name:'Save',exact:true}).click();
  22  |  await expect(tabs(page).nth(1)).toHaveText('עברית study');expect(await page.evaluate(()=>JSON.stringify(history.state)+location.href)).not.toContain('study');
  23  |  await tabs(page).nth(1).focus();await page.keyboard.press('Home');await expect(tabs(page).first()).toBeFocused();await expect(tabs(page).nth(1)).toHaveAttribute('aria-selected','true');await page.keyboard.press('Enter');await expect(tabs(page).first()).toHaveAttribute('aria-selected','true');
  24  |  await page.getByRole('button',{name:'Close tab 1',exact:true}).click();await expect(tabs(page)).toHaveCount(1);await expect(tabs(page).first()).toBeFocused();await expect(page.getByRole('button',{name:/Close tab/})).toHaveCount(0);
  25  | });
  26  | test('twelve tab cap never evicts and closed history requires explicit public-only victim choice',async({page})=>{
  27  |  await setup(page);await add(page);const closed=await page.evaluate(()=>history.state.usr.scribeswellReader.tabKey);await page.getByRole('button',{name:'Close tab 2',exact:true}).click();
  28  |  for(let i=0;i<11;i++)await add(page);await expect(tabs(page)).toHaveCount(12);await page.getByRole('button',{name:'New workspace tab',exact:true}).click();await expect(page.getByText('Close a tab to open another.',{exact:true})).toBeVisible();
  29  |  await page.evaluate(()=>history.go(-12));const dialog=page.getByRole('dialog',{name:'Choose tab to close and restore'});await expect(dialog).toBeVisible();await expect(tabs(page)).toHaveCount(12);const index=await page.evaluate(()=>history.state.idx);
  30  |  await dialog.getByRole('button',{name:/Close tab 3:/}).click();await expect(dialog).toHaveCount(0);await expect(tabs(page)).toHaveCount(12);expect(await page.evaluate(()=>history.state.idx)).toBe(index);
  31  |  expect(await tabs(page).filter({hasText:'Genesis'}).count()).toBe(12);expect(await page.locator(`[data-workspace-tab="${closed}"]`).getAttribute('aria-selected')).toBe('true');
  32  | });
  33  | 
  34  | test('valid Unicode punctuation snapshot tab identity remains selectable and close focus is safe',async({page})=>{
  35  |  const key='עברית "quoted" [pane] #1',catalogue=require('../src/generated/reference-catalogue.json');
  36  |  const ref={catalogue_id:catalogue.catalogue_id,catalogue_version:catalogue.catalogue_version,versification_id:catalogue.books[0].versification_id,book_id:'Gen',target:{kind:'chapter',chapter:1}};
  37  |  // The native key is installed before the initial app controller exists, so
  38  |  // no departing live controller can overwrite the arranged public identity.
  39  |  await page.addInitScript(({key,ref})=>{history.replaceState({...history.state,usr:{scribeswellReader:{v:1,tabKey:key,activePaneKey:'unicode-pane',panes:[{paneKey:'unicode-pane',ref}]}}},'');},{key,ref});
  40  |  await setup(page);await page.reload();await expect(tabs(page)).toHaveCount(1);expect(await tabs(page).first().getAttribute('data-workspace-tab')).toBe(key);await expect(page.getByRole('tabpanel',{name:'Genesis 1',exact:true})).toBeVisible();await add(page);await tabs(page).first().click();await page.getByRole('button',{name:'Close tab 1',exact:true}).click();await expect(tabs(page)).toHaveCount(1);await expect(tabs(page).first()).toBeFocused();
  41  | });
  42  | 
  43  | test('POP checkpoints the outgoing live tab anchor for a later explicit tab activation',async({page})=>{
  44  |  await setup(page);await page.route('**/api/bible/**/verses',r=>r.fulfill({json:{data:Array.from({length:31},(_,i)=>({id:i+1,verse_num:i+1,book_id:1,chapter_num:1,words:[{id:i+1,position:1,surface_he:'בְּרֵאשִׁית',display_he:'בְּרֵאשִׁית',lemma_strong:null,morph_code:null}]})),total:31}}));await page.reload();const scroll=page.locator('[data-reader-scroll]');await expect(scroll).toHaveAttribute('data-ready','true');const source=await scroll.evaluate(el=>{el.dispatchEvent(new WheelEvent('wheel',{bubbles:true}));el.scrollTop=140;el.dispatchEvent(new Event('scroll',{bubbles:true}));return el.scrollTop;});expect(source).toBeGreaterThan(50);await page.waitForTimeout(200);await add(page);await expect(scroll).toHaveAttribute('data-ready','true');const before=await scroll.evaluate(el=>{el.dispatchEvent(new WheelEvent('wheel',{bubbles:true}));el.scrollTop=350;el.dispatchEvent(new Event('scroll',{bubbles:true}));return el.scrollTop;});expect(before).toBeGreaterThan(100);await page.waitForTimeout(200);await page.goBack();await expect.poll(async()=>Math.abs(await scroll.evaluate(el=>el.scrollTop)-source)).toBeLessThan(3);await page.goForward();await expect.poll(async()=>Math.abs(await scroll.evaluate(el=>el.scrollTop)-before)).toBeLessThan(3);await page.goBack();await expect.poll(async()=>Math.abs(await scroll.evaluate(el=>el.scrollTop)-source)).toBeLessThan(3);await tabs(page).nth(1).click();await expect(scroll).toHaveAttribute('data-ready','true');await expect.poll(async()=>Math.abs(await scroll.evaluate(el=>el.scrollTop)-before)).toBeLessThan(3);
  45  | });
  46  | 
  47  | 
  48  | test('closing the sole pane delegates to tab closure and preserves the final reader without reset',async({page})=>{
  49  |  await setup(page);const first=await tabs(page).first().getAttribute('data-workspace-tab');await add(page);const index=await page.evaluate(()=>history.state.idx),reference=await page.evaluate(()=>history.state.usr.scribeswellReader.panes[0].ref);await page.getByRole('button',{name:'Close passage 1',exact:true}).click();await expect(tabs(page)).toHaveCount(1);expect(await tabs(page).first().getAttribute('data-workspace-tab')).toBe(first);await expect(tabs(page).first()).toHaveAttribute('aria-selected','true');await expect(tabs(page).first()).toBeFocused();expect(await page.evaluate(()=>history.state.idx)).toBe(index+1);expect(await page.evaluate(()=>history.state.usr.scribeswellReader.panes[0].ref)).toEqual(reference);await expect(page.getByRole('button',{name:'Close passage 1',exact:true})).toHaveCount(0);await expect(page.getByRole('button',{name:/Close tab/})).toHaveCount(0);await expect(page.getByRole('button',{name:/Word: בְּרֵאשִׁית/})).toBeVisible();
  50  | });
  51  | 
  52  | test('review tabs B8 complete manual keyboard movement wraps and reveals all twelve controls without activation',async({page})=>{
  53  |  await setup(page);for(let i=0;i<11;i++)await add(page);const list=page.getByRole('tablist',{name:'Workspace tabs'}),controls=tabs(page),index=await page.evaluate(()=>history.state.idx);await controls.nth(11).focus();
  54  |  for(const [key,target] of [['ArrowRight',0],['ArrowLeft',11],['Home',0],['ArrowRight',1],['End',11],['ArrowLeft',10]]){await page.keyboard.press(key);await expect(controls.nth(target)).toBeFocused();expect(await page.evaluate(()=>history.state.idx)).toBe(index);await expect(controls.nth(11)).toHaveAttribute('aria-selected','true');const bounds=await controls.nth(target).evaluate(el=>{const r=el.getBoundingClientRect(),p=el.closest('[role="tablist"]').getBoundingClientRect();return {left:r.left-p.left,right:r.right-p.right};});expect(bounds.left).toBeGreaterThanOrEqual(-1);expect(bounds.right).toBeLessThanOrEqual(1);}
  55  |  await page.keyboard.press('Space');await expect(controls.nth(10)).toHaveAttribute('aria-selected','true');expect(await page.evaluate(()=>history.state.idx)).toBe(index+1);await page.keyboard.press('Home');await page.keyboard.press('Enter');await expect(controls.first()).toHaveAttribute('aria-selected','true');expect(await page.evaluate(()=>history.state.idx)).toBe(index+2);await expect(list).toBeVisible();
  56  | });
  57  | 
  58  | test('P10 malformed tab provenance never revives scrubbed complete callback query credentials',async({page})=>{
  59  |  await setup(page);
  60  |  const user={id:'33333333-3333-3333-3333-333333333333',email:'synthetic-reader@example.invalid',aud:'authenticated',app_metadata:{},user_metadata:{}};
  61  |  const token=[{alg:'HS256',typ:'JWT'},{sub:user.id,exp:Math.floor(Date.now()/1000)+3600},'synthetic-signature'].map(value=>Buffer.from(typeof value==='string'?value:JSON.stringify(value)).toString('base64url')).join('.');
  62  |  let releaseUser,userReads=0;
  63  |  await page.route('**/auth/v1/user*',async route=>{userReads++;await new Promise(resolve=>releaseUser=resolve);await route.fulfill({json:user});});
  64  |  const query=new URLSearchParams({reader:'{}',foreign:'kept value',access_token:token,refresh_token:'synthetic-refresh-only',expires_in:'3600',token_type:'bearer',type:'signup',code:'synthetic-code-only',provider_token:'synthetic-provider-only',provider_refresh_token:'synthetic-provider-refresh-only'});
  65  |  await page.goto('/?'+query);
  66  |  await expect(page.getByText('Invalid reading link',{exact:true})).toBeVisible();
  67  |  await expect.poll(()=>!!releaseUser).toBe(true);
  68  |  // The SDK must still see its callback until provider verification finishes.
  69  |  expect(await page.evaluate(()=>new URLSearchParams(location.search).has('access_token'))).toBe(true);
  70  |  releaseUser();
  71  |  await expect(page.getByRole('button',{name:'Sign out',exact:true})).toBeVisible();
  72  |  await expect.poll(()=>page.evaluate(()=>[...new URLSearchParams(location.search).keys()].sort())).toEqual(['foreign','reader']);
  73  |  expect(userReads).toBe(1);
  74  |  await page.evaluate(()=>history.replaceState({...history.state,foreignNative:'retained',usr:{...history.state.usr,foreignUser:'retained'}},''));
  75  |  const cleanQuery=()=>page.evaluate(()=>({keys:[...new URLSearchParams(location.search).keys()].sort(),foreign:new URLSearchParams(location.search).get('foreign'),native:history.state.foreignNative,user:history.state.usr.foreignUser}));
  76  |  const expected={keys:['foreign','reader'],foreign:'kept value',native:'retained',user:'retained'};
  77  |  await page.getByRole('button',{name:'New workspace tab',exact:true}).click();
  78  |  await expect(page.getByRole('dialog',{name:'Book and chapter selector'})).toBeVisible();
  79  |  expect(await cleanQuery()).toEqual(expected);
  80  |  expect(new URL(page.url()).searchParams.get('reader')).toBe('{}');
  81  |  await page.getByRole('dialog',{name:'Book and chapter selector'}).getByRole('button',{name:'Chapter 1 of Genesis',exact:true}).click();
  82  |  await expect(page.getByText('Invalid reading link',{exact:true})).toHaveCount(0);
  83  |  expect(await cleanQuery()).toEqual(expected);
  84  |  await tabs(page).first().click();
  85  |  await expect(page.getByText('Invalid reading link',{exact:true})).toBeVisible();
  86  |  expect(new URL(page.url()).searchParams.get('reader')).toBe('{}');
  87  |  expect(await cleanQuery()).toEqual(expected);
  88  |  await expect(page.getByRole('button',{name:'Sign out',exact:true})).toBeVisible();
  89  | });
  90  | 
  91  | test('P10 ordinary malformed tab retains raw search bytes when no callback fields exist',async({page})=>{
  92  |  await setup(page);
  93  |  const raw='?reader=%7b%7d&foreign=a%20b&foreign=%2f&flag&empty=&other=%7e';
  94  |  await page.goto('/'+raw);
  95  |  expect(new URL(page.url()).search).toBe(raw);
  96  |  await page.getByRole('button',{name:'New workspace tab',exact:true}).click();
  97  |  await page.getByRole('dialog',{name:'Book and chapter selector'}).getByRole('button',{name:'Chapter 1 of Genesis',exact:true}).click();
  98  |  await tabs(page).first().click();
  99  |  await expect(page.getByText('Invalid reading link',{exact:true})).toBeVisible();
  100 |  expect(new URL(page.url()).search).toBe(raw);
  101 | });
  102 | 
```