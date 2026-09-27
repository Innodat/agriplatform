const {test,expect}=require('@playwright/test');
const actor='33333333-3333-3333-3333-333333333333',org='11111111-1111-1111-1111-111111111111';
const user={id:actor,email:'reader@example.invalid',aud:'authenticated',app_metadata:{},user_metadata:{}};
const session={access_token:'test-token',refresh_token:'test-refresh',expires_at:Date.now()/1000+3600,expires_in:3600,token_type:'bearer',user};
const apps=[{id:'pts',name:'PtS',url:'http://localhost:5183',icon:'book-open',description:'Swahili Poetry',enabled:true},{id:'scribeswell',name:'Scribeswell',url:'http://localhost:5183/scribeswell/',icon:'book-open',description:'Hebrew Bible',enabled:true},{id:'disabled',name:'Disabled',url:'http://localhost:9999',icon:'book-open',description:'Not ready',enabled:false}];
async function setup(context){
 await context.route('**/auth/v1/**',r=>r.request().url().includes('/token')?r.fulfill({json:session}):r.request().url().includes('/logout')?r.fulfill({status:204}):r.fulfill({json:user}));
 await context.route('http://127.0.0.1:8001/**',r=>r.fulfill({json:r.request().url().endsWith('/api/apps')?apps:{apps:apps.filter(a=>a.enabled),context:{org_id:org,member_id:1,roles:[]}}}));
 await context.route('http://127.0.0.1:8010/**',r=>r.fulfill({json:{sources:[{id:'S1',title:'Protected source',rights_id:'R1'}],rights:[],source_documents:[]}}));
 await context.route('**/api/bible/**',r=>r.fulfill({json:r.request().url().includes('/words/')?{id:1,position:1,surface_he:'בְּרֵאשִׁית',display_he:'בְּרֵאשִׁית',lemma_strong:null,morph_code:null,morphemes:[]}:r.request().url().endsWith('/books')?{data:[{id:1,osis_id:'Gen',name_en:'Genesis',name_he:'בראשית',testament:'OT',book_order:1}],total:1}:{data:[{id:1,verse_num:1,book_id:1,chapter_num:1,words:[{id:1,position:1,surface_he:'בְּרֵאשִׁית',display_he:'בְּרֵאשִׁית',lemma_strong:null,morph_code:null}]}],total:1}}));
}
test('existing PtS session and sign-out synchronize across both readers',async({context,page})=>{
 await setup(context);await page.goto('/?view=sources&org='+org);await page.evaluate(s=>localStorage.setItem('pts-auth',JSON.stringify(s)),session);await page.reload();
 await expect(page.getByRole('heading',{name:'Protected source'})).toBeVisible();
 const bible=await context.newPage();await bible.goto('http://localhost:5183/scribeswell/?book=Gen&chapter=1');
 await expect(bible.getByRole('button',{name:'Sign out',exact:true})).toBeVisible();await expect(bible.getByRole('list',{name:'Verses'})).toBeVisible();
 await bible.getByRole('button',{name:'Sign out',exact:true}).click();
 await expect(page.getByRole('heading',{name:'Protected source'})).toHaveCount(0);await expect(page.getByRole('heading',{name:'Sign in to read'})).toBeVisible();
 await expect(bible.getByRole('button',{name:'Sign in',exact:true})).toBeVisible();await expect(bible.getByRole('list',{name:'Verses'})).toBeVisible();
 await bible.getByRole('button',{name:'App launcher'}).click();await expect(bible.getByRole('menuitem',{name:'Open PtS'})).toBeVisible();await expect(bible.getByRole('menuitem',{name:'Open Disabled'})).toHaveCount(0);
 await bible.keyboard.press('Escape');await bible.getByRole('button',{name:'Sign in',exact:true}).click();await bible.getByLabel('Email',{exact:true}).fill(user.email);await bible.getByLabel('Password',{exact:true}).fill('fixture-password');await bible.getByRole('dialog').getByRole('button',{name:'Sign in',exact:true}).click();
 await expect(page.getByRole('heading',{name:'Protected source'})).toBeVisible();await page.getByRole('button',{name:'Sign out',exact:true}).click();await expect(bible.getByRole('button',{name:'Sign in',exact:true})).toBeVisible();
 await expect(bible).toHaveURL(/\/scribeswell\/\?book=Gen&chapter=1$/);
 await page.getByLabel('Email',{exact:true}).fill(user.email);await page.getByLabel('Password',{exact:true}).fill('fixture-password');await page.getByRole('button',{name:'Sign in',exact:true}).click();await expect(bible.getByRole('button',{name:'Sign out',exact:true})).toBeVisible();
});
test('anonymous reader has a launchpad and no authentication requirement',async({context,page})=>{
 await setup(context);await page.goto('/scribeswell/');await expect(page.getByRole('list',{name:'Verses'})).toBeVisible();
 await page.getByRole('button',{name:/Word:/}).click();await expect(page.getByRole('complementary',{name:'Word morphology'})).toBeVisible();
 await page.getByRole('button',{name:'App launcher'}).click();await expect(page.getByRole('menuitem',{name:'Open PtS'})).toBeVisible();await expect(page.getByRole('menuitem',{name:'Open Scribeswell'})).toBeVisible();await expect(page.getByRole('menuitem',{name:'Open Disabled'})).toHaveCount(0);
});

