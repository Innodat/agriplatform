// Actual UI registration, local captured mail and provider callbacks throughout.
const {test,expect}=require('@playwright/test');
const {safeScenario}=require('./studies-owner-reporter.cjs');
const {credentialInspection}=require('./studies-owner-privacy.cjs');
const fs=require('fs'),path=require('path');
const proof=path.dirname(process.env.SCRIBESWELL_SIGNUP_FIXTURE);
const fixture=JSON.parse(fs.readFileSync(process.env.SCRIBESWELL_SIGNUP_FIXTURE,'utf8'));
function write(name,value){fs.writeFileSync(path.join(proof,name),JSON.stringify(value),{flag:'wx',mode:0o600});}
function stage(name){fs.appendFileSync(path.join(proof,'signup-browser-stages.jsonl'),JSON.stringify({stage:name})+'\n',{mode:0o600});}
async function checkpoint(name){
 stage(name);write('signup-'+name+'-check.json',{ready:true});
 const deadline=Date.now()+(name==='expiry-ready'?150000:30000);
 while(!fs.existsSync(path.join(proof,'signup-'+name+'-observed.json'))){if(Date.now()>deadline)throw Error('Independent signup observation unavailable');await new Promise(resolve=>setTimeout(resolve,50));}
}
async function session(page){return page.evaluate(async()=>{const {supabase}=await import('/src/lib/supabase.ts');return (await supabase.auth.getSession()).data.session!==null;});}
async function request(page,route){
 return page.evaluate(async route=>{
  const {supabase}=await import('/src/lib/supabase.ts');const {data}=await supabase.auth.getSession();
  const response=await fetch(route,{headers:data.session?{Authorization:'Bearer '+data.session.access_token}:{}});
  return {status:response.status,body:await response.json()};
 },route);
}
async function publicReader(page){await expect(page.getByText('בְּרֵאשִׁית',{exact:true}).first()).toBeVisible();}
async function signup(page,account){
 await page.goto('/');await publicReader(page);
 await page.getByRole('button',{name:'Create account',exact:true}).click();
 const dialog=page.getByRole('dialog',{name:'Create account',exact:true});
 await dialog.getByLabel('Email',{exact:true}).fill(account.email);await dialog.getByLabel('Password',{exact:true}).fill(account.password);
 // Exercise the approved standalone root callback. Keep only public reader state
 // and avoid using provider URLs or any private return metadata as input.
 await page.evaluate(()=>history.replaceState(history.state,'','/'));
 const reply=page.waitForResponse(response=>new URL(response.url()).pathname==='/auth/v1/signup'&&response.request().method()==='POST');
 await dialog.getByRole('button',{name:'Create account',exact:true}).click();
 expect((await reply).status()).toBe(200);
 await expect(page.getByRole('heading',{name:'Check your email',exact:true})).toBeVisible();
 await expect(page.getByRole('status').filter({hasText:'If this address can be registered, check your email for a confirmation link.'})).toBeVisible();
 expect(await session(page)).toBe(false);
 await page.getByRole('button',{name:'Continue reading',exact:true}).click();
 await expect(page.getByRole('button',{name:'Sign in',exact:true})).toBeVisible();
 expect((await request(page,'/api/studies')).status).toBe(401);await publicReader(page);
}
async function callback(page,link,accepted){
 const statuses=[];
 page.on('response',response=>{if(new URL(response.url()).pathname==='/auth/v1/verify')statuses.push(response.status());});
 try{await page.goto(link);}catch{throw Error('Provider signup callback navigation failed');}
 if(accepted){await expect(page.getByRole('button',{name:'Sign out',exact:true})).toBeVisible();expect(await session(page)).toBe(true);}
 else{
  await expect(page.getByText(/This confirmation link is invalid/)).toBeVisible();
  await expect(page.getByRole('button',{name:'Sign in',exact:true}).first()).toBeVisible();
  expect(await session(page)).toBe(false);expect((await request(page,'/api/studies')).status).toBe(401);
 }
 expect(statuses.length).toBeGreaterThan(0);
 expect(await page.evaluate(async()=>{const {hasAccountCallback}=await import('/src/lib/account-entry.ts');return hasAccountCallback();})).toBe(false);
 await publicReader(page);
}

