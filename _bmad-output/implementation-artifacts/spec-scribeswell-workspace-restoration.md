---
title: 'Remember the reading workspace on the same device'
type: 'feature'
created: '2026-10-26'
status: 'done'
route: 'dispatch'
review_loop_iteration: 1
baseline_commit: '95e54f90b37d7b7c0c00c0a4c7ee3acdd29f5a43'
context:
  - '{project-root}/apps/scribeswell/docs/WORKSPACE_RESTORATION_V1.md'
  - '{project-root}/apps/scribeswell/docs/WORKSPACE_TABS_V1.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Open reading setups and selected personal study/note contexts currently
disappear on refresh or a later visit. CAP-11/ST-35 requires a same-device return
without persisting private content or treating remembered identity as permission.

**Approach:** Persist bounded, separate public layout and verified-account metadata
using native IndexedDB. Restore public reading independently; verify the same
account and current API authority before attaching remembered private selections to
existing resource lanes. Apply the adopted WORKSPACE_RESTORATION_V1 contract.

## Boundaries & Constraints

**Always:** Keep one controller/history/anchor owner and one account/note lane.
Preserve pending metadata during Auth/outages; bind account, incarnation and current
intent before attaching results. Explicit links and newer input win. Preserve dirty
and concurrent work, including README and canonical untracked specs. Record actual
ATDD/TDD chronology and exact verification evidence.

**Never:** Store bodies/snippets/titles/highlights/selection/credentials/commands;
restore unsent input; auto-enroll or create records; infer permission from identity;
silently evict tabs; introduce a competing Access/Auth account implementation.
No migrations/native SQL/actual-owner integration/KDG ports until final phase.
No Leave/factory, sharing, provider configuration, deployment or release activation.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected behavior | Failure handling |
|---|---|---|---|
| Public return | Anonymous, saved layouts | Restore refs/anchors | Reading starts immediately |
| Explicit link | Fresh target plus12 saved tabs | Public target wins; explicit victims | Cancel retains record; Retry respects newer intent |
| Personal return | Same verified account | Current-authorized refetch into single lanes | Hide pending candidates |
| Account/lifetime race | Switched account or retired incarnation | No leak/resurrection/overwrite | Ignore stale completions |
| Authority failure | Outage/401 versus403/404 | Retain hidden versus clear affected context | Public layouts survive |
| Storage failure | Denied/quota/blocked/old/malformed | Safe reading and truthful Retry | Unknown versions untouched |
| Multiple windows | Competing transactions | Last completion wins future load | No live merging |

</frozen-after-approval>

## Code Map

Under `apps/scribeswell/web/src/`:

- `hooks/useReaderWorkspace.ts`: snapshots/anchors/history/capacity; no initial checkpoint effect.
- `context/ReaderWorkspaceContext.tsx`: fields-map freshness and tab lifetime.
- `context/StudiesContext.tsx`: lanes/epochs/masking; hydrate without ordinary openNote/openStudy.
- `lib/supabase.ts`, `context/AuthContext.tsx`: bounded transport/session ownership; SDK getUser(jwt) has stale rejection effects.
- `lib/personal-notes.ts`, `lib/reader-layout.ts`: protected GETs and closed public codec.
- `../tests/*.spec.cjs`: intercepted harness; integration files excluded.

## Tasks & Acceptance

**Execution:**
- [x] `apps/scribeswell/web/tests/workspace-restoration.spec.cjs` — characterize risky
  paths and observe real IDB reload red before runtime; cover every matrix row,
  privacy and races using intercepted Auth/business HTTP.
- [x] `apps/scribeswell/web/src/lib/workspace-storage.ts` — TDD closed DTOs,
  bounds/expiry/versions, atomic serialized writes and failure/retry policy.
- [x] `apps/scribeswell/web/src/hooks/useReaderWorkspace.ts` and context provider —
  checkpoint notifications, incarnations, guarded bootstrap and capacity actions.
- [x] `apps/scribeswell/web/src/lib/supabase.ts` and Auth context — nonmutating
  identity verification; prove stale401 isolation and unchanged signup behavior.
