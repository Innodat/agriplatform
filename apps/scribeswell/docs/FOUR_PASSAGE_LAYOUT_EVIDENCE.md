# Four-passage layout evidence

Status: locally component-qualified; delivery remains in review for the deferred
final integration/device/release gates. The adopted [contract](FOUR_PASSAGE_LAYOUT_V1.md)
and [delivery spec](../../../_bmad-output/implementation-artifacts/spec-scribeswell-four-passage-layout.md)
remain authoritative. This is public-reader work only. Final owner/native/session,
physical iOS/Android selection/IME/keyboard and production gates are not passed.
Workspace tabs, per-tab private associations and durable same-device restoration
remain subsequent deliveries; none of the canonical 11 capabilities/38 stories is removed.

## Observed chronology and limitations

1. Loaded the whole delivery spec and all three frontmatter context documents before
   implementation inspection. Codec/controller files were **drafted before their
   focused tests**. This is an explicit TDD-ordering gap; there was no original
   focused codec/controller red. The drafts were briefly moved to `/tmp`, then
   restored before any browser execution; no missing-module result is evidence.
2. Two startup attempts failed before tests: invoking the web configuration from
   the repository root gave `Process from config.webServer was not able to start`;
   a subsequent command used web cwd with repository-relative move destinations,
   so those moves failed and the restricted socket startup failed. Drafts were
   restored from repository cwd. Local browser port 5182 was then run with authorized
   socket escalation. No shared KDG port or native fixture was used.
3. Before ReaderPage wiring, from `apps/scribeswell/web`:
   `npx playwright test --config playwright.config.cjs --project desktop --grep 'four panes preserve|closed codec|late chapter responses|reader failures can be retried' --workers 1`.
   Observed **one missing-Add failure** (30-second wait for `Add reader pane`) and
   **three passes**, 33.0 seconds: drafted codec assertions, existing late-chapter
   isolation, existing retry/location behavior. Session 3788. This establishes a
   genuine outer acceptance red and two pre-wiring characterizations, not complete
   pre-refactor characterization of focus/ranges/editor/IME/operations.
4. Broader focus/editor/IME/original-operation protection was exercised after
   refactoring. The first wired focused run, session 98700, passed seven cases in
   10.4 seconds (four-pane/codec, composition deferral, unknown-original-operation,
   late chapter, retry, focus). Its command appended
   `|focus mode preserves|composition defers autosave|unknown response blocks`
   to the preceding grep expression. Initial build failed on an unused import and
   unsupported `Object.hasOwn` library target; removed the import and used
   `Object.prototype.hasOwnProperty.call`. Subsequent production build passed,
   with the existing large-bundle advisory.
5. `npx playwright test --config playwright.config.cjs four-passage.spec.cjs --workers 1`
   first passed four cases in 4.4 seconds, then the expanded suite passed **16/16**
   in 18.0 seconds (session 81045), across desktop and mobile viewport projects.
   One preparation attempt used the wrong cwd for its Python/test append commands;
   those commands failed without changing files; its browser run therefore covered
   only the earlier four cases. The expanded run followed the successful append.
6. Affected reader regression command:
   `SCRIBESWELL_TEST_PYTHON=/tmp/scribeswell-manual-python/bin/python npx playwright test --config playwright.config.cjs reader.spec.cjs --workers 1`
   observed **46 passes / 4 failures**, 1.8 minutes, session 74023. Two per-viewport
   failures expected a second pane/Close comparison after invalid coordinates;
   the contract instead requires one safe fallback and final-close refusal.
   Two expected the comparison inspector below both readers at tablet width;
   available-container geometry now permits the independent inspector beside readers.
   Assertions were updated to the adopted safe fallback/final-close and measured
   side-tool behavior while keeping navigation/late-response/scroll protections.
