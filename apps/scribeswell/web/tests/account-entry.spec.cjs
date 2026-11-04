const {test,expect}=require('@playwright/test');
const user={id:'33333333-3333-3333-3333-333333333333',email:'reader@example.invalid',aud:'authenticated',app_metadata:{},user_metadata:{}};
const session={access_token:'test-token',refresh_token:'test-refresh',expires_at:Date.now()/1000+3600,expires_in:3600,token_type:'bearer',user};
async function setup(page){
 await page.route('http://127.0.0.1:8001/**',r=>r.fulfill({json:[]}));
 await page.route('**/api/bible/**',r=>{const path=new URL(r.request().url()).pathname;const book={id:1,osis_id:'Gen',name_en:'Genesis',name_he:'בראשית',testament:'OT',book_order:1};const word={id:1,position:1,surface_he:'בְּרֵאשִׁית',display_he:'בְּרֵאשִׁית',lemma_strong:null,morph_code:null};return r.fulfill({json:path.endsWith('/books')?{data:[book],total:1}:path.endsWith('/books/Gen')?{...book,chapters:[{id:1,chapter_num:1}]}:path.includes('/words/')?{...word,morphemes:[]}:{data:[{id:1,verse_num:1,book_id:1,chapter_num:1,words:[word]}],total:1}});});
}
async function enter(page,mode='Create account'){
 await page.getByRole('banner').getByRole('button',{name:mode,exact:true}).click();
 await page.getByLabel('Email',{exact:true}).fill(user.email);await page.getByLabel('Password',{exact:true}).fill('fixture-password');
}
test('existing sign-in and cancellation preserve public analysis',async({page})=>{
 await setup(page);await page.goto('/?book=Gen&chapter=1');await page.getByRole('button',{name:/Word:/}).click();await enter(page,'Sign in');
 await page.getByRole('button',{name:'Close sign in dialog'}).click();await expect(page.getByRole('complementary',{name:'Word morphology'})).toBeVisible();await expect(page).toHaveURL(/book=Gen&chapter=1/);
});
test('standalone Create account is available without a study',async({page})=>{
 await setup(page);await page.goto('/');await expect(page.getByRole('banner').getByRole('button',{name:'Create account',exact:true})).toBeVisible();
});
test('confirmation pending is neutral, explicit and keeps only validated public return fields',async({page})=>{
 await setup(page);let requests=[];await page.route('**/auth/v1/signup*',r=>{requests.push({url:r.request().url(),body:r.request().postDataJSON()});return r.fulfill({json:{id:user.id,email:user.email,identities:[]}});});
 await page.goto('/?book=Gen&chapter=1&verse=1&compareBook=Exod&compareChapter=2&compareVerse=3&return=https://evil.invalid&access_token=secret#redirect_to=https://evil.invalid');
 await enter(page);await page.getByRole('dialog').getByRole('button',{name:'Create account',exact:true}).click();
 await expect(page.getByRole('heading',{name:'Check your email'})).toBeVisible();await expect(page.getByRole('status')).toContainText('If this address can be registered');
 expect(requests).toHaveLength(1);expect(requests[0].body.email).toBe(user.email);expect(requests[0].body.password).toBe('fixture-password');
 expect(new URL(requests[0].url).searchParams.get('redirect_to')).toBe('http://127.0.0.1:5182/?book=Gen&chapter=1&verse=1&compareBook=Exod&compareChapter=2&compareVerse=3');
 await page.getByRole('dialog').getByRole('button',{name:'Sign in',exact:true}).click();await expect(page.getByLabel('Password',{exact:true})).toHaveValue('');
 await page.keyboard.press('Escape');await expect(page.getByRole('banner').getByRole('button',{name:'Create account',exact:true})).toBeFocused();await expect(page.getByRole('list',{name:'Verses'}).first()).toBeVisible();
});
for(const [code,message] of [['signup_disabled','currently unavailable'],['weak_password','stronger password'],['email_address_invalid','Check your email address'],['over_request_rate_limit','Too many attempts'],['unknown','could not complete']])test('signup maps safe typed error '+code,async({page})=>{
 await setup(page);let calls=0;await page.route('**/auth/v1/signup*',r=>{calls++;return r.fulfill({status:400,headers:{'x-supabase-api-version':'2024-01-01','access-control-expose-headers':'X-Supabase-Api-Version'},json:{code,msg:'sensitive provider exception'}});});await page.goto('/');await enter(page);await page.getByRole('dialog').getByRole('button',{name:'Create account',exact:true}).click();
 await expect(page.getByRole('alert')).toContainText(message);await expect(page.getByRole('alert')).not.toContainText('sensitive');await expect(page.getByRole('dialog').getByRole('button',{name:'Create account',exact:true})).toBeEnabled();expect(calls).toBe(1);await expect(page.getByLabel('Email',{exact:true})).toBeEditable();await page.getByRole('dialog').getByRole('button',{name:'Create account',exact:true}).click();await expect.poll(()=>calls).toBe(2);await expect(page.getByRole('dialog').getByRole('button',{name:'Create account',exact:true})).toBeEnabled();
});
for(const [code,message] of [['invalid_credentials','Check your email and password'],['email_not_confirmed','Confirm your email']])test('sign-in maps safe typed error '+code,async({page})=>{
 await setup(page);await page.route('**/auth/v1/token*',r=>r.fulfill({status:400,headers:{'x-supabase-api-version':'2024-01-01','access-control-expose-headers':'X-Supabase-Api-Version'},json:{code,msg:'private provider text'}}));await page.goto('/');await enter(page,'Sign in');await page.getByRole('dialog').getByRole('button',{name:'Sign in',exact:true}).click();await expect(page.getByRole('alert')).toContainText(message);await expect(page.getByRole('alert')).not.toContainText('private provider');
});
test('session signup updates shared storage without protected requests',async({page})=>{
 await setup(page);const requests=[];page.on('request',r=>requests.push(r.url()));await page.route('**/auth/v1/signup*',r=>r.fulfill({json:session}));await page.goto('/?book=Gen&chapter=1');await enter(page);await page.getByRole('dialog').getByRole('button',{name:'Create account',exact:true}).click();await expect(page.getByRole('button',{name:'Sign out',exact:true})).toBeVisible();await expect(page.getByRole('dialog')).toHaveCount(0);expect(await page.evaluate(()=>JSON.parse(localStorage.getItem('pts-auth')).user.id)).toBe(user.id);expect(requests.filter(url=>/\/api\/(?:studies|operations|enroll|membership|grant)(?:\/|$)|\/v2\/(?:enrollments|check)(?:\/|$)/.test(new URL(url).pathname))).toEqual([]);await expect(page.getByRole('list',{name:'Verses'})).toBeVisible();
});
test('invalid callback preserves existing session and scrubs metadata',async({page})=>{
 await setup(page);await page.goto('/');await page.evaluate(s=>localStorage.setItem('pts-auth',JSON.stringify(s)),session);await page.goto('/?book=Gen&chapter=1&error_code=otp_expired&error_description=private#access_token=bad&error=access_denied');await expect(page.getByRole('alert')).toContainText('invalid or has expired');await expect(page.getByRole('alert')).not.toContainText('private');await expect(page).toHaveURL('http://127.0.0.1:5182/?book=Gen&chapter=1');await expect(page.getByRole('button',{name:'Sign out',exact:true})).toBeVisible();await page.getByRole('button',{name:'Dismiss'}).click();await expect(page.getByRole('alert')).toHaveCount(0);
});
test('cancel and mode switch discard late outcomes and clear secrets',async({page})=>{
 await setup(page);let release;await page.route('**/auth/v1/signup*',async r=>{await new Promise(resolve=>release=resolve);await r.fulfill({status:400,headers:{'x-supabase-api-version':'2024-01-01','access-control-expose-headers':'X-Supabase-Api-Version'},json:{code:'weak_password',msg:'private'}});});await page.goto('/');await enter(page);await page.getByRole('dialog').getByRole('button',{name:'Create account',exact:true}).click();await expect.poll(()=>Boolean(release)).toBe(true);await page.getByRole('dialog').getByRole('button',{name:'Sign in',exact:true}).click();await expect(page.getByLabel('Password',{exact:true})).toHaveValue('');const late=page.waitForResponse('**/auth/v1/signup*');release();await (await late).finished();await page.evaluate(()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))));await expect(page.getByRole('dialog').getByRole('button',{name:'Sign in',exact:true})).toBeEnabled();await expect(page.getByRole('alert')).toHaveCount(0);await page.keyboard.press('Escape');await enter(page);await expect(page.getByRole('alert')).toHaveCount(0);
});
test('focus trap and short viewport retain accessible entry and confirmation',async({page})=>{
 await setup(page);await page.setViewportSize({width:320,height:375});await page.route('**/auth/v1/signup*',r=>r.fulfill({json:{...user,identities:[]}}));await page.goto('/');await enter(page);const dialog=page.getByRole('dialog');const close=dialog.getByRole('button',{name:'Close create account dialog'});await close.focus();await page.keyboard.press('Shift+Tab');await expect(dialog.getByRole('button',{name:'Sign in',exact:true})).toBeFocused();await page.keyboard.press('Tab');await expect(close).toBeFocused();await dialog.getByRole('button',{name:'Create account',exact:true}).scrollIntoViewIfNeeded();await page.screenshot({path:'/tmp/scribeswell-account-entry.png'});await dialog.getByRole('button',{name:'Create account',exact:true}).click();await expect(page.getByRole('button',{name:'Continue reading'})).toBeInViewport();await page.screenshot({path:'/tmp/scribeswell-account-confirmation.png'});expect(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth)).toBe(false);await page.getByRole('button',{name:'Continue reading'}).click();await expect(page.getByRole('dialog')).toHaveCount(0);
});
test('return helper drops duplicate malformed and oversized fields',async({page})=>{
 await setup(page);await page.goto('/?book=Gen&book=Exod&chapter=999&verse=01&compareBook='+('x'.repeat(1000))+'&compareChapter=2&compareVerse=176&redirect_to=https://evil.invalid#secret');expect(await page.evaluate(async()=>{const {publicAccountReturn}=await import('/src/lib/account-entry.ts');return publicAccountReturn();})).toBe('http://127.0.0.1:5182/?compareChapter=2&compareVerse=176');
});
test('thrown transport error settles without provider text or automatic retry',async({page})=>{
 await setup(page);await page.goto('/');await page.evaluate(async()=>{const {supabase}=await import('/src/lib/supabase.ts');supabase.auth.signUp=async()=>{throw new Error('private transport payload');};});await enter(page);await page.getByRole('dialog').getByRole('button',{name:'Create account',exact:true}).click();await expect(page.getByRole('alert')).toContainText('Check your connection');await expect(page.getByRole('alert')).not.toContainText('private');await expect(page.getByRole('dialog').getByRole('button',{name:'Create account',exact:true})).toBeEnabled();
});
test('valid provider signup callback uses the existing session owner',async({page})=>{
 await setup(page);await page.route('**/auth/v1/user*',r=>r.fulfill({json:user}));const token=[{alg:'HS256',typ:'JWT'},{sub:user.id,exp:Math.floor(Date.now()/1000)+3600},'fixture'].map(v=>Buffer.from(typeof v==='string'?v:JSON.stringify(v)).toString('base64url')).join('.');await page.goto('/?book=Gen&chapter=1#'+new URLSearchParams({access_token:token,refresh_token:'fixture-refresh',expires_in:'3600',token_type:'bearer',type:'signup'}));await expect(page.getByRole('button',{name:'Sign out',exact:true})).toBeVisible();await expect(page.getByRole('list',{name:'Verses'})).toBeVisible();await expect(page.getByRole('alert')).toHaveCount(0);
});
test('provider requests use a fifteen second network bound without automatic retry',async({page})=>{
 await setup(page);await page.goto('/');await page.evaluate(()=>{window.accountCalls=0;const original=window.fetch;window.fetch=(input,init)=>{if(String(input).includes('/auth/v1/signup')){window.accountCalls++;window.accountSignal=init.signal;return new Promise((resolve,reject)=>init.signal.addEventListener('abort',()=>reject(init.signal.reason)));}return original(input,init);};});await enter(page);const started=Date.now();await page.getByRole('dialog').getByRole('button',{name:'Create account',exact:true}).click();await expect(page.getByRole('alert')).toContainText('Check your connection',{timeout:18000});expect(Date.now()-started).toBeGreaterThanOrEqual(14500);expect(await page.evaluate(()=>window.accountCalls)).toBe(1);await expect(page.getByRole('dialog').getByRole('button',{name:'Create account',exact:true})).toBeEnabled();
});

