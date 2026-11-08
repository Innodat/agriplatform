const {test,expect}=require('@playwright/test');
const {files,sessionFor,context:documentContext}=require('./file-fixture.cjs');
test.beforeEach(async({page})=>files(page));
const org='11111111-1111-1111-1111-111111111111';
const actor='33333333-3333-3333-3333-333333333333';
const poem={id:'TEST-1',title:'Fixture poem',text:'Line one\nLine two',source_id:'SOURCE-1',creator:{name:'Fixture poet'},classification:{genre:'poem'},geography:{origin_locality:'Mombasa',dialect:'Kimvita'},quality:{text_status:'checked_transcription',complete_in_witness:true,reviewer_note:'Assistant check only'},source:{citation:'Fixture citation',locator:'page 1',url:'https://source.invalid/'}};
const completeCitation='Line one\nLine two\nFixture citation\nText checked against source\nFixture rights restricted\nOriginal notices retained';
const source={id:'SOURCE-1',title:'Fixture source',rights_id:'RIGHTS-1'};
const evidence={schema_version:'1.2',exported_at:'2026-09-24',note:'Fixture only',poems:[poem],witnesses:[{id:'W-1',poem_id:'TEST-1',source_id:'SOURCE-1',text:'Alternate'}],sources:[source],rights:[{id:'RIGHTS-1',assessment:'Fixture rights restricted'}],source_documents:[{id:'D-1',source_id:'SOURCE-1',title:'Fixture document',local_path:'source.pdf',copying_basis:'Original notices retained'}]};
async function setup(page,initialSession=null){
 await page.addInitScript(({actor,initialSession})=>{const session=initialSession;localStorage.setItem('pts-auth',JSON.stringify(session));Object.defineProperty(navigator,'clipboard',{value:{writeText:async text=>{window.copiedText=text}}});},{actor,initialSession:initialSession||sessionFor(actor,'fixture@example.invalid','reader-default')});
 await page.route('**/auth/v1/**',route=>route.fulfill({json:{id:actor,email:'fixture@example.invalid'}}));
 await page.route('http://127.0.0.1:8001/**',route=>route.fulfill({json:{apps:[],context:{org_id:org,member_id:1,roles:[]}}}));
 let denied=false;const queries=[];
 await page.route('http://127.0.0.1:8010/**',async route=>{
   const url=new URL(route.request().url());queries.push(url);
   if(denied)return route.fulfill({status:403,json:{detail:{code:'access_denied'}}});
   if(url.pathname.startsWith('/api/exports'))return route.fulfill({json:evidence});
   if(url.pathname.startsWith('/api/documents'))return route.fulfill({json:{status:'stored',document:evidence.source_documents[0]}});
   if(url.pathname==='/api/poetry/TEST-1')return route.fulfill({json:{poem,evidence,citation:completeCitation}});
   const none=url.searchParams.get('search')==='absent';
   return route.fulfill({json:{...evidence,poems:none?[]:[poem],total:none?0:1,collection_total:1,filters:{source:['SOURCE-1'],genre:['poem'],origin:['Mombasa'],dialect:['Kimvita'],status:['checked_transcription']},citations:{}}});
 });
 return {queries,revoke:()=>{denied=true;}};
}

test('simple private research reader keeps advanced controls and technical records out of the main view',async({page})=>{
 const state=await setup(page);await page.goto('/?org='+org);
 await expect(page.getByRole('heading',{name:'Fixture poem'})).toBeVisible();
 await expect(page.locator('.intro')).toHaveCount(0);
 await expect(page.getByRole('combobox',{name:'Dialect',exact:true})).toBeVisible();
 await expect(page.getByRole('combobox',{name:'Source',exact:true})).not.toBeVisible();
 await expect(page.getByText('Rights need review',{exact:true}).first()).toBeVisible();
 await expect(page.getByText('Text checked against source',{exact:true})).toBeVisible();
 await page.getByRole('checkbox',{name:'Ready for team research',exact:true}).check();
 await expect.poll(()=>state.queries.some(q=>q.searchParams.get('availability')==='research')).toBeTruthy();
 await page.getByRole('button',{name:/^Filters/}).click();
 const modal=page.getByRole('dialog');await expect(modal).toBeVisible();
 await expect(modal.getByRole('combobox',{name:'Origin',exact:true})).toBeVisible();
 await modal.getByRole('button',{name:'Close',exact:true}).click();
 await expect(page.getByRole('dialog')).not.toBeVisible();
});

