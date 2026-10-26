# In-memory workspace tabs: component evidence

Delivery source: [the approved implementation spec](../../../_bmad-output/implementation-artifacts/spec-scribeswell-workspace-tabs.md), consuming [WORKSPACE_TABS_V1](WORKSPACE_TABS_V1.md). Baseline HEAD is `05e4b70e70ef88833f38adacf5e4d20015faa3ca`. This is bounded component evidence for CAP-11/ST-31–34. Parent independent reviews and final full/build qualification are complete; native/actual-owner/session/device/release gates remain deferred. The sections below retain historical handoffs and failed attempts.

## Implementation and ownership

The public workspace owner sits above the single Studies provider and reuses the existing closed reference/URL/snapshot codec and 64-entry anchor cache. Up to twelve ordered in-memory tabs retain independent one-to-four-pane layouts. Creation inserts beside active; the explicit supplied-reference action avoids a picker. Activation and successful closure each push once; replay never pushes. The final reader cannot close. Labels remain private memory and clear on confirmed denial/account replacement, including subsequent public navigation.

Tab-owned presentation records hold study/note associations, tool/subtab, outline/library query/cursor/position and compact analysis state. Origin-bound setters and stable per-tab navigation refs reject closed/replaced view writes. Resource saves, metadata, collections, creation and deletion retain their shared account/resource operation owners. Acknowledgements refresh all referencing views. Closing a tab synchronously removes its private presentation and inheritance entry; closed-history replay creates public-only context.

There is one retained editor host per associated or unresolved note lane, with explicit lane-bound input/composition/retry handlers. Saved unassociated notes do not acquire hidden editors. Different notes preserve DOM/range/owned atoms; shared notes reuse a host. Deliberate last-context discard stops newer autosave while retaining the original unknown operation as an explicit recovery item. Creation keeps the captured original command and known outcome until origin attachment or deliberate authorized opening succeeds.

Departure is rechecked after asynchronous reads/creation follow-up and immediately before association changes. Another live editing context permits immediate departure. The last unresolved context gets bounded recovery and fresh account/view/lane/input/composition/action checks. Background replacement preserves its origin rather than opening a modal on another tab. Sign-out guards unresolved account lanes. Public layout changes cause no note/study deletion.

At capacity, closed-history replay holds the current arrangement and requests an explicit victim. Stay/Cancel closes consent/chooser but retains the exact unmatched-entry marker. Checkpoints and Add current passage remain suspended for that held entry; an explicit retry reopens the chooser. Ordinary navigation commits its real arrangement and clears the marker. The pending incoming snapshot is never overwritten. This records canonical decision357's technical cancellation clarification without changing the frozen intent.

## Chronology and honest red evidence

Before runtime edits, all 39 relevant owning source and protected reader/personal-notes/lexicon test hashes matched the predecessor's `evidence/four-passage-layout/parent-full-after.json`. The predecessor's `parent-full-run.log` and before/after manifests are parent-executed characterization, not a worker-run broad suite. Concurrent unrelated work was preserved.

All logs below are retained under [evidence/workspace-tabs](evidence/workspace-tabs/). They are chronological; no runtime was removed to manufacture a failure.

