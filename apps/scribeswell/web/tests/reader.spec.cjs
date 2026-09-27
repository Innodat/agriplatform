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
 await page.goto('/');
 const header=page.getByRole('banner');const launcherBounds=await header.getByRole('button',{name:'App launcher'}).boundingBox();const authBounds=await header.getByRole('button',{name:'Sign in',exact:true}).boundingBox();
 expect(launcherBounds.x).toBe(16);expect(authBounds.x+authBounds.width).toBe(await page.evaluate(()=>innerWidth-16));expect((await header.boundingBox()).height).toBe(57);
 const trigger=page.getByRole('button',{name:'App launcher'});await expect(trigger).toHaveText('');await expect(trigger).toHaveAttribute('title','App launcher');await trigger.click();
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
 const panelBounds=await page.getByRole('dialog').boundingBox();expect(panelBounds.y).toBeGreaterThanOrEqual(0);expect(panelBounds.y+panelBounds.height).toBeLessThanOrEqual(375);expect(await page.evaluate(()=>scrollY)).toBe(0);
 await chapter.focus();await page.keyboard.press('Escape');await expect(page.getByRole('button',{name:/Navigate:/})).toBeFocused();
});
test('only chapter text scrolls while navigation and morphology remain in view',async({page},info)=>{
 await setup(page);
 await page.route('**/api/bible/books/Gen/chapters/1/verses',r=>r.fulfill({json:{data:Array.from({length:100},(_,i)=>({id:i+1,verse_num:i+1,book_id:1,chapter_num:1,words:[first]})),total:100}}));
 await page.goto('/');const text=page.getByRole('region',{name:'Chapter text'});const navigation=page.getByRole('button',{name:/Navigate:/});
 await page.getByRole('button',{name:/Word:/}).first().click();const analysis=page.getByRole('complementary',{name:'Word morphology'});await expect(analysis).toBeVisible();
 const before=await analysis.boundingBox();const navBefore=await navigation.boundingBox();
 await text.focus();await page.keyboard.press('PageDown');await expect.poll(()=>text.evaluate(el=>el.scrollTop)).toBeGreaterThan(0);
 await text.evaluate(el=>el.scrollTop=el.scrollHeight);
 await expect(page.getByLabel('Verse 100',{exact:true})).toBeInViewport();
 const after=await analysis.boundingBox();const navAfter=await navigation.boundingBox();expect(Math.abs(after.y-before.y)).toBeLessThan(2);expect(Math.abs(navAfter.y-navBefore.y)).toBeLessThan(2);expect(await page.evaluate(()=>window.scrollY)).toBe(0);
 if(info.project.name==='mobile'){const last=await page.getByLabel('Verse 100',{exact:true}).boundingBox();expect(last.y+last.height).toBeLessThanOrEqual(after.y);}
 await navigation.click();await page.getByRole('button',{name:/Exodus —/}).click();await page.getByRole('button',{name:'Chapter 1 of Exodus'}).click();await expect(page.getByRole('button',{name:/Word: שֵׁמוֹת/})).toBeVisible();await expect.poll(()=>text.evaluate(el=>el.scrollTop)).toBe(0);
});
test('long morphology scrolls independently and text stays at a readable width',async({page},info)=>{
 await setup(page);await page.route('**/api/bible/words/1/morphology',r=>r.fulfill({json:{...first,morphemes:Array.from({length:30},(_,i)=>({segment_index:i,language:'Hebrew',part_of_speech:'noun',pos_code:'N'}))}}));
 await page.goto('/');const text=page.getByRole('region',{name:'Chapter text'});const bounds=await text.boundingBox();
 if(info.project.name==='desktop'){expect(bounds.width).toBeLessThanOrEqual(704);expect(Math.abs(bounds.x+bounds.width/2-640)).toBeLessThan(2);}
 await page.getByRole('button',{name:/Word:/}).click();const panel=page.getByRole('complementary',{name:'Word analysis panel'});await expect(page.getByRole('complementary',{name:'Word morphology'})).toBeVisible();
 const textBefore=await text.evaluate(el=>el.scrollTop);await panel.evaluate(el=>el.scrollTop=el.scrollHeight);await expect.poll(()=>panel.evaluate(el=>el.scrollTop)).toBeGreaterThan(0);expect(await text.evaluate(el=>el.scrollTop)).toBe(textBefore);expect(await page.evaluate(()=>window.scrollY)).toBe(0);
 await expect(panel.getByText('Noun',{exact:true}).last()).toBeInViewport();await expect(panel.getByRole('button',{name:'Close morphology panel'})).toBeInViewport();await panel.getByRole('button',{name:'Close morphology panel'}).click();await expect(panel).toHaveCount(0);
});

