const {test,expect}=require('@playwright/test');
const API=process.env.PUBLIC_API_ORIGIN||'https://api.scribeswell.com';
test('assembled artifact serves both SPAs, nested assets, direct reader navigation and external API',async({page,request})=>{
 const requests=[];
 await page.route(API+'/**',route=>{
  const url=route.request().url();requests.push(url);
  if(url.includes('/directory/'))return route.fulfill({json:[]});
  const book={id:1,osis_id:'Gen',name_en:'Genesis',name_he:'בראשית',testament:'OT',book_order:1,division:'torah'};
  return route.fulfill({json:url.endsWith('/books')?{data:[book],total:1}:url.endsWith('/verses')?{data:[],total:0}:{...book,chapters:[{id:1,chapter_num:1}]}});
 });
 await page.route('https://*.supabase.co/**',r=>r.fulfill({status:401,json:{error:'fixture-anonymous'}}));
 await page.goto('/');
 const rootAssets=await page.locator('script[src]').evaluateAll(nodes=>nodes.map(n=>n.getAttribute('src')));
 expect(rootAssets.length).toBeGreaterThan(0);expect(rootAssets.every(src=>src.startsWith('/assets/'))).toBe(true);
 await page.goto('/scribeswell/?book=Gen&chapter=1');
 await expect(page.getByRole('button',{name:/Navigate: Genesis/})).toBeVisible();
 const assets=await page.locator('script[src],link[rel="stylesheet"]').evaluateAll(nodes=>nodes.map(n=>n.getAttribute('src')||n.getAttribute('href')));
 expect(assets.length).toBeGreaterThan(1);expect(assets.every(src=>src.startsWith('/scribeswell/assets/'))).toBe(true);
 for(const src of [...rootAssets,...assets])expect((await request.get(src)).status()).toBe(200);
 expect(requests).toContain(API+'/scribeswell/api/bible/books');expect(requests.some(url=>url.includes('/chapters/1/verses'))).toBe(true);
 await page.reload();await expect(page.getByRole('button',{name:/Navigate: Genesis/})).toBeVisible();
 const fallback=await request.get('/scribeswell/direct-route-probe');expect(fallback.status()).toBe(200);expect(await fallback.text()).toContain('/scribeswell/assets/');
 expect(await (await request.get('/scribeswell/')).text()).not.toContain('/@vite/client');
});