test('closing and reopening during signup ignores late errors and secrets',async({page})=>{
 await setup(page);let release;await page.route('**/auth/v1/signup*',async r=>{await new Promise(resolve=>release=resolve);await r.fulfill({status:400,json:{error_code:'weak_password',msg:'private'}});});await page.goto('/');await enter(page);await page.getByRole('dialog').getByRole('button',{name:'Create account',exact:true}).click();await expect.poll(()=>Boolean(release)).toBe(true);await page.keyboard.press('Escape');await page.getByRole('banner').getByRole('button',{name:'Create account',exact:true}).click();await expect(page.getByLabel('Email',{exact:true})).toHaveValue('');await expect(page.getByLabel('Password',{exact:true})).toHaveValue('');const late=page.waitForResponse('**/auth/v1/signup*');release();await (await late).finished();await page.evaluate(()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))));await expect(page.getByRole('alert')).toHaveCount(0);await expect(page.getByRole('dialog').getByRole('button',{name:'Create account',exact:true})).toBeEnabled();
});

test('transport exception diagnostics and inline error exclude sensitive messages',async({page})=>{
 const diagnostics=[];page.on('console',message=>{if(message.type()==='error')diagnostics.push(message.text());});await setup(page);await page.goto('/');await page.evaluate(()=>{const original=window.fetch;window.fetch=(input,init)=>String(input).includes('/auth/v1/signup')?Promise.reject(new Error('synthetic-secret-password callback-token')):original(input,init);});await enter(page);await page.getByRole('dialog').getByRole('button',{name:'Create account',exact:true}).click();await expect(page.getByRole('alert')).toContainText('Check your connection');await expect(page.getByRole('alert')).not.toContainText('synthetic-secret');expect(diagnostics.join(' ')).not.toMatch(/synthetic-secret|callback-token/);
 // The current Auth SDK suppresses transport console logs; any emitted diagnostics must remain sanitized.
});
test('signed-out invalid callback offers sign-in and preserves public reading',async({page})=>{
 await setup(page);await page.goto('/?book=Gen&chapter=1#error=access_denied&error_code=otp_expired&error_description=synthetic-private-callback');const notice=page.getByRole('alert');await expect(notice).toContainText('invalid or has expired');await expect(notice).not.toContainText('synthetic-private');await expect(page).toHaveURL('http://127.0.0.1:5182/?book=Gen&chapter=1');await expect(page.getByRole('list',{name:'Verses'})).toBeVisible();await notice.getByRole('button',{name:'Sign in',exact:true}).click();await expect(page.getByRole('dialog',{name:'Sign in'})).toBeVisible();await expect(page.getByLabel('Email',{exact:true})).toHaveValue('');await page.keyboard.press('Escape');await expect(page.getByRole('list',{name:'Verses'})).toBeVisible();await expect(notice.getByRole('button',{name:'Sign in',exact:true})).toBeFocused();
});
for(const kind of ['incomplete','rejected','mixed'])test('callback recovery scrubs secrets and preserves prior session: '+kind,async({page})=>{
 const diagnostics=[];page.on('console',m=>diagnostics.push(m.text()));await setup(page);await page.goto('/');await page.evaluate(s=>localStorage.setItem('pts-auth',JSON.stringify(s)),session);await page.route('**/auth/v1/user*',r=>r.fulfill({status:401,json:{error_code:'session_not_found',msg:'synthetic-callback-secret'}}));
 const auth={access_token:'synthetic-callback-secret',refresh_token:'synthetic-refresh-secret',expires_in:'3600',expires_at:String(Math.floor(Date.now()/1000)+3600),token_type:'bearer',type:'signup',provider_token:'synthetic-provider-secret',provider_refresh_token:'synthetic-provider-refresh'};if(kind==='incomplete')delete auth.refresh_token;if(kind==='mixed')auth.error_description='synthetic-callback-secret';await page.goto('/?book=Gen&chapter=1&provider_token=synthetic-query-secret#'+new URLSearchParams(auth));await expect(page.getByRole('alert')).toContainText('invalid or has expired');await expect(page).toHaveURL('http://127.0.0.1:5182/?book=Gen&chapter=1');await expect(page.getByRole('button',{name:'Sign out',exact:true})).toBeVisible();expect(diagnostics.join(' ')).not.toMatch(/synthetic-callback-secret|synthetic-refresh-secret|synthetic-provider-secret|synthetic-query-secret/);
});
test('modal isolates header and reader through confirmation and restores interaction',async({page})=>{
 await setup(page);await page.goto('/');await page.evaluate(()=>{const marker=document.createElement('aside');marker.id='already-inert';marker.inert=true;document.body.append(marker);});await page.route('**/auth/v1/signup*',r=>r.fulfill({json:user}));await enter(page);await expect.poll(()=>page.getByRole('banner').getByRole('button',{name:'Sign in',exact:true,includeHidden:true}).first().evaluate(el=>Boolean(el.closest('[inert]')))).toBe(true);expect(await page.locator('main').evaluate(el=>el.inert)).toBe(true);await page.getByRole('dialog').getByRole('button',{name:'Create account',exact:true}).click();await expect(page.getByRole('heading',{name:'Check your email'})).toBeVisible();expect(await page.locator('main').evaluate(el=>el.inert)).toBe(true);await page.getByRole('button',{name:'Continue reading'}).click();expect(await page.locator('#already-inert').evaluate(el=>el.inert)).toBe(true);expect(await page.locator('main').evaluate(el=>el.inert)).toBe(false);await page.getByRole('button',{name:/Word:/}).click();await expect(page.getByRole('complementary',{name:'Word morphology'})).toBeVisible();
});
test('populated launcher and account controls fit 320px closed header',async({page})=>{
 await setup(page);await page.route('http://127.0.0.1:8001/**',r=>r.fulfill({json:[{id:'pts',name:'PtS',description:'Poetry',icon:'book-open',url:'http://localhost:5179',enabled:true}]}));await page.setViewportSize({width:320,height:568});await page.goto('/');await expect(page.getByRole('button',{name:'App launcher'})).toBeVisible();expect(await page.evaluate(()=>document.documentElement.scrollWidth)).toBeLessThanOrEqual(320);for(const name of ['App launcher','Create account','Sign in']){const b=await page.getByRole('banner').getByRole('button',{name,exact:true}).boundingBox();expect(b.x).toBeGreaterThanOrEqual(0);expect(b.x+b.width).toBeLessThanOrEqual(320);}const brand=await page.getByText("Scribes' Well",{exact:true}).boundingBox();const create=await page.getByRole('button',{name:'Create account',exact:true}).boundingBox();expect(brand.x+brand.width).toBeLessThanOrEqual(create.x);expect((await page.getByRole('banner').boundingBox()).height).toBe(57);await page.screenshot({path:'/tmp/scribeswell-header-320-populated.png'});await page.getByRole('button',{name:'Create account',exact:true}).click();await expect(page.getByRole('dialog')).toBeVisible();
});
test('held account request announces busy progress and settles',async({page})=>{
 await setup(page);let release;await page.route('**/auth/v1/signup*',async r=>{await new Promise(resolve=>release=resolve);await r.fulfill({status:400,json:{error_code:'signup_disabled',msg:'unavailable'}});});await page.goto('/');await enter(page);await page.getByRole('dialog').getByRole('button',{name:'Create account',exact:true}).click();await expect.poll(()=>Boolean(release)).toBe(true);await expect(page.locator('form')).toHaveAttribute('aria-busy','true');await expect(page.getByRole('status')).toContainText('Requesting account');release();await expect(page.locator('form')).toHaveAttribute('aria-busy','false');await expect(page.getByRole('alert')).toBeVisible();await expect(page.getByRole('status')).toHaveCount(0);
});
for(const action of ['close','switch'])test('late successful signup establishes session after '+action,async({page})=>{
 await setup(page);let release;await page.route('**/auth/v1/signup*',async r=>{await new Promise(resolve=>release=resolve);await r.fulfill({json:session});});await page.goto('/');await enter(page);await page.getByRole('dialog').getByRole('button',{name:'Create account',exact:true}).click();await expect.poll(()=>Boolean(release)).toBe(true);if(action==='close'){await page.keyboard.press('Escape');await page.getByRole('button',{name:'Create account',exact:true}).click();await expect(page.getByLabel('Email',{exact:true})).toHaveValue('');}else await page.getByRole('dialog').getByRole('button',{name:'Sign in',exact:true}).click();await expect(page.getByLabel('Password',{exact:true})).toHaveValue('');release();await expect(page.getByRole('button',{name:'Sign out',exact:true})).toBeVisible();await expect(page.getByRole('dialog')).toHaveCount(0);expect(await page.evaluate(()=>JSON.parse(localStorage.getItem('pts-auth')).user.id)).toBe(user.id);await expect(page.getByRole('list',{name:'Verses'})).toBeVisible();
});
test('rejected startup callback never restores a concurrently signed-out session',async({context,page})=>{
 await setup(page);await page.goto('/');await page.evaluate(s=>localStorage.setItem('pts-auth',JSON.stringify(s)),session);const other=await context.newPage();await setup(other);await other.route('**/auth/v1/logout*',r=>r.fulfill({status:204}));await other.goto('/');await expect(other.getByRole('button',{name:'Sign out',exact:true})).toBeVisible();let release;await page.route('**/auth/v1/user*',async r=>{await new Promise(resolve=>release=resolve);await r.fulfill({status:401,json:{error_code:'session_not_found',msg:'synthetic-private-rejection'}});});await page.goto('/?book=Gen&chapter=1#'+new URLSearchParams({access_token:'synthetic-rejected',refresh_token:'synthetic-refresh',expires_in:'3600',token_type:'bearer',type:'signup'}));await expect.poll(()=>Boolean(release)).toBe(true);await other.getByRole('button',{name:'Sign out',exact:true}).click();await expect(other.getByRole('banner').getByRole('button',{name:'Create account',exact:true})).toBeVisible();release();await expect(page.getByRole('alert')).toContainText('invalid or has expired');await expect(page.getByRole('button',{name:'Sign out',exact:true})).toHaveCount(0);expect(await page.evaluate(()=>localStorage.getItem('pts-auth'))).toBeNull();await expect(page.getByRole('list',{name:'Verses'})).toBeVisible();
});
test('ordinary user rejection after callback initialization keeps SDK session semantics',async({page})=>{
 await setup(page);await page.goto('/');await page.evaluate(s=>localStorage.setItem('pts-auth',JSON.stringify(s)),session);await page.route('**/auth/v1/user*',r=>r.fulfill({status:401,json:{error_code:'session_not_found',msg:'synthetic-private-rejection'}}));await page.goto('/?book=Gen&chapter=1#'+new URLSearchParams({access_token:'synthetic-rejected',refresh_token:'synthetic-refresh',expires_in:'3600',token_type:'bearer',type:'signup'}));await expect(page.getByRole('alert')).toContainText('invalid or has expired');await expect(page.getByRole('button',{name:'Sign out',exact:true})).toBeVisible();await page.evaluate(async()=>{const {supabase}=await import('/src/lib/supabase.ts');await supabase.auth.getUser();});await expect(page.getByRole('button',{name:'Sign out',exact:true})).toHaveCount(0);expect(await page.evaluate(()=>localStorage.getItem('pts-auth'))).toBeNull();
});

