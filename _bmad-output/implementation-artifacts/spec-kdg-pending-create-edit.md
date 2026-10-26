---
title: 'Local edits of pending creates with confirmed predecessors'
type: 'feature'
created: '2026-10-26'
status: 'done'
baseline_commit: 'ca96804b8f8477ee7cc95956d54440021c162c4a'
route: 'dispatch'
review_loop_iteration: 0
context:
  - '{project-root}/AGENTS.md'
  - '{project-root}/apps/kdg-capture/AGENTS.md'
  - '{project-root}/apps/kdg-capture/docs/CREATE_DELIVERY_EVIDENCE.md'
  - '{project-root}/apps/kdg-capture/docs/LOCAL_EDIT_SAVE_EVIDENCE.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** A completed locally saved capture cannot yet be edited before its create synchronizes. Existing edits require a server detail, which pending creates do not have.

**Approach:** Save a separate explicit local edit using the original definition and independent own-edit evidence. Prepare its command only after its actual predecessor receipt resolves; reuse existing explicit create/edit delivery.

## Boundaries & Constraints

**Always:** Preserve original create bytes, content, eligibility reference, device time and identities. Local pending content has no invented server revision, baseline or audit. Own-read and own-edit remain independent of create rights, current child assignment/activity and latest questionnaire. Each completed Save has a distinct action, exact predecessor and immutable proposal/base; whole-form validation, false/1 and hidden-detail rules apply. First edit derives expected revision only from its matching create receipt; later edits use their matching edit receipts. Retain stale proposals for attention without auto-rebase or false Synced. Preserve populated schema3 and supported old action interpretations, unknown versions and newer overlays. Honor current scope/session, deadlines, transaction completion, negative evidence and explicit newer restoration; old reviewed handles never revive after denial.

**Never:** UI/editor/Leave, unfinished typing persistence, automatic sender/queue/claims/scheduling/browser/service-worker/default-startup activation, real accounts/Auth/Access, native PostgreSQL/Docker, provisioning/migration execution, deployment/production/pilot/cleanup, installs/dependency changes, fingerprints/HMAC or push. Preserve historical evidence, concurrent changes/resources and TS7.0.2. Never read/run/copy/hash the preexisting untracked migration fixture; selected-source capsules only.

## I/O & Edge-Case Matrix

| Scenario | Input/state | Expected behavior | Failure handling |
|---|---|---|---|
| Pending edit | Real local create; exact setup own-read/edit | Original-version form, atomic separate action/overlay | Original create unchanged; no server facts invented |
| Independent authority | No create grant/children, inactive or unassigned child, newer questionnaire | Valid exact own-edit edits original capture | Missing/expired/denied own-edit blocks editing, retains readable input |
| Ordered work | Two local edits behind create | First blocks until validated create receipt; next until first edit receipt | No history/readback-only acknowledgement or guessed revision |
| Create uncertainty | Lost create response, readback outage or wrong receipt | Recover original receipt; only matching receipt enables predecessor | Preserve IDs; no replacement create |
| Conflict/races | New server progress; competing local Save; create receipt/readback during open/Save | Exact reviewed proposal retained, newer overlay survives; no silent rebase | Separate attention on stale proposal/chain |
| Authority restoration | Denial, stale/new setup positives, process/durable/cross-page state | Fresh positive authorizes future review only | Failed denial persistence cannot revive old forms |
| Storage/version | Quota, abort, completion ambiguity, collisions, malformed/unknown actions | Atomic commit or honest failure; exact retry/reopen preserves identity | Retain unsupported work without sending/deleting |
| Integrated flow | Actual local create then local edit, explicit deliveries | Create revision1 precedes correct edit revision2/readback | Existing server checks/idempotency preserved |

</frozen-after-approval>

## Code Map

- `apps/kdg-capture/web/src/history-store.ts`: ReviewedEdit/LocalEditIntent currently require CaptureDetail; add an explicit versioned local-base variant rather than optional server fields. Reuse validation, transaction/read/edit fences and action persistence. Keep existing v1 interpretation. `editAuthority` requires baseline/edit_context; pending local authority must use exact separate setup observations. `importProvision` null edit latches denial but positive setup restoration is missing: add newer-positive future-review restoration without reviving old handles, respecting process/durable generations/floors. Avoid a new permission engine.
- `history-store.ts` openEdit/saveEdit: preserve original reviewed local base and latest saved overlay, explicit typed create/edit predecessor. `prepareEdit` currently resolves edit_actions only; resolve a create predecessor from matching validated create receipt, never latest baseline. `prepared`, receipt consumption, ownProgress and reconcileBaseline need narrow union-aware adaptation; retain newer overlays during create readback. Newer unrelated baseline progress pauses unprepared descendants rather than rebasing.
- `web/src/create-delivery.ts`, edit-delivery.ts and Auth entries: reuse explicit bounded consumers without transport contract changes. Receipt may exist without readback; it is sufficient predecessor evidence, never server content. Existing recovery/PUT still enforce authority.
- `web/tests/local-edit-save-proof.mjs`, edit-reconciliation-proof.mjs, create-delivery-proof.mjs: existing real-IDB patterns and characterization protection. New `pending-create-edit-proof.mjs`, types/config: focused acceptance first. Root owns new actual HTTP integration using the explicit selected-source create fixture; never change historical fixture behavior.

## Tasks & Acceptance

