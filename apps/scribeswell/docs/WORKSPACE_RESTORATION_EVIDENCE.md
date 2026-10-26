# Same-device workspace restoration: component evidence

Current component qualification: **994 passed /2 expected native integration
skips,18.1m**, with a passing TypeScript/production build. All165 owning source,
test and configuration files match before/after/current,
SHAa4002d1be4fae051a4565dc18b5f955464173b7aa5f85209128446a30c47c070.
All three independent reviews and parent patch audit are complete:12 loop1
individual verdicts, four addressed patch roots, one pre-existing adapter defect
deferred. No actual-owner/native-device/session or release qualification is claimed.
Earlier failed/interrupted and prepatch passing runs remain chronological evidence.

Delivery source: [approved implementation spec](../../../_bmad-output/implementation-artifacts/spec-scribeswell-workspace-restoration.md), consuming [WORKSPACE_RESTORATION_V1](WORKSPACE_RESTORATION_V1.md) and [WORKSPACE_TABS_V1](WORKSPACE_TABS_V1.md). The immutable delivery baseline is `95e54f90b37d7b7c0c00c0a4c7ee3acdd29f5a43`. Concurrent owner work, including the KDG checkpoint `d7f942a1c247570e07bb5dd7be4d242566b9e734`, README changes and canonical untracked specifications, is preserved. Parent owns canonical memlog/spec companions and final independent review/regression.

## Implementation and policy

The existing reader controller remains the sole layout, public history, anchor and capacity owner. Each live tab has an opaque incarnation outside URL/history; surviving tabs retain it, while new tabs and closed-key replay receive a new incarnation. Original entry information is captured before checkpoints. Native IndexedDB restoration never pushes history. Fresh explicit links retain their displayed public target, including at the twelve-tab boundary, where remembered setups remain staged until explicit indexed victims make room. Cancel retains the old record. Changed intent or explicit Retry requires a current installation decision and preserves newly created current tabs. The existing departure guard also owns current-tab victims.

`workspace-storage.ts` accepts closed public/private DTOs and validates canonical references, existing anchor/key/label limits, UTF-8 byte budgets, timestamp freshness, versions and cardinality. Projection objects and committed private records are both supported; only the latter receive the bounded storage-only completion ordinal assigned atomically in a read/write transaction. That ordinal ranks account retention independently of tied/backward device clocks. Public and eligible current-account metadata commit together. Anonymous writes preserve other accounts. A window serializes writes and coalesces pending projections for the same account; account transitions retain distinct queued owner writes. Every attempt includes open/transaction in a three-second bound; late timed-out upgrade transactions abort, and late opens close. Reads cap fetched record count. Unknown future records suspend all writes and survive cross-window eligibility checks. Malformed/old/expired current records are rejected and an eligible current projection may replace them; expiry is device-clock best effort.

The provider debounces checkpoints by 250ms with a two-second maximum, skips equal closed projections and flushes lifecycle events best effort. It holds writes during unresolved bootstrap, capacity decisions and existing unmatched-history state. Failures preserve reading, expose concise truthful Retry and never promise unload durability. Private recovery feedback survives unrelated successful public writes.

Identity verification uses the existing Auth transport's configured provider GET, public anon key, fifteen-second bound and caller cancellation. It consumes only a canonical ID and never invokes SDK `getUser(jwt)` or mutates sessions. Captured account/token/session identity and intent bind results. Untouched signup has no selected private projection and therefore triggers no protected Studies request. SDK signin/signup/signout/callback behavior remains owned by Auth.

Studies owns private projection and progressive hydration into the existing single account/note lanes. Pending metadata is separate from empty live fields. At most two protected GETs run concurrently under a thirty-second attempt. Results validate owner and study/note/parent IDs, map identity, tab incarnation, navigation, current input intent and lane freshness. Hydration never calls ordinary openStudy/openNote or changes active tab, tools or focus. Explicit Rename/Reset has its own in-memory generation, so pending metadata preserves resource IDs while respecting newer label choices. Current admission403 uses existing global Studies denial cleanup even after unrelated origin intent changes; outages/401 retain hidden candidates, while current resource404 fans out through existing view/lane registries to every affected association and label. Note404 retains its authorized parent study and independently selected notes; study404 clears that study’s child contexts. Current-token resource denial is independent of changed origin intent, while stale-account/token results remain ignored. Sign-out clears live private state, retaining owner-bound metadata for surviving-tab return under fresh checks; anonymous closure followed by public replay cannot recover the retired private incarnation.