7. A later 46-case selection, session 63201, was **contaminated by runtime/test
   edits while Vite and tests were active**. It reported 41 passes/5 failures in
   2.1 minutes, including desktop private-UI loss during HMR. Its results do not
   qualify runtime correctness. Source edits also exposed real focus/geometry
   restoration competition and a test that toggled an already-selected word off;
   both were addressed before the frozen run. Do not treat unchanged isolated
   passes as proving a broad suite pass. Complete pre-refactor characterization
   and original codec/controller-red chronology remain unfulfilled historical
   requirements; later checks cannot reconstruct them.
8. The subsequent focused run hashes all six affected runtime files and four
   browser test sources before execution; no runtime/test edits are permitted
   until it finishes. Exact source hashes and retained log are under
   `evidence/four-passage-layout/`. Results are appended after execution.

## Requirement-to-check mapping

| Contract requirement | Executable checks |
| --- | --- |
| Add, full canonical duplicate, Cancel keeps pane; four-pane capacity and explicit target replacement; active-neighbor close | `four-passage.spec.cjs`: four-pane identities/capacity; complete-range duplication/replacement |
| Closed URL grammar, new precedence, legacy input, size limits, complete ranges, reference-only chapters | focused codec cases; existing reader typed range/reference-only boundary cases; personal-notes collected/reference-link cases |
| Closed snapshot, offset/word bounds, unique active membership; preserve primitive/array usr and foreign outer/user fields | focused codec snapshot case; primitive/array replay cases; foreign state/exact-push case |
| Exactly one push per deliberate action; activation replaces; matching identity/anchors on repeated browser replay | focused push/state/repeated replay and same-reference independent-anchor cases |
| Hidden-pane ready seek applies once; repeated identical Open seeks freshly; independent errors and stale work | reader late chapter/morphology/error/independent-scroll cases; lexicon explicit reopen, responsive ready-seek cases |
| Open here uses active target even with distinct analysis origin; beside inserts adjacent | lexicon active-versus-origin semantic-action case |
| Minimum 320px/16px geometry, one/two/three columns, four-pane two-row, short-height switcher; independent overflow | focused reduced-height case, existing viewport/scroll tests, geometry anchor case |
| Preserve focus clamp/Escape, distinguish geometry clamp and user movement | reader focus/roundtrip/selector Escape cases; focused layout-clamp case |
| Preserve same editor/owned atom/composition and original save operation; public transitions issue no note mutations | personal-notes new four-pane composing editor/owned-atom case and original-operation case; existing composition/unknown-save cases |
| Malformed fallback uncollectable, Studies opens without rewriting input URL | unchanged malformed-coordinate matrix in `personal-notes.spec.cjs`; new codec tests |

Existing legacy-emitted URL assertions now project the new closed public wire into
coordinates for the same behavioral expectations. Tests continue to load real legacy
links. Actual deliberate URL writing is separately checked to emit `reader` and
preserve unrelated query/hash. Binary Compare controls were replaced with Add plus
picker Cancel and pane-specific Close. Identical Open beside now adds a pane; a
fresh repeat seek is checked through Open here on the active existing target.

## Implementation and impact decisions

`reader-layout.ts` owns the handwritten closed public codec; `useReaderWorkspace.ts`
owns one ordered stable-keyed workspace, bounded public entry cache, Router navigation,
checkpointing and replay. `PassagePane` retains isolated requests/scroll/picker/ready
seek, exposes one-based source word position, and protects geometry anchors. Analysis
uses semantic here/beside callbacks with exact origin navigation identity. Studies
provider/lane/editor ownership and saving code are unchanged; the tools subtree is
not keyed by pane/layout and no lane cloning is introduced.

Scaffold: no change; these patterns are app-specific and no reusable neutral consumer
has proved promotion. Shared UI: no promotion. Agent context: no new rule. Documentation:
adopted contract, this evidence and the delivery record describe component results and
remaining gates. ADRs: no amendment/new decision. Database, migrations, API wire,
owner services, provider configuration, deployment and production: unchanged.

The parent owns canonical/audit reconciliation, independent reviews, final complete
browser regression and checkpointing. Runtime qualification must be reported against
the reviewed frozen sources, not an earlier draft or contaminated run.