| Logs | Observed result and significance |
| --- | --- |
| `01-public-red.log` | Local server could not start in the restricted sandbox; this is not acceptance red. An earlier path mistake also failed before tests. |
| `02-public-red.log` | Genuine missing Workspace tabs tablist failure before public runtime changes. |
| `03-context-red.log` | Public test passed; new-tab Reader/tool-context acceptance failed before the private presentation/editor refactor. |
| `04-focused.log`, `05-boundary.log` | Seven existing/new focused cases, then two distinct-lane/last-context cases passed. |
| `06-analysis-red.log` | Initial pagination selector was wrong; not behavioral red. |
| `07-analysis-red.log` | Corrected test genuinely failed retained Occurrences subtab after tab return. |
| `08-recovery-red.log`, `09-focused-matrix.log` | Genuine missing closed-origin creation recovery and displaced-close focus failures; other public history/capacity cases passed. |
| `10-caret-red.log`, `11-caret-focus.log` | Real caret endpoint loss (0/0 rather than 2/4); retained-range generation fixed it. The remaining focus failure traced to a retained picker trigger reopening a selector on remount. |
| `12-focused-matrix.log` | Sixteen passed; two capacity-test assertions toggled an already active Analysis tool off. Expectations were corrected to follow current tool state. |
| `13-held-entry.log` | Both viewport cases passed Stay/Cancel, checkpoint/collection suspension, explicit retry and ordinary navigation. |
| `14-final-focused.log` | Watched-source intermediate only: source/tests changed while it ran. 39 passed and one mobile firstNote timed out waiting for Add note; cause unproven. This is not frozen qualification. |
| `15-delta-focused.log` | Sixteen passed; two mobile delete assertions expected reader text while tools covered it. Tests now explicitly Return to reader before checking visible preserved content. |
| `16-frozen-focused.log` | 54 passed; all 53 owning-file hashes unchanged between `focused-before.json` and `focused-after16.json`. This predates the subsequent corrections below. |
| `17-denial-red.log` | Existing rename403, collection403 and library-denial tests genuinely failed after old origin setters were invalidated by clearing presentation maps. Whole-study403 passed. |
| `18-departure-red.log` | Initial delayed-read assertion toggled retained Analysis off; corrected before behavioral qualification. |
| `19-departure-red.log` | Genuine delayed replacement race replaced unsaved origin text with A second after the other live context departed. |
| `20-boundary-corrections.log` | Ten desktop/mobile denial and delayed replacement checks passed after minimal corrections. |
| `21-view-isolation-red.log` | Genuine private-label resurrection on later public navigation and distinct-library scroll loss when view flags matched. |
| `22-creation-consent-red.log` | Genuine known-created-note recovery loss after late input caused guarded attachment to Stay. |
| `23-view-corrections.log` | Ten viewport cases passed library/label/known-creation corrections and affected library/creation recovery regressions. |

The broader public/private acceptance reds preceded their owning refactors. Several safeguards were source-audit-directed before their dedicated browser assertion, including held-entry cancellation, arbitrary snapshot-key DOM lookup, compact-state pruning, acknowledgement fan-out and token/account binding. Later assertions qualify these; this is not a claim that every helper had an isolated pre-change TDD failure.

## Initial worker verification (before parent P1/P2 audit)

The final affected browser selection is recorded verbatim below. It runs from `apps/scribeswell/web`, using intercepted component fixtures only:

```sh
SCRIBESWELL_TEST_PYTHON=/tmp/scribeswell-manual-python/bin/python npx playwright test --config playwright.config.cjs reader.spec.cjs personal-notes.spec.cjs lexicon.spec.cjs workspace-tabs.spec.cjs --grep 'workspace tabs|tab activation closure|tab labels|twelve tab|valid Unicode punctuation|POP checkpoints|failed saves use inline|same-account reauthentication preserves|unknown response blocks|rename: explicit Save Cancel|rename: 403|rename patch: supplementary|collected current access or lifecycle refusal 403|library search hides unavailable pages|library search restores multi-page|note deletion requires safe-focused|whole-study deletion confirms captured|whole-study deletion current 403|study deletion review recovered creation|four-pane public transitions preserve an unknown' --workers 1
```

Final results: `24-worker-final-focused.log` **72 passed (2.3m)** across desktop and mobile; `25-rename-focus.log` **2 passed (3.6s)** for the existing supplementary-scalar keyboard focus case. `26-build.log`: `npm run build --workspace=apps/scribeswell/web` passed (TypeScript and production bundle), with the existing >500kB chunk warning. `27-diff-check.log`: the scoped `git diff --check` passed. No worker broad all-spec regression was run.

The 53 owning source/test/config hashes in `worker-final-before.json` and `worker-final-after.json` are identical. `worker-final-source-proof.json` records zero changed files. No owning source/test was edited during these final checks. Exact retained stdout hashes are indexed by `logs.sha256`; the local `.gitignore` exception retains only this delivery's safe synthetic/public logs. `rename patch: supplementary` does not match the longer existing test name; the explicit supplementary-scalar/focus case is run separately in the final handoff checks.

## Acceptance traceability

