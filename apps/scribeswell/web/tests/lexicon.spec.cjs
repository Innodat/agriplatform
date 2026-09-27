const {test,expect}=require('@playwright/test');
const books=[{id:1,osis_id:'Gen',name_en:'Genesis',name_he:'א',testament:'old',division:'torah',book_order:1},{id:2,osis_id:'Exod',name_en:'Exodus',name_he:'ב',testament:'old',division:'torah',book_order:2}];
const words=[{id:1,position:1,surface_he:'מֶלֶךְ',display_he:'מֶלֶךְ',lemma_strong:'4428',lexical_id:'4428',match_key:'root:haj',morph_code:'HNcmsa'},{id:2,position:2,surface_he:'מַמְלָכָה',display_he:'מַמְלָכָה',lemma_strong:'c/4467',lexical_id:'4467',match_key:'root:haj',morph_code:'HC/Ncfsa'},{id:3,position:3,surface_he:'מָלַךְ',display_he:'מָלַךְ',lemma_strong:'4427 b',lexical_id:'4427 b',match_key:'root:hah',morph_code:'HVqp3ms'}];
async function setup(page){
 await page.route('http://127.0.0.1:8001/**',r=>r.fulfill({json:[]}));
 await page.route('**/api/bible/**',r=>{
  const u=new URL(r.request().url()),p=u.pathname;
  if(p.endsWith('/books'))return r.fulfill({json:{data:books,total:2}});
  if(p.includes('/lexicon/'))return r.fulfill({json:{status:'available',lexical_id:'4428',lemma:'מֶלֶךְ',definition:'king',transliteration:'melekh',root:{id:'haj',text:'מלך'},pronunciation:'meh-lek',bdb:[{kind:'sense',text:'1',children:[{kind:'text',text:'king '},{kind:'reference',text:'Ex 1:20',book:'Exod',chapter:1,verse:20}]}]}});
  if(p.includes('/occurrences/')){const offset=Number(u.searchParams.get('offset'));return r.fulfill({json:{data:[{id:100+offset,position:1,surface_he:'מלך',display_he:'מלך',book:'Exod',book_name:'Exodus',chapter:1,verse:20}],total:51,verse_total:40,offset,limit:25}});}
  if(p.includes('/words/')){const w=words.find(w=>p.includes(`/words/${w.id}/`));return r.fulfill({json:{...w,morphemes:[{segment_index:0,language:'Hebrew',part_of_speech:'noun',pos_code:'N'}]}});}
  if(p.endsWith('/verses'))return r.fulfill({json:{data:Array.from({length:30},(_,i)=>({id:i+1,verse_num:i+1,book_id:p.includes('Exod')?2:1,chapter_num:1,words:i===0?words:[{...words[0],id:10+i}]})),total:30}});
  return r.fulfill({json:{...books[p.includes('Exod')?1:0],chapters:[{id:1,chapter_num:1},{id:2,chapter_num:2}]}});
 });
 await page.goto('/');
}

test('root highlights keep homonyms distinct in both chapters; dwell cancels and restores pinned state',async({page})=>{
 await setup(page);await page.getByRole('button',{name:'Compare passages',exact:true}).click();
 await page.setViewportSize({width:1280,height:900});
 const one=page.getByRole('region',{name:'Passage 1',exact:true}),two=page.getByRole('region',{name:'Passage 2',exact:true});
 await one.locator('.word-token').first().click();
 await expect(one.locator('.selected')).toHaveCount(1);await expect(two.locator('.related')).toHaveCount(31);
 await expect(one.locator('.word-token').nth(2)).not.toHaveClass(/related/);
 await one.locator('.word-token').nth(2).hover();await page.waitForTimeout(600);await expect(two.locator('.word-token').first()).toHaveClass(/related/);
 await page.getByRole('tab',{name:'Word',exact:true}).hover();await page.waitForTimeout(550);await expect(two.locator('.word-token').first()).toHaveClass(/related/);
 await one.locator('.word-token').nth(2).focus();await page.waitForTimeout(1100);await expect(two.locator('.word-token').nth(2)).toHaveClass(/related/);await expect(one.locator('.selected')).toHaveCount(1);
 await page.getByRole('tab',{name:'Word',exact:true}).focus();await expect(two.locator('.word-token').first()).toHaveClass(/related/);
 await page.getByRole('button',{name:'Enter focus mode'}).click();await one.locator('.word-token').nth(2).hover();await page.waitForTimeout(1100);await expect(page.getByRole('button',{name:'Exit focus mode'})).toBeVisible();await expect(page.getByRole('complementary',{name:'Word analysis panel'})).toHaveCount(0);
 await one.getByRole('button',{name:'Next chapter',exact:true}).click();await page.waitForTimeout(1100);await expect(two.locator('.related')).toHaveCount(0);
});

