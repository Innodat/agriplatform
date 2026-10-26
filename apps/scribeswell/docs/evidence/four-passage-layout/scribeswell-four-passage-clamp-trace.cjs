const fs=require('fs');
const pw=require('/home/ck/repos/innodat/agriplatform/node_modules/@playwright/test');
const source=fs.readFileSync('/home/ck/repos/innodat/agriplatform/apps/scribeswell/web/tests/four-passage.spec.cjs','utf8');
const {setup}=new Function('require',source.slice(0,source.indexOf("test('"))+'\nreturn {setup};')(p=>p==='@playwright/test'?pw:require(p));
(async()=>{const browser=await pw.chromium.launch({headless:true});try{for(let attempt=0;attempt<3;attempt++){
 const page=await browser.newPage({viewport:{width:390,height:844}});await setup(page);
 await page.addInitScript(()=>{
  window.__readerTrace=[];
  const snapshot=()=>[...document.querySelectorAll('[data-reader-scroll]')].map(n=>({top:n.scrollTop,height:n.clientHeight,width:n.clientWidth,max:n.scrollHeight-n.clientHeight,preserved:n.dataset.preservedScroll}));
  const emit=(event,extra={})=>window.__readerTrace.push({event,...extra,at:Math.round(performance.now()*10)/10,scroll:snapshot()});
  const descriptor=Object.getOwnPropertyDescriptor(Element.prototype,'scrollTop');
  Object.defineProperty(Element.prototype,'scrollTop',{...descriptor,set(value){const reader=this.hasAttribute('data-reader-scroll');if(reader)emit('set-before',{value,caller:new Error().stack.split('\n').slice(2,4).join(' ')});descriptor.set.call(this,value);if(reader)emit('set-after',{value});}});
  const Native=window.ResizeObserver;let next=0;
  window.ResizeObserver=class extends Native{constructor(callback){const id=++next;super((entries,observer)=>{emit('resize-before',{id,targets:entries.map(e=>e.target.hasAttribute('data-reader-scroll')?'scroll':'other')});callback(entries,observer);emit('resize-after',{id});});}};
  document.addEventListener('scroll',e=>{if(e.target instanceof Element&&e.target.hasAttribute('data-reader-scroll'))emit('scroll');},true);
  window.addEventListener('resize',()=>emit('viewport'));
 });
 await page.setViewportSize({width:1100,height:500});await page.goto('http://127.0.0.1:5182/');
 const scroll=page.locator('[data-reader-scroll]');await pw.expect(page.locator('[data-word-position]').first()).toBeVisible();await scroll.evaluate(el=>el.scrollTop=el.scrollHeight);const before=await scroll.evaluate(el=>el.scrollTop);
 await page.setViewportSize({width:1100,height:900});await page.setViewportSize({width:1100,height:500});await pw.expect.poll(()=>scroll.evaluate(el=>el.scrollTop)).toBe(before);
 await scroll.evaluate(el=>el.scrollTop=120);await page.setViewportSize({width:1100,height:900});await page.setViewportSize({width:1100,height:500});
 await page.waitForTimeout(200);const actual=await scroll.evaluate(el=>el.scrollTop);const trace=await page.evaluate(()=>window.__readerTrace);console.log(JSON.stringify({attempt,before,actual,trace}));await page.close();if(actual!==120){process.exitCode=1;break;}
}}finally{await browser.close();}})().catch(e=>{console.error(e.message);process.exitCode=1;});