| Contract/acceptance | Executable evidence |
| --- | --- |
| Twelve layouts + unresolved sole context + explicit guarded victim + public-only restore/no push (AC1) | `workspace tabs capacity replay guards the sole unresolved context…` tests Stay, retry, Cancel, suspended collection/checkpoints, ordinary navigation, then successful Close anyway at twelve without an index increase or private restoration. |
| Hebrew/atom/caret A→B→A, one host/lane and origin composition (AC2) | `workspace tabs retain distinct note DOM caret atoms and composition routing…` asserts DOM and owned-atom identity, both Range containers and offsets 2/4, origin composition completion, native Undo/Redo and successful serialization. Shared-lane inheritance asserts no additional note creation. |
| Adjacent complete-reference + Cancel; direct supplied range/no picker | Reader missing-tab acceptance; `workspace tabs direct Open in new tab…` compares the complete cross-chapter range and inherited note identity. |
| Independent context, analysis, outline and library | Private inheritance; distinct library applied-query/scroll; inherited independent pagination cursors; lexicon page/filter/expansion/no hidden request assertions. |
| Exact pushes, final close, manual keyboard/focus, arbitrary safe snapshot identities | `workspace-tabs.spec.cjs` push/replay, roving Home/Enter, close focus/final guard and Unicode/punctuation snapshot-key cases. |
| Public anchor continuity after POP then explicit activation | `POP checkpoints the outgoing live tab anchor…` checks the restored scroll within three CSS pixels. |
| Origin-bound late creation and post-read departure | Closed-origin creation; known creation retained after late input/Stay; delayed replacement after other-context departure, with no background modal. |
| Fresh consent and recoverable unknown originals | Changed-input and changed-layout/account consent; last-context discard compares the original retried operation/payload and proves no hidden editor or background activation. |
| Deletion/account/denial across tabs | Both cross-tab note and study deletion; label mask/recovery/replacement plus later navigation; existing focused403 denial tests. |

## Delivery boundaries and impact decisions

No private API, SQL, migration, owner-service, provider, deployment or production activation changed. No native/actual-owner/session integration fixture ran and no KDG55481/55482 qualification was acquired. Physical iOS/Android selection, keyboard and IME remain unqualified by viewport automation. Parent full browser regression and independent reviews remain required before final component acceptance.

Scaffold: no generator input or template change. Shared UI: app-specific reader/editor retention remains in Scribeswell; no neutral promotion is justified. Agent context: unchanged. Documentation: this evidence and the adopted contract/runtime handoff updated; parent owns canonical delivery tracking. ADRs: no amendment. Durable same-device restoration remains the next contract and has not been implemented or removed.


## Parent initial audit follow-up: P1 malformed origin and P2 delegated closure

The earlier72+2 source-frozen result remains intact as **pre-P1/P2** evidence.
P1 was reproduced before the fix in `28-malformed-tab-red.log`: activating the
invalid original tab incorrectly retained the other tab's canonical Genesis2 URL.
`malformed-red-before.json` / `malformed-red-after.json` prove unchanged red-run
source. The minimal correction retains `invalidSearch` per public workspace,
inherits it only while unresolved, clears it on explicit valid navigation and uses
it instead of ambient entry search when committing an invalid tab. The closed
snapshot/URL codec and private/public boundary are unchanged. The test retains
foreign outer/user history fields, malformed URL/warning and collection refusal,
then proves explicit valid navigation enables collection.

`29-malformed-and-close-green.log`:18 desktop/mobile affected cases passed, with
identical `malformed-green-before.json` / `malformed-green-after.json`. Added
sole-pane delegation checks prove adjacent-tab survival, exactly one push, stable
reference and final-reader close absence. The existing private last-context
discard test now explicitly proves zero DELETE requests.

P2's strengthened focus assertion genuinely failed in
`30-sole-close-focus-red.log`, with identical `sole-close-red-before.json` /
`sole-close-red-after.json`. The delegated control carries `data-close-pane`;
the displaced-close origin matcher now accepts it alongside `data-close-tab`.
The survivor tab receives displaced focus after the commit using the existing
entry/focus guards.

Final affected command, from `apps/scribeswell/web`:

```sh
SCRIBESWELL_TEST_PYTHON=/tmp/scribeswell-manual-python/bin/python npx playwright test --config playwright.config.cjs personal-notes.spec.cjs workspace-tabs.spec.cjs --grep 'retain malformed-origin URL|sole pane delegates|last-context discard retains|malformed Add Cancel|malformed capacity Add|tab activation closure|tab labels|twelve tab cap|capacity replay guards' --workers 1
```

`31-parent-audit-focused-green.log`: **20 passed (46.8s)** across desktop/mobile.
`32-parent-audit-build.log`: workspace TypeScript/production build passed, retaining
the existing chunk-size warning. `33-parent-audit-diff-check.log`: scoped diff check
passed. All53 owning hashes in `parent-audit-final-before.json` and
`parent-audit-final-after.json` are identical; `parent-audit-source-proof.json`
records zero changed files during these checks. The exact stdout index
`logs.sha256` includes these follow-ups. No broad regression, native integration,
production or other investigation was added; parent audit/reviews/regression remain
the next step.