test('compare passages independently, restore URL state and identify word origin',async({page},info)=>{
 await setup(page);await page.goto('/');
 await page.getByRole('button',{name:'Compare passages',exact:true}).click();
 const one=page.getByRole('region',{name:'Passage 1',exact:true,includeHidden:true});const two=page.getByRole('region',{name:'Passage 2',exact:true,includeHidden:true});
 if(info.project.name==='mobile')await page.getByRole('button',{name:/Show passage 2/}).click();
 await two.getByRole('button',{name:/Navigate:/}).click();await two.getByRole('button',{name:/Exodus —/}).click();await two.getByRole('button',{name:'Chapter 1 of Exodus',exact:true}).click();
 await expect(page).toHaveURL(/compareBook=Exod/);await expect(two.getByRole('button',{name:/Word: שֵׁמוֹת/})).toBeVisible();
 await page.route('**/api/bible/words/2/morphology',r=>r.fulfill({json:{...second,morphemes:[]}}));
 await two.getByRole('button',{name:/Word: שֵׁמוֹת/}).click();await expect(page.getByText('Passage 2 · Exodus 1:1',{exact:true})).toBeVisible();
 await expect(page.getByLabel('Hebrew word: שֵׁמוֹת',{exact:true})).toBeVisible();
 if(info.project.name==='mobile')await page.getByRole('button',{name:/Show passage 1/}).click();
 await expect(one.getByRole('button',{name:/Word: בְּרֵאשִׁית/})).toBeVisible();
 await one.getByRole('button',{name:/Word: בְּרֵאשִׁית/}).click();await expect(page.getByText('Passage 1 · Genesis 1:1',{exact:true})).toBeVisible();
 expect(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth)).toBe(false);
 await page.reload();await expect(one.getByRole('button',{name:/Word: בְּרֵאשִׁית/})).toBeVisible();
 if(info.project.name==='mobile')await page.getByRole('button',{name:/Show passage 2/}).click();
 await expect(two.getByRole('button',{name:/Word: שֵׁמוֹת/})).toBeVisible();
 await page.getByRole('button',{name:'Close comparison',exact:true}).click();await expect(page).not.toHaveURL(/compareBook/);await expect(two).toHaveCount(0);
 await page.goBack();if(info.project.name==='mobile')await page.getByRole('button',{name:/Show passage 2/}).click();await expect(two.getByRole('button',{name:/Word: שֵׁמוֹת/})).toBeVisible();
});

