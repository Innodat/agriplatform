const {
  test,
  expect
} = require('@playwright/test');
const book = {
  id: 1,
  osis_id: 'Gen',
  name_en: 'Genesis',
  name_he: 'בראשית',
  testament: 'OT',
  book_order: 1,
  division: 'torah'
};
async function setup(page) {
  await page.route('http://127.0.0.1:8001/**', r => r.fulfill({
    json: []
  }));
  await page.route('**/api/bible/**', r => {
    const p = new URL(r.request().url()).pathname;
    if (p.endsWith('/books')) return r.fulfill({
      json: {
        data: [book],
        total: 1
      }
    });
    if (p.endsWith('/verses')) return r.fulfill({
      json: {
        data: Array.from({
          length: 31
        }, (_, i) => ({
          id: i + 1,
          verse_num: i + 1,
          book_id: 1,
          chapter_num: 1,
          words: [{
            id: i + 1,
            position: 1,
            surface_he: 'אב',
            display_he: 'אב',
            lemma_strong: 'H1',
            morph_code: 'HNcmsa'
          }]
        })),
        total: 31
      }
    });
    return r.fulfill({
      json: {
        ...book,
        chapters: [{
          id: 1,
          chapter_num: 1
        }, {
          id: 2,
          chapter_num: 2
        }]
      }
    });
  });
}
async function add(page) {
  await page.getByRole('button', {
    name: 'Add reader pane',
    exact: true
  }).click();
  await page.getByRole('dialog', {
    name: 'Book and chapter selector'
  }).getByRole('button', {
    name: 'Cancel',
    exact: true
  }).click();
}
test('four panes preserve stable identities and require explicit capacity replacement', async ({
  page
}) => {
  await setup(page);
  await page.goto('/');
  for (let i = 0; i < 3; i++) await add(page);
  await expect(page.locator('[data-pane-key][data-reader-pane]')).toHaveCount(4);
  const keys = await page.locator('[data-reader-pane]').evaluateAll(ns => ns.map(n => n.dataset.paneKey));
  await page.getByRole('button', {
    name: 'Add reader pane',
    exact: true
  }).click();
  const dialog = page.getByRole('dialog', {
    name: 'Choose passage to replace'
  });
  await expect(dialog).toBeVisible();
  await dialog.getByRole('button', {
    name: 'Cancel',
    exact: true
  }).click();
  expect(await page.locator('[data-reader-pane]').evaluateAll(ns => ns.map(n => n.dataset.paneKey))).toEqual(keys);
  await page.goBack();
  await expect(page.locator('[data-reader-pane]')).toHaveCount(3);
  await page.goForward();
  await expect(page.locator('[data-reader-pane]')).toHaveCount(4);
  expect(await page.locator('[data-reader-pane]').evaluateAll(ns => ns.map(n => n.dataset.paneKey))).toEqual(keys);
});
test('closed codec refuses malformed links and retains complete ranges', async ({
  page
}) => {
  await setup(page);
  await page.goto('/');
  const result = await page.evaluate(async () => {
    const m = await import('/src/lib/reader-layout.ts'),
      r = await import('/src/lib/passage-references.ts');
    const ref = r.parseReference('Genesis 1:2–2:3');
    const p = new URLSearchParams(m.readerSearch('?other=kept', [ref], 0));
    return {
      good: m.parseReaderURL(p),
      bad: m.parseReaderURL(new URLSearchParams('reader={}&book=Exod')),
      duplicate: m.parseReaderURL(new URLSearchParams('reader={}&reader={}')),
      primitive: m.snapshotState(['keep'], {}),
      other: p.get('other')
    };
  });
  expect(result.good.refs[0].target.end).toEqual({
    chapter: 2,
    verse: 3
  });
  expect(result.bad.invalid).toBe(true);
  expect(result.duplicate.invalid).toBe(true);
  expect(result.primitive).toEqual(['keep']);
  expect(result.other).toBe('kept');
});
test('controller preserves foreign native state and uses one push per deliberate transition', async ({
  page
}) => {
  await setup(page);
  await page.goto('/?foreign=keep#fragment');
  await page.evaluate(() => {
    history.replaceState({
      ...history.state,
      outer: {
        keep: true
      },
      usr: {
        foreign: 'retained'
      }
    }, '');
    window.__pushes = 0;
    const push = history.pushState.bind(history);
    history.pushState = (...args) => {
      window.__pushes++;
      return push(...args);
    };
  });
  await add(page);
  expect(await page.evaluate(() => window.__pushes)).toBe(1);
  expect(await page.evaluate(() => history.state.outer)).toEqual({
    keep: true
  });
  expect(await page.evaluate(() => history.state.usr.foreign)).toBe('retained');
  expect(new URL(page.url()).searchParams.get('foreign')).toBe('keep');
  expect(new URL(page.url()).hash).toBe('#fragment');
  await page.getByRole('button', {
    name: 'Close passage 2',
    exact: true
  }).click();
  expect(await page.evaluate(() => window.__pushes)).toBe(2);
  await expect(page.getByRole('button', {
    name: 'Close passage 1',
    exact: true
  })).toHaveCount(0);
  await page.goBack();
  await expect(page.locator('[data-reader-pane]')).toHaveCount(2);
  await page.goForward();
  await expect(page.locator('[data-reader-pane]')).toHaveCount(1);
  await page.goBack();
  await expect(page.locator('[data-reader-pane]')).toHaveCount(2);
});
for (const usr of [17, ['foreign']]) test('non-record Router usr survives add and repeated replay ' + JSON.stringify(usr), async ({
  page
}) => {
  await setup(page);
  await page.goto('/');
  await page.evaluate(usr => history.replaceState({
    ...history.state,
    usr,
    foreign: 'outer'
  }, ''), usr);
  await add(page);
  const keys = await page.locator('[data-reader-pane]').evaluateAll(ns => ns.map(n => n.dataset.paneKey));
  expect(await page.evaluate(() => history.state.usr)).toEqual(usr);
  expect(await page.evaluate(() => history.state.foreign)).toBe('outer');
  await page.goBack();
  await expect(page.locator('[data-reader-pane]')).toHaveCount(1);
  await page.goForward();
  await expect(page.locator('[data-reader-pane]')).toHaveCount(2);
  expect(await page.locator('[data-reader-pane]').evaluateAll(ns => ns.map(n => n.dataset.paneKey))).toEqual(keys);
});
test('independent same-reference anchors survive repeated browser replay', async ({
  page
}) => {
  await setup(page);
  await page.goto('/');
  await add(page);
  const scrolls = page.locator('[data-reader-scroll]');
  const switcher = page.getByRole('button', {
    name: /Show passage 1:/
  });
  if (await switcher.isVisible()) await switcher.click();
  await scrolls.nth(0).evaluate(el => el.scrollTop = 120);
  if (await switcher.isVisible()) await page.getByRole('button', {
    name: /Show passage 2:/
  }).click();
  await scrolls.nth(1).evaluate(el => el.scrollTop = 280);
  await add(page);
  await page.goBack();
  await expect(page.locator('[data-reader-pane]')).toHaveCount(2);
  await expect.poll(() => scrolls.nth(1).evaluate(el => el.scrollTop)).toBe(280);
  if (await switcher.isVisible()) await switcher.click();
  await expect.poll(() => scrolls.nth(0).evaluate(el => el.scrollTop)).toBe(120);
  await page.goForward();
  await expect(page.locator('[data-reader-pane]')).toHaveCount(3);
  await page.goBack();
  await expect(page.locator('[data-reader-pane]')).toHaveCount(2);
  if (await switcher.isVisible()) await switcher.click();
  await expect.poll(() => scrolls.nth(0).evaluate(el => el.scrollTop)).toBe(120);
});
test('codec rejects closed snapshot violations and URL bounds without private fields', async ({
  page
}) => {
  await setup(page);
  await page.goto('/');
  const r = await page.evaluate(async () => {
    const m = await import('/src/lib/reader-layout.ts'),
      p = await import('/src/lib/passage-references.ts'),
      ref = p.chapterReference('Gen', 1),
      url = {
        refs: [ref],
        active: 0,
        invalid: false
      },
      snapshot = {
        v: 1,
        tabKey: 'tab',
        activePaneKey: 'pane',
        panes: [{
          paneKey: 'pane',
          ref,
          anchor: {
            chapter: 1,
            verse: 1,
            word: 1,
            offset: -4
          }
        }]
      };
    return {
      valid: !!m.parseSnapshot(snapshot, url),
      extra: !!m.parseSnapshot({
        ...snapshot,
        note: 'private'
      }, url),
      offset: !!m.parseSnapshot({
        ...snapshot,
        panes: [{
          ...snapshot.panes[0],
          anchor: {
            chapter: 1,
            verse: 1,
            offset: 513
          }
        }]
      }, url),
      wrong: !!m.parseSnapshot({
        ...snapshot,
        activePaneKey: 'missing'
      }, url),
      large: m.parseReaderURL(new URLSearchParams({
        reader: ' '.repeat(4097)
      })).invalid,
      newPrecedence: m.parseReaderURL(new URLSearchParams(m.readerSearch('?book=Exod', [ref], 0))).refs[0].book_id
    };
  });
  expect(r).toEqual({
    valid: true,
    extra: false,
    offset: false,
    wrong: false,
    large: true,
    newPrecedence: 'Gen'
  });
});
test('reduced-height four pane layout offers named switcher and no viewport overflow', async ({
  page
}) => {
  await setup(page);
  await page.setViewportSize({
    width: 1100,
    height: 450
  });
  await page.goto('/');
  for (let i = 0; i < 3; i++) await add(page);
  await expect(page.getByRole('group', {
    name: 'Visible passage'
  })).toBeVisible();
  await expect(page.locator('[data-reader-pane]:visible')).toHaveCount(1);
  expect(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth)).toBe(false);
});
test('Add duplicates the complete canonical range and replacement changes only the explicitly chosen pane', async ({
  page
}) => {
  await setup(page);
  await page.goto('/?book=Gen&chapter=1&verse=2&EndChapter=2&EndVerse=3');
  for (let i = 0; i < 3; i++) await add(page);
  const before = await page.locator('[data-reader-pane]').evaluateAll(ns => ns.map(n => n.dataset.paneKey));
  const layout = JSON.parse(new URL(page.url()).searchParams.get('reader'));
  expect(layout.panes.every(p => p.ref.target.end.chapter === 2 && p.ref.target.end.verse === 3)).toBe(true);
  await page.getByRole('button', {
    name: 'Add reader pane',
    exact: true
  }).click();
  await page.getByRole('dialog', {
    name: 'Choose passage to replace'
  }).getByRole('button', {
    name: 'Replace passage 1: Genesis 1:2–2:3',
    exact: true
  }).click();
  await expect(page.getByRole('dialog', {
    name: 'Book and chapter selector'
  })).toBeVisible();
  await page.getByRole('dialog', {
    name: 'Book and chapter selector'
  }).getByRole('button', {
    name: 'Cancel',
    exact: true
  }).click();
  expect(await page.locator('[data-reader-pane]').evaluateAll(ns => ns.map(n => n.dataset.paneKey))).toEqual(before);
  expect(JSON.parse(new URL(page.url()).searchParams.get('reader')).active).toBe(0);
  await page.getByRole('button', {
    name: 'Close passage 1',
    exact: true
  }).click();
  const after = await page.locator('[data-reader-pane]').evaluateAll(ns => ns.map(n => n.dataset.paneKey));
  expect(after).toEqual(before.slice(1));
  expect(JSON.parse(new URL(page.url()).searchParams.get('reader')).active).toBe(0);
});
test('layout clamps retain intended anchor while a subsequent user movement replaces it', async ({
  page
}) => {
  await setup(page);
  await page.setViewportSize({
    width: 1100,
    height: 500
  });
  await page.goto('/');
  const scroll = page.locator('[data-reader-scroll]');
  await expect(page.locator('[data-word-position]').first()).toBeVisible();
  await scroll.evaluate(el => el.scrollTop = el.scrollHeight);
  const before = await scroll.evaluate(el => el.scrollTop);
  await page.setViewportSize({
    width: 1100,
    height: 900
  });
  await page.setViewportSize({
    width: 1100,
    height: 500
  });
  await expect.poll(() => scroll.evaluate(el => el.scrollTop)).toBe(before);
  await scroll.evaluate(el => el.scrollTop = 120);
  await page.setViewportSize({
    width: 1100,
    height: 900
  });
  await page.setViewportSize({
    width: 1100,
    height: 500
  });
  await expect.poll(() => scroll.evaluate(el => el.scrollTop)).toBe(120);
});
test('closing an inactive pane preserves active survivor and native default-key semantics', async ({
  page
}) => {
  await setup(page);
  await page.setViewportSize({
    width: 1600,
    height: 1000
  });
  await page.goto('/');
  await page.evaluate(() => {
    const {
      key,
      ...state
    } = history.state;
    history.replaceState({
      ...state,
      foreign: 'default-entry'
    }, '');
  });
  await add(page);
  await add(page);
  const keys = await page.locator('[data-reader-pane]').evaluateAll(ns => ns.map(n => n.dataset.paneKey));
  await page.getByRole('button', {
    name: 'Close passage 1',
    exact: true
  }).click();
  const state = await page.evaluate(() => history.state.usr.scribeswellReader);
  expect(state.activePaneKey).toBe(keys[2]);
  expect(state.panes.map(p => p.paneKey)).toEqual(keys.slice(1));
  await page.goBack();
  await expect(page.locator('[data-reader-pane]')).toHaveCount(3);
  await page.goBack();
  await expect(page.locator('[data-reader-pane]')).toHaveCount(2);
  await page.goBack();
  await expect(page.locator('[data-reader-pane]')).toHaveCount(1);
  expect(await page.evaluate(() => Object.hasOwn(history.state, 'key'))).toBe(false);
  expect(await page.evaluate(() => history.state.foreign)).toBe('default-entry');
});
test('a deferred outgoing checkpoint cannot overwrite the new browser entry', async ({
  page
}) => {
  await setup(page);
  await page.goto('/');
  const scroll = page.locator('[data-reader-scroll]');
  await expect(page.locator('[data-word-position]').first()).toBeVisible();
  await scroll.dispatchEvent('wheel', {
    deltaY: 120
  });
  await scroll.evaluate(el => el.scrollTop = 120);
  await add(page);
  const key = await page.evaluate(() => history.state.key);
  await page.waitForTimeout(180);
  expect(await page.evaluate(() => history.state.key)).toBe(key);
  expect(await page.evaluate(() => history.state.usr.scribeswellReader.panes.length)).toBe(2);
  await page.goBack();
  await expect(page.locator('[data-reader-pane]')).toHaveCount(1);
  await expect.poll(() => page.locator('[data-reader-scroll]').evaluate(el => el.scrollTop)).toBe(120);
});
test('structured foreign Router user values remain unmodified by checkpoints and navigation', async ({
  page
}) => {
  await setup(page);
  await page.goto('/');
  const result = await page.evaluate(async () => {
    const m = await import('/src/lib/reader-layout.ts');
    return [new Date('2026-10-26T00:00:00Z'), new Map([['foreign', 42]]), new Set(['foreign']), ['foreign'], 17, null].map(value => {
      const merged = m.snapshotState(value, {
        v: 1
      });
      return value === null ? merged.scribeswellReader.v === 1 : merged === value;
    });
  });
  expect(result).toEqual([true, true, true, true, true, true]);
  await page.evaluate(() => history.replaceState({
    ...history.state,
    usr: new Map([['foreign', 42]])
  }, ''));
  await add(page);
  expect(await page.evaluate(() => history.state.usr instanceof Map && history.state.usr.get('foreign') === 42)).toBe(true);
  await page.goBack();
  await expect(page.locator('[data-reader-pane]')).toHaveCount(1);
  expect(await page.evaluate(() => history.state.usr instanceof Map && history.state.usr.get('foreign') === 42)).toBe(true);
});
test('four-pane row qualification reserves two hundred usable text pixels after controls', async ({
  page
}) => {
  await setup(page);
  await page.setViewportSize({
    width: 1100,
    height: 650
  });
  await page.goto('/');
  for (let i = 0; i < 3; i++) await add(page);
  const visible = page.locator('[data-reader-pane]:visible');
  if ((await visible.count()) > 1) {
    const heights = await page.locator('[data-reader-scroll]:visible').evaluateAll(ns => ns.map(n => n.clientHeight));
    expect(Math.min(...heights)).toBeGreaterThanOrEqual(200);
  } else await expect(page.getByRole('group', {
    name: 'Visible passage'
  })).toBeVisible();
});
test('capacity confirmation refuses a different replayed layout after close-add cycles', async ({
  page
}) => {
  await setup(page);
  await page.goto('/');
  for (let i = 0; i < 3; i++) await add(page);
  for (let i = 0; i < 3; i++) {
    await page.getByRole('button', {
      name: 'Close passage 4',
      exact: true
    }).click();
    await add(page);
  }
  await page.getByRole('button', {
    name: 'Add reader pane',
    exact: true
  }).click();
  const capacity = page.getByRole('dialog', {
    name: 'Choose passage to replace'
  });
  await expect(capacity).toBeVisible();
  await page.goBack();
  await expect(page.locator('[data-reader-pane]')).toHaveCount(3);
  const before = page.url(),
    idx = await page.evaluate(() => history.state.idx);
  await capacity.getByRole('button', {
    name: 'Replace passage 1: Genesis 1',
    exact: true
  }).click();
  expect(page.url()).toBe(before);
  expect(await page.evaluate(() => history.state.idx)).toBe(idx);
  await expect(page.getByRole('dialog', {
    name: 'Book and chapter selector'
  })).toHaveCount(0);
});
test('closed codec enforces pane, active, identity and canonical anchor boundaries', async ({
  page
}) => {
  await setup(page);
  await page.goto('/');
  const r = await page.evaluate(async () => {
    const m = await import('/src/lib/reader-layout.ts'),
      p = await import('/src/lib/passage-references.ts'),
      ref = p.chapterReference('Gen', 1);
    const url = (n, active = 0, extra = {}) => m.parseReaderURL(new URLSearchParams({
      reader: JSON.stringify({
        v: 1,
        panes: Array.from({
          length: n
        }, () => ({
          ref
        })),
        active,
        ...extra
      })
    }));
    const state = {
        v: 1,
        tabKey: 'tab',
        activePaneKey: 'a',
        panes: [{
          paneKey: 'a',
          ref,
          anchor: {
            chapter: 1,
            verse: 1,
            word: 1,
            offset: 0
          }
        }]
      },
      valid = s => !!m.parseSnapshot(s, {
        refs: s.panes.map(x => x.ref),
        active: 0,
        invalid: false
      });
    const anchor = x => valid({
      ...state,
      panes: [{
        ...state.panes[0],
        anchor: x
      }]
    });
    const key128 = '界'.repeat(128),
      keyed = {
        ...state,
        tabKey: key128,
        activePaneKey: key128,
        panes: [{
          ...state.panes[0],
          paneKey: key128
        }]
      },
      multiple = {
        ...state,
        panes: [state.panes[0], state.panes[0]]
      };
    const richRef = p.parseReference('Psalms 119:176–150:6'),
      panes = Array.from({
        length: 4
      }, (_, i) => ({
        paneKey: '界'.repeat(127) + i,
        ref: richRef,
        anchor: {
          chapter: 119,
          verse: 176,
          word: 4096,
          offset: -512
        }
      })),
      multibyte = {
        v: 1,
        tabKey: key128,
        activePaneKey: panes[0].paneKey,
        panes
      };
    const tooLarge = {
      ...state,
      tabKey: '界'.repeat(4096)
    };
    return {
      url: [url(1).invalid, url(4).invalid, url(5).invalid, url(0).invalid, url(4, -1).invalid, url(4, 4).invalid, url(1, 0, {
        v: 2
      }).invalid, url(1, 0, {
        private: 'refused'
      }).invalid],
      keys: [valid(keyed), valid({
        ...keyed,
        tabKey: key128 + 'x'
      }), valid(multiple)],
      anchors: [anchor({
        chapter: 1,
        verse: 1,
        word: 0,
        offset: 0
      }), anchor({
        chapter: 1,
        verse: 1,
        word: 4097,
        offset: 0
      }), anchor({
        chapter: 1,
        verse: 32,
        offset: 0
      }), anchor({
        chapter: 2,
        verse: 1,
        offset: 0
      }), anchor({
        chapter: 1,
        verse: 1,
        word: 4096,
        offset: 512
      })],
      multibyte: valid(multibyte),
      bytes: new TextEncoder().encode(JSON.stringify(multibyte)).length,
      oversize: valid(tooLarge)
    };
  });
  expect(r.url).toEqual([false, false, true, true, true, true, true, true]);
  expect(r.keys).toEqual([true, false, false]);
  expect(r.anchors).toEqual([false, false, false, false, true]);
  expect(r.multibyte).toBe(true);
  expect(r.bytes).toBeLessThan(8192);
  expect(r.oversize).toBe(false);
});
test('initial StrictMode entry keeps one committed pane identity while data becomes ready', async ({
  page
}) => {
  await setup(page);
  await page.addInitScript(() => {
    window.__initialPaneKeys = new Set();
    new MutationObserver(records => {
      for (const record of records) for (const node of [...record.addedNodes, ...record.removedNodes]) {
        if (!(node instanceof Element)) continue;
        const panes = [...(node.matches('[data-reader-pane]') ? [node] : []), ...node.querySelectorAll('[data-reader-pane]')];
        for (const pane of panes) window.__initialPaneKeys.add(pane.dataset.paneKey);
      }
    }).observe(document, {
      childList: true,
      subtree: true
    });
  });
  await page.goto('/');
  await expect(page.locator('[data-reader-scroll][data-ready="true"]')).toBeVisible();
  expect(await page.evaluate(() => window.__initialPaneKeys.size)).toBe(1);
});
test('painted ready text retains actual wheel input without a late seek', async ({
  page
}) => {
  await setup(page);
  await page.setViewportSize({
    width: 1100,
    height: 500
  });
  await page.goto('/');
  await expect(page.locator('[data-reader-scroll][data-ready="true"]')).toBeVisible();
  await page.evaluate(() => document.fonts.ready);
  const scroll = page.locator('[data-reader-scroll]');
  await scroll.hover();
  await page.mouse.wheel(0, 120);
  await expect.poll(() => scroll.evaluate(n => n.scrollTop)).toBe(120);
  await page.evaluate(() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve))));
  expect(await scroll.evaluate(n => n.scrollTop)).toBe(120);
});
test('available-container geometry supplies three columns, wrapping and four-pane two-by-two with tools', async ({
  page
}) => {
  await setup(page);
  await page.setViewportSize({
    width: 1500,
    height: 1000
  });
  await page.goto('/');
  await add(page);
  await add(page);
  const shape = () => page.locator('[data-reader-pane]:visible').evaluateAll(ns => {
    const rs = ns.map(n => n.getBoundingClientRect());
    return {
      count: rs.length,
      columns: new Set(rs.map(r => Math.round(r.left))).size,
      rows: new Set(rs.map(r => Math.round(r.top))).size,
      minWidth: Math.min(...rs.map(r => r.width))
    };
  });
  async function grid(count, columns, rows) {
    await expect.poll(async () => {
      const s = await shape();
      return [s.count, s.columns, s.rows];
    }).toEqual([count, columns, rows]);
    expect((await shape()).minWidth).toBeGreaterThanOrEqual(320);
  }
  await grid(3, 3, 1);
  await page.setViewportSize({
    width: 1000,
    height: 1000
  });
  await grid(3, 2, 2);
  await page.setViewportSize({
    width: 1200,
    height: 1000
  });
  await grid(3, 3, 1);
  await page.getByRole('button', {
    name: 'Analysis',
    exact: true
  }).click();
  await grid(3, 2, 2);
  await add(page);
  await grid(4, 2, 2);
  await page.getByRole('button', {
    name: 'Analysis',
    exact: true
  }).click();
  await grid(4, 2, 2);
});
test('review: missing restored anchor falls back to the explicit target verse', async ({
  page
}) => {
  await setup(page);
  await page.setViewportSize({
    width: 1100,
    height: 500
  });
  await page.route('**/api/bible/books/Gen/chapters/1/verses', route => route.fulfill({
    json: {
      data: Array.from({
        length: 29
      }, (_, i) => ({
        id: i + 1,
        verse_num: i + 1,
        book_id: 1,
        chapter_num: 1,
        words: [{
          id: 1000 + i,
          position: 1,
          surface_he: 'אב',
          display_he: 'אב',
          lemma_strong: 'H1',
          morph_code: 'HNcmsa'
        }]
      })),
      total: 29
    }
  }));
  await page.goto('/?book=Gen&chapter=1&verse=20');
  await page.evaluate(async () => {
    const {
      parseReference
    } = await import('/src/lib/passage-references.ts');
    history.replaceState({
      ...history.state,
      usr: {
        ...history.state.usr,
        scribeswellReader: {
          v: 1,
          tabKey: 'restore-tab',
          activePaneKey: 'restore-pane',
          panes: [{
            paneKey: 'restore-pane',
            ref: parseReference('Genesis 1:20'),
            anchor: {
              chapter: 1,
              verse: 30,
              word: 7,
              offset: 40
            }
          }]
        }
      }
    }, '');
  });
  await page.reload();
  const scroll = page.locator('[data-reader-scroll]');
  await expect.poll(() => scroll.evaluate(node => {
    const verse = node.querySelector('[data-verse="20"]');
    return verse ? Math.round(verse.getBoundingClientRect().top - node.getBoundingClientRect().top) : null;
  })).toBe(0);
});
for (const target of ['active', 'inactive']) test(`review: closing a focused ${target} control hands focus to the active survivor`, async ({
  page
}) => {
  await setup(page);
  await page.setViewportSize({
    width: 1600,
    height: 1000
  });
  await page.goto('/');
  await add(page);
  await add(page);
  const keys = await page.locator('[data-reader-pane]').evaluateAll(nodes => nodes.map(node => node.dataset.paneKey));
  const close = page.getByRole('button', {
    name: `Close passage ${target === 'active' ? 3 : 2}`,
    exact: true
  });
  const survivor = keys[target === 'active' ? 1 : 2];
  const survivorPane = page.locator(`[data-reader-pane][data-pane-key="${survivor}"]`);
  await survivorPane.locator('[data-reader-scroll]').evaluate(node => node.scrollTop = 120);
  const idx = await page.evaluate(() => history.state.idx);
  await close.focus();
  await close.press('Enter');
  await expect(survivorPane.getByRole('button', {
    name: /Navigate:/
  })).toBeFocused();
  await expect(survivorPane).toHaveAttribute('aria-current', 'true');
  expect(await survivorPane.locator('[data-reader-scroll]').evaluate(node => node.scrollTop)).toBe(120);
  expect(await page.evaluate(() => history.state.idx)).toBe(idx + 1);
  const unrelated = page.getByRole('button', {
    name: 'Add reader pane',
    exact: true
  });
  await unrelated.focus();
  await page.locator('[data-close-pane]').first().evaluate(node => node.click());
  await expect(unrelated).toBeFocused();
});
for (const initialPane of ['active', 'inactive']) test(`review: a scrollbar gesture checkpoints movement after one second through completion from ${initialPane} pane`, async ({
  page
}) => {
  await setup(page);
  await page.setViewportSize({width: 1600, height: 1000});
  await page.goto('/');
  if (initialPane === 'inactive') await add(page);
  const pane = page.locator('[data-reader-pane]').first();
  await expect(pane.locator('[data-reader-scroll][data-ready="true"]')).toBeVisible();
  await page.evaluate(() => document.fonts.ready);
  await page.clock.install();
  const scroll = pane.locator('[data-reader-scroll]');
  const before = await page.evaluate(() => ({key: history.state.key, idx: history.state.idx}));
  await scroll.dispatchEvent('pointerdown', {
    pointerId: 73,
    button: 0
  });
  await expect(pane).toHaveAttribute('aria-current', 'true');
  const activated = await page.evaluate(() => ({key: history.state.key, idx: history.state.idx}));
  expect(activated.idx).toBe(before.idx);
  if (initialPane === 'inactive') expect(activated.key).not.toBe(before.key);
  await scroll.evaluate(node => {
    node.scrollTop = 120;
    node.dispatchEvent(new Event('scroll'));
  });
  await page.clock.runFor(1500);
  await scroll.evaluate(node => {
    node.scrollTop = 280;
    node.dispatchEvent(new Event('scroll'));
  });
  await page.clock.runFor(150);
  const expected = await scroll.evaluate(node => {
    const bounds = node.getBoundingClientRect(),
      word = [...node.querySelectorAll('[data-word-position]')].find(n => n.getBoundingClientRect().bottom > bounds.top);
    return {
      chapter: 1,
      verse: Number(word.closest('[data-verse]').dataset.verse),
      word: Number(word.dataset.wordPosition),
      offset: Math.round(word.getBoundingClientRect().top - bounds.top)
    };
  });
  await page.evaluate(() => window.dispatchEvent(new PointerEvent('pointerup', {
    pointerId: 73,
    button: 0
  })));
  expect(await page.evaluate(() => history.state.usr.scribeswellReader.panes[0].anchor)).toEqual(expected);
  await page.clock.resume();
  await page.reload();
  await expect.poll(() => page.locator('[data-reader-pane]').first().locator('[data-reader-scroll]').evaluate((node, anchor) => {
    const word = node.querySelector(`[data-verse="${anchor.verse}"] [data-word-position="${anchor.word}"]`);
    return word ? Math.abs(Math.round(word.getBoundingClientRect().top - node.getBoundingClientRect().top) - anchor.offset) : null;
  }, expected)).toBeLessThanOrEqual(1);
});
test('review: wrapping controls and navigation errors requalify unchanged grid height', async ({
  page
}) => {
  await setup(page);
  await page.setViewportSize({
    width: 1000,
    // The tab region (74px) plus its12px gap consume86px; retain the
    // original grid space so normal text qualifies and wrapped controls do not.
    height: 846
  });
  await page.goto('/');
  for (let i = 0; i < 3; i++) await add(page);
  await expect(page.locator('[data-reader-pane]:visible')).toHaveCount(4);
  const initialTextHeights = await page.locator('[data-reader-scroll]:visible').evaluateAll(nodes => nodes.map(node => node.clientHeight));
  expect(Math.min(...initialTextHeights)).toBeGreaterThanOrEqual(200);
  const gridHeight = await page.locator('[data-reader-pane]').first().evaluate(node => node.parentElement.clientHeight);
  const trigger = page.locator('[data-reader-pane]').nth(3).getByRole('button', {
    name: /Navigate:/
  });
  await trigger.evaluate(node => node.style.width = '380px');
  await expect(page.locator('[data-reader-pane]:visible')).toHaveCount(1);
  const stable = await page.evaluate(async () => {
    const counts = [];
    for (let i = 0; i < 12; i++) {
      await new Promise(requestAnimationFrame);
      counts.push([...document.querySelectorAll('[data-reader-pane]')].filter(n => n.clientHeight > 0).length);
    }
    return counts;
  });
  expect(stable).toEqual(Array(12).fill(1));
  await trigger.evaluate(node => node.style.removeProperty('width'));
  await expect(page.locator('[data-reader-pane]:visible')).toHaveCount(4);
  expect(await page.locator('[data-reader-pane]').first().evaluate(node => node.parentElement.clientHeight)).toBe(gridHeight);
  let fail = true;
  await page.route('**/api/bible/books/Exod', route => fail ? route.fulfill({
    status: 503,
    json: {
      error: 'unavailable'
    }
  }) : route.fulfill({
    json: {
      id: 2,
      osis_id: 'Exod',
      name_en: 'Exodus',
      name_he: 'שמות',
      testament: 'OT',
      book_order: 2,
      chapters: [{
        id: 1,
        chapter_num: 1
      }]
    }
  }));
  await trigger.click();
  await page.getByRole('dialog', {
    name: 'Book and chapter selector'
  }).getByLabel('Passage reference', {
    exact: true
  }).fill('Exodus 1');
  await page.getByLabel('Passage reference', {
    exact: true
  }).press('Enter');
  await expect(page.getByRole('button', {
    name: 'Retry navigation',
    exact: true
  })).toBeVisible();
  await expect(page.locator('[data-reader-pane]:visible')).toHaveCount(1);
  fail = false;
  await page.getByRole('button', {
    name: 'Retry navigation',
    exact: true
  }).click();
  await expect(page.locator('[data-reader-pane]:visible')).toHaveCount(4);
  const heights = await page.locator('[data-reader-scroll]:visible').evaluateAll(nodes => nodes.map(node => node.clientHeight));
  expect(Math.min(...heights)).toBeGreaterThanOrEqual(200);
});
test('review: wrapped word-position anchors restore a later word independently of its ID', async ({
  page
}) => {
  await setup(page);
  await page.setViewportSize({
    width: 700,
    height: 500
  });
  await page.route('**/api/bible/books/Gen/chapters/1/verses', route => route.fulfill({
    json: {
      data: Array.from({
        length: 20
      }, (_, i) => ({
        id: i + 1,
        verse_num: i + 1,
        book_id: 1,
        chapter_num: 1,
        words: Array.from({
          length: 24
        }, (_, j) => ({
          id: 10000 + i * 100 + j,
          position: j + 1,
          surface_he: 'בְּרֵאשִׁיתבְּרֵאשִׁית',
          display_he: 'בְּרֵאשִׁיתבְּרֵאשִׁית',
          lemma_strong: 'H1',
          morph_code: 'HNcmsa'
        }))
      })),
      total: 20
    }
  }));
  await page.goto('/');
  await page.evaluate(() => document.fonts.ready);
  const scroll = page.locator('[data-reader-scroll]');
  await expect(scroll.locator('[data-verse="4"] [data-word-position="24"]')).toHaveCount(1);
  await scroll.evaluate(node => {
    const word = node.querySelector('[data-verse="4"] [data-word-position="24"]');
    node.scrollTop += word.getBoundingClientRect().top - node.getBoundingClientRect().top - 7;
  });
  const expected = await scroll.evaluate(node => {
    const bounds = node.getBoundingClientRect(),
      word = [...node.querySelectorAll('[data-word-position]')].find(w => w.getBoundingClientRect().bottom > bounds.top);
    return {
      verse: Number(word.closest('[data-verse]').dataset.verse),
      word: Number(word.dataset.wordPosition),
      offset: Math.round(word.getBoundingClientRect().top - bounds.top)
    };
  });
  expect(expected.word).toBeGreaterThan(1);
  await add(page);
  await page.goBack();
  await expect(page.locator('[data-reader-pane]')).toHaveCount(1);
  const offset = () => page.locator('[data-reader-scroll]').evaluate((node, anchor) => {
    const word = node.querySelector(`[data-verse="${anchor.verse}"] [data-word-position="${anchor.word}"]`);
    return word ? Math.round(word.getBoundingClientRect().top - node.getBoundingClientRect().top) : null;
  }, expected);
  await expect.poll(offset).toBe(expected.offset);
  await page.goForward();
  await page.goBack();
  await expect.poll(offset).toBe(expected.offset);
});
for (const transition of ['navigation', 'POP']) test(`review: a late gesture completion cannot checkpoint a different entry after ${transition}`, async ({
  page
}) => {
  await setup(page);
  await page.goto('/');
  if (transition === 'POP') await add(page);
  const scroll = page.locator('[data-reader-scroll]').last();
  await expect(scroll).toHaveAttribute('data-ready', 'true');
  await scroll.dispatchEvent('pointerdown', {
    pointerId: 73,
    button: 0
  });
  await scroll.evaluate(node => {
    node.scrollTop = 120;
    node.dispatchEvent(new Event('scroll'));
  });
  if (transition === 'POP') {
    await page.goBack();
    await expect(page.locator('[data-reader-pane]')).toHaveCount(1);
  } else {
    await add(page);
  }
  const before = await page.evaluate(() => JSON.stringify(history.state));
  await page.evaluate(() => window.dispatchEvent(new PointerEvent('pointerup', {
    pointerId: 73,
    button: 0
  })));
  expect(await page.evaluate(() => JSON.stringify(history.state))).toBe(before);
});