test('failed Scribeswell sign-out reports an error without clearing either session',async({context,page})=>{
 await setup(context);await page.goto('/?view=sources&org='+org);await page.evaluate(s=>localStorage.setItem('pts-auth',JSON.stringify(s)),session);await page.reload();await expect(page.getByRole('heading',{name:'Protected source'})).toBeVisible();
 const bible=await context.newPage();await bible.goto('/scribeswell/');await expect(bible.getByRole('button',{name:'Sign out',exact:true})).toBeVisible();
 await context.route('**/auth/v1/logout*',r=>r.fulfill({status:400,json:{msg:'fixture failure'}}));
 await bible.getByRole('button',{name:'Sign out',exact:true}).click();await expect(bible.getByRole('alert')).toContainText('could not sign you out');
 await expect(bible.getByRole('button',{name:'Sign out',exact:true})).toBeVisible();await expect(page.getByRole('heading',{name:'Protected source'})).toBeVisible();
});
test('account replacement clears previous PtS context and protected content',async({context,page})=>{
 await setup(context);await page.goto('/?view=sources&org='+org+'&search=private-context');await page.evaluate(s=>localStorage.setItem('pts-auth',JSON.stringify(s)),session);await page.reload();await expect(page.getByRole('heading',{name:'Protected source'})).toBeVisible();
 const bible=await context.newPage();await bible.goto('/scribeswell/');await expect(bible.getByRole('button',{name:'Sign out',exact:true})).toBeVisible();
 await context.route('**/auth/v1/token*',r=>r.fulfill({json:{...session,user:{...user,id:'44444444-4444-4444-4444-444444444444',email:'other@example.invalid'},access_token:'other-token'}}));
 await context.route('http://127.0.0.1:8010/**',r=>r.fulfill({status:403,json:{detail:{code:'access_denied'}}}));
 await bible.evaluate(async()=>{const {supabase}=await import('/scribeswell/src/lib/supabase.ts');await supabase.auth.signInWithPassword({email:'other@example.invalid',password:'fixture-password'});});
 await expect(page.getByRole('heading',{name:'Protected source'})).toHaveCount(0);await expect(page).not.toHaveURL(/private-context/);await expect(page).not.toHaveURL(/view=sources/);await expect(bible.getByRole('list',{name:'Verses'})).toBeVisible();
});
test('old standalone reader address redirects to shared origin preserving chapter',async({context,page})=>{
 await setup(context);await page.goto('http://localhost:5184/?book=Gen&chapter=1');await expect(page).toHaveURL('http://localhost:5183/scribeswell/?book=Gen&chapter=1');await expect(page.getByRole('list',{name:'Verses'})).toBeVisible();
});

