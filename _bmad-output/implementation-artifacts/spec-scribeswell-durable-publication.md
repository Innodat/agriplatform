---
title: 'Persist and activate an audited source manifest'
type: 'feature'
created: '2026-10-26'
status: 'in-review'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: 'f5899ecdd22cc4dad56ad646960b967582ade606'
context:
  - /home/ck/repos/innodat/agriplatform/AGENTS.md
  - /home/ck/repos/innodat/agriplatform/apps/scribeswell/docs/HIGHLIGHT_EVIDENCE_CONTRACT.md
  - /home/ck/repos/innodat/agriplatform/platform/docs/development/migration-verification.md
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

Implement the release-gated durable publication path consuming the delivered closed auditor: immutable manifest staging, completion and short activation with safe original-operation recovery. This supplies the protected stored evidence needed by the next reader/highlight consumer. The adopted highlight contract's proposed durable design is authoritative for this implementation.

## Boundaries & Constraints

**Always:** Preserve ordinary controller begin/recover/seal semantics, source-writing fences, prior controller records and public reads. Only a controlled owner runtime audits actual rows; shape-valid caller JSON never proves correspondence. Stage/completion/activation recheck current restricted principal/publication authority, enforcement and exact closed tuple. Immutable revision identity, canonical auditor-version-bound digest, full inventory and exact retry semantics are mandatory. Protected tables/routines use actor/server-UTC attribution, bounded transactions, stable safe errors and least privilege. Preserve all unrelated dirty files.

**Never:** Run native SQL/migrations, grant/revoke credentials, enable enforcement, touch KDGports55481/55482, call actual owner services, deploy/push or change Leave/factory/PtS. No source text in manifests/logs, startup migrations, competing Access path, new custody/operator framework or generated reference hand-edits. Native permissions/isolation/recovery qualification remains the agreed final phase; test doubles establish wrapper behavior only.

</frozen-after-approval>

## Code Map

- `apps/scribeswell/backend/closed_corpus_audit.py` supplies actual observation; `corpus_manifest.py` immutable candidates; `corpus_publication.py` existing caller connection/receipt discipline.
- `apps/scribeswell/migrations/versions/0002_corpus_writer_fence.py`, `0003_corpus_controller.py`: retain unchanged. Add forward0004; separate publication pointer, no new epoch enum.
- `apps/scribeswell/migrations/baseline.py`, `prepared_controller.py`, `controller_history.py`, `env.py`, `release_profile.py`, `apps/scribeswell/deployment/migrate.py`: current profiles pin0003 and upgrade head. Preserve historical profile contracts while adding explicit publication-capable profile.
- `apps/scribeswell/migrations/catalogue.py`, `generate_reference.py`: historical generated snapshots stay unchanged. New profile compares the objects present in pinned0003 by exact existing identity/definition/normalized ACL, allowing additions, and uses focused new-object behavior instead of a new full whitelist.
- Existing tests `test_owned_migrations.py`, `test_prepared_controller.py`, `test_controller_history.py`, `test_release_profile.py` and related runner tests provide compatibility patterns. Native tests are authored, not executed now.

## Tasks & Acceptance

**Execution:**
- [x] `backend/corpus_publish.py` under the app: canonical manifest encoder/hash and controlled publish/lookup API. Prequalify strict seal/source, derive stable revision/suboperation UUIDs from caller operation UUID, reconcile original activation before reauditing, invoke auditor internally, stage batches/complete/activate through fixed parameterized restricted routines. Never accept external claimed audit. Restore caller row factory and reconcile lost acknowledgements.
- [x] `migrations/versions/0004_corpus_publication.py`: additive private immutable header/verse/batch/completion/outcome records, current publication pointer and explicit source publication authority, strict execute/lookup routines. Full canonical digest/count and ordered IDs validated before completion. New writes require same enforced closed tuple; replay returns original acknowledgement under current authority without reactivation. Structural constraints and immutable protections include alternate writes. All new privileges remain revoked by default.
- [x] Migration/profile files above: recognize0004 independently of historical PROFILES; explicit versioned publication profile accepts0003 before upgrade and0004 repeat/postflight. Keep old0003 profiles version-pinned instead of making upgrade-head silently fail them. Support both dormant and explicitly prepared/history inputs without provisioning. Extend runner/result checks and focused tests coherently.
- [ ] `tests/test_corpus_publish.py`, profile unit tests, opt-in `tests/test_corpus_publish_native.py`: ATDD red before behavior, then protocol/encoding/retry/late failure/authority/error/compatibility tests; native upgrade/repeat/old controller/permission/stale completion/rollback cases authored and clearly unrun.
- [x] Adopted app contract and evidence: record implemented code, exact executed commands/results and remaining native/transport/release gates. Scaffold/sharedUI/agentcontext/ADR: app-specific, no promotion or decision change.