Storage never receives generic view maps, editor buffers or unsent input. Public records contain references/anchors/identities only. Private records contain verified owner/resource IDs and optional labels plus closed version/timestamp/retention metadata. Existing SDK Auth session storage remains separately owned.

## Chronology and retained failures

Logs are retained under [evidence/workspace-restoration](evidence/workspace-restoration/). Commands are recorded in the logs themselves; shell redirections only captured stdout/stderr. No runtime was removed to reconstruct a red.

- The first local browser command could not bind the Vite server in the restricted sandbox. This was an environment failure, not acceptance red. The same command ran with local test-server permission.
- `red.log`: genuine real-IDB reload red before runtime work: two open tabs became one after reload. Nine existing controller tests passed in the same command.
- `runtime-before.sha256`: pre-runtime owning-file hashes. `characterization.log` completed 43 passed / 1 failed with two effective workers (two files; no fully-parallel flag), including note inheritance, guarded departures, closed-origin creation, history capacity and account masking. Relevant passes and the distinct-note failure were observed before runtime edits; storage work began while the remaining characterization cases were finishing, so the entire run is not claimed as frozen baseline qualification.
- The unchanged distinct-note DOM/caret/IME characterization failed waiting for the first tab's exposed editor after switching back. This is an unexplained pre-runtime visibility/context failure, not established caret-value loss. `window-caret.log` later passed that unchanged scenario together with deterministic window/Retry checks on current source; passing isolation does not establish the original cause.
- `codec-red.log`: genuine missing storage-module import failure before its helper existed. The closed-codec and reload checks then passed (`public-green.log`).
- `matrix-first.log`: 16 passed / 2 failed. The capacity chooser invalidated its own pending decision through captured pointer intent; the new note fixture also used an invalid paragraph shape and crashed rendering. Runtime decision handling and fixture schema were corrected; three affected cases passed (`focused-fixes.log`).
- `matrix-second.log`: 25 passed / 2 failed. Successful public writes cleared unresolved private Retry feedback; corrected. The first two-window test assumed a fixed initial count without proving completed startup; replaced with explicit readiness and app-owned transaction assertions.
- `matrix-third.log`: 31 passed / 1 failed. A direct storage-module write bypassed the provider's projection ledger and a subsequent lifecycle flush could become the later transaction. The window fixture now waits for public-ready plus persisted/live identity equality, changes each window through actual tab actions and checks a fresh third window. This passes in `window-caret.log`.
- `focused-both.log`: diagnostic 73 passed / 3 mobile failures. Source changed during this run; it is not frozen qualification. Symptoms were absent initial capacity dialog, one public tab in a503 fixture and absent selector Cancel under quota. A source mutation/HMR is a confounder, not proof of each failure's cause.
- `focused-frozen.log`: 82 passed / 2 mobile failures (affected-only404 and initial active label in the dirty-lane race). Seed arrangement still competed with a live app writer. The fixture now navigates to a same-origin static storage document before arranging real IDB, so no live app writer remains during seed; both formerly failing cases pass in `refinements-green.log`. This retains all original behavior assertions.
- `label-red.log`: genuine held-identity Rename and Reset failures: persisted old label instead of the newer explicit label/absence, while resource IDs remained. `order-red.log`: genuine tied-clock pruning failure (A/B/D instead of B/C/D). `admission-red.log`: genuine current403 failure retaining an already visible editor after newer origin intent. Fixes followed these reds.
- `refinements-green.log`: 12 passed / 2 failed. A literal patch had missed the duplicated old hydration403 branch; corrected precisely. `admission-green.log` then passed both viewports. Label/ordinal and formerly failing seed cases passed in the refinement command.

Several account/controller/hydration safeguards were source-audit-directed before their dedicated assertions. The reload and codec reds preceded the broad runtime change; the label, admission and retention refinements have dedicated pre-fix reds. This is not a claim of isolated pre-change TDD red for every helper or branch.

## Acceptance traceability

