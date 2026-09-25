const {test,expect}=require('@playwright/test');
const org='11111111-1111-1111-1111-111111111111';
const actor='33333333-3333-3333-3333-333333333333';
async function setup(page){
 await page.addInitScript(({actor})=>{localStorage.setItem('pts-auth',JSON.stringify({access_token:'test-token',refresh_token:'test-refresh',expires_at:Date.now()/1000+3600,expires_in:3600,token_type:'bearer',user:{id:actor,email:'fixture@example.invalid',aud:'authenticated',app_metadata:{},user_metadata:{}}}));window.open=url=>{window.openedDocument=url;return null;};},{actor});
 await page.route('**/auth/v1/**',r=>r.fulfill({json:{id:actor,email:'fixture@example.invalid'}}));
 await page.route('http://127.0.0.1:8001/**',r=>r.fulfill({json:{apps:[],context:{org_id:org,roles:[]}}}));
 let denied=false;const requests=[];
 await page.route('http://127.0.0.1:8010/**',r=>{
  const path=new URL(r.request().url()).pathname;requests.push(path);
  if(denied)return r.fulfill({status:403,json:{detail:{code:'access_denied'}}});
  if(path.startsWith('/api/documents/'))return r.fulfill({json:{status:'stored',url:'https://private.invalid/download',expires_in:300,document:{}}});
  if(path==='/api/sources')return r.fulfill({json:{sources:[{id:'S1',title:'Collected volume',rights_id:'R1',historical_context:'Historical description',document_id:'D1'},{id:'S2',title:'Uncollected lead',rights_id:'R2',document_id:'D1',completeness:'Incomplete scan',repository_url:'javascript:alert(1)'}],rights:[{id:'R1',assessment:'Conflicting licence notices',research_use:'Review required',source_document_copying:{status:'stored',copying_basis:'Preserve notices'}},{id:'R2',assessment:'No clearance recorded',source_document_copying:'Link only'}],source_documents:[{id:'D1',source_id:'S1',title:'Shared PDF',local_path:'sources/test.pdf',url:'https://source.invalid/volume.pdf',copying_basis:'Recorded copying basis'},{id:'D2',source_id:'S1',title:'HTML scan',local_path:'sources/source.html'},{id:'D3',title:'Rights reference',url:'https://reference.invalid/',status:'online_reference'}]}});
  return r.fulfill({json:{schema_version:'1',exported_at:'today',note:'',poems:[],witnesses:[],sources:[],rights:[],source_documents:[],total:0,collection_total:0,filters:{},citations:{}}});
 });
 return {requests,revoke:()=>{denied=true;}};
}
test('sources include leads, rights and shared documents with protected downloads',async({page})=>{
 const state=await setup(page);await page.goto('/?org='+org+'&view=sources&search=absent');
 await expect(page.getByRole('heading',{name:'Uncollected lead',exact:true})).toBeVisible();
 await expect(page.getByText('Historical description').first()).toBeVisible();
 await expect(page.getByText('Conflicting licence notices')).toBeVisible();
 await expect(page.getByText('Incomplete scan').first()).toBeVisible();
 await expect(page.getByText('Link only',{exact:true})).toBeVisible();
 await expect(page.getByRole('button',{name:'Download PDF',exact:true})).toHaveCount(2);
 await expect(page.getByRole('button',{name:'Download document (HTML)'})).toHaveCount(1);
 await expect(page.getByRole('link',{name:'Open online PDF'}).first()).toHaveAttribute('href','https://source.invalid/volume.pdf');
 expect(state.requests.every(p=>p==='/api/sources')).toBe(true);
 await expect(page.locator('a[href^="javascript:"]')).toHaveCount(0);
 await page.getByRole('button',{name:'Download PDF',exact:true}).last().click();
 await expect.poll(()=>page.evaluate(()=>window.openedDocument)).toBe('https://private.invalid/download');
 expect(state.requests).toContain('/api/documents/D1');
 expect(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth)).toBe(false);
 state.revoke();await page.getByRole('button',{name:'Download PDF',exact:true}).first().click();
 await expect(page.getByRole('alert')).toContainText('do not currently have access');
 await expect(page.getByRole('heading',{name:'Collected volume'})).toHaveCount(0);
});
test('source navigation preserves filters and Back; sign-out clears sources',async({page})=>{
 await setup(page);await page.goto('/?org='+org+'&search=absent');
 await page.getByRole('button',{name:'Sources',exact:true}).click();
 await expect(page.getByRole('heading',{name:'Collected volume'})).toBeVisible();
 await expect(page).toHaveURL(/view=sources/);
 await page.getByRole('button',{name:'Sources',exact:true}).click();
 await expect(page.getByRole('heading',{name:'Collected volume'})).toBeVisible();
 await page.goBack();await expect(page.getByLabel('Search title, poet, place, form or dialect')).toHaveValue('absent');
 await page.goForward();await expect(page.getByRole('heading',{name:'Collected volume'})).toBeVisible();
 await page.getByRole('button',{name:'Sign out',exact:true}).click();
 await expect(page.getByRole('heading',{name:'Collected volume'})).toHaveCount(0);
});

test('a late poem request cannot overwrite Sources with a stale error',async({page})=>{
 await setup(page);let release;
 await page.route('http://127.0.0.1:8010/api/poetry?*',async r=>{await new Promise(resolve=>release=resolve);await r.fallback();});
 await page.goto('/?org='+org);
 await expect.poll(()=>Boolean(release)).toBe(true);
 await page.getByRole('button',{name:'Sources',exact:true}).click();
 await expect(page.getByRole('heading',{name:'Collected volume'})).toBeVisible();
 release();await page.waitForTimeout(150);
 await expect(page.getByRole('alert')).toHaveCount(0);
});
