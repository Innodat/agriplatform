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
 const outline=page.getByRole('region',{name:'BDB outline',exact:true});
 if(await outline.getByRole('button',{name:'Show more',exact:true}).count())await outline.getByRole('button',{name:'Show more',exact:true}).click();
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

test('compact grammar and linked dictionary preserve selected passage and restore entry history',async({page})=>{
 await setup(page);
 await page.route('**/api/bible/lexicon/**',r=>{const id=decodeURIComponent(new URL(r.request().url()).pathname.split('/').pop());return r.fulfill({json:{status:'available',lexical_id:id,lemma:id==='4428'?'מֶלֶךְ':'אָב',definition:id==='4428'?'king':'father',root:{id:'root',text:'אב',lexical_id:id==='4428'?'1':'6'},bdb:[{kind:'text',text:'Definition '.repeat(150)},{kind:'dictionary_reference',text:'six',lexical_id:'6'}]}});});
 await page.locator('.word-token').first().click();
 await expect(page.getByRole('heading',{name:'מֶלֶךְ',exact:true})).toBeVisible();
 const url=page.url();await page.getByRole('button',{name:'Open dictionary entry 1'}).click();
 await expect(page.getByRole('heading',{name:'אָב',exact:true})).toBeVisible();await expect(page.getByLabel('Word morphology',{exact:true})).toHaveCount(0);
 expect(page.url()).toBe(url);await expect(page.locator('.selected')).toHaveCount(1);
 await page.getByRole('button',{name:'Open dictionary entry 6',exact:true}).click();
 await page.getByRole('button',{name:'Back to previous dictionary entry'}).click();await page.getByRole('button',{name:'Back to previous dictionary entry'}).click();
 await expect(page.getByRole('heading',{name:'מֶלֶךְ',exact:true})).toBeVisible();await expect(page.getByLabel('Word morphology',{exact:true})).toBeVisible();
});

test('actual aligned participle segments remain readable without source details',async({page})=>{
 await setup(page);
 await page.route('**/api/bible/words/*/morphology',r=>r.fulfill({json:{...words[0],surface_he:'בְּ/עֹשָׂ֑י/ו',display_he:'בְּעֹשָׂ֑יו',morph_code:'HR/Vqrmpc/Sp3ms',morphemes:[{segment_index:0,language:'hebrew',part_of_speech:'preposition',pos_code:'R'},{segment_index:1,language:'hebrew',part_of_speech:'verb',pos_code:'Vqrmpc',verb_stem:'qal',verb_aspect:'participle_active',gender:'masculine',number:'plural',state:'construct'},{segment_index:2,language:'hebrew',part_of_speech:'suffix',pos_code:'Sp3ms',person:'third',gender:'masculine',number:'singular'}]}}));
 await page.locator('.word-token').first().click();const grammar=page.getByLabel('Word morphology',{exact:true});
 await expect(grammar.getByText('עֹשָׂ֑י',{exact:true})).toBeVisible();await expect(grammar).toContainText('Qal active participle');await expect(grammar).toContainText('masculine · plural · construct');
 await expect(page.getByText('HR/Vqrmpc/Sp3ms',{exact:true})).toHaveCount(0);await expect(page.getByText('Source details',{exact:true})).toHaveCount(0);
});