test('reader searches, filters, links, copies, exports and opens document with notices',async({page},info)=>{
 const state=await setup(page);await page.goto('/?org='+org);
 await expect(page.getByRole('heading',{name:'Fixture poem'})).toBeVisible();
 await expect(page.locator('.poem-text')).toHaveText('Line one\nLine two');
 await page.getByLabel('Search title, poet, place, form or dialect').fill('absent');
 await expect(page.getByText('No poems match these filters.')).toBeVisible();
 await page.getByRole('button',{name:'Clear filters'}).click();
 await expect(page.getByRole('heading',{name:'Fixture poem'})).toBeVisible();
 {
  await page.getByRole('button',{name:/^Filters/}).click();
  const dialog=page.getByRole('dialog');await expect(dialog).toBeVisible();
  await dialog.getByLabel('Show poems').selectOption('all');
  await dialog.getByRole('button',{name:'Close',exact:true}).click();
  await expect(page.getByRole('button',{name:'Filters',exact:true})).toBeFocused();
  await page.getByRole('button',{name:/^Filters/}).click();
  await expect(dialog.getByLabel('Show poems')).toHaveValue('research');
  await dialog.getByLabel('Show poems').selectOption('all');
  await page.goBack();
  await expect(dialog).not.toBeVisible();
  await page.getByRole('button',{name:/^Filters/}).click();
  await expect(dialog.getByLabel('Show poems')).toHaveValue('research');
  for(const [label,value] of [['Source','SOURCE-1'],['Genre','poem'],['Origin','Mombasa'],['Dialect','Kimvita'],['Text status','checked_transcription']])await dialog.getByRole('combobox',{name:label,exact:true}).selectOption(value);
  await dialog.getByLabel('Show poems').selectOption('checked');
  await dialog.getByRole('button',{name:'Apply filters'}).click();
 }
 await expect.poll(()=>state.queries.some(q=>q.searchParams.get('availability')==='checked')).toBeTruthy();
 await page.getByText('Other downloads',{exact:true}).click();const download=page.waitForEvent('download');await page.getByRole('button',{name:'Export results (JSON)'}).click();expect((await download).suggestedFilename()).toBe('Swahili-poetry-selection.json');
 await page.getByRole('button',{name:'Copy poem with citation',exact:true}).click();
 await expect.poll(()=>page.evaluate(()=>window.copiedText)).toContain('Fixture rights restricted');
 await page.getByRole('link',{name:'Fixture poem',exact:true}).click();
 await expect(page).toHaveURL(/poem=TEST-1/);await expect(page.getByRole('button',{name:'Back to results'})).toBeVisible();
 await page.getByText('Usage and source details',{exact:true}).click();await page.getByText('Copying notices',{exact:true}).click();
 await expect(page.getByText('Original notices retained')).toBeVisible();
 await page.evaluate(()=>{window.open=(url)=>{window.openedDocument=url;return null;};});
 await page.getByRole('button',{name:'Open source document'}).click();
 await expect.poll(()=>page.evaluate(()=>window.openedDocument)).toBe(documentContext);
 await page.screenshot({path:'/tmp/pts-reader-'+info.project.name+'.png',fullPage:true});
 const overflow=await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth);expect(overflow).toBe(false);
 state.revoke();await page.getByRole('button',{name:'Copy poem with citation',exact:true}).click();
 await expect(page.getByRole('alert')).toContainText('do not currently have access');
 await expect(page.locator('.poem-text')).toHaveCount(0);
});

test('direct link and sign-out clear protected content',async({page})=>{
 await setup(page);await page.goto('/?org='+org+'&poem=TEST-1');
 await expect(page.locator('.poem-text')).toBeVisible();
 await page.getByRole('button',{name:'Sign out',exact:true}).click();
 await expect(page.locator('.poem-text')).toHaveCount(0);
 await expect(page.getByRole('heading',{name:'Sign in to read'})).toBeVisible();
});

