---
title: 'Retain independent reading and writing contexts across workspace tabs'
type: 'feature'
created: '2026-10-26'
status: 'in-review'
baseline_commit: '05e4b70e70ef88833f38adacf5e4d20015faa3ca'
route: 'dispatch'
review_loop_iteration: 0
context:
  - '{project-root}/AGENTS.md'
  - '{project-root}/apps/scribeswell/docs/WORKSPACE_TABS_V1.md'
  - '{project-root}/apps/scribeswell/docs/FOUR_PASSAGE_LAYOUT_V1.md'
  - '{project-root}/apps/scribeswell/docs/PERSONAL_NOTES_V1.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** One reading setup cannot retain the approved independent passage/study/note contexts while readers move between their work.

**Approach:** Deliver in-memory workspace tabs under CAP-11/ST-31–34: independent public layouts and authorized private associations, one shared note resource lane, guarded last-context departure and public-only closed-tab history replay.

## Boundaries & Constraints

**Always:** Consume WORKSPACE_TABS_V1.md and the four-pane codec/Router contracts. Public reading works anonymously. Preserve references/anchors/origin generations, autosave/command identity, IME/atoms/caret/account masks. ATDD/TDD; characterize first. Preserve concurrent work.

**Never:** Clone note buffers/providers; private URL/history data; background focus/tab activation; implicit capacity eviction; final-reader close; layout-triggered record deletion. No durable storage/highlights/owner-service/Leave/factory work; native/migration/actual-owner/session integration/KDG55481/55482 or deployment/production changes. Durable same-device restoration remains next, not removed.

## I/O & Edge-Case Matrix

| Given / when | Then |
| --- | --- |
| Active setup; + versus Open in new tab | Adjacent complete reference; + picker/Cancel retains, direct Open no picker; authorized associations inherited by identity. |
| Switch/rename/open study/Leave | Per-tab context/positions; one activation step/no exit. Label changes no study; study actions move no passages. |
| Same/different notes; delayed outcomes | One lane/host per resource; retain caret/IME/atoms; origin-bound outcomes never hijack active tab. |
| Close pane/tab/final/last unresolved context | No record deletion; nearest survivor/final guard; sole pane delegates. Last-context bounded recovery/Stay/Anyway; another live context leaves immediately. |
| Input/account/context changes during consent | Fresh identity/input/action checks prevent stale discard; original unknown operation remains recoverable. |
| History names live/closed tab at12-cap | Public-only replay/no push; closed restores no private context. Explicit victim uses departure guard; Stay/intervening navigation cancels. |
| Late creation/deletion/denial/account change | Serialized captured creation/recovery; clear affected associations everywhere, all private state on account change. |

</frozen-after-approval>

## Code Map

`A=apps/scribeswell`, `W=A/web/src`. `hooks/useReaderWorkspace.ts`: public tabs/Router/cache, preserve codec. `context/ReaderWorkspaceContext.tsx`, `App.tsx`: shared public owner above single StudiesProvider; retain Auth/Router. `context/StudiesContext.tsx`: tab-scope presentation; keep global lanes/resource operations. Existing saves acknowledge captured lane; global creation/exit need origin/last-context guards. `ReaderPage.tsx`: composition/tools/selection. `WordStudy.tsx` and `StudiesPanel.tsx`: retain tab view/candidate state. `NoteEditor.tsx`: lane redraw loses DOM; retain resource hosts with explicit binding.

## Tasks & Acceptance

- [x] `A/web/tests/{reader,personal-notes,lexicon}.spec.cjs`: protected characterizations and missing-tab acceptance red BEFORE any runtime/helper draft; record chronology, never manufacture red.
- [x] `W/hooks/useReaderWorkspace.ts`, `W/context/ReaderWorkspaceContext.tsx`, `W/App.tsx`: focused red then tab collection/transitions/cap/replay using existing codecs.
- [x] `W/context/StudiesContext.tsx`: focused red then tab views/global resource operations, origin-safe creation/deletion and fresh last-context departure guard.
- [x] `W/components/studies/{NoteEditor,StudiesPanel}.tsx`, `W/components/bible/WordStudy.tsx`, `W/pages/ReaderPage.tsx`: retained hosts/view context, accessible tabs/actions, focus/mobile geometry.
- [x] `A/web/tests/workspace-tabs.spec.cjs`, affected tests: matrix, caret endpoints/late outcomes/stale consent/cap replay cancellation; no native/owner fixtures.
- [x] `A/docs/WORKSPACE_TABS_EVIDENCE.md`, contract/delivery: chronology/commands/hashes/traceability/impacts. Parent owns canonical/reviews/full regression/checkpoint; worker focused tests only.