test('comparison preserves independent scroll and isolates identical-word selection',async({page},info)=>{
 await setup(page);await page.route('**/api/bible/books/Gen/chapters/1/verses',r=>r.fulfill({json:{data:Array.from({length:100},(_,i)=>({id:i+1,verse_num:i+1,book_id:1,chapter_num:1,words:[{...first,id:i+1}]})),total:100}}));
 await page.goto('/?book=Gen&chapter=1&compareBook=Gen&compareChapter=1');
 const one=page.getByRole('region',{name:'Passage 1',exact:true,includeHidden:true}),two=page.getByRole('region',{name:'Passage 2',exact:true,includeHidden:true});
 const firstText=one.getByRole('region',{name:'Passage 1 text',includeHidden:true}),secondText=two.getByRole('region',{name:'Passage 2 text',includeHidden:true});
 await one.getByRole('button',{name:/Word:/}).first().click();await expect(page.getByText('Passage 1 · Genesis 1:1',{exact:true})).toBeVisible();
 await expect(one.getByRole('button',{name:/Word:/}).first()).toHaveAttribute('aria-pressed','true');
 if(info.project.name==='mobile')await page.getByRole('button',{name:/^Show passage 2:/}).click();
 await two.getByRole('button',{name:/Word:/}).first().click();await expect(page.getByText('Passage 2 · Genesis 1:1',{exact:true})).toBeVisible();
 await expect(one.locator('.word-token').first()).toHaveAttribute('aria-pressed','false');
 await page.getByRole('button',{name:'Close morphology panel'}).click();
 await secondText.evaluate(el=>el.scrollTop=250);await expect.poll(()=>secondText.evaluate(el=>el.scrollTop)).toBe(250);
 if(info.project.name==='mobile')await page.getByRole('button',{name:/^Show passage 1:/}).click();
 expect(await firstText.evaluate(el=>el.scrollTop)).toBe(0);await firstText.evaluate(el=>el.scrollTop=500);
 if(info.project.name==='mobile')await page.getByRole('button',{name:/^Show passage 2:/}).click();
 await expect.poll(()=>secondText.evaluate(el=>el.scrollTop)).toBe(250);
 await two.getByRole('button',{name:/Navigate:/}).click();const dialog=two.getByRole('dialog');const bounds=await dialog.boundingBox();expect(bounds.x).toBeGreaterThanOrEqual(0);expect(bounds.x+bounds.width).toBeLessThanOrEqual(await page.evaluate(()=>innerWidth));
 await two.getByRole('button',{name:/Exodus —/}).click();await two.getByRole('button',{name:'Chapter 1 of Exodus'}).click();await expect(two.getByRole('button',{name:/Word: שֵׁמוֹת/})).toBeVisible();
 await expect.poll(()=>secondText.evaluate(el=>el.scrollTop)).toBe(0);
 if(info.project.name==='mobile')await page.getByRole('button',{name:/^Show passage 1:/}).click();
 await expect.poll(()=>firstText.evaluate(el=>el.scrollTop)).toBe(500);expect(await page.evaluate(()=>scrollY)).toBe(0);
});

test('comparison chapter failure and delayed response leave the other passage usable',async({page})=>{
 await setup(page);let fail=true,release;
 await page.route('**/api/bible/books/Exod/chapters/1/verses',r=>fail?r.fulfill({status:503,json:{error:'unavailable'}}):r.fallback());
 await page.goto('/?book=Gen&chapter=1&compareBook=Exod&compareChapter=1');
 const one=page.getByRole('region',{name:'Passage 1',exact:true,includeHidden:true}),two=page.getByRole('region',{name:'Passage 2',exact:true,includeHidden:true});
 const switcher=page.getByRole('button',{name:/^Show passage 2:/});if(await switcher.isVisible())await switcher.click();
 await expect(two.getByRole('button',{name:'Retry chapter'})).toBeVisible();fail=false;await two.getByRole('button',{name:'Retry chapter'}).click();await expect(two.getByRole('button',{name:/Word: שֵׁמוֹת/})).toBeVisible();
 await page.route('**/api/bible/words/2/morphology',async r=>{await new Promise(resolve=>release=resolve);await r.fulfill({json:{...second,morphemes:[]}});});
 await two.getByRole('button',{name:/Word: שֵׁמוֹת/}).click();await expect.poll(()=>Boolean(release)).toBe(true);
 await page.getByRole('button',{name:'Close comparison',exact:true}).click();
 await one.getByRole('button',{name:/Word: בְּרֵאשִׁית/}).click();await expect(page.getByLabel('Hebrew word: בְּרֵאשִׁית',{exact:true})).toBeVisible();
 const late=page.waitForResponse('**/api/bible/words/2/morphology');release();await (await late).finished();await expect(page.getByLabel('Hebrew word: שֵׁמוֹת',{exact:true})).toHaveCount(0);
});