test('occurrence pages survive tabs, filter resets, errors retry and new words clear old results',async({page})=>{
 await setup(page);await page.locator('.word-token').first().click();await page.getByRole('tab',{name:'Occurrences'}).click();await expect(page.getByText('51 word occurrences in 40 verses')).toBeVisible();
 await page.getByRole('button',{name:'Next results'}).click();await expect(page.getByRole('button',{name:'Previous results'})).toBeEnabled();
 await page.getByRole('tab',{name:'Word',exact:true}).click();await page.getByRole('tab',{name:'Occurrences'}).click();await expect(page.getByRole('button',{name:'Previous results'})).toBeEnabled();
 await page.getByLabel('Filter occurrences by book').selectOption('Gen');await expect(page.getByRole('button',{name:'Previous results'})).toBeDisabled();
 let fail=true;await page.route('**/api/bible/occurrences/4467?**',r=>fail?r.fulfill({status:503,json:{error:'unavailable'}}):r.fulfill({json:{data:[],total:0,verse_total:0,offset:0,limit:25}}));
 await page.locator('.word-token').nth(1).click();await expect(page.getByText('51 word occurrences in 40 verses')).toHaveCount(0);await page.getByRole('tab',{name:'Occurrences'}).click();await expect(page.getByRole('button',{name:'Retry occurrences'})).toBeVisible();fail=false;await page.getByRole('button',{name:'Retry occurrences'}).click();await expect(page.getByText('No matching occurrences.')).toBeVisible();
});

test('BDB safe references preview and open at verse without changing the other passage',async({page})=>{
 await setup(page);await page.locator('.word-token').first().click();await page.getByText('BDB outline',{exact:true}).click();await page.getByRole('button',{name:'Ex 1:20',exact:true}).click();const preview=page.getByRole('region',{name:'Scripture preview'});await expect(preview.getByText('מלך',{exact:true})).toHaveCount(0);await expect(preview.locator('[lang=he]')).toBeVisible();
 await preview.getByRole('button',{name:'Open in comparison',exact:true}).click();await expect(page).toHaveURL(/compareBook=Exod/);await expect(page).toHaveURL(/compareVerse=20/);
 const two=page.getByRole('region',{name:'Passage 2',exact:true});await expect(two.locator('[data-verse="20"]')).toBeInViewport();
 await page.setViewportSize({width:1280,height:900});await expect(page.getByRole('region',{name:'Passage 1',exact:true}).getByRole('button',{name:/Navigate: Genesis, chapter 1/})).toBeVisible();
 await page.goBack();await expect(page.getByRole('button',{name:'Compare passages',exact:true})).toBeVisible();
});

test('missing dictionary and failures keep morphology usable with retry; touch pins without hover',async({page})=>{
 await setup(page);let missing=false;await page.route('**/api/bible/lexicon/**',r=>missing?r.fulfill({json:{status:'missing',lexical_id:'4428'}}):r.fulfill({status:503,json:{error:'unavailable'}}));
 await page.locator('.word-token').first().dispatchEvent('pointerenter',{pointerType:'touch'});await page.waitForTimeout(1100);await expect(page.locator('.related')).toHaveCount(0);
 await page.locator('.word-token').first().click();await expect(page.getByText('Noun',{exact:true})).toBeVisible();await expect(page.getByRole('button',{name:'Retry dictionary'})).toBeVisible();missing=true;await page.getByRole('button',{name:'Retry dictionary'}).click();await expect(page.getByText('No dictionary entry for this word.')).toBeVisible();
});

