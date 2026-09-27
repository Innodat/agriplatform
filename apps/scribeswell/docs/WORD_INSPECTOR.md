---
title: Compact linked word inspector
type: feature
created: 2026-09-27
status: done
route: dispatch
baseline_commit: 0d8a0e73962dc83fc127466387590eaf58e6dfcf
context: []
---

<frozen-after-approval>
## Intent

Make the existing Word inspector compact, readable and navigable as a dictionary. The user approved the proposed layout and following Strong's/root references within the same pane, with Back restoration. Preserve the distinction between a selected passage word and a dictionary entry. Correct the participle decoding gap exposed by Psalm 149:2 as part of presenting complete readable grammar.

## Boundaries & Constraints

Use a bold pointed lemma as the main dictionary heading, compact transliteration/short meaning, root and Strong's metadata. Retain the actual selected word and verse in a small context header. Keep Word/Occurrences tabs. Put compact segmented grammar above long dictionary details; show a bounded verbatim BDB preview with Show more, full Strong's expandable. Keep raw morphology and segment codes under Source details, not as main badges. Retain pronunciation and attribution without clutter. Hebrew/Latin groups must wrap naturally on mobile.

Display actual source morpheme substrings only when slash boundaries align with morphology segments; otherwise retain readable grammar without invented splits/translations. Psalm149:2 source is `בְּ/עֹשָׂ֑י/ו`, code `HR/Vqrmpc/Sp3ms`: middle segment is Qal active participle, masculine plural construct, no person; suffix is third masculine singular. Fix canonical parsing and existing API read presentation without production/local DB writes or import. Preserve source text, lexical identities and existing integrity checks.

Make explicit dictionary cross-references in Strong's/BDB and recorded roots clickable only when they resolve uniquely to an available entry. Missing/ambiguous targets stay source text; never guess a homonym or auto-link arbitrary digits. Preserve source markup as safe structured data, old plain fields compatibly, original XML/checksums, dictionary notices and incomplete BDB status. Never insert raw HTML or fetch new external content.

Following a link changes only inspector dictionary context: show target lemma/root/definitions and its Occurrences, without borrowing the selected token's morphology or presenting its verse as the target's occurrence. Keep Bible references, reading positions and selected highlight unchanged. Provide an explicit Back control restoring the previous entry's tab, filters/page, expansions and inspector scroll position (including returning to original word). New passage-word selection or close resets dictionary history; handle repeated links, loading/error/retry and late responses safely. Existing scripture previews/open actions remain functional. No NET placeholder tab.

## I/O & Edge-Case Matrix

| Scenario | Expected behavior |
| --- | --- |
| Selected word on desktop/mobile | Compact lemma/meaning/root; small selected-form context; readable actual segments; no raw code in main view |
| Participle/finite verb/infinitive | Correct positional parsing; participle gender/number/state and no person; preserve finite-verb features |
| Missing/unmatched surface segments | No invented substrings; readable grammar remains; missing lexicon still leaves morphology usable |
| Explicit valid versus ambiguous/missing dictionary reference | Unique target opens; other source text remains noninteractive, identities never guessed |
| Follow A→B→C, Back twice | Restore entry, tab/filter/page/expansions/scroll; original selected morphology restored; Bible/highlights unchanged |
| Target occurrences/new word/late response/error | Lookup uses displayed identity; no stale entry/results/morphology; retry works; new word clears history |
| Long BDB/Hebrew labels/keyboard | Bounded preview, usable Show more, no hidden focusable links or viewport overflow |

</frozen-after-approval>

## Code Map

All paths below are repository-relative under `apps/scribeswell/` unless stated otherwise.
- `web/src/components/bible/WordStudy.tsx`: current inspector, dictionary and occurrence fetching, BDB nodes, scripture preview. `MorphologyPanel.tsx` renders verbose cards. `ReaderPage.tsx` owns the scrolling aside and pinned selection; coordinate inspector scroll restoration without moving text panes.
- `web/src/hooks/useBible.ts`: request-identity protection and retry; preserve it. `web/src/schemas/bible.schema.ts` and `backend/schemas/bible_schemas.py`: additive schemas.
- `tools/py/build_lexicon.py`: immutable source builder. `data/hebrew-lexicon/` originals unchanged. Strong XML uses `<w src="H6">6</w>`; BDB has `<w src="a.ab.aa">…</w>` referring to BDB IDs, requiring mapped unique lexical identity. `LexicalIndex.xml` xrefs/AugIndex connect IDs; root IDs are lexical entries. Preserve text/language/valid scripture nodes.
- `backend/services/lexicon_service.py`: cached artifact and exact identities. `backend/services/bible_service.py:get_word_morphology`: DB integrity checks then decoded morphemes. `tools/py/oshb_morph.py`: current canonical parser erroneously assumes every verb is finite. Importer already adds backend to sys.path. A single backend-owned parser with a compatible tooling wrapper is acceptable; avoid duplicate parser rules. Existing stored derived fields may be stale, so API must derive corrected features from preserved codes without requiring import.
- `tests/test_lexicon.py`, `test_reader_integrity.py`, `test_import_bible.py`; `web/tests/lexicon.spec.cjs`, `reader.spec.cjs`: extend real-source/contract and browser coverage, preserve previous regressions.