test('review: signup retains a complete public reader arrangement and strips private destinations', async ({page}) => {
  await setup(page);
  await page.goto('/');
  const reader = await page.evaluate(async () => {
    const {makeReference, chapterReference} = await import('/src/lib/passage-references.ts');
    return {v: 1, panes: [
      {ref: makeReference('Gen', {kind: 'verse_range', start: {chapter: 1, verse: 2}, end: {chapter: 2, verse: 3}})},
      {ref: chapterReference('Exod', 2)},
    ], active: 1};
  });
  const query = new URLSearchParams({
    reader: JSON.stringify(reader), book: 'Mal', chapter: '4',
    study_id: 'private-study', note_id: 'private-note',
    return: 'https://evil.invalid', redirect_to: 'https://evil.invalid',
  });
  await page.goto('/?' + query + '#private-fragment');
  const requests = [];
  await page.route('**/auth/v1/signup*', route => {
    requests.push(route.request().url());
    return route.fulfill({json: {...user, identities: []}});
  });
  await enter(page);
  await page.getByRole('dialog').getByRole('button', {name: 'Create account', exact: true}).click();
  await expect(page.getByRole('heading', {name: 'Check your email'})).toBeVisible();
  expect(requests).toHaveLength(1);
  const destination = new URL(new URL(requests[0]).searchParams.get('redirect_to'));
  expect(destination.origin + destination.pathname).toBe('http://127.0.0.1:5182/');
  expect([...destination.searchParams.keys()]).toEqual(['reader']);
  expect(JSON.parse(destination.searchParams.get('reader'))).toEqual(reader);
  expect(destination.hash).toBe('');
});

