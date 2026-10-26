# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: four-passage.spec.cjs >> layout clamps retain intended anchor while a subsequent user movement replaces it
- Location: tests/four-passage.spec.cjs:341:1

# Error details

```
Error: expect(received).toBe(expected) // Object.is equality

Expected: 120
Received: 921

Call Log:
- Timeout 5000ms exceeded while waiting on the predicate
```

# Page snapshot

```yaml
- generic [ref=e3]:
  - banner [ref=e5]:
    - generic [ref=e6]:
      - generic [ref=e7]: Scribes' Well
      - generic [ref=e13]:
        - button "Create account" [ref=e14]
        - button "Sign in" [ref=e15]
  - main [ref=e19]:
    - generic [ref=e20]:
      - generic [ref=e21]:
        - button "Add reader pane" [ref=e22]
        - button "Enter focus mode" [ref=e25]: Focus mode
      - navigation "Reader tools" [ref=e31]:
        - button "Studies" [ref=e32]
        - button "Analysis" [ref=e33]
      - region "Passage 1" [ref=e36]:
        - generic [ref=e37]:
          - button "Previous chapter" [disabled] [ref=e38]
          - 'button "Navigate: Genesis, chapter 1. Open selector." [ref=e42]': Genesis א
          - button "Next chapter" [ref=e45]
        - region "Chapter text" [ref=e48]:
          - list "Verses" [ref=e49]:
            - listitem [ref=e50]:
              - generic "Verse 1" [ref=e51]: "1"
              - paragraph [ref=e52]:
                - 'button "Word: אב (H1)" [ref=e53] [cursor=pointer]': אב
            - listitem [ref=e54]:
              - generic "Verse 2" [ref=e55]: "2"
              - paragraph [ref=e56]:
                - 'button "Word: אב (H1)" [ref=e57] [cursor=pointer]': אב
            - listitem [ref=e58]:
              - generic "Verse 3" [ref=e59]: "3"
              - paragraph [ref=e60]:
                - 'button "Word: אב (H1)" [ref=e61] [cursor=pointer]': אב
            - listitem [ref=e62]:
              - generic "Verse 4" [ref=e63]: "4"
              - paragraph [ref=e64]:
                - 'button "Word: אב (H1)" [ref=e65] [cursor=pointer]': אב
            - listitem [ref=e66]:
              - generic "Verse 5" [ref=e67]: "5"
              - paragraph [ref=e68]:
                - 'button "Word: אב (H1)" [ref=e69] [cursor=pointer]': אב
            - listitem [ref=e70]:
              - generic "Verse 6" [ref=e71]: "6"
              - paragraph [ref=e72]:
                - 'button "Word: אב (H1)" [ref=e73] [cursor=pointer]': אב
            - listitem [ref=e74]:
              - generic "Verse 7" [ref=e75]: "7"
              - paragraph [ref=e76]:
                - 'button "Word: אב (H1)" [ref=e77] [cursor=pointer]': אב
            - listitem [ref=e78]:
              - generic "Verse 8" [ref=e79]: "8"
              - paragraph [ref=e80]:
                - 'button "Word: אב (H1)" [ref=e81] [cursor=pointer]': אב
            - listitem [ref=e82]:
              - generic "Verse 9" [ref=e83]: "9"
              - paragraph [ref=e84]:
                - 'button "Word: אב (H1)" [ref=e85] [cursor=pointer]': אב
            - listitem [ref=e86]:
              - generic "Verse 10" [ref=e87]: "10"
              - paragraph [ref=e88]:
                - 'button "Word: אב (H1)" [ref=e89] [cursor=pointer]': אב
            - listitem [ref=e90]:
              - generic "Verse 11" [ref=e91]: "11"
              - paragraph [ref=e92]:
                - 'button "Word: אב (H1)" [ref=e93] [cursor=pointer]': אב
            - listitem [ref=e94]:
              - generic "Verse 12" [ref=e95]: "12"
              - paragraph [ref=e96]:
                - 'button "Word: אב (H1)" [ref=e97] [cursor=pointer]': אב
            - listitem [ref=e98]:
              - generic "Verse 13" [ref=e99]: "13"
              - paragraph [ref=e100]:
                - 'button "Word: אב (H1)" [ref=e101] [cursor=pointer]': אב
            - listitem [ref=e102]:
              - generic "Verse 14" [ref=e103]: "14"
              - paragraph [ref=e104]:
                - 'button "Word: אב (H1)" [ref=e105] [cursor=pointer]': אב
            - listitem [ref=e106]:
              - generic "Verse 15" [ref=e107]: "15"
              - paragraph [ref=e108]:
                - 'button "Word: אב (H1)" [ref=e109] [cursor=pointer]': אב
            - listitem [ref=e110]:
              - generic "Verse 16" [ref=e111]: "16"
              - paragraph [ref=e112]:
                - 'button "Word: אב (H1)" [ref=e113] [cursor=pointer]': אב
            - listitem [ref=e114]:
              - generic "Verse 17" [ref=e115]: "17"
              - paragraph [ref=e116]:
                - 'button "Word: אב (H1)" [ref=e117] [cursor=pointer]': אב
            - listitem [ref=e118]:
              - generic "Verse 18" [ref=e119]: "18"
              - paragraph [ref=e120]:
                - 'button "Word: אב (H1)" [ref=e121] [cursor=pointer]': אב
            - listitem [ref=e122]:
              - generic "Verse 19" [ref=e123]: "19"
              - paragraph [ref=e124]:
                - 'button "Word: אב (H1)" [ref=e125] [cursor=pointer]': אב
            - listitem [ref=e126]:
              - generic "Verse 20" [ref=e127]: "20"
              - paragraph [ref=e128]:
                - 'button "Word: אב (H1)" [ref=e129] [cursor=pointer]': אב
            - listitem [ref=e130]:
              - generic "Verse 21" [ref=e131]: "21"
              - paragraph [ref=e132]:
                - 'button "Word: אב (H1)" [ref=e133] [cursor=pointer]': אב
            - listitem [ref=e134]:
              - generic "Verse 22" [ref=e135]: "22"
              - paragraph [ref=e136]:
                - 'button "Word: אב (H1)" [ref=e137] [cursor=pointer]': אב
            - listitem [ref=e138]:
              - generic "Verse 23" [ref=e139]: "23"
              - paragraph [ref=e140]:
                - 'button "Word: אב (H1)" [ref=e141] [cursor=pointer]': אב
            - listitem [ref=e142]:
              - generic "Verse 24" [ref=e143]: "24"
              - paragraph [ref=e144]:
                - 'button "Word: אב (H1)" [ref=e145] [cursor=pointer]': אב
            - listitem [ref=e146]:
              - generic "Verse 25" [ref=e147]: "25"
              - paragraph [ref=e148]:
                - 'button "Word: אב (H1)" [ref=e149] [cursor=pointer]': אב
            - listitem [ref=e150]:
              - generic "Verse 26" [ref=e151]: "26"
              - paragraph [ref=e152]:
                - 'button "Word: אב (H1)" [ref=e153] [cursor=pointer]': אב
            - listitem [ref=e154]:
              - generic "Verse 27" [ref=e155]: "27"
              - paragraph [ref=e156]:
                - 'button "Word: אב (H1)" [ref=e157] [cursor=pointer]': אב
            - listitem [ref=e158]:
              - generic "Verse 28" [ref=e159]: "28"
              - paragraph [ref=e160]:
                - 'button "Word: אב (H1)" [ref=e161] [cursor=pointer]': אב
            - listitem [ref=e162]:
              - generic "Verse 29" [ref=e163]: "29"
              - paragraph [ref=e164]:
                - 'button "Word: אב (H1)" [ref=e165] [cursor=pointer]': אב
            - listitem [ref=e166]:
              - generic "Verse 30" [ref=e167]: "30"
              - paragraph [ref=e168]:
                - 'button "Word: אב (H1)" [ref=e169] [cursor=pointer]': אב
            - listitem [ref=e170]:
              - generic "Verse 31" [ref=e171]: "31"
              - paragraph [ref=e172]:
                - 'button "Word: אב (H1)" [ref=e173] [cursor=pointer]': אב
```

