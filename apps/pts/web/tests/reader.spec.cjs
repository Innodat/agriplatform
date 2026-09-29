const {test,expect}=require('@playwright/test');
const org='11111111-1111-1111-1111-111111111111';
const actor='33333333-3333-3333-3333-333333333333';
const poem={id:'TEST-1',title:'Fixture poem',text:'Line one\nLine two',source_id:'SOURCE-1',creator:{name:'Fixture poet'},classification:{genre:'poem'},geography:{origin_locality:'Mombasa',dialect:'Kimvita'},quality:{text_status:'checked_transcription',reviewer_note:'Assistant check only'},source:{citation:'Fixture citation',locator:'page 1',url:'https://source.invalid/'}};
const source={id:'SOURCE-1',title:'Fixture source',rights_id:'RIGHTS-1'};
const evidence={schema_version:'1.2',exported_at:'2026-09-24',note:'Fixture only',poems:[poem],witnesses:[{id:'W-1',poem_id:'TEST-1',source_id:'SOURCE-1',text:'Alternate'}],sources:[source],rights:[{id:'RIGHTS-1',assessment:'Fixture rights restricted'}],source_documents:[{id:'D-1',source_id:'SOURCE-1',title:'Fixture document',local_path:'source.pdf',copying_basis:'Original notices retained'}]};
async function setup(page){
 await page.addInitScript(({actor})=>{const session={access_token:'test-token',refresh_token:'test-refresh',expires_at:Date.now()/1000+3600,expires_in:3600,token_type:'bearer',user:{id:actor,email:'fixture@example.invalid',aud:'authenticated',app_metadata:{},user_metadata:{}}};localStorage.setItem('pts-auth',JSON.stringify(session));Object.defineProperty(navigator,'clipboard',{value:{writeText:async text=>{window.copiedText=text}}});},{actor});
 await page.route('**/auth/v1/**',route=>route.fulfill({json:{id:actor,email:'fixture@example.invalid'}}));
 await page.route('http://127.0.0.1:8001/**',route=>route.fulfill({json:{apps:[],context:{org_id:org,member_id:1,roles:[]}}}));
 let denied=false;const queries=[];
 await page.route('http://127.0.0.1:8010/**',async route=>{
   const url=new URL(route.request().url());queries.push(url);
   if(denied)return route.fulfill({status:403,json:{detail:{code:'access_denied'}}});
   if(url.pathname.startsWith('/api/exports'))return route.fulfill({json:evidence});
   if(url.pathname.startsWith('/api/documents'))return route.fulfill({json:{status:'stored',url:'https://private.invalid/read?bounded=true',expires_in:300,document:evidence.source_documents[0]}});
   if(url.pathname==='/api/poetry/TEST-1')return route.fulfill({json:{poem,evidence,citation:'Line one\nLine two\nFixture citation\nFixture rights restricted'}});
   const none=url.searchParams.get('search')==='absent';
   return route.fulfill({json:{...evidence,poems:none?[]:[poem],total:none?0:1,collection_total:1,filters:{source:['SOURCE-1'],genre:['poem'],origin:['Mombasa'],dialect:['Kimvita'],status:['checked_transcription']},citations:{}}});
 });
 return {queries,revoke:()=>{denied=true;}};
}

