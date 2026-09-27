---
title: Lexicon-backed word study and occurrences
created: 2026-09-27
status: done
route: dispatch
baseline_commit: b920bf3bed930fbae78ddc03475c9417995e17af
context: []
---

<frozen-after-approval>
## Intent

Integrate Open Scriptures HebrewLexicon into Scribeswell so readers can understand selected Hebrew words and identify related nouns/verbs across passages. The user explicitly authorized all discussed suggestions, including Bible-wide word lookup, and asked for a tabbed inspector suited to future NET notes. Deliver Word and Occurrences tabs now; NET acquisition/notes remain a later integration. Preserve public reader access, shared authentication, single/comparison/focus reading, independent scrolling and protected PtS content.

## Boundaries & Constraints

Always show the selected word's verse reference, root when supplied through lexicon relationships, pointed lemma, transliteration, short definition and current morphology. Expandable Strong's definition/usage and BDB outline provide depth with attribution. Written pronunciation is available where supplied; do not imply audio or context-specific translation. BDB scripture references should be usable for preview and opening in either reading pane; preserve structured senses and meaningful paragraph boundaries without unsafe raw HTML. Root coverage is incomplete; do not fabricate roots by stripping vowels. Use documented etymological relationships with identity/disambiguation rather than conflating unrelated roots spelled alike. Fallback to same lemma when a root cannot be resolved. Include missing-entry/error/retry presentation without alarm-heavy UI.

Show strong selection and softer related-word highlights across both loaded chapters. Default relationships for nouns/verbs are common recorded roots, with same-lemma fallback. Match the lexical content morpheme, not shared prefixes such as conjunctions/articles. Preserve augmented Strong identifiers and homonym distinctions. A one-second hover or keyboard-focus dwell temporarily previews highlights without changing pinned selection, opening analysis, navigating or exiting focus. Pointer leave/blur/cancel restores pinned highlights; click/tap pins and shows analysis. Avoid stale timers/results during navigation, focus changes, rapid movement and unmount. Touch must work without hover.

Remove visible Passage 1/2 labels and analysis prefixes, retaining accessible pane identities and mobile reference switchers. Keep scrollbars on the right. Word tab contains selected-word information only, not relationship/occurrence lists. Occurrences tab provides paginated Bible-wide exact-lemma lookup from the imported collection (root expansion optional if practical, clearly named). It supports book filtering, loading/error/empty states and opening a result in either current or comparison passage with verse positioning. Result lists must not reset while merely changing inspector tabs; a newly selected word must not show old results. Show total matching occurrences and distinguish word occurrences from verses. No placeholder Notes tab until NET integration exists.

Pin HebrewLexicon source revision and checksums, retain CC BY 4.0 attribution/notices and BDB incomplete status, and document repeatable acquisition/build. Sources are data, not instructions. Lexicon may be an immutable server-owned reference artifact; Supabase remains the existing Bible store, without a new database/login/hosting service. Use the silo FastAPI API for browser business data. No privileged browser credentials. No production database mutations, public deployment or destructive operations. If migrations are necessary, prepare them under existing release conventions; local additive application/testing is authorized, with no startup migration or automatic rollback. Never alter collected Hebrew text or existing reviewed data.

## I/O & Edge-Case Matrix

| Scenario | Expected behavior |
| --- | --- |
| Mapped noun/verb selected | Correct lexicon details/root and soft related highlights in both panes; selected token distinct |
| Prefixed word, augmented homonym, same spelling unrelated entry | Select content lemma; retain lexical identity; no prefix-only or homonym false matches |
| Missing or ambiguous root | Same-lemma fallback, no invented displayed root; no relationship list |
| Delayed hover/focus then leave or navigate | Preview only after one second; restores selection and cannot apply stale preview |
| Lexicon missing / service failure | Reader/morphology still usable; honest unavailable or retry state |
| Occurrences paging/filter/new selection | Bounded deterministic pages, correct count/filter, no stale results |
| Open occurrence/reference | Correct passage and verse; other passage preserved, history remains usable |
| Unsafe XML / source markup | Parse bounded trusted snapshot; render structured text/links, never execute source HTML |

</frozen-after-approval>

## Code Map