## Review correction handoff — 2026-10-26

This follow-up addresses the13 requested review roots only. The pre-review
qualification above remains prepatch evidence. B5 cache retention was explicitly
deferred by parent triage; B7 chooser identity was rejected by that triage. Neither
was changed here. No storage slice, scaffold, shared UI, agent-context or ADR change
was needed: these corrections stay in Scribeswell's existing browser owners.

| Finding | Correction and browser proof |
| --- | --- |
| B1 | Confirmed denial clears labels on the latest live controller tabs, including a newer inactive rename made while an earlier command awaits its denial. |
| B2 | Dictionary focus intent belongs to deliberate follow/Back navigation. A retained linked entry remount and its late dictionary response preserve the explicitly activated workspace-tab focus. Existing Back, failed-entry Retry and scroll restoration remain covered. |
| B3 | Word scroll capture requires an exposed, connected word view; Notes scrolling cannot overwrite it. Revealing Word restores its retained position without moving focus from its tab. |
| B4 | Queued Edit-mode restoration rechecks account, tab, lane, host and current visibility before touching document selection. A delayed callback cannot replace another retained editor's selection. |
| B6 | Masked Rename controls are disabled with an accessible access-recovery reason. Authorized and anonymous renaming remain covered. |
| B8 | Complete manual keyboard coverage includes Left/Right/Home/End, wrap, Space/Enter, all12 controls' focus visibility, no history push for focus movement and one push per activation. |
| B10 | Closed-origin title and collection401/403 failures retain safe account-level recovery feedback, mask current private labels and preserve surviving tab focus/tool closure. Same-account Retry restores only permitted labels; confirmed denial clears them. |
| E1 | Sole conflicted-note reopen goes through consent and a fresh read rather than the healthy-current fast return. Stay preserves input; Switch anyway opens latest. Other live contexts prevent replacement of the shared conflicted lane. |
| E2 | Live POP retains matching pane/reference analysis generations and gives captured-anchor seeks their own fresh revision. Filters/page survive unchanged Back/Forward; changed reference origins invalidate analysis. Back/Forward anchors and later explicit tab activation restore the captured positions. |
| E3 | Notes retain one compact current note/scroll record per tab. Capture and restoration require the actual exposed note host, preserving distinct long-note tab positions without focus movement or hidden-view writes. |
| V1 | Account-exit approvals are non-destructive until the actual account action and re-evaluate live unresolved lanes/input/composition. Failed/composing background notes, sequential Stay/Anyway cancellation, completed sign-out and late input on a previously saved background lane are exercised. |
| V2 | Actual dictionary-preview and occurrence-row Open in new tab clicks both prove supplied verse, active new tab, no picker and preserved source pane identity/reference. |
| P3 | One UTF-16 code-unit hex formatter supplies tab DOM IDs, panel labelling and focus lookup; accepted wire keys remain unchanged, including keys URI encoding cannot encode. The punctuation/Unicode/whitespace replay case asserts the panel's actual accessible name. |

Exact commands (working directory `apps/scribeswell/web`, environment
`SCRIBESWELL_TEST_PYTHON=/tmp/scribeswell-manual-python/bin/python`):

```sh
npx playwright test --config playwright.config.cjs personal-notes.spec.cjs lexicon.spec.cjs workspace-tabs.spec.cjs --grep 'review tabs|valid Unicode punctuation' --project desktop --workers 1
npx playwright test --config playwright.config.cjs personal-notes.spec.cjs lexicon.spec.cjs workspace-tabs.spec.cjs --grep 'review tabs|valid Unicode punctuation|POP checkpoints|tab labels stay|closing the sole pane|keyboard dictionary Back|Back keeps saved scroll|delayed dictionary cannot|dictionary Back restores|note links: Read Edit|confirmed conflict discard|distinct note DOM' --workers 1
```

The first command's genuine pre-runtime-fix red is
`34-review-regressions-red.log`:14 failed,5 passed. Its next execution,
`35-review-regressions-green-attempt.log`, reached18 passed/1 failed: E1 still
encountered its old conflicted lane at the second guard, requiring the guarded
fresh-read correction. The two additional late-input/shared-conflict assertions
were added after the initial red and are source-audit-directed guards; no separate
prepatch failure is claimed for them.