- [x] `apps/scribeswell/web/src/context/StudiesContext.tsx` — safe private projection
  and bounded hydration into single lanes, pending preservation and denial cleanup.
- [x] `apps/scribeswell/web/src/components/bible/WorkspaceTabs.tsx` and owning shell —
  explicit restoration choices/Retry with keyboard and focus protection.
- [x] `apps/scribeswell/docs/WORKSPACE_RESTORATION_EVIDENCE.md` — exact commands,
  source hashes, acceptance traceability, reviews and limits; update contract status.
  Parent alone writes canonical memlog/spec companions.

**Acceptance Criteria:**
- Given multiple distinct setups, when returning anonymously or as their verified
  owner, then public layouts and eligible selections restore under the matrix and
  contract, with no private fields in public records/history/URLs.
- Given pending edits, changed tabs/accounts or delayed verification, when an old
  result completes, then it cannot replace current work, activate/focus a view or
  resurrect a retired private tab incarnation.
- Given component qualification, when reporting completion, then actual-owner,
  native-phone/session and release gates remain explicitly open for final integration.

## Implementation Notes

- Loop1 current source is parent-qualified:984 registered browser cases,982pass/
  2expected native integration skips16.2m, production build2.28s and whitespace
  checks pass. Full165-file before/after/current match
  SHA8c320388b65c3b7e4543769aac06e56abda2887eee4bf1278882f889ec877df7.
  Loop1 review follows; native/owner/device/session/release stays deferred.
  Earlier notes below describe their historical source and pending state.

- Parent audited the complete scoped unified diff and41 indexed log outputs. The
  shared index stays untouched; step03 staging used a temporary index. Baseline
  remains95e54f90b37d7b7c0c00c0a4c7ee3acdd29f5a43; concurrent KDG commits are excluded.
- All seven matrix rows have executed passing coverage: intermediate frozen120
  cases; later resource-scope12, affected26 and final owner-recovery18 cases, with
  exact source changes disclosed in app evidence. Parent independently reran16
  current public/link/lifetime/storage/window cases: all passed21.3s on unchanged
  165-file inventory SHA3ed7bb8d387f3276270dbec2214f33fed2b15b5179c641863dfc8be8356496d0.
- Direct reload/label/denial/retention/tuple/focus/anchor reds and failed intermediate
  runs are retained. A module-import failure is not codec-behavior red. Several
  safeguards were audit-directed rather than individually test-first; the mixed
  characterization run and unexplained original caret visibility failure remain
  explicit limits. No whole-browser final-source qualification is claimed yet.
- Scaffold/shared UI remain app-owned; agent context/ADRs unchanged. Auth ownership
  stays with existing SDK and transport; business HTTP/Access contracts unchanged.
  Canonical handoff and all actual-owner/native/session/device/release gates remain
  parent-owned and deferred. Independent review/full regression follows this audit.

## Spec Change Log

### Review loop 1: restoration completion and departure transaction

The 17 individual loop0 findings above were recorded before grouping. E1/E2/V2
share staged-departure handling; B1/E4 share denial targeting. The remaining
confirmed findings are separate. They route to bad_spec because completion,
queue bounds and final-survivor coordination need explicit non-frozen detail.
No frozen intent changes. Reviewers: fresh same-capability blind child, then two
fresh read-only Codex CLI reviewers after child capacity was exhausted; all three
reported before triage. No claim that all three launched simultaneously.

Amendments and known-bad states to avoid:
- Stage victim identities without running destructive departure handling. When the
  union fits, protect all removed live contexts against the final survivor set,
  once per affected lane, through the existing Studies exit owner. Stay or Cancel
  before installation preserves all live input, attempts and tabs. An intermediate
  victim choice must never discard input. Confirmed final install may discard
  only explicitly approved last-context input; preserve original unknown attempts.
  Recheck freshness/identity/input before final installation. Do not create another
  modal, editor lane or guard owner. Cover shared dirty lane across multiple
  current victims, sole dirty current victim, Stay, explicit discard and Cancel
  after an intermediate victim. Existing single-close/history/account guards stay.