The first frozen focused run passed **34/34 in 50.5 seconds** (session2241).
`focused-before.sha256` and `focused-after.sha256` match byte-for-byte, and
`focused-run.log` retains its exact output. Its command was:

```sh
SCRIBESWELL_TEST_PYTHON=/tmp/scribeswell-manual-python/bin/python npx playwright test --config playwright.config.cjs --grep 'four-pane|four panes|closed codec|controller preserves|non-record Router|independent same-reference|codec rejects|reduced-height|Add duplicates|layout clamps|comparison bounds|comparison isolates a late|focus roundtrip|Open here follows|explicitly reopening' --workers 1
```

After that run, source inspection found that pointer/focus bubbling on an inactive
pane's Close button could activate it before closing, changing the selected survivor.
The Close control now excludes those activation events; a focused inactive-close and
absent-native-key replay regression was added. This later change requires the next
frozen-source verification recorded below; the34-case pass applies to its own hashes.

## Subsequent frozen verification and audit corrections

The full affected public-reader/word-analysis/controller suites passed **128/128 in
2.8 minutes** (session94087):

```sh
SCRIBESWELL_TEST_PYTHON=/tmp/scribeswell-manual-python/bin/python npx playwright test --config playwright.config.cjs reader.spec.cjs lexicon.spec.cjs four-passage.spec.cjs --workers 1
```

`verification-before.sha256` and `verification-after.sha256` match; exact output is
`verification-run.log`. This is pre-audit-correction evidence, not the final sources.

Parent source audit then identified structured foreign `usr` values (Date/Map/Set)
being mistaken for mergeable records, and a collision between layout revision and
pane-generation counters after close/add/POP. A separate usable-height boundary
check measured175px text scrollports at1100×650, below the required200px. Each was
observed failing before its corresponding fix:

```sh
npx playwright test --config playwright.config.cjs four-passage.spec.cjs --project desktop --grep 'structured foreign|row qualification' --workers 1
npx playwright test --config playwright.config.cjs four-passage.spec.cjs --project desktop --grep 'capacity confirmation refuses' --workers 1
```

The first had **two failures**; the second had **one stale-confirmation failure**.
See `audit-state-height-red.log` and `audit-capacity-red.log`. Fixes preserve non-plain
structured values untouched, use a separate monotonic layout generation, and subtract
measured toolbar space (minimum52px) before qualifying each200px text row.
No approved geometry threshold was relaxed.

The frozen audit corrections plus editor/focus/malformed regression selection passed
**68/68 in1.4 minutes** (session51985):

```sh
SCRIBESWELL_TEST_PYTHON=/tmp/scribeswell-manual-python/bin/python npx playwright test --config playwright.config.cjs --grep 'four-passage|four-pane|passage review malformed current|focus roundtrip|Open here follows' --workers 1
```

`audit-fix-before.sha256` and `audit-fix-after.sha256` match; see `audit-fix-run.log`.
Later tests extend the codec bounds and verify different-reference capacity replacement,
so final focused hashes/log are retained separately. The8192-byte gate is tested with
an oversized invalid state and a valid four-pane multibyte-key snapshot below8192;
the oversized fixture also violates key-length constraints. This is overlapping-bound
rejection, not a claim that a valid8192-byte boundary is reachable in the closed grammar.
Final-pane semantic refusal is source-audited in the controller; browser assertions
prove its hidden control, not a direct programmatic invocation of the final-close guard.

The next frozen selection passed **46/46 in1.2 minutes** (session35033), with
matching `final-focused-before.sha256` / `final-focused-after.sha256` and retained
`final-focused-run.log`:

```sh
SCRIBESWELL_TEST_PYTHON=/tmp/scribeswell-manual-python/bin/python npx playwright test --config playwright.config.cjs --grep 'four-passage|four-pane|capacity beside|Open here follows|focus roundtrip|collected matching chapter|note links: keyboard edit' --workers 1
```

