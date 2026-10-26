---
title: 'Explicit resolution of confirmed own edit conflicts'
type: 'feature'
created: '2026-10-26'
status: 'done'
baseline_commit: '084bc886d5c53a70bd52f19aec202a768fac83f9'
route: 'dispatch'
review_loop_iteration: 1
context:
  - '{project-root}/AGENTS.md'
  - '{project-root}/apps/kdg-capture/AGENTS.md'
  - '{project-root}/apps/kdg-capture/docs/PENDING_CREATE_EDIT_EVIDENCE.md'
  - '{project-root}/apps/kdg-capture/docs/EDIT_DELIVERY_EVIDENCE.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Confirmed own-edit conflicts and descendants are retained but have no explicit local resolution decision. They cannot safely adopt current state or save a reviewed replacement.

**Approach:** Add an unmounted owner that reviews actual current server state and atomically adopts it or saves a new complete replacement with immutable decision linkage and paused descendants. Reuse existing read/edit-context/conditional PUT/recovery.

## Boundaries & Constraints

**Always:** Current own-read permits use-current without own-edit. Replacement requires fresh actual own-edit context, original definition and the revision actually reviewed. Preserve source commands, proposals/bases, receipt/conflict evidence, original create bytes and all descendants. Never automatically include/replay descendant changes. Unknown earlier prepared outcomes block competing decisions; unresolved lookup alone cannot prove no in-flight commit. New replacement identity, no changed reuse of conflicting operation. Atomic decision/action/overlay/dispositions and reviewed head/generation/current-state CAS. Late receipt/readback cannot revive retired branches or clear newer work. Exact retries are truthful; permission/session/deadline/storage failures cannot claim success or rollback without evidence.

**Never:** UI/editor/Leave, automatic merge, new conflict/override endpoint/service, active sender/queue/claims/scheduling/browser/service-worker/default-startup activation, unfinished typing persistence, real accounts/Auth/Access, native PostgreSQL/Docker, provisioning/migration execution, deployment/production/pilot/cleanup, installs/dependency changes, fingerprints/HMAC or push. Preserve TS7.0.2, concurrent work and historical evidence/resources. Never read/run/copy/hash the preexisting untracked migration fixture. Same-phone unprepared and pending-create conflict decisions are the next separate subset, not implemented here.

## I/O & Edge-Case Matrix

| Scenario | Input/state | Expected behavior | Failure handling |
|---|---|---|---|
| Use current | Known matching edit409; fresh authorized current detail; own-read only | Atomic local adoption/decision, proposals retained, descendants paused | No PUT or invented revision/audit |
| Replacement | Fresh current edit-context and reviewed complete original-version values | New action/operation pins shown revision, ordinary explicit delivery | Report local pending until actual receipt/readback |
| Unknown outcome | Any earlier prepared capture action lacks receipt/known conflict | Block competing resolution; original recovery remains available | Preserve IDs; unresolved is still uncertain |
| Stale/concurrent review | Local head, baseline or decision generation changes | Reject stale decision; preserve acknowledged proposals | No silent rebase or overwritten overlay |
| Repeated change/lateness | Replacement later conflicts; old receipt/readback arrives | Retain new conflict; retired descendants never send | No resurrection or false completed resolution |
| Scope/storage/identity | Denial/logout, quota/abort/completion ambiguity, repeated decision IDs | Atomic commit or honest failure; exact retry recovers decision | Contradictory retries rejected, no partial dispositions |
| Compatibility/bounds | Populated schema1/2/3, unknown versions or oversized capture branch | Additive isolated upgrade, retain all rows, safe refusal on unsupported/incomplete review | Old schema3 clients cannot bypass resolution fences |

</frozen-after-approval>

## Code Map

