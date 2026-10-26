# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: workspace-tabs.spec.cjs >> P10 malformed tab provenance never revives scrubbed complete callback query credentials
- Location: tests/workspace-tabs.spec.cjs:53:1

# Error details

```
Error: expect(received).toEqual(expected) // deep equality

- Expected  - 0
+ Received  + 8

  Object {
    "foreign": "kept value",
    "keys": Array [
+     "access_token",
+     "code",
+     "expires_in",
      "foreign",
+     "provider_refresh_token",
+     "provider_token",
      "reader",
+     "refresh_token",
+     "token_type",
+     "type",
    ],
    "native": "retained",
    "user": "retained",
  }
```

# Page snapshot

```yaml
- generic [ref=f1e3]:
  - banner [ref=f1e5]:
    - generic [ref=f1e6]:
      - generic [ref=f1e7]: Scribes' Well
      - generic [ref=f1e13]:
        - generic [ref=f1e14]: synthetic-reader@example.invalid
        - button "Sign out" [ref=f1e17]
  - main [ref=f1e21]:
    - generic [ref=f1e22]:
      - generic [ref=f1e23]:
        - tablist "Workspace tabs" [ref=f1e24]:
          - generic [ref=f1e25]:
            - tab "Genesis 1" [ref=f1e26]
            - button "Rename tab 1" [ref=f1e27]: Rename
            - button "Close tab 1" [ref=f1e28]: ×
          - generic [ref=f1e29]:
            - tab "Genesis 1" [selected] [ref=f1e30]
            - button "Rename tab 2" [ref=f1e31]: Rename
            - button "Close tab 2" [ref=f1e32]: ×
        - button "New workspace tab" [ref=f1e33]: + New tab
      - generic [ref=f1e34]:
        - button "Add reader pane" [ref=f1e35]
        - alert [ref=f1e38]: Invalid reading link
        - button "Enter focus mode" [ref=f1e39]: Focus mode
      - navigation "Reader tools" [ref=f1e45]:
        - button "Studies" [ref=f1e46]
        - button "Analysis" [ref=f1e47]
      - tabpanel "Genesis 1" [ref=f1e49]:
        - region "Passage 1" [ref=f1e50]:
          - generic [ref=f1e51]:
            - button "Previous chapter" [disabled] [ref=f1e52]
            - generic [ref=f1e55]:
              - 'button "Navigate: Genesis, chapter 1. Open selector." [expanded] [ref=f1e56]': Genesis א
              - dialog "Book and chapter selector" [ref=f1e59]:
                - generic [ref=f1e60]:
                  - generic [ref=f1e61]:
                    - text: Passage reference
                    - textbox "Passage reference" [active] [ref=f1e62]:
                      - /placeholder: Psalm 110:1–3 / תהילים קי:1
                      - text: Genesis 1
                  - status [ref=f1e63]: Genesis 1
                  - button "Cancel" [ref=f1e64]
                - generic [ref=f1e65]:
                  - navigation "Books of the Bible" [ref=f1e66]:
                    - generic [ref=f1e67]:
                      - heading "Torah" [level=3] [ref=f1e68]
                      - button "Genesis — בראשית" [ref=f1e69]:
                        - generic [ref=f1e70]: Genesis
                        - generic [ref=f1e71]: בראשית
                      - button "Exodus — שְׁמוֹת" [ref=f1e72]:
                        - generic [ref=f1e73]: Exodus
                        - generic [ref=f1e74]: שְׁמוֹת
                      - button "Leviticus — וַיִּקְרָא" [ref=f1e75]:
                        - generic [ref=f1e76]: Leviticus
                        - generic [ref=f1e77]: וַיִּקְרָא
                      - button "Numbers — בְּמִדְבַּר" [ref=f1e78]:
                        - generic [ref=f1e79]: Numbers
                        - generic [ref=f1e80]: בְּמִדְבַּר
                      - button "Deuteronomy — דְּבָרִים" [ref=f1e81]:
                        - generic [ref=f1e82]: Deuteronomy
                        - generic [ref=f1e83]: דְּבָרִים
                    - generic [ref=f1e84]:
                      - heading "Nevi’im" [level=3] [ref=f1e85]
                      - button "Joshua — יְהוֹשֻׁעַ" [ref=f1e86]:
                        - generic [ref=f1e87]: Joshua
                        - generic [ref=f1e88]: יְהוֹשֻׁעַ
                      - button "Judges — שׁוֹפְטִים" [ref=f1e89]:
                        - generic [ref=f1e90]: Judges
                        - generic [ref=f1e91]: שׁוֹפְטִים
                      - button "I Samuel — שְׁמוּאֵל א" [ref=f1e92]:
                        - generic [ref=f1e93]: I Samuel
                        - generic [ref=f1e94]: שְׁמוּאֵל א
                      - button "II Samuel — שְׁמוּאֵל ב" [ref=f1e95]:
                        - generic [ref=f1e96]: II Samuel
                        - generic [ref=f1e97]: שְׁמוּאֵל ב
                      - button "I Kings — מְלָכִים א" [ref=f1e98]:
                        - generic [ref=f1e99]: I Kings
                        - generic [ref=f1e100]: מְלָכִים א
                      - button "II Kings — מְלָכִים ב" [ref=f1e101]:
                        - generic [ref=f1e102]: II Kings
                        - generic [ref=f1e103]: מְלָכִים ב
                      - button "Isaiah — יְשַׁעְיָהוּ" [ref=f1e104]:
                        - generic [ref=f1e105]: Isaiah
                        - generic [ref=f1e106]: יְשַׁעְיָהוּ
                      - button "Jeremiah — יִרְמְיָהוּ" [ref=f1e107]:
                        - generic [ref=f1e108]: Jeremiah
                        - generic [ref=f1e109]: יִרְמְיָהוּ
                      - button "Ezekiel — יְחֶזְקֵאל" [ref=f1e110]:
                        - generic [ref=f1e111]: Ezekiel
                        - generic [ref=f1e112]: יְחֶזְקֵאל
                      - button "Hosea — הוֹשֵׁעַ" [ref=f1e113]:
                        - generic [ref=f1e114]: Hosea
                        - generic [ref=f1e115]: הוֹשֵׁעַ
                      - button "Joel — יוֹאֵל" [ref=f1e116]:
                        - generic [ref=f1e117]: Joel
                        - generic [ref=f1e118]: יוֹאֵל
                      - button "Amos — עָמוֹס" [ref=f1e119]:
                        - generic [ref=f1e120]: Amos
                        - generic [ref=f1e121]: עָמוֹס
                      - button "Obadiah — עֹבַדְיָה" [ref=f1e122]:
                        - generic [ref=f1e123]: Obadiah
                        - generic [ref=f1e124]: עֹבַדְיָה
                      - button "Jonah — יוֹנָה" [ref=f1e125]:
                        - generic [ref=f1e126]: Jonah
                        - generic [ref=f1e127]: יוֹנָה
                      - button "Micah — מִיכָה" [ref=f1e128]:
                        - generic [ref=f1e129]: Micah
                        - generic [ref=f1e130]: מִיכָה
                      - button "Nahum — נַחוּם" [ref=f1e131]:
                        - generic [ref=f1e132]: Nahum
                        - generic [ref=f1e133]: נַחוּם
                      - button "Habakkuk — חֲבַקּוּק" [ref=f1e134]:
                        - generic [ref=f1e135]: Habakkuk
                        - generic [ref=f1e136]: חֲבַקּוּק
                      - button "Zephaniah — צְפַנְיָה" [ref=f1e137]:
                        - generic [ref=f1e138]: Zephaniah
                        - generic [ref=f1e139]: צְפַנְיָה
                      - button "Haggai — חַגַּי" [ref=f1e140]:
                        - generic [ref=f1e141]: Haggai
                        - generic [ref=f1e142]: חַגַּי
                      - button "Zechariah — זְכַרְיָה" [ref=f1e143]:
                        - generic [ref=f1e144]: Zechariah
                        - generic [ref=f1e145]: זְכַרְיָה
                      - button "Malachi — מַלְאָכִי" [ref=f1e146]:
                        - generic [ref=f1e147]: Malachi
                        - generic [ref=f1e148]: מַלְאָכִי
                    - generic [ref=f1e149]:
                      - heading "Ketuvim" [level=3] [ref=f1e150]
                      - button "Psalms — תְּהִלִּים" [ref=f1e151]:
                        - generic [ref=f1e152]: Psalms
                        - generic [ref=f1e153]: תְּהִלִּים
                      - button "Proverbs — מִשְׁלֵי" [ref=f1e154]:
                        - generic [ref=f1e155]: Proverbs
                        - generic [ref=f1e156]: מִשְׁלֵי
                      - button "Job — אִיּוֹב" [ref=f1e157]:
                        - generic [ref=f1e158]: Job
                        - generic [ref=f1e159]: אִיּוֹב
                      - button "Song of Solomon — שִׁיר הַשִּׁירִים" [ref=f1e160]:
                        - generic [ref=f1e161]: Song of Solomon
                        - generic [ref=f1e162]: שִׁיר הַשִּׁירִים
                      - button "Ruth — רוּת" [ref=f1e163]:
                        - generic [ref=f1e164]: Ruth
                        - generic [ref=f1e165]: רוּת
                      - button "Lamentations — אֵיכָה" [ref=f1e166]:
                        - generic [ref=f1e167]: Lamentations
                        - generic [ref=f1e168]: אֵיכָה
                      - button "Ecclesiastes — קֹהֶלֶת" [ref=f1e169]:
                        - generic [ref=f1e170]: Ecclesiastes
                        - generic [ref=f1e171]: קֹהֶלֶת
                      - button "Esther — אֶסְתֵּר" [ref=f1e172]:
                        - generic [ref=f1e173]: Esther
                        - generic [ref=f1e174]: אֶסְתֵּר
                      - button "Daniel — דָּנִיֵּאל" [ref=f1e175]:
                        - generic [ref=f1e176]: Daniel
                        - generic [ref=f1e177]: דָּנִיֵּאל
                      - button "Ezra — עֶזְרָא" [ref=f1e178]:
                        - generic [ref=f1e179]: Ezra
                        - generic [ref=f1e180]: עֶזְרָא
                      - button "Nehemiah — נְחֶמְיָה" [ref=f1e181]:
                        - generic [ref=f1e182]: Nehemiah
                        - generic [ref=f1e183]: נְחֶמְיָה
                      - button "I Chronicles — דִּבְרֵי הַיָּמִים א" [ref=f1e184]:
                        - generic [ref=f1e185]: I Chronicles
                        - generic [ref=f1e186]: דִּבְרֵי הַיָּמִים א
                      - button "II Chronicles — דִּבְרֵי הַיָּמִים ב" [ref=f1e187]:
                        - generic [ref=f1e188]: II Chronicles
                        - generic [ref=f1e189]: דִּבְרֵי הַיָּמִים ב
                    - generic [ref=f1e190]:
                      - heading "New Testament" [level=3] [ref=f1e191]
                      - button "Matthew — Reference only" [ref=f1e192]:
                        - generic [ref=f1e193]: Matthew
                      - button "Mark — Reference only" [ref=f1e194]:
                        - generic [ref=f1e195]: Mark
                      - button "Luke — Reference only" [ref=f1e196]:
                        - generic [ref=f1e197]: Luke
                      - button "John — Reference only" [ref=f1e198]:
                        - generic [ref=f1e199]: John
                      - button "Acts — Reference only" [ref=f1e200]:
                        - generic [ref=f1e201]: Acts
                      - button "Romans — Reference only" [ref=f1e202]:
                        - generic [ref=f1e203]: Romans
                      - button "I Corinthians — Reference only" [ref=f1e204]:
                        - generic [ref=f1e205]: I Corinthians
                      - button "II Corinthians — Reference only" [ref=f1e206]:
                        - generic [ref=f1e207]: II Corinthians
                      - button "Galatians — Reference only" [ref=f1e208]:
                        - generic [ref=f1e209]: Galatians
                      - button "Ephesians — Reference only" [ref=f1e210]:
                        - generic [ref=f1e211]: Ephesians
                      - button "Philippians — Reference only" [ref=f1e212]:
                        - generic [ref=f1e213]: Philippians
                      - button "Colossians — Reference only" [ref=f1e214]:
                        - generic [ref=f1e215]: Colossians
                      - button "I Thessalonians — Reference only" [ref=f1e216]:
                        - generic [ref=f1e217]: I Thessalonians
                      - button "II Thessalonians — Reference only" [ref=f1e218]:
                        - generic [ref=f1e219]: II Thessalonians
                      - button "I Timothy — Reference only" [ref=f1e220]:
                        - generic [ref=f1e221]: I Timothy
                      - button "II Timothy — Reference only" [ref=f1e222]:
                        - generic [ref=f1e223]: II Timothy
                      - button "Titus — Reference only" [ref=f1e224]:
                        - generic [ref=f1e225]: Titus
                      - button "Philemon — Reference only" [ref=f1e226]:
                        - generic [ref=f1e227]: Philemon
                      - button "Hebrews — Reference only" [ref=f1e228]:
                        - generic [ref=f1e229]: Hebrews
                      - button "James — Reference only" [ref=f1e230]:
                        - generic [ref=f1e231]: James
                      - button "I Peter — Reference only" [ref=f1e232]:
                        - generic [ref=f1e233]: I Peter
                      - button "II Peter — Reference only" [ref=f1e234]:
                        - generic [ref=f1e235]: II Peter
                      - button "I John — Reference only" [ref=f1e236]:
                        - generic [ref=f1e237]: I John
                      - button "II John — Reference only" [ref=f1e238]:
                        - generic [ref=f1e239]: II John
                      - button "III John — Reference only" [ref=f1e240]:
                        - generic [ref=f1e241]: III John
                      - button "Jude — Reference only" [ref=f1e242]:
                        - generic [ref=f1e243]: Jude
                      - button "Revelation of John — Reference only" [ref=f1e244]:
                        - generic [ref=f1e245]: Revelation of John
                  - group "Chapters of Genesis" [ref=f1e246]:
                    - heading "Genesis" [level=3] [ref=f1e247]
                    - generic [ref=f1e248]:
                      - button "Chapter 1 of Genesis" [ref=f1e249]: א
                      - button "Chapter 2 of Genesis" [ref=f1e250]: ב
                      - button "Chapter 3 of Genesis" [ref=f1e251]: ג
                      - button "Chapter 4 of Genesis" [ref=f1e252]: ד
                      - button "Chapter 5 of Genesis" [ref=f1e253]: ה
                      - button "Chapter 6 of Genesis" [ref=f1e254]: ו
                      - button "Chapter 7 of Genesis" [ref=f1e255]: ז
                      - button "Chapter 8 of Genesis" [ref=f1e256]: ח
                      - button "Chapter 9 of Genesis" [ref=f1e257]: ט
                      - button "Chapter 10 of Genesis" [ref=f1e258]: י
                      - button "Chapter 11 of Genesis" [ref=f1e259]: יא
                      - button "Chapter 12 of Genesis" [ref=f1e260]: יב
                      - button "Chapter 13 of Genesis" [ref=f1e261]: יג
                      - button "Chapter 14 of Genesis" [ref=f1e262]: יד
                      - button "Chapter 15 of Genesis" [ref=f1e263]: טו
                      - button "Chapter 16 of Genesis" [ref=f1e264]: טז
                      - button "Chapter 17 of Genesis" [ref=f1e265]: יז
                      - button "Chapter 18 of Genesis" [ref=f1e266]: יח
                      - button "Chapter 19 of Genesis" [ref=f1e267]: יט
                      - button "Chapter 20 of Genesis" [ref=f1e268]: כ
                      - button "Chapter 21 of Genesis" [ref=f1e269]: כא
                      - button "Chapter 22 of Genesis" [ref=f1e270]: כב
                      - button "Chapter 23 of Genesis" [ref=f1e271]: כג
                      - button "Chapter 24 of Genesis" [ref=f1e272]: כד
                      - button "Chapter 25 of Genesis" [ref=f1e273]: כה
                      - button "Chapter 26 of Genesis" [ref=f1e274]: כו
                      - button "Chapter 27 of Genesis" [ref=f1e275]: כז
                      - button "Chapter 28 of Genesis" [ref=f1e276]: כח
                      - button "Chapter 29 of Genesis" [ref=f1e277]: כט
                      - button "Chapter 30 of Genesis" [ref=f1e278]: ל
                      - button "Chapter 31 of Genesis" [ref=f1e279]: לא
                      - button "Chapter 32 of Genesis" [ref=f1e280]: לב
                      - button "Chapter 33 of Genesis" [ref=f1e281]: לג
                      - button "Chapter 34 of Genesis" [ref=f1e282]: לד
                      - button "Chapter 35 of Genesis" [ref=f1e283]: לה
                      - button "Chapter 36 of Genesis" [ref=f1e284]: לו
                      - button "Chapter 37 of Genesis" [ref=f1e285]: לז
                      - button "Chapter 38 of Genesis" [ref=f1e286]: לח
                      - button "Chapter 39 of Genesis" [ref=f1e287]: לט
                      - button "Chapter 40 of Genesis" [ref=f1e288]: מ
                      - button "Chapter 41 of Genesis" [ref=f1e289]: מא
                      - button "Chapter 42 of Genesis" [ref=f1e290]: מב
                      - button "Chapter 43 of Genesis" [ref=f1e291]: מג
                      - button "Chapter 44 of Genesis" [ref=f1e292]: מד
                      - button "Chapter 45 of Genesis" [ref=f1e293]: מה
                      - button "Chapter 46 of Genesis" [ref=f1e294]: מו
                      - button "Chapter 47 of Genesis" [ref=f1e295]: מז
                      - button "Chapter 48 of Genesis" [ref=f1e296]: מח
                      - button "Chapter 49 of Genesis" [ref=f1e297]: מט
                      - button "Chapter 50 of Genesis" [ref=f1e298]: נ
            - button "Next chapter" [ref=f1e299]
            - button "Close passage 1" [ref=f1e302]: ×
          - region "Chapter text" [ref=f1e303]:
            - list "Verses" [ref=f1e304]:
              - listitem [ref=f1e305]:
                - generic "Verse 1" [ref=f1e306]: "1"
                - paragraph [ref=f1e307]:
                  - 'button "Word: בְּרֵאשִׁית" [ref=f1e308] [cursor=pointer]': בְּרֵאשִׁית
```