**Acceptance Criteria:**
- Given12 layouts and sole-context unresolved input, when replay needs a closed tab, then explicit guarded victim selection restores public context without push/overwrite.
- Given Hebrew input/reference atom in A, when switching tabs A→B→A, then lane/DOM/atom/caret survive and composition targets A's single lane.

## Implementation Notes

Planning checkpoint self-review: one coherent goal; no open intent/owner question or irreversible execution. Routine approval delegated by user. Implementation began after the four-pane component checkpoint at the recorded baseline. The initial planning checkpoint had no tab runtime; component implementation, independent review/repairs and final parent full/build qualification are now complete. Wider live integration gates remain deferred. Reuse the predecessor's final parent-run log/manifest as baseline characterization only after verifying identical owning sources; record it as parent-executed, never worker-executed. Run any missing focused characterization and the new missing-tab red before drafting runtime. Do not repeat a broad suite solely to recreate existing evidence. Baseline proof: `A/docs/evidence/four-passage-layout/parent-full-{before,after}.json` and `parent-full-run.log`.

## Spec Change Log

- 2026-10-26 — Canonical decision357 clarifies cancellation of a capacity replay: close chooser/consent while retaining the unmatched-entry marker, checkpoint/collection suspension and explicit retry; ordinary navigation commits its real setup. No frozen intent or acceptance boundary changed.

## Review Triage Log


All three context-free same-capability reviews completed before classification. Agent capacity allowed only one reviewer at a time; every lens used the same frozen diff. Exact reports are retained under `../../apps/scribeswell/docs/evidence/workspace-tabs/review-{blind,edge,verification}.*`. Each finding below was graded individually before grouping; verification-gap claims are trusted as filed.

| ID | Verdict | Route | Evidence / decision |
| --- | --- | --- | --- |
| P1 | medium | patch, addressed | Initial parent audit reproduced malformed A returning with valid B URL (28 red). Per-workspace invalidSearch preserves source query until explicit valid navigation; latest20 affected checks/build passed. |
| P2 | medium | patch, addressed | Initial parent close-row audit added sole-pane/no-DELETE assertions; delegated close lost survivor focus (30 red). Existing displaced-origin match now accepts pane Close; latest20 affected checks/build passed. |
| B1 | medium | patch, addressed | fail() clears captured workspace.tabs, while create/close/rename replace the live array/objects. latest.current.workspace clears only the current clone; later recovery can expose newer inactive labels. Clear the latest live array and test an intervening rename. |
| B2 | medium | patch, addressed | WordStudy mount and ready effects both focus retained initial.linked/focusId. Its tab remount reuses those flags and can take focus from an explicitly activated workspace tab; distinguish restored context from deliberate dictionary navigation. |
| B3 | medium | patch, addressed | WordStudy remains mounted under hidden Notes when tool=analysis, and its common-inspector listener records Notes scrolling without a visibility guard. Studies actually unmounts it, but the Notes path proves position corruption; restore/capture only the exposed word view. |
| B4 | medium | patch, addressed | switchMode's queued restore checks only the bound lane. Retained same-account hidden hosts keep that lane and contained Range, so restore() can replace another active editor's document selection; require current exposed host/lane. Account unmount already nulls the root. |
| B5 | medium | defer, pre-existing | Baseline05e4b70 StudiesContext already cached every opened note in lanes.current and evicted only on account/denial/delete/conflict discard. Unassociated saved-body retention can grow over an account lifetime, but this story did not introduce it. Record bounded cache investigation separately. |
| B6 | low | patch, addressed | Rename stays enabled under searchMasked while its dialog is omitted. Clicking it has no visible result and may leave a deferred edit state. Directly disable the unavailable control with an accessible reason; no new recovery workflow. |
| B7 | false | reject | Chooser buttons already include distinct ordered indices: Close tab1 versus Close tab2 even when labels match. This disproves indistinguishable victims; the last-context guard subsequently discloses unsaved input. Additional pre-choice contextual decoration is not needed to correct that claim. |
| B8 | medium | patch, addressed | The workspace keyboard test executes Home/Enter only; no workspace assertions cover Left/Right/End/Space/wrap or focused-item visibility at12-tab overflow. Existing reader/editor key tests exercise different consumers. Complete focused keyboard coverage. |
| B9 | medium | patch, addressed | At review time, full all-spec browser regression had not run on this provider/editor ownership change. It is already planned and must run after repairs on frozen owning sources, with exact result and unchanged manifests. |
| B10 | medium | patch, addressed | Closed-origin title/collection denial has no combined test. fail() can clear all views while refusing old setters and create no safe feedback record if its captured tab closed; test account-wide masking and visible safe recovery without background tool activation. |
| E1 | medium | patch, addressed | openNote returns unconditionally when id===current, including a conflicted lane. The existing Back to Studies/reopen-latest guidance cannot reach departure or the fresh read for the sole conflicted context. Restore that guarded path while retaining other live contexts. |
| E2 | medium | patch, addressed | incoming() assigns fresh generations to every pane. On live-tab POP with unchanged pane/reference, ReaderPage rejects the retained selection then prunes its analysis fields, losing filters/context. Preserve matching analysis provenance while retaining fresh anchor seeking and changed-reference invalidation. |
| E3 | medium | patch, addressed | Retained note hosts share one scrollable inspector; no per-tab/note Notes scroll capture/restore exists. Switching distinct long notes reuses the other's viewport. Retain compact Notes position under its actual view identity. |
| V1 | medium | patch, addressed | Pre-verified regression gap: single-note sign-out tests and two-note switching tests do not prove exitAccount guards a failed/composing background note or each unresolved lane. Add multi-lane sign-out and Stay/Anyway sequencing coverage. |
| V2 | medium | patch, addressed | Pre-verified regression gap: collected-passage new-tab coverage bypasses both new WordStudy preview/occurrence dispatchers. Parameterize actual clicks proving a new active tab, supplied verse, no picker and preserved source setup. |
| P3 | low | patch, addressed | Parent source audit: raw accepted snapshot keys become DOM IDs/aria-labelledby values. Existing valid Unicode/punctuation key includes spaces; synthetic Chromium probe found1 panel but0 named Genesis1 panels. Use one consistently DOM-safe ID formatter and assert actual panel accessible name. |