test('browser Back and Forward restore results and poem',async({page})=>{
 await setup(page);await page.goto('/?org='+org);
 await page.getByRole('link',{name:'Fixture poem',exact:true}).click();
 await expect(page).toHaveURL(/poem=TEST-1/);
 await page.goBack();await expect(page.getByRole('button',{name:'Download poems',exact:true})).toBeVisible();
 await page.goForward();await expect(page.getByRole('button',{name:'Back to results'})).toBeVisible();
});

test('same-user refresh preserves deep link and filters',async({page})=>{
 const sessionId='55555555-5555-4555-8555-555555555555';
 const original=sessionFor(actor,'fixture@example.invalid','reader-original',sessionId);
 const renewed=sessionFor(actor,'fixture@example.invalid','reader-refreshed',sessionId);
 await setup(page,original);let first=true,refreshed=false;
 // The existing auth owner's /user double verifies this same account; its SDK
 // can then return exact same-session claims from a real-shaped refresh response.
 await page.route('**/auth/v1/token*',r=>r.fulfill({json:renewed}));
 await page.route('http://127.0.0.1:8010/api/poetry/TEST-1',async r=>{
   if(first){first=false;return r.fulfill({status:401,json:{detail:{code:'authentication_required'}}});}
   refreshed=r.request().headers().authorization==='Bearer '+renewed.access_token;return r.fallback();
 });
 await page.goto('/?org='+org+'&poem=TEST-1&availability=checked');
 await expect(page.locator('.poem-text')).toBeVisible();
 expect(refreshed).toBe(true);await expect(page).toHaveURL(/poem=TEST-1/);await expect(page).toHaveURL(/availability=checked/);
});

test('late parsed body cannot copy after sign-out',async({page})=>{
 await setup(page);await page.goto('/?org='+org+'&poem=TEST-1');await expect(page.locator('.poem-text')).toBeVisible();
 await page.evaluate(()=>{const original=window.fetch;window.fetch=async(...args)=>{const response=await original(...args);if(String(args[0]).includes('/api/poetry/TEST-1')){const json=response.json.bind(response);response.json=async()=>{const body=await json();await new Promise(resolve=>{window.releaseBody=resolve;});return body;};}return response;};});
 await page.getByRole('button',{name:'Copy poem with citation',exact:true}).click();
 await expect.poll(()=>page.evaluate(()=>Boolean(window.releaseBody))).toBe(true);
 await page.getByRole('button',{name:'Sign out',exact:true}).click();
 await expect(page.getByRole('heading',{name:'Sign in to read'})).toBeVisible();
 await page.evaluate(()=>window.releaseBody());await page.waitForTimeout(100);
 expect(await page.evaluate(()=>window.copiedText)).toBeUndefined();await expect(page.getByRole('dialog')).toHaveCount(0);
});

test('account replacement drops old context and late clipboard fallback',async({page})=>{
 await setup(page);await page.goto('/?org='+org+'&poem=TEST-1');await expect(page.locator('.poem-text')).toBeVisible();
 await page.evaluate(()=>{navigator.clipboard.writeText=()=>new Promise((_resolve,reject)=>{window.rejectCopy=reject;});});
 await page.getByRole('button',{name:'Copy poem with citation',exact:true}).click();
 await expect.poll(()=>page.evaluate(()=>Boolean(window.rejectCopy))).toBe(true);
 const other='44444444-4444-4444-4444-444444444444';
 const replacement=sessionFor(other,'other@example.invalid');
 await page.route('**/auth/v1/token*',r=>r.fulfill({json:replacement}));
 await page.route('**/auth/v1/user',r=>r.fulfill({json:replacement.user}));
 await page.route('http://127.0.0.1:8010/**',r=>r.fulfill({status:403,json:{detail:{code:'access_denied'}}}));
 await page.evaluate(async()=>{const {auth}=await import('/src/auth.ts');await auth.signInWithPassword({email:'other@example.invalid',password:'fixture-only'});});
 await expect(page).not.toHaveURL(/poem=TEST-1/);await expect(page.locator('.poem-text')).toHaveCount(0);
 await page.evaluate(()=>window.rejectCopy(new Error('fixture clipboard denied')));await page.waitForTimeout(100);
 await expect(page.getByRole('dialog')).toHaveCount(0);expect(await page.evaluate(()=>window.copiedText)).toBeUndefined();
});

