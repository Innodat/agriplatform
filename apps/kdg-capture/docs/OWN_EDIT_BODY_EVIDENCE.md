# Inert own-edit transaction body — 2026-10-25

`write-candidate/capture_edit.py:edit_in_transaction` implements the fresh-action body
for the next own-edit consumer. It creates no engine, route or network client. The
trusted caller must establish current admission/membership, durable actor and current
own-read/own-edit authority, then supply the same verified own_write context and original
Budget installed by write.transaction. Parameter shape checks confer no authority.

After strict path/command revalidation, the body acquires the scoped capture.edit
operation lock and performs private lookup. An existing outcome stops with
operation_verification_unavailable: outer orchestration must later authorize its actual
stored target before replay/disclosure. Fresh input never selects a replay target.

Ordinary scoped SELECT FOR UPDATE locks the current own capture. Missing/foreign records
share capture_unavailable. The supplied expected revision must match even for a no-op;
RevisionConflict carries only the stable kdg_capture.capture_revision_conflict identifier
and a string current_revision. Its eventual409 wire mapping remains unimplemented.
The exact stored questionnaire version supplies answer validation; no latest version,
current assignment/create eligibility or active-child check substitutes for historical
own-edit authority. Existing database foreign keys bind original questionnaire/version.

PostgreSQL JSONB/date equality determines unchanged input, keeping boolean/integer
semantics with PostgreSQL. A changed save conditionally updates only observation date,
answers and revision, then appends the compact outcome and full immutable snapshot in
the existing transaction. Snapshot SQL copies original owner, child/version/device facts
from the capture and uses the verified current executor/initiator. A no-op appends only
its outcome with the unchanged revision: no capture UPDATE, timestamp change or fake
history. No-op at signed-bigint max is valid; changed overflow fails safely before writes.

Receipts are provisional until the outer durable commit. Failures escape and prevent
acknowledgement. Late commit acknowledgement reports execution_timeout without a rollback
claim; the original operation may need recovery. No automatic retry, new operation,
fingerprint/HMAC, replay, conflict UI or saved-state feedback is introduced.

| Requirement | Behavioral evidence in test_capture_edit.py |
|---|---|
| Changed save with linked evidence | Conditional owner/revision UPDATE, outcome/history linkage and snapshot projection |
| Current authorized no-op | Receipt-only write, unchanged revision; original answers still validated |
| Stale input | Safe revision conflict even when proposed values are unchanged |
| Original version/historical editing | Exact stored version query; removed child/assignment/create eligibility does not block own edit |
| Scope/operation identity | Scoped capture predicate, lock before lookup/read, exact original key/Budget/context |
| Partial changes | Date-only/answers-only bindings plus compound PostgreSQL equality contract |
| Safe failures/deadlines | Original-definition/read/write SQL failures, zero update/history count, shared deadline after each write |
| Commit uncertainty/input pinning | Failed/late commit and caller mutation after private revalidation |

ATDD observed17 tests failing against the pending stub (23 subcase errors). Final
**23 focused tests and199 affected tests pass**, plus three scaffold parity checks.
Blind review produced five findings, all addressed: four test gaps closed and a redundant
consistency guard removed in favor of the existing foreign key. None deferred.

This is synthetic control-flow/SQL-generation evidence using existing connection doubles.
It does not establish native RLS, locking/concurrency, atomic rollback/durable commits or
actual no-op timestamp preservation for this new body. Earlier native stored-edit evidence
used fixture SQL and does not qualify this implementation. No native/Docker action occurs
in this delivery. Current-access HTTP coordination, stored-target replay, active startup,
editor/queue/UI, native qualification and ADR-0020 release gates remain separate.

Scaffold: proven neutral helpers reused unchanged and parity-checked; domain SQL stays
KDG-owned. Shared UI, agent context and ADR unchanged; contracts/handoff/evidence updated.
Approved dependencies, TypeScript7.0.2, historical evidence and concurrent work preserved.
Synthetic local/CI only; no Leave/editor, real accounts/Access, production, provisioning,
deployment/pilot or cleanup. See [receipt](evidence/own-edit-body-20261025.json) and
[delivery record](../../../_bmad-output/implementation-artifacts/spec-kdg-own-edit-body.md).