test('comparison bounds shared chapter numbers and keeps analysis with the visible mobile passage',async({page})=>{
 await setup(page);await page.goto('/?book=Gen&chapter=9007199254740991&compareBook=Exod&compareChapter=-1');
 const one=page.getByRole('region',{name:'Passage 1',exact:true});
 await expect(one.getByRole('button',{name:/Navigate: Genesis, chapter 1/})).toBeVisible();
 await page.getByRole('button',{name:'Close comparison',exact:true}).click();
 await one.getByRole('button',{name:/Word:/}).click();await expect(page.getByRole('complementary',{name:'Word morphology'})).toBeVisible();
 await page.getByRole('button',{name:'Compare passages',exact:true}).click();await expect(page.getByRole('complementary',{name:'Word morphology'})).toHaveCount(0);
 await page.setViewportSize({width:1280,height:900});await one.getByRole('button',{name:/Word:/}).click();
 await page.setViewportSize({width:390,height:844});await expect(one).toBeVisible();await expect(page.getByText('Passage 1 · Genesis 1:1',{exact:true})).toBeVisible();
 const switcher=page.getByRole('button',{name:'Show passage 2: Genesis 1'});await expect(switcher).toHaveAttribute('aria-controls','passage-2');await switcher.focus();await page.keyboard.press('Enter');await expect(one).toHaveCount(0);await expect(page.getByRole('complementary',{name:'Word morphology'})).toHaveCount(0);
});

test('comparison isolates a late chapter and supports keyboard reading at tablet width',async({page})=>{
 await setup(page);await page.setViewportSize({width:1100,height:768});let release;
 await page.route('**/api/bible/books/Exod/chapters/1/verses',async r=>{await new Promise(resolve=>release=resolve);await r.fulfill({json:verses(ex,second)});});
 await page.route('**/api/bible/books/Gen/chapters/1/verses',r=>r.fulfill({json:{data:Array.from({length:100},(_,i)=>({id:i+1,verse_num:i+1,book_id:1,chapter_num:1,words:[{...first,id:i+1}]})),total:100}}));
 await page.goto('/?book=Gen&chapter=1&compareBook=Exod&compareChapter=1');await expect.poll(()=>Boolean(release)).toBe(true);
 const one=page.getByRole('region',{name:'Passage 1',exact:true}),two=page.getByRole('region',{name:'Passage 2',exact:true});const text=one.getByRole('region',{name:'Passage 1 text'});
 await text.focus();await page.keyboard.press('PageDown');await expect.poll(()=>text.evaluate(el=>el.scrollTop)).toBeGreaterThan(0);
 await two.getByRole('button',{name:/Navigate:/}).focus();await page.keyboard.press('Enter');await two.getByRole('button',{name:/Genesis —/}).focus();await page.keyboard.press('Enter');await two.getByRole('button',{name:'Chapter 1 of Genesis',exact:true}).focus();await page.keyboard.press('Enter');
 await expect(two.getByRole('button',{name:/Word: בְּרֵאשִׁית/}).first()).toBeVisible();
 const late=page.waitForResponse('**/api/bible/books/Exod/chapters/1/verses');release();await (await late).finished();await page.evaluate(()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))));
 await expect(two.getByRole('button',{name:/Word: שֵׁמוֹת/})).toHaveCount(0);await expect.poll(()=>text.evaluate(el=>el.scrollTop)).toBeGreaterThan(0);
 await two.getByRole('button',{name:/Word:/}).first().focus();await page.keyboard.press('Enter');await expect(page.getByText('Passage 2 · Genesis 1:1',{exact:true})).toBeVisible();
 const textBounds=await text.boundingBox(),panelBounds=await page.getByRole('complementary',{name:'Word analysis panel'}).boundingBox();expect(textBounds.y+textBounds.height).toBeLessThanOrEqual(panelBounds.y);expect(await page.evaluate(()=>scrollY)).toBe(0);
});