| Matrix/contract | Executable component evidence in workspace-restoration.spec.cjs |
| --- | --- |
| Anonymous public return and retained native lifetime | real IndexedDB reload; anonymous names/retained native incarnation refresh |
| Fresh link, twelve cap, Cancel, current intent and explicit victims | fresh explicit target stages twelve; late public read preserves new tabs; account intent invalidates delayed bootstrap; fresh equal-reference target stays public |
| Same verified account / one resource lane / privacy | same verified owner refetches selections; stored public/private forbidden-field assertions; untouched signup remains covered by account-entry suite |
| Account/lifetime/edited-lane races | different account no protected reads; old identity401/new SDK signin; delayed hydration navigation/closed incarnation/account switch; dirty shared lane; surviving owner return; anonymous closed-key replay |
| Authority outage versus denial | helper unavailable/401/different ID; protected503/401/403/404; affected-only404; current admission403 clears previously hydrated live editor |
| Storage denied/quota/blocked/evicted/old/malformed/oversize/future | storage failure variants; current-record variants; eviction; current reading Retry recovery; late timed-out open cannot upgrade |
| Multiple windows and atomic writes | deterministic independent windows/third return; cross-window future guard; coalescing, rollback on private-put failure and retain-three; tied/backward-clock completion ordinal |
| DTO limits and private label intent | maximum accepted twelve-by-four/80-scalar combinations; UTF-8 budgets; finite/future timestamps; closed unknown-field rejection; ordinal bounds; held-identity Rename/Reset |
| Actual references/positions across device reload | real device reload restores four independent pane references/anchors and active pane, switches every phone pane and inactive tab, then repeats after reload |
| No unsent-input recovery or focus changes | unsent body absence plus acknowledged refetch after reload; changed-navigation/account/lifetime focus checks; explicit capacity completion active-tab focus |

## Verification status and limits

`worker-frozen-final.log`: **120 passed (2.6m)** across both component viewports for `workspace-tabs.spec.cjs workspace-restoration.spec.cjs`, before the final resource404 refinement. The complete owning source/test/config manifests in `worker-final-before.json` and `worker-final-after.json` match exactly; `worker-final-source-proof.json` records zero changes. `resource-scope-red.log` then genuinely failed both gated current404 scope cases with the already-exposed editor retained. The owning Studies registry cleanup and closed pending projection were corrected; `resource-scope-green.log` passed all **12 affected desktop/mobile cases (15.0s)**, including current admission403, old-account isolation, affected-only404 and the new note/study fan-out cases. `build-resource-scope.log` passed the owning TypeScript/Vite build with the existing >500kB bundle warning. `worker-handoff-source.json` captures the latest handoff after the resource404, current401 and existing-anchor refinements below; `worker-handoff-delta.json` names the files changed since the120-pass frozen proof. `worker-handoff-delta.log` passed the requested26 denial/outage/dirty-lane/identity/label viewport cases (27.7s) after resource404 cleanup.

Exact final worker commands (repository root):

```sh
SCRIBESWELL_TEST_PYTHON=/tmp/scribeswell-manual-python/bin/python npm run test:browser --workspace=apps/scribeswell/web -- workspace-tabs.spec.cjs workspace-restoration.spec.cjs --workers=4 --fully-parallel
SCRIBESWELL_TEST_PYTHON=/tmp/scribeswell-manual-python/bin/python npm run test:browser --workspace=apps/scribeswell/web -- workspace-restoration.spec.cjs --workers=4 --fully-parallel --grep '404 clears every affected live|authority 404|resource404 clears only|late hydration ignores account switch|current admission403'
SCRIBESWELL_TEST_PYTHON=/tmp/scribeswell-manual-python/bin/python npm run test:browser --workspace=apps/scribeswell/web -- personal-notes.spec.cjs workspace-restoration.spec.cjs --workers=4 --fully-parallel --grep 'same-account reauthentication preserves|library search authentication failure|stale old-token401|note deletion same-account authority|study deletion review explicit reopening|workspace tabs mask all private labels|current hydration401|last public scroll checkpoint|dirty shared note'
npm run build --workspace=apps/scribeswell/web
git diff --check -- apps/scribeswell/web
```

Final current401/anchor boundary: `current401-anchor-existing-red.log` genuinely failed current401 masking (one exposed editor remained), while its first seeded-anchor assertion still accepted original anchorA too early. Tightening the checkpoint assertion to require later verse10 yielded `existing-anchor-distinct-red.log`: completed hidden-pane storage regressed from expected verse10/offset-8 to original verse3/offset0. Snapshot capture now prefers exposed measured DOM, otherwise the latest matching current-entry/key/reference checkpoint, even if the pane already carries an older anchor. No second anchor cache or owner was added.

