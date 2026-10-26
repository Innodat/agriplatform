# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: personal-notes.spec.cjs >> D12 anchored outline Open carries source occurrence in one reader history navigation
- Location: tests/personal-notes.spec.cjs:1936:1

# Error details

```
Error: expect(received).toBe(expected) // Object.is equality

Expected: 2
Received: 1

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
        - generic [ref=e14]: reader@example.invalid
        - button "Sign out" [ref=e18]
  - main [ref=e22]:
    - generic [ref=e23]:
      - generic [ref=e24]:
        - tablist "Workspace tabs" [ref=e25]:
          - generic [ref=e26]:
            - tab "Genesis 2:1" [selected] [ref=e27]
            - button "Rename tab 1" [ref=e28]: Rename
        - button "New workspace tab" [ref=e29]: + New tab
      - generic [ref=e30]:
        - button "Add reader pane" [ref=e31]
        - button "Enter focus mode" [ref=e34]: Focus mode
      - navigation "Reader tools" [ref=e40]:
        - button "Studies" [ref=e41]
        - button "Analysis" [pressed] [ref=e42]
        - generic [ref=e43]: Untitled study
      - generic [ref=e44]:
        - tabpanel "Genesis 2:1" [ref=e45]:
          - region "Passage 1" [ref=e46]:
            - generic [ref=e47]:
              - button "Previous chapter" [disabled] [ref=e48]
              - 'button "Navigate: Genesis, chapter 2. Open selector." [ref=e52]': Genesis ב
              - button "Next chapter" [disabled] [ref=e55]
            - region "Chapter text" [ref=e58]:
              - paragraph [ref=e59]: Genesis 2:1
              - paragraph [ref=e60]:
                - generic [ref=e61]: "Current note: Anchored explanation"
                - text: · Draft saved
              - list "Verses" [ref=e62]:
                - listitem [ref=e63]:
                  - generic "Verse 1" [ref=e64]: "1"
                  - paragraph [ref=e65]:
                    - 'button "Word: בְּרֵאשִׁית" [ref=e66] [cursor=pointer]': בְּרֵאשִׁית
        - complementary "Study tools" [ref=e67]:
          - generic [ref=e68]:
            - tablist "Analysis" [ref=e69]:
              - tab "Word" [disabled] [ref=e70]
              - tab "Occurrences" [disabled] [ref=e71]
              - tab "Notes" [selected] [ref=e72]
            - generic [ref=e73]:
              - region "Relevant own notes" [ref=e74]:
                - heading "Relevant own notes" [level=3] [ref=e75]
                - paragraph [ref=e76]: Genesis 2:1 · Only you
                - paragraph [ref=e77]: No relevant saved notes.
                - list
              - region "Note editor" [ref=e79]:
                - heading "Notes" [level=3] [ref=e80]
                - button "Duplicate note" [ref=e81]
                - button "Delete note" [ref=e82]
                - button "Delete study" [ref=e83]
                - paragraph [ref=e84]: Untitled study
                - button "Genesis 2:1" [ref=e85]
                - button "Read note" [ref=e86]
                - toolbar "Note formatting" [ref=e87]:
                  - button "Bold" [ref=e88]: B
                  - button "Italic" [ref=e89]: I
                  - button "Bullet list" [ref=e90]
                  - button "Numbered list" [ref=e91]
                  - button "Link" [ref=e92]
                  - button "Insert passage reference" [ref=e95]
                  - generic [ref=e98]:
                    - text: Direction
                    - combobox "Paragraph direction" [ref=e99]:
                      - option "Auto" [selected]
                      - option "Left to right"
                      - option "Right to left"
                - textbox "Note text" [ref=e100]:
                  - paragraph [ref=e101]: Anchored explanation
                - status [ref=e102]: Draft saved
                - button "Back to Studies" [ref=e103]
```

# Test source