# Test source

```ts
  1  | const {test,expect}=require('@playwright/test');
  2  | async function setup(page){
  3  |  await page.route('http://127.0.0.1:8001/**',r=>r.fulfill({json:[]}));
  4  |  await page.route('**/api/bible/**',r=>{
  5  |   const path=new URL(r.request().url()).pathname,b={id:1,osis_id:'Gen',name_en:'Genesis',name_he:'בראשית',testament:'OT',book_order:1};
  6  |   return r.fulfill({json:path.endsWith('/books')?{data:[b],total:1}:path.endsWith('/verses')?{data:[{id:1,verse_num:1,book_id:1,chapter_num:1,words:[{id:1,position:1,surface_he:'בְּרֵאשִׁית',display_he:'בְּרֵאשִׁית',lemma_strong:null,morph_code:null}]}],total:1}:{...b,chapters:[{id:1,chapter_num:1},{id:2,chapter_num:2}]}});
  7  |  });
  8  |  await page.goto('/');
  9  | }
  10 | const tabs=page=>page.getByRole('tablist',{name:'Workspace tabs'}).getByRole('tab');
  11 | async function add(page){await page.getByRole('button',{name:'New workspace tab',exact:true}).click();await page.getByRole('dialog',{name:'Book and chapter selector'}).getByRole('button',{name:'Cancel',exact:true}).click();}
  12 | test('tab activation closure and replay push exactly once and closed replay restores only public identity',async({page})=>{
  13 |  await setup(page);const initial=await page.evaluate(()=>history.state.idx);await add(page);
  14 |  const key=await page.evaluate(()=>history.state.usr.scribeswellReader.tabKey);expect(await page.evaluate(()=>history.state.idx)).toBe(initial+1);
  15 |  await tabs(page).first().click();expect(await page.evaluate(()=>history.state.idx)).toBe(initial+2);await tabs(page).first().click();expect(await page.evaluate(()=>history.state.idx)).toBe(initial+2);
  16 |  await page.getByRole('button',{name:'Close tab 2',exact:true}).click();expect(await page.evaluate(()=>history.state.idx)).toBe(initial+3);
  17 |  await page.goBack();await expect(tabs(page)).toHaveCount(1);await page.goBack();await expect(tabs(page)).toHaveCount(2);
  18 |  expect(await page.evaluate(()=>history.state.usr.scribeswellReader.tabKey)).toBe(key);expect(await page.evaluate(()=>history.state.idx)).toBe(initial+1);
  19 | });
  20 | test('tab labels stay out of public history and manual roving keys preserve activation',async({page})=>{
  21 |  await setup(page);await add(page);await page.getByRole('button',{name:'Rename tab 2',exact:true}).click();await page.getByLabel('Tab name',{exact:true}).fill('  עברית study  ');await page.getByRole('dialog',{name:'Rename workspace tab'}).getByRole('button',{name:'Save',exact:true}).click();
  22 |  await expect(tabs(page).nth(1)).toHaveText('עברית study');expect(await page.evaluate(()=>JSON.stringify(history.state)+location.href)).not.toContain('study');
  23 |  await tabs(page).nth(1).focus();await page.keyboard.press('Home');await expect(tabs(page).first()).toBeFocused();await expect(tabs(page).nth(1)).toHaveAttribute('aria-selected','true');await page.keyboard.press('Enter');await expect(tabs(page).first()).toHaveAttribute('aria-selected','true');
  24 |  await page.getByRole('button',{name:'Close tab 1',exact:true}).click();await expect(tabs(page)).toHaveCount(1);await expect(tabs(page).first()).toBeFocused();await expect(page.getByRole('button',{name:/Close tab/})).toHaveCount(0);
  25 | });
  26 | test('twelve tab cap never evicts and closed history requires explicit public-only victim choice',async({page})=>{
  27 |  await setup(page);await add(page);const closed=await page.evaluate(()=>history.state.usr.scribeswellReader.tabKey);await page.getByRole('button',{name:'Close tab 2',exact:true}).click();
  28 |  for(let i=0;i<11;i++)await add(page);await expect(tabs(page)).toHaveCount(12);await page.getByRole('button',{name:'New workspace tab',exact:true}).click();await expect(page.getByText('Close a tab to open another.',{exact:true})).toBeVisible();
  29 |  await page.evaluate(()=>history.go(-12));const dialog=page.getByRole('dialog',{name:'Choose tab to close and restore'});await expect(dialog).toBeVisible();await expect(tabs(page)).toHaveCount(12);const index=await page.evaluate(()=>history.state.idx);
  30 |  await dialog.getByRole('button',{name:/Close tab 3:/}).click();await expect(dialog).toHaveCount(0);await expect(tabs(page)).toHaveCount(12);expect(await page.evaluate(()=>history.state.idx)).toBe(index);
  31 |  expect(await tabs(page).filter({hasText:'Genesis'}).count()).toBe(12);expect(await page.locator(`[data-workspace-tab="${closed}"]`).getAttribute('aria-selected')).toBe('true');
  32 | });
  33 | 
  34 | test('valid Unicode punctuation snapshot tab identity remains selectable and close focus is safe',async({page})=>{
  35 |  await setup(page);await add(page);const key='עברית "quoted" [pane] #1';await page.evaluate(key=>{const state=history.state;history.replaceState({...state,usr:{...state.usr,scribeswellReader:{...state.usr.scribeswellReader,tabKey:key}}},'');},key);await page.reload();await expect(tabs(page)).toHaveCount(1);expect(await tabs(page).first().getAttribute('data-workspace-tab')).toBe(key);await expect(page.getByRole('tabpanel',{name:'Genesis 1',exact:true})).toBeVisible();await add(page);await tabs(page).first().click();await page.getByRole('button',{name:'Close tab 1',exact:true}).click();await expect(tabs(page)).toHaveCount(1);await expect(tabs(page).first()).toBeFocused();
  36 | });
  37 | 
  38 | test('POP checkpoints the outgoing live tab anchor for a later explicit tab activation',async({page})=>{
  39 |  await setup(page);await page.route('**/api/bible/**/verses',r=>r.fulfill({json:{data:Array.from({length:31},(_,i)=>({id:i+1,verse_num:i+1,book_id:1,chapter_num:1,words:[{id:i+1,position:1,surface_he:'בְּרֵאשִׁית',display_he:'בְּרֵאשִׁית',lemma_strong:null,morph_code:null}]})),total:31}}));await page.reload();const scroll=page.locator('[data-reader-scroll]');await expect(scroll).toHaveAttribute('data-ready','true');const source=await scroll.evaluate(el=>{el.dispatchEvent(new WheelEvent('wheel',{bubbles:true}));el.scrollTop=140;el.dispatchEvent(new Event('scroll',{bubbles:true}));return el.scrollTop;});expect(source).toBeGreaterThan(50);await page.waitForTimeout(200);await add(page);await expect(scroll).toHaveAttribute('data-ready','true');const before=await scroll.evaluate(el=>{el.dispatchEvent(new WheelEvent('wheel',{bubbles:true}));el.scrollTop=350;el.dispatchEvent(new Event('scroll',{bubbles:true}));return el.scrollTop;});expect(before).toBeGreaterThan(100);await page.waitForTimeout(200);await page.goBack();await expect.poll(async()=>Math.abs(await scroll.evaluate(el=>el.scrollTop)-source)).toBeLessThan(3);await page.goForward();await expect.poll(async()=>Math.abs(await scroll.evaluate(el=>el.scrollTop)-before)).toBeLessThan(3);await page.goBack();await expect.poll(async()=>Math.abs(await scroll.evaluate(el=>el.scrollTop)-source)).toBeLessThan(3);await tabs(page).nth(1).click();await expect(scroll).toHaveAttribute('data-ready','true');await expect.poll(async()=>Math.abs(await scroll.evaluate(el=>el.scrollTop)-before)).toBeLessThan(3);
  40 | });
  41 | 
  42 | 
  43 | test('closing the sole pane delegates to tab closure and preserves the final reader without reset',async({page})=>{
  44 |  await setup(page);const first=await tabs(page).first().getAttribute('data-workspace-tab');await add(page);const index=await page.evaluate(()=>history.state.idx),reference=await page.evaluate(()=>history.state.usr.scribeswellReader.panes[0].ref);await page.getByRole('button',{name:'Close passage 1',exact:true}).click();await expect(tabs(page)).toHaveCount(1);expect(await tabs(page).first().getAttribute('data-workspace-tab')).toBe(first);await expect(tabs(page).first()).toHaveAttribute('aria-selected','true');await expect(tabs(page).first()).toBeFocused();expect(await page.evaluate(()=>history.state.idx)).toBe(index+1);expect(await page.evaluate(()=>history.state.usr.scribeswellReader.panes[0].ref)).toEqual(reference);await expect(page.getByRole('button',{name:'Close passage 1',exact:true})).toHaveCount(0);await expect(page.getByRole('button',{name:/Close tab/})).toHaveCount(0);await expect(page.getByRole('button',{name:/Word: בְּרֵאשִׁית/})).toBeVisible();
  45 | });
  46 | 
  47 | test('review tabs B8 complete manual keyboard movement wraps and reveals all twelve controls without activation',async({page})=>{
  48 |  await setup(page);for(let i=0;i<11;i++)await add(page);const list=page.getByRole('tablist',{name:'Workspace tabs'}),controls=tabs(page),index=await page.evaluate(()=>history.state.idx);await controls.nth(11).focus();
  49 |  for(const [key,target] of [['ArrowRight',0],['ArrowLeft',11],['Home',0],['ArrowRight',1],['End',11],['ArrowLeft',10]]){await page.keyboard.press(key);await expect(controls.nth(target)).toBeFocused();expect(await page.evaluate(()=>history.state.idx)).toBe(index);await expect(controls.nth(11)).toHaveAttribute('aria-selected','true');const bounds=await controls.nth(target).evaluate(el=>{const r=el.getBoundingClientRect(),p=el.closest('[role="tablist"]').getBoundingClientRect();return {left:r.left-p.left,right:r.right-p.right};});expect(bounds.left).toBeGreaterThanOrEqual(-1);expect(bounds.right).toBeLessThanOrEqual(1);}
  50 |  await page.keyboard.press('Space');await expect(controls.nth(10)).toHaveAttribute('aria-selected','true');expect(await page.evaluate(()=>history.state.idx)).toBe(index+1);await page.keyboard.press('Home');await page.keyboard.press('Enter');await expect(controls.first()).toHaveAttribute('aria-selected','true');expect(await page.evaluate(()=>history.state.idx)).toBe(index+2);await expect(list).toBeVisible();
  51 | });
  52 | 
  53 | test('P10 malformed tab provenance never revives scrubbed complete callback query credentials',async({page})=>{
  54 |  await setup(page);
  55 |  const user={id:'33333333-3333-3333-3333-333333333333',email:'synthetic-reader@example.invalid',aud:'authenticated',app_metadata:{},user_metadata:{}};
  56 |  const token=[{alg:'HS256',typ:'JWT'},{sub:user.id,exp:Math.floor(Date.now()/1000)+3600},'synthetic-signature'].map(value=>Buffer.from(typeof value==='string'?value:JSON.stringify(value)).toString('base64url')).join('.');
  57 |  let releaseUser,userReads=0;
  58 |  await page.route('**/auth/v1/user*',async route=>{userReads++;await new Promise(resolve=>releaseUser=resolve);await route.fulfill({json:user});});
  59 |  const query=new URLSearchParams({reader:'{}',foreign:'kept value',access_token:token,refresh_token:'synthetic-refresh-only',expires_in:'3600',token_type:'bearer',type:'signup',code:'synthetic-code-only',provider_token:'synthetic-provider-only',provider_refresh_token:'synthetic-provider-refresh-only'});
  60 |  await page.goto('/?'+query);
  61 |  await expect(page.getByText('Invalid reading link',{exact:true})).toBeVisible();
  62 |  await expect.poll(()=>!!releaseUser).toBe(true);
  63 |  // The SDK must still see its callback until provider verification finishes.
  64 |  expect(await page.evaluate(()=>new URLSearchParams(location.search).has('access_token'))).toBe(true);
  65 |  releaseUser();
  66 |  await expect(page.getByRole('button',{name:'Sign out',exact:true})).toBeVisible();
  67 |  await expect.poll(()=>page.evaluate(()=>[...new URLSearchParams(location.search).keys()].sort())).toEqual(['foreign','reader']);
  68 |  expect(userReads).toBe(1);
  69 |  await page.evaluate(()=>history.replaceState({...history.state,foreignNative:'retained',usr:{...history.state.usr,foreignUser:'retained'}},''));
  70 |  const cleanQuery=()=>page.evaluate(()=>({keys:[...new URLSearchParams(location.search).keys()].sort(),foreign:new URLSearchParams(location.search).get('foreign'),native:history.state.foreignNative,user:history.state.usr.foreignUser}));
  71 |  const expected={keys:['foreign','reader'],foreign:'kept value',native:'retained',user:'retained'};
  72 |  await page.getByRole('button',{name:'New workspace tab',exact:true}).click();
  73 |  await expect(page.getByRole('dialog',{name:'Book and chapter selector'})).toBeVisible();
> 74 |  expect(await cleanQuery()).toEqual(expected);
     |                             ^ Error: expect(received).toEqual(expected) // deep equality
  75 |  expect(new URL(page.url()).searchParams.get('reader')).toBe('{}');
  76 |  await page.getByRole('dialog',{name:'Book and chapter selector'}).getByRole('button',{name:'Chapter 1 of Genesis',exact:true}).click();
  77 |  await expect(page.getByText('Invalid reading link',{exact:true})).toHaveCount(0);
  78 |  expect(await cleanQuery()).toEqual(expected);
  79 |  await tabs(page).first().click();
  80 |  await expect(page.getByText('Invalid reading link',{exact:true})).toBeVisible();
  81 |  expect(new URL(page.url()).searchParams.get('reader')).toBe('{}');
  82 |  expect(await cleanQuery()).toEqual(expected);
  83 |  await expect(page.getByRole('button',{name:'Sign out',exact:true})).toBeVisible();
  84 | });
  85 | 
  86 | test('P10 ordinary malformed tab retains raw search bytes when no callback fields exist',async({page})=>{
  87 |  await setup(page);
  88 |  const raw='?reader=%7b%7d&foreign=a%20b&foreign=%2f&flag&empty=&other=%7e';
  89 |  await page.goto('/'+raw);
  90 |  expect(new URL(page.url()).search).toBe(raw);
  91 |  await page.getByRole('button',{name:'New workspace tab',exact:true}).click();
  92 |  await page.getByRole('dialog',{name:'Book and chapter selector'}).getByRole('button',{name:'Chapter 1 of Genesis',exact:true}).click();
  93 |  await tabs(page).first().click();
  94 |  await expect(page.getByText('Invalid reading link',{exact:true})).toBeVisible();
  95 |  expect(new URL(page.url()).search).toBe(raw);
  96 | });
  97 | 
```