Restoration-origin current401 now uses existing `fail(authentication_required)` mask/retain authority handling with closed pending-metadata retention, empty private selections/labels during recovery, preserved actual lanes/original commands and explicit Retry/new-session verification eligibility. Same-account pending metadata survives the storage re-read. A fresh accepted GET reattaches an unchanged retained lane; dirty input/unknown attempts remain intact, while clean acknowledged values may refresh without downgrading a newer acknowledgement. Current input arriving during the read still wins. Ordinary Notes401 retains its established view/operation recovery semantics.

`current401-anchor-green.log` passed12 viewport checks (18.9s), followed by `current401-existing-regression.log` with10 passes /2 desktop failures: overbroad clearing had broken ordinary private-label and study-deletion recovery. The extra empty-view preparation was limited to restoration-origin401, preserving the original assertions. On the final patched source, **`owner-recovery-final.log` passed18 cases (19.2s)** across both viewports: existing same-account input, stale-token401, note/study deletion recovery and labels, plus new restoration401 dirty-lane/original-command recovery, changed-input protection and latest-anchor precedence. **`worker-handoff-build.log` passed** TypeScript/Vite (2.11s; existing bundle warning); scoped `git diff --check` passed. The source/test/config inventory has55 files. No whole-browser regression is claimed on this final patched source.

Parent independent reviews and final broad frozen-source browser/build verification remain required. This worker has not run the whole browser suite. `logs.sha256` indexes retained outputs. The first denied server start and first TypeScript `useRef` initialization diagnostics survive in the tool transcript; those original temporary log paths were reused on retry rather than retained as standalone originals. This limitation is explicit; later genuine reds and all substantive failed browser runs remain retained.

Later focused refinements retained their own chronology: `worker-final-focused.log` was109 passed /3 failed (Unicode native/direct-IDB fixture identities and automatic late modal over a newer picker). The Unicode test now arranges its closed native snapshot before the first controller mounts, retaining its original1→2→1 and focus assertions. `tuple-focus-anchor-red.log` genuinely failed a shared-incarnation third-tab association and automatic focus retention; its first anchor check passed against an earlier record and was tightened. `anchor-red.log` then observed a completed post-hide public write lose the checkpoint anchor. The fix reuses the controller’s existing bounded cache with key/reference matching and prefers a compatible native anchor over an older device anchor. `tuple-focus-anchor-green.log` passed10 /failed2 because the picker is a div with role=dialog and its focus assertion searched only native dialog; the DOM adapter was corrected. `public-fidelity.log` then passed all8 viewport cases, including actual four-pane/inactive-tab DOM positions across reload. The subsequent120-pass frozen run includes these corrections. The success-marker binding is the complete unambiguous account/tabKey/incarnation tuple; duplicate incarnations across distinct accepted tab keys remain independently verified.

No migrations, native SQL, actual Auth/Identity/Access or owner-service integration, live signup, KDG55481/55482, physical-device/native-session validation, deployment, provider configuration or release activation was performed. Those final integration gates remain open. Browser viewport tests and intercepted synthetic HTTP do not establish those properties. Existing application ownership is retained: no scaffold/shared-UI promotion, new agent rule or ADR amendment is introduced.


## Parent implementation and matrix audit

Parent read the scoped unified diff, checked all41 original stdout log hashes and
verified the55-file worker handoff against current source. Every frozen matrix row
has an executed passing case; the120-pass source and later patched subsets remain
separate claims. Parent's current-source16-case command covers four-pane DOM
positions/active pane/inactive tabs, fresh-link12-cap, late selector focus, anonymous
closed-key replay, owner-response refusal, denied storage and independent windows/
future-version preservation. **16 passed21.3s**, unchanged165-file app inventory:
`3ed7bb8d387f3276270dbec2214f33fed2b15b5179c641863dfc8be8356496d0`.
See `parent-matrix-audit/parent-matrix-run.log` and `source-proof.json` for exact
command/results. This does not replace final broad verification or independent
review. Normal Git index/README/frozen intent and concurrent KDG work are preserved.

## Independent review and correction loop 1