test('focus mode preserves the passage, restores analysis and handles Escape in order',async({page})=>{
 await setup(page);await page.route('**/api/bible/books/Gen/chapters/1/verses',r=>r.fulfill({json:{data:Array.from({length:100},(_,i)=>({id:i+1,verse_num:i+1,book_id:1,chapter_num:1,words:[{...first,id:i+1}]})),total:100}}));
 await page.goto('/');await page.getByRole('button',{name:/Word:/}).first().click();await expect(page.getByRole('complementary',{name:'Word morphology'})).toBeVisible();
 const text=page.getByRole('region',{name:'Chapter text'});await text.evaluate(el=>el.scrollTop=300);
 await page.getByRole('button',{name:'Enter focus mode',exact:true}).click();await expect(page.getByRole('banner')).toHaveCount(0);await expect(page.getByRole('complementary',{name:'Word analysis panel'})).toHaveCount(0);await expect.poll(()=>text.evaluate(el=>el.scrollTop)).toBe(300);
 await page.getByRole('button',{name:/Navigate:/}).click();await page.keyboard.press('Escape');await expect(page.getByRole('dialog',{name:'Book and chapter selector'})).toHaveCount(0);await expect(page.getByRole('button',{name:'Exit focus mode',exact:true})).toBeVisible();
 await page.keyboard.press('Escape');await expect(page.getByRole('banner')).toBeVisible();await expect(page.getByRole('complementary',{name:'Word morphology'})).toBeVisible();await expect(page.getByRole('button',{name:'Enter focus mode',exact:true})).toBeFocused();await expect.poll(()=>text.evaluate(el=>el.scrollTop)).toBe(300);
 await page.getByRole('button',{name:'Enter focus mode',exact:true}).click();await text.evaluate(el=>el.scrollTop=0);await page.getByRole('button',{name:/Word:/}).first().click();await expect(page.getByRole('banner')).toBeVisible();await expect(page.getByRole('complementary',{name:'Word morphology'})).toBeVisible();
});

test('previous and next chapters cross book boundaries and preserve comparison state',async({page},info)=>{
 await setup(page);await page.goto('/?book=Gen&chapter=1&compareBook=Exod&compareChapter=1');
 const one=page.getByRole('region',{name:'Passage 1',exact:true}),two=page.getByRole('region',{name:'Passage 2',exact:true});
 await expect(one.getByRole('button',{name:'Previous chapter',exact:true})).toBeDisabled();
 await one.getByRole('button',{name:'Next chapter',exact:true}).click();await expect(page).toHaveURL(/book=Gen&chapter=2&compareBook=Exod&compareChapter=1/);
 await one.getByRole('button',{name:'Next chapter',exact:true}).click();await expect(page).toHaveURL(/book=Exod&chapter=1&compareBook=Exod&compareChapter=1/);
 await one.getByRole('button',{name:'Previous chapter',exact:true}).click();await expect(page).toHaveURL(/book=Gen&chapter=2&compareBook=Exod&compareChapter=1/);
 await page.getByRole('button',{name:'Enter focus mode',exact:true}).click();
 if(info.project.name==='mobile')await page.getByRole('button',{name:/Show passage 2:/}).click();
 await two.getByRole('button',{name:'Next chapter',exact:true}).click();await expect(page).toHaveURL(/book=Gen&chapter=2&compareBook=Exod&compareChapter=2/);await expect(two.getByRole('button',{name:'Next chapter',exact:true})).toBeDisabled();await expect(page.getByRole('button',{name:'Exit focus mode',exact:true})).toBeVisible();
 await page.goBack();await expect(page).toHaveURL(/compareChapter=1/);await expect(two.getByRole('button',{name:'Next chapter',exact:true})).toBeEnabled();
});