# Test source

```ts
  272 |       large: m.parseReaderURL(new URLSearchParams({
  273 |         reader: ' '.repeat(4097)
  274 |       })).invalid,
  275 |       newPrecedence: m.parseReaderURL(new URLSearchParams(m.readerSearch('?book=Exod', [ref], 0))).refs[0].book_id
  276 |     };
  277 |   });
  278 |   expect(r).toEqual({
  279 |     valid: true,
  280 |     extra: false,
  281 |     offset: false,
  282 |     wrong: false,
  283 |     large: true,
  284 |     newPrecedence: 'Gen'
  285 |   });
  286 | });
  287 | test('reduced-height four pane layout offers named switcher and no viewport overflow', async ({
  288 |   page
  289 | }) => {
  290 |   await setup(page);
  291 |   await page.setViewportSize({
  292 |     width: 1100,
  293 |     height: 450
  294 |   });
  295 |   await page.goto('/');
  296 |   for (let i = 0; i < 3; i++) await add(page);
  297 |   await expect(page.getByRole('group', {
  298 |     name: 'Visible passage'
  299 |   })).toBeVisible();
  300 |   await expect(page.locator('[data-reader-pane]:visible')).toHaveCount(1);
  301 |   expect(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth)).toBe(false);
  302 | });
  303 | test('Add duplicates the complete canonical range and replacement changes only the explicitly chosen pane', async ({
  304 |   page
  305 | }) => {
  306 |   await setup(page);
  307 |   await page.goto('/?book=Gen&chapter=1&verse=2&EndChapter=2&EndVerse=3');
  308 |   for (let i = 0; i < 3; i++) await add(page);
  309 |   const before = await page.locator('[data-reader-pane]').evaluateAll(ns => ns.map(n => n.dataset.paneKey));
  310 |   const layout = JSON.parse(new URL(page.url()).searchParams.get('reader'));
  311 |   expect(layout.panes.every(p => p.ref.target.end.chapter === 2 && p.ref.target.end.verse === 3)).toBe(true);
  312 |   await page.getByRole('button', {
  313 |     name: 'Add reader pane',
  314 |     exact: true
  315 |   }).click();
  316 |   await page.getByRole('dialog', {
  317 |     name: 'Choose passage to replace'
  318 |   }).getByRole('button', {
  319 |     name: 'Replace passage 1: Genesis 1:2–2:3',
  320 |     exact: true
  321 |   }).click();
  322 |   await expect(page.getByRole('dialog', {
  323 |     name: 'Book and chapter selector'
  324 |   })).toBeVisible();
  325 |   await page.getByRole('dialog', {
  326 |     name: 'Book and chapter selector'
  327 |   }).getByRole('button', {
  328 |     name: 'Cancel',
  329 |     exact: true
  330 |   }).click();
  331 |   expect(await page.locator('[data-reader-pane]').evaluateAll(ns => ns.map(n => n.dataset.paneKey))).toEqual(before);
  332 |   expect(JSON.parse(new URL(page.url()).searchParams.get('reader')).active).toBe(0);
  333 |   await page.getByRole('button', {
  334 |     name: 'Close passage 1',
  335 |     exact: true
  336 |   }).click();
  337 |   const after = await page.locator('[data-reader-pane]').evaluateAll(ns => ns.map(n => n.dataset.paneKey));
  338 |   expect(after).toEqual(before.slice(1));
  339 |   expect(JSON.parse(new URL(page.url()).searchParams.get('reader')).active).toBe(0);
  340 | });
  341 | test('layout clamps retain intended anchor while a subsequent user movement replaces it', async ({
  342 |   page
  343 | }) => {
  344 |   await setup(page);
  345 |   await page.setViewportSize({
  346 |     width: 1100,
  347 |     height: 500
  348 |   });
  349 |   await page.goto('/');
  350 |   const scroll = page.locator('[data-reader-scroll]');
  351 |   await expect(page.locator('[data-word-position]').first()).toBeVisible();
  352 |   await scroll.evaluate(el => el.scrollTop = el.scrollHeight);
  353 |   const before = await scroll.evaluate(el => el.scrollTop);
  354 |   await page.setViewportSize({
  355 |     width: 1100,
  356 |     height: 900
  357 |   });
  358 |   await page.setViewportSize({
  359 |     width: 1100,
  360 |     height: 500
  361 |   });
  362 |   await expect.poll(() => scroll.evaluate(el => el.scrollTop)).toBe(before);
  363 |   await scroll.evaluate(el => el.scrollTop = 120);
  364 |   await page.setViewportSize({
  365 |     width: 1100,
  366 |     height: 900
  367 |   });
  368 |   await page.setViewportSize({
  369 |     width: 1100,
  370 |     height: 500
  371 |   });
> 372 |   await expect.poll(() => scroll.evaluate(el => el.scrollTop)).toBe(120);
      |                                                                ^ Error: expect(received).toBe(expected) // Object.is equality
  373 | });
  374 | test('closing an inactive pane preserves active survivor and native default-key semantics', async ({
  375 |   page
  376 | }) => {
  377 |   await setup(page);
  378 |   await page.setViewportSize({
  379 |     width: 1600,
  380 |     height: 1000
  381 |   });
  382 |   await page.goto('/');
  383 |   await page.evaluate(() => {
  384 |     const {
  385 |       key,
  386 |       ...state
  387 |     } = history.state;
  388 |     history.replaceState({
  389 |       ...state,
  390 |       foreign: 'default-entry'
  391 |     }, '');
  392 |   });
  393 |   await add(page);
  394 |   await add(page);
  395 |   const keys = await page.locator('[data-reader-pane]').evaluateAll(ns => ns.map(n => n.dataset.paneKey));
  396 |   await page.getByRole('button', {
  397 |     name: 'Close passage 1',
  398 |     exact: true
  399 |   }).click();
  400 |   const state = await page.evaluate(() => history.state.usr.scribeswellReader);
  401 |   expect(state.activePaneKey).toBe(keys[2]);
  402 |   expect(state.panes.map(p => p.paneKey)).toEqual(keys.slice(1));
  403 |   await page.goBack();
  404 |   await expect(page.locator('[data-reader-pane]')).toHaveCount(3);
  405 |   await page.goBack();
  406 |   await expect(page.locator('[data-reader-pane]')).toHaveCount(2);
  407 |   await page.goBack();
  408 |   await expect(page.locator('[data-reader-pane]')).toHaveCount(1);
  409 |   expect(await page.evaluate(() => Object.hasOwn(history.state, 'key'))).toBe(false);
  410 |   expect(await page.evaluate(() => history.state.foreign)).toBe('default-entry');
  411 | });
  412 | test('a deferred outgoing checkpoint cannot overwrite the new browser entry', async ({
  413 |   page
  414 | }) => {
  415 |   await setup(page);
  416 |   await page.goto('/');
  417 |   const scroll = page.locator('[data-reader-scroll]');
  418 |   await expect(page.locator('[data-word-position]').first()).toBeVisible();
  419 |   await scroll.dispatchEvent('wheel', {
  420 |     deltaY: 120
  421 |   });
  422 |   await scroll.evaluate(el => el.scrollTop = 120);
  423 |   await add(page);
  424 |   const key = await page.evaluate(() => history.state.key);
  425 |   await page.waitForTimeout(180);
  426 |   expect(await page.evaluate(() => history.state.key)).toBe(key);
  427 |   expect(await page.evaluate(() => history.state.usr.scribeswellReader.panes.length)).toBe(2);
  428 |   await page.goBack();
  429 |   await expect(page.locator('[data-reader-pane]')).toHaveCount(1);
  430 |   await expect.poll(() => page.locator('[data-reader-scroll]').evaluate(el => el.scrollTop)).toBe(120);
  431 | });
  432 | test('structured foreign Router user values remain unmodified by checkpoints and navigation', async ({
  433 |   page
  434 | }) => {
  435 |   await setup(page);
  436 |   await page.goto('/');
  437 |   const result = await page.evaluate(async () => {
  438 |     const m = await import('/src/lib/reader-layout.ts');
  439 |     return [new Date('2026-10-26T00:00:00Z'), new Map([['foreign', 42]]), new Set(['foreign']), ['foreign'], 17, null].map(value => {
  440 |       const merged = m.snapshotState(value, {
  441 |         v: 1
  442 |       });
  443 |       return value === null ? merged.scribeswellReader.v === 1 : merged === value;
  444 |     });
  445 |   });
  446 |   expect(result).toEqual([true, true, true, true, true, true]);
  447 |   await page.evaluate(() => history.replaceState({
  448 |     ...history.state,
  449 |     usr: new Map([['foreign', 42]])
  450 |   }, ''));
  451 |   await add(page);
  452 |   expect(await page.evaluate(() => history.state.usr instanceof Map && history.state.usr.get('foreign') === 42)).toBe(true);
  453 |   await page.goBack();
  454 |   await expect(page.locator('[data-reader-pane]')).toHaveCount(1);
  455 |   expect(await page.evaluate(() => history.state.usr instanceof Map && history.state.usr.get('foreign') === 42)).toBe(true);
  456 | });
  457 | test('four-pane row qualification reserves two hundred usable text pixels after controls', async ({
  458 |   page
  459 | }) => {
  460 |   await setup(page);
  461 |   await page.setViewportSize({
  462 |     width: 1100,
  463 |     height: 650
  464 |   });
  465 |   await page.goto('/');
  466 |   for (let i = 0; i < 3; i++) await add(page);
  467 |   const visible = page.locator('[data-reader-pane]:visible');
  468 |   if ((await visible.count()) > 1) {
  469 |     const heights = await page.locator('[data-reader-scroll]:visible').evaluateAll(ns => ns.map(n => n.clientHeight));
  470 |     expect(Math.min(...heights)).toBeGreaterThanOrEqual(200);
  471 |   } else await expect(page.getByRole('group', {
  472 |     name: 'Visible passage'
```