All three same-capability context-free reviews completed before parent triage.
The blind child ran first; the child thread limit then prevented the other two
launches. Parent ran edge and verification concurrently as fresh ephemeral
read-only Codex CLI sessions (gpt-6.1-sol, medium). They consumed the identical
544255-byte diff SHA b54939b2d8112183c4699b45b1079ad87ba1d41586ced7dfa35b2d9cc310b9d4.
The schedule was not three simultaneous children. Reports/provenance are under
loop0-review; the delivery spec records17 individual verdict rows before grouping.

Confirmed completion defects include staged-victim last-context protection,
destructive intermediate departure before Cancel, delayed old-resource denial
affecting a newer selection, Retry after eviction retaining an obsolete projection
ledger, unbounded alternating-owner queueing and null requested-resource acceptance.
Focused verification gaps cover first-time selection persistence, note identity
validation, current dirty victims, hydration deadline, lifecycle flush and native
IDB contention/async abort. Existing <=2 concurrency assertion refutes that blind
claim. Byte/cardinality closed bounds and the lack of a named independent developer
harm refute the requested unreachable budget fixture and general formatting claims.

These require a BMAD bad_spec correction loop, not component completion. Frozen
intent is unchanged (SHA366fc71fc1c416595d1e0fc7fb73a16b7b05713803949ff1859c6afa77e9cf5b).
Parent preserved the full known-incomplete runtime/test reference in
/tmp/scribeswell-restoration-loop0-source, then reverted only the10 restoration-owned
runtime/test paths to the approved95e54 baseline. All prior evidence and unrelated
working-tree changes remain. The amended non-frozen spec records positive KEEP
requirements and concrete bad states. A fresh implementation child is re-deriving
the slice with dedicated regression reds under loop1. No final broad regression,
checkpoint or actual-owner integration is claimed.

## Review loop 1 correction evidence (2026-10-26)

Loop 0 source is retained as a known-incomplete reference. Loop 1 restored its
positive behavior onto the reverted baseline, retained every original assertion,
and added the review counterexamples in `workspace-restoration.spec.cjs`. New
logs live in [evidence/workspace-restoration-loop1](evidence/workspace-restoration-loop1/).
No loop 0 output was overwritten. Parent still owns final review, the canonical
handoff, and whole-browser frozen-source qualification.

The controller stages every victim without invoking departure. Once the final
union fits, Studies captures removed contexts and final survivors, visits each
last-context resource lane once through its existing bounded exit owner, and
stages consent without abandoning any lane. Final installation rechecks context,
account, input and lifecycle freshness, then abandons only approved unresolved
last-context input. Stay/Cancel preserve live tabs, buffers and original attempts.
Unknown save attempts remain available for explicit recovery after installation.
No second modal or editor/guard owner was added.

Requested study and note responses must be non-null and match the expected
resource, parent and owner before attaching selections or labels. Resource denial
clears matching live fields independently from old pending metadata: delayed A404
cannot clear a newer live B selection or label. Successful Retry reads invalidate
the provider's successful-projection ledger, so eviction can repopulate an
unchanged live projection.

Storage admission now retains one executing batch, at most eight pending owner
batches and at most 64 waiters per pending coalesced batch. Full admission rejects
excess work through the existing unavailable failure. Accepted distinct owner
batches are never silently removed; same-owner success acknowledges the latest
coalesced batch projection, rather than claiming each intermediate projection
committed. Tests hold an actual read/write transaction and verify exactly nine
accepted strictly alternating writes or 65 same-owner writes, with all excess
calls rejected and the first accepted owner write completed.

Chronology and exact commands are retained in numbered logs (each command header
includes its npm/Playwright arguments; the Python override is
`SCRIBESWELL_TEST_PYTHON=/tmp/scribeswell-manual-python/bin/python`):

- `01-baseline-red.log`: sandbox prevented local loopback startup; no behavior
  claim. `02-baseline-red.log`: genuine pre-runtime real-IDB reload failure, two
  open public setups became one.
- `03-review-defects-red.log`: four genuine failures / three passes, 47.2s.
  Null requested study/note exposed a label; unchanged eviction Retry failed;
  alternating owners accepted all 200 writes. Wrong note ID/parent/owner passed.