The second command's intermediate `36-review-affected.log` retained58 passed/4
failed: existing dictionary Back/Retry focus regressed in both viewports. The
correction tracks deliberate navigation focus ownership through a removed Retry
button while cancelling it on external focus. Final frozen execution
`37-review-final-focused.log` passed all62 selected cases across desktop/mobile
(1.8m), including those unchanged existing expectations and strengthened explicit
Back/Forward anchor assertions. No source/test edits occurred during any of these
runs. All53 owning files match between `review-fixes-final-before.json` and
`review-fixes-final-after.json`; `review-fixes-source-proof.json` records no changed
files. Scoped diff-check passed. `logs.sha256` indexes exact stdout through37.

No build, full suite, integration or production verification was run for this
correction turn: parent owns the requested full verification after handoff.

## First full-run corrections P4–P7 — 2026-10-26

Parent's immutable `parent-first-full-run.log` and paired inventory preserve the
observed red:768 passed,8 failed (four roots in both viewports),2 expected skips;
16.5 minutes. The163-file inventory was unchanged during that run (SHA
`c71eab337793559f6311f37e54c00d1d5beab611039df49242711624b50c07f1`).
These failures were traced before changing source or test expectations.

- **P5 runtime correction:** healthy same-current `openNote` now increments only
  its tab navigation marker before revealing Notes. The held `beginRename` read
  therefore fails its original navigation freshness check. Lane/current/DOM and
  title-read identity remain untouched; the existing `finally` still clears loading
  for the same study. The original cancellation test is unchanged.
- **P4 measured fixture correction:** isolated probes against the then-running
  frozen Vite server showed that the added74px tab region and12px gap reduce the
  old1000×760 candidate text area to186.5px per cell, below the200px contract.
  The viewport now uses1000×846, retaining precisely the former grid space:
  grid968×579, four cells476×281.5 and229.5px text each. The original380px trigger
  injection produces78px controls,90px chrome and192px candidate text, correctly
  falling back to one pane; removal restores four. Navigation failure likewise
  falls back and Retry restores four at the identical579px grid height. All
  original count, stability, equal-height, failure and Retry assertions remain;
  an initial200px text-minimum assertion was added. Geometry runtime is unchanged.
  The observed qualification boundary was viewport832→833: candidate199.5→200px
  in fallback, then four visible cells with223px actual text. Parent's saved
  `parent-workspace-grid-boundary-probe.cjs/.json` and the additional
  `post-full-grid-initial-probe.cjs/.json` preserve exact setup/dimensions.
- **P6 adopted account-clear fixture:** the original error snapshot showed closed
  Studies/Analysis and a public reader, matching WORKSPACE_TABS_V1's requirement
  to clear all private context on account change. The test now asserts both tools
  closed and search absent, explicitly reopens Studies, and retains its empty
  candidate/current-empty-result/late-old403-rejection assertions. No runtime edit.
- **P7 adopted departure fixture:** the original test composed unsaved text,
  approved last-context Switch anyway, then expected that abandoned text to return.
  The snapshot's empty reopened note follows the documented abandonment rule:
  the no-attempt lane is released and a fresh read returns saved empty content.
  The fixture now retains another inherited live note context before composing
  and leaving one tab. It asserts no exit prompt while preserving every original
  unsent-text, unchanged-library-flow URL, zero-PUT and no-search-payload-leak
  assertion. URL capture follows deliberate new-tab setup. Existing last-context
  abandonment tests remain unchanged and were included in focused qualification.

Exact focused command, working directory `apps/scribeswell/web`:

```sh
SCRIBESWELL_TEST_PYTHON=/tmp/scribeswell-manual-python/bin/python npx playwright test --config playwright.config.cjs personal-notes.spec.cjs four-passage.spec.cjs --grep 'wrapping controls and navigation errors|opening a note during initial read|account replacement clears candidates|preserves unacknowledged note input|guard only the last live|last-context discard retains|review tabs E1|note links: Read Edit' --workers 1
```

`38-post-full-focused.log`:18 passed across desktop/mobile (33.1s). Scoped
three-file diff-check passed. All163 hashes in `post-full-fixes-before.json` and
`post-full-fixes-after.json` match; `post-full-fixes-source-proof.json` records no
changes during qualification. `logs.sha256` includes the exact new stdout without
altering parent runner files. No build, broad, native, integration or production
checks ran. Source/tests are frozen again for parent full verification.