test('chapter navigation retries metadata and follows actual sorted chapters',async({page})=>{
 await setup(page);let failCurrent=true,failNeighbor=true;
 await page.route('**/api/bible/books/Gen',r=>failCurrent?r.fulfill({status:503,json:{error:'unavailable'}}):r.fulfill({json:{...gen,chapters:[{id:3,chapter_num:3},{id:1,chapter_num:1}]}}));
 await page.route('**/api/bible/books/Exod',r=>failNeighbor?r.fulfill({status:503,json:{error:'unavailable'}}):r.fulfill({json:{...ex,chapters:[{id:2,chapter_num:2},{id:1,chapter_num:1}]}}));
 await page.goto('/');const next=page.getByRole('button',{name:'Next chapter',exact:true});await expect(next).toBeDisabled();await expect(page.getByRole('button',{name:/Word:/})).toBeVisible();
 failCurrent=false;await page.getByRole('button',{name:'Retry navigation',exact:true}).click();await expect(next).toBeEnabled();await next.focus();await page.keyboard.press('Enter');await expect(page).toHaveURL(/chapter=3/);
 await expect(next).toBeDisabled();await expect(page.getByRole('button',{name:'Previous chapter',exact:true})).toBeEnabled();failNeighbor=false;await page.getByRole('button',{name:'Retry navigation',exact:true}).click();await next.click();await expect(page).toHaveURL(/book=Exod&chapter=1/);
 await page.getByRole('button',{name:'Previous chapter',exact:true}).click();await expect(page).toHaveURL(/book=Gen&chapter=3/);
});

test('late navigation metadata cannot restore targets from the old book',async({page})=>{
 await setup(page);let release;
 await page.route('**/api/bible/books/Exod',async r=>{await new Promise(resolve=>release=resolve);await r.fulfill({json:{...ex,chapters:[{id:1,chapter_num:1},{id:2,chapter_num:2}]}});});
 await page.goto('/?book=Exod&chapter=1');await expect.poll(()=>Boolean(release)).toBe(true);await expect(page.getByRole('button',{name:'Next chapter',exact:true})).toBeDisabled();
 // A previously visited reference is another real way to change passage while metadata is pending.
 await page.evaluate(()=>{history.pushState({},'', '?book=Gen&chapter=1');dispatchEvent(new PopStateEvent('popstate'));});
 await expect(page.getByRole('button',{name:/Navigate: Genesis/})).toBeVisible();const late=page.waitForResponse('**/api/bible/books/Exod');release();await (await late).finished();
 await expect(page.getByRole('button',{name:'Previous chapter',exact:true})).toBeDisabled();await page.getByRole('button',{name:'Next chapter',exact:true}).click();await expect(page).toHaveURL(/book=Gen&chapter=2/);
});

test('focus roundtrip preserves the final reading position and respects new scrolling',async({page})=>{
 await setup(page);await page.route('**/api/bible/books/Gen/chapters/1/verses',r=>r.fulfill({json:{data:Array.from({length:30},(_,i)=>({id:i+1,verse_num:i+1,book_id:1,chapter_num:1,words:Array.from({length:20},(_,j)=>({...first,id:i*20+j+1,position:j+1}))})),total:30}}));
 await page.goto('/');await page.getByRole('button',{name:/Word:/}).first().click();await expect(page.getByRole('complementary',{name:'Word morphology'})).toBeVisible();
 const text=page.getByRole('region',{name:'Chapter text'});await text.evaluate(el=>el.scrollTop=el.scrollHeight);const before=await text.evaluate(el=>el.scrollTop);
 await page.getByRole('button',{name:'Enter focus mode',exact:true}).click();await page.getByRole('button',{name:'Exit focus mode',exact:true}).click();await expect.poll(()=>text.evaluate(el=>el.scrollTop)).toBeCloseTo(before,0);
 await page.getByRole('button',{name:'Enter focus mode',exact:true}).click();await text.evaluate(el=>el.scrollTop=0);await page.keyboard.press('Escape');await expect.poll(()=>text.evaluate(el=>el.scrollTop)).toBe(0);
});

test('selector closes when keyboard focus leaves in focus mode',async({page})=>{
 await setup(page);await page.goto('/');await page.getByRole('button',{name:'Enter focus mode',exact:true}).click();
 const selector=page.getByRole('button',{name:/Navigate:/});await selector.click();await page.keyboard.press('Shift+Tab');await expect(page.getByRole('dialog',{name:'Book and chapter selector'})).toHaveCount(0);
 await expect(page.getByRole('button',{name:'Exit focus mode',exact:true})).toBeVisible();await page.keyboard.press('Escape');await expect(page.getByRole('banner')).toBeVisible();
});