- `04-basic-defects-green.log`: despite its filename, six passed / one failed,
  8.9s. The tightened queue assertion exposed 72 accepted alternating calls
  because calls matching a full queue's tail could still coalesce. Admission was
  fenced at eight queued batches; no failure is renamed as a pass.
- `05-denial-and-first-selection-red.log`: three fixture failures, not three
  behavior reds: normal Studies listing uses POST search and the first fixture
  rejected it. After correcting that interception, `07-denial-fixture-red.log`
  genuinely failed both old-A/new-B label assertions. The first selection case
  wrote the expected private IDs, then its immediate Analysis click correctly
  superseded unfinished automatic restoration. It now waits for the restored
  hidden lane before explicitly exposing Analysis; it never reselects a resource.
- `06-departure-red.log`: the sole dirty intermediate victim genuinely prompted
  before the union fit. The two shared-victim failures were not valid E1 reds:
  New tab inserts adjacent to active, while the fixture incorrectly assumed it
  was last, retaining a live note holder among final survivors. The helper now
  captures the new public tab identity and chooses actual eligible live victims.
- `08-build.log`: owning TypeScript/Vite build passed, with the existing bundle
  size warning. `09-review-defects-focused.log`: 11 passed / three failed, 41.8s;
  the remaining fixture errors were the new-tab ordering above and a redundant
  Analysis toggle that hid an already-open editor. Text assertions were retained.
- `10-loop1-focused.log`: all 19 focused desktop cases passed, 36.3s, including
  corrected shared dirty Stay/discard, exact queue bounds, first UI selection to
  actual IDB IDs to automatic reload, stale denial identity, null/mismatched
  responses, lifecycle pagehide flush and unresolved-decision suppression.
  It also executes the 30-second overall hydration deadline with requests released
  at 14s and 28s (below each 15s request limit), cancels the remaining hidden
  candidates, rejects their late responses and restores them through explicit
  Retry. Real blocked upgrade contention exercises the three-second queued-open
  deadline and recovery. A successful IDB put event aborts an actual transaction,
  proving atomic public/private rollback and a subsequent successful retry.

The shared-final-survivor guard, 64-waiter bound and additional lifecycle/deadline
cases are audit-directed safeguards with passing executable coverage; no isolated
pre-fix red is claimed for them. Earlier unexplained loop 0 caret visibility and
all other original failures remain disclosed above. Component HTTP interception
is the only authority exercised here; actual Auth/Identity/Access owner services,
native sessions/devices, migrations, deployment and release remain open.

Scaffold/shared UI remain application-owned. Agent context and ADRs are unchanged.
Documentation impact is this evidence and the adopted contract status; canonical
specifications and handoff remain parent-owned.

Subsequent loop 1 verification (same command override as above):

- `11-restoration-suite.log`: affected suite, desktop/mobile,
  `--workers=4 --fully-parallel workspace-restoration.spec.cjs`: **149 passed /
  one failed, 3.7m**. The failure was the mobile shared-Stay helper waiting for its
  induced storage-failure feedback before reaching the restoration chooser. The
  helper had proved stored tab keys but not the latest active-key projection;
  a successful-projection timing race was a plausible fixture cause, not an
  established runtime root cause. It now explicitly waits for the captured new
  public active tab key to be durable before injecting the future record. Both
  source manifests (`11-source-during.json`, `11-source-after.json`) match, with
  zero changes among the 55 captured frontend runtime/test/config files.
- The positive lifecycle test now runs both `pagehide` and `visibilitychange`.
  The alternating-owner test additionally verifies nine actual read/write
  transactions completed, rather than only nine fulfilled calls. Ordinary Stay
  invokes device cancellation only when a device decision exists, preserving
  ordinary departure focus behavior.
- `12-loop1-both-viewports.log`: focused `-g loop1` with four fully parallel
  workers, **43 passed / one failed, 1.3m**. The mobile deadline case failed its
  first expected private label after the 14s jump. With an auto-progressing clock,
  real runner delay plus the 14s jump may cross the per-request 15s deadline.
  The fixture now pauses the installed clock before application startup; it retains
  every expected label, the 14s/28s/30.1s sequence and cancellation/Retry checks.
- `13-final-build.log`: `npm run build --workspace=apps/scribeswell/web` passed,
  Vite 19.78s, with the existing >500kB bundle warning. Runtime has not changed
  since that build; subsequent changes only make the deadline fixture deterministic.