**Acceptance Criteria:**
- Given an audited closed source, when the controlled publisher runs, then it stages the complete immutable ordered manifest, completes its exact auditor-version-bound digest and returns publication acknowledgement only after activation commit.
- Given acknowledgement loss at each boundary, when the same operation is retried, then stable suboperation identities reconcile original results; changed semantics conflict and retired receipts never reactivate evidence.
- Given recovery/disable/revocation or partial/mismatched staging, when a new write executes, then it fails safely without published partial proof.
- Given existing0003 migration/history profiles, when the new code is used, then their versioned behavior remains supported and the explicit new profile selects0004. No generated reference edits.
- Given native integration deferred, when verification is reported, then application-side tests actually run/pass and native cases are identified as unexecuted, with no live publication claim.

## Implementation Notes

Technical choices are delegated within the adopted contract. Caller operation UUID identifies activation; derive revision/stage/batch/completion UUIDs deterministically. Activation request binds original seal/source/attempt/generation/checksum so changed retry intent conflicts, while lookup can reconcile before a new audit after recovery. Use separate publication authority rather than extending historical controller command grammar. The existing operator identity is trusted only inside the controlled auditor/publisher runtime. SQL reconstructs canonical manifest bytes from immutable header/ordered rows to verify completion; it does not independently attest that Python audited actual corpus correspondence. Retain incomplete stages for investigation. No routine checkpoint approval required under user's explicit continue-without-stops direction.

## Spec Change Log

## Review Triage Log

| Finding | Verdict | Route | Evidence |
| --- | --- | --- | --- |
| Blind1: profile does not check every new publication object | false | reject | This profile deliberately preserves pinned0003 identities and does not certify runtime publication readiness. Native focused behavior/permission qualification is an explicit release gate; another full-object whitelist conflicts with the adopted migration verification approach. |
| Blind2: alternate append races completion | high | patch | Insert trigger checks completion without a common header lock. A concurrent insert can pass the check before completion commits; serialize existing appends/completion on that header and author the two-connection regression. |
| Blind3: batch records need not match normalized rows | high | patch | Completion checks counts and canonical verse data but not each batch's index/offset/payload correspondence. Check the already stored relationship before completion. |
| Blind4: constituent actor mismatch | medium | patch | Alternate inserts can use another nonzero actor despite header ownership. Existing insert protection must require the header actor across constituent records. |
| Blind5: no native recovery race case | medium | patch | Sequential recovery cannot exercise the CAS race. Author a bounded two-connection regression; actual execution remains final-phase work. |
| Blind6: no native lost-ack cases | medium | patch | Doubles exercise reconciliation but not actual committed SQL boundaries. Author native post-commit-loss cases, explicitly unrun. |
| Blind7: native corpus exercises only one batch | medium | patch | Current native fixture has39 verses; a multi-batch resume/order/completion case is missing. Author focused coverage without claiming native results. |
| Blind8: maximum manifest performance unmeasured | maybe-false | defer | The code has bounded waits but no executed PostgreSQL maximum-manifest timing evidence. This is already a final integration gate; measure maximum supported inventory and digest reconstruction on actual PostgreSQL before activation. |
| Blind9: prepared audit policies can broaden other identities | maybe-false | defer | Added policy rows are allowed while original policies remain exact. No broad policy is shipped by0004; native operator/anonymous/other-role visibility and deployment preparation must be qualified before activation to establish whether a concrete unsafe preparation is accepted. |
| Blind10: controlled caller retention/transport integration absent | maybe-false | defer | Publisher is intentionally an internal caller-owned connection adapter, and no live publication claim exists. Original-operation retention and hard transport containment still need executable final integration evidence before activation. |
| Edge1: alternate append/completion race | high | patch | Same demonstrated unsynchronized completion check as Blind2; both rows retained and grouped for one header-lock fix. |
| Verification1: complete incorrect digest has no rejection test | medium | patch | Existing partial tests fail before canonical digest validation, and doubles cannot exercise SQL. Author a complete valid structure with wrong declared digest and require absent completion/pointer after rejection. |

All review layers completed before triage. The third fresh reviewer initially could not start while both earlier reviewers occupied slots; it was launched as a slot became available, before triage. A read-only CLI fallback failed to initialize its app-server client due to read-only filesystem; it produced no review result. No review assertion or failure was suppressed.

## Verification

Implementation and tests are present. The testing task retains its unchecked box because the initial publisher behavioral ATDD red was not observed; this historical process gap cannot be repaired by rerunning passing assertions. Profile behavioral red was observed. Native cases are authored only. Parent reviewed the complete owned diff, corrected the three structural storage roots, and inspected all added native cases without collecting/executing them.


Run smallest meaningful failing application-side tests before implementation, then the affected protocol/profile/previous comparison suites using `/tmp/scribeswell-implementation-python/bin/python`. Do not execute opt-in native files or other commands capable of opening real database fixtures. Record exact argv/results and source fingerprints. Parent owns final independent review and checkpoint; implementer must not stage/commit or modify canonical spec files.

Parent post-review verification:422passed46.30s,18equal before/after source/reference fingerprints. Earlier422passed50.30s evidence remains as pre-review artifacts. All12 review rows retained; native/performance/RLS/transport final gates remain. Implementation checkpoint is complete; status stays in-review for final native/release qualification and disclosed ATDD chronology gap.