- Resource denial updates old pending metadata separately. Clear live selections
  and labels only when current resource identity actually matches; newer B survives
  delayed A404. Test both study and note identity cases under delayed responses.
- A fresh successful Retry read invalidates/reconciles the successful-write ledger;
  eviction followed by Retry must repopulate an unchanged live layout without reload.
- Bound queued per-window write projections and waiter retention even across rapid
  alternating owner transitions. Fail excess work truthfully without dropping an
  accepted owner batch or losing atomicity. Preserve existing same-owner coalescing:
  batch success acknowledges its latest coalesced projection, never every intermediate
  projection. Bound admission to8 pending batches and64 waiters per batch in addition
  to one executing batch; reject excess through the existing unavailable failure.
  Keep coalescing and last-completed-transaction semantics; test delayed
  transactions and alternating accounts. No platform framework or new public API.
- Requested study/note responses must be non-null and match expected IDs/owner/
  parent before attaching any private label or selection. Add null payload and
  mismatched note ID/parent/owner cases after an accepted study response.
- Execute first-time acknowledged UI selection -> actual private IDB IDs -> reload
  automatic restoration, without manual reselection or initial private seed.
- Execute held 30-second overall hydration deadline, unfinished hidden candidates,
  cancellation, Retry and late-response rejection. Execute lifecycle flush of the
  latest eligible projection and suppression while decisions remain unresolved.
  Exercise actual IndexedDB upgrade contention and asynchronous abort recovery,
  not solely synthetic open events/synchronous put throws. Existing byte/cardinality
  maximum tests remain; do not invent unreachable above-budget valid DTOs.
- Returning to an authorized selected study must leave its ordinary Studies panel
  usable: opening it exposes the current complete first note page/cursor and
  collected passages with normal passage actions, without Leave/reselect. Keep
  the restored selected note and existing dirty lane. Add genuine return-path red
  before fixing missing outline loading; late account/tab/resource changes must
  not attach stale lists. Reuse the existing Studies HTTP and collection owners;
  automatic hydration must not invoke ordinary openStudy/openNote navigation.
  Keep the existing hydration2-request/30s and owner-read timeout boundaries.
  Retain legacy reload content/format/count assertions plus actual metadata and
  authorized-restoration readiness. Explicit Leave/reopen fixtures cannot serve
  as evidence for the default restored-panel behavior.
- Final parent runs full frozen-source browser suite/build. Retain all original
  failures and chronology, including unexplained pre-runtime caret visibility;
  repeat that unchanged case without changing expected values to hide failure.

KEEP: All proven public layout/history/anchor/incarnation/privacy, dirty single-lane,
identity nonmutation/current401, denial scope, labels, ordinal retention, two-window,
fresh-link/capacity/focus and source-boundary behavior in loop0 remain requirements.
The entire pre-loop implementation/tests are preserved at
`/tmp/scribeswell-restoration-loop0-source` as a known-incomplete reference for
positive preservation, not accepted truth. Re-derive from the reverted baseline,
using that reference to preserve working behavior while correcting these defects.
Retain every original test assertion and archived log; add genuine failing cases
for confirmed defects before fixing them. Do not overwrite loop0 evidence outputs.
Use a new evidence loop1 directory. The parent broad run remains deferred until
implementation returns. Component HTTP interception only; final integration remains
open. No changes outside the owning app runtime/tests/docs/evidence; parent owns
canonical specs, this delivery spec and concurrent files.


## Review Triage Log