test('review: invalid supplied reader never blends legacy fields into account return', async ({page}) => {
  await setup(page);
  await page.goto('/');
  const results = await page.evaluate(async () => {
    const {publicAccountReturn} = await import('/src/lib/account-entry.ts');
    const {chapterReference} = await import('/src/lib/passage-references.ts');
    const valid = {v: 1, panes: [{ref: chapterReference('Gen', 1)}], active: 0};
    const values = [
      'reader=%7B%7D',
      new URLSearchParams({reader: JSON.stringify({...valid, v: 2})}).toString(),
      new URLSearchParams({reader: JSON.stringify({...valid, private: true})}).toString(),
      new URLSearchParams({reader: 'x'.repeat(5000)}).toString(),
      new URLSearchParams([['reader', JSON.stringify(valid)], ['reader', JSON.stringify(valid)]]).toString(),
    ];
    return values.map(query => {
      history.replaceState(history.state, '', '/?' + query + '&book=Gen&chapter=1&return=https://evil.invalid#private');
      return publicAccountReturn();
    });
  });
  expect(results).toEqual(Array(5).fill('http://127.0.0.1:5182/'));
});

test('P10 callback projection is pure and preserves unrelated raw query when only the fragment needs filtering',async({page})=>{
 await setup(page);await page.goto('/');
 const result=await page.evaluate(async()=>{
  const {projectAccountCallback}=await import('/src/lib/account-entry.ts');
  const raw='?reader=%7b%7d&foreign=a%20b&foreign=%2f&flag&empty=&other=%7e';
  const callbacks=new URLSearchParams({error:'synthetic-error',error_code:'synthetic-code',error_description:'synthetic-description',code:'synthetic-auth-code',access_token:'synthetic-access',refresh_token:'synthetic-refresh',expires_in:'3600',expires_at:'123456',token_type:'bearer',type:'signup',provider_token:'synthetic-provider',provider_refresh_token:'synthetic-provider-refresh',fragmentForeign:'kept'});
  const input=new URL(location.origin+'/'+raw+'#'+callbacks),original=input.href,native=location.href,state=JSON.stringify(history.state);
  const projected=projectAccountCallback(input);
  const queryInput=new URL(location.origin+'/?'+callbacks),queryProjected=projectAccountCallback(queryInput);
  return {search:projected.search,fragmentKeys:[...new URLSearchParams(projected.hash.slice(1)).keys()],queryKeys:[...queryProjected.searchParams.keys()],inputUnchanged:input.href===original,cloned:input!==projected,nativeUnchanged:location.href===native,stateUnchanged:JSON.stringify(history.state)===state};
 });
 expect(result).toEqual({search:'?reader=%7b%7d&foreign=a%20b&foreign=%2f&flag&empty=&other=%7e',fragmentKeys:['fragmentForeign'],queryKeys:['fragmentForeign'],inputUnchanged:true,cloned:true,nativeUnchanged:true,stateUnchanged:true});
});