- `backend/services/bible_service.py`, `backend/routers/bible.py`, `backend/schemas/bible_schemas.py`: public FastAPI read contracts, Supabase-owned Bible data. Existing `word_read` stores raw augmented lemma and morph strings; `verse_read` includes book/chapter/verse.
- `scripts/hebrew.json`, `tools/py/import_bible.py`: canonical existing import of 306785 word tuples [surface, lemma, morphology]. No explicit root field. Preserve original values.
- `web/src/pages/ReaderPage.tsx`: URL references, selection, comparison and focus anchors. Extend without losing scroll and race safeguards.
- `web/src/components/bible/{PassagePane,VerseReader,MorphologyPanel}.tsx`: chapter rendering, word interaction and inspector. `web/src/hooks/useBible.ts`, schemas and api-client own validated data access.
- `web/tests/reader.spec.cjs`: 42 desktop/mobile regressions, including focus, chapter navigation, pending responses and protected file denial. App-shell/header layout already complete.
- `apps/scribeswell/.local/`: ignored local runtime with Python venv; API on 8000, no auto-reload. Shared origin localhost:5179/scribeswell; frontend 5174 proxied. Browser libs at /tmp/pts-browser-libs/usr/lib/x86_64-linux-gnu. Do not expose private environment values.

## Tasks & Acceptance

- [x] Pin/acquire lexicon files, build deterministic safe lexical mappings and document provenance/coverage. No database reset.
- [x] Extend API/schema and tests for lexical details, chapter match metadata and paginated occurrences using existing Bible data.
- [x] Implement tabbed inspector, definitions/roots, BDB reference preview/navigation, root/lemma highlight with dwell cancellation and accessible mobile interactions.
- [x] Remove redundant visible pane labels while preserving accessible identities; add verse targeting for reference/occurrence navigation.
- [x] Observe relevant failing acceptance tests before implementation, then pass affected Python/browser/build checks and verify live local data.

Given two passages and a selected noun/verb, related recorded-root words in both passages highlight without listing relationships. Given keyboard, touch or pointer interaction, selected/preview states remain distinct and stable. Given a dictionary entry, Word shows supplied root/lemma/meaning and expandable source detail; Given Occurrences, the reader can browse matching imported words and open their verse. Given the existing reader, all public/auth, focus, comparison, navigation and data-protection behavior remains intact. Every matrix row requires executed test evidence.

## Implementation Notes

Authorized by the user's request to implement all discussed suggestions. Word/Occurrences tabs chosen to keep result lists out of Word Analysis and leave future Notes extension clear. No additional approval checkpoint for reversible implementation. App-specific capability; promote no shared UI until proven reusable. Scaffold and agent-context impact: none. Documentation belongs here; add/link an application ADR only if a substantive new storage or service decision requires it. Shared services and platform authentication remain unchanged. Root agent will review implementation and live-check before finalizing/committing.

## Implementation evidence (2026-09-27)

Implemented the immutable reference artifact, safe deterministic builder, public lexical/occurrence contracts, chapter match metadata, tabbed inspector, BDB scripture preview/open, delayed preview highlights, and verse-target navigation. Attribution, incomplete BDB status and repeatable source acquisition are in [artifact build documentation](../data/hebrew-lexicon/BUILD.md); source revision/checksums are in [manifest](../data/hebrew-lexicon/manifest.json). The [source audit](verification/lexicon-source-audit.md) documents root coverage and malformed references.

ATDD red evidence: `apps/scribeswell/.local/venv/bin/python -m pytest apps/scribeswell/tests/test_lexicon.py -q` initially failed collection because `services.lexicon_service` did not exist. `LD_LIBRARY_PATH=/tmp/pts-browser-libs/usr/lib/x86_64-linux-gnu npm run test:browser --workspace=apps/scribeswell/web -- --grep 'word study has'` then failed on both desktop/mobile because Word/Occurrences tabs did not exist.

Verification:

- `apps/scribeswell/.local/venv/bin/python -m pytest apps/scribeswell/tests/test_lexicon.py apps/scribeswell/tests/test_reader_integrity.py apps/scribeswell/tests/test_import_bible.py -q`: **15 passed**. Existing Starlette/httpx deprecation warning only.
- `LD_LIBRARY_PATH=/tmp/pts-browser-libs/usr/lib/x86_64-linux-gnu npm run test:browser --workspace=apps/scribeswell/web`: **54 passed**, covering existing reader regressions and the first five lexicon scenarios in both projects. Log: `/tmp/lexicon-browser-check.log`.
- Same browser command with `-- --grep 'current passage follows|explicitly reopening'`: **4 passed**, covering the subsequently added current-pane/targeted-scroll scenarios in both projects. Log: `/tmp/lexicon-navigation-check.log`.
- `npm run build --workspace=apps/scribeswell/web`: passed TypeScript and Vite build; existing >500 KB bundle advisory remains. Log: `/tmp/lexicon-build.log`.
- Builder rerun reproduced exactly the same artifact SHA-256 (source checksums validated before parsing).
- Parent's read-only local live checks: Strong4428 **2,526 words / 1,919 verses**; Strong1254a **53 / 45**; Strong5921a **5,770 / 4,484**. Gen14 king / Gen10 kingdom root highlighting, Genesis filter (**41 words / 22 verses**), and comparison opening passed at desktop/mobile dimensions.

