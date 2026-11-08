const {test,expect}=require('@playwright/test');
const user={id:'33333333-3333-3333-3333-333333333333',email:'reader@example.invalid',aud:'authenticated',app_metadata:{},user_metadata:{}};
const session={access_token:'test-token',refresh_token:'test-refresh',expires_at:Date.now()/1000+3600,expires_in:3600,token_type:'bearer',user};
const apps=[{id:'scribeswell',name:'Scribeswell',description:'Hebrew Bible reader',icon:'book-open',url:'https://scribeswell.com/',enabled:true},{id:'pts',name:'PtS',description:'Swahili Poetry',icon:'book-open',url:'https://machon.io/pts/',enabled:true}];
async function setup(page,authenticated=true){
 if(authenticated)await page.addInitScript(s=>localStorage.setItem('pts-auth',JSON.stringify(s)),session);
 await page.route('**/auth/v1/**',r=>r.request().url().includes('logout')?r.fulfill({status:204}):r.fulfill({json:user}));
 await page.route('**/api/bible/**',r=>{const p=new URL(r.request().url()).pathname;const book={id:1,osis_id:'Gen',name_en:'Genesis',name_he:'בראשית',testament:'OT',book_order:1};return r.fulfill({json:p.endsWith('/books')?{data:[book],total:1}:p.endsWith('/books/Gen')?{...book,chapters:[{id:1,chapter_num:1}]}:{data:[{id:1,verse_num:1,book_id:1,chapter_num:1,words:[]}],total:1}});});
}
test('current account launcher preserves icon-only cards, links and keyboard on narrow/zoom viewports',async({page})=>{
 await setup(page);await page.route('http://127.0.0.1:8001/**',r=>r.fulfill({json:{apps,protected_access_status:'complete'}}));
 await page.goto('/');const trigger=page.getByRole('button',{name:'App launcher'});await trigger.click();const touch=await trigger.boundingBox();expect(touch.width).toBeGreaterThanOrEqual(44);expect(touch.height).toBeGreaterThanOrEqual(44);const menu=page.getByRole('menu');const first=menu.getByRole('menuitem',{name:'Open Scribeswell'});await expect(first).toBeFocused();await expect(first).toHaveAttribute('aria-current','page');await page.keyboard.press('End');await expect(menu.getByRole('menuitem',{name:'Open PtS'})).toBeFocused();await expect(first).toHaveAttribute('target','_blank');
 for(const width of [390,320]){await page.setViewportSize({width,height:700});const bounds=await menu.boundingBox();expect(bounds.x).toBeGreaterThanOrEqual(0);expect(bounds.x+bounds.width).toBeLessThanOrEqual(width);}
 await page.setViewportSize({width:1280,height:900});await page.evaluate(()=>document.documentElement.style.zoom='2');expect(await page.evaluate(()=>document.documentElement.scrollWidth)).toBeLessThanOrEqual(1280);await page.screenshot({path:'/tmp/scribeswell-launcher-zoom-'+test.info().project.name+'.png'});await page.keyboard.press('Escape');await expect(trigger).toBeFocused();
});
for(const state of ['unavailable','empty','expired','denied'])test('discovery '+state+' stays honest and reader remains usable',async({page})=>{
 await setup(page);let mode=state;
 await page.route('http://127.0.0.1:8001/**',r=>mode==='expired'?r.fulfill({status:401,json:{error_id:'authentication_required'}}):mode==='denied'?r.fulfill({status:403,json:{error_id:'access_denied'}}):r.fulfill({json:{apps:[],protected_access_status:mode==='unavailable'?'unavailable':'complete'}}));
 await page.goto(state==='expired'?'/?book=Gen&chapter=1':'/');await expect(page.getByRole('list',{name:'Verses'})).toBeVisible();await page.getByRole('button',{name:'App launcher'}).click();const menu=page.getByRole('menu');await expect(menu.getByRole('menuitem',{name:/Open /})).toHaveCount(0);
 if(state==='unavailable'){await expect(menu.getByRole('menuitem',{name:'Retry'})).toBeFocused();mode='empty';await menu.getByRole('menuitem',{name:'Retry'}).click();await expect(menu.getByRole('status')).toContainText('No apps');}
 else await expect(menu.getByRole('status')).toContainText(state==='expired'?'expired':state==='denied'?'cannot access':'No apps');
 if(state==='expired'){
  const passage=page.url();await expect(page.getByRole('button',{name:'Sign out',exact:true})).toBeVisible();await menu.getByRole('menuitem',{name:'Sign in',exact:true}).click();const dialog=page.getByRole('dialog',{name:'Sign in',exact:true});await expect(dialog).toBeVisible();await expect(dialog.getByLabel('Email',{exact:true})).toBeEditable();await expect(dialog.getByLabel('Password',{exact:true})).toBeEditable();await dialog.getByLabel('Email',{exact:true}).fill('retained-user@example.invalid');await dialog.getByLabel('Password',{exact:true}).fill('fixture-password');await dialog.getByRole('button',{name:'Close sign in dialog'}).click();await expect(dialog).toHaveCount(0);await expect(page).toHaveURL(passage);await expect(page.getByRole('button',{name:/Navigate: Genesis, chapter 1/})).toBeVisible();await expect(page.getByRole('list',{name:'Verses'})).toBeVisible();return;
 }
 await page.keyboard.press('Home');await page.keyboard.press('Escape');await expect(page.getByRole('list',{name:'Verses'})).toBeVisible();
});
test('anonymous launcher never requests public catalogue and signout clears observed links',async({page})=>{
 await setup(page);const paths=[];await page.route('http://127.0.0.1:8001/**',r=>{paths.push(new URL(r.request().url()).pathname);return r.fulfill({json:{apps,protected_access_status:'complete'}});});
 await page.goto('/');await page.getByRole('button',{name:'App launcher'}).click();await expect(page.getByRole('menuitem',{name:'Open PtS'})).toBeVisible();await page.keyboard.press('Escape');await page.getByRole('button',{name:'Sign out',exact:true}).click();await page.getByRole('button',{name:'App launcher'}).click();await expect(page.getByRole('menuitem',{name:/Open /})).toHaveCount(0);await expect(page.getByRole('menu').getByRole('status')).toContainText('Sign in');expect(paths).not.toContain('/api/apps');
});
test('late discovery for a replaced Scribeswell account never restores links or interrupts reading',async({page})=>{
 await setup(page);let release;
 await page.route('http://127.0.0.1:8001/api/v2/me/apps',async r=>{
  if(r.request().headers().authorization==='Bearer test-token'){await new Promise(resolve=>release=resolve);await r.fulfill({json:{apps:[{...apps[0],id:'old',name:'Old account app'}],protected_access_status:'complete'}}).catch(()=>{});}
  else await r.fulfill({json:{apps:[{...apps[0],id:'current',name:'Current account app'}],protected_access_status:'complete'}});
 });
 await page.goto('/');await page.getByRole('button',{name:'App launcher'}).click();await expect.poll(()=>Boolean(release)).toBe(true);
 await page.route('**/auth/v1/token*',r=>r.fulfill({json:{...session,access_token:'new-token',user:{...user,id:'44444444-4444-4444-4444-444444444444'}}}));
 await page.evaluate(async()=>{const {supabase}=await import('/src/lib/supabase.ts');await supabase.auth.signInWithPassword({email:'current@example.invalid',password:'fixture'});});
 await expect(page.getByRole('menuitem',{name:'Open Current account app'})).toBeVisible();release();await page.waitForTimeout(100);await expect(page.getByRole('menuitem',{name:'Open Old account app'})).toHaveCount(0);await expect(page.getByRole('list',{name:'Verses'})).toBeVisible();
});