**Execution:**
- [x] `web/tests/pending-create-edit-proof.mjs`, types and config — observe behavioral acceptance RED before implementation; cover matrix with real IndexedDB.
- [x] `web/src/history-store.ts` — typed pending edit Save, independent current setup evidence and actual predecessor materialization; preserve old consumers.
- [x] `web/tests/pending-create-edit-http-proof.mjs` — actual synthetic create→pending edit→create delivery→edit delivery/readback; root owned.
- [x] `apps/kdg-capture/docs/`, web README — append contracts, prepend handoff, source-bound traceability/evidence and five impacts; root owned.

**Acceptance Criteria:**
- Given every matrix state, when the focused proofs execute, then its expected behavior passes under exact sources.
- Given a real saved create and later local edit, when explicit delivery resumes, then actual API receives original create unchanged followed by receipt-based edit and correct readback.
- Given existing storage/Auth/setup/delivery consumers, when affected regression and scaffold parity run, then old supported behavior remains intact.

## Implementation Notes

Technical subset of approved Story2.2; story_key unset, not whole-story completion. No intent gaps or irreversible effects. Standing user authorization covers continuation through routine checkpoints and preserving the concurrent dirty tree. Investigation completed by a read-only agent. Root owns docs/integration/review/qualification/scoped commit; implementation agent owns store/focused tests. No new runtime service or generic lifecycle.

Impacts: scaffold primitives unchanged unless a demonstrated neutral defect requires owner/template/test promotion; shared UI and agent context unchanged; current handoff/contracts/evidence updated; existing ADRs suffice, accepted ADRs immutable. No activation or release-readiness claim.

## Spec Change Log

## Review Triage Log

## Verification

Retained approved toolchains only. Run the smallest behavioral RED then focused proof, actual synthetic HTTP integration and affected regression/parity. Base18-command runner: `platform/deployment/.local/kdg-explicit-create-delivery-20261026/root-verify/qualified.json`. Record exact commands/results and source custody under `platform/deployment/.local/kdg-pending-create-edit-20261026/`; reuse backend342 tests only after reconfirming85 effective source hashes. No native permission/rollback claim.

Compatibility correction: prior local-create Save proof intentionally asserted pending creates could not open a server-backed edit. This feature supersedes only that unavailable result with a typed local-create edit; retain the original no-server-provenance assertion and explicitly prove the new local discriminator. Failed stable qualification is retained, not hidden.

Pre-review qualification:20 source-bound commands pass;119 focused pending checks and39 actual HTTP groups, all18 previous regression/parity commands. Backend342 tests reused only after all85 effective source hashes reconfirmed. Root actual create→two pending edits reaches revisions1/2/3; receipt-only predecessor and foreign progress cases pass. New malformed non-head base RED then original-create binding retained. Exact traces and limits: `apps/kdg-capture/docs/evidence/pending-create-edit-20261026.json`.

| Finding | Verdict / route | Evidence |
|---|---|---|
| B1 persisted expected revision | medium / patch | A mutated v2 prepared revision/serialized pair can bypass its actual predecessor receipt. Validate persisted preparation against that receipt at reuse/consumption boundaries. |
| B2 exact pending permissions | medium / patch | Pending edit authority passes each declared permission back to the validator. Require exact read.own/edit.own names so malformed persisted setup cannot substitute another observation. |
| B3 independent setup import | medium / patch | Edit denial currently rejects the entire otherwise usable positive setup without restoreDenied. Commit independent read/create setup while retaining edit denial unless explicit newer restoration succeeds. |
| B4 stale epoch negative publication | medium / patch | A stale cross-page store can publish its early process latch before durable epoch rejection, blocking a current store. Reject stale publication without weakening latches on actual storage failure. |
| B5 malformed retry result | medium / patch | Exact v2 retry returns unvalidated existing.result. Validate original action/result identity and supported disposition before publication, retaining malformed evidence. |
| B6 redundant predecessor identities | low / patch | Embedded reviewed predecessor_action_id can disagree with typed predecessor/action fields. Reject that demonstrated contradictory envelope. |
| B7 denial completion coverage | low / patch | Extend direct v2 denial coverage beyond transaction acquisition to queued-write/completion failure and reopen. |
| B8 pending Save cancellation coverage | low / patch | Add abort and freshness change while IDB requests are pending; verify atomic no-write and original retry identity. |
| B9 mixed populated compatibility coverage | low / patch | Reopen one schema3 database containing supported v1/v2 edits plus unknown actions; prove independent supported behavior and unknown retention/blocking. |
| B10 rejected create descendants | low / patch | Root HTTP proof should attempt descendant delivery after actual known create rejection, proving no PUT and unchanged original identity/proposals. |
| E1 stale epoch denial | medium / patch | Same early-latch defect as B4, independently traced across pages. Preserve previous valid negative evidence when rejecting only stale invocation. |
| V1 independent reviewed expiry | medium / patch | Pre-verified gap: current expiry scenario expires current and reviewed setup together. Refresh current setup and separately expire original read/edit review, proving no save or overlay update. |
| R1 command byte-bound verification | low / patch | The named byte_bound case puts a string in a rating and fails earlier validation. Add valid original text questions whose UTF-8 command exceeds131072 bytes, proving actual command-size rejection. |

Final qualification:20 commands pass with unchanged247-source custody;216 focused checks,47 actual synthetic HTTP groups, all18 affected regression/parity commands including five scaffold parities. All13 review findings addressed; no deferrals. Known create rejection preserves readable descendants and sends no PUT. Running Save/denial race suppresses stale success and retains atomic completion evidence without claiming rollback. All85 backend sources reconfirmed for342 reused backend tests;171 historical/dependency files unchanged and prior contracts/handoff preserved.