| Finding | Verdict | Evidence | Route |
|---|---|---|---|
| B1 | medium | Old pending A matches even after live selection B: clearResourceContexts uses affected||pending for live fields/label, independently of freshness. | bad_spec |
| B2 | medium | Retry reopens an evicted store but never resets last.current; the equal live projection skips repopulation. | bad_spec |
| B3 | medium | Only adjacent same-account tails coalesce; repeated alternating owners append unlimited distinct projections and waiters while transactions wait. | bad_spec |
| B4 | false | same verified owner refetches test already executes expect(calls.max()).toBeLessThanOrEqual(2), with two restoration workers. | reject |
| B5 | medium | No held overall-deadline test exists; 30-second cancellation and late-result rejection currently rely on source guards. | bad_spec |
| B6 | medium | No executable visibilitychange/pagehide fixture covers eligible flush or unresolved decision suppression. | bad_spec |
| B7 | false | The oversize fixture is not isolated, but a conservative closed-shape envelope is84770 public/24026 private UTF-8 bytes, below98304/32768 budgets (loop0-review/byte-budget-refutation.json). Otherwise-valid immediately-above DTOs are unreachable with current bounds; retain maximum accepted combinations. | reject |
| B8 | medium | Blocked open is a synthetic onblocked event and rollback uses a synchronous put throw; actual blocked-upgrade and asynchronous abort recovery remain untested. | bad_spec |
| B9 | false | Density alone names no caller divergence or broken invariant; the actual missing guards are individually captured in B1/E4 and E1/E2. A broad formatting rewrite is not independently justified. | reject |
| B10 | medium | Final frozen full-browser verification is pending as disclosed. Pre-runtime caret failure must remain disclosed and its unchanged case run in the final regression; do not claim an unproved root cause. | bad_spec |
| E1 | high | Each staged victim calls exit while all other staged live contexts still exist; contexts() sees another note holder even though final union removes all, bypassing last-context protection. | bad_spec |
| E2 | high | exit/proceed can discard a sole dirty lane for an intermediate victim while union remains above12; Cancel then retains that live tab with discarded input. | bad_spec |
| E3 | medium | Null selected/note bypass truthy response checks; label-only fallback can mark requested missing resources hydrated and expose a label. | bad_spec |
| E4 | medium | Same verified old-A/new-B denial race as B1; pending metadata cannot authorize clearing unrelated current B. | bad_spec |
| V1 | medium | Pre-verified regression gap: seeded restoration cases do not establish first-time UI selection to IDB to automatic reload. | bad_spec |
| V2 | high | Pre-verified regression gap: device current-victim dirty Stay/discard path is not exercised by remembered-victim or ordinary-close tests. | bad_spec |
| V3 | medium | Pre-verified regression gap: foreign-study response stops before note validation; mismatched note ID/parent/owner rejection lacks executable coverage. | bad_spec |

## Design Notes

No intent gaps remain; technical choices are delegated. No migrations, external
communications or activation. App-specific storage/controller/Auth/Studies/UI only.
Scaffold/shared-UI: retain app ownership. Agent context: no new rule. ADRs: unchanged.
Exact storage/identity/hydration bounds and policy live in the adopted contract.

## Verification

- `SCRIBESWELL_TEST_PYTHON=/tmp/scribeswell-manual-python/bin/python npm run test:browser --workspace=apps/scribeswell/web -- --workers=4 --fully-parallel` — focused red/green, then full suite; disclose native-browser skips.
- `npm run build --workspace=apps/scribeswell/web` — owning TypeScript/Vite build passes.
- Capture source hashes and all failure logs; disclose chronology and deferred integration.

### Loop1 independent review — individual verdicts before grouping