test('launcher works',async({page})=>{
 await setup(page);
 await page.route('http://127.0.0.1:8001/**',route=>route.fulfill({json:{apps:[{id:'pts',name:'PtS',url:'http://localhost:5179',icon:'book-open',description:'Swahili Poetry',enabled:true}],protected_access_status:'complete'}}));
 await page.goto('/');await expect(page.locator('.poem-text')).toBeVisible();
 await page.getByRole('button',{name:'App launcher',exact:true}).click();
 await expect(page.getByRole('menuitem',{name:'Open PtS',exact:true})).toHaveAttribute('href','http://localhost:5179');
 await page.keyboard.press('Escape');await expect(page.getByRole('menu')).toHaveCount(0);
 });
test('development server denies existing private files without the collected library',async({page})=>{
 const fs=require('node:fs'),path=require('node:path');
 const directory=fs.mkdtempSync(path.resolve(__dirname,'../../reference/.browser-privacy-'));
 const marker='synthetic private source sentinel';
 try{
  const probe=path.join(directory,'private.txt');fs.writeFileSync(probe,marker);
  const blocked=await page.request.get('/@fs'+probe);expect(blocked.status()).toBe(403);
  const shell=await page.request.get('/reference/'+path.basename(directory)+'/private.txt');expect(await shell.text()).not.toContain(marker);
 }finally{fs.rmSync(directory,{recursive:true});}
});

test('filtered length summary counts distinct works and distinguishes missing and unchecked texts',async({page},info)=>{
 await setup(page);
 const p={...poem,work_id:'WORK-1'};
 const medium={...poem,id:'TEST-2',work_id:'WORK-2',title:'Medium example',text:Array(13).fill('Swahili verse').join('\n'),quality:{text_status:'draft_transcription',complete_in_witness:false}};
 const long={...poem,id:'TEST-3',work_id:'WORK-3',title:'Long example',text:Array(40).fill('Swahili verse').join('\n')};
 const missing={...poem,id:'TEST-4',title:'Missing example',text:null,quality:{text_status:'not_collected'}};
 await page.route('http://127.0.0.1:8010/api/poetry?*',r=>{
  const filtered=new URL(r.request().url()).searchParams.get('search')==='only';
  return r.fulfill({json:{...evidence,poems:filtered?[medium]:[p,{...p,id:'VARIANT'},medium,long,missing],research_usage:{'TEST-1':{eligible_for_private_training:true},'VARIANT':{eligible_for_private_training:true},'TEST-3':{eligible_for_private_training:true}},total:filtered?1:5,collection_total:5,filters:{},citations:{}}});
 });
 await page.goto('/?org='+org+'&availability=all');
 const summary=page.getByRole('region',{name:'Results summary'});
 await expect(summary).toContainText('4 distinct works');
 await expect(summary.locator('[data-stat=short]')).toHaveText('1');
 await expect(summary.locator('[data-stat=medium]')).toHaveText('1');
 await expect(summary.locator('[data-stat=substantial]')).toHaveText('1');
 await expect(summary.locator('[data-stat=missing]')).toHaveText('1');
 await expect(summary.locator('[data-stat=ready]')).toHaveText('2');
 await expect(page.locator('#TEST-2 .poem-length')).toContainText('Medium text · 13 lines');
 await expect(page.locator('#TEST-2 .poem-length')).toContainText('Excerpt / incomplete');
 await page.getByLabel('Search title, poet, place, form or dialect').fill('only');
 await expect(summary).toContainText('1 distinct work');
 await expect(summary.locator('[data-stat=short]')).toHaveText('0');
 await expect(summary.locator('[data-stat=ready]')).toHaveText('0');
 await page.screenshot({path:'/tmp/pts-length-'+info.project.name+'.png',fullPage:true});
 expect(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth)).toBe(false);
});