| P4 | medium | patch, addressed | Parent full run fails the old wrapping/error fixture before injection: 1000×760 now includes86px of tab-region/gap cost. Isolated actual-browser probe proves186.5px candidate text below200px minimum, with832/833 threshold; 1000×846 reproduces the prior available grid height and every original wrap/error/recovery condition. Adjust fixture height with measured explanation; retain all original assertions and strengthen initial minimum text proof. No geometry runtime change is justified. |
| P5 | medium | patch, addressed | Existing held-rename-read cancellation test fails: healthy same-current openNote returns before navigation increment, so beginRename's captured navigation remains current and opens Title after deliberate note reopening. Advance only navigation in that fast return; preserve lane/DOM and existing titleReads/finally loading cleanup. Original test is the observed red. |


| P6 | medium | patch, addressed | Existing account-replacement library fixture expects Search studies to remain visible. Actual snapshot and source show synchronous account-wide view clearing and default closed tools, as adopted contract requires. Explicitly assert closure and reopen Studies, then retain empty candidate/current results/late-old403 rejection assertions. No runtime change justified. |
| P7 | medium | patch, addressed | Existing library/input fixture expects unattempted composing text to survive last-context Leave plus explicit Switch anyway. Actual empty reopened note follows the adopted abandonment contract: stop autosave and remove the abandoned no-attempt lane. Retain another live inherited note context instead, assert departure has no prompt and retain all unsent input/reader position/zero PUT/no search-body leak assertions. No unsent survival promise or runtime change justified. |

| P8 | medium | patch, addressed | Second frozen full run775pass/1fail/2skips exposes mobile E3 note-scroll restoration drift of10px against unchanged <3px assertion. This failed only at broad qualification, not the focused run; runtime versus fixture timing cause remains unproven. Trace the actual scroll/layout/focus event sequence, reproduce the cause deterministically before correction, and preserve the position expectation. No tolerance widening or success inferred from retries. |

| P9 | medium | patch, addressed | Third frozen full run with4 workers exposes desktop B3 Word scroll restoration difference230px against unchanged <3px requirement. Runtime versus fixture/readiness timing cause remains unproven. Trace painted-data readiness, exposed scroll capture and restore ownership before any correction; preserve the original position expectation and no-focus assertions. |