| Finding | Verdict | Evidence / route |
| --- | --- | --- |
| L1-B1 identity failure after prior hydration | false | Same-account token rotation preserves already-authorized live lanes under the existing Studies authority owner; Identity verification gates new device hydration and persistence, not established live permission. No new candidate can hydrate while verifiedAccount is absent; account changes mask through dataAccount/authority. Current protected401/403 still masks/clears. |
| L1-B2 queued writes exceed3s | false | Adopted contract bounds each open/read/write attempt; queued admission is separately bounded to8 batches. Timer begins when an executing transaction opens, as specified, rather than claiming an end-to-end queue deadline. |
| L1-B3 coalesce before full-queue refusal | false | Carried delegated decision386 explicitly fences admission at8 pending batches, including matching-tail calls, and preserves already accepted calls. Exact alternating9 accepted transactions and65 same-owner calls are tested. Proposed change contradicts adopted overload behavior. |
| L1-B4 retention uses stored clock | false | Completion ordinal intentionally survives tied/backward clocks; read eligibility rejects future timestamps independently. Retention structurally validates records at their recorded clock to preserve actual completion ordering. Existing backward-clock test exercises this distinction. No permission follows retention. |
| L1-B5 large preexisting IDB clone | low | IDB necessarily clones a value before userland DTO validation; count limit5 and transaction timeout are present. A custom persistence transport to avoid native cloning adds complexity for externally corrupted storage and is rejected. Existing oversized persisted-value fixture proves recovery; no claim of pre-clone byte enforcement. |
| L1-B6 hydrated identity-failure regression | false | Same requirement proposed as B1: masking established same-account live authority on an Identity outage would change existing ownership semantics, rather than prove device-candidate safety. Existing hidden-candidate cases prove the gate this slice introduces. |
| L1-B7 history during restoration dialog | medium | Existing POP increments deviceIntent and install checks it; explicit stale-dialog completion/cancel recovery lacks direct coverage. Patch adds browser POP regression preserving the current target and usable Cancel/Retry. |
| L1-B8 queued failure/success recovery | medium | Provider success clears failure notice but does not clear failed.current set by an earlier serialized failed write; an already accepted newer success can hide continuing suppression. Patch requires actual provider regression with queued failure then success and third changed projection, plus smallest confirmed correction. |
| L1-B9 compressed helper extraction | false | Carried B9: density alone identifies no independent caller divergence or broken invariant. Named ownership/cancellation checks are directly exercised; broad refactoring would create risk without demonstrated harm. |
| L1-B10 adopted contract status | low | Opening status lags completed982-pass component gate. Direct documentation correction; reviews/integration remain distinct. |
| L1-E1 malformed note document outline crash | medium | New outline consumes existing api.notes transport, which casts JSON without content validation; ordinary openStudy/moreNotes already feed the identical StudiesPanel preview and have this pre-existing malformed-response exposure. Defer shared response-validation correction with concrete caller evidence; do not duplicate a restoration-only note schema. |
| L1-V1 continuous checkpoints maximum wait | medium | Trusted verification-gap evidence: settled scroll and lifecycle tests cannot detect removing max timer. Patch adds paused-clock repeated eligible changes below250ms and durable latest projection at2s without lifecycle flush. |

Grouping: B7, B8, B10 and V1 are four independent patch roots. E1 is a pre-existing shared adapter validation defect and routes to defer. Other rows are rejected on their individual evidence. No frozen intent or non-frozen design amendment is needed for the direct scheduler correction/test coverage.

### Loop1 patch audit and verification handoff

All four patch roots were addressed by the same implementation agent. Parent read
the exact operation-order provider delta and all six new browser cases. Actual
held-IDB pre-fix failures prove B8's suppression and newer-read-warning defects;
B7 needs only tests because current POP intent guards already reject stale choices.
V1 proves1999ms unchanged/2000ms current durable projection with150ms changes and no
lifecycle flush. The first POP fixture accidentally gated only one StrictMode
bootstrap read; its failed output is retained and the corrected fixture observes
both reads. Focused20 desktop/mobile cases pass26.4s. Owning build passes2.25s.
Parent full996-case run is in progress on unchanged165-file source manifest
SHAa4002d1be4fae051a4565dc18b5f955464173b7aa5f85209128446a30c47c070;
no postpatch whole-browser pass or checkpoint is inferred until it completes.

### Final bounded completion

Parent postpatch full run:996 registered,994 passed/2 expected native integration
skips,18.1m,exit0;165-file before/after/current manifest unchanged at
a4002d1be4fae051a4565dc18b5f955464173b7aa5f85209128446a30c47c070.
Parent build passes2.25s with existing bundle warning; whitespace check passes.
BMAD status done records this bounded browser component delivery, not final
integration acceptance or release. User direction266 defers actual-owner/native,
physical-device/session/signup and release gates to the end. One pre-existing
shared Notes malformed-response validation issue remains in deferred-work.md.
All prior failures and unexplained initial caret visibility remain disclosed.