test('dictionary Back restores pagination, expansions and inspector scroll; clipped links are absent',async({page})=>{
 await setup(page);
 await page.route('**/api/bible/lexicon/**',r=>{const id=decodeURIComponent(new URL(r.request().url()).pathname.split('/').pop());return r.fulfill({json:{status:'available',lexical_id:id,lemma:id==='4428'?'מֶלֶךְ':'אָב',definition:'meaning',strong_definition:'Full Strong definition',bdb:[{kind:'text',text:'Long definition '.repeat(100)},{kind:'dictionary_reference',text:'father',lexical_id:'1'}]}});});
 await page.locator('.word-token').first().click();await page.getByRole('tab',{name:'Occurrences'}).click();await page.getByLabel('Filter occurrences by book').selectOption('Gen');await page.getByRole('button',{name:'Next results'}).click();await page.getByRole('tab',{name:'Word',exact:true}).click();
 await expect(page.getByRole('button',{name:'Open dictionary entry 1'})).toHaveCount(0);
 await page.getByText('Strong’s definition and usage',{exact:true}).click();await page.getByRole('button',{name:'Show more',exact:true}).click();
 const panel=page.getByRole('complementary',{name:'Word analysis panel'}), link=page.getByRole('button',{name:'Open dictionary entry 1'});
 await link.scrollIntoViewIfNeeded();const position=await panel.evaluate(el=>el.scrollTop);const passage=page.locator('[data-reader-scroll]');const passagePosition=await passage.evaluate(el=>el.scrollTop);
 await link.click();await expect(page.getByRole('heading',{name:'אָב',exact:true})).toBeVisible();await page.getByRole('button',{name:'Back to previous dictionary entry'}).click();
 await expect(page.getByRole('button',{name:'Show less',exact:true})).toBeVisible();await expect(page.getByText('Full Strong definition',{exact:true})).toBeVisible();await expect(page.getByText('Source details',{exact:true})).toHaveCount(0);
 await expect.poll(()=>panel.evaluate(el=>el.scrollTop)).toBe(position);expect(await passage.evaluate(el=>el.scrollTop)).toBe(passagePosition);
 await page.getByRole('tab',{name:'Occurrences'}).click();await expect(page.getByLabel('Filter occurrences by book')).toHaveValue('Gen');await expect(page.getByRole('button',{name:'Previous results'})).toBeEnabled();
 await page.locator('.word-token').nth(1).click();await expect(page.getByRole('button',{name:'Back to previous dictionary entry'})).toHaveCount(0);
});

test('linked identity controls occurrences; late dictionaries and retry never restore token grammar',async({page})=>{
 await setup(page);let release,fail=true;
 await page.route('**/api/bible/lexicon/4428',r=>r.fulfill({json:{status:'available',lexical_id:'4428',lemma:'מֶלֶךְ',root:{id:'a',text:'אב',lexical_id:'1'}}}));
 await page.route('**/api/bible/lexicon/1',async r=>{if(fail)return r.fulfill({status:503,json:{error:'unavailable'}});await new Promise(resolve=>release=resolve);await r.fulfill({json:{status:'available',lexical_id:'1',lemma:'late father'}});});
 await page.route('**/api/bible/occurrences/1?**',r=>r.fulfill({json:{data:[],total:0,verse_total:0,offset:0,limit:25}}));
 await page.locator('.word-token').first().click();await page.getByRole('button',{name:'Open dictionary entry 1'}).click();await expect(page.getByRole('button',{name:'Retry dictionary'})).toBeVisible();await expect(page.getByLabel('Word morphology',{exact:true})).toHaveCount(0);
 await page.getByRole('tab',{name:'Occurrences'}).click();await expect(page.getByText('Exact lemma: 1',{exact:true})).toBeVisible();await expect(page.getByText('No matching occurrences.')).toBeVisible();await page.getByRole('tab',{name:'Word',exact:true}).click();
 fail=false;await page.getByRole('button',{name:'Retry dictionary'}).click();await expect.poll(()=>Boolean(release)).toBe(true);await page.getByRole('button',{name:'Back to previous dictionary entry'}).click();
 const response=page.waitForResponse('**/api/bible/lexicon/1');release();await (await response).finished();await expect(page.getByRole('heading',{name:'מֶלֶךְ',exact:true})).toBeVisible();await expect(page.getByText('late father')).toHaveCount(0);await expect(page.getByLabel('Word morphology',{exact:true})).toBeVisible();
});

test('unaligned source retains grammar without fabricated surface pieces',async({page})=>{
 await setup(page);await page.route('**/api/bible/words/*/morphology',r=>r.fulfill({json:{...words[0],surface_he:'בְּעֹשָׂ֑יו',morph_code:'HR/Vqrmpc/Sp3ms',morphemes:[{segment_index:0,language:'hebrew',part_of_speech:'preposition',pos_code:'R'},{segment_index:1,language:'hebrew',part_of_speech:'verb',pos_code:'Vqrmpc',verb_stem:'qal',verb_aspect:'participle_active',gender:'masculine',number:'plural',state:'construct'},{segment_index:2,language:'hebrew',part_of_speech:'suffix',pos_code:'Sp3ms',person:'third',gender:'masculine',number:'singular'}]}}));
 await page.locator('.word-token').first().click();const grammar=page.getByLabel('Word morphology',{exact:true});await expect(grammar).toContainText('Qal active participle');await expect(grammar.locator('[lang=he]')).toHaveCount(0);
 const width=await page.evaluate(()=>({client:document.documentElement.clientWidth,scroll:document.documentElement.scrollWidth}));expect(width.scroll).toBe(width.client);
});