## Tasks & Acceptance

- [x] Characterize finite verbs/current contracts and observe failing participle/UI/link acceptance tests before implementation.
- [x] Correct one canonical parser and API presentation; add safe aligned surface segments or derive alignment in the client from existing source fields.
- [x] Extend reference builder/contracts with uniquely resolved dictionary/root links; regenerate artifact deterministically with source checksums unchanged.
- [x] Refactor inspector into compact Word layout and reversible dictionary history; preserve Occurrences, scripture previews, selection and passage scroll.
- [x] Execute every matrix row's tests, existing Python/browser suites, build and real local desktop/mobile checks; record evidence and review.

Given a selected word, when opening Word, then lemma/meaning and grammar are concise and complete. Given a dictionary reference, when following and returning, then the inspector changes/restores while Bible context does not. Given unavailable source information, then preserve readable supported data without manufacturing analyses.

## Implementation Notes

User's “lets do this” authorizes the discussed changes and reversible implementation; no new approval needed. Footprint spans the existing silo's builder, parser, API and inspector; no new service/database/auth or schema migration. Scaffold/shared-UI/agent-context impact: none. Documentation: this spec and BUILD notes. ADR: no new architectural decision. Application data and private PtS routing unchanged. Parent performs independent review/live verification and local commit, no push/deploy.

## Verification

- Python: `apps/scribeswell/.local/venv/bin/python -m pytest apps/scribeswell/tests/test_lexicon.py apps/scribeswell/tests/test_reader_integrity.py apps/scribeswell/tests/test_import_bible.py -q` (add parser test file if created).
- Browser: `LD_LIBRARY_PATH=/tmp/pts-browser-libs/usr/lib/x86_64-linux-gnu npm run test:browser --workspace=apps/scribeswell/web`.
- Build: `npm run build --workspace=apps/scribeswell/web`; `git diff --check` (original source whitespace unchanged).
- Live app http://localhost:5179/scribeswell/ (shared origin); local API8000, Supabase running. Parent can restart only API using `/tmp/restart-scribeswell-api.py`. Python TestClient hangs in sandbox: run tests as a separate escalated command, never bundle edits and escalation. Send progress before tools and if blocked; keep individual waits <=60s. No secrets in output.

## Verification evidence before independent review

- ATDD: finite-verb characterization passed; participle decoding, existing-row API correction and explicit dictionary-link assertions failed before implementation (3 failed / 1 passed). Static Back-control assertion failed before UI changes. A focused browser attempt failed sandbox server startup; an escalated attempt using the PtS binary failed test discovery because of a different Playwright version. Those runner failures are not claimed as feature red evidence. The corrected Scribeswell workspace runner passed the compact inspector scenario after implementation.
- Full Python command above including `test_word_inspector.py`: **24 passed**, existing Starlette/httpx deprecation warning only. Browser command: **78 passed** (29.5 s), log `/tmp/inspector-browser.log`. Production build passed, existing >500 KB advisory, log `/tmp/inspector-build.log`.
- Matrix coverage: compact/segmented/hidden-code and unmatched-boundary browser tests; canonical active/passive participle, finite/infinitive and real Psalm149:2 Python tests; real-source link and whole-artifact identity/fallback tests; A→B→C/Back, scroll/filter/page/expansions, linked occurrences/error/retry/late responses/new selection, clipped links and mobile overflow browser checks.
- Source audit: all 306,785 imported token boundary counts align. Participles: 9,462 Hebrew and 319 Aramaic segments, each six characters in this corpus. Original source checksums unchanged. Dictionary links retain plain text fallback for older frontend compatibility.

Canonical parser now lives in `backend/services/oshb_morph.py`; the tooling module re-exports it. Existing source codes are decoded at read time after stored-row completeness validation. No database writes/re-import occurred. A later importer verification may identify stale derived participle features in stored morpheme rows; that is an existing derived-data discrepancy, not a change to collected Hebrew text.

## Review Triage Log

All three independent layers returned; findings verified individually before grouping. Corrections preserve the authorized interface and use no production writes.

