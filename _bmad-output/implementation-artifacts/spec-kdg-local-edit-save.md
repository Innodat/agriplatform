---
title: 'KDG atomic local explicit edit Save'
type: 'feature'
created: '2026-10-26'
status: 'done'
baseline_commit: 'a97e9d1ea74ea42c6812b30568ae7dcd48b24daa'
route: 'dispatch'
review_loop_iteration: 1
context:
  - '/home/ck/repos/innodat/agriplatform/AGENTS.md'
  - '/home/ck/repos/innodat/agriplatform/apps/kdg-capture/AGENTS.md'
  - '/home/ck/repos/innodat/agriplatform/apps/kdg-capture/docs/OWN_EDIT_CONTEXT_EVIDENCE.md'
---

<frozen-after-approval reason="user authorizes continued KDG implementation without routine internal approval stops">

## Intent

Implement the isolated local persistence consumer for explicit edits to server-backed
own captures. Persist exact verified edit-context evidence, pin the actually reviewed
base, and atomically commit completed saved changes plus a distinct durable edit
intent. This implements the storage portion of approved Story2.2, without UI activation.

## Boundaries & Constraints

Keep account/organization isolation, original definition/owner/child/version facts,
independent seven-day own-read/edit observations and existing denial/clock/epoch fences.
Context import must not overwrite pending overlays, reviewed bases, conflicts or action
IDs. History/read-only success cannot renew edit authority. Original questionnaire
validation applies;1 and false are valid, hidden details are excluded from saved false
answers. No unfinished typing/Cancel writes. Saved means local transaction completion,
never Synced or a server receipt.

Each explicit action has stable supplied UUID identity, immutable snapshot and its
reviewed base. Retrying the same action is idempotent only for identical content;
changed content under that ID refuses. Serial saves depend on their own unresolved
predecessor; never guess its expected server revision. A stale local form or unrelated
newer server baseline preserves a separate completed proposal as Needs attention,
without overwriting newer saved work or automatically rebasing. No mutation of old
in-flight commands. Current denial/expiry prevents Save, outage remains unavailable;
pending work remains retained/locked. Commit failures never claim saved success.

Synthetic local/CI only. No UI/editor/Leave, pending-create producer, queue sending/
claiming/reconciliation, service-worker/browser/default-startup activation, real Auth/
Access/accounts, PostgreSQL/native/Docker qualification, provisioning/migrations,
deployment/production/pilot or cleanup. A private isolated IndexedDB schema upgrade
is permitted; no live application activation. Preserve concurrent work, historical
evidence/resources and dependencies including TypeScript7.0.2. Fingerprints/HMAC stay
deferred. Never read/run/copy the preexisting untracked migrations/tests/schema_fixture.py.

## I/O & Edge-Case Matrix

| Scenario | Expected behavior |
|---|---|
| Verified original server record then offline reopen | Persist both exact observations/definition; return immutable reviewed snapshot under valid scope |
| Explicit valid Save, close/reopen | Overlay and action commit atomically; original baseline/attribution unchanged; saved locally only |
| Typing/Cancel, invalid whole form | No committed edit/action; caller input unchanged; validate original required rules and false/detail handling |
| Repeat same ID / changed-ID content | Identical replay returns same result without duplicate; contradictory reuse refuses |
| Sequential saves / two tabs / stale form | Distinct immutable actions and predecessor; no guessed revision; stale proposal retained as attention without replacing newer overlay |
| History refresh / newer remote baseline | Preserve actions/base; background refresh cannot upgrade reviewed revision; stale Save retains attention |
| Denial, expiry, clock anomaly, logout, account replacement | Prevent affected stale publication/write, retain original-account work; read success never renews edit scope |
| Quota/abort/upgrade/reopen | No partial overlay/action or success; existing v1 history remains compatible and readable |

</frozen-after-approval>

## Code Map

- `apps/kdg-capture/docs/contracts.md` local persistence and own-edit increments; `docs/epics.md` Story2.2: authoritative scope, later pending-create/sender work remains there.
- `web/src/history-store.ts`: declare a scoped bounded action/proposal read method (default30/max100 and key continuation), capability-specific edit denial plus explicit newer verified-context restoration, and safe expired/denied/unavailable results. Bind edit observations to durable denial generation so history restoration cannot revive them. Recheck authority before writes/publication. Match supported PUT character and131072-byte payload rules using normalized completed changes; cover maximal expected-revision overhead. Existing four-store v1 IndexedDB, atomic page import, namespace/epoch/denial/clock fences. Extend minimally or add a local module sharing the same store owner; preserve history metadata and all opaque pending fields. Avoid a generic persistence engine.
- `web/src/edit-context.ts`, `own-observation.ts`, `read-validation.ts`: reuse exact envelope, evidence and original-definition validation. Clone inputs before freezing. Add only a small whole-form normalization seam if false-detail exclusion requires it.
- `web/offline-tools/idb.ts`: generated transaction primitives; reuse unchanged unless a concrete neutral defect requires owner template/generated tests together.
- `web/tests/history-store-proof.mjs`: retained explicit-source TypeScript7.0.2/Chromium proof, real IDB rollback/reopen and isolated loopback assets. Add a similarly source-bound `local-edit-save-proof.mjs`, fixtures/type checks and actual acceptance RED. Update old raw open version assumptions for compatible upgrade if needed, preserving all61 existing checks.