- `apps/kdg-capture/web/src/history-store.ts`: add isolated schema4 `resolutions` store and capture-scoped action index, preserving all stores/opaque rows. Old connections close on versionchange; schema3 opens must refuse4 rather than ignore fences. No activation: incompatible local format requires coordinated browser update/recovery qualification before any release. Reuse short transactions, own-read/edit observations, branded frozen reviews and complete-time checks.
- Add `openConflict`, `useCurrent`, `saveConflictReplacement`, bounded `readResolutions` (equivalent concise names acceptable). Input pins account/org/capture/source action. Require validated source `delivery.conflict` and active saved head within its branch; block capture actions with unknown prepared outcomes or unsupported interpretation. Bound capture review to100 actions via index; overflow refuses without writes, never silently omits descendants. Decision version1 stores complete reviewed current snapshot, source/head/generation, selected complete result, new replacement link and internally derived source/paused dispositions. No caller-supplied disposition authority. Increment record resolution_generation and fence all older reviews, including ordinary openEdit/saveEdit.
- Keep resolution disposition outside immutable action content/status/predecessors/bytes. `prepareEdit` blocks retired/paused work including frozen commands; strict original lookup/outcome retention may support recovery but never sending. `reconcileBaseline` retains new replacement overlay and immutable decisions under late old outcomes. Replacement is ordinary server-backed v1 intent based on actual reviewed detail, with new operation and frozen expected revision; do not change v1/v2 payload meaning.
- New `web/src/conflict-resolution.ts` and Auth entry reuse current explicit entry patterns: review uses readCapture for use-current, loadEditContext for replacement; decision starts a new lease and rechecks current read/detail or edit-context outside transactions before CAS. No lease/transaction spans human review. Total30sec default/max per invocation incl storage/publication/release; each HTTP≤10sec/remaining. Detail/current entry context cannot fabricate or renew seven-day offline observations: existing valid retained own-read remains required; expiry safely requires existing setup/history refresh. Replacement observes original reviewed expiry independently of refreshed current evidence.
- `web/tests/edit-reconciliation-proof.mjs`, pending-create-edit-proof.mjs and delivery proofs provide characterization. Root owns actual HTTP integration/docs/broad qualification; agent owns store, explicit owner/entry, focused proof/types/config and necessary selected-source imports. Historical fixture sources remain unchanged.

- Recovery correction: add `lookupResolution` (equivalent name acceptable) under current retained own-read. Snapshot/normalize immutable original reviewed decision inputs (choice, decision_id, replacement action_id and complete changes); do not include newly fetched detail/permission timestamps in retry identity. Coordinator checks this before any HTTP or new-write authority. Valid existing outcomes recover even after later server changes/edit denial/reopen. Missing means perform the existing fresh read/edit-context checks and original CAS; known read denial still prevents protected recovery. Keep new-decision branding and scope guards. Return no new-decision success from unknown/corrupt evidence.
- Recovery must validate actual retained effects: source/action identity, immutable decision selection/linkage, replacement action when present, and recognized record dispositions/generation. Allow legitimate later resolution, receipt/readback or baseline progress; never require the old overlay/head still to be active. Missing/contradictory effects refuse without deleting evidence. Validate complete known v1 scope/capture/base/input/predecessor/expected/result consistency and the bounded associated predecessor graph (typed v2 create links, missing references/cycles), rather than treating malformed work as interpreted. Do not impose a global cross-kind UUID namespace.
- After edit denial, latch edit loss but only lock own-read on an actual applicable read denial; an unavailable/malformed probe is not a verified negative. Replacement uses ordinary false-boolean hidden-detail normalization before identity/validation, shared with existing Save paths without changing their behavior. `readResolutions` returns safe invalid on malformed untyped cursor/input.
- Add focused source-bound cases for immutable decision replay after server progress, read-only recovery after lost edit permission, missing linked effects, malformed v1/graph, true boolean normalization, live decision abort versus completion ambiguity, and populated real schema3 create receipts/prepared edits/overlay/chain upgraded to4. Root extends actual HTTP proof with edit authority revoked between review/decision and unavailable read probe retaining independent history.

## Tasks & Acceptance

**Execution:**
- [x] `web/tests/conflict-resolution-proof.mjs`, types/config — observe real-IDB behavioral RED; cover matrix and schema upgrade/version refusal.
- [x] `web/src/history-store.ts`, conflict-resolution.ts and entry — explicit confirmed-server conflict review/decision and paused branch safeguards.
- [x] `web/tests/conflict-resolution-http-proof.mjs` and isolated fixture — root: actual conflict→read-only adoption/replacement→repeat conflict/recovery.
- [x] `apps/kdg-capture/docs/`, web README — root: contracts/handoff, release-format gate, source-bound evidence and five impacts.

**Acceptance Criteria:**
- Given every matrix state, when registered focused proofs run, then expected behavior passes without deleted evidence.
- Given actual synthetic409 and current state, when adoption/replacement is explicit, then no override endpoint is used and only a matching replacement acknowledgement confirms server success.
- Given existing v1/v2/setup/history/Auth/delivery consumers, when affected regression and scaffold parity run, then compatibility holds under the explicitly isolated new format.

## Implementation Notes

Technical subset of approved Story2.3, story_key unset. No unresolved intent gaps or irreversible external actions; synthetic IndexedDB upgrades only. Standing authorization covers cohesive specification size, dirty-tree preservation and routine checkpoints. Root preserves baseline in `platform/deployment/.local/kdg-own-conflict-resolution-20261026/`. Dedicated immutable decisions avoid unbounded record blobs and give older code an explicit version boundary.

Scaffold: reuse proven Auth/IDB primitives unchanged unless a demonstrated neutral fix warrants template/generated-test promotion. Shared UI and agent context unchanged; docs updated; accepted ADRs remain immutable. No release/device/native readiness claim. Same-phone/pending-local resolution follows automatically after this qualification.