It adds real differing-reference Open beside at capacity, nonactive explicit target
replacement, Cancel retaining refs/keys/positions, URL pane/active/version/unknown-field
bounds, duplicate snapshot keys,128/129-character keys, one-based word0/4096/4097,
canonical verse/chapter rejection and offset edges. The valid multibyte four-pane
snapshot is **3854 UTF-8 bytes**; it is a valid near-maximum-key fixture, not a claim
of an independently reachable8192-byte exact valid boundary. Public anchors and keys
are constrained separately; the oversized invalid fixture exercises overlapping guards.

Parent audit then required an evident desktop active target, because analysis origin
can differ from Open here's destination. The new `desktop active-pane cue` assertion
failed before implementation (`active-cue-red.log`). A restrained inset ring, visible
Active text and `aria-current` now distinguish the target without color alone.
The regression requires focus activation to preserve analysis origin, both scroll
positions and history index. A subsequent full focused handoff run is retained separately.

## Startup identity and ready-seek corrections

The next source-frozen handoff selection had **77 passes / 1 failure in1.8 minutes**
(session64363); `handoff-before.sha256` and `handoff-after.sha256` match. The mobile
geometry case expected921px after its resize round trip and received0px. Its original
expected positions were retained. `handoff-run.log` preserves the failure; this run
is not a full pass. The build on those sources passed (`handoff-build.log`).

A separate initial-entry audit found that the state initializer and initial layout
effect both ingested the same entry. An added-nodes-only MutationObserver test initially
passed because the old pane was created before root attachment. Including removed
nodes exposed **two committed pane keys where one was required** (`initial-red.log`);
`initial-added-only-pass.log` retains the earlier insufficient assertion. The controller
now acknowledges its already-ingested initial entry instead of rebuilding it in the
effect. The unchanged geometry case and corrected initial-identity case then passed
**20/20 in20.6 seconds**, five repetitions in both viewports (`startup-fix-run.log`;
matching startup before/after hashes):

```sh
npx playwright test --config playwright.config.cjs four-passage.spec.cjs --grep 'initial StrictMode entry|layout clamps' --repeat-each 5 --workers 1
```

That later pass alone does not prove the exact cause of the historical77/1 failure.
A synthetic regression reacted when ready text entered the DOM, chose120px and
observed the next two animation frames. With initial identity already fixed it failed
120px → 0px (`ready-seek-red.log`). Initial reset and ready target application were
moved to layout effects so application seeking precedes paint; hidden targets still
wait for visibility/readiness. The next frozen86-case selection still reported
**84 passes / 2 failures in2.0 minutes**, both that synthetic ready-position assertion
(`complete-run.log`, matching complete before/after hashes, passing build).

This showed that moving the application seek alone did not establish the synthetic
failure's cause. Temporary public-only setter/shape tracing then recorded reset0,
ready seek0, observer input120, with **no later JavaScript scrollTop setter**. The same
273px scrollport/1194px content subsequently emitted native120→119 events; earlier
untraced runs ended at0. `ready-setter-trace.log` and
`ready-native-position-trace.log` retain those diagnostics. The synthetic action was
before painted/actionable reading and stable font layout; its red must not be claimed
as proof of a delayed JavaScript seek. The exact historical77/1 cause remains
unproven. No temporary production instrumentation was introduced, and the temporary
setter instrumentation was removed from the tests.

The final regression uses painted actionable ready text, actual wheel input and
font readiness, retaining the exact120px expected position. It does not add a wait
to the original geometry/clamp case or relax its expected positions. Layout-effect
seek timing remains justified by the requirement to finish app-owned initial seeking
before the reader can act on painted ready text. The final frozen matrix also adds
measured three-column, below992px wrapping, four-pane two-by-two and visible-tool
available-container geometry checks, using pane rectangles and real widths rather
than CSS implementation strings.

## Review-ready component verification

The final frozen selection passed **54/54 in1.3 minutes** (session62354):