test('real standalone signup confirmation explicit enrollment consumed and elapsed expired links',safeScenario(async({browser,page})=>{
 const privacy=credentialInspection([fixture.service_key_sentinel,fixture.provider_service_sentinel]);privacy.inspect(page.context());
 stage('valid-ui-signup');await signup(page,fixture.valid);await checkpoint('valid-created');
 stage('unconfirmed-ui-login');await page.getByRole('button',{name:'Sign in',exact:true}).click();
 const signIn=page.getByRole('dialog',{name:'Sign in',exact:true});
 await signIn.getByLabel('Email',{exact:true}).fill(fixture.valid.email);await signIn.getByLabel('Password',{exact:true}).fill(fixture.valid.password);
 const deniedReply=page.waitForResponse(response=>new URL(response.url()).pathname==='/auth/v1/token'&&response.request().method()==='POST');
 await signIn.getByRole('button',{name:'Sign in',exact:true}).click();
 const denied=await deniedReply;expect(denied.status()).toBe(400);expect((await denied.json()).code).toBe('email_not_confirmed');
 await expect(signIn.getByRole('alert')).toHaveText('Confirm your email using your confirmation link, then sign in.');
 expect(await session(page)).toBe(false);await signIn.getByRole('button',{name:'Close sign in dialog',exact:true}).click();
 await checkpoint('valid-unconfirmed');
 const valid=JSON.parse(fs.readFileSync(path.join(proof,'valid-confirmation-private.json'),'utf8'));
 stage('valid-mail-confirmation');await callback(page,valid.link,true);
 const before=await request(page,'/api/studies');expect(before.status).toBe(503);expect(before.body.code).toBe('studies_access_unavailable');
 await checkpoint('valid-confirmed');
 stage('explicit-ui-enrollment');await page.getByRole('button',{name:'Studies',exact:true}).click();
 let createRequests=0;page.on('request',request=>{if(new URL(request.url()).pathname==='/api/studies'&&request.method()==='POST')createRequests++;});
 const enrolledReply=page.waitForResponse(response=>new URL(response.url()).pathname==='/api/studies/enrollment'&&response.request().method()==='POST');
 await page.getByRole('button',{name:'Start a study',exact:true}).click();
 const enrolled=await enrolledReply;expect(enrolled.status()).toBe(200);const acknowledgment=await enrolled.json();expect(acknowledgment.result.disposition).toBe('created');
 await expect(page.getByLabel('Study title (optional)',{exact:true})).toBeVisible();expect(createRequests).toBe(0);
 const current=await request(page,'/api/studies');expect(current.status).toBe(200);expect(current.body.items).toEqual([]);
 write('signup-enrollment-private.json',{account:acknowledgment.result.account_id,actor:acknowledgment.result.actor_id,enrollment:acknowledgment.operation_id});
 await checkpoint('valid-enrolled');
 stage('separate-ui-study-creation');await page.getByLabel('Study title (optional)',{exact:true}).fill('Synthetic signup study');
 const createdReply=page.waitForResponse(response=>new URL(response.url()).pathname==='/api/studies'&&response.request().method()==='POST');
 await page.getByRole('button',{name:'Create study',exact:true}).click();
 const created=await createdReply;expect(created.status()).toBe(200);const study=await created.json();expect(createRequests).toBe(1);
 write('signup-study-private.json',{study:study.study_id,operation:study.operation_id});await checkpoint('valid-study-created');
 stage('consumed-mail-fresh-context');const reused=await browser.newContext();privacy.inspect(reused);await callback(await reused.newPage(),valid.link,false);await checkpoint('reused-rejected');await reused.close();
 stage('expiry-ui-signup');const expired=await browser.newContext();privacy.inspect(expired);const expiredPage=await expired.newPage();await signup(expiredPage,fixture.expired);await checkpoint('expired-created');
 stage('actual-provider-expiry-wait');await checkpoint('expiry-ready');
 const expiredLink=JSON.parse(fs.readFileSync(path.join(proof,'expired-confirmation-private.json'),'utf8'));
 // A fresh browser context proves the expired link supplies no session even
 // without any state established by signup or a prior provider callback.
 const fresh=await browser.newContext();privacy.inspect(fresh);await callback(await fresh.newPage(),expiredLink.link,false);await checkpoint('expired-rejected');
 const inspection=await privacy.settle();await fresh.close();await expired.close();
 write('signup-result.json',{ui_signup:true,unconfirmed_login_denied:true,confirmed_session:true,explicit_enrollment:true,separate_create:true,reused_link_denied:true,expired_link_denied:true,credential_inspection:inspection});
}));
