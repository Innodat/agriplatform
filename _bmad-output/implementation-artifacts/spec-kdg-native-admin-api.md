---
title: 'Native KDG administrator API qualification'
type: 'feature'
created: '2026-10-27'
status: 'done'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: '2586a22e0e97f39f2742b4d73c2d6a130d744c98'
context: []
---

<frozen-after-approval reason="user explicitly approved retained synthetic PostgreSQL qualification; standing approval covers routine delivery checkpoints">

## Intent

Qualify the implemented administrator Save/recovery API and its supporting record/context/audit reads against the retained synthetic PostgreSQL fixture. Mock Access only; use actual candidate engines, worker orchestration, transaction SQL, restricted roles and independent committed-state checks. Keep application/schema unchanged unless a reproduced defect needs a focused correction.

## Boundaries & Constraints

Use only run99b7231c-0a5b-4bdb-98e8-3329564c526a, database kdg_schema_659350f762c8494c9241b7b1c8ea9566, existing private custody, applied0002 provenance and recorded restricted runtime logins. Resume only the existing synthetic stack after network/volume custody checks; stop normally afterwards preserving all resources. No preparer, migration execution/promotion, provisioning, privilege expansion, cleanup, reset, real accounts/Identity/Access, UI/editor/Leave, startup/browser/queue/worker activation, deployment/production/pilot, install/dependency change or push. Fingerprints/HMAC remain deferred; preserve TypeScript7.0.2 and concurrent/historical work. Never read/run/copy/hash migrations/tests/schema_fixture.py.

Journal fresh synthetic parent, owner/admin account/actor, organization, target, operation and command IDs/inputs before seeding. Distinct admin account and actor must differ from owner; no synthetic Auth/Identity records. Use existing seed/create helpers, two observations under one fresh organization and original definition. Capture original complete business-row snapshot/counts outside the new org. Retain intent, observed execution before assertions and safe append-only success/failure evidence. Bind explicitly selected executed sources before imports/before writes/after qualification; no broad migration discovery, schema/ledger inventory or raw exception/credential/payload diagnostics.

All writes go through actual candidate APIs under current paired all permissions or owner permissions, retaining original deadlines/freshness and actual executor. Reads and recovery use actual read-only candidates; outcomes remain executor private even with all-read. Independent new physical restricted read-only sessions inspect capture/history under all_read and outcomes separately under each executor. After each response require released leases and exact receipt/error, immutable original facts, linked history/outcome attribution and expected complete row changes. Prior data/sentinel/ordinary Alembic head stay unchanged. Fault after update/private outcome before history must produce actual constraint SQLSTATE, full rollback and successful original-operation retry. Preserve failures; no blind rerun.

## I/O & Edge-Case Matrix

| Given / when | Then |
|---|---|
| Owner-created observations, administrator corrections | Original owner/creation/child/version retained; actual admin update and linked event/receipt; current detail/context/audit agree |
| Both owner/admin write orderings and intervening correction | Matching revision wins; stale/repeated reviewed operations409 without effects; new reviewed revision succeeds |
| No-op, changed-path/body replay, later revisions | No-op adds receipt only; replay returns original target/revision, no extra update/history |
| Edit loss/read-only recovery; read loss; another executor or organization | Current read.all recovers original receipt without PUT; denials before checkout; private absence unresolved; foreign target404 |
| Either paired capability denied, malformed evidence/input | Exact safe error/no-store, no own fallback/precheck checkout or mutations |
| Native constraint fault between provisional outcome and history | Safe error and actual SQLSTATE; all effects roll back; original retry exactly once |
| Read/driver/oracle/source/report failure | Safe unqualified failure evidence, observed execution retained, resources/data preserved |

</frozen-after-approval>

## Code Map

- New `apps/kdg-capture/migrations/tests/qualify_admin_api.py`; reuse capture_commit_fixture.retained/engine/identities/sentinel/revision/receipt/migration_qualified read-only custody, qualify_capture_commit.Dataset/seed/execute, qualify_own_edit.verify_transition, qualify_edit_recovery_http.snapshot/table_counts. Never call migrate_retained or native_fixture.prepare. Existing single-account row oracle is unsuitable for foreign-owner admin outcomes.
- Actual candidates: admin_http, admin_edit_context_http, audit_http, admin_edit_http, edit_http; existing handler/body/DTO exports and transaction_context unchanged. New qualifier owns cross-account oracle and matrix, not a new runtime abstraction.
- New `write-tests/test_native_admin_api.py`: behavioral ATDD and focused checks for response/lease, attribution/preservation, private receipts, journal/source/failure behavior; tests never connect to a database.
- Parent owns source capsule, retained run lifecycle/checkpoints/native execution and evidence; append contracts, prepend handoff and add `docs/NATIVE_ADMIN_API_EVIDENCE.md` plus machine record.

## Tasks & Acceptance

