import test from 'node:test';
import assert from 'node:assert/strict';
import {createServer} from 'vite';
import {chromium,expect} from '@playwright/test';
const fixture=new URL('.',import.meta.url).pathname;
let server,browser,origin;
const app=(id)=>({id,name:id,url:'https://machon.io/'+id,icon:'book-open',description:'App '+id,enabled:true});
test.before(async()=>{server=await createServer({root:fixture,configFile:false,server:{host:'127.0.0.1',port:0,fs:{allow:[new URL('../../../',import.meta.url).pathname]}}});await server.listen();origin=server.resolvedUrls.local[0];browser=await chromium.launch({headless:true});});
test.after(async()=>{await browser?.close();await server?.close();});
test('session and same-account token races never redisplay superseded links',async()=>{
 const page=await browser.newPage();let held=[];
 await page.route('**/api/v2/me/apps',async route=>{const token=route.request().headers().authorization;if(token==='Bearer first'||token==='Bearer refreshed'){await new Promise(resolve=>held.push(()=>route.fulfill({json:{apps:[app(token==='Bearer first'?'old':'stale')],protected_access_status:'complete'}}).then(resolve).catch(resolve)));}else await route.fulfill({json:{apps:[app('current')],protected_access_status:'complete'}});});
 await page.goto(origin);await expect.poll(()=>held.length).toBe(1);
 await page.evaluate(()=>window.setLauncherSession({accountId:'second',accessToken:'second'}));
 await expect(page.locator('[data-observation]')).toHaveText('complete');await page.getByRole('button',{name:'App launcher'}).click();
 await expect(page.getByRole('menuitem',{name:'Open current'})).toBeVisible();await held.shift()();await expect(page.getByRole('menuitem',{name:'Open old'})).toHaveCount(0);
 await page.evaluate(()=>window.setLauncherSession({accountId:'second',accessToken:'refreshed'}));await expect(page.getByRole('menuitem')).toHaveCount(0);await expect.poll(()=>held.length).toBe(1);
 await page.evaluate(()=>window.setLauncherSession({accountId:'second',accessToken:'latest'}));await expect(page.getByRole('menuitem',{name:'Open current'})).toBeVisible();await held.shift()();await expect(page.getByRole('menuitem',{name:'Open stale'})).toHaveCount(0);
 await page.evaluate(()=>window.setLauncherSession(null));await expect(page.getByRole('menuitem')).toHaveCount(0);await expect(page.getByRole('status')).toHaveText('Sign in to see your apps.');await page.close();
});
for(const transition of ['signed-out','other-session'])test('restoring the same session after '+transition+' waits for a fresh observation',async()=>{
 const page=await browser.newPage();let hold=false;const pending=[];
 await page.route('**/api/v2/me/apps',async route=>{
  const token=route.request().headers().authorization;
  if(hold)await new Promise(resolve=>pending.push({token,release:()=>route.fulfill({json:{apps:[app(token==='Bearer first'?'restored':'superseded')],protected_access_status:'complete'}}).then(resolve).catch(resolve)}));
  else await route.fulfill({json:{apps:[app('saved')],protected_access_status:'complete'}});
 });
 await page.goto(origin);await page.getByRole('button',{name:'App launcher'}).click();await expect(page.getByRole('menuitem',{name:'Open saved'})).toBeVisible();hold=true;
 await page.evaluate(value=>window.setLauncherSession(value),transition==='signed-out'?null:{accountId:'other',accessToken:'other'});
 await expect(page.locator('[data-observation]')).toHaveText(transition==='signed-out'?'sign_in_required':'loading');
 if(transition==='other-session')await expect.poll(()=>pending.length).toBe(1);
 await page.evaluate(()=>window.setLauncherSession({accountId:'first',accessToken:'first'}));await expect(page.locator('[data-observation]')).toHaveText('loading');await expect(page.getByRole('menuitem')).toHaveCount(0);
 await expect.poll(()=>pending.length).toBe(transition==='signed-out'?1:2);
 if(transition==='other-session'){await pending.shift().release();await expect(page.locator('[data-observation]')).toHaveText('loading');await expect(page.getByRole('menuitem')).toHaveCount(0);}
 assert.equal(pending[0].token,'Bearer first');await pending.shift().release();await expect(page.getByRole('menuitem',{name:'Open restored'})).toBeVisible();await expect(page.getByRole('menuitem',{name:'Open superseded'})).toHaveCount(0);await page.close();
});
test('unavailable Retry, empty keyboard, reopening and focus recheck',async()=>{
 const page=await browser.newPage({viewport:{width:320,height:568}});let mode='unavailable',calls=0;
 await page.route('**/api/v2/me/apps',route=>{calls++;return route.fulfill({json:{apps:mode==='complete'?[app('pts')]:[],protected_access_status:mode}});});
 await page.goto(origin);await page.getByRole('button',{name:'App launcher'}).click();const retry=page.getByRole('menuitem',{name:'Retry'});await expect(retry).toBeFocused();await page.keyboard.press('End');await expect(retry).toBeFocused();
 const bounds=await retry.boundingBox();assert.ok(bounds.height>=44);assert.ok(bounds.width>=44);
 mode='complete';await retry.click();await expect(page.getByRole('menuitem',{name:'Open pts'})).toBeVisible();
 await page.keyboard.press('Escape');mode='complete';const before=calls;await page.getByRole('button',{name:'App launcher'}).click();await expect.poll(()=>calls).toBeGreaterThan(before);
 await page.route('**/api/v2/me/apps',r=>r.fulfill({json:{apps:[],protected_access_status:'complete'}}));await page.evaluate(()=>window.dispatchEvent(new Event('focus')));await expect(page.getByRole('status')).toContainText('No apps');await page.keyboard.press('ArrowDown');await page.keyboard.press('Home');await page.keyboard.press('Escape');await expect(page.getByRole('button',{name:'App launcher'})).toBeFocused();
 await page.getByRole('button',{name:'App launcher'}).click();const menu=await page.getByRole('menu').boundingBox();assert.ok(menu.x>=0&&menu.x+menu.width<=320);await page.close();
});
test('loading status permits Shift+Tab back to the trigger without a focus trap',async()=>{
 const page=await browser.newPage();await page.route('**/api/v2/me/apps',r=>new Promise(()=>{}));await page.goto(origin);const trigger=page.getByRole('button',{name:'App launcher'});await trigger.click();await expect(page.getByRole('status')).toBeFocused();await page.keyboard.press('Shift+Tab');await expect(trigger).toBeFocused();await expect(page.getByRole('menu')).toHaveCount(0);await page.close();
});
test('anonymous and expired states without a host sign-in action focus their status',async()=>{
 const page=await browser.newPage();await page.route('**/api/v2/me/apps',r=>r.fulfill({status:401,json:{error_id:'authentication_required'}}));await page.goto(origin);const trigger=page.getByRole('button',{name:'App launcher'});await trigger.click();await expect(page.getByRole('status')).toBeFocused();await page.keyboard.press('Escape');await page.evaluate(()=>window.setLauncherSession(null));await trigger.click();await expect(page.getByRole('status')).toBeFocused();await page.keyboard.press('Shift+Tab');await expect(trigger).toBeFocused();await page.close();
});
test('rapid reopening and Shift+Tab remain closed when fresh discovery completes',async()=>{
 const page=await browser.newPage();await page.route('**/api/v2/me/apps',r=>r.fulfill({json:{apps:[app('current')],protected_access_status:'complete'}}));await page.goto(origin);const trigger=page.getByRole('button',{name:'App launcher'});
 for(let i=0;i<10;i++){await trigger.click();await page.keyboard.press('Shift+Tab');await expect(trigger).toBeFocused();await expect(page.getByRole('menu')).toHaveCount(0);}
 await page.close();
});
