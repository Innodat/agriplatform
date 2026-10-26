const {test,expect}=require('@playwright/test');
async function setup(page){
 await page.route('http://127.0.0.1:8001/**',r=>r.fulfill({json:[]}));
 await page.route('**/api/bible/**',r=>{
  const path=new URL(r.request().url()).pathname,b={id:1,osis_id:'Gen',name_en:'Genesis',name_he:'בראשית',testament:'OT',book_order:1};
  return r.fulfill({json:path.endsWith('/books')?{data:[b],total:1}:path.endsWith('/verses')?{data:[{id:1,verse_num:1,book_id:1,chapter_num:1,words:[{id:1,position:1,surface_he:'בְּרֵאשִׁית',display_he:'בְּרֵאשִׁית',lemma_strong:null,morph_code:null}]}],total:1}:{...b,chapters:[{id:1,chapter_num:1},{id:2,chapter_num:2}]}});
 });
 await page.goto('/');
}
const tabs=page=>page.getByRole('tablist',{name:'Workspace tabs'}).getByRole('tab');
async function add(page){await page.getByRole('button',{name:'New workspace tab',exact:true}).click();await page.getByRole('dialog',{name:'Book and chapter selector'}).getByRole('button',{name:'Cancel',exact:true}).click();}
test('tab activation closure and replay push exactly once and closed replay restores only public identity',async({page})=>{
 await setup(page);const initial=await page.evaluate(()=>history.state.idx);await add(page);
 const key=await page.evaluate(()=>history.state.usr.scribeswellReader.tabKey);expect(await page.evaluate(()=>history.state.idx)).toBe(initial+1);
 await tabs(page).first().click();expect(await page.evaluate(()=>history.state.idx)).toBe(initial+2);await tabs(page).first().click();expect(await page.evaluate(()=>history.state.idx)).toBe(initial+2);
 await page.getByRole('button',{name:'Close tab 2',exact:true}).click();expect(await page.evaluate(()=>history.state.idx)).toBe(initial+3);
 await page.goBack();await expect(tabs(page)).toHaveCount(1);await page.goBack();await expect(tabs(page)).toHaveCount(2);
 expect(await page.evaluate(()=>history.state.usr.scribeswellReader.tabKey)).toBe(key);expect(await page.evaluate(()=>history.state.idx)).toBe(initial+1);
});
test('tab labels stay out of public history and manual roving keys preserve activation',async({page})=>{
 await setup(page);await add(page);await page.getByRole('button',{name:'Rename tab 2',exact:true}).click();await page.getByLabel('Tab name',{exact:true}).fill('  עברית study  ');await page.getByRole('dialog',{name:'Rename workspace tab'}).getByRole('button',{name:'Save',exact:true}).click();
 await expect(tabs(page).nth(1)).toHaveText('עברית study');expect(await page.evaluate(()=>JSON.stringify(history.state)+location.href)).not.toContain('study');
 await tabs(page).nth(1).focus();await page.keyboard.press('Home');await expect(tabs(page).first()).toBeFocused();await expect(tabs(page).nth(1)).toHaveAttribute('aria-selected','true');await page.keyboard.press('Enter');await expect(tabs(page).first()).toHaveAttribute('aria-selected','true');
 await page.getByRole('button',{name:'Close tab 1',exact:true}).click();await expect(tabs(page)).toHaveCount(1);await expect(tabs(page).first()).toBeFocused();await expect(page.getByRole('button',{name:/Close tab/})).toHaveCount(0);
});
test('twelve tab cap never evicts and closed history requires explicit public-only victim choice',async({page})=>{
 await setup(page);await add(page);const closed=await page.evaluate(()=>history.state.usr.scribeswellReader.tabKey);await page.getByRole('button',{name:'Close tab 2',exact:true}).click();
 for(let i=0;i<11;i++)await add(page);await expect(tabs(page)).toHaveCount(12);await page.getByRole('button',{name:'New workspace tab',exact:true}).click();await expect(page.getByText('Close a tab to open another.',{exact:true})).toBeVisible();
 await page.evaluate(()=>history.go(-12));const dialog=page.getByRole('dialog',{name:'Choose tab to close and restore'});await expect(dialog).toBeVisible();await expect(tabs(page)).toHaveCount(12);const index=await page.evaluate(()=>history.state.idx);
 await dialog.getByRole('button',{name:/Close tab 3:/}).click();await expect(dialog).toHaveCount(0);await expect(tabs(page)).toHaveCount(12);expect(await page.evaluate(()=>history.state.idx)).toBe(index);
 expect(await tabs(page).filter({hasText:'Genesis'}).count()).toBe(12);expect(await page.locator(`[data-workspace-tab="${closed}"]`).getAttribute('aria-selected')).toBe('true');
});