```sh
# cwd: apps/scribeswell/web; authorized local browser socket5182
SCRIBESWELL_TEST_PYTHON=/tmp/scribeswell-manual-python/bin/python npx playwright test --config playwright.config.cjs --grep 'four-passage|four-pane|capacity beside|Open here follows|desktop active-pane cue|focus roundtrip|responsive reveal apply|explicitly reopening' --workers 1
```

`review-ready-before.sha256` and `review-ready-after.sha256` match byte-for-byte;
`review-ready-run.log` is the exact retained output. This selection covers every new
codec/controller/capacity/geometry/active-cue case, actual wheel reading, initial
StrictMode identity, existing repeated/hidden ready seeks, focus roundtrip, composing
editor/owned atoms and original unknown save operation. The prior current-runtime
86-case attempt's84 passes retain the malformed-coordinate and complete-range
collection/note-link coverage; its two withdrawn synthetic trigger failures are
explicitly recorded above, not counted as a full pass. The parent still owns the
complete browser regression on reviewed final sources.

`npm run build --workspace=apps/scribeswell/web` passed on the final sources
(`review-ready-build.log`), with the existing bundle-size advisory. `git diff --check`
passed. Before this final freeze, one whitespace-only blank line was removed from
PassagePane; no functional change was made for that cleanup. All owning runtime/test
sources stayed frozen during the final run. Documentation-only edits afterward do
not change those recorded source hashes.

Remaining limits: the original codec/controller unit-red and complete pre-refactor
characterization chronology gaps cannot be retrospectively repaired; no claim of full
ATDD/TDD ordering is made. Exact cause of the earlier77/1 native-position occurrence
is not proven. Final-pane guard invocation is source-audited; its hidden control is
browser-tested. The8192-byte independent valid boundary is not claimed reachable.
Physical devices, native SQL/owner/session integration, release/activation and the
parent's independent reviews/full final browser suite were still open at that
54-case handoff; their eventual result is recorded below. No native/private
integration or shared KDG port was run for this slice.

## Review corrections and bounded verification

The review corrections preserve malformed-link provenance through Add, capacity
replacement, picker Cancel, repeated Back/Forward and refresh. These commands retain
the original unresolved URL and duplicate invalid state using the existing closed
native snapshot grammar. A deliberate valid passage choice resolves the public
arrangement; no per-pane public validity field was added. Focused tests assert the
one-push Add behavior and that collection stays unavailable until that choice.

Reader geometry now observes control, error and scrollport geometry in addition to
the outer grid. Measured wrapping cost is retained while single-pane fallback widens
the controls, avoiding a self-induced grid/single loop; changing the actual chrome
requalifies it. The regression changes toolbar width and produces/removes a real
navigation error while the outer grid height stays fixed, asserting at least200px
text rows. Missing restored anchors fall through to a present explicit reference
start before chapter top. Focus displaced by a removed Close control moves to the
active survivor's passage control without scrolling or an extra history entry;
unrelated deliberately placed focus remains untouched. Pointer gesture ownership
now lasts until completion instead of expiring after one second, retaining current
entry checks for late completion and deferred capture.

The composing-editor regression demonstrated a lost retained range after Add.
`NoteEditor` remembers only ranges whose endpoints belong to its current root and
restores them only on explicit editor focus with the same lane, account and input
generation. A new pointer placement, detached endpoint, changed lane/account,
reading mode or new input generation prevents restoration. Both collapsed caret
and noncollapsed range endpoints (including original text-node identity) are now
asserted through Add, Close, repeated replay, composition completion and saved
feedback; the test explicitly refocuses after intentional UI focus transfers.
Existing account replacement, lane switch, IME cancellation and external-focus
protections were included in the focused run. Wrapped-anchor coverage now uses
multiword wrapped verses with word IDs distinct from one-based source positions,
captures a later source word, and verifies its relative scrollport offset on replay.
New test blocks are formatted directly; no test framework/dependency was added.

