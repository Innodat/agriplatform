const {test,expect}=require('@playwright/test');
const org='11111111-1111-1111-1111-111111111111';
const actor='33333333-3333-3333-3333-333333333333';
const user={id:actor,email:'reader@example.invalid',aud:'authenticated',app_metadata:{},user_metadata:{}};
const token=[{alg:'HS256',typ:'JWT'},{sub:actor,exp:Math.floor(Date.now()/1000)+3600},'fixture'].map(v=>Buffer.from(typeof v==='string'?v:JSON.stringify(v)).toString('base64url')).join('.');
const session={access_token:token,refresh_token:'fixture-refresh',expires_in:3600,token_type:'bearer',user};
async function setup(page){
 let reads=0;
 await page.route('**/auth/v1/user',r=>r.fulfill({json:user}));
 await page.route('**/auth/v1/logout*',r=>r.fulfill({status:204}));
 await page.route('http://127.0.0.1:8001/**',r=>r.fulfill({json:{apps:[],context:{org_id:org,member_id:1,roles:[]}}}));
 await page.route('http://127.0.0.1:8010/**',r=>{reads++;return r.fulfill({json:{schema_version:'1',poems:[],sources:[],rights:[],witnesses:[],source_documents:[],total:0,collection_total:312,filters:{},citations:{}}});});
 return ()=>reads;
}
function callback(type){return '/#'+new URLSearchParams({access_token:token,refresh_token:'fixture-refresh',expires_in:'3600',token_type:'bearer',type});}
test('email login retries safely and preserves same-user return context',async({page})=>{
 await setup(page);let attempts=0;
 await page.route('**/auth/v1/token*',r=>{attempts++;return r.fulfill(attempts===1?{status:400,headers:{'x-supabase-api-version':'2024-01-01','access-control-expose-headers':'x-supabase-api-version'},json:{code:'invalid_credentials',msg:'SECRET RAW ERROR'}}:{json:session});});
 await page.goto('/?org='+org+'&availability=checked');
 await expect(page.getByRole('button',{name:'Continue with Microsoft'})).toHaveCount(0);
 await expect(page.getByRole('button',{name:/sign up|register/i})).toHaveCount(0);
 await page.getByLabel('Email', {exact:true}).fill(user.email);
 await page.getByLabel('Password',{exact:true}).fill('fixture-password');
 await page.getByRole('button',{name:'Sign in',exact:true}).click();
 await expect(page.getByRole('alert')).toContainText('Check your email and password');
 await expect(page.locator('body')).not.toContainText('SECRET RAW ERROR');
 await page.getByRole('button',{name:'Sign in',exact:true}).click();
 await expect(page.getByRole('button',{name:'Sign out',exact:true})).toBeVisible();
 await expect(page).toHaveURL(/availability=checked/);
});
test('reset email has neutral confirmation and disables repeated submission',async({page})=>{
 await setup(page);let release;
 await page.route('**/auth/v1/recover*',async r=>{await new Promise(resolve=>release=resolve);await r.fulfill({json:{}});});
 await page.goto('/');await page.getByRole('button',{name:'Forgot password?'}).click();
 await page.getByLabel('Email',{exact:true}).fill(user.email);
 await page.getByRole('button',{name:'Send reset link'}).click();
 await expect(page.getByRole('button',{name:'Sending…'})).toBeDisabled();
 await expect.poll(()=>Boolean(release)).toBe(true);release();
 await expect(page.getByRole('status')).toContainText('If an account exists');
 await page.getByRole('button',{name:'Back to sign in'}).click();
 await expect(page.getByLabel('Password',{exact:true})).toBeVisible();
});
for(const type of ['invite','recovery'])test(type+' requires confirmed password before reading, survives reload and failed update',async({page})=>{
 const reads=await setup(page);let updates=0;
 await page.route('**/auth/v1/user',r=>{if(r.request().method()==='PUT'){updates++;return r.fulfill(updates===1?{status:422,headers:{'x-supabase-api-version':'2024-01-01','access-control-expose-headers':'x-supabase-api-version'},json:{code:'weak_password',msg:'RAW password rule'}}:{json:user});}return r.fulfill({json:user});});
 await page.goto(callback(type));await expect(page.getByRole('heading',{name:type==='invite'?'Set your password':'Choose a new password'})).toBeVisible();
 expect(reads()).toBe(0);await page.reload();await expect(page.getByLabel('New password',{exact:true})).toBeVisible();
 await page.getByLabel('New password',{exact:true}).fill('first-password');await page.getByLabel('Confirm password',{exact:true}).fill('other-password');
 await page.getByRole('button',{name:'Save password'}).click();await expect(page.getByRole('alert')).toContainText('Passwords do not match');expect(updates).toBe(0);
 await page.getByLabel('Confirm password',{exact:true}).fill('first-password');await page.getByRole('button',{name:'Save password'}).click();
 await expect(page.getByRole('alert')).toContainText('stronger password');expect(reads()).toBe(0);
 await page.getByLabel('New password',{exact:true}).fill('better-password');await page.getByLabel('Confirm password',{exact:true}).fill('better-password');await page.getByRole('button',{name:'Save password'}).click();
 await expect(page.getByText('0 of 312 records')).toBeVisible();await expect(page.getByLabel('New password',{exact:true})).toHaveCount(0);
});
test('expired callback does not update an existing session',async({page})=>{
 await setup(page);await page.addInitScript(s=>localStorage.setItem('pts-auth',JSON.stringify({...s,expires_at:Date.now()/1000+3600})),session);
 await page.goto('/#error=access_denied&error_code=otp_expired&error_description=PRIVATE&type=recovery');
 await expect(page.getByRole('alert')).toContainText('link is invalid or has expired');
 await expect(page.getByLabel('New password',{exact:true})).toHaveCount(0);
 await expect(page.locator('body')).not.toContainText('PRIVATE');
});