test('review: rapid POP replay expires outgoing gesture timers and intent', async ({page}) => {
  await setup(page);
  await page.setViewportSize({width: 1600, height: 1000});
  await page.goto('/');
  await add(page);
  await page.evaluate(() => document.fonts.ready);
  const scroll = page.locator('[data-reader-scroll]').last();
  await expect(scroll).toHaveAttribute('data-ready', 'true');
  await page.clock.install();
  await scroll.dispatchEvent('pointerdown', {pointerId: 73, button: 0});
  await scroll.evaluate(node => {
    node.scrollTop = 120;
    node.dispatchEvent(new Event('scroll'));
  });
  const outgoingKey = await page.evaluate(() => history.state.key);
  await page.goBack();
  await expect(page.locator('[data-reader-pane]')).toHaveCount(1);
  await page.goForward();
  await expect(page.locator('[data-reader-pane]')).toHaveCount(2);
  await expect(scroll).toHaveAttribute('data-ready', 'true');
  expect(await page.evaluate(() => history.state.key)).toBe(outgoingKey);
  const before = await page.evaluate(() => JSON.stringify(history.state));
  await scroll.evaluate(node => {
    node.scrollTop = 280;
    node.dispatchEvent(new Event('scroll'));
  });
  await page.evaluate(() => window.dispatchEvent(new PointerEvent('pointerup', {pointerId: 73, button: 0})));
  await page.clock.runFor(150);
  expect(await page.evaluate(() => JSON.stringify(history.state))).toBe(before);
});