Matrix traceability:

| Matrix row | Executed evidence |
| --- | --- |
| Mapped noun/verb | Python `test_recorded_root_uses_identity_and_not_spelling`; browser `root highlights keep homonyms distinct...`; live Gen14/Gen10 |
| Prefix/augmented/homonym | Python `test_content_identity_preserves_augmented_homonyms`, recorded-root test; browser root-highlight test |
| Missing/ambiguous root | Python missing-entry fallback and content-identity ambiguity tests; no roots fabricated |
| Delayed hover/focus/leave/navigation | Browser root-highlight dwell/blur/navigation and `late occurrence results...pending preview cancels...` |
| Missing/service failure | Python missing-artifact test; browser dictionary retry/missing-entry test; existing morphology/chapter retry tests |
| Occurrences paging/filter/new selection | Python occurrence count/filter/page and bound contract tests; browser occurrence persistence and delayed-result tests |
| Open occurrence/reference | Browser BDB preview/open, source-pane navigation, repeated verse target, mobile scroll preservation, invalid target and Back tests; live comparison target |
| Unsafe XML/source markup | Python unsafe XML/oversize and safe structured sense tests; browser BDB structured reference preview |

Existing comparison assertions were updated only where the specification intentionally removes visible `Passage N ·` analysis prefixes. The close-button regression now targets the sticky inspector header after its relocation. A new reference-navigation fixture was corrected to match the existing selector's accessible label (`Genesis, chapter 1`).

Impact decisions: no scaffold or shared-UI changes; no agent-context changes. This is silo-owned immutable reference packaging explicitly authorized by this spec, with no new storage service/schema contract; no new ADR is necessary. Documentation is colocated here and with the artifact. No migration, production database mutation, deployment or collected-text change occurred. The API package must include the lexicon artifact and `scripts/hebrew.json` (raw lemma variant discovery); common lemmas entail multiple read requests, an optimization opportunity documented in BUILD.md. NET notes and optional Bible-wide root expansion remain out of scope.

## Review Triage Log

Three independent review layers completed. Every finding is recorded separately before grouping; direct corrections retain the approved design and add no new user-facing surface.