- [x] Observe behavioral acceptance failure in the new independent oracle before implementation; preserve source/log.
- [x] Implement selected native plan/oracles and focused tests, actual API matrix, safe append-only intent/results and explicit --qualify-retained CLI.
- [x] Parent execute once on approved retained target, reconcile failures before any retry, independently verify preservation/ledger/resources and normal stop.
- [x] Run focused affected tests, five scaffold parities, review and record exact source-bound commands/results. No full Story3.1/3.2, real Access, listener/network, native contention/cancellation or release-ready claim.

Given current administrator correction, when native qualification passes, then actual restricted SQL proves original ownership, conditional edits, linked private outcomes/audit and authorized recovery without altering historical data. Given any failure, when recording, then no passing qualification or silent reset follows.

## Implementation Notes

One cohesive native administrator Save qualification; routes/contracts already closed. No new human intent choice. User explicitly approved retained native testing after the prior handoff exclusion; that authorization supersedes historical no-native wording only for this slice. Standing authorization covers dirty tree/cohesive spec/routine checkpoints. Scaffold/shared UI/agent-context/ADR unchanged unless a concrete neutral failure requires promotion; five adopted code/test parity checks remain required. Docs/evidence updated. Do not touch Leave trackers/global cached context. Parent owns workflow/commits/execution; implementation child owns only new qualifier/tests, no skills, native execution or old source edits.

## Spec Change Log

## Review Triage Log

| Finding | Verdict | Route | Evidence |
|---|---|---|---|
| B1 | medium | patch | repeated_review copies admin_a value2 although admin_a2 current value4; correct journaled payload and regression. |
| B2 | medium | patch | Current native recovery covers changed outcome only; add recovery for the existing no-history noop outcome. |
| B3 | medium | patch | Detail/audit direct GETs omit recorded/asserted current READ sequence although independent row state passes; add exact sequence/checkout observations. |
| B4 | medium | patch | Independent field comparisons omit extra top-level/event keys and audit limit; add exact closed contract keys and limit assertion. |
| B5 | low | rejected | Existing unchanged read candidate authorization/foreign-scope tests are source-bound in prior185 suite; native correction adds current READ assertions. A full negative cross-product would add test branches without a reproduced application failure; low additional coverage rejected. |
| B6 | false | rejected | Applied0002 grants runtime SELECT only on parent tables (lines284-288), INSERT on capture/outcome/history and column UPDATE on capture only. Candidate runs as physically verified restricted runtime; cannot mutate seeded parents. No expanded snapshot mechanism needed. |
| B7 | low | rejected | Applied unchanged0002 triggers server-manage outcome committed_at/history created_at; prior migration/storage proof remains source-bound. Existing transition guard independently requires changed updated_at to increase and audit compares native history instant. Extra clock-bound guards for an unreproduced trigger defect would add complexity; rejected. |
| B8 | low | rejected | Safe failure type/stage, journal and pre-assertion observations already reconcile failures (demonstrated first native failure). Allowlisted additional check diagnostics require a new mechanism for negligible developer convenience; rejected. |
| B9 | low | patch | Fallback result contains receipt_error_type but stdout omits it, hiding report-storage failure. Include only safe type and canary regression. |
| B10 | low | patch | Owned current handoff prefix still describes pre-execution state; replace current prefix with completed counts/results and preserved failure; historical bytes retained. |

All three layers reported before triage: blind ten findings, edge zero, verification zero. Runtime thread cap required reusing prior reviewers for edge/verification; neither implemented this native slice. Five code/test patches and the owned current handoff correction; no deferrals or intent changes.

## Verification

Retained owner-env Python without symlink resolution; Node26.11.1/TS7.0.2, no installs. Explicit new focused tests plus affected own/admin/read/recovery suites and five scaffold checks. Source capsules exclude prohibited fixture. New native qualifier uses --qualify-retained only, verifies retained identities/applied migration before any seed and records all results. Private custody `platform/deployment/.local/kdg-native-admin-api-20261027/`;194 protected files/322 prior sources. Full portal/session/device, real authority, native contention/cancellation and release activation remain open.

Custody observation: four exact-project containers were already running before this delivery. User resource/concurrent-work preservation takes precedence over stopping an already-running stack. Parent will make no lifecycle call and preserve the initial running state; normal owned candidate lifespan/pool disposal still applies. Network/volume custody matched. No preparer/migration/lifecycle operation has run.

Candidate qualification passes37 native cases with69 bound sources,78 focused affected helper tests (22 new), five scaffold parities and independent postflight; earlier223-test affected run retained. One harness nested-loop failure was independently reconciled; failed parent dataset/source/report remain retained. All322 prior sources/194 protected files and24 prior proofs remain unchanged. No lifecycle call; four initially running containers remain running. Independent review follows.

Final review corrections pass: 38 native cases on a fresh journaled dataset,83 helper tests (27 new),five scaffold parities. Prior37-case proof/source/data retained. Final counts parents11 each/captures20/history50/outcomes56; independently reconnected postflight passes. Three review layers complete; six corrections,one false,three low rejected,zero deferrals. No application/schema/dependency changes; all original source/evidence/resource safeguards hold.