test('review: pending deliberate movement survives scroll delivery after a real height change', async ({page}) => {
  await setup(page);
  await page.setViewportSize({width: 1100, height: 500});
  await page.goto('/');
  const scroll = page.locator('[data-reader-scroll]');
  await expect(scroll).toHaveAttribute('data-ready', 'true');
  await page.evaluate(() => document.fonts.ready);
  const original = await scroll.evaluate(node => {
    node.scrollTop = node.scrollHeight;
    node.dispatchEvent(new Event('scroll'));
    return {height: node.clientHeight, top: node.scrollTop};
  });
  expect(original.top).toBeGreaterThan(520);
  const changed = await scroll.evaluate(node => {
    const height = node.clientHeight;
    // Deliver the pending movement only after layout changes, before ResizeObserver.
    node.scrollTop = 120;
    node.style.flex = 'none';
    node.style.height = `${height + 400}px`;
    const grown = node.clientHeight;
    node.dispatchEvent(new Event('scroll'));
    return {height: grown, top: node.scrollTop};
  });
  expect(changed.height).toBe(original.height + 400);
  expect(changed.top).toBe(120);
  await page.evaluate(() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve))));
  await expect(scroll).toHaveJSProperty('clientHeight', original.height + 400);
  await scroll.evaluate((node, height) => { node.style.height = `${height}px`; }, original.height);
  await expect(scroll).toHaveJSProperty('clientHeight', original.height);
  await expect.poll(() => scroll.evaluate(node => node.scrollTop)).toBe(120);
});