| Finding | Verdict | Evidence and route |
| --- | --- | --- |
| Blind 1: aspect hidden when stem absent | medium | New heading conditional omits decoded aspect whenever stem is null, including real Aramaic Varmsa/Vai3mp. Patch aspect composition independently of stem. |
| Blind 2: self-target links do nothing | low | `follow` rejects current identity while root/node rendering still exposes buttons; real roots include 1,624 self targets. Direct correction: render current-entry references as text. |
| Blind 3: Back loses keyboard focus | medium | Original frame remount removes the active Back button and `initial.linked` suppresses replacement focus. Patch focus restoration to the originating control or appropriate inspector fallback. |
| Blind 4: retry loses saved scroll | medium | Restoration marks complete on error/unavailable data, when short content clamps saved scroll. Patch readiness/error guard and retry coverage. |
| Blind 5: late dictionary overwrites user interaction | medium | Pending restoration waits for dictionary while Occurrences can already be read; later response can reset scroll/focus into hidden Word panel. Patch cancellation on intervening user navigation/scroll, and never focus a hidden heading. |
| Blind 6: failed linked lookup lacks identity | medium | Header retains selected-word context but target identity appears only after success or in Occurrences. Patch linked loading/error/missing header to identify requested entry. |
| Blind 7: preview splits combining characters | low | Slice counts UTF-16 units, so pointed Hebrew can be cut mid-grapheme. Direct correction with grapheme-aware preview boundary. |
| Blind 8: destination test misses wrong existing target | medium | Whole-artifact test asserts destination existence, but does not compare every node with its source `src`. Patch source-to-target assertions independently of builder resolver. |
| Blind 9: Aramaic verification missing | medium | Only Hebrew decoder examples protect the moved parser, although source has 319 Aramaic participles. Patch real Aramaic/API and missing-stem display coverage. |
| Blind 10: obsolete morphology props | low | Sole consumer passes props ignored by the new grammar-only component. Direct deletion of obsolete contract/call arguments. |
| Edge 1: failed Back reload loses restoration | medium | Same demonstrated error/readiness defect as Blind 4; same patch. |
| Edge 2: Back focus lost | medium | Same destroyed-button/no-origin-focus defect as Blind 3; same patch. |
| Verification 1: new link fields lack HTTP coverage | medium | Added identity/node fields only tested before Pydantic serialization; extend real lexical HTTP response assertions for entry10 and nested BDB links. |
| Verification 2: Strong source links lack automated browser coverage | medium | Existing fixture links cover roots/BDB; live root check proved Strong2→1, but repeatable suite needs an actual Strong source link/navigation assertion. Patch browser regression using entry10→6. |
| Parent: nested BDB preview still too tall | medium | Live Psalm149:2 screenshot shows 480 text characters spanning many nested sense blocks and hundreds of pixels. Patch preview to a short contiguous prefix bounded by structural blocks as well as graphemes; expose complete text through Show more. |
| Parent: canonical Aramaic stem lookup conflicts with language | medium | The moved decoder inherits a shared lookup where q means qal and a is absent, contrary to OSHB Aramaic q=peal/a=aphel. Read-time canonical decoding now owns displayed morphology, so correct language-specific lookup and verify finite/participle cases without DB writes. Source: https://hb.openscriptures.org/parsing/HebrewMorphologyCodes.html. |

Parent live verification before review patches passed Psalm149:2 grammar and Ezra4:15 Strong2→1 navigation, target occurrences and Back scroll/expanded-state restoration on desktop/mobile, preserving URL/highlight/passage scroll. Screenshots inspected; the preview-height issue above was visible in real data.

## Review closure and final verification

All review findings above were corrected and verified; nothing deferred. Back restores the originating keyboard control and saved scroll after retry, while intervening user navigation cancels pending restoration. Self references remain text; linked error/loading states identify the requested entry. Preview boundaries preserve graphemes and complete link labels. Hebrew and Aramaic stem maps are language-specific; known aspects remain visible independently of stem availability.

- `apps/scribeswell/.local/venv/bin/python -m pytest apps/scribeswell/tests/test_word_inspector.py apps/scribeswell/tests/test_lexicon.py apps/scribeswell/tests/test_reader_integrity.py apps/scribeswell/tests/test_import_bible.py -q`: **26 passed**, existing Starlette/httpx warning only.
- `LD_LIBRARY_PATH=/tmp/pts-browser-libs/usr/lib/x86_64-linux-gnu npm run test:browser --workspace=apps/scribeswell/web > /tmp/inspector-browser.log 2>&1`: **88 passed**, two new source-link assertions failed because their expectation confused root 10→6 with Strong source links. Original H10 XML explicitly references H9 and H11. Corrected only those expectations; root 10→6 remains asserted.
- `LD_LIBRARY_PATH=/tmp/pts-browser-libs/usr/lib/x86_64-linux-gnu npm run test:browser --workspace=apps/scribeswell/web -- --grep 'actual entry 10' > /tmp/inspector-links-browser.log 2>&1`: **2 passed**, covering the corrected source 10→9 navigation and Back on desktop/mobile. Thus all **90 browser cases** passed across the full run and focused correction rerun.
- `npm run build --workspace=apps/scribeswell/web > /tmp/inspector-build.log 2>&1`: passed; existing large-chunk advisory remains.
- `LD_LIBRARY_PATH=/tmp/pts-browser-libs/usr/lib/x86_64-linux-gnu node /tmp/pts-local/inspector-live.cjs`: passed after restarting only the local API. Real Psalm149:2 grammar and Ezra4:15 dictionary navigation/occurrences/Back preserve reading context on desktop/mobile. Final screenshots inspected, including the shortened outline.
- Builder `build()` rerun with before/after SHA-256 comparison: identical generated artifact; all pinned source checksums validated. `git diff --check`: clean.

No database changes, re-import, public deployment or source-file changes. The local API has the updated decoder loaded. Release uses the existing application build/deployment process.