## Tasks & Acceptance

- [x] `web/tests/local-edit-save-proof.mjs` — observe real missing behavior RED and retain exact sources/logs before implementation; characterize touched history behavior first.
- [x] `web/src/history-store.ts` and minimal local edit module — implement import/open/explicit Save with scoped fences and versioned immutable intents; no sender.
- [x] `web/tests/` — focused TDD and actual isolated Chromium tests for every matrix row, including rollback, cross-tab race, same-ID replay, independent observation expiry and v1 upgrade.
- [x] Root — source/diff audit, focused then affected regression, independent BMAD reviews, evidence/contracts/handoff and scoped local commit.

Given a valid original-owner reviewed capture and current exact observations, when an
explicit Save completes, then its immutable action and saved overlay survive reopen
atomically. Given stale bases, failed storage or invalid authority, when Save executes,
then it never overwrites newer work or claims unsaved input was saved.

## Implementation Notes

Implementation re-derivation1 is authorized without routine halt; no human intent changed. The pre-rederive working implementation/proof is preserved under `platform/deployment/.local/kdg-local-edit-save-20261026/rederive-1/` as concrete KEEP evidence. Reuse sound pieces while correcting the above plan gaps. Record behavioral RED against preserved prior sources for every changed failure class, then focused TDD. Root owns final documentation and review triage. Add immediate mutation, independent refreshed-token expiry, pending-only/conflict-only and denial→read restoration canaries. New typed outcomes must remain backward compatible with existing generic history methods.

No intent gap or irreversible external action. Engineering choices include API names,
local schema version/action shape; document them. Keep sender/pending-create follow-up
within existing Story2.2, not a second specification. Root owns final docs/spec/commit;
implementer must not stage/commit or alter unrelated files. Record exact commands,
pre-fix RED/snapshots, source/log hashes under
`platform/deployment/.local/kdg-local-edit-save-20261026/` using unique run directories.
Use retained tool paths from prior evidence; request escalated execution for Node child
compilation/Chromium. No whole-silo copies. Scaffold: reuse proven IDB/Auth primitives;
domain state stays KDG. Shared UI/context: none. Docs: append/prepend, preserve history.
ADR: inherit existing decisions, no accepted edits.

## Spec Change Log

Iteration1: B3/B4/B6 exposed incomplete non-frozen storage API planning. Add bounded retained-action reads, independent edit denial/recovery and safe authority outcomes. Avoid inaccessible acknowledged proposals, unnecessary read revocation and renewal of denied edit authority through read recovery. Frozen intent remains unchanged. KEEP all47 working Chromium cases, exact observations, v1 compatibility, normalized hidden-detail exclusion, pinned bases, immutable intent/predecessor identity, atomic rollback and all61 history checks. Pre-rederive four-source snapshot/diff/hashes retained under the private rederive-1 capsule; no historical evidence is rewritten.

## Review Triage Log

All three review layers returned before triage; runtime slot capacity required sequential reviewers.

