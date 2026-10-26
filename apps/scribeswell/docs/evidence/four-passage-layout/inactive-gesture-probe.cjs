const fs=require('fs');
const {chromium,expect}=require('/home/ck/repos/innodat/agriplatform/node_modules/@playwright/test');
const source=fs.readFileSync('/home/ck/repos/innodat/agriplatform/apps/scribeswell/web/tests/four-passage.spec.cjs','utf8');
const {setup,add}=new Function('require',source.slice(0,source.indexOf("test('"))+'\nreturn {setup,add};')(p=>p==='@playwright/test'?require('/home/ck/repos/innodat/agriplatform/node_modules/@playwright/test'):require(p));
(async()=>{const browser=await chromium.launch({headless:true});try{
 const page=await browser.newPage({viewport:{width:1600,height:1000}});await setup(page);await page.goto('http://127.0.0.1:5182/');await add(page);await page.evaluate(()=>document.fonts.ready);
 const pane=page.locator('[data-reader-pane]').first(),scroll=pane.locator('[data-reader-scroll]');await expect(scroll).toBeVisible();await page.clock.install();
 const before=await page.evaluate(()=>history.state.key);await scroll.dispatchEvent('pointerdown',{pointerId:73,button:0});await expect(pane).toHaveAttribute('aria-current','true');
 const after=await page.evaluate(()=>history.state.key);await scroll.evaluate(n=>{n.scrollTop=120;n.dispatchEvent(new Event('scroll'));});await page.clock.runFor(1500);await scroll.evaluate(n=>{n.scrollTop=280;n.dispatchEvent(new Event('scroll'));});await page.clock.runFor(150);
 const expected=await scroll.evaluate(n=>{const b=n.getBoundingClientRect(),w=[...n.querySelectorAll('[data-word-position]')].find(x=>x.getBoundingClientRect().bottom>b.top);return {chapter:1,verse:Number(w.closest('[data-verse]').dataset.verse),word:Number(w.dataset.wordPosition),offset:Math.round(w.getBoundingClientRect().top-b.top)};});
 await page.evaluate(()=>window.dispatchEvent(new PointerEvent('pointerup',{pointerId:73,button:0})));
 const actual=await page.evaluate(()=>history.state.usr.scribeswellReader.panes[0].anchor);console.log(JSON.stringify({before,after,expected,actual}));expect(actual).toEqual(expected);
}finally{await browser.close();}})().catch(e=>{console.error(e.message);process.exitCode=1;});
