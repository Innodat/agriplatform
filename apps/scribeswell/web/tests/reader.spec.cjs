const {test,expect}=require('@playwright/test');
const book=(id,osis,name,he)=>({id,osis_id:osis,name_en:name,name_he:he,testament:'OT',book_order:id,division:'torah'});
const gen=book(1,'Gen','Genesis','בראשית'),ex=book(2,'Exod','Exodus','שמות');
const word=(id,text)=>({id,position:1,surface_he:text,display_he:text,lemma_strong:'H1',morph_code:'HNcmsa'});
const first=word(1,'בְּרֵאשִׁית'),second=word(2,'שֵׁמוֹת');
const verses=(b,w)=>({data:[{id:b.id,verse_num:1,book_id:b.id,chapter_num:1,words:[w]}],total:1});
async function setup(page){
 await page.route('http://127.0.0.1:8001/**',r=>r.fulfill({json:r.request().url().endsWith('/api/apps')?[]:{apps:[],context:{org_id:null,member_id:null,roles:[]}}}));
 await page.route('**/api/bible/**',r=>{
  const path=new URL(r.request().url()).pathname;
  if(path==='/api/bible/books')return r.fulfill({json:{data:[gen,ex],total:2}});
  if(path.includes('/words/'))return r.fulfill({json:{...first,morphemes:[{segment_index:0,language:'Hebrew',part_of_speech:'noun',pos_code:'N'}]}});
  const b=path.includes('/Exod')?ex:gen;
  if(path.endsWith('/verses'))return r.fulfill({json:verses(b,b===gen?first:second)});
  return r.fulfill({json:{...b,chapters:[{id:1,chapter_num:1},{id:2,chapter_num:2}]}});
 });
}
test('reader selector and morphology fit the viewport; Back clears old word selection',async({page})=>{
 await setup(page);await page.goto('/');
 await expect(page.getByRole('button',{name:/Word: בְּרֵאשִׁית/})).toBeVisible();
 await page.evaluate(()=>document.fonts.ready);expect(await page.evaluate(()=>document.fonts.check('20px "Noto Serif Hebrew"'))).toBe(true);
 await expect(page.locator('.verse-line').first()).toHaveCSS('font-family',/Noto Serif Hebrew/);
 await page.getByRole('button',{name:/Navigate:/}).click();
 const dialog=page.getByRole('dialog',{name:'Book and chapter selector'});await expect(dialog).toBeVisible();
 const bounds=await dialog.boundingBox();expect(bounds.x).toBeGreaterThanOrEqual(0);
 await page.getByRole('button',{name:/Exodus —/}).click();
 await dialog.getByRole('button',{name:'Chapter 1 of Exodus',exact:true}).click();
 await expect(page.getByRole('button',{name:/Word: שֵׁמוֹת/})).toBeVisible();
 await page.goBack();await expect(page.getByRole('button',{name:/Word: בְּרֵאשִׁית/})).toBeVisible();
 await page.getByRole('button',{name:/Word: בְּרֵאשִׁית/}).click();
 await expect(page.getByRole('complementary',{name:'Word morphology'})).toBeVisible();
 expect(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth)).toBe(false);
 await page.goForward();await expect(page.getByRole('complementary',{name:'Word morphology'})).toHaveCount(0);
});
test('late chapter responses cannot replace the chosen chapter',async({page})=>{
 await setup(page);let release;
 await page.route('**/api/bible/books/Gen/chapters/1/verses',async r=>{await new Promise(resolve=>release=resolve);await r.fulfill({json:verses(gen,first)});});
 await page.goto('/');await expect.poll(()=>Boolean(release)).toBe(true);
 await page.getByRole('button',{name:/Navigate:/}).click();const dialog=page.getByRole('dialog');
 await page.getByRole('button',{name:/Exodus —/}).click();await dialog.getByRole('button',{name:'Chapter 1 of Exodus',exact:true}).click();
 await expect(page.getByRole('button',{name:/Word: שֵׁמוֹת/})).toBeVisible();const late=page.waitForResponse('**/api/bible/books/Gen/chapters/1/verses');release();await (await late).finished();await page.evaluate(()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))));
 await expect(page.getByRole('button',{name:/Word: שֵׁמוֹת/})).toBeVisible();
 await expect(page.getByRole('button',{name:/Word: בְּרֵאשִׁית/})).toHaveCount(0);
});