| P10 | high | patch, addressed | Parent source follow-up plus isolated synthetic-key-only probe reproduces credentials reintroduced from malformed Workspace.invalidSearch: a held complete query callback renders before asynchronous Auth scrub; New tab/return recommits stored raw query, and valid navigation preserves the callback keys as foreign fields. Error/incomplete callbacks scrub synchronously and do not show this path. Factor the existing callbackKeys deletion into one shared pure projection and apply it when retaining malformed provenance; preserve foreign fields/invalid reader and existing SDK callback timing. Do not duplicate policy or invoke early side-effect scrubbing. |

### Grouping and disposition

No distinct claims are merged merely for sharing a file or fix. P1/P2 are already addressed. B5 is one pre-existing defer; B7 is rejected. B9 is the parent-owned full verification root. The remaining13 small source/test correction roots go to the same implementer (B1/B2/B3/B4/B6/B8/B10/E1/E2/E3/V1/V2/P3). Their state/authority requirements are already settled by the adopted contract; no new product decision, owner API, storage or public operation is required. No intent_gap/bad_spec loopback is warranted for these local corrections.

## Verification

- Focused browser commands via `SCRIBESWELL_TEST_PYTHON=/tmp/scribeswell-manual-python/bin/python npx playwright test --config playwright.config.cjs ... --workers 1` from `A/web`; record runnable red before each changed behavior.
- Parent all `.spec.cjs` browser regression after corrections, frozen runtime/test hashes; `npm run build --workspace=apps/scribeswell/web`; `git diff --check` scoped paths.
- Viewport automation does not qualify physical phones or final native/owner/session/release gates.

### Parent implementation and matrix audit

Parent read the actual scoped runtime/test/doc unified diff and subsequent P1/P2 deltas, verified all33 exact stdout hashes and paired53-file manifests, and mapped each frozen matrix row/AC to executed desktop/mobile assertions. The original72+2 focused checks remain pre-P1/P2; latest20 affected checks/build pass on the corrected frozen source. Sole-pane delegation and malformed provenance gaps were reproduced and repaired before review. No final broad pass is claimed.

Baseline characterization is expressly the predecessor parent-run686-pass proof on identical baseline owning sources. Broad public/private acceptance reds preceded their refactors; source-audit-directed helper guards were tested later, so no isolated test-first chronology for every helper is claimed. Historical failed/watched-source attempts remain disclosed. Component documentation tasks are complete; parent review/full qualification/checkpoint and all user-deferred integration/device/release gates remain open.

### Parent audit of review corrections

The same implementer corrected all13 dispatched roots. Parent reconstructed the exact reviewed tree in a temporary directory from the recorded frozen diff and compared the actual repair delta:9 previously changed runtime/test files plus the new DOM identity helper in reader-layout.ts. The runtime and added assertions were read against each individual triage claim. Source changes preserve the shared resource registry, closed public codec and existing expected Back/Retry focus behavior. Account-exit approvals stage consent without discarding earlier lanes and recompute unresolved lanes before the account action; POP separates analysis provenance from fresh anchor seeking.

Exact logs34–37 retain genuine14-failure red,18/19 intermediate,58/62 affected intermediate and final62/62 affected desktop/mobile green. Added keyboard/new-tab checks already passed before runtime corrections; the late-input/shared-conflict guards have no isolated prepatch red claim. Parent verified all37 stdout hashes and every current owning hash against the final53-file before/after pair. B5 remains deferred and B7 rejected. B9 broad verification is running on a separate full owning-source inventory; no result is inferred. The parent TypeScript/production build passed after these repairs, retaining the existing large-chunk warning. Native/actual-owner/session/device/release qualification stays deferred.


### Parent first broad result and bounded correction audit

First full run:778 registered,768 passed/8 failed/2 expected native-browser skips (16.5m). All163 source hashes match its before/after inventory, SHA c71eab337793559f6311f37e54c00d1d5beab611039df49242711624b50c07f1. Exact stdout and8 failure contexts remain archived as parent-first-full artifacts. Four causes appeared in both viewports: P4–P7 were individually traced before any change; three fixtures changed only after contract/source and actual-browser dimension evidence explained their superseded assumptions. P5 is a one-line navigation freshness correction; its existing cancellation expectation is unchanged. Parent read all four actual corrections.