```ts
  1839 | });
  1840 | 
  1841 | test('copies review: held copied-note read never reselects after confirmed source deletion',async({page})=>{
  1842 |  let release;await copiesFixture(page,{beforeCopyRead:()=>new Promise(resolve=>release=resolve)});await firstNote(page);await page.getByRole('button',{name:'Duplicate note',exact:true}).click();await expect.poll(()=>!!release).toBe(true);await page.getByRole('button',{name:'Delete note',exact:true}).click();await page.getByRole('dialog',{name:'Delete this note?'}).getByRole('button',{name:'Delete note',exact:true}).click();await expect(page.getByRole('textbox',{name:'Note text',exact:true})).toHaveCount(0);release();await expect(page.getByRole('button',{name:'Open created note',exact:true})).toBeVisible();await expect(page.getByRole('textbox',{name:'Note text',exact:true})).toHaveCount(0);
  1843 | });
  1844 | 
  1845 | test('copies review: study conflict refreshes metadata for the next explicit copy only',async({page})=>{
  1846 |  const store=await copiesFixture(page);await firstNote(page);store.metadata.revision='2';store.metadata.title='Current authorized title';await page.getByRole('button',{name:'Back to Studies',exact:true}).click();await page.getByRole('button',{name:'Copy study',exact:true}).click();await expect(page.getByRole('heading',{name:'Current authorized title',exact:true})).toBeVisible();expect(store.attempts).toHaveLength(1);expect(store.copies).toHaveLength(0);await page.getByRole('button',{name:'Copy study',exact:true}).click();await expect.poll(()=>store.copies.length).toBe(1);expect(store.attempts[1].payload.expected_revision).toBe('2');
  1847 | });
  1848 | 
  1849 | for(const label of ['Source study','Original unavailable'])test('copies review: note and study credit display '+label,async({page})=>{
  1850 |  await copiesFixture(page,{creditLabel:label});await firstNote(page);await page.getByRole('button',{name:'Duplicate note',exact:true}).click();await expect(page.getByText('Copied from: '+label,{exact:true})).toBeVisible();await page.getByRole('button',{name:'Back to Studies',exact:true}).click();await page.getByRole('button',{name:'Copy study',exact:true}).click();await expect(page.getByText('Copied from: '+label,{exact:true})).toBeVisible();
  1851 | });
  1852 | 
  1853 | test('copies review: adapters reject malformed credit on note study and library reads',async({page})=>{
  1854 |  await setup(page);await page.goto('/');const valid=copyCredit(),baseNote={...attribution,id:note,study_id:study,revision:'1',visibility:'study',value:{document:{version:1,blocks:[]},connections:[],highlights:[]}},baseStudy={...attribution,id:study,title:'Study',revision:'1'};
  1855 |  const variants=[undefined,null,valid,{...valid,label:{}},{...valid,source_note_id:'not-an-id'},{...valid,origin_account_id:'00000000-0000-0000-0000-000000000000'},{...valid,relation:'unsafe'},{...valid,created_at:'2026-02-30T00:00:00.000000Z'},{...valid,created_by_actor_id:'bad'},{...valid,label:'\uD800'},{...valid,label:' '},{...valid,created_by_actor_id:actor+'\n'},{...valid,created_at:attribution.created_at+'\n'}];
  1856 |  const result=await page.evaluate(async({variants,baseNote,baseStudy})=>{const {api}=await import('/src/lib/personal-notes.ts');const original=window.fetch,results=[];try{for(const credit of variants){const row={...baseNote,...(credit===undefined?{}:{copy_credit:credit})};window.fetch=async()=>new Response(JSON.stringify(row));try{await api.note('current',baseNote.study_id,baseNote.id);results.push(true);}catch{results.push(false);}}const bad={...baseStudy,copy_credit:{label:{}}};window.fetch=async()=>new Response(JSON.stringify(bad));try{await api.study('current',baseStudy.id);results.push(true);}catch{results.push(false);}window.fetch=async()=>new Response(JSON.stringify({items:[bad],next_cursor:null}));for(const read of [()=>api.studies('current'),()=>api.search('current','q')]){try{await read();results.push(true);}catch{results.push(false);}}return results;}finally{window.fetch=original;}},{variants,baseNote,baseStudy});expect(result).toEqual([true,true,true,...Array(13).fill(false)]);
  1857 | });
  1858 | 
  1859 | test('D1 study details use explicit whole-form Save Cancel and preserve note writing',async({page})=>{
  1860 |  await setup(page);await collectionStudy(page);
  1861 |  await page.getByRole('button',{name:'Edit study details',exact:true}).click();
  1862 |  await page.getByLabel('Introduction',{exact:true}).fill('Introduction\nמבוא');
  1863 |  await page.getByLabel('Source URL',{exact:true}).fill('https://example.invalid/source');
  1864 |  await page.getByRole('button',{name:'Save',exact:true}).click();
  1865 |  await expect(page.getByText('Introduction\nמבוא',{exact:true})).toBeVisible();
  1866 |  await expect(page.getByRole('link',{name:'Study source',exact:true})).toHaveAttribute('rel','noopener noreferrer');
  1867 | });
  1868 | 
  1869 | test('D2 relevant own notes offer inspection without changing current note',async({page})=>{
  1870 |  await setup(page);await firstNote(page);
  1871 |  await expect(page.getByRole('region',{name:'Relevant own notes',exact:true})).toBeVisible();
  1872 | });
  1873 | 
  1874 | function detailsReference(chapter=1,verse){const catalogue=require('../../data/reference-catalogue/catalogue.json'),book=catalogue.books.find(b=>b.book_id==='Gen');return {catalogue_id:catalogue.catalogue_id,catalogue_version:catalogue.catalogue_version,versification_id:book.versification_id,book_id:'Gen',target:verse?{kind:'verse_range',start:{chapter,verse},end:{chapter,verse}}:{kind:'chapter',chapter}};}
  1875 | const discoveryStudy='30000000-0000-4000-8000-000000000002',discoveryNote='40000000-0000-4000-8000-000000000002';
  1876 | async function discoveryFixture(page,options={}){
  1877 |  const store=await setup(page,options),reference=detailsReference(2,1),originReference=detailsReference(1,1);
  1878 |  const value={document:{version:2,blocks:[{type:'paragraph',direction:'auto',content:[{type:'text',text:'Another own explanation',marks:[]},{type:'passage_link',label:'Genesis 2:1',reference},{type:'passage_link',label:'Genesis 1:1',reference:originReference}]}]},connections:[],highlights:[]};
  1879 |  const result={study_id:discoveryStudy,study_title:'Another study',owner_account_id:account,note_id:discoveryNote,revision:'1',preview:'Another own explanation',references:[reference,originReference]};
  1880 |  const reads=[];
  1881 |  await page.route('**/api/studies/context-notes',async r=>{const body=r.request().postDataJSON();reads.push(body);expect(body.reference).toEqual(detailsReference(body.reference.target.kind==='chapter'?body.reference.target.chapter:body.reference.target.start.chapter,body.reference.target.kind==='verse_range'?body.reference.target.start.verse:undefined));if(options.context)return options.context(r,body,result);return r.fulfill({json:{items:[1,2].includes(body.reference.target.kind==='chapter'?body.reference.target.chapter:body.reference.target.start.chapter)?[result]:[],next_cursor:null}});});
  1882 |  await page.route('**/api/studies/'+discoveryStudy+'**',async r=>{const path=new URL(r.request().url()).pathname;if(options.beforePreview&&path.endsWith('/'+discoveryNote))await options.beforePreview();return r.fulfill({json:path.endsWith('/notes/'+discoveryNote)?{...attribution,id:discoveryNote,study_id:discoveryStudy,visibility:'study',revision:'1',value}:path.endsWith('/passages')?{study_id:discoveryStudy,revision:'1',items:[]}:path.endsWith('/notes')?{items:[],next_cursor:null}:{...attribution,id:discoveryStudy,title:'Another study',revision:'1'}});});
  1883 |  return {...store,reads};
  1884 | }
  1885 | 
  1886 | test('D3 relevant Preview preserves local writing destination and explicit Open uses save guard once',async({page})=>{
  1887 |  await discoveryFixture(page,{failPut:503});await firstNote(page);
  1888 |  const editor=page.getByRole('textbox',{name:'Note text',exact:true});await editor.fill('Local pending explanation');
  1889 |  const surface=page.getByRole('region',{name:'Relevant own notes',exact:true});await expect(surface.getByText('Another study · You · Saved preview',{exact:true})).toBeVisible();
  1890 |  const before=await page.evaluate(()=>({href:location.href,length:history.length}));
  1891 |  await surface.getByRole('button',{name:'Preview',exact:true}).click();await expect(page.getByRole('region',{name:'Relevant note preview'})).toContainText('Another own explanation');
  1892 |  await expect(editor).toHaveText('Local pending explanation');expect(await page.evaluate(()=>location.href)).toBe(before.href);await expect(page.getByRole('dialog',{name:'Changes not saved'})).toHaveCount(0);
  1893 |  await surface.getByRole('button',{name:'Open',exact:true}).click();const dialog=page.getByRole('dialog',{name:'Changes not saved'});await expect(dialog).toBeVisible();await dialog.getByRole('button',{name:'Stay',exact:true}).click();await expect(editor).toHaveText('Local pending explanation');
  1894 |  await surface.getByRole('button',{name:'Open',exact:true}).click();await dialog.getByRole('button',{name:'Switch anyway',exact:true}).click();
  1895 |  await expect(editor).toContainText('Another own explanation');expect(readerParams(page.url()).get('chapter')??'1').toBe('1');expect(await page.evaluate(()=>history.length)).toBe(before.length);
  1896 | });
  1897 | 
  1898 | test('D4 relevant pagination retains authorized items on failure and retries same cursor',async({page})=>{
  1899 |  let failed=false;const store=await discoveryFixture(page,{context:(r,body,result)=>{if(body.cursor&&!failed){failed=true;return r.fulfill({status:503,json:{code:'studies_storage_unavailable'}});}return r.fulfill({json:{items:[result],next_cursor:body.cursor?null:'next_page'}});}});await firstNote(page);
  1900 |  const surface=page.getByRole('region',{name:'Relevant own notes'});await surface.getByRole('button',{name:'More relevant notes'}).click();await expect(surface.getByRole('alert')).toBeVisible();await expect(surface.getByText('Another own explanation',{exact:true})).toBeVisible();await surface.getByRole('button',{name:'Retry relevant notes'}).click();await expect(surface.getByRole('alert')).toHaveCount(0);expect(store.reads.filter(r=>r.cursor==='next_page')).toHaveLength(2);await expect(surface.getByText('Another own explanation',{exact:true})).toHaveCount(1);
  1901 | });
  1902 | 
  1903 | test('D5 details invalid source preserves candidate and new corrected operation; Cancel changes nothing',async({page})=>{
  1904 |  const store=await setup(page);await collectionStudy(page);const attempts=[];await page.route('**/api/studies/'+study,r=>{if(r.request().method()!=='PUT')return r.fallback();const body=r.request().postDataJSON();attempts.push(body);if(body.source_url.startsWith('javascript:'))return r.fulfill({status:400,json:{code:'scribeswell_personal_notes_input_invalid'}});return r.fallback();});
  1905 |  await page.getByRole('button',{name:'Edit study details'}).click();await page.getByLabel('Introduction',{exact:true}).fill('Candidate intro');await page.getByLabel('Source URL',{exact:true}).fill('javascript:bad');await page.getByRole('button',{name:'Save',exact:true}).click();await expect(page.getByRole('alert')).toContainText('safe HTTP');await expect(page.getByLabel('Introduction',{exact:true})).toHaveValue('Candidate intro');await page.getByLabel('Source URL',{exact:true}).fill('https://example.invalid');await page.getByRole('button',{name:'Save',exact:true}).click();await expect(page.getByRole('link',{name:'Study source'})).toBeVisible();expect(attempts[0].operation_id).not.toBe(attempts[1].operation_id);
  1906 |  await page.getByRole('button',{name:'Edit study details'}).click();await page.getByLabel('Introduction',{exact:true}).fill('Cancelled');await page.getByRole('button',{name:'Cancel',exact:true}).click();expect(store.metadata.introduction).toBe('Candidate intro');expect(attempts).toHaveLength(2);
  1907 | });
  1908 | 
  1909 | test('D6 details conflict deliberately reads current without replacing candidate',async({page})=>{
  1910 |  const store=await setup(page);await collectionStudy(page);let first=true;await page.route('**/api/studies/'+study,r=>{if(r.request().method()==='PUT'&&first){first=false;store.metadata.revision='2';store.metadata.introduction='Remote intro';return r.fulfill({status:409,json:{code:'study_revision_conflict'}});}return r.fallback();});
  1911 |  await page.getByRole('button',{name:'Edit study details'}).click();await page.getByLabel('Introduction',{exact:true}).fill('Mine');await page.getByRole('button',{name:'Save',exact:true}).click();await page.getByRole('button',{name:'Load current details'}).click();await expect(page.getByRole('region',{name:'Current saved study details'})).toContainText('Remote intro');await expect(page.getByLabel('Introduction',{exact:true})).toHaveValue('Mine');await page.getByRole('button',{name:'Save',exact:true}).click();await expect(page.getByRole('form',{name:'Study details'})).toHaveCount(0);expect(store.metadata.introduction).toBe('Mine');
  1912 | });
  1913 | 
  1914 | test('D7 details unknown Cancel reopens original frozen operation without rollback promise',async({page})=>{
  1915 |  await setup(page,{unresolved:true});await collectionStudy(page);const attempts=[];let first=true;await page.route('**/api/studies/'+study,r=>{if(r.request().method()!=='PUT')return r.fallback();attempts.push(r.request().postDataJSON());if(first){first=false;return r.abort('connectionreset');}return r.fallback();});
  1916 |  await page.getByRole('button',{name:'Edit study details'}).click();await page.getByLabel('Introduction',{exact:true}).fill('Frozen');await page.getByRole('button',{name:'Save',exact:true}).click();await expect(page.getByRole('button',{name:'Retry details save'})).toBeVisible();await expect(page.getByText(/An unconfirmed save may still complete/)).toBeVisible();await page.getByRole('button',{name:'Cancel',exact:true}).click();await page.getByRole('button',{name:'Edit study details'}).click();await expect(page.getByLabel('Introduction',{exact:true})).toHaveAttribute('readonly','');await page.getByRole('button',{name:'Retry details save'}).click();await expect(page.getByRole('form',{name:'Study details'})).toHaveCount(0);expect(attempts).toHaveLength(2);expect(attempts[1]).toEqual(attempts[0]);
  1917 | });
  1918 | 
  1919 | test('D8 late context and Preview cannot leak across a new workspace tab',async({page})=>{
  1920 |  let release;await discoveryFixture(page,{beforePreview:()=>new Promise(resolve=>release=resolve)});await firstNote(page);const surface=page.getByRole('region',{name:'Relevant own notes'});await surface.getByRole('button',{name:'Preview',exact:true}).click();await expect.poll(()=>!!release).toBe(true);await page.getByRole('button',{name:'New workspace tab',exact:true}).click();await page.getByRole('dialog',{name:'Book and chapter selector'}).getByRole('button',{name:'Cancel',exact:true}).click();release();await expect(page.getByRole('region',{name:'Relevant note preview'})).toHaveCount(0);
  1921 | });
  1922 | 
  1923 | test('D9 contextual admission denial masks private results without hiding public reading',async({page})=>{
  1924 |  let denied=false;await discoveryFixture(page,{context:(r,body,result)=>r.fulfill(denied?{status:403,json:{code:'studies_access_denied'}}:{json:{items:[result],next_cursor:'next_page'}})});await firstNote(page);const surface=page.getByRole('region',{name:'Relevant own notes'});await expect(surface.getByText('Another own explanation',{exact:true})).toBeVisible();denied=true;await surface.getByRole('button',{name:'More relevant notes'}).click();await expect(page.getByText('Another own explanation',{exact:true})).toHaveCount(0);await expect(page.getByRole('button',{name:'Studies',exact:true})).toBeVisible();
  1925 | });
  1926 | 
  1927 | for(const chapter of [1,2])test('D10 outline note Open reveals only absent relevant passage '+chapter,async({page})=>{
  1928 |  const reference=detailsReference(chapter,1),value={document:{version:2,blocks:[{type:'paragraph',direction:'auto',content:[{type:'text',text:'Reference explanation',marks:[]},{type:'passage_link',reference,label:'Genesis '+chapter+':1'}]}]},connections:[],highlights:[]};
  1929 |  await setup(page,{noteValue:value});await firstNote(page);const before=await page.evaluate(()=>({href:location.href,length:history.length}));await page.getByRole('button',{name:'Back to Studies',exact:true}).click();expect(await page.evaluate(()=>location.href)).toBe(before.href);await page.getByRole('list',{name:'Notes',exact:true}).getByRole('button',{name:/Reference explanation/}).click();await expect(page.getByRole('textbox',{name:'Note text',exact:true})).toContainText('Reference explanation');expect(readerParams(page.url()).get('chapter')??'1').toBe(String(chapter));expect(await page.evaluate(()=>history.length)).toBe(before.length+(chapter===1?0:1));
  1930 | });
  1931 | 
  1932 | test('D11 late relevant Open after tab change cannot select or navigate the new tab',async({page})=>{
  1933 |  let release;await discoveryFixture(page,{beforePreview:()=>new Promise(resolve=>release=resolve)});await firstNote(page);await page.getByRole('region',{name:'Relevant own notes'}).getByRole('button',{name:'Open',exact:true}).click();await expect.poll(()=>!!release).toBe(true);await page.getByRole('button',{name:'New workspace tab',exact:true}).click();await page.getByRole('dialog',{name:'Book and chapter selector'}).getByRole('button',{name:'Cancel',exact:true}).click();const before=page.url();release();await expect.poll(()=>page.url()).toBe(before);await expect(page.getByText('Another study',{exact:true})).toHaveCount(0);
  1934 | });
  1935 | 
  1936 | test('D12 anchored outline Open carries source occurrence in one reader history navigation',async({page})=>{
  1937 |  const reference=detailsReference(2,1),catalogue=require('../../data/reference-catalogue/catalogue.json');
  1938 |  const value={format_version:3,document:{version:1,blocks:[{type:'paragraph',direction:'auto',content:[{type:'text',text:'Anchored explanation',marks:[]}]}]},connections:[],highlights:[{id:'66666666-6666-4666-8666-666666666666',colour:'#FFE066',anchor:{version:1,source_id:'source-v1',source_revision:'11111111-1111-4111-8111-111111111111',catalogue_version:catalogue.catalogue_version,versification_id:reference.versification_id,tokenization_version:'tokens-v1',segments:[{reference,start_position:2,end_position:2,observed_word_ids:['2'],verse_token_digest:'a'.repeat(64)}]}}]};
> 1939 |  await setup(page,{noteValue:value});await firstNote(page);await page.getByRole('button',{name:'Back to Studies',exact:true}).click();const before=await page.evaluate(()=>history.length);await page.getByRole('list',{name:'Notes',exact:true}).getByRole('button',{name:'Anchored explanation',exact:true}).click();await expect.poll(()=>page.evaluate(()=>history.state?.usr?.scribeswellReader?.panes[0].anchor?.word)).toBe(2);expect(await page.evaluate(()=>history.length)).toBe(before+1);
       |                                                                                                                                                                                                                                                                                                                                                                                                                               ^ Error: expect(received).toBe(expected) // Object.is equality
  1940 | });
  1941 | 
  1942 | test('D13 study details stay independent of the autosaved note lane',async({page})=>{
  1943 |  const store=await setup(page);await firstNote(page);await page.getByRole('textbox',{name:'Note text',exact:true}).fill('Independent note writing');await page.getByRole('button',{name:'Back to Studies',exact:true}).click();await page.getByRole('button',{name:'Edit study details'}).click();await page.getByLabel('Introduction',{exact:true}).fill('Whole form candidate');await expect.poll(()=>store.requests.some(r=>r.method==='PUT'&&r.path.endsWith('/notes/'+note))).toBe(true);expect(store.requests.filter(r=>r.method==='PUT'&&r.path.endsWith('/'+study))).toHaveLength(0);await page.getByRole('button',{name:'Save',exact:true}).click();await page.getByRole('list',{name:'Notes',exact:true}).getByRole('button',{name:'Independent note writing',exact:true}).click();await expect(page.getByRole('textbox',{name:'Note text',exact:true})).toHaveText('Independent note writing');await expect(page.getByRole('status').filter({hasText:'Draft saved'})).toBeVisible();
  1944 | });
  1945 | 
  1946 | test('D14 explicit study creation carries optional whole-form details and preserves candidate on refusal',async({page})=>{
  1947 |  await setup(page);const attempts=[];await page.route('**/api/studies',r=>{if(r.request().method()!=='POST')return r.fallback();attempts.push(r.request().postDataJSON());return r.fulfill({status:400,json:{code:'scribeswell_personal_notes_input_invalid'}});});await page.goto('/');await expect(page.getByRole('tablist',{name:'Workspace tabs'})).toHaveAttribute('data-device-ready','true');await page.getByRole('button',{name:'Studies',exact:true}).click();await page.getByRole('button',{name:'Start a study',exact:true}).click();await page.getByLabel('Study title (optional)').fill('Created title');await page.getByLabel('Introduction (optional)').fill('Created intro');await page.getByLabel('Source URL (optional)').fill('https://example.invalid/source');await page.getByRole('button',{name:'Create study',exact:true}).click();await expect(page.getByRole('alert')).toBeVisible();expect(attempts[0]).toMatchObject({title:'Created title',introduction:'Created intro',source_url:'https://example.invalid/source'});await expect(page.getByRole('textbox',{name:'Introduction (optional)'})).toHaveValue('Created intro');
  1948 | });
  1949 | 
  1950 | test('R1 explicit note Open activates a relevant hidden pane without changing positions or adding history',async({page})=>{
  1951 |  await page.setViewportSize({width:390,height:844});const ref=detailsReference(2,1),value={document:{version:2,blocks:[{type:'paragraph',direction:'auto',content:[{type:'text',text:'Hidden pane explanation',marks:[]},{type:'passage_link',label:'Genesis 2:1',reference:ref}]}]},connections:[],highlights:[]};
  1952 |  await setup(page,{noteValue:value});await firstNote(page);await page.getByRole('button',{name:'Add reader pane',exact:true}).click();await page.getByLabel('Passage reference',{exact:true}).fill('Gen 2:1');await page.getByLabel('Passage reference',{exact:true}).press('Enter');await page.getByRole('button',{name:/Show passage 1:/}).click();await page.getByRole('button',{name:'Studies',exact:true}).click();const before=await page.evaluate(()=>({length:history.length,snapshot:history.state.usr.scribeswellReader}));await page.getByRole('list',{name:'Notes',exact:true}).getByRole('button',{name:/Hidden pane explanation/}).click();await expect(page.getByRole('button',{name:/Show passage 2:/})).toHaveAttribute('aria-pressed','true');const after=await page.evaluate(()=>({length:history.length,snapshot:history.state.usr.scribeswellReader}));expect(after.length).toBe(before.length);expect(after.snapshot.panes).toEqual(before.snapshot.panes);await page.getByRole('button',{name:'Return to reader',exact:true}).click();await expect(page.getByRole('region',{name:'Passage 2',exact:true})).toBeVisible();
  1953 | });
  1954 | 
  1955 | for(const status of [503,404])test('R2 Preview has direct truthful recovery for '+status,async({page})=>{
  1956 |  await discoveryFixture(page);let fail=true,reads=0;await page.route('**/api/studies/'+discoveryStudy+'/notes/'+discoveryNote,r=>{reads++;return fail?r.fulfill({status,json:{code:status===404?'resource_unavailable':'studies_storage_unavailable'}}):r.fallback();});await firstNote(page);const surface=page.getByRole('region',{name:'Relevant own notes'});await surface.getByRole('button',{name:'Preview',exact:true}).click();await expect(surface.getByRole('alert')).toBeVisible();if(status===503){await expect(surface.getByRole('button',{name:'Retry Preview',exact:true})).toBeVisible();fail=false;await surface.getByRole('button',{name:'Retry Preview',exact:true}).click();await expect(page.getByRole('region',{name:'Relevant note preview'})).toContainText('Another own explanation');expect(reads).toBe(2);}else{await expect(surface.getByRole('alert')).toContainText('This note is unavailable.');await expect(surface.getByRole('button',{name:'Retry Preview',exact:true})).toHaveCount(0);await expect(surface.getByRole('button',{name:'Preview',exact:true})).toHaveCount(0);await surface.getByRole('button',{name:'Close preview',exact:true}).click();await expect(surface.getByRole('alert')).toHaveCount(0);expect(reads).toBe(1);}
  1957 | });
  1958 | 
  1959 | for(const action of ['Save','Cancel'])test('R3 study details '+action+' restores its own trigger focus',async({page})=>{
  1960 |  await setup(page);await collectionStudy(page);const trigger=page.getByRole('button',{name:'Edit study details',exact:true});await trigger.click();await page.getByLabel('Introduction',{exact:true}).fill('Focus candidate');await page.getByRole('button',{name:action,exact:true}).click();await expect(trigger).toBeFocused();
  1961 | });
  1962 | 
  1963 | test('R4 successful note autosave preserves separate preview and completed pagination',async({page})=>{
  1964 |  const store=await discoveryFixture(page,{context:(r,body,result)=>r.fulfill({json:{items:[result],next_cursor:body.cursor?null:'next_page'}})});await firstNote(page);const surface=page.getByRole('region',{name:'Relevant own notes'});await surface.getByRole('button',{name:'More relevant notes'}).click();await expect(surface.getByRole('button',{name:'More relevant notes'})).toHaveCount(0);await surface.getByRole('button',{name:'Preview',exact:true}).click();const preview=page.getByRole('region',{name:'Relevant note preview'});await expect(preview).toContainText('Another own explanation');await page.getByRole('textbox',{name:'Note text',exact:true}).fill('Successful current-lane save');await expect(page.getByRole('status').filter({hasText:'Draft saved'})).toBeVisible();await expect(preview).toContainText('Another own explanation');expect(store.reads).toHaveLength(2);await expect(surface.getByRole('button',{name:'More relevant notes'})).toHaveCount(0);
  1965 | });
  1966 | 
  1967 | test('R5 unknown creation visibly freezes original complete candidate until reconciliation',async({page})=>{
  1968 |  await setup(page,{unresolved:true});let failed=false;const attempts=[];await page.route('**/api/studies',r=>{if(r.request().method()!=='POST')return r.fallback();attempts.push(r.request().postDataJSON());if(!failed){failed=true;return r.abort('connectionreset');}return r.fallback();});await page.goto('/');await page.getByRole('button',{name:'Studies',exact:true}).click();await page.getByRole('button',{name:'Start a study',exact:true}).click();await page.getByLabel('Study title (optional)').fill('Frozen title');await page.getByLabel('Introduction (optional)').fill('Frozen intro');await page.getByLabel('Source URL (optional)').fill('https://example.invalid/original');await page.getByRole('button',{name:'Create study',exact:true}).click();const retry=page.getByRole('button',{name:'Retry original study creation',exact:true});await expect(retry).toBeEnabled();for(const label of ['Study title (optional)','Introduction (optional)','Source URL (optional)'])await expect(page.getByRole('textbox',{name:label,exact:true})).toHaveAttribute('readonly','');await expect(page.getByText('The original study creation is not yet reconciled. Retry uses these same details.')).toBeVisible();await retry.click();await expect(page.getByRole('button',{name:'Add note',exact:true})).toBeVisible();expect(attempts).toHaveLength(2);expect(attempts[1]).toEqual(attempts[0]);
  1969 | });
  1970 | 
  1971 | test('R6 discovery requests exact complete canonical reference again after deliberate passage change',async({page})=>{
  1972 |  const store=await discoveryFixture(page);await firstNote(page);await expect.poll(()=>store.reads.length).toBe(1);expect(store.reads[0].reference).toEqual(detailsReference(1));await page.getByRole('button',{name:'Analysis',exact:true}).click();await page.getByRole('region',{name:'Passage 1',exact:true}).getByRole('button',{name:/Navigate:/}).click();await page.getByLabel('Passage reference',{exact:true}).fill('Gen 2:1');await page.getByLabel('Passage reference',{exact:true}).press('Enter');await page.getByRole('button',{name:'Analysis',exact:true}).click();await expect.poll(()=>store.reads.length).toBe(2);expect(store.reads[1].reference).toEqual(detailsReference(2,1));
  1973 | });
  1974 | 
  1975 | test('R7 empty readable context page with continuation offers More without a global empty claim',async({page})=>{
  1976 |  await discoveryFixture(page,{context:(r,body,result)=>r.fulfill({json:{items:body.cursor?[result]:[],next_cursor:body.cursor?null:'raw_scan_cursor'}})});await firstNote(page);const surface=page.getByRole('region',{name:'Relevant own notes'});await expect(surface.getByText('No readable notes on this page.',{exact:true})).toBeVisible();await expect(surface.getByText('No relevant saved notes.',{exact:true})).toHaveCount(0);await surface.getByRole('button',{name:'More relevant notes'}).click();await expect(surface.getByText('Another own explanation',{exact:true})).toBeVisible();
  1977 | });
  1978 | 
  1979 | test('R8 Switch anyway unmounts source editor while destination read waits and preserves original unknown operation',async({page})=>{
  1980 |  let release;const store=await discoveryFixture(page,{failPut:503,beforePreview:()=>new Promise(resolve=>release=resolve)});await firstNote(page);const editor=page.getByRole('textbox',{name:'Note text',exact:true});await editor.fill('Original unknown source save');await expect(page.getByRole('status').filter({hasText:'Changes not saved'})).toBeVisible();const original=structuredClone(store.requests.find(r=>r.method==='PUT'&&r.path.endsWith('/notes/'+note)).payload);
  1981 |  await page.getByRole('region',{name:'Relevant own notes'}).getByRole('button',{name:'Open',exact:true}).click();const guard=page.getByRole('dialog',{name:'Changes not saved'});await expect(guard).toBeVisible();await guard.getByRole('button',{name:'Switch anyway',exact:true}).click();await expect.poll(()=>!!release).toBe(true);
  1982 |  await expect(page.locator('[aria-label="Note text"]')).toHaveCount(0);await expect(page.getByRole('region',{name:'Note editor',exact:true})).toHaveCount(0);await expect(guard).toHaveCount(0);const recovery=page.getByRole('button',{name:'Recover note save 1',exact:true});await expect(recovery).toBeVisible();
  1983 |  // Ordinary UI has no mounted source editor to receive new input/composition.
  1984 |  // Reconciliation remains available under the original operation while read waits.
  1985 |  await recovery.click();await expect.poll(()=>store.requests.filter(r=>r.method==='PUT'&&r.path.endsWith('/notes/'+note)).length).toBe(2);expect(store.requests.filter(r=>r.method==='PUT'&&r.path.endsWith('/notes/'+note))[1].payload).toEqual(original);await expect(page.locator('[aria-label="Note text"]')).toHaveCount(0);
  1986 |  release();await expect(editor).toContainText('Another own explanation');await expect(guard).toHaveCount(0);
  1987 | });
  1988 | 
  1989 | test('note text wire grammar rejects NUL and preserves newlines and combining marks',async({page})=>{
  1990 |  await setup(page);await page.goto('/');
  1991 |  const values=['before\u0000after','First\nבְּרֵאשִׁית\ne\u0301'].map(text=>({document:{version:1,blocks:[{type:'paragraph',direction:'rtl',content:[{type:'text',text,marks:[]}]}]},connections:[],highlights:[]}));
  1992 |  const actual=await page.evaluate(async values=>{const {isReadableNoteValue}=await import('/src/lib/note-value.ts');return values.map(isReadableNoteValue);},values);
  1993 |  expect(actual).toEqual([false,true]);
  1994 | });
  1995 | 
  1996 | 
  1997 | test('editor rejects impossible scalar input locally and retains correctable DOM',async({page})=>{
  1998 |  const store=await setup(page);await firstNote(page);const editor=page.getByRole('textbox',{name:'Note text',exact:true});
  1999 |  for(const invalid of ['Before\u0000after','Before\uD800after','Before\uDC00after']){
  2000 |   const before=store.requests.filter(r=>r.method==='PUT').length;
  2001 |   await editor.evaluate((el,text)=>{el.replaceChildren(document.createTextNode(text));el.dispatchEvent(new InputEvent('input',{bubbles:true,inputType:'insertText'}));},invalid);
  2002 |   await expect(page.getByRole('status').filter({hasText:'Changes not saved'})).toBeVisible();
  2003 |   await page.waitForTimeout(700);expect(store.requests.filter(r=>r.method==='PUT')).toHaveLength(before);
  2004 |   await page.getByRole('button',{name:'Retry',exact:true}).click();await page.waitForTimeout(100);
  2005 |   expect(store.requests.filter(r=>r.method==='PUT')).toHaveLength(before);expect(await editor.textContent()).toBe(invalid);
  2006 |  }
  2007 |  const corrected='Useful\nבְּרֵאשִׁית e\u0301 😀';
  2008 |  await editor.evaluate((el,text)=>{el.replaceChildren(document.createTextNode(text));el.dispatchEvent(new InputEvent('input',{bubbles:true,inputType:'insertText'}));},corrected);
  2009 |  await page.getByRole('button',{name:'Retry',exact:true}).click();
  2010 |  await expect(page.getByRole('status').filter({hasText:'Draft saved'})).toBeVisible();
  2011 |  const saved=store.requests.filter(r=>r.method==='PUT').at(-1).payload.value;
  2012 |  expect(saved.document.blocks[0].content.map(n=>n.text).join('')).toBe(corrected);
  2013 | });
  2014 | 
  2015 | test('exported note scalar schema uses JavaScript code-unit semantics',async({page})=>{
  2016 |  const fs=require('node:fs'),path=require('node:path');const schema=JSON.parse(fs.readFileSync(path.join(__dirname,'../../contracts/personal-notes-v1.openapi.json'),'utf8'));
  2017 |  const patterns=[];function visit(node){if(!node||typeof node!=='object')return;if(node.description?.includes('Unicode scalar')||node.properties?.text){const field=node.properties?.text??node;if(field.not?.pattern)patterns.push(field.not.pattern);}for(const value of Object.values(node))if(value&&typeof value==='object')visit(value);}visit(schema);
  2018 |  expect(patterns.length).toBeGreaterThan(0);
  2019 |  const results=await page.evaluate(patterns=>patterns.map(pattern=>['x\u0000y','x\uD800y','x\uDC00y','x😀y','x\ne\u0301'].map(value=>!new RegExp(pattern).test(value))),patterns);
  2020 |  expect(results).toEqual(patterns.map(()=>[false,false,false,true,true]));
  2021 | });
  2022 | 
  2023 | 
  2024 | for(const state of ['clean','unknown'])test(`same current ${state} note reentry preserves lane and original operation`,async({page})=>{
  2025 |  const {requests}=await setup(page,state==='unknown'?{dropPut:true,unresolved:true}:{});await firstNote(page);
  2026 |  const editor=page.getByRole('textbox',{name:'Note text',exact:true});await editor.fill('Retained '+state+' body');
  2027 |  await expect(page.getByRole('status').filter({hasText:state==='clean'?'Draft saved':'Changes not saved'})).toBeVisible();
  2028 |  const writes=requests.filter(r=>r.method==='PUT');expect(writes).toHaveLength(1);const original=structuredClone(writes[0].payload);
  2029 |  const reads=requests.filter(r=>r.path.endsWith('/notes/'+note)&&r.method==='GET').length;
  2030 |  await page.getByRole('button',{name:'Back to Studies',exact:true}).click();await page.getByRole('list',{name:'Notes',exact:true}).locator(':scope > li > button:first-child').click();
  2031 |  await expect(page.getByRole('dialog',{name:'Changes not saved'})).toHaveCount(0);await expect(editor).toHaveText('Retained '+state+' body');
  2032 |  expect(requests.filter(r=>r.path.endsWith('/notes/'+note)&&r.method==='GET')).toHaveLength(reads);
  2033 |  if(state==='unknown'){await page.getByRole('button',{name:'Retry',exact:true}).click();await expect(page.getByRole('status').filter({hasText:'Draft saved'})).toBeVisible();expect(requests.filter(r=>r.method==='PUT').map(r=>r.payload)).toEqual([original,original]);}
  2034 |  else expect(requests.filter(r=>r.method==='PUT')).toHaveLength(1);
  2035 | });
  2036 | 
```