test('late occurrence results cannot cross selections and pending preview cancels on focus changes',async({page})=>{
 await setup(page);let release;await page.route('**/api/bible/occurrences/4428?**',async r=>{await new Promise(resolve=>release=resolve);await r.fulfill({json:{data:[],total:999,verse_total:999,offset:0,limit:25}});});
 await page.locator('.word-token').first().click();await page.getByRole('tab',{name:'Occurrences'}).click();await expect.poll(()=>Boolean(release)).toBe(true);
 await page.locator('.word-token').nth(1).click();await page.getByRole('tab',{name:'Occurrences'}).click();await expect(page.getByText('51 word occurrences in 40 verses')).toBeVisible();const late=page.waitForResponse('**/api/bible/occurrences/4428?**');release();await (await late).finished();await expect(page.getByText('999 word occurrences in 999 verses')).toHaveCount(0);
 await page.locator('.word-token').nth(2).hover();await page.getByRole('button',{name:'Enter focus mode'}).click();await page.waitForTimeout(1100);await expect(page.locator('.word-token').nth(2)).not.toHaveClass(/related/);await expect(page.getByRole('button',{name:'Exit focus mode'})).toBeVisible();
});

test('current passage follows selected pane and ordinary mobile switches preserve targeted scroll',async({page})=>{
 await setup(page);await page.getByRole('button',{name:'Compare passages',exact:true}).click();
 const two=page.getByRole('region',{name:'Passage 2',exact:true});await two.locator('.word-token').first().click();await page.getByRole('tab',{name:'Occurrences'}).click();await page.getByRole('button',{name:'Open in current passage',exact:true}).click();await expect(page).toHaveURL(/compareBook=Exod/);expect(new URL(page.url()).searchParams.get('book')).not.toBe('Exod');await expect(two.locator('[data-verse="20"]')).toBeInViewport();
 await page.setViewportSize({width:390,height:844});const text=two.locator('[data-reader-scroll]');await text.evaluate(el=>el.scrollTop=100);await page.getByRole('button',{name:/Show passage 1/}).click();await page.getByRole('button',{name:/Show passage 2/}).click();await expect.poll(()=>text.evaluate(el=>el.scrollTop)).toBe(100);
});

test('explicitly reopening the same verse seeks again and invalid verse URLs are ignored',async({page})=>{
 await setup(page);await page.setViewportSize({width:1280,height:900});await page.locator('.word-token').first().click();await page.getByRole('tab',{name:'Occurrences'}).click();const open=page.getByRole('button',{name:'Open in comparison',exact:true});await open.click();const two=page.getByRole('region',{name:'Passage 2',exact:true});await expect(two.locator('[data-verse="20"]')).toBeInViewport();await two.locator('[data-reader-scroll]').evaluate(el=>el.scrollTop=0);await open.click();await expect(two.locator('[data-verse="20"]')).toBeInViewport();
 await page.goto('/?verse=999999');await expect(page.locator('[data-verse="1"]')).toBeInViewport();await expect.poll(()=>page.locator('[data-reader-scroll]').evaluate(el=>el.scrollTop)).toBe(0);
});

test('review regression: desktop reload and responsive reveal apply pending verse targets once',async({page})=>{
 await setup(page);await page.setViewportSize({width:1280,height:900});
 await page.goto('/?compareBook=Exod&compareChapter=1&compareVerse=20');
 const two=page.getByRole('region',{name:'Passage 2',exact:true});await expect(two.locator('[data-verse="20"]')).toBeInViewport();
 await page.reload();await expect(two.locator('[data-verse="20"]')).toBeInViewport();
 await page.setViewportSize({width:390,height:844});await page.goto('/?compareBook=Exod&compareChapter=1&compareVerse=20');
 await expect(page.getByRole('region',{name:'Passage 1',exact:true})).toBeVisible();
 await page.setViewportSize({width:1280,height:900});await expect(two.locator('[data-verse="20"]')).toBeInViewport();
 await two.locator('[data-reader-scroll]').evaluate(el=>el.scrollTop=100);
 await page.setViewportSize({width:390,height:844});await page.setViewportSize({width:1280,height:900});
 await expect.poll(()=>two.locator('[data-reader-scroll]').evaluate(el=>el.scrollTop)).toBe(100);
 await page.getByRole('button',{name:'Close comparison',exact:true}).click();expect(new URL(page.url()).searchParams.has('compareVerse')).toBe(false);
});