The same implementer's38-post-full-focused log passed18 affected desktop/mobile cases33.1s, including unchanged retained-caret, last-context/unknown-save abandonment and conflict expectations. Parent verified both163-file manifests/current sources. Runtime/tests are frozen for the final778-case parent run now in progress; no final pass is inferred. The parent post-correction production build passed. All22 triage rows remain individually recorded:20 patch roots (19 addressed, broad verification ongoing),1 pre-existing defer and1 rejection. All final live integration/device/release gates remain open.


### Parent P8 trace and readiness audit

Second full:775 passed/1 failed/2 expected native-browser skips16.3m, all163 sources unchanged. The same implementer traced the exact10px B-return failure: the fixture set650 while B GET was pending, recording the old outline's clamped10px; mounting the actual new editor correctly recorded/restored0. Run39 observed the timing split; held-GET run40 deterministically reproduced the same failure. Parent read the fixture delta and trace evidence before accepting its readiness correction. The intended note paragraphs now prove readiness before unchanged220/650px capture, with explicit no-clamp assertions; both original <3px position and focus assertions remain. No runtime changed.

Run41 passes10 affected desktop/mobile cases16.2s on unchanged163-file manifests, verified by parent. Only personal-notes.spec.cjs differs from second-full source. All6 test files use isolated cases and no serial/shared mutable fixtures; read-only Python and per-test filesystem probes were checked. Parent final run now registers the same778 cases with4 workers/fully-parallel to reduce file-serialization time, with exact command/frozen-source proof; no pass inferred. Current23 triage rows:21 patch roots (20 addressed, full verification ongoing),1 pre-existing defer and1 rejection. Deferred final live integration/device/release gates remain open.


### Parent P9/P10 audit and final verification dispatch

Third full:774 passes/2 failures/2 expected skips13.7min on unchanged163-file source. Both Word-scroll failures are traced to pre-activation actionability scrolling, not lexical readiness or hidden-view capture: the isolated forced-order probe stores230 then0 while Word remains exposed, and returns0; non-scrolling focus plus native keyboard activation preserves230. Parent read the exact two test-action replacements; no WordStudy runtime changed and the original positions/tolerance/focus assertions remain.

The separate synthetic-only callback probe demonstrates the high P10 privacy failure. Registered run42 genuinely fails on callback keys returning after SDK completion, before the helper change; its raw-byte characterization already passes. Parent reads the minimal pure cloned-URL projection using the existing callbackKeys policy, original scrub delegation and retained malformed-search projection. Actual native URL is untouched by projection, SDK timing/standalone/session behavior unchanged, callback-free raw query bytes retained. The installed SDK parses callback parameters synchronously before first await with this app's default null lock; no extra pending-callback state machine or Access path is introduced.

Run43 passes98 affected desktop/mobile checks1.9min on unchanged163-file manifests, verified by parent. Exactly2 runtime and3 test files differ from third full; all47 stable stdout hashes and current owning hashes verified. Three new meaningful cases add6 viewport registrations, so the final full run now registers784 cases with4 workers/fully-parallel. No pass inferred. Current25 individually triaged rows:23 patch roots (22 addressed, broad verification ongoing),1 pre-existing defer,1 rejection. Wider final integration/device/release gates remain open.


### Final parent result and checkpoint boundary

All784 registered component browser cases ran:782 passed/2 expected native-browser skips/0 failed13.3min, final production build passed (existing chunk warning). All163 owning hashes stayed byte-identical before/after/current; inventory SHA d692edb61d6f60565ce2437e92cde05d1de0338875bfd1f4b938c2c2c2544525. Scoped whitespace checks and all49 stdout hashes verified. Exact commands, source proof, three retained failed broad attempts, individual fixture/runtime causes and historical method limits are recorded in WORKSPACE_TABS_EVIDENCE.md. All25 triage rows are resolved for this bounded component:23 patch roots addressed,1 pre-existing defer,1 false rejection. No wider capability acceptance inferred.

Keep in-review for the explicitly user-deferred native/actual-owner/session/device/release integration gates; bounded component qualification is complete. No KDG55481/55482 acquisition, migrations, production/provider activation, Access/Leave/factory implementation or durable device storage occurred. Local commit must include only this delivery's explicit source/test/docs/evidence allowlist, preserving README/canonical spec/deferred/unrelated working-tree changes. No push. Durable restoration continues as the next authorized bounded slice.