async function cachedReader(page){
 const state=await setup(page);const requests=[];let version=1,denied=false,hold=false,release=null;
 await page.route('http://127.0.0.1:8010/api/poetry?*',async r=>{
  const validator=r.request().headers()['if-none-match'],lean=new URL(r.request().url()).searchParams.get('lean')==='true';requests.push({validator,version,lean});
  if(denied)return r.fulfill({status:403,json:{detail:{code:'access_denied'}}});
  const tag='W/"fixture-'+version+(lean?'':'-full')+'"';
  if(validator===tag){if(hold){hold=false;await new Promise(resolve=>{release=resolve;});}return r.fulfill({status:304,headers:{ETag:tag,'Access-Control-Expose-Headers':'ETag'}});}
  return r.fulfill({headers:{ETag:tag,'Access-Control-Expose-Headers':'ETag'},json:{...evidence,poems:[{...poem,text:version===1?poem.text:'Changed authorized verse'}],total:1,collection_total:1,filters:{},citations:lean?{}:{'TEST-1':completeCitation}}});
 });
 return {...state,requests,hold:()=>{hold=true},release:()=>release?.(),pending:()=>Boolean(release),change:()=>version++,deny:()=>{denied=true}};
}
test('versioned reader reuses authorized bytes on reload and focus without moving reading state',async({page})=>{
 const state=await cachedReader(page);await page.goto('/');await expect(page.locator('.poem-text')).toHaveText(poem.text);
 await expect.poll(()=>page.evaluate(()=>Object.keys(localStorage).some(k=>k.startsWith('platform-json-cache:')))).toBe(true);
 await page.reload();await expect(page.locator('.poem-text')).toHaveText(poem.text);
 expect(state.requests.at(-1).validator).toBe('W/"fixture-1"');
 await page.getByText('Usage and source details',{exact:true}).click();
 await page.evaluate(()=>{window.scrollTo(0,220);window.readerScroll=scrollY;});
 await page.waitForTimeout(1100);
 const before=state.requests.length;const position=await page.locator('.poem-text').boundingBox();state.hold();
 await page.evaluate(()=>{for(let i=0;i<5;i++){window.dispatchEvent(new Event('focus'));document.dispatchEvent(new Event('visibilitychange'));window.dispatchEvent(new Event('resize'));}});
 await expect.poll(()=>state.requests.length).toBe(before+1);await expect.poll(state.pending).toBe(true);
 expect((await page.locator('.poem-text').boundingBox()).y).toBe(position.y);state.release();
 await expect(page.locator('.poem-text')).toHaveText(poem.text);
 expect(await page.evaluate(()=>scrollY)).toBe(await page.evaluate(()=>window.readerScroll));
 await expect(page.locator('.poem-details')).toHaveAttribute('open','');
 state.change();await page.waitForTimeout(1100);await page.evaluate(()=>window.dispatchEvent(new Event('focus')));
 await expect(page.locator('.poem-text')).toHaveText('Changed authorized verse');
 state.deny();await page.waitForTimeout(1100);await page.evaluate(()=>window.dispatchEvent(new Event('focus')));
 await expect(page.getByRole('alert')).toContainText('do not currently have access');
 await expect(page.locator('.poem-text')).toHaveCount(0);
 expect(await page.evaluate(()=>Object.keys(localStorage).filter(k=>k.startsWith('platform-json-cache:')).length)).toBe(0);
});
test('persisted reader bytes stay hidden when current authorization is unavailable',async({page})=>{
 await cachedReader(page);await page.goto('/');await expect(page.locator('.poem-text')).toBeVisible();
 await page.route('http://127.0.0.1:8010/api/poetry?*',r=>r.fulfill({status:503,json:{detail:{code:'access_unavailable'}}}));
 await page.reload();await expect(page.getByRole('alert')).toContainText('retry');await expect(page.locator('.poem-text')).toHaveCount(0);
});
test('reader bounds a hung body, retries, and ignores obsolete filter responses',async({page})=>{
 await page.clock.install({time:new Date()});await setup(page);
 await page.addInitScript(()=>{const original=window.fetch;window.fetch=async(...args)=>{const response=await original(...args);if(String(args[0]).includes('/api/poetry?')&&!window.releaseReaderBody){response.json=()=>new Promise(resolve=>{window.releaseReaderBody=()=>resolve({});});}return response;};});
 await page.goto('/');await expect.poll(()=>page.evaluate(()=>Boolean(window.releaseReaderBody))).toBe(true);
 await page.clock.fastForward(30_000);await expect(page.getByRole('alert')).toHaveCount(0);
 await page.clock.fastForward(30_001);await expect(page.getByRole('alert')).toContainText('timed out');
 await page.getByRole('button',{name:'Retry',exact:true}).click();await expect(page.locator('.poem-text')).toHaveText(poem.text);
 let release;await page.route('http://127.0.0.1:8010/api/poetry?*',async r=>{if(new URL(r.request().url()).searchParams.get('search')==='slow'){await new Promise(resolve=>{release=resolve});try{await r.fulfill({json:{...evidence,poems:[{...poem,text:'Obsolete'}],filters:{},total:1,citations:{}}});}catch{} }else await r.fallback();});
 await page.getByLabel('Search title, poet, place, form or dialect').fill('slow');await expect.poll(()=>Boolean(release)).toBe(true);
 await page.getByLabel('Search title, poet, place, form or dialect').fill('latest');await expect(page.locator('.poem-text')).toHaveText(poem.text);release();await page.waitForTimeout(100);await expect(page.locator('.poem-text')).toHaveText(poem.text);
});
test('compact reader has one identity and a collapsed optional summary',async({page})=>{
 await setup(page);await page.goto('/');await expect(page.locator('.poem-text')).toBeVisible();
 await expect(page.getByRole('heading',{name:'Swahili Poetry',exact:true})).toHaveCount(0);
 await expect(page.getByRole('region',{name:'Results summary'})).not.toHaveAttribute('open','');
 await expect(page.locator('.intro')).toHaveCount(0);
 expect(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth)).toBe(false);
});
test('corrupt corpus payloads and quota failure fall back to network',async({page})=>{
 const state=await cachedReader(page);await page.goto('/');await expect(page.locator('.poem-text')).toHaveText(poem.text);
 await page.evaluate(()=>{for(const key of Object.keys(localStorage).filter(k=>k.startsWith('platform-json-cache:'))){const entry=JSON.parse(localStorage.getItem(key));entry.value=null;localStorage.setItem(key,JSON.stringify(entry));}});
 await page.reload();await expect(page.locator('.poem-text')).toHaveText(poem.text);expect(state.requests.at(-1).validator).toBeUndefined();
 await page.addInitScript(()=>{const set=Storage.prototype.setItem;Storage.prototype.setItem=function(key,value){if(key.startsWith('platform-json-cache:'))throw new DOMException('quota','QuotaExceededError');return set.call(this,key,value);};});
 await page.evaluate(()=>{for(const key of Object.keys(localStorage).filter(k=>k.startsWith('platform-json-cache:')))localStorage.removeItem(key);});
 await page.reload();await expect(page.locator('.poem-text')).toHaveText(poem.text);
});
test('sign-out rejects late collection bodies and cache writes',async({page})=>{
 const state=await cachedReader(page);await page.goto('/');await expect(page.locator('.poem-text')).toHaveText(poem.text);
 await page.evaluate(()=>{const original=window.fetch;window.fetch=async(...args)=>{const response=await original(...args);if(String(args[0]).includes('/api/poetry?')){const json=response.json.bind(response);response.json=async()=>{const data=await json();await new Promise(resolve=>{window.releaseCollection=resolve;});return data;};}return response;};});
 state.change();await page.waitForTimeout(1100);await page.evaluate(()=>window.dispatchEvent(new Event('focus')));
 await expect.poll(()=>page.evaluate(()=>Boolean(window.releaseCollection))).toBe(true);
 await page.getByRole('button',{name:'Sign out',exact:true}).click();await expect(page.getByRole('heading',{name:'Sign in to read'})).toBeVisible();
 await page.evaluate(()=>window.releaseCollection());await page.waitForTimeout(100);
 await expect(page.locator('.poem-text')).toHaveCount(0);
 expect(await page.evaluate(()=>Object.keys(localStorage).filter(k=>k.startsWith('platform-json-cache:')).length)).toBe(0);
});
test('token rotation revalidates scoped cached collection without a second full body',async({page})=>{
 const state=await cachedReader(page);await page.goto('/?dialect=Kimvita');await expect(page.locator('.poem-text')).toHaveText(poem.text);
 const renewed=sessionFor(actor,'fixture@example.invalid','reader-cache-rotated');
 await page.route('**/auth/v1/token*',r=>r.fulfill({json:renewed}));
 const before=state.requests.length;
 await page.evaluate(async()=>{const {auth}=await import('/src/auth.ts');const result=await auth.refreshSession();if(result.error)throw result.error;});
 await expect.poll(()=>state.requests.length).toBeGreaterThan(before);
 expect(state.requests.at(-1).validator).toBe('W/"fixture-1"');
 await expect(page.locator('.poem-text')).toHaveText(poem.text);await expect(page).toHaveURL(/dialect=Kimvita/);
});
test('account replacement removes the previous account persisted corpus',async({page})=>{
 await cachedReader(page);await page.goto('/');await expect(page.locator('.poem-text')).toHaveText(poem.text);
 const other=sessionFor('44444444-4444-4444-4444-444444444444','other@example.invalid','cache-replacement');
 await page.route('**/auth/v1/token*',r=>r.fulfill({json:other}));await page.route('**/auth/v1/user',r=>r.fulfill({json:other.user}));
 await page.route('http://127.0.0.1:8010/**',r=>r.fulfill({status:403,json:{detail:{code:'access_denied'}}}));
 await page.evaluate(async()=>{const {auth}=await import('/src/auth.ts');await auth.signInWithPassword({email:'other@example.invalid',password:'fixture-only'});});
 await expect(page.locator('.poem-text')).toHaveCount(0);
 expect(await page.evaluate(()=>Object.keys(localStorage).filter(k=>k.startsWith('platform-json-cache:')).length)).toBe(0);
});
test('focus cannot restore corpus while provider sign-out is pending',async({page})=>{
 const state=await cachedReader(page);await page.goto('/');await expect(page.locator('.poem-text')).toHaveText(poem.text);
 let release,held=false;const pending=new Promise(resolve=>release=resolve);
 await page.route('**/auth/v1/logout*',async r=>{held=true;await pending;return r.fulfill({status:204});});
 try{
  await page.getByRole('button',{name:'Sign out',exact:true}).click();await expect.poll(()=>held).toBe(true);
  const before=state.requests.length;await page.waitForTimeout(1100);
  await page.evaluate(()=>{window.dispatchEvent(new Event('focus'));document.dispatchEvent(new Event('visibilitychange'));});
  await page.waitForTimeout(250);expect(state.requests.length).toBe(before);
  await expect(page.locator('.poem-text')).toHaveCount(0);
  expect(await page.evaluate(()=>Object.keys(localStorage).filter(k=>k.startsWith('platform-json-cache:')).length)).toBe(0);
 }finally{release();}
 await expect(page.getByRole('heading',{name:'Sign in to read'})).toBeVisible();
});
test('failed filter replacement clears old results and latest response wins',async({page})=>{
 await cachedReader(page);await page.goto('/');await expect(page.locator('.poem-text')).toHaveText(poem.text);
 let release,held=false;const pending=new Promise(resolve=>release=resolve);
 const result=(title,text)=>({...evidence,poems:[{...poem,title,text}],total:1,collection_total:1,filters:{},citations:{}});
 await page.route('http://127.0.0.1:8010/api/poetry?*',async r=>{
  const search=new URL(r.request().url()).searchParams.get('search');
  if(search==='failed')return r.fulfill({status:503,json:{detail:{code:'access_unavailable'}}});
  if(search==='slow'){held=true;await pending;try{return await r.fulfill({json:result('Obsolete result','Obsolete verse')});}catch{return;}}
  return r.fulfill({json:result('Latest result','Latest verse')});
 });
 await page.getByLabel('Search title, poet, place, form or dialect').fill('failed');
 await expect(page.getByRole('alert')).toContainText('retry');await expect(page.locator('.poem-text')).toHaveCount(0);
 await expect(page.getByRole('button',{name:'Download poems',exact:true})).toHaveCount(0);
 await expect(page.getByText('1 poems and excerpts shown',{exact:true})).toHaveCount(0);
 try{
  await page.getByLabel('Search title, poet, place, form or dialect').fill('slow');await expect.poll(()=>held).toBe(true);
  await expect(page.locator('.poem-text')).toHaveCount(0);
  await page.getByLabel('Search title, poet, place, form or dialect').fill('latest');await expect(page.locator('.poem-text')).toHaveText('Latest verse');
  release();await page.waitForTimeout(100);await expect(page.getByRole('heading',{name:'Latest result'})).toBeVisible();
  await expect(page.getByRole('heading',{name:'Obsolete result'})).toHaveCount(0);await expect(page.getByText('1 poems and excerpts shown',{exact:true})).toBeVisible();
 }finally{release();}
});
for(const corrupt of ['plan reason','plan contact','lead origin','lead contact'])test('persisted Sources corruption falls back to network: '+corrupt,async({page})=>{
 await setup(page);const requests=[];
 const data={sources:[source],rights:[],source_documents:[],acquisition:{'SOURCE-1':{priority:'high',reason:'Useful recorded source',access:'Ask the source',next_step:'Review terms',contact:{name:'Source contact',verified_on:'2026-11-05'}}},acquisition_leads:[{id:'LEAD-1',title:'Collection lead',origin:'Coast',reason:'Relevant collection',contact:{name:'Lead contact',verified_on:'2026-11-05'}}]};
 await page.route('http://127.0.0.1:8010/api/sources',r=>{const validator=r.request().headers()['if-none-match'];requests.push(validator);return r.fulfill(validator?{status:304,headers:{ETag:'W/"sources"','Access-Control-Expose-Headers':'ETag'}}:{headers:{ETag:'W/"sources"','Access-Control-Expose-Headers':'ETag'},json:data});});
 await page.goto('/?view=sources');await expect(page.getByRole('heading',{name:'Fixture source'})).toBeVisible();
 await expect.poll(()=>page.evaluate(()=>Object.keys(localStorage).some(k=>k.startsWith('platform-json-cache:')))).toBe(true);
 await page.evaluate(corrupt=>{for(const key of Object.keys(localStorage).filter(k=>k.startsWith('platform-json-cache:'))){const entry=JSON.parse(localStorage.getItem(key));if(entry.path!=='/api/sources')continue;const row=corrupt.startsWith('plan')?entry.value.acquisition['SOURCE-1']:entry.value.acquisition_leads[0];if(corrupt.endsWith('contact'))row.contact.name={bad:'value'};else row[corrupt.endsWith('reason')?'reason':'origin']={bad:'value'};localStorage.setItem(key,JSON.stringify(entry));}},corrupt);
 await page.reload();await expect(page.getByRole('heading',{name:'Fixture source'})).toBeVisible();
 expect(requests.at(-1)).toBeUndefined();await expect(page.getByText('Useful recorded source',{exact:true})).toBeVisible();
});

test('persisted collection is lean and copy fetches complete citation freshly',async({page})=>{
 const state=await cachedReader(page);await page.goto('/');await expect(page.locator('.poem-text')).toHaveText(poem.text);
 const stored=()=>page.evaluate(()=>Object.keys(localStorage).filter(k=>k.startsWith('platform-json-cache:')).map(k=>JSON.parse(localStorage.getItem(k))).find(e=>e.path.startsWith('/api/poetry?'))?.value);
 await expect.poll(stored).toBeTruthy();expect((await stored()).citations).toEqual({});expect(state.requests.at(-1).lean).toBe(true);
 const before=state.queries.filter(q=>q.pathname==='/api/poetry/TEST-1').length;
 await page.getByRole('button',{name:'Copy poem with citation',exact:true}).click();
 await expect.poll(()=>state.queries.filter(q=>q.pathname==='/api/poetry/TEST-1').length).toBe(before+1);
 await expect.poll(()=>page.evaluate(()=>window.copiedText)).toBe(completeCitation);
});