- `14-deadline-paused-clock.log`: both unchanged deadline behavior assertions pass
  under the paused clock, **two passed, 9.3s**.

No failed intermediate run above is presented as whole-source qualification.
The parent still must run the complete browser suite on the final source, including
its unchanged original caret/IME case, and independently review the complete diff.

`15-loop1-final-focused.log` is the final focused handoff run:
`SCRIBESWELL_TEST_PYTHON=/tmp/scribeswell-manual-python/bin/python npm run test:browser --workspace=apps/scribeswell/web -- --workers=4 --fully-parallel workspace-restoration.spec.cjs -g 'loop1'`
passed **44 desktop/mobile cases, 1.4m**. It includes every loop1 regression and
both positive lifecycle events, with the corrected active-key synchronization and
paused overall-deadline fixture. `15-source-before.json` and
`15-source-after.json` cover 55 frontend runtime/test/config files;
`15-source-proof.json` records zero source changes during this run. The manifest
SHA-256 is `7ccd2e6c2dab3a505ad795b165ad39d7435f40a2735aeb999e598fd1de1d3fed`.

The final build remains `13-final-build.log`; no runtime changed afterward.
`git diff --check -- apps/scribeswell/web apps/scribeswell/docs/WORKSPACE_RESTORATION_EVIDENCE.md apps/scribeswell/docs/WORKSPACE_RESTORATION_V1.md`
passed. Full unchanged-case browser regression, independent review and all actual
owner/native/release gates remain parent-owned and open.

## Parent resumed regression environment

The user continuation resumed in an environment with cleared `/tmp`. Repository
source/evidence, the55-file handoff hashes, frozen intent and preserved README
remain intact. Earlier temporary reference/diff/runner paths are no longer locally
available; their historical paths are not current deliverables. Raw reviewer
reports and source hashes remain repository-backed. The interrupted
`parent-loop1-final` attempt contains a before-manifest and empty run log, not a
completed test run. The missing temporary runner invocation was an environment
startup failure, not test evidence. Parent recreated its runner and independently
validated current source against every55-file handoff hash. System `/usr/bin/python3`
successfully imports the two browser tests' `passage_references` dependency; it
replaces the cleared temporary Python environment without a dependency/code change.
The complete browser run is recorded separately in `parent-loop1-regression-01`;
its before/after inventory covers the full owning app, not only the frontend.
No passing full regression is inferred while that run is in progress.

Parent broad attempt01 was stopped with normal Playwright SIGINT after repeated
demonstrated legacy reload-flow failures: **311 passed /11 failed /4 interrupted /
1 skipped /609 did not run,7.4m**, exit130. Before/after full165-file inventories
match exactly, SHA673a1af4e9a0e8300410bf4b15b24410c9959dfd8f9902bca63e799a0beeb720.
This is partial regression evidence, not complete qualification. Failed snapshots
show the requested library row disappearing after automatic private hydration has
already selected that study; note content remains in the restored outline. The
sole-runner child tree was identified and only its Playwright CLI received SIGINT;
its ordinary shutdown closed the owning test server. An initial process-name match
found no target and sent no signal. Four in-progress tests, including the original
distinct-note caret/IME case, remain unverified by this attempt.

The same implementation agent is correcting the stale reload consumer flow using
actual checkpoint/authorized restoration readiness. Original saved-content, rich
formatting, links, composition and command-count assertions must remain; no storage
suppression, assertion weakening or production change is inferred. A new focused
run and later complete frozen regression are required.

The legacy reload correction is retained in
`evidence/workspace-restoration-loop1-reload-correction/`: final30 passes /2 existing
native-gate skips with all prior assertions and actual reloads retained. Parent
read the entire test delta; only readiness/navigation changed, no runtime change.

Broad attempt02 was stopped normally for a source-audit gap in restored-panel
consumption: **117 passed /1 failed /4 interrupted /1 skipped /813 did not run,
2.1m**, exit130. Its full165-file before/after inventory is unchanged,
SHA3599e50f453defdfb2c277e6fcf768542abdbaa86ed030bcc298a75f2a80972f.
The one failure is a fixture identity callback calling page.evaluate after test
teardown in rejected-title correction. That lifecycle issue remains open; errors
are not suppressed. Separately, opening restored Studies does not load its full
note page/cursor or collected passages, leaving passage actions disabled. Existing
Leave/reopen fixtures do not qualify the default restored-panel path. The same
worker must observe dedicated acceptance red and repair existing-owner bounded
readonly consumption while preserving selected/dirty lanes and freshness. Neither
partial broad attempt establishes full qualification.