| Finding | Verdict / route | Evidence |
|---|---|---|
| B1 NUL/lone surrogate local text | medium / patch | validateDetail text does not enforce server AnswerText character rules; sanitize/validate completed changes before durable success, including boolean details. |
| B2 old context-read expiry locks fresh read cache | medium / patch | editAccess calls sensible on expired context read even after partition observation renewal; reject only that edit, preserve current independent read authority. |
| B3 retained proposal inaccessible after reopen | medium / bad_spec | Actions live outside read/openEdit view, with no scoped retrieval. Plan omitted bounded action/proposal read API required to consume acknowledged retained work. |
| B4 independent edit denial missing | medium / bad_spec | Only namespace-wide deny exists. Plan omitted a capability-specific denial/recovery seam required by current denied-edit versus readable-history scope. |
| B5 pending-create editing missing | low / reject | Current Intent explicitly selects server-backed captures and excludes pending-create producer. Pending-create dependencies remain unimplemented Story2.2 scope, recorded as a delivery limit rather than claimed complete. |
| B6 expiry/denial collapsed into unavailable | medium / bad_spec | Current catch erases known authority states. Plan must declare safe typed outcomes distinguishing expired/denied from transient unavailable. |
| B7 mutation during first await untested | low / patch | Copying exists but tests only inspect after completion. Add immediate caller mutation canaries for import and Save. |
| E1 expired context read locks current read cache | medium / patch | Same observed path as B2; current newer partition own-read must remain usable. |
| E2 observation expires during action lookup | medium / patch | Checks precede awaited IDB lookup; final transaction check covers only session/lifetime. Revalidate reviewed/current observations immediately before writes and publication. |
| VG1 refreshed stored authority masks stale review checks | medium / patch | Preverified: existing expiry tests fail in editAccess before token checks. Refresh context then expire original read/edit separately and prove no new action. |
| VG2 pending/conflict blockers untested | medium / patch | Preverified: pending fixture only proves upgrade. Seed each independently with matching revision/head and verify attention/no overwritten overlay. |
| R1 read restoration revives old edit context | medium / patch | deny increments partition epoch; importPage restoration clears denial, while old row.edit_context has no epoch binding. Bind edit evidence to denial generation; fresh read alone cannot restore it. |
| R2 local Save can exceed supported wire size | medium / patch | Original form bounds permit many multibyte answers beyond PUT131072-byte payload limit; validate sendable completed command size before saved success, including conservative revision overhead. |

## Verification

New real IndexedDB acceptance proof and existing61-case history regression are required.
Use existing strict TypeScript7.0.2 and explicit selected-source capsules. Run compiled
Auth/client regression, synthetic16-group HTTP path if shared validators change, six
schema/client owners and five scaffold parities. No actual DB or physical durability
claims. Root captures baseline protected/historical hashes and final source-bound runs.

Second review completed all three layers before triage. No intent or plan loopback is required; remaining corrections use existing methods and demonstrated states.

| Finding | Verdict / route | Evidence |
|---|---|---|
| B2.1 cross-tab durable generation | medium / patch | Process generation remains0 after another realm writes/restores generation1; explicit fresh import may commit but final validation refuses. Synchronize observed current generation while preserving old-token invalidation. |
| B2.2 failed denial generation recovery | medium / patch | Latch increments before failed metadata write; fresh import uses older durable generation and cannot clear the process denial. Reconcile only with explicit newer verified restoration. |
| B2.3 expiry at commit boundary | low / patch | Final check intentionally suppresses publication after commit, so retained work may exist. Add direct test and original-ID recovery documentation; never claim rollback after completion or invent another outcome model. |
| B2.4 retained proof prerequisites | low / patch (root docs) | Clean checkout alone lacks approved ignored capsules. Document exact retained paths/argv and this reproduction gap; no install/setup framework or dependency change is justified. |
| B2.5 fresh-realm reopening | low / patch | Existing handle reopen retains module fences; add actual page reload proof of saved overlay/proposal recovery. |
| B2.6 failed denial untested | medium / patch | Existing quota tests do not fail the denial partitions write. Verify latch/read isolation and fresh repair on that actual path. |
| B2.7 byte-bounded proposal projection | low / reject | Reads already have count/key bounds consistent with existing local history. No measured memory failure or everyday defect was demonstrated; a second projection/detail API adds complexity. No new unbounded scan or pruning is introduced. |
| B2.8 operation docs and impacts | low / patch (root docs) | Final root docs were excluded from runtime review diff. Publish operations/outcomes/reproduction/traceability and all five impact decisions; draft already contains explicit choices. |
| E2.1 cross-tab restoration | medium / patch | Same generation mismatch as B2.1; verify existing handle can recover from another realm's newer durable state without reviving old review tokens. |
| VG2.1 action read isolation/authority | medium / patch | Preverified: one-partition fixture cannot detect missing IDB range or read-expiry enforcement. Populate foreign account/org and deny/expire read separately; edit-only denial must preserve permitted retrieval. |
| VG2.2 failed edit-denial latch | medium / patch | Preverified: successful writes cannot detect a latch moved after commit. Fail the write and prove denied editing through existing/reopened handles while reads remain available. |
| R3 missing edit context mislabeled denial | low / patch | History-only row has no edit_epoch and reaches denied before checking absence of evidence; return unavailable for a cache/evidence miss, preserving actual denial outcomes. |

Final evidence and requirement mapping: `apps/kdg-capture/docs/LOCAL_EDIT_SAVE_EVIDENCE.md` and its machine record. All29 affected jobs pass with unchanged source hashes; prior313 backend proof reused only after full backend source hash comparison. All eight unchanged protected files and every historical evidence hash match baseline; the concurrent root package.json PtS workspace registration is preserved and documented, with all dependency declarations and the lock unchanged. Local scoped commit only, no push.
