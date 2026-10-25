---
title: KDG inert own-edit transaction body
type: feature
created: 2026-10-25
status: done
route: oneshot
baseline_commit: 6072e73377d5d7b4a46b0975b53800001431ed94
---

<frozen-after-approval reason="human-owned intent">

## Intent

Implement the next bounded KDG persistence slice in `write-candidate/capture_edit.py`: a fresh-only `edit_in_transaction` body consuming existing verified owner context, original Budget, path capture ID, EditCommand and exact own-edit permission. It is inert: no engine, routes, Auth/HTTP coordination, current-access service call, UI/editor/queue or active startup. Caller must establish current organization admission/membership, durable actor and current own-edit authority before the transaction; shape checks grant nothing. Receipt remains provisional until the enclosing durable commit.

Use the existing operation lock/private lookup, then lock the explicitly scoped original capture with ordinary SELECT FOR UPDATE. Stop on existing outcome without disclosing it; later orchestration must authorize its actual stored target. Missing/foreign captures share a safe failure. Validate fresh answers against the stored original published definition. Historical own editing survives unassignment and ordinary child inactivity, so no create eligibility/current assignment/active-child checks apply. Preserve immutable owner, child, version, creation attribution and device timestamp.

Require the reviewed expected revision even for unchanged values. A conflict carries stable `kdg_capture.capture_revision_conflict` and only typed current_revision; wire adaptation remains later. Changed saves conditionally update date/answers and increment once, then atomically append compact outcome and immutable snapshot with verified executor/initiator. Authorized unchanged saves append only their outcome with unchanged revision: no update, fake history or new timestamps. PostgreSQL JSONB/date equality determines no-op, avoiding Python bool/int equivalence. No-op at signed-bigint max remains valid; changed overflow fails safely before mutation.

Synthetic acceptance/TDD must cover changed/no-op writes, original version validation, stale conflict, lock/read ordering and scope, fresh-only duplicate refusal, wrong permission/context/input, absent/foreign target, rollback paths and shared deadlines. Use existing connection doubles and label them as control-flow evidence, not native RLS/concurrency/durable commit proof. Do not change expected tests merely to dismiss unexplained failures.

Preserve concurrent changes, all historical evidence, Docker resources/data and approved dependencies including TypeScript7.0.2. No migrations, provisioning, native fixture writes, cleanup, Leave/editor, real accounts/Access, production, deployment or pilot. Fingerprints/HMAC deferred. Record scaffold/shared-UI/context/docs/ADR impact in this item; promote only a proven reusable neutral fix if needed. Update current contracts/evidence and prepend handoff with historical bytes intact. Routine approval halts are skipped under the user's explicit instruction.

</frozen-after-approval>

## Implementation Notes

bmad-help selects [BD] Build for the explicit next slice in next-session.md. Investigation confirms existing0002 runtime grants/guards and deferred links permit changed and no-op edit receipts; no schema change is needed. Reuse same-silo create query helpers, existing operation outcomes and generated transaction context; never hand-edit managed files. Small reversible code/test/doc footprint, no intent gap or irreversible execution: oneshot. No shared-UI, agent-context or ADR change expected; domain SQL stays KDG-owned and scaffold primitives remain unchanged/parity-checked. Native qualification/HTTP authorization, replay and release remain consuming gates.

## Implementation Notes (completion)

Added inert capture_edit.py, reusing same-silo create query helpers, outcomes and the generated transaction/Budget implementation. Scoped SELECT FOR UPDATE follows the existing-operation lock/lookup. PostgreSQL computes JSONB/date equality. Only date/answers/revision are conditionally updated; history copies immutable facts and edited snapshot from the locked capture with current executor/initiator. No-op appends its compact outcome only. Conflict is an app-owned WriteError subtype with safe current_revision string; current wire error catalog and generated clients remain unchanged pending HTTP adoption. At bigint max changed input fails internal_error before mutation; no-op remains valid.

Scaffold: existing neutral helpers unchanged; three managed code/test parity checks pass. New SQL, conflict behavior and test scenarios are KDG-specific, so no new generic runtime/scaffold pattern. Shared UI, agent context and ADR: no change. Documentation: current contracts, source-bound evidence and prepended handoff updated here; original handoff preserved verbatim as suffix. Dependencies including TypeScript7.0.2 unchanged. No native or Docker execution, and no consumption/edit/run of the preexisting untracked schema_fixture.py.

## Review Triage Log

- Low, patch — original-definition questionnaire-ID mismatch guard lacked coverage. Existing0002 composite FK already binds capture to its original questionnaire/version, and the read queries that exact stored version. Removed the redundant guard and unused projection rather than adding a synthetic impossible-state test. Missing/invalid definition remains a safe failure.
- Medium, patch — canned no-op result did not protect date-only/answers-only bindings against a changed SQL conjunction. Added independent proposals plus exact delegated PostgreSQL conjunction contract; actual native equality remains a qualification gate.
- Medium, patch — history test omitted immutable snapshot projection. Added structured column/projection checks for owner, child/version/device, edited values/revision and current executor/initiator parameters. This protects SQL generation, not native snapshot enforcement.
- Medium, patch — original-definition SELECT was omitted from SQL-failure cases. Injected failure proves safe internal_error, no mutation and transaction error exit.
- Medium, patch — ordering test omitted scoped operation identity. Spy verifies original command/org/account/operation key shared by lock and lookup, with the original Budget/context. All five findings addressed; none deferred.

## Verification

ATDD:17 behavioral tests failed against the explicit pending stub (23 subcase errors); the changed-save acceptance reached the body and failed NotImplementedError before implementation. Focused TDD progressed17→21→23 passing tests. Final affected write suite199 PASS in8.213s; focused23 PASS in0.052s. Three scaffold parity checks PASS. Pinned Python owner environment and Node26.11.1 used; actual TypeScript version7.0.2 confirmed. Deadline failures after each write, missing snapshot, SQL/commit failures, late commit acknowledgement and caller-input mutation are covered. Connection doubles establish adapter/control flow and delegated SQL contracts only; native permissions, contention, commit durability and actual unchanged timestamps require the next consuming qualification. Exact commands, code hashes and retained logs/source capsule are linked from OWN_EDIT_BODY_EVIDENCE.md and its receipt.