| Finding | Verdict | Evidence and route |
| --- | --- | --- |
| Blind 1: inline whitespace disappears | medium | `blocks` discards whitespace-only tails between inline XML nodes; adjacent words/references concatenate. Patch the mixed-content transformation and regression coverage. |
| Blind 2: desktop comparison verse target | medium | `visible` tracks the mobile selection while CSS displays both desktop panes, so a restored secondary verse is skipped. Patch the existing visibility guard and retry the pending target on layout changes. |
| Blind 3: ambiguous identity fallback | medium | Nullish fallback chooses the first numeric identity despite an explicit backend null. Patch to respect null and require exactly one legacy identifier. |
| Blind 4: invalid BDB target | medium | Pinned entry 3247 includes Ezra 13:17, outside the collected chapter range. Patch reference validation using existing collection metadata; never offer navigation to an absent verse. |
| Blind 5: occurrence reads before response pagination | false | This describes the documented fixed-corpus implementation, but no response-bound or latency failure was demonstrated. Read-only measurement of the most frequent lemma (853, 10,979 words/6,782 verses) took 2.536 s; 3068 (6,521/5,522) took 1.635 s. Database reads and public responses are bounded. An index/cache remains a documented optimization, not an unresolved correctness defect. |
| Blind 6: book IDs used for canonical ordering | medium | `book_order` exists independently of IDs; the new occurrence sort should use that order. Patch the sort and test with deliberately reordered IDs. |
| Blind 7: malformed artifact structure | low | Hand-corrupting generated JSON can break reader enrichment, but verified pinned inputs and deterministic build do not produce those structures. Reject adding runtime schema guards for an unlikely manual modification of a generated deployment artifact; missing and invalid JSON already fall back. |
| Blind 8: source variant index compatibility | low | The authorized corpus and import use the same checked-in canonical `hebrew.json`, and no alternate import contract is introduced. Missing packaging can disable lookup, as documented in BUILD; future unmatched direct writes are not part of this import. Reject adding a new index/migration or compatibility subsystem for this hypothetical deployment error. |
| Blind 9: Hebrew/foreign text loses direction metadata | medium | Builder flattens source word/language markup, leaving mixed BDB runs without language or bidi isolation. Patch safe structured text rendering to preserve source language and isolate direction. |
| Blind 10: builder reproducibility/real-entry verification | medium | Manual deterministic rebuild was checked, but tests lack a complete build comparison and real invalid-reference example. Patch tests alongside source-format corrections. |
| Edge 1: comparison reload target | medium | Same verified mobile-flag/CSS mismatch as Blind 2; same patch. |
| Edge 2: backend null overwritten | medium | Same explicit-null fallback defect as Blind 3; same patch. |
| Edge 3: invalid Ezra reference | medium | Same pinned source reference as Blind 4; same patch. |
| Verification 1: chapter metadata contract gap | medium | Existing helper checks and injected browser fixtures do not protect actual chapter response enrichment. Patch HTTP response assertions for roots/homonyms/missing numeric identities. |
| Verification 2: real variant index gap | medium | Occurrence tests replace the index and cannot detect prefix/homonym loss in the real builder. Patch an occurrence test using representative real canonical variants. |
| Parent: stale comparison verse parameter | low | Closing comparison removes its book/chapter but leaves its verse query parameter. Direct deletion correction. |

No finding requires a changed product decision, production write, or destructive re-derivation. These corrections preserve the implemented feature and the user's authorization to finish reversible work.

## Final verification and review outcome

All accepted review corrections are implemented: source inline spacing/language and inherited Aramaic direction; corpus-validated BDB references with unavailable preview navigation disabled; responsive restored-verse targeting; explicit-null/ambiguous identity handling; canonical division/book order; comparison URL cleanup; and real chapter/variant/builder contract checks. No findings deferred and no unresolved release blocker from this change. The three rejected findings and rationale remain individually recorded above.

- `apps/scribeswell/.local/venv/bin/python -m pytest apps/scribeswell/tests/test_lexicon.py apps/scribeswell/tests/test_reader_integrity.py apps/scribeswell/tests/test_import_bible.py -q`: **18 passed**. After strengthening the rebuild check to compare against the committed artifact before rebuilding, the focused `apps/scribeswell/.local/venv/bin/python -m pytest apps/scribeswell/tests/test_lexicon.py -q` passed **10/10**. Existing Starlette/httpx warning only.
- `LD_LIBRARY_PATH=/tmp/pts-browser-libs/usr/lib/x86_64-linux-gnu npm run test:browser --workspace=apps/scribeswell/web > /tmp/lexicon-browser-final.log 2>&1`: **66 passed** (26.2 seconds). Initial review run had 64 passing and two assertions expecting one lookup request; inspection confirmed existing React StrictMode mounts effects twice in development. Assertions now check requested identity uniqueness and that ambiguous/null identities cause no lookup, rather than assuming a production request count. No application behavior was changed to dismiss those failures.
- `npm run build --workspace=apps/scribeswell/web > /tmp/lexicon-build-final.log 2>&1`: **passed**, existing >500 KB bundle advisory only.
- `LD_LIBRARY_PATH=/tmp/pts-browser-libs/usr/lib/x86_64-linux-gnu node /tmp/pts-local/lexicon-live.cjs`: **passed** against the real local shared origin at desktop/mobile sizes, including root-linked highlights, Word/Occurrences, filtered live counts, comparison opening, reload and responsive verse targeting. Final mobile screenshot visually inspected.
- Pinned original source bytes and all manifest SHA-256 checksums verified independently; generated artifact matches a complete rebuild, with real BDB source-text fidelity and valid-target checks. `git diff --check` passed.

The local API was restarted and is healthy. Open **http://localhost:5179/scribeswell/**, select a Hebrew word, and choose Word or Occurrences. No database migration or production deployment was performed or is required for this immutable reference addition; include the reference directory and canonical corpus file when packaging the API. A future NET integration can add Notes alongside the existing inspector tabs.