`review-corrections-red.log` preserves all eight observed failures. The wrapped-word
case was a fixture precondition failure (the chosen word had not wrapped), not
proof of a product defect. `review-corrections-pass1.log` preserves5 passes and3
failures: the explicit target could not reach the viewport top with the original
short chapter/tall viewport; the scroll test expected an unrounded raw position
rather than the actual canonical anchor offset; the malformed test toggled an
already-open Studies tool shut. These fixture corrections did not weaken the
product anchor, collection or focus assertions. `review-corrections-pass2.log`
records8 desktop passes in11.6s. The subsequent final focused selection passed
**46/46 in1.4 minutes**, both viewport projects:

```sh
# cwd: apps/scribeswell/web; authorized local browser socket5182
npx playwright test --config playwright.config.cjs --grep 'review: (missing restored|closing a focused|a scrollbar|wrapping controls|wrapped word|malformed Add|malformed capacity|a late gesture)|four-pane|a deferred outgoing checkpoint|available-container geometry|layout clamps|focus roundtrip|note links: (account replacement|note switch|cancel invalid IME)|note links patch: deliberate external focus|note links review: interrupted composition' --workers 1
```

Exact output is `review-corrections-focused.log`; the before/after SHA256 source
manifests match byte-for-byte. Runtime and tests stayed frozen during that run.

The parent then identified account signup return filtering as an affected consumer
of the new URL. `review-account-return-red.log` records two genuine desktop failures:
intercepted signup discarded the complete multi-pane range arrangement; supplied
invalid reader JSON blended legacy fields into the callback. `publicAccountReturn`
now reuses the real reader parser/serializer only when `reader` is supplied, retains
only a valid closed public arrangement, rejects malformed/duplicate/oversized/
unknown-version/extra-field reader values without legacy blending, and keeps the
fixed origin/application-root callback. The absent-reader legacy path is unchanged.
The intercepted signup fixture also contains hostile destinations and private study/
note fields, all excluded from the callback. No provider/service integration ran.

```sh
# Observed red:2 failed, desktop
npx playwright test --config playwright.config.cjs tests/account-entry.spec.cjs --project desktop --grep 'review:.*(signup retains|invalid supplied)' --workers 1
# Final affected signup/legacy/callback selection:12 passed in8.3s, both projects
npx playwright test --config playwright.config.cjs tests/account-entry.spec.cjs --grep 'review:.*(signup retains|invalid supplied)|confirmation pending is neutral|return helper drops|valid provider signup callback|invalid callback preserves existing' --workers 1
```

`review-account-return-focused.log` and matching before/after source manifests retain
that final frozen verification. `git diff --check` passed. No broad regression or
new build was run during these corrections; the parent owns those final checks.
The local evidence-directory `.gitignore` narrowly exempts only this delivery's
`.log` files from the global exclusion. All original outputs, including failures,
are retained byte-for-byte and indexed by `logs.sha256`; they contain safe synthetic/
public test output. Global ignore rules and unrelated logs are unchanged.

## Inactive-pane prolonged gesture correction

After the review-correction handoff, the parent's public probe found that a native
pointerdown captured the inactive pane's old entry before React activation replaced
that entry. The registered inactive-pane regression reproduced the precise failure:
expected verse8/offset−14 after1500ms, stored verse4/offset−6. Exact failing output is
`inactive-gesture-registered-red.log`; the parent's standalone probe and its red log
also remain in this evidence directory. This is an additional observed runtime
failure, distinct from the earlier active-pane gesture case and rounding fixture.

The smallest correction invokes the existing pane activation action during native
scrollport pointer capture, then records gesture ownership against the resulting
entry. The subsequent React activation coalesces as a no-op. No transfer state,
public schema or additional history push is introduced. POP explicitly clears
pending pointer gesture ownership; genuine navigation remains protected by exact
entry identity. Tests now exercise prolonged gestures starting in both active and
inactive panes, asserting activation uses replace without increasing history index,
and late completion after navigation and POP.