test('tokenless callback cannot start password setup for an older session',async({page})=>{
 await setup(page);await page.addInitScript(s=>localStorage.setItem('pts-auth',JSON.stringify({...s,expires_at:Date.now()/1000+3600})),session);
 await page.goto('/#type=invite&access_token=');await expect(page.getByText('0 of 312 records')).toBeVisible();await expect(page.getByLabel('New password',{exact:true})).toHaveCount(0);
});
test('failed logout is visible during password setup',async({page})=>{
 await setup(page);await page.route('**/auth/v1/logout*',r=>r.fulfill({status:400,json:{error_code:'unexpected_failure',msg:'PRIVATE'}}));
 await page.goto(callback('invite'));await expect(page.getByRole('heading',{name:'Set your password'})).toBeVisible();
 await page.getByRole('button',{name:'Sign out',exact:true}).click();await expect(page.getByRole('alert')).toContainText('could not sign you out');
});
test('password recovery restores same-user filters without including them in the email URL',async({page})=>{
 await setup(page);let redirect='';await page.addInitScript(actor=>sessionStorage.setItem('pts-last-user',actor),actor);
 await page.route('**/auth/v1/recover*',r=>{redirect=r.request().url();return r.fulfill({json:{}});});
 await page.goto('/?org='+org+'&availability=checked&search=fixture');await page.getByRole('button',{name:'Forgot password?'}).click();
 await page.getByLabel('Email',{exact:true}).fill(user.email);await page.getByRole('button',{name:'Send reset link'}).click();await expect(page.getByRole('status')).toContainText('If an account exists');
 expect(redirect).not.toContain('fixture');
 await page.goto(callback('recovery'));await expect(page.getByLabel('New password',{exact:true})).toBeVisible();
 await page.getByLabel('New password',{exact:true}).fill('new-password');await page.getByLabel('Confirm password',{exact:true}).fill('new-password');await page.getByRole('button',{name:'Save password'}).click();
 await expect(page.getByText('0 of 312 records')).toBeVisible();await expect(page).toHaveURL(/availability=checked/);await expect(page.getByLabel('Search title, poet, place, form or dialect')).toHaveValue('fixture');
});

test('Microsoft sign-in is opt-in and preserves the local return URL',async({page})=>{
 await setup(page);await page.goto('/?org='+org+'&availability=checked');
 if(process.env.PTS_TEST_MICROSOFT!=='true'){
  await expect(page.getByRole('button',{name:'Continue with Microsoft'})).toHaveCount(0);return;
 }
 await page.route('**/auth/v1/authorize*',r=>r.fulfill({contentType:'text/html',body:'<p>Configured provider</p>'}));
 await page.getByRole('button',{name:'Continue with Microsoft'}).click();
 await expect(page).toHaveURL(/\/auth\/v1\/authorize/);
 const callback=new URL(new URL(page.url()).searchParams.get('redirect_to'));
 expect(callback.origin).toBe('http://127.0.0.1:5181');expect(callback.searchParams.get('org')).toBe(org);expect(callback.searchParams.get('availability')).toBe('checked');
});