test('selecting the same token in the other passage resets dictionary history',async({page})=>{
 await setup(page);await page.setViewportSize({width:1280,height:900});await page.getByRole('button',{name:'Compare passages',exact:true}).click();
 await page.route('**/api/bible/lexicon/**',r=>r.fulfill({json:{status:'available',lexical_id:'4428',lemma:'מֶלֶךְ',root:{id:'a',text:'אב',lexical_id:'1'}}}));
 const one=page.getByRole('region',{name:'Passage 1',exact:true}),two=page.getByRole('region',{name:'Passage 2',exact:true});
 await one.locator('.word-token').first().click();await page.getByRole('button',{name:'Open dictionary entry 1'}).click();await expect(page.getByRole('button',{name:'Back to previous dictionary entry'})).toBeVisible();
 await two.locator('.word-token').first().click();await expect(page.getByRole('button',{name:'Back to previous dictionary entry'})).toHaveCount(0);await expect(page.getByLabel('Word morphology',{exact:true})).toBeVisible();
});

test('keyboard dictionary Back restores originating link and failed-entry fallback focus',async({page})=>{
 await setup(page);let unavailable=false;
 await page.route('**/api/bible/lexicon/**',r=>{const id=decodeURIComponent(new URL(r.request().url()).pathname.split('/').pop());return r.fulfill({json:unavailable&&id==='4428'?{status:'unavailable',lexical_id:id}:{status:'available',lexical_id:id,lemma:id,root:{id:'a',text:'אב',lexical_id:id==='4428'?'1':'6'}}});});
 await page.locator('.word-token').first().click();const origin=page.getByRole('button',{name:'Open dictionary entry 1',exact:true});await origin.focus();await page.keyboard.press('Enter');
 await page.getByRole('button',{name:'Back to previous dictionary entry'}).focus();await page.keyboard.press('Enter');await expect(origin).toBeFocused();
 await page.keyboard.press('Enter');unavailable=true;await page.getByRole('button',{name:'Back to previous dictionary entry'}).click();await expect(page.getByRole('button',{name:'Retry dictionary'})).toBeVisible();await expect(page.getByLabel('Dictionary inspector',{exact:true})).toBeFocused();
 unavailable=false;await page.getByRole('button',{name:'Retry dictionary'}).click();await expect(origin).toBeFocused();
});

test('Back keeps saved scroll through failed reload and retry',async({page})=>{
 await setup(page);let fail=false;
 await page.route('**/api/bible/lexicon/**',r=>{const id=new URL(r.request().url()).pathname.split('/').pop();return r.fulfill({json:fail&&id==='4428'?{status:'unavailable',lexical_id:id}:{status:'available',lexical_id:id,lemma:id,bdb:[{kind:'text',text:'Long outline '.repeat(100)},{kind:'dictionary_reference',text:'father',lexical_id:'1'}]}});});
 await page.locator('.word-token').first().click();await page.getByRole('button',{name:'Show more',exact:true}).click();const origin=page.getByRole('button',{name:'Open dictionary entry 1',exact:true});await origin.scrollIntoViewIfNeeded();const panel=page.getByRole('complementary',{name:'Word analysis panel'}),saved=await panel.evaluate(el=>el.scrollTop);await origin.click();await expect(page.getByRole('heading',{name:'1',exact:true})).toBeVisible();
 fail=true;await page.getByRole('button',{name:'Back to previous dictionary entry'}).click();await expect(page.getByRole('button',{name:'Retry dictionary'})).toBeVisible();fail=false;await page.getByRole('button',{name:'Retry dictionary'}).click();await expect(origin).toBeFocused();await expect.poll(()=>panel.evaluate(el=>el.scrollTop)).toBe(saved);
});