test('valid Unicode punctuation snapshot tab identity remains selectable and close focus is safe',async({page})=>{
 const key='עברית "quoted" [pane] #1',catalogue=require('../src/generated/reference-catalogue.json');
 const ref={catalogue_id:catalogue.catalogue_id,catalogue_version:catalogue.catalogue_version,versification_id:catalogue.books[0].versification_id,book_id:'Gen',target:{kind:'chapter',chapter:1}};
 // The native key is installed before the initial app controller exists, so
 // no departing live controller can overwrite the arranged public identity.
 await page.addInitScript(({key,ref})=>{history.replaceState({...history.state,usr:{scribeswellReader:{v:1,tabKey:key,activePaneKey:'unicode-pane',panes:[{paneKey:'unicode-pane',ref}]}}},'');},{key,ref});
 await setup(page);await page.reload();await expect(tabs(page)).toHaveCount(1);expect(await tabs(page).first().getAttribute('data-workspace-tab')).toBe(key);await expect(page.getByRole('tabpanel',{name:'Genesis 1',exact:true})).toBeVisible();await add(page);await tabs(page).first().click();await page.getByRole('button',{name:'Close tab 1',exact:true}).click();await expect(tabs(page)).toHaveCount(1);await expect(tabs(page).first()).toBeFocused();
});

test('POP checkpoints the outgoing live tab anchor for a later explicit tab activation',async({page})=>{
 await setup(page);await page.route('**/api/bible/**/verses',r=>r.fulfill({json:{data:Array.from({length:31},(_,i)=>({id:i+1,verse_num:i+1,book_id:1,chapter_num:1,words:[{id:i+1,position:1,surface_he:'בְּרֵאשִׁית',display_he:'בְּרֵאשִׁית',lemma_strong:null,morph_code:null}]})),total:31}}));await page.reload();const scroll=page.locator('[data-reader-scroll]');await expect(scroll).toHaveAttribute('data-ready','true');const source=await scroll.evaluate(el=>{el.dispatchEvent(new WheelEvent('wheel',{bubbles:true}));el.scrollTop=140;el.dispatchEvent(new Event('scroll',{bubbles:true}));return el.scrollTop;});expect(source).toBeGreaterThan(50);await page.waitForTimeout(200);await add(page);await expect(scroll).toHaveAttribute('data-ready','true');const before=await scroll.evaluate(el=>{el.dispatchEvent(new WheelEvent('wheel',{bubbles:true}));el.scrollTop=350;el.dispatchEvent(new Event('scroll',{bubbles:true}));return el.scrollTop;});expect(before).toBeGreaterThan(100);await page.waitForTimeout(200);await page.goBack();await expect.poll(async()=>Math.abs(await scroll.evaluate(el=>el.scrollTop)-source)).toBeLessThan(3);await page.goForward();await expect.poll(async()=>Math.abs(await scroll.evaluate(el=>el.scrollTop)-before)).toBeLessThan(3);await page.goBack();await expect.poll(async()=>Math.abs(await scroll.evaluate(el=>el.scrollTop)-source)).toBeLessThan(3);await tabs(page).nth(1).click();await expect(scroll).toHaveAttribute('data-ready','true');await expect.poll(async()=>Math.abs(await scroll.evaluate(el=>el.scrollTop)-before)).toBeLessThan(3);
});


test('closing the sole pane delegates to tab closure and preserves the final reader without reset',async({page})=>{
 await setup(page);const first=await tabs(page).first().getAttribute('data-workspace-tab');await add(page);const index=await page.evaluate(()=>history.state.idx),reference=await page.evaluate(()=>history.state.usr.scribeswellReader.panes[0].ref);await page.getByRole('button',{name:'Close passage 1',exact:true}).click();await expect(tabs(page)).toHaveCount(1);expect(await tabs(page).first().getAttribute('data-workspace-tab')).toBe(first);await expect(tabs(page).first()).toHaveAttribute('aria-selected','true');await expect(tabs(page).first()).toBeFocused();expect(await page.evaluate(()=>history.state.idx)).toBe(index+1);expect(await page.evaluate(()=>history.state.usr.scribeswellReader.panes[0].ref)).toEqual(reference);await expect(page.getByRole('button',{name:'Close passage 1',exact:true})).toHaveCount(0);await expect(page.getByRole('button',{name:/Close tab/})).toHaveCount(0);await expect(page.getByRole('button',{name:/Word: בְּרֵאשִׁית/})).toBeVisible();
});