## Second full-run scroll fixture correction P8 — 2026-10-26

Parent's `parent-second-full-run.log`, paired163-file inventories and
`parent-second-full-scroll-failure.md` remain untouched:775 passed,1 failed,
2 expected skips in16.3 minutes. That frozen source inventory SHA is
`fa4ab1a42a8c454e88f45ac1f719ed4d92a023577e30f42db30d080793ed25b6`.
The failing assertion was the second (B-return) scroll poll, with10px error against
its unchanged <3px requirement. The cause was investigated before any runtime edit.

Temporary test-only instrumentation traced inspector scrollTop writes/stacks,
compact noteScroll map writes, exposed editor/layout dimensions, focus events and
animation frames. `39-p8-scroll-trace.log` observed1 failure and2 passes in three
mobile executions (11.4s), rather than treating green retries as qualification.
In the failed trace, at963ms the test attempted B scrollTop650 while its note GET
was still pending: the Studies outline was575px high with585px scrollHeight and
no exposed editor. The browser clamped the returned test value to10px. At986ms
B's long editor mounted (scrollHeight6213); its first Notes-context layout effect
correctly restored0 and recorded0. On B return at1182ms the effect restored that
same stored0, producing the exact10px test failure. Passing traces instead set650
after editor mount, stored650 and restored650 exactly. No intervening focus move,
post-restore anchoring shift or runtime loss of a retained Notes position was seen.
Parsed events remain in `p8-scroll-traces.json`; both163-file trace manifests match.

`40-p8-deterministic-red.log` then forced the same ordering with a held second-note
GET, still using the original scroll expectation. At976ms the650px assignment
was deterministically clamped to10 (outline585−575); releasing the GET mounted
Notes and recorded0, and the original B-return comparison failed by10. The exact
instrumented case is retained in `p8-deterministic-red-probe.txt`, events in
`p8-deterministic-red-events.json`, and failure context in
`p8-deterministic-red-failure.md`. Paired163-file red manifests match. This is an
observed fixture-readiness defect, not a speculative runtime adjustment.

Only `personal-notes.spec.cjs` changes in the final patch. The E3 test now waits
for the actual intended note's first paragraph before setting its position, and
always holds/releases B's GET to qualify the previously racing boundary. It
asserts that no editor is exposed while that read is pending. Both original
220/650px targets are now also asserted not to have clamped; the original A/B
return focus assertions and <3px restoration tolerances are unchanged. All
instrumentation was removed from final application/test execution. NoteEditor
runtime remains unchanged; no runtime correction was warranted by this evidence.

Exact commands, working directory `apps/scribeswell/web`:

```sh
SCRIBESWELL_SCROLL_TRACE=1 SCRIBESWELL_TEST_PYTHON=/tmp/scribeswell-manual-python/bin/python npx playwright test --config playwright.config.cjs personal-notes.spec.cjs --grep 'review tabs E3 distinct long' --project mobile --repeat-each 3 --workers 1
SCRIBESWELL_SCROLL_TRACE=1 SCRIBESWELL_SCROLL_DELAY=1 SCRIBESWELL_TEST_PYTHON=/tmp/scribeswell-manual-python/bin/python npx playwright test --config playwright.config.cjs personal-notes.spec.cjs --grep 'review tabs E3 distinct long' --project mobile --workers 1
SCRIBESWELL_TEST_PYTHON=/tmp/scribeswell-manual-python/bin/python npx playwright test --config playwright.config.cjs personal-notes.spec.cjs --grep 'review tabs E3 distinct long|review tabs B3 word scroll|review tabs B4 delayed|distinct note DOM|libraries retain distinct' --workers 1
```

`41-p8-focused-green.log`:10 passed across desktop/mobile (16.2s), including
retained DOM/caret/atoms/composition, library scroll, delayed callback selection,
Word/Notes scroll and the deterministic delayed long-note case. Scoped test-file
diff-check passed. `p8-final-before.json`/`p8-final-after.json` match all163 hashes;
`p8-source-proof.json` records zero changes during final verification and only the
one test file changed from parent second full. `logs.sha256` indexes exact stdout
through41. No broader suite, build, native or integration check ran. Source/tests
are frozen for parent verification; test count and test names remain unchanged.

## Third full-run corrections P9/P10 — 2026-10-26