## Spec Change Log

### Review loop1 — committed-decision recovery

B3/B4/E1 exposed a Code Map gap: fresh server context was mixed into immutable retry identity and required before discovering committed local success. Amend the owner/store contract with an own-read committed-decision lookup before HTTP, plus linked-effect validation. Avoid false decision_id_reused after server progress and false denial when recovering an already-saved replacement. Other verified internal corrections/behavioral gaps are carried into this re-derivation; B1/B8 are rejected on documented evidence. Frozen intent remains unchanged.

KEEP: isolated additive schema4 and capture indexes; no mounted/runtime activation or new opt-in API. Existing startup imports Auth only. Preserve all prior current/adopt/replacement semantics, immutable original commands/bases/create bytes, paused off-head descendants, unknown-outcome refusal, exact current-state CAS, epoch/negative/expiry fences, total30sec/HTTP10sec budgets and release/device gate. Preserve all89 focused and51 actual HTTP positive behaviors plus previous20 suites. Preserve strict malformed-decision decoder and known Needs attention proposal compatibility. Do not copy back known-bad current-dependent retry or unconditional outage-as-denial behavior.

All16 pre-rederive owned files/diff/source hashes are archived under `platform/deployment/.local/kdg-own-conflict-resolution-20261026/before-rederive-1/`; old proofs/capsules remain unchanged. Archived focused/HTTP tests are positive-preservation references. Root restores/adapts its HTTP proof/fixture and owns documentation/qualification. Fresh implementation agent re-derives only owned store/owner/entry/focused types/config and necessary transitive lists. No other working tree changes may be reverted.

## Review Triage Log

| Finding | Verdict / route | Evidence |
|---|---|---|
| B1 default schema activation | false / reject | No runtime startup/UI imports or calls openHistoryStore: all source references are type-only, with store injected into unmounted consumers. startup.tsx→LocalEntryRoute mounts Auth only. Explicit isolated calls upgrade by design; no default-startup activation occurred. Clarify docs; do not add an unneeded opt-in surface. |
| B2 unavailable read probe locks history | medium / patch | After edit403 any failed probe calls deny; transient outage is not verified own-read loss. Lock only applicable own-read denial, retaining independent known read scope otherwise. |
| B3 current-state-dependent retry identity | medium / bad_spec | Fresh current detail is in immutable retry identity, so another server update turns an exact committed retry into decision_id_reused. Define identity from original reviewed decision inputs and consult committed evidence before new-state checks. |
| B4 replacement recovery requires edit | medium / bad_spec | Coordinator loads edit-context before committed-decision lookup. Add an own-read lookup/recovery path before authority needed only for a new replacement; this requires an explicit new store surface in Code Map. |
| B5 incomplete v1 interpretation | medium / patch | Conflict branch checks v1 base/input but not embedded scope/capture/predecessor/expected/result consistency. Decode known v1 identity completely for branch interpretation, preserving expired historical evidence as data. |
| B6 incomplete associated graph | medium / patch | Only head→source ancestry is checked; missing/cyclic off-head predecessors can be treated as fully understood associated work. Validate bounded associated graph and retain unsupported work on refusal. |
| B7 missing durable decision effects | medium / patch | Valid decision result may report saved_locally after linked replacement is missing. Recovery must verify retained linked actions/dispositions without rejecting legitimate later decisions or acknowledgement progress. |
| B8 cross-kind identity asymmetry | false / reject | Actions and local decisions use separately typed keyed stores; there is no global cross-kind uniqueness contract and matching strings do not overwrite data or redirect typed callers. Extending every creation path adds guards without a demonstrated user/developer failure. |
| B9 replacement false-detail normalization | medium / patch | Replacement validates directly while ordinary Save strips hidden details for false booleans. Reuse same normalization and prove valid1/false behavior without mutating caller input. |
| B10 populated upgrade characterization | medium / patch | Existing upgrade proof has opaque placeholders only; add schema3 real pending/prepared chains, create receipt and overlay preservation with usable conflict resolution after additive4 upgrade. |
| B11 live decision cancellation | medium / patch | Add controlled pre-commit abort with decision/action/overlay/baseline/dispositions unchanged; completion ambiguity remains a separate honest outcome. |
| E1 committed retry after newer detail | medium / bad_spec | Independent duplicate of B3; immutable decision lookup must precede fresh detail and compare original inputs only. |
| E2 malformed resolution cursor | low / patch | readResolutions calls startsWith on untyped non-string outside handling. Return safe invalid for malformed cursor/input. |
| V1 authority revoked between review/Save | medium / patch | Pre-verified gap: real HTTP currently revokes only after local Save. Add actual edit denial between successful review and decision, asserting no new action/decision/disposition and readable original proposal. |

