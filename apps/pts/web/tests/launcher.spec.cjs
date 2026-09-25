const {test,expect}=require('@playwright/test');
const org='11111111-1111-1111-1111-111111111111';
async function setup(page){
 await page.addInitScript(()=>localStorage.setItem('pts-auth',JSON.stringify({access_token:'test-token',refresh_token:'test-refresh',expires_at:Date.now()/1000+3600,expires_in:3600,token_type:'bearer',user:{id:'33333333-3333-3333-3333-333333333333',email:'fixture@example.invalid',aud:'authenticated',app_metadata:{},user_metadata:{}}})));
 await page.route('**/auth/v1/**',r=>r.fulfill({json:{}}));
 await page.route('http://127.0.0.1:8001/**',r=>r.fulfill({json:{apps:[{id:'pts',name:'PtS',url:'http://localhost:5179',icon:'book-open',description:'Swahili Poetry: poems, sources and witnesses',enabled:true},{id:'scribeswell',name:'Scribeswell',url:'http://localhost:5174',icon:'book-open',description:'Hebrew Bible reader with morphological analysis',enabled:true}],context:{org_id:org,member_id:1,roles:[]}}}));
 await page.route('http://127.0.0.1:8010/**',r=>r.fulfill({json:{sources:[],rights:[],source_documents:[]}}));
 await page.goto('/?org='+org+'&view=sources');
}
test('launcher has readable styled app cards, current app and keyboard navigation',async({page})=>{
 await setup(page);const trigger=page.getByRole('button',{name:'App launcher',exact:true});
 await trigger.click();const menu=page.getByRole('menu',{name:'Available apps'});
 await expect(menu).toBeVisible();
 await expect(menu.getByText('Current app',{exact:true})).toBeVisible();
 const pts=menu.getByRole('menuitem',{name:'Open PtS',exact:true});const bible=menu.getByRole('menuitem',{name:'Open Scribeswell',exact:true});
 await expect(pts).toBeFocused();await page.keyboard.press('ArrowDown');await expect(bible).toBeFocused();
 await expect(bible).toHaveAttribute('href','http://localhost:5174');await expect(bible).toHaveAttribute('target','_blank');
 const styles=await menu.evaluate(el=>({shadow:getComputedStyle(el).boxShadow,width:el.getBoundingClientRect().width,right:el.getBoundingClientRect().right}));
 expect(styles.shadow).not.toBe('none');expect(styles.width).toBeGreaterThan(280);expect(styles.right).toBeLessThanOrEqual(await page.evaluate(()=>innerWidth));
 await page.screenshot({path:'/tmp/pts-launcher-'+test.info().project.name+'.png'});
 await page.keyboard.press('Escape');await expect(menu).toHaveCount(0);await expect(trigger).toBeFocused();
 await page.keyboard.press('ArrowDown');await expect(pts).toBeFocused();await page.keyboard.press('End');await expect(bible).toBeFocused();
 await page.keyboard.press('Tab');await expect(menu).toHaveCount(0);await expect(page.locator('.brand')).toBeFocused();
 await trigger.click();await page.keyboard.press('Shift+Tab');await expect(trigger).toBeFocused();await expect(menu).toHaveCount(0);
});