test('review regression: explicit null and ambiguous legacy lemmas never choose an identity',async({page})=>{
 await setup(page);const lookups=new Set();
 page.on('request',request=>{if(request.url().includes('/lexicon/'))lookups.add(decodeURIComponent(new URL(request.url()).pathname.split('/').pop()));});
 await page.route('**/api/bible/words/*/morphology',r=>{
  const id=Number(r.request().url().match(/words\/(\d+)/)[1]);
  const w={...words[id-1],lemma_strong:id===2?'4428/4467':id===3?'c/4428':'4428',morphemes:[]};
  if(id===1)w.lexical_id=null;else delete w.lexical_id;
  return r.fulfill({json:w});
 });
 await page.locator('.word-token').nth(0).click();await expect(page.getByText('No dictionary entry for this word.')).toBeVisible();
 await page.getByRole('tab',{name:'Occurrences'}).click();await expect(page.getByText('No lexical identity is available for lookup.')).toBeVisible();
 await page.locator('.word-token').nth(1).click();await expect(page.getByText('No dictionary entry for this word.')).toBeVisible();expect(lookups.size).toBe(0);
 await page.locator('.word-token').nth(2).click();await expect(page.getByText('Strong’s 4428',{exact:true})).toBeVisible();await expect.poll(()=>Array.from(lookups)).toEqual(['4428']);
});

test('review regression: actual BDB invalid Ezra reference remains text and Hebrew runs retain direction and font',async({page})=>{
 await setup(page);
 const fs=require('node:fs'),path=require('node:path');
 const entry=JSON.parse(fs.readFileSync(path.resolve(__dirname,'../../data/hebrew-lexicon/lexicon.json'),'utf8')).entries['3247'];
 await page.route('**/api/bible/lexicon/**',r=>r.fulfill({json:{status:'available',...entry}}));
 await page.locator('.word-token').first().click();await page.getByText('BDB outline',{exact:true}).click();
 const outline=page.locator('details').filter({has:page.getByText('BDB outline',{exact:true})});
 await expect(outline).toContainText('13:17');await expect(outline.getByRole('button',{name:/13:17/})).toHaveCount(0);
 const hebrew=outline.locator('bdi[lang="he"]').first();await expect(hebrew).toHaveAttribute('dir','rtl');await expect(hebrew).toHaveCSS('font-family',/Noto Serif Hebrew/);
});

test('review regression: unavailable reference previews cannot replace a working passage',async({page})=>{
 await setup(page);
 await page.route('**/api/bible/books/Exod/chapters/1/verses',r=>r.fulfill({json:{data:[{id:1,verse_num:1,book_id:2,chapter_num:1,words:[words[0]]}],total:1}}));
 await page.locator('.word-token').first().click();await page.getByText('BDB outline',{exact:true}).click();await page.getByRole('button',{name:'Ex 1:20',exact:true}).click();
 const preview=page.getByRole('region',{name:'Scripture preview'});await expect(preview.getByText('Verse not present in this collection.')).toBeVisible();
 await expect(preview.getByRole('button',{name:'Open in current passage',exact:true})).toBeDisabled();await expect(preview.getByRole('button',{name:'Open in comparison',exact:true})).toBeDisabled();
 await expect(page.getByRole('region',{name:'Passage 1',exact:true}).getByRole('button',{name:/Navigate: Genesis, chapter 1/})).toBeVisible();
});