test('shared launcher works in Scribeswell and private workspace files are denied',async({page})=>{
 await setup(page);
 await page.route('http://127.0.0.1:8001/**',r=>r.fulfill({json:[{id:'scribeswell',name:'Scribeswell',description:'Hebrew Bible reader',icon:'book-open',url:'http://localhost:5174',enabled:true},{id:'pts',name:'PtS',description:'Swahili Poetry',icon:'book-open',url:'http://localhost:5179',enabled:true}]}));
 await page.goto('/');const trigger=page.getByRole('button',{name:'App launcher'});await trigger.click();
 const menu=page.getByRole('menu');await expect(menu.getByText('Current app')).toBeVisible();
 await expect(menu.getByRole('menuitem',{name:'Open Scribeswell'})).toHaveAttribute('aria-current','page');
 await page.keyboard.press('ArrowDown');await expect(menu.getByRole('menuitem',{name:'Open PtS'})).toBeFocused();
 const b=await menu.boundingBox();expect(b.x).toBeGreaterThanOrEqual(0);expect(b.x+b.width).toBeLessThanOrEqual(await page.evaluate(()=>innerWidth));
 await page.keyboard.press('Escape');await expect(trigger).toBeFocused();
 const path=require('node:path').resolve(__dirname,'../../../pts/reference/poetry-library/library.json');
 expect((await page.request.get('/@fs'+path)).status()).toBe(403);
});
test('reader failures can be retried without losing the selected location',async({page})=>{
 await setup(page);let fail=true;
 await page.route('**/api/bible/books',r=>fail?r.fulfill({status:503,json:{error:'unavailable'}}):r.fallback());
 await page.route('**/api/bible/books/Gen/chapters/1/verses',r=>fail?r.fulfill({status:503,json:{error:'unavailable'}}):r.fallback());
 await page.goto('/');await expect(page.getByRole('button',{name:'Retry books'})).toBeVisible();await expect(page.getByRole('button',{name:'Retry chapter'})).toBeVisible();
 fail=false;await page.getByRole('button',{name:'Retry books'}).click();await page.getByRole('button',{name:'Retry chapter'}).click();
 await expect(page.getByRole('button',{name:/Navigate: Genesis/})).toBeVisible();await expect(page.getByRole('button',{name:/Word:/})).toBeVisible();
});
test('word analysis remains visible near the viewport in a long chapter',async({page})=>{
 await setup(page);await page.route('**/api/bible/books/Gen/chapters/1/verses',r=>r.fulfill({json:{data:Array.from({length:50},(_,i)=>({id:i+1,verse_num:i+1,book_id:1,chapter_num:1,words:[first]})),total:50}}));
 await page.goto('/');await page.getByRole('button',{name:/Word:/}).first().click();const panel=page.getByRole('complementary',{name:'Word morphology'});await expect(panel).toBeVisible();
 const b=await panel.boundingBox();expect(b.y).toBeLessThan(await page.evaluate(()=>innerHeight));expect(b.x+b.width).toBeLessThanOrEqual(await page.evaluate(()=>innerWidth));
 await panel.getByRole('button',{name:'Close morphology panel'}).click();await expect(panel).toHaveCount(0);
});
test('late book details cannot restore a previously hovered book',async({page})=>{
 await setup(page);let release;
 await page.route('**/api/bible/books/Gen',async r=>{await new Promise(resolve=>release=resolve);await r.fulfill({json:{...gen,chapters:[{id:1,chapter_num:1}]}});});
 await page.goto('/');await page.getByRole('button',{name:/Navigate:/}).click();await expect.poll(()=>Boolean(release)).toBe(true);
 await page.getByRole('button',{name:/Exodus —/}).click();await expect(page.getByRole('group',{name:'Chapters of Exodus'})).toBeVisible();
 const late=page.waitForResponse('**/api/bible/books/Gen');release();await (await late).finished();await page.evaluate(()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))));
 await expect(page.getByRole('group',{name:'Chapters of Exodus'})).toBeVisible();
});
test('late word analysis cannot replace a newer word or reopen a closed panel',async({page})=>{
 await setup(page);let release;
 await page.route('**/api/bible/books/Gen/chapters/1/verses',r=>r.fulfill({json:{data:[{id:1,verse_num:1,book_id:1,chapter_num:1,words:[first,{...second,position:2}]}],total:1}}));
 await page.route('**/api/bible/words/1/morphology',async r=>{await new Promise(resolve=>release=resolve);await r.fulfill({json:{...first,morphemes:[]}});});
 await page.route('**/api/bible/words/2/morphology',r=>r.fulfill({json:{...second,morphemes:[]}}));
 await page.goto('/');await page.getByRole('button',{name:/Word: בְּרֵאשִׁית/}).click();await expect.poll(()=>Boolean(release)).toBe(true);
 await page.getByRole('button',{name:/Word: שֵׁמוֹת/}).click();await expect(page.getByLabel('Hebrew word: שֵׁמוֹת',{exact:true})).toBeVisible();
 const late=page.waitForResponse('**/api/bible/words/1/morphology');release();await (await late).finished();await page.evaluate(()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))));
 await expect(page.getByLabel('Hebrew word: שֵׁמוֹת',{exact:true})).toBeVisible();
 await page.getByRole('button',{name:'Close morphology panel'}).click();release=null;
 await page.getByRole('button',{name:/Word: בְּרֵאשִׁית/}).click();await expect.poll(()=>Boolean(release)).toBe(true);
 await page.getByRole('button',{name:/Word: בְּרֵאשִׁית/}).click();
 const closed=page.waitForResponse('**/api/bible/words/1/morphology');release();await (await closed).finished();await page.evaluate(()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))));
 await expect(page.getByRole('complementary',{name:'Word morphology'})).toHaveCount(0);
});
test('long bilingual names and 150 chapters fit narrow and short viewports',async({page})=>{
 await setup(page);const ps={...gen,osis_id:'Ps',name_en:'Psalms',name_he:'תהילים',division:'ketuvim'};
 await page.setViewportSize({width:320,height:568});
 await page.route('**/api/bible/books',r=>r.fulfill({json:{data:[gen,ps,{...ex,name_en:'Song of Solomon',name_he:'שיר השירים'}],total:3}}));
 await page.route('**/api/bible/books/Ps',r=>r.fulfill({json:{...ps,chapters:Array.from({length:150},(_,i)=>({id:i+1,chapter_num:i+1}))}}));
 await page.goto('/');await page.getByRole('button',{name:/Navigate:/}).click();await page.getByRole('button',{name:/Psalms —/}).click();
 const chapter=page.getByRole('button',{name:'Chapter 150 of Psalms',exact:true});await chapter.scrollIntoViewIfNeeded();await expect(chapter).toBeInViewport();
 const b=await page.getByRole('dialog').boundingBox();expect(b.x).toBeGreaterThanOrEqual(0);expect(b.x+b.width).toBeLessThanOrEqual(320);
 await page.setViewportSize({width:667,height:375});await chapter.scrollIntoViewIfNeeded();await expect(chapter).toBeInViewport();
});