```sh
# cwd: apps/scribeswell/web; authorized local browser socket5182
# Registered red before runtime repair:1 failed
npx playwright test --config playwright.config.cjs tests/four-passage.spec.cjs --project desktop --grep 'a scrollbar gesture.*inactive pane' --workers 1
# Frozen affected-only verification
npx playwright test --config playwright.config.cjs tests/four-passage.spec.cjs tests/lexicon.spec.cjs --grep 'a scrollbar gesture|a late gesture completion|controller preserves foreign native state|closing an inactive pane|a deferred outgoing checkpoint|layout clamps|available-container geometry|row qualification|wrapping controls|desktop active-pane cue' --workers 1
```

The final affected-only selection passed **24/24 in29.1s**, both projects, including
active/inactive long gestures, navigation/POP late completion, activation cue,
replace/push counts, deferred entry capture, layout clamps and measured geometry.
`inactive-gesture-focused.log` retains exact output; `inactive-gesture-before.sha256`
and `inactive-gesture-after.sha256` match byte-for-byte. Sources were frozen for
that run. `git diff --check` passed. No broad suite or build ran; parent owns them.

A final parent audit noted that clearing only the pointer gesture on POP left its
pending timer and one-second intent window alive. The registered rapid Back/Forward
case observed a genuine additional red: after replay returned to the same native
entry, a geometry-style scroll with no new input changed that entry's snapshot to
verse8/offset−14. `inactive-gesture-rapid-pop-red.log` retains the failure. POP now
also cancels the pending capture timer and expires input intent. The final frozen
command above was repeated with `rapid POP replay` added to its grep selection.
The initial24-pass result remains evidence for its earlier sources, not this final
cancellation expansion.

Final result: **26/26 passed in33.3s**, both projects. Exact output is
`inactive-gesture-final-focused.log`; final before/after source SHA256 manifests
match byte-for-byte. `git diff --check` passed. No runtime/test edits followed that
frozen run. Parent full regression/build remain pending.

## Pending deliberate movement before resize observation (P3)

Parent full regression completed with683 passes,2 expected native skips and1 failure
in13.3 minutes on its frozen160-source aggregate
`9f2d84d2c3548e2a34d12af7cacdc4083687a645dcd667e2f8a6eaa53f636466`.
The retained `parent-full-clamp-failed*` artifacts and
`parent-clamp-failure-context.md` identify the original clamp case's second
assertion: latest120 was overwritten to921. The first bottom-preservation assertion
passed. This differs from the historical first921→0 occurrence; this investigation
does not establish that historical occurrence's cause.

The parent's retained public-only `scribeswell-four-passage-clamp-trace.cjs` and log
establish ordering: deliberate setter120 at823.8ms with height273/max921; pending
scroll delivered at827.3ms after growth to height673/max521; `moved()` rejected the
changed dimensions; pane ResizeObserver at827.6ms wrote the obsolete held921,
natively clamped to521; shrink then restored921. The first two passing probes had
coalesced viewport changes, so they had not exercised the actual intermediate size.

Before runtime repair, the registered regression reproduced120→921 deterministically
(`pending-movement-red.log`). It establishes a held bottom, then in one JavaScript
task sets120, changes the real scrollport height by400px, forces measurement and
delivers the pending scroll before ResizeObserver. It asserts both actual grown and
restored heights and retains the exact120 expectation. Two animation frames allow
native observation; there are no fixed sleeps, altered original expectations or
mocked observers. The original clamp case remains unchanged.

`PassagePane` now retains its last observed/generated scroll position. Before anchor
restoration, only `min(lastScroll,newMax)` is treated as the expected native clamp.
A different current position refreshes the held canonical word/offset first, so
pending deliberate movement is not overwritten. App seeks and generated restoration
update the same local position; temporary hidden panes keep their held anchor until
visible again. No public state/wire or controller changes were needed.