### Round2 triage

| Finding | Verdict / route | Evidence |
|---|---|---|
| R2-B1 recovery after100 actions | false / reject | The declared compatibility/overflow contract deliberately refuses an oversized capture branch without deleting evidence. Recovery remains a bounded protected operation; no false success or mutation is reported. Expanding supported lifetime bounds is not a demonstrated correctness fix. |
| R2-B2 omitted descendant disposition | medium / patch | decisionEffects only verifies listed descendants. An omitted off-head retained descendant and omitted record disposition can pass the decoder; compare the derived complete source/descendant set. |
| R2-B3 contradictory retained baseline | medium / patch | decisionEffects accepts any truthy baseline. Validate actual retained detail identity/original definition and revision at least the adopted current revision before recovering success. |
| R2-B4 v1 baseline lineage | medium / patch | A root v1 review has no saved predecessor, so openEdit sets baseline_revision equal to base.revision. Decoder permits a contradictory decimal. Keep legitimate progressed-baseline child reviews; validate root equality and monotonic baseline/base relation. |
| R2-B5 reviewed predecessor proposal | medium / patch | Known associated v1 review capture can contradict existing predecessor base+changes while passing sameOriginal. Validate the editable complete snapshot actually produced by openEdit; do not reject legitimate baseline progress. |
| R2-B6 safe-integer generation overflow | low / reject | Reaching MAX_SAFE_INTEGER requires more than9 quadrillion decisions, while this decoder refuses captures above100 retained actions. No supported path reaches that generation. Adding overflow guards for invented state would not prevent an everyday failure. |
| R2-B7 repeated graph interpretation | low / reject | Measured supported100-action/99-decision review opened in2968.5ms within30000ms; setup223253.1ms is separate from a user invocation. No operation-budget failure was observed. Additional reuse plumbing targets an extreme repeated-conflict case, not a demonstrated everyday defect; retain measurement instead of adding complexity. |
| R2-B8 independent connection concurrency | medium / patch | Preexisting same-instance concurrency covers transaction ordering but not new durable resolution CAS through separate connections. Add two-connection decision competition and ordinary Save race with one truthful outcome. |
| R2-B9 cancellation during lookup/refresh | medium / patch | New coordinator lookup and replacement refresh phases need cancellation/deadline characterization, including releasing a deferred result after return and proving no later writes. |
| R2-B10 confirmed own-read denial | medium / patch | HTTP proof tests unavailable probe only. Add actual direct read403 and edit403/read403 paths, refusing subsequent protected reads/recovery while retaining raw evidence. |
| R2-E1 omitted descendant disposition | medium / patch | Independent duplicate of R2-B2; derive and compare complete retained source/descendant disposition set. |
| R2-V1 confirmed own-read denial | medium / patch | Pre-verified regression gap: removing either coordinator deny call leaves current tests unchanged. Add actual403 routes and retained-history/decision-recovery denial assertions. |

Final supported-bound rerun:4399.3ms/30000ms review;440504.3ms fixture setup, no forced stop.

Round2 patches preserve the public surface: complete dispositions and actual retained baseline are decoded; v1 root/proposal lineage is checked while progressed children remain valid. Independent-connection CAS, lookup/refresh cancellation/deadline and both actual read-denial paths are now characterized. Four focused RED frames precede internal corrections; no new deferrals. Final22-command qualification of patched sources passes.

## Verification

## Verification

Retained Node26.11.1/TS7.0.2/Chromium/modules/Python only. Focused RED→GREEN, actual synthetic HTTP, then previous20 commands from `platform/deployment/.local/kdg-pending-create-edit-20261026/root-verify/qualified.json`; update superseded schema expectations only with explained new behavior, retaining invariants. Record exact sources/commands/traceability. Reuse342 backend tests only after reconfirming85 effective source hashes. No native permission/rollback claims.

Compatibility verification correction: the old create proof forced version4 to simulate a future unsupported format when owner schema was3; now force5, retaining versionchange closure/refusal. The actual create HTTP proof raw-inspection helper opened explicit3; open the existing fixture database without requesting a stale downgrade. These are explained fixture updates for isolated schema4, with prior failed run retained.

Final qualification:22 commands pass against254 stable sources:282 focused checks,
77 actual HTTP checks and all20 previous affected regression/parity commands. Five
scaffold parities pass. All85 backend sources are unchanged before reusing342 tests;
173 historical/dependency hashes, append-only contracts and prepend-only handoff pass.
Exact commands/results and source hashes: apps/kdg-capture/docs/evidence/conflict-resolution-20261026.json.
Initial and intermediate candidate frames remain in the private evidence directory;
none replace final source-bound results. Two rounds:26 findings,21 addressed, five
rejected with individual evidence, zero new deferrals. Accepted ADRs remain unchanged.