test('reader searches, filters, links, copies, exports and opens document with notices',async({page},info)=>{
 const state=await setup(page);await page.goto('/?org='+org);
 await expect(page.getByRole('heading',{name:'Fixture poem'})).toBeVisible();
 await expect(page.locator('.poem-text')).toHaveText('Line one\nLine two');
 await page.getByLabel('Search title, poet, place, form or dialect').fill('absent');
 await expect(page.getByText('No poems match these filters.')).toBeVisible();
 await page.getByRole('button',{name:'Clear filters'}).click();
 await expect(page.getByRole('heading',{name:'Fixture poem'})).toBeVisible();
 if(info.project.name==='mobile'){
  await page.getByRole('button',{name:/^Filters/}).click();
  const dialog=page.getByRole('dialog');await expect(dialog).toBeVisible();
  await dialog.getByLabel('Show poems').selectOption('all');
  await dialog.getByRole('button',{name:'Close',exact:true}).click();
  await expect(page.getByRole('button',{name:'Filters',exact:true})).toBeFocused();
  await page.getByRole('button',{name:/^Filters/}).click();
  await expect(dialog.getByLabel('Show poems')).toHaveValue('text');
  await dialog.getByLabel('Show poems').selectOption('all');
  await page.goBack();
  await expect(dialog).not.toBeVisible();
  await page.getByRole('button',{name:/^Filters/}).click();
  await expect(dialog.getByLabel('Show poems')).toHaveValue('text');
  for(const [label,value] of [['Source','SOURCE-1'],['Genre','poem'],['Origin','Mombasa'],['Dialect','Kimvita'],['Text status','checked_transcription']])await dialog.getByRole('combobox',{name:label,exact:true}).selectOption(value);
  await dialog.getByLabel('Show poems').selectOption('checked');
  await dialog.getByRole('button',{name:'Apply filters'}).click();
 }else{for(const [label,value] of [['Source','SOURCE-1'],['Genre','poem'],['Origin','Mombasa'],['Dialect','Kimvita'],['Text status','checked_transcription']])await page.getByRole('combobox',{name:label,exact:true}).first().selectOption(value);await page.getByLabel('Show poems').first().selectOption('checked');}
 await expect.poll(()=>state.queries.some(q=>q.searchParams.get('availability')==='checked')).toBeTruthy();
 const download=page.waitForEvent('download');await page.getByRole('button',{name:'Export results (JSON)'}).click();expect((await download).suggestedFilename()).toBe('Swahili-poetry-selection.json');
 await page.getByRole('button',{name:'Copy poem with citation',exact:true}).click();
 await expect.poll(()=>page.evaluate(()=>window.copiedText)).toContain('Fixture rights restricted');
 await page.getByRole('link',{name:'Fixture poem',exact:true}).click();
 await expect(page).toHaveURL(/poem=TEST-1/);await expect(page.getByRole('button',{name:'Back to results'})).toBeVisible();
 await page.getByText('Evidence, witnesses and rights',{exact:true}).click();
 await expect(page.getByText('Original notices retained')).toBeVisible();
 await page.evaluate(()=>{window.open=(url)=>{window.openedDocument=url;return null;};});
 await page.getByRole('button',{name:'Open source document'}).click();
 await expect.poll(()=>page.evaluate(()=>window.openedDocument)).toContain('https://private.invalid/read');
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
 await page.goBack();await expect(page.getByRole('button',{name:'Export results (JSON)'})).toBeVisible();
 await page.goForward();await expect(page.getByRole('button',{name:'Back to results'})).toBeVisible();
});

test('same-user refresh preserves deep link and filters',async({page})=>{
 await setup(page);let first=true,refreshed=false;
 await page.route('**/auth/v1/token*',r=>r.fulfill({json:{access_token:'refreshed-token',refresh_token:'refreshed',expires_in:3600,token_type:'bearer',user:{id:actor,email:'fixture@example.invalid',aud:'authenticated',app_metadata:{},user_metadata:{}}}}));
 await page.route('http://127.0.0.1:8010/api/poetry/TEST-1',async r=>{
   if(first){first=false;return r.fulfill({status:401,json:{detail:{code:'authentication_required'}}});}
   refreshed=r.request().headers().authorization==='Bearer refreshed-token';return r.fallback();
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
 await page.route('**/auth/v1/token*',r=>r.fulfill({json:{access_token:'other-token',refresh_token:'other-refresh',expires_in:3600,token_type:'bearer',user:{id:other,email:'other@example.invalid',aud:'authenticated',app_metadata:{},user_metadata:{}}}}));
 await page.route('http://127.0.0.1:8010/**',r=>r.fulfill({status:403,json:{detail:{code:'access_denied'}}}));
 await page.evaluate(async()=>{const {auth}=await import('/src/auth.ts');await auth.signInWithPassword({email:'other@example.invalid',password:'fixture-only'});});
 await expect(page).not.toHaveURL(/poem=TEST-1/);await expect(page.locator('.poem-text')).toHaveCount(0);
 await page.evaluate(()=>window.rejectCopy(new Error('fixture clipboard denied')));await page.waitForTimeout(100);
 await expect(page.getByRole('dialog')).toHaveCount(0);expect(await page.evaluate(()=>window.copiedText)).toBeUndefined();
});

test('launcher works',async({page})=>{
 await setup(page);
 await page.route('http://127.0.0.1:8001/**',route=>route.fulfill({json:{apps:[{id:'pts',name:'PtS',url:'http://localhost:5179',icon:'book-open',description:'Swahili Poetry',enabled:true}],context:{org_id:org,member_id:1,roles:[]}}}));
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