Parent's `parent-third-full-run.log`, paired163-file inventories and failure
contexts remain untouched:774 passed,2 failed (B3 in both viewports),2 expected
skips in13.7 minutes, source SHA
`2eea2464fb3b28140989a8df0ffe8dab19bfb97ae1547ab32e5cb2a1a243bc70`.

**P9 is a fixture-only action correction.** Read-only isolated execution of the
unchanged B3 callback against the then-running frozen server observed2 failures
and1 pass; exact event data and callback harness remain in
`parent-workspace-word-scroll-probe.cjs/.json`. The failed trace captured/stored
Word230 at3859ms with exposed ready content (inspector631px high, scrollHeight2676).
At4043ms, before Notes activation, browser actionability scrolled the inspector to0
to expose the offscreen Notes button; Word was still exposed and legitimately
stored0 at4045ms. Notes focus arrived4099ms and its visibility commit4164ms. On
Word return4475ms, restoration correctly used the now-stored0. The passing trace's
scroll-to0 event arrived only after Word became hidden, retaining230. This actual
sequence refutes the earlier lexical-loading/restored-flag hypothesis: the word
position had already been accepted and stored, and no hidden Notes scroll was
recorded into it.

`parent-workspace-word-scroll-boundary-probe.cjs` explicitly forces
scrollIntoView plus two animation frames before the original Notes click:
`parent-workspace-word-scroll-forced-probe.json` fails the unchanged230/<3px
comparison. Word230 is stored5006ms, exposed Word0 at5235ms, Notes focuses5389ms.
The corresponding keyboard and both-transition keyboard probes pass. In
`parent-workspace-word-scroll-keyboard-both-probe.json`, Notes focus5240ms leaves
Word230 intact; Word focus5630ms leaves Notes600 intact; Word reveals/stores230 at
5750ms. The final source changes ONLY the two tool actions to explicit
`focus({preventScroll:true})` followed by `page.keyboard.press('Enter')`; it avoids
locator actionability/focus scrolling. Both original230/600 assignments, the
<3px tolerance and Word focus assertion remain. WordStudy runtime is unchanged.

**P10 is a demonstrated malformed-provenance callback leak.** The isolated
synthetic-only `parent-auth-query-probe.cjs/.json` held provider `/auth/v1/user`
verification while the public workspace rendered a malformed reader query plus
complete implicit callback parameters. `consumeCallbackError` synchronously
rejects incomplete/error callbacks, but accepts this complete callback pending
SDK verification. Workspace `invalidSearch` therefore captured those query fields
before asynchronous callbackRecovery scrub. After successful SDK completion the
native URL contained only reader/foreign; a subsequent tab action reconstructed
all8 supplied callback fields from that retained string. Valid navigation preserved
them as unrelated query fields and returning to the malformed tab recreated them.
Probe output contains keys/booleans only and all supplied values are synthetic.

Before any helper/runtime change, the registered browser test genuinely reproduced
that path in `42-p10-registered-red.log`:1 failed/1 passed (3.5s). Failure is the
first new-tab query comparison, showing8 callback keys restored after successful
SDK completion/scrub; malformed raw-byte characterization already passed. Exact
failure context is `p10-registered-red-failure.md`; paired163-file red inventories
match. This is distinct from the source-audit-only projection guard added later.

The runtime correction factors existing callbackKeys filtering into ONE pure
`projectAccountCallback(URL)` helper, returning a clone. Existing native
`scrubAccountCallback` delegates to it at the original SDK completion timing;
malformed workspace capture retains only its projected search. Capture does not
mutate the SDK/native URL or history. Deletion occurs only for keys actually
present, so an ordinary callback-free malformed query keeps its original percent
encoding, repeated fields, bare flag, empty value and spacing bytes. Callback
filtering only in a fragment likewise leaves the unrelated raw query untouched.
No copied callback-key policy, publicAccountReturn substitution, premature native
scrub, pending-Auth navigation state or new Auth/provider flow was introduced.

Browser coverage proves that provider verification still sees its callback before
release and completes once; callback keys never return on new-tab/valid-navigation/
return; malformed warning/provenance and unrelated foreign query plus native/Router
state survive. Additional projection coverage proves all existing policy fields
are removed from query/fragment without mutating its input or current URL/history.

Exact commands, working directory `apps/scribeswell/web`:

```sh
SCRIBESWELL_TEST_PYTHON=/tmp/scribeswell-manual-python/bin/python npx playwright test --config playwright.config.cjs workspace-tabs.spec.cjs --grep 'P10 ' --project desktop --workers 1
SCRIBESWELL_TEST_PYTHON=/tmp/scribeswell-manual-python/bin/python npx playwright test --config playwright.config.cjs account-entry.spec.cjs workspace-tabs.spec.cjs personal-notes.spec.cjs reader.spec.cjs four-passage.spec.cjs --grep 'P10 |callback|signup|standalone Create account|confirmation pending|invalid supplied reader|invalid reading|malformed|tab activation closure|review tabs B3 word scroll|review tabs E3 distinct long|review tabs B4 delayed' --workers 1
```

`43-p9-p10-focused-green.log`:98 affected cases passed across desktop/mobile
(1.9m), covering callback/signup/error/session behavior, malformed-reader retention
and collection refusal, public tab transitions, Word/Notes scroll, delayed editor
callbacks and distinct note scroll. Five-file scoped diff-check passed. Final
`p9-p10-final-before.json`/`p9-p10-final-after.json` match all163 source hashes;
`p9-p10-source-proof.json` records unchanged red and green runs. Only two runtime
files and three browser-test files differ from parent third full. Three new tests
add6 viewport cases; existing names/counts otherwise remain. `logs.sha256` indexes
exact stdout through43 without altering parent runner artifacts. No broad/full,
build, native or integration check ran. Source/tests are frozen for parent audit,
build and full verification. These changes reuse the current app-owned Auth and
workspace policies; no scaffold/shared UI/agent-context/ADR change applies.


## Final parent component qualification — 2026-10-26

All784 registered cases across all six `.spec.cjs` files ran on the final frozen
source: **782 passed,2 expected native-browser skips,0 failed (13.3m)**. Exact command:

```sh
SCRIBESWELL_TEST_PYTHON=/tmp/scribeswell-manual-python/bin/python npm run test:browser --workspace=apps/scribeswell/web -- --workers=4 --fully-parallel
npm run build --workspace=apps/scribeswell/web
```

`parent-full-run.log` retains the complete successful stdout; paired
`parent-full-before.json` and `parent-full-after.json` match all163 owning runtime,
test, migration and contract-source hashes. Their exact inventory SHA256 is
`d692edb61d6f60565ce2437e92cde05d1de0338875bfd1f4b938c2c2c2544525`.
Parent also verified every current owning hash. `parent-final-source-proof.json`
records the result. `parent-callback-final-build.log` records the post-P10
TypeScript/production build, exit0; the existing minified-chunk warning remains.
Scoped source/test/new-file whitespace checks passed. `logs.sha256` indexes all49
safe exact stdout artifacts. No source/test changes occurred during final checks.

All three independent review lenses and parent follow-ups are individually triaged
in the delivery:25 rows,23 addressed patch roots,1 pre-existing saved-lane cache
retention defer and1 rejected chooser-identity claim. Parent read the actual initial
runtime/test diff and every repair delta; reviewers saw the recorded prepatch diff,
not an invented final review. The high malformed-tab callback resurrection was
reproduced with synthetic data before correction, and its new regression passes in
both viewports. Historical method limits remain: outer public/private ATDD reds
preceded refactors, but no isolated per-helper test-first claim is made; initial
watched-source run14's mobile setup-timeout cause remains unproven.

All failed broad attempts remain intact: first768pass/8fail/2skip16.5m; second
775pass/1fail/2skip16.3m; third774pass/2fail/2skip13.7m. Their exact source pairs,
contexts and probes explain each corrected runtime or fixture cause. No expected
result was widened to dismiss an unexplained failure. Parallel scheduling preserves
all cases; isolation was audited before using4 workers/fully-parallel. This is not a
repository-wide performance benchmark or physical-device proof.

This qualifies the in-memory component only. No native SQL/migrations, actual
Identity/Access/session integration, live standalone signup/mail, physical iOS/
Android keyboard/selection or release activation ran in this delivery. KDG55481/
55482 were not acquired. Wider gates stay open and the delivery remains in-review
for the user-deferred final integration. Durable same-device storage remains the
next slice; provisional notes are not implemented behavior.

Final impacts: no backend/private wire/schema/migration change; no Access/Identity
implementation or provider configuration change. The app-owned Auth callback
projection reuses the existing policy. No shared scaffold/UI promotion, agent-context
edit or ADR amendment is justified. Existing unrelated working-tree changes are
preserved; the local checkpoint is scoped to this delivery.