test('nested Bible requests reach the API with the application prefix removed',async({context,page})=>{
 await setup(context);await context.unroute('**/api/bible/**');await page.goto('/scribeswell/');await expect(page.getByRole('list',{name:'Verses'})).toBeVisible();
 const response=await page.request.get('http://127.0.0.1:5185/requests');const paths=await response.json();expect(paths).toContain('/api/bible/books');expect(paths).toContain('/api/bible/books/Gen/chapters/1/verses');expect(paths.some(p=>p.startsWith('/scribeswell/'))).toBe(false);
});
test('signing in through PtS closes and clears the open Scribeswell sign-in dialog',async({context,page})=>{
 await setup(context);await page.goto('/?view=sources&org='+org);
 const bible=await context.newPage();await bible.goto('/scribeswell/');await bible.getByRole('button',{name:'Sign in',exact:true}).click();await bible.getByLabel('Email',{exact:true}).fill('unfinished@example.invalid');
 await page.getByLabel('Email',{exact:true}).fill(user.email);await page.getByLabel('Password',{exact:true}).fill('fixture-password');await page.getByRole('button',{name:'Sign in',exact:true}).click();
 await expect(bible.getByRole('dialog')).toHaveCount(0);await expect(bible.getByRole('button',{name:'Sign out',exact:true})).toBeVisible();
 await page.getByRole('button',{name:'Sign out',exact:true}).click();await expect(bible.getByRole('button',{name:'Sign in',exact:true})).toBeVisible();await expect(bible.getByRole('dialog')).toHaveCount(0);
 await bible.getByRole('button',{name:'Sign in',exact:true}).click();await expect(bible.getByLabel('Email',{exact:true})).toHaveValue('');
});
test('expired shared session refreshes and is recognized by both apps',async({context,page})=>{
 await setup(context);let refreshes=0;await context.route('**/auth/v1/token*',r=>{refreshes++;return r.fulfill({json:session});});
 await page.goto('/?view=sources&org='+org);await page.evaluate(s=>localStorage.setItem('pts-auth',JSON.stringify(s)),{...session,expires_at:1});await page.reload();
 await expect(page.getByRole('heading',{name:'Protected source'})).toBeVisible();expect(refreshes).toBeGreaterThan(0);
 const bible=await context.newPage();await bible.goto('/scribeswell/');await expect(bible.getByRole('button',{name:'Sign out',exact:true})).toBeVisible();await expect(bible.getByRole('list',{name:'Verses'})).toBeVisible();
});
for(const action of ['complete','logout'])test('shared recovery keeps public reading available: '+action,async({context,page})=>{
 await setup(context);await page.goto('/?view=sources&org='+org);await page.evaluate(s=>localStorage.setItem('pts-auth',JSON.stringify(s)),session);await page.reload();
 const bible=await context.newPage();await bible.goto('/scribeswell/');await expect(bible.getByRole('button',{name:'Sign out',exact:true})).toBeVisible();
 const token=[{alg:'HS256',typ:'JWT'},{sub:actor,exp:Math.floor(Date.now()/1000)+3600},'fixture'].map(v=>Buffer.from(typeof v==='string'?v:JSON.stringify(v)).toString('base64url')).join('.');
 await page.goto('/?view=sources&org='+org+'#'+new URLSearchParams({access_token:token,refresh_token:'fixture-refresh',expires_in:'3600',token_type:'bearer',type:'recovery'}));
 await expect(page.getByRole('heading',{name:'Choose a new password'})).toBeVisible();await expect(page.getByRole('heading',{name:'Protected source'})).toHaveCount(0);await expect(bible.getByRole('list',{name:'Verses'})).toBeVisible();
 if(action==='logout'){
  await bible.getByRole('button',{name:'Sign out',exact:true}).click();await expect(page.getByRole('heading',{name:'Sign in to read'})).toBeVisible();await expect(page.getByLabel('New password',{exact:true})).toHaveCount(0);
 }else{
  await page.getByLabel('New password',{exact:true}).fill('fixture-new-password');await page.getByLabel('Confirm password',{exact:true}).fill('fixture-new-password');await page.getByRole('button',{name:'Save password'}).click();await expect(page.getByRole('heading',{name:'Protected source'})).toBeVisible();await expect(bible.getByRole('button',{name:'Sign out',exact:true})).toBeVisible();
 }
});
test('failed refresh leaves Bible reading public and clears expired PtS content',async({context,page})=>{
 await setup(context);await context.route('**/auth/v1/token*',r=>r.fulfill({status:400,json:{code:'refresh_token_not_found',msg:'Expired fixture session'}}));
 await page.goto('/?view=sources&org='+org);await page.evaluate(s=>localStorage.setItem('pts-auth',JSON.stringify(s)),{...session,expires_at:1});await page.reload();
 const bible=await context.newPage();await bible.goto('/scribeswell/');await expect(bible.getByRole('list',{name:'Verses'})).toBeVisible();await expect(bible.getByRole('button',{name:'Sign in',exact:true})).toBeVisible();await expect(page.getByRole('heading',{name:'Protected source'})).toHaveCount(0);await expect(page.getByRole('heading',{name:'Sign in to read'})).toBeVisible();
});