```sh
# cwd: apps/scribeswell/web; authorized local browser socket5182
# Registered red before runtime repair:1 failed
npx playwright test --config playwright.config.cjs tests/four-passage.spec.cjs --project desktop --grep 'pending deliberate movement' --workers 1
# Initial original+new regression green:2 passed in2.1s
npx playwright test --config playwright.config.cjs tests/four-passage.spec.cjs --project desktop --grep 'pending deliberate movement|layout clamps' --workers 1
# Frozen affected-only selection
npx playwright test --config playwright.config.cjs tests/four-passage.spec.cjs tests/reader.spec.cjs tests/lexicon.spec.cjs tests/personal-notes.spec.cjs --grep 'layout clamps|pending deliberate movement|independent same-reference anchors|reduced-height|row qualification|available-container geometry|missing restored anchor|wrapping controls|wrapped word-position|painted ready text|a scrollbar gesture|rapid POP replay|a late gesture completion|focus mode preserves|focus roundtrip|responsive reveal apply|explicitly reopening|four-pane layout retains|four-pane public transitions|comparison preserves independent scroll|comparison isolates a late chapter|Open here follows active|capacity beside replacement|desktop active-pane cue' --workers 1
```

Final affected-only result: **54/54 passed in1.4 minutes**, both projects, including
the original unchanged clamp case, deterministic pending-movement regression,
independent/wrapped source-word anchors, hidden-pane ready seeks, focus roundtrip,
active/inactive gestures, rapid POP invalidation, measured geometry and composing
editor caret/range identity. Exact output is `pending-movement-focused.log`;
`pending-movement-before.sha256` and `pending-movement-after.sha256` match
byte-for-byte. Sources stayed frozen throughout. `git diff --check` passed. No broad
suite, build, native/owner integration or historical-cause claim was added; parent
owns final regression/build.

## Final parent component qualification

All three independent review layers completed before individual triage. Their13
findings plus three parent coupling/race findings yield16 rows:15 surviving rows
addressed across12 actual roots (11 worker repairs plus parent full verification),
with one low-complexity internal final-guard harness finding rejected with its
source-only limit disclosed. No accepted requirement or broader integration gate
was silently deferred by that rejection.

Final exact command from repository root:

```sh
SCRIBESWELL_TEST_PYTHON=/tmp/scribeswell-manual-python/bin/python npm run test:browser --workspace=apps/scribeswell/web -- --workers=2
```

Result: **686 passed / 2 expected native-PostgreSQL browser skips, 13.5 minutes**,
exit0, out of688 registered cases across desktop/mobile viewport projects. All five
`.spec.cjs` suites ran. Actual owner/session `.integration.cjs` and production-release
checks are not matched by this component configuration. `parent-full-run.log`
retains exact output. The160 runtime/test/migration-source inventory in
`parent-full-before.json` and `parent-full-after.json` matches byte-for-byte with
SHA256 `04b1c8998c46e4b2c29738836492c55ebf11e4f8e27d09980418eaa09718847d`;
no source edits occurred during the run or after it. Shared UI/directory runtime
and package lock have no working-tree changes.

`npm run build --workspace=apps/scribeswell/web` passed on these final sources
in1.86s, retaining the existing bundle advisory (`parent-build-clamp-final.log`).
No backend/API/generated contract/migration changed, so no new Python/native check
is claimed. Scoped source/document whitespace checks pass; exact stdout/trace data
is retained without whitespace normalization and indexed in `logs.sha256`.

Earlier evidence remains intact: the intentionally interrupted680 attempt
(302 passes/1 skip/2 interrupted/375 not run,5.3min), complete failed686 attempt
(683 passes/2 skips/1 latest-position failure,13.3min), their matched source inventories,
public exploratory probes, registered reds and all focused corrections. They are
not relabeled passes. The latest-position resize cause is established; the older
initial921→0 occurrence's exact cause remains unproven. Initial helper-red and
wider-precharacterization chronology gaps remain unfulfilled historical requirements;
this report does not claim complete ATDD/TDD ordering or overall feature acceptance.

Native SQL/migrations/permissions/concurrency, actual owner/session integration,
live signup/confirmation activation, physical iOS/Android behavior, default Access
readiness and production release remain final-phase gates. No KDG55481/55482,
owner implementation, migration execution or activation was used for this slice.
Tabs/per-tab associations and durable same-device restoration are subsequent work.
