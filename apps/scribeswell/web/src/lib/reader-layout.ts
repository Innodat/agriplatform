/** Closed, public-only reader URL/history grammar. */
import { chapterReference, makeReference, referenceStart, referenceKey, validateReference, type PassageReference } from './passage-references';
export type Anchor = {
  chapter: number;
  verse: number;
  word?: number;
  offset: number;
};
export type PublicPane = {
  paneKey: string;
  ref: PassageReference;
  anchor?: Anchor;
};
export type Snapshot = {
  v: 1;
  tabKey: string;
  activePaneKey: string;
  panes: PublicPane[];
};
export type LayoutURL = {
  refs: PassageReference[];
  active: number;
  invalid: boolean;
};
const legacy = ['book', 'chapter', 'verse', 'EndChapter', 'EndVerse', 'compareBook', 'compareChapter', 'compareVerse', 'compareEndChapter', 'compareEndVerse'];
export const record = (x: unknown): x is Record<string, unknown> => !!x && typeof x === 'object' && (Object.getPrototypeOf(x) === Object.prototype || Object.getPrototypeOf(x) === null);
const keys = (x: Record<string, unknown>, allowed: string[], required = allowed) => Object.keys(x).every(k => allowed.includes(k)) && required.every(k => Object.prototype.hasOwnProperty.call(x, k));
const integer = (n: unknown, min: number, max: number) => typeof n === 'number' && Number.isInteger(n) && n >= min && n <= max;
const safe = (): LayoutURL => ({
  refs: [chapterReference('Gen', 1)],
  active: 0,
  invalid: true
});
export function parseReaderURL(params: URLSearchParams): LayoutURL {
  if (params.has('reader')) {
    try {
      const values = params.getAll('reader');
      if (values.length !== 1 || new URLSearchParams({
        reader: values[0]
      }).toString().length > 4096) return safe();
      const x: unknown = JSON.parse(values[0]);
      if (!record(x) || !keys(x, ['v', 'panes', 'active']) || x.v !== 1 || !Array.isArray(x.panes) || x.panes.length < 1 || x.panes.length > 4 || !integer(x.active, 0, x.panes.length - 1)) return safe();
      const refs: PassageReference[] = [];
      for (const p of x.panes) {
        if (!record(p) || !keys(p, ['ref']) || !validateReference(p.ref)) return safe();
        refs.push(p.ref);
      }
      return {
        refs,
        active: x.active as number,
        invalid: false
      };
    } catch {
      return safe();
    }
  }
  try {
    function ref(compare: boolean) {
      const b = compare ? 'compareBook' : 'book',
        c = compare ? 'compareChapter' : 'chapter',
        v = compare ? 'compareVerse' : 'verse',
        prefix = compare ? 'compare' : '';
      function coord(key: string, fallback?: number) {
        const raw = params.get(key);
        if (raw === null) return fallback;
        if (!/^[1-9][0-9]*$/.test(raw)) throw Error();
        const n = Number(raw);
        if (!Number.isSafeInteger(n)) throw Error();
        return n;
      }
      const book = params.get(b) ?? 'Gen',
        chapter = coord(c, 1)!,
        verse = coord(v);
      if (verse === undefined) {
        if (params.has(prefix + 'EndChapter') || params.has(prefix + 'EndVerse')) throw Error();
        return chapterReference(book, chapter);
      }
      return makeReference(book, {
        kind: 'verse_range',
        start: {
          chapter,
          verse
        },
        end: {
          chapter: coord(prefix + 'EndChapter', chapter)!,
          verse: coord(prefix + 'EndVerse', verse)!
        }
      });
    }
    return {
      refs: params.has('compareBook') ? [ref(false), ref(true)] : [ref(false)],
      active: 0,
      invalid: false
    };
  } catch {
    return safe();
  }
}
export function readerSearch(search: string, refs: PassageReference[], active: number) {
  const p = new URLSearchParams(search);
  legacy.forEach(k => p.delete(k));
  p.delete('reader');
  const wire = new URLSearchParams({
    reader: JSON.stringify({
      v: 1,
      panes: refs.map(ref => ({
        ref
      })),
      active
    })
  });
  if (wire.toString().length > 4096) throw Error('Reading link too large');
  p.set('reader', wire.get('reader')!);
  return '?' + p.toString();
}
export function parseSnapshot(value: unknown, url: LayoutURL): Snapshot | undefined {
  try {
    if (new TextEncoder().encode(JSON.stringify(value)).length > 8192 || !record(value) || !keys(value, ['v', 'tabKey', 'activePaneKey', 'panes']) || value.v !== 1 || !validKey(value.tabKey) || !validKey(value.activePaneKey) || !Array.isArray(value.panes) || value.panes.length !== url.refs.length) return;
    const seen = new Set<string>();
    for (let i = 0; i < value.panes.length; i++) {
      const p: unknown = value.panes[i];
      if (!record(p) || !keys(p, ['paneKey', 'ref', 'anchor'], ['paneKey', 'ref']) || !validKey(p.paneKey) || seen.has(p.paneKey) || !validateReference(p.ref) || referenceKey(p.ref) !== referenceKey(url.refs[i])) return;
      seen.add(p.paneKey);
      if (p.anchor !== undefined && !validAnchor(p.anchor, p.ref)) return;
    }
    if (value.panes[url.active]?.paneKey !== value.activePaneKey) return;
    return value as Snapshot;
  } catch {
    return;
  }
}
function validKey(x: unknown): x is string {
  return typeof x === 'string' && x.length > 0 && x.length <= 128;
}
export function validAnchor(x: unknown, ref: PassageReference): x is Anchor {
  if (!record(x) || !keys(x, ['chapter', 'verse', 'word', 'offset'], ['chapter', 'verse', 'offset']) || x.chapter !== referenceStart(ref).chapter || !integer(x.offset, -512, 512) || x.word !== undefined && !integer(x.word, 1, 4096)) return false;
  try {
    makeReference(ref.book_id, {
      kind: 'verse_range',
      start: {
        chapter: x.chapter as number,
        verse: x.verse as number
      },
      end: {
        chapter: x.chapter as number,
        verse: x.verse as number
      }
    });
    return true;
  } catch {
    return false;
  }
}
export function snapshotState(usr: unknown, snapshot: Snapshot): unknown {
  return usr != null && !record(usr) ? usr : {
    ...(record(usr) ? usr : {}),
    scribeswellReader: snapshot
  };
}
