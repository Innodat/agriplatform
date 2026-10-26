import { useLayoutEffect, useRef, useState } from 'react';
import { useLocation, useNavigate, useNavigationType } from 'react-router-dom';
import { parseReaderURL, parseSnapshot, readerSearch, snapshotState, validAnchor, record, type Anchor, type Snapshot, type PublicPane } from '@/lib/reader-layout';
import {referenceKey, validateReference, type PassageReference} from '@/lib/passage-references';
export type ReaderPane = PublicPane & {
  generation: number;
  picker: number;
  valid: boolean;
};
type Workspace = {
  tabKey: string;
  panes: ReaderPane[];
  activePaneKey: string;
  revision: number;
  invalid: boolean;
};
const uuid = () => crypto.randomUUID();
const entry = () => JSON.stringify([window.history.state?.key ?? 'default', window.history.state?.idx ?? null, window.location.href]);
export function useReaderWorkspace(root: React.RefObject<HTMLElement | null>) {
  const location = useLocation(),
    navigate = useNavigate(),
    navigationType = useNavigationType();
  const generation = useRef(0),
    layoutGeneration = useRef(0),
    cache = useRef(new Map<string, Snapshot>()),
    own = useRef<string | null>(null),
    observed = useRef<string | null>(null),
    displacedClose = useRef<{origin: Element; paneKey: string; entry: string} | null>(null);
  function incoming(): Workspace {
    const url = parseReaderURL(new URLSearchParams(window.location.search)),
      native = window.history.state,
      recover = (value: unknown) => {
        if (!url.invalid) return parseSnapshot(value, url);
        // A malformed URL remains the provenance marker. Its existing closed
        // snapshot may retain only independently keyed copies of that fallback.
        if (!record(value) || !Array.isArray(value.panes) || value.panes.length < 1 || value.panes.length > 4) return;
        const panes = value.panes;
        if (!panes.every(p => record(p) && validateReference(p.ref) && referenceKey(p.ref) === referenceKey(url.refs[0]))) return;
        const active = panes.findIndex(p => p.paneKey === value.activePaneKey);
        return parseSnapshot(value, {...url, refs: panes.map(p => p.ref), active});
      },
      snapshot = recover(cache.current.get(entry())) ?? recover(native?.usr?.scribeswellReader);
    const panes = (snapshot?.panes ?? url.refs.map(ref => ({
      paneKey: uuid(),
      ref
    }))).map(p => ({
      ...p,
      generation: ++generation.current,
      picker: 0,
      valid: !url.invalid
    }));
    return {
      tabKey: snapshot?.tabKey ?? uuid(),
      panes,
      activePaneKey: snapshot?.activePaneKey ?? panes[url.active].paneKey,
      revision: ++layoutGeneration.current,
      invalid: url.invalid
    };
  }
  const [workspace, setWorkspace] = useState(incoming),
    current = useRef(workspace);
  current.current = workspace;
  const read = () => current.current;
  function snapshot(w: Workspace, capture = false): Snapshot {
    return {
      v: 1,
      tabKey: w.tabKey,
      activePaneKey: w.activePaneKey,
      panes: w.panes.map(({
        paneKey,
        ref,
        anchor
      }) => {
        if (capture) {
          const scroll = Array.from(root.current?.querySelectorAll<HTMLElement>('[data-reader-scroll]') ?? []).find(n => n.dataset.paneKey === paneKey);
          if (scroll?.clientHeight && scroll.dataset.ready === 'true') {
            let preserved: unknown;
            try {
              preserved = scroll.dataset.preservedAnchor ? JSON.parse(scroll.dataset.preservedAnchor) : undefined;
            } catch {/* invalid diagnostic-free fallback */}
            if (Number(scroll.dataset.preservedScroll) === scroll.scrollTop && validAnchor(preserved, ref)) return {
              paneKey,
              ref,
              anchor: preserved
            };
            const bounds = scroll.getBoundingClientRect(),
              word = Array.from(scroll.querySelectorAll<HTMLElement>('[data-word-position]')).find(n => {
                const r = n.getBoundingClientRect();
                return r.bottom > bounds.top && r.top < bounds.bottom;
              });
            if (word) {
              const verse = Number(word.closest<HTMLElement>('[data-verse]')?.dataset.verse),
                position = Number(word.dataset.wordPosition);
              const candidate: Anchor = {
                chapter: Number(scroll.dataset.chapter),
                verse,
                offset: Math.max(-512, Math.min(512, Math.round(word.getBoundingClientRect().top - bounds.top))),
                ...(position >= 1 && position <= 4096 ? {
                  word: position
                } : {})
              };
              if (validAnchor(candidate, ref)) anchor = candidate;
            }
          }
        }
        return {
          paneKey,
          ref,
          ...(anchor ? {
            anchor
          } : {})
        };
      })
    };
  }
  function remember(key: string, s: Snapshot) {
    cache.current.delete(key);
    cache.current.set(key, s);
    while (cache.current.size > 64) cache.current.delete(cache.current.keys().next().value!);
  }
  function checkpoint() {
    const key = entry(),
      s = snapshot(read(), true);
    remember(key, s);
    const native = window.history.state ?? {};
    const usr = snapshotState(native.usr, s);
    if (usr !== native.usr) window.history.replaceState({
      ...native,
      usr
    }, '');
    return s;
  }
  function commit(next: Workspace, replace = false) {
    next = {
      ...next,
      revision: ++layoutGeneration.current
    };
    const previous = read(),
      old = checkpoint();
    next = {
      ...next,
      panes: next.panes.map(p => previous.panes.some(x => x.paneKey === p.paneKey && x.generation === p.generation) ? {
        ...p,
        anchor: old.panes.find(x => x.paneKey === p.paneKey)?.anchor
      } : p)
    };
    const before = window.history.state ?? {},
      s = snapshot(next),
      search = next.invalid ? window.location.search : readerSearch(window.location.search, next.panes.map(p => p.ref), next.panes.findIndex(p => p.paneKey === next.activePaneKey));
    current.current = next;
    setWorkspace(next);
    navigate({
      pathname: location.pathname,
      search,
      hash: window.location.hash
    }, {
      replace,
      state: snapshotState(before.usr, s)
    });
    const after = window.history.state ?? {};
    const extra = Object.fromEntries(Object.entries(before).filter(([k]) => !['usr', 'key', 'idx'].includes(k)));
    window.history.replaceState({
      ...extra,
      ...after
    }, '');
    own.current = entry();
    remember(entry(), s);
  }
  useLayoutEffect(() => {
    const id = entry();
    // useState already ingested this initial entry. StrictMode effect replay must
    // retain those committed pane identities and their pending ready seeks.
    if (observed.current === null) {
      observed.current = id;
      return;
    }
    if (observed.current === id) return;
    observed.current = id;
    if (own.current === id && navigationType !== 'POP') {
      own.current = null;
      return;
    }
    own.current = null;
    const next = incoming();
    current.current = next;
    setWorkspace(next);
  }, [location.key, location.pathname, location.search, location.hash, navigationType]);
  useLayoutEffect(() => {
    const pending = displacedClose.current;
    if (!pending) return;
    displacedClose.current = null;
    if (pending.entry !== entry() || pending.origin.isConnected ||
        document.activeElement !== document.body && document.activeElement !== pending.origin) return;
    const pane = Array.from(root.current?.querySelectorAll<HTMLElement>('[data-reader-pane]') ?? [])
      .find(node => node.dataset.paneKey === pending.paneKey);
    (pane?.querySelector<HTMLElement>('button[aria-haspopup="dialog"]') ?? pane?.querySelector<HTMLElement>('[data-reader-scroll]'))?.focus({preventScroll: true});
  }, [workspace]);
  useLayoutEffect(() => {
    const pop = () => {
      if (observed.current) remember(observed.current, snapshot(read(), true));
    };
    window.addEventListener('popstate', pop);
    return () => window.removeEventListener('popstate', pop);
  }, []);
  // Gesture ownership lasts until release; a long scrollbar drag must not
  // outlive a short input-observation window. All callbacks remain entry-scoped.
  useLayoutEffect(() => {
    let timer: ReturnType<typeof setTimeout> | undefined;
    let userUntil = 0;
    let gesture: {pointerId: number; entry: string} | null = null;
    const intent = () => { userUntil = performance.now() + 1000; };
    const pointerDown = (event: PointerEvent) => {
      intent();
      const scroll = (event.target as Element)?.closest<HTMLElement>('[data-reader-scroll]');
      if (event.button === 0 && scroll) {
        // Activation replaces the Router entry. Capture ownership after that
        // existing semantic action; the pane's later React activation is a no-op.
        if (scroll.dataset.paneKey) activate(scroll.dataset.paneKey);
        gesture = {pointerId: event.pointerId, entry: entry()};
      }
    };
    const pop = () => {
      gesture = null;
      clearTimeout(timer);
      userUntil = 0;
    };
    const complete = (event?: PointerEvent) => {
      if (!gesture || event && event.pointerId !== gesture.pointerId) return;
      const captured = gesture;
      gesture = null;
      if (captured.entry !== entry()) return;
      intent();
      clearTimeout(timer);
      checkpoint();
    };
    const scroll = () => {
      if (!(gesture?.entry === entry()) && performance.now() > userUntil) return;
      const id = entry();
      clearTimeout(timer);
      timer = setTimeout(() => { if (id === entry()) checkpoint(); }, 120);
    };
    const blur = () => complete();
    const node = root.current;
    node?.addEventListener('scroll', scroll, true);
    node?.addEventListener('pointerdown', pointerDown, true);
    for (const event of ['wheel', 'touchmove', 'keydown']) node?.addEventListener(event, intent, true);
    for (const event of ['pointerup', 'pointercancel', 'lostpointercapture']) window.addEventListener(event, complete as EventListener, true);
    window.addEventListener('blur', blur);
    window.addEventListener('popstate', pop);
    return () => {
      clearTimeout(timer);
      node?.removeEventListener('scroll', scroll, true);
      node?.removeEventListener('pointerdown', pointerDown, true);
      for (const event of ['wheel', 'touchmove', 'keydown']) node?.removeEventListener(event, intent, true);
      for (const event of ['pointerup', 'pointercancel', 'lostpointercapture']) window.removeEventListener(event, complete as EventListener, true);
      window.removeEventListener('blur', blur);
      window.removeEventListener('popstate', pop);
    };
  }, []);
  function activate(key: string) {
    const w = read();
    if (key === w.activePaneKey || !w.panes.some(p => p.paneKey === key)) return;
    commit({
      ...w,
      activePaneKey: key
    }, true);
  }
  function open(ref: PassageReference, key = read().activePaneKey, picker = false) {
    const w = read();
    if (!w.panes.some(p => p.paneKey === key)) return;
    const unresolved=w.invalid&&picker;
    commit({
      ...w,
      invalid: unresolved,
      revision: w.revision + 1,
      activePaneKey: key,
      panes: w.panes.map(p => p.paneKey === key ? {
        ...p,
        ref,
        anchor: undefined,
        valid: !unresolved,
        generation: ++generation.current,
        picker: picker ? p.picker + 1 : 0
      } : w.invalid&&!unresolved?{...p,valid:true}:p)
    });
  }
  function add(ref: PassageReference, picker = false) {
    const w = read();
    if (w.panes.length >= 4) return false;
    const unresolved=w.invalid&&picker;
    const index = w.panes.findIndex(p => p.paneKey === w.activePaneKey),
      p = {
        paneKey: uuid(),
        ref,
        generation: ++generation.current,
        picker: picker ? 1 : 0,
        valid: !unresolved
      };
    commit({
      ...w,
      invalid: unresolved,
      revision: w.revision + 1,
      activePaneKey: p.paneKey,
      panes: [...w.panes.slice(0, index + 1), p, ...w.panes.slice(index + 1)].map(p=>w.invalid&&!unresolved?{...p,valid:true}:p)
    });
    return true;
  }
  function close(key: string) {
    const w = read(),
      index = w.panes.findIndex(p => p.paneKey === key);
    if (w.panes.length === 1 || index < 0) return;
    const panes = w.panes.filter(p => p.paneKey !== key);
    const activePaneKey = w.activePaneKey === key ? panes[Math.max(0, index - 1)].paneKey : w.activePaneKey;
    const origin = document.activeElement;
    const displaced = origin instanceof Element && origin.matches('[data-close-pane]') &&
      origin.closest<HTMLElement>('[data-reader-pane]')?.dataset.paneKey === key;
    commit({...w, panes, activePaneKey});
    if (displaced) displacedClose.current = {origin, paneKey: activePaneKey, entry: entry()};
  }
  return {
    workspace,
    read,
    activate,
    open,
    add,
    close
  };
}