test('delayed dictionary cannot move Occurrences scroll or focus its hidden heading',async({page})=>{
 await setup(page);let release;
 await page.route('**/api/bible/lexicon/4428',r=>r.fulfill({json:{status:'available',lexical_id:'4428',lemma:'king',root:{id:'a',text:'אב',lexical_id:'1'}}}));
 await page.route('**/api/bible/lexicon/1',async r=>{await new Promise(resolve=>release=resolve);await r.fulfill({json:{status:'available',lexical_id:'1',lemma:'father'}});});
 await page.route('**/api/bible/occurrences/1?**',r=>r.fulfill({json:{data:Array.from({length:25},(_,i)=>({id:i,position:1,surface_he:'אב',display_he:'אב',book:'Gen',book_name:'Genesis',chapter:1,verse:i+1})),total:25,verse_total:25,offset:0,limit:25}}));
 await page.locator('.word-token').first().click();await page.getByRole('button',{name:'Open dictionary entry 1'}).click();await expect(page.getByText('Dictionary entry · Strong’s 1',{exact:true})).toBeVisible();await expect.poll(()=>Boolean(release)).toBe(true);
 const tab=page.getByRole('tab',{name:'Occurrences',exact:true});await tab.click();await expect(page.getByText('25 word occurrences in 25 verses')).toBeVisible();const panel=page.getByRole('complementary',{name:'Word analysis panel'});await panel.evaluate(el=>el.scrollTop=180);await tab.focus();const saved=await panel.evaluate(el=>el.scrollTop);
 const response=page.waitForResponse('**/api/bible/lexicon/1');release();await (await response).finished();await expect(tab).toBeFocused();await expect.poll(()=>panel.evaluate(el=>el.scrollTop)).toBe(saved);await expect(page.getByRole('heading',{name:'father',includeHidden:true})).not.toBeFocused();
});

test('self references are text and missing-stem aspects remain readable in Aramaic segments',async({page})=>{
 await setup(page);
 await page.route('**/api/bible/lexicon/**',r=>r.fulfill({json:{status:'available',lexical_id:'4428',lemma:'king',root:{id:'a',text:'מלך',lexical_id:'4428'},bdb:[{kind:'dictionary_reference',text:'same entry',lexical_id:'4428'}]}}));
 await page.route('**/api/bible/words/*/morphology',r=>r.fulfill({json:{...words[0],surface_he:'מְהַחֲצֵ֣ף',morph_code:'AVxrmsa',morphemes:[{segment_index:0,language:'aramaic',part_of_speech:'verb',pos_code:'Vxrmsa',verb_aspect:'participle_active',gender:'masculine',number:'singular',state:'absolute'}]}}));
 await page.locator('.word-token').first().click();await expect(page.getByRole('button',{name:'Open dictionary entry 4428'})).toHaveCount(0);await expect(page.getByText('same entry',{exact:true})).toBeVisible();const grammar=page.getByLabel('Word morphology',{exact:true});await expect(grammar).toContainText('Active participle');await expect(grammar.locator('bdi')).toHaveAttribute('lang','arc');
});

test('BDB preview bounds real nested outline and keeps graphemes and link labels intact',async({page})=>{
 await setup(page);const fs=require('node:fs'),path=require('node:path');const entries=JSON.parse(fs.readFileSync(path.resolve(__dirname,'../../data/hebrew-lexicon/lexicon.json'),'utf8')).entries;
 await page.route('**/api/bible/lexicon/**',r=>r.fulfill({json:{status:'available',...entries['6213 a']}}));await page.locator('.word-token').first().click();const outline=page.getByRole('region',{name:'BDB outline',exact:true});await expect(outline.getByRole('button',{name:'Show more',exact:true})).toBeVisible();expect(await outline.locator('[data-bdb-content] .border-l').count()).toBeLessThanOrEqual(2);expect((await outline.locator('[data-bdb-content]').boundingBox()).height).toBeLessThan(360);
 await outline.getByRole('button',{name:'Show more',exact:true}).click();expect(await outline.locator('[data-bdb-content] .border-l').count()).toBeGreaterThan(2);
 const pointed='אְ'.repeat(239)+'בַּ';await page.route('**/api/bible/lexicon/**',r=>r.fulfill({json:{status:'available',lexical_id:'4467',lemma:'test',bdb:[{kind:'text',text:pointed},{kind:'dictionary_reference',text:'complete label',lexical_id:'6'},{kind:'text',text:' tail'}]}}));await page.locator('.word-token').nth(1).click();await expect(outline.locator('[data-bdb-content]')).toHaveText(pointed);await expect(page.getByRole('button',{name:'Open dictionary entry 6'})).toHaveCount(0);await outline.getByRole('button',{name:'Show more',exact:true}).click();await expect(page.getByRole('button',{name:'Open dictionary entry 6'})).toHaveText('complete label');
});

