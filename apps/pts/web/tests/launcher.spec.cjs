const {test,expect}=require('@playwright/test');
const {files,sessionFor}=require('./file-fixture.cjs');
test.beforeEach(async({page})=>files(page));
const org='11111111-1111-1111-1111-111111111111';
async function setup(page){
 await page.addInitScript(()=>localStorage.setItem('pts-auth',JSON.stringify({access_token:'test-token',refresh_token:'test-refresh',expires_at:Date.now()/1000+3600,expires_in:3600,token_type:'bearer',user:{id:'33333333-3333-3333-3333-333333333333',email:'fixture@example.invalid',aud:'authenticated',app_metadata:{},user_metadata:{}}})));
 await page.route('**/auth/v1/**',r=>r.fulfill({json:{}}));
 await page.route('http://127.0.0.1:8001/**',r=>r.fulfill({json:{apps:[{id:'pts',name:'PtS',url:'http://localhost:5179',icon:'book-open',description:'Swahili Poetry: poems, sources and witnesses',enabled:true},{id:'scribeswell',name:'Scribeswell',url:'http://localhost:5174',icon:'book-open',description:'Hebrew Bible reader with morphological analysis',enabled:true}],protected_access_status:'complete'}}));
 await page.route('http://127.0.0.1:8010/**',r=>r.fulfill({json:{schema_version:'1.2',exported_at:'fixture',note:'fixture',sources:[],rights:[],source_documents:[],poems:[],witnesses:[],filters:{},citations:{},total:0,collection_total:0}}));
 await page.goto('/?org='+org+'&view=sources');
}
test('launcher has readable styled app cards, current app and keyboard navigation',async({page})=>{
 await setup(page);const trigger=page.getByRole('button',{name:'App launcher',exact:true});
 await trigger.click();const menu=page.getByRole('menu',{name:'Available apps'});
 await expect(menu).toBeVisible();
 await expect(menu.getByText('Current app',{exact:true})).toBeVisible();
 const pts=menu.getByRole('menuitem',{name:'Open PtS',exact:true});const bible=menu.getByRole('menuitem',{name:'Open Scribeswell',exact:true});
 await expect(pts).toBeFocused();await page.keyboard.press('ArrowDown');await expect(bible).toBeFocused();
 await expect(bible).toHaveAttribute('href','http://localhost:5174');await expect(bible).toHaveAttribute('target','_blank');
 const styles=await menu.evaluate(el=>({shadow:getComputedStyle(el).boxShadow,width:el.getBoundingClientRect().width,right:el.getBoundingClientRect().right}));
 expect(styles.shadow).not.toBe('none');expect(styles.width).toBeGreaterThan(280);expect(styles.right).toBeLessThanOrEqual(await page.evaluate(()=>innerWidth));
 await page.screenshot({path:'/tmp/pts-launcher-'+test.info().project.name+'.png'});
 await page.keyboard.press('Escape');await expect(menu).toHaveCount(0);await expect(trigger).toBeFocused();
 await page.keyboard.press('ArrowDown');await expect(pts).toBeFocused();await page.keyboard.press('End');await expect(bible).toBeFocused();
 await page.keyboard.press('Tab');await expect(menu).toHaveCount(0);await expect(page.locator('.brand')).toBeFocused();
 await trigger.click();await page.keyboard.press('Shift+Tab');await expect(trigger).toBeFocused();await expect(menu).toHaveCount(0);
});
test('late discovery for a replaced PtS account never restores its links',async({page})=>{
 await setup(page);let release;let newObserved=false;
 const current={id:'current',name:'Current account app',url:'https://machon.io/current',icon:'book-open',description:'Current',enabled:true};
 await page.route('http://127.0.0.1:8001/api/v2/me/apps',async r=>{
  if(r.request().headers().authorization==='Bearer test-token'){await new Promise(resolve=>release=resolve);await r.fulfill({json:{apps:[{...current,id:'old',name:'Old account app'}],protected_access_status:'complete'}}).catch(()=>{});}
  else {newObserved=true;await r.fulfill({json:{apps:[current],protected_access_status:'complete'}});}
 });
 await page.getByRole('button',{name:'App launcher'}).click();await expect.poll(()=>Boolean(release)).toBe(true);
 const replacement=sessionFor('44444444-4444-4444-4444-444444444444','current@example.invalid');
 await page.route('**/auth/v1/token*',r=>r.fulfill({json:replacement}));
 await page.route('**/auth/v1/user',r=>r.fulfill({json:replacement.user}));
 await page.evaluate(async()=>{const {auth}=await import('/src/auth.ts');await auth.signInWithPassword({email:'current@example.invalid',password:'fixture'});});
 await expect.poll(()=>newObserved).toBe(true);if(!await page.getByRole('menu',{name:'Available apps'}).isVisible())await page.getByRole('button',{name:'App launcher'}).click();
 await expect(page.getByRole('menuitem',{name:'Open Current account app'})).toBeVisible();release();await page.waitForTimeout(100);await expect(page.getByRole('menuitem',{name:'Open Old account app'})).toHaveCount(0);
});
test('unavailable discovery Retry uses the current session and distinguishes empty success',async({page})=>{
 await setup(page);let mode='unavailable';const observations=[];
 const current={id:'pts',name:'PtS',url:'https://machon.io/pts/',icon:'book-open',description:'Current poetry app',enabled:true};
 await page.route('http://127.0.0.1:8001/api/v2/me/apps',r=>{observations.push(r.request().headers().authorization);return r.fulfill({json:{apps:mode==='links'?[current]:[],protected_access_status:mode==='links'?'complete':mode}});});
 await page.getByRole('button',{name:'App launcher'}).click();const menu=page.getByRole('menu');await expect(menu.getByRole('menuitem',{name:/Open /})).toHaveCount(0);const retry=menu.getByRole('menuitem',{name:'Retry'});await expect(retry).toBeFocused();
 mode='complete';await retry.click();await expect(menu.getByRole('status')).toContainText('No apps');await expect(menu.getByRole('menuitem')).toHaveCount(0);
 await page.keyboard.press('Escape');mode='links';await page.getByRole('button',{name:'App launcher'}).click();await expect(menu.getByRole('menuitem',{name:'Open PtS'})).toHaveAttribute('href',current.url);expect(observations.length).toBeGreaterThanOrEqual(3);expect(observations.every(value=>value==='Bearer test-token')).toBe(true);
});
test('expired discovery clears links and opens the existing PtS sign-in surface',async({page})=>{
 await setup(page);await page.route('http://127.0.0.1:8001/api/v2/me/apps',r=>r.fulfill({status:401,json:{error_id:'authentication_required'}}));await page.getByRole('button',{name:'App launcher'}).click();const menu=page.getByRole('menu');await expect(menu.getByRole('status')).toContainText('expired');await expect(menu.getByRole('menuitem',{name:/Open /})).toHaveCount(0);await menu.getByRole('menuitem',{name:'Sign in',exact:true}).click();await expect(menu).toHaveCount(0);await expect(page.getByRole('heading',{name:'Sign in to read'})).toBeVisible();await expect(page.getByLabel('Email',{exact:true})).toBeVisible();await expect(page.getByLabel('Password',{exact:true})).toBeVisible();
});
