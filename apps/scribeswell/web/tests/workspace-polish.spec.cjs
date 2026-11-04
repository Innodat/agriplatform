const {test,expect}=require('@playwright/test');
async function setup(page){
 await page.route('**/directory/**',r=>r.fulfill({json:[]}));
 await page.route('http://127.0.0.1:8001/**',r=>r.fulfill({json:[]}));
 await page.route('**/api/bible/**',r=>{
  const path=new URL(r.request().url()).pathname;
  const book={id:23,osis_id:'Isa',name_en:'Isaiah',name_he:'ישעיהו',testament:'OT',book_order:23,division:'nevi_im'};
  return r.fulfill({json:path.endsWith('/books')?{data:[book],total:1}:path.endsWith('/verses')?{data:Array.from({length:20},(_,i)=>({id:i+1,verse_num:i+1,book_id:23,chapter_num:4,words:['וְהָיָה','בַּיּוֹם','הַהוּא','לְכָבוֹד','וּלְתִפְאָרֶת'].map((text,j)=>({id:i*5+j+1,position:j+1,surface_he:text,display_he:text,lemma_strong:null,morph_code:null}))})),total:20}:{...book,chapters:Array.from({length:66},(_,i)=>({id:i+1,chapter_num:i+1}))}});
 });
 await page.goto('/?book=Isa&chapter=4');
 await expect(page.locator('[data-reader-scroll][data-ready="true"]')).toBeVisible();
}
const tabs=page=>page.getByRole('tablist',{name:'Workspace tabs'}).getByRole('tab');
async function add(page){await page.getByRole('button',{name:'New workspace tab',exact:true}).click();await page.getByRole('dialog',{name:'Book and chapter selector'}).getByRole('button',{name:'Cancel',exact:true}).click();}
test('workspace chrome is compact with inline add and discreet rename',async({page},testInfo)=>{
 await setup(page);await add(page);
 await expect(tabs(page).first()).toHaveText('Isaiah ד');
 const rename=page.getByRole('button',{name:'Rename tab 2',exact:true});
 await expect(rename).toHaveText('');await expect(rename).toHaveAccessibleName('Rename tab 2');
 const tab=await tabs(page).last().boundingBox(),plus=await page.getByRole('button',{name:'New workspace tab',exact:true}).boundingBox();
 expect(Math.abs((tab.y+tab.height/2)-(plus.y+plus.height/2))).toBeLessThan(3);
 const tools=page.getByRole('navigation',{name:'Reader tools'}),focus=page.getByRole('button',{name:'Enter focus mode'});
 const tb=await tools.boundingBox(),fb=await focus.boundingBox();expect(Math.abs(tb.y+tb.height/2-fb.y-fb.height/2)).toBeLessThan(3);
 expect(await page.getByRole('button',{name:'Navigate: Isaiah, chapter 4. Open selector.'}).evaluate(el=>el.getBoundingClientRect().top)).toBeLessThan(205);
 await page.getByRole('button',{name:'Analysis',exact:true}).click();await expect(page.getByRole('button',{name:'Analysis',exact:true})).toHaveAttribute('aria-pressed','true');
 await page.getByRole('button',{name:'Analysis',exact:true}).click();await expect(page.getByRole('complementary',{name:'Study tools',exact:true})).toBeHidden();
 await rename.focus();await expect(rename).toHaveCSS('opacity','1');await rename.click();
 await page.getByLabel('Tab name',{exact:true}).fill('קריאה שלי');await page.getByRole('dialog',{name:'Rename workspace tab'}).getByRole('button',{name:'Save',exact:true}).click();
 await expect(tabs(page).last()).toHaveText('קריאה שלי');
 await rename.click();await page.getByRole('button',{name:'Reset name',exact:true}).click();await expect(tabs(page).last()).toHaveText('Isaiah ד');
 expect(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth)).toBe(false);
 if(process.env.WORKSPACE_POLISH_SCREENSHOTS){await page.mouse.move(0,0);await tabs(page).last().focus();await page.screenshot({path:`${process.env.WORKSPACE_POLISH_SCREENSHOTS}/scribeswell-workspace-${testInfo.project.name}.png`});}
});
test('overflow keeps add available and Hebrew range labels leave reference identity intact',async({page})=>{
 await setup(page);
 await page.getByRole('button',{name:/Navigate: Isaiah/}).click();await page.getByLabel('Passage reference').fill('Isaiah 15:2–16:3');await page.getByLabel('Passage reference').press('Enter');
 await expect(tabs(page).first()).toHaveText('Isaiah טו:ב–טז:ג');
 expect(JSON.parse(new URL(page.url()).searchParams.get('reader')).panes[0].ref.target).toEqual({kind:'verse_range',start:{chapter:15,verse:2},end:{chapter:16,verse:3}});
 for(let i=0;i<6;i++)await add(page);
 const plus=await page.getByRole('button',{name:'New workspace tab',exact:true}).boundingBox();expect(plus.x).toBeGreaterThanOrEqual(0);expect(plus.x+plus.width).toBeLessThanOrEqual(page.viewportSize().width);
 await tabs(page).last().focus();await page.keyboard.press('Home');await expect(tabs(page).first()).toBeFocused();
 expect(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth)).toBe(false);
});
test('selected passage uses Hebrew names and retains chapter colour while previewing',async({page},testInfo)=>{
 await setup(page);
 const trigger=page.getByRole('button',{name:'Navigate: Isaiah, chapter 4. Open selector.'});
 await expect(trigger).toHaveText('ישעיהו›ד');await expect(trigger).toHaveAccessibleName(/ישעיהו ד/);await trigger.click();
 const dialog=page.getByRole('dialog',{name:'Book and chapter selector'}),current=dialog.getByRole('button',{name:'Chapter 4 of Isaiah',exact:true}),candidate=dialog.getByRole('button',{name:'Chapter 5 of Isaiah',exact:true});
 await expect(dialog.getByRole('heading',{name:'ישעיהו',exact:true})).toBeVisible();
 await page.getByLabel('Passage reference').fill('');
 await expect(current).toHaveAttribute('aria-current','page');
 await expect(current).toHaveCSS('background-color','oklch(0.555 0.163 48.998)');
 await page.getByLabel('Passage reference').fill('Isaiah 5');
 await expect(current).toHaveCSS('background-color','oklch(0.555 0.163 48.998)');
 expect(await candidate.evaluate(el=>getComputedStyle(el).backgroundColor)).not.toBe(await current.evaluate(el=>getComputedStyle(el).backgroundColor));
 if(process.env.WORKSPACE_POLISH_SCREENSHOTS)await page.screenshot({path:`${process.env.WORKSPACE_POLISH_SCREENSHOTS}/scribeswell-selector-${testInfo.project.name}.png`});
 await candidate.click();await expect(trigger).toHaveCount(0);
 await expect(page.getByRole('button',{name:'Navigate: Isaiah, chapter 5. Open selector.'})).toHaveText('ישעיהו›ה');
});
test('selected book falls back to English when Hebrew is unavailable',async({page})=>{
 await setup(page);
 await page.route('**/api/bible/books',r=>r.fulfill({json:{data:[{id:23,osis_id:'Isa',name_en:'Isaiah',name_he:'',testament:'OT',book_order:23,division:'nevi_im'}],total:1}}));
 await page.reload();
 const trigger=page.getByRole('button',{name:'Navigate: Isaiah, chapter 4. Open selector.'});
 await expect(trigger).toHaveText('Isaiah›ד');await trigger.click();
 await expect(page.getByRole('dialog',{name:'Book and chapter selector'}).getByRole('heading',{name:'Isaiah',exact:true})).toBeVisible();
});