test('review tabs B8 complete manual keyboard movement wraps and reveals all twelve controls without activation',async({page})=>{
 await setup(page);for(let i=0;i<11;i++)await add(page);const list=page.getByRole('tablist',{name:'Workspace tabs'}),controls=tabs(page),index=await page.evaluate(()=>history.state.idx);await controls.nth(11).focus();
 for(const [key,target] of [['ArrowRight',0],['ArrowLeft',11],['Home',0],['ArrowRight',1],['End',11],['ArrowLeft',10]]){await page.keyboard.press(key);await expect(controls.nth(target)).toBeFocused();expect(await page.evaluate(()=>history.state.idx)).toBe(index);await expect(controls.nth(11)).toHaveAttribute('aria-selected','true');const bounds=await controls.nth(target).evaluate(el=>{const r=el.getBoundingClientRect(),p=el.closest('[role="tablist"]').getBoundingClientRect();return {left:r.left-p.left,right:r.right-p.right};});expect(bounds.left).toBeGreaterThanOrEqual(-1);expect(bounds.right).toBeLessThanOrEqual(1);}
 await page.keyboard.press('Space');await expect(controls.nth(10)).toHaveAttribute('aria-selected','true');expect(await page.evaluate(()=>history.state.idx)).toBe(index+1);await page.keyboard.press('Home');await page.keyboard.press('Enter');await expect(controls.first()).toHaveAttribute('aria-selected','true');expect(await page.evaluate(()=>history.state.idx)).toBe(index+2);await expect(list).toBeVisible();
});

test('P10 malformed tab provenance never revives scrubbed complete callback query credentials',async({page})=>{
 await setup(page);
 const user={id:'33333333-3333-3333-3333-333333333333',email:'synthetic-reader@example.invalid',aud:'authenticated',app_metadata:{},user_metadata:{}};
 const token=[{alg:'HS256',typ:'JWT'},{sub:user.id,exp:Math.floor(Date.now()/1000)+3600},'synthetic-signature'].map(value=>Buffer.from(typeof value==='string'?value:JSON.stringify(value)).toString('base64url')).join('.');
 let releaseUser,userReads=0;
 await page.route('**/auth/v1/user*',async route=>{userReads++;await new Promise(resolve=>releaseUser=resolve);await route.fulfill({json:user});});
 const query=new URLSearchParams({reader:'{}',foreign:'kept value',access_token:token,refresh_token:'synthetic-refresh-only',expires_in:'3600',token_type:'bearer',type:'signup',code:'synthetic-code-only',provider_token:'synthetic-provider-only',provider_refresh_token:'synthetic-provider-refresh-only'});
 await page.goto('/?'+query);
 await expect(page.getByText('Invalid reading link',{exact:true})).toBeVisible();
 await expect.poll(()=>!!releaseUser).toBe(true);
 // The SDK must still see its callback until provider verification finishes.
 expect(await page.evaluate(()=>new URLSearchParams(location.search).has('access_token'))).toBe(true);
 releaseUser();
 await expect(page.getByRole('button',{name:'Sign out',exact:true})).toBeVisible();
 await expect.poll(()=>page.evaluate(()=>[...new URLSearchParams(location.search).keys()].sort())).toEqual(['foreign','reader']);
 expect(userReads).toBe(1);
 await page.evaluate(()=>history.replaceState({...history.state,foreignNative:'retained',usr:{...history.state.usr,foreignUser:'retained'}},''));
 const cleanQuery=()=>page.evaluate(()=>({keys:[...new URLSearchParams(location.search).keys()].sort(),foreign:new URLSearchParams(location.search).get('foreign'),native:history.state.foreignNative,user:history.state.usr.foreignUser}));
 const expected={keys:['foreign','reader'],foreign:'kept value',native:'retained',user:'retained'};
 await page.getByRole('button',{name:'New workspace tab',exact:true}).click();
 await expect(page.getByRole('dialog',{name:'Book and chapter selector'})).toBeVisible();
 expect(await cleanQuery()).toEqual(expected);
 expect(new URL(page.url()).searchParams.get('reader')).toBe('{}');
 await page.getByRole('dialog',{name:'Book and chapter selector'}).getByRole('button',{name:'Chapter 1 of Genesis',exact:true}).click();
 await expect(page.getByText('Invalid reading link',{exact:true})).toHaveCount(0);
 expect(await cleanQuery()).toEqual(expected);
 await tabs(page).first().click();
 await expect(page.getByText('Invalid reading link',{exact:true})).toBeVisible();
 expect(new URL(page.url()).searchParams.get('reader')).toBe('{}');
 expect(await cleanQuery()).toEqual(expected);
 await expect(page.getByRole('button',{name:'Sign out',exact:true})).toBeVisible();
});

test('P10 ordinary malformed tab retains raw search bytes when no callback fields exist',async({page})=>{
 await setup(page);
 const raw='?reader=%7b%7d&foreign=a%20b&foreign=%2f&flag&empty=&other=%7e';
 await page.goto('/'+raw);
 expect(new URL(page.url()).search).toBe(raw);
 await page.getByRole('button',{name:'New workspace tab',exact:true}).click();
 await page.getByRole('dialog',{name:'Book and chapter selector'}).getByRole('button',{name:'Chapter 1 of Genesis',exact:true}).click();
 await tabs(page).first().click();
 await expect(page.getByText('Invalid reading link',{exact:true})).toBeVisible();
 expect(new URL(page.url()).search).toBe(raw);
});