Parent failure DOM snapshots from attempts01/02 are retained byte-for-byte in
`failure-snapshots.zip` beside each run log. Parent verified every archived byte
against the originals before removing redundant plain copies; the adjacent manifest
records each original SHA-256 and archive SHA-256. These are synthetic fixture
snapshots, not live account data. Compression changes no failure evidence.

## Parent full component regression before subsequent review corrections

`parent-loop1-regression-03/parent-full-run.log`: exact owning command
`SCRIBESWELL_TEST_PYTHON=/usr/bin/python3 npm run test:browser --workspace=apps/scribeswell/web -- --workers=4 --fully-parallel`
completed984 registered cases, **982 passed /2 expected native browser integration
skips,16.2m**, exit0. All165 owning application source/test/config files match
before/after/current at SHA8c320388b65c3b7e4543769aac06e56abda2887eee4bf1278882f889ec877df7.
The original distinct-note DOM/caret/IME case passed in both projects unchanged;
its initial pre-runtime failure remains unexplained, not erased. Parent production
build passed (`parent-build-final.log`,2.28s), retaining the existing chunk warning.
The Next-chapter lifetime-recovery case uses a wide viewport even under its mobile
project label; other narrow Chromium coverage is not native iOS/Android proof.
All actual Auth/Identity/Access, native PostgreSQL, physical-device/session and
release checks remain deferred. This result qualifies that prior source snapshot. Subsequent provider review
corrections require fresh whole-browser verification; independent review and final
integration remain open. README and concurrent KDG
commit43e03e35c9c129eb2e472f677648e18a64f3b892 remain preserved.


## Post-qualification provider review correction

New evidence is retained in
[evidence/workspace-restoration-loop1-provider-review](evidence/workspace-restoration-loop1-provider-review/).
No prior log or parent delivery/canonical companion was changed.

A held actual provider transaction failed, then an already accepted newer queued
projection committed successfully and cleared the notice while leaving persistence
suppressed. A third real user change remained absent from IDB. The pre-fix newer
account-read failure variant also proved that the older queued success erased its
warning. Both genuine failures are retained in `01-provider-red.log`.

Storage attempts now carry a per-provider monotonic order. Only a successful write
at or after the latest failed operation releases suppression and clears the public
storage warning. A newer read/write failure keeps its warning and Retry; successful
public writes preserve unrelated private recovery feedback. The serialized storage
queue, closed projections, authority and explicit Retry policies remain unchanged.

The paused-clock maximum-wait case performs actual eligible changes every150ms,
asserts the previous durable projection at1999ms and the current projection at2000ms,
without pagehide or visibilitychange. The POP cases exercise both stale accept and
victim while the remembered-set dialog remains open, prove the POP target survives,
then Cancel and current Retry successfully install alongside that current target.
No controller runtime change was needed. Full verification remains parent-owned.

## Final post-review component qualification

`parent-loop1-regression-04/parent-full-run.log` records the exact command
`SCRIBESWELL_TEST_PYTHON=/usr/bin/python3 npm run test:browser --workspace=apps/scribeswell/web -- --workers=4 --fully-parallel`:
996 registered,994 passed,2 expected native integration skips,18.1m,exit0.
Before/after/current165-file manifests match at
SHAa4002d1be4fae051a4565dc18b5f955464173b7aa5f85209128446a30c47c070.
Parent owning build passes2.25s (`parent-build-post-review.log`), with the existing
bundle warning. Exact review input is retained as loop1-review/input.patch.gz,
verified byte-for-byte after decompression; provenance records its digest.
Parent audited all runtime/test patch changes; all12 individual review rows are
resolved as four addressed patch roots, one pre-existing malformed-note response
validation defer and seven rejected findings. Loop0's17 rows and correction-loop
history remain separately recorded. Frozen intent, README and unrelated work stay
preserved. This closes the bounded component delivery only; final native SQL,
actual Auth/Identity/Access, signup, device/session and release gates remain open.
KDG ports55481/55482 were not used by this delivery's browser verification.