test('actual entry 10 Strong source link follows 9 and restores keyboard origin on Back',async({page})=>{
 await setup(page);const fs=require('node:fs'),path=require('node:path');const entries=JSON.parse(fs.readFileSync(path.resolve(__dirname,'../../data/hebrew-lexicon/lexicon.json'),'utf8')).entries;
 await page.route('**/api/bible/words/*/morphology',r=>r.fulfill({json:{...words[0],lexical_id:'10',morphemes:[]}}));await page.route('**/api/bible/lexicon/**',r=>{const id=decodeURIComponent(new URL(r.request().url()).pathname.split('/').pop());return r.fulfill({json:{status:'available',...entries[id]}});});
 await page.locator('.word-token').first().click();await page.getByText('Strong’s definition and usage',{exact:true}).click();const source=page.locator('details').filter({has:page.getByText('Strong’s definition and usage',{exact:true})});const link=source.getByRole('button',{name:'Open dictionary entry 9',exact:true});await link.focus();await page.keyboard.press('Enter');await expect(page.getByRole('heading',{name:entries['9'].lemma,exact:true})).toBeVisible();await page.getByRole('button',{name:'Back to previous dictionary entry'}).click();await expect(link).toBeFocused();await expect(page.getByRole('heading',{name:entries['10'].lemma,exact:true})).toBeVisible();
});


for(const expanded of [true,false])test('Back restores Strong details when navigation precedes the native toggle event: '+expanded,async({page})=>{
 await setup(page);const fs=require('node:fs'),path=require('node:path');const entries=JSON.parse(fs.readFileSync(path.resolve(__dirname,'../../data/hebrew-lexicon/lexicon.json'),'utf8')).entries;
 await page.route('**/api/bible/words/*/morphology',r=>r.fulfill({json:{...words[0],lexical_id:'10',morphemes:[]}}));
 await page.route('**/api/bible/lexicon/**',r=>{const id=decodeURIComponent(new URL(r.request().url()).pathname.split('/').pop());return r.fulfill({json:{status:'available',...entries[id]}});});
 await page.locator('.word-token').first().click();
 const source=page.locator('details').filter({has:page.getByText('Strong’s definition and usage',{exact:true})});
 await expect(source).toBeVisible();
 if(!expanded)await source.locator('summary').click();
 await source.evaluate((details,expanded)=>{details.querySelector('summary').click();const link=expanded?details.querySelector('[aria-label="Open dictionary entry 9"]'):document.querySelector('[data-dictionary-link="root"]');link.focus();link.click();},expanded);
 const target=expanded?'9':'6';
 await expect(page.getByRole('heading',{name:entries[target].lemma,exact:true})).toBeVisible();
 await page.getByRole('button',{name:'Back to previous dictionary entry'}).click();
 await expect(source).toHaveJSProperty('open',expanded);
 await expect(page.getByRole('button',{name:'Open dictionary entry '+target,exact:true})).toBeFocused();
});

test('dictionary controls show hand cursors and header closes either tab without duplicate actions',async({page})=>{
 await setup(page);
 await page.route('**/api/bible/occurrences/*?**',r=>r.fulfill({json:{data:Array.from({length:25},(_,i)=>({id:100+i,position:i+1,surface_he:'מלך',display_he:null,book:'Gen',book_name:'Genesis',chapter:1,verse:i+1})),total:51,verse_total:40,offset:0,limit:25}}));
 await page.route('**/api/bible/lexicon/**',r=>r.fulfill({json:{status:'available',lexical_id:'4428',lemma:'king',root:{id:'a',text:'father',lexical_id:'1'},bdb:[{kind:'dictionary_reference',text:'dictionary word',lexical_id:'6'}]}}));
 await page.locator('.word-token').first().click();
 for(const id of ['1','6']){const link=page.getByRole('button',{name:`Open dictionary entry ${id}`,exact:true});await link.hover();await expect(link).toHaveCSS('cursor','pointer');}
 await expect(page.getByText('Source details',{exact:true})).toHaveCount(0);
 for(const tab of ['Word','Occurrences']){
  await page.getByRole('tab',{name:tab,exact:true}).click();await expect(page.getByRole('button',{name:'Close word study',exact:true})).toHaveCount(0);
  const panel=page.getByRole('complementary',{name:'Word analysis panel'});
  if(tab==='Occurrences'){
   await expect(page.getByText('51 word occurrences in 40 verses',{exact:true})).toBeVisible();
   await panel.evaluate(el=>el.scrollTop=el.scrollHeight);
  }
  const close=page.getByRole('button',{name:'Close morphology panel',exact:true});
  await expect(close).toBeInViewport();await close.click();
  await expect(panel).toHaveCount(0);await expect(page.locator('.word-token.selected')).toHaveCount(0);
  if(tab==='Word')await page.locator('.word-token').first().click();
 }
});
