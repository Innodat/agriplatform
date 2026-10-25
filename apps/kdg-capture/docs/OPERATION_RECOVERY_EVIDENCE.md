# Own-read operation recovery — 2026-10-25

The unmounted `write-candidate/operation_recovery.py` consumes the existing private
outcome adapter and managed transaction helper. Its current Access check requires
`kdg_capture.capture.read.own`, verified account/durable actor, organization membership,
own-account scope and fresh bounded evidence before SQL. It shares the existing
protected Access transport and cancellation-safe worker with create orchestration;
create defaults and transaction behavior are unchanged and regression-tested.

| Requirement | Evidence |
| --- | --- |
| Original create receipt after create/assignment loss; no child checks or locks | `test_recovers_original_receipt_using_only_current_own_read`; native original-create case with inactive assignment |
| Original edit revision, without current-revision substitution | `test_edit_returns_recorded_revision_without_current_revision_substitution` (synthetic only) |
| Exact scoped/discriminated lookup and verified absence | Compact-unresolved acceptance; native unknown/type/account/org cases |
| Actual stored owner authorization; corrupt/unsupported outcome refusal | Missing/foreign target and unsupported/foreign outcome tests |
| Current access, durable actor, admission and scope | Access denial/bad-evidence tests; native denial |
| No false unresolved on read/transaction failure or deadline | Statement-error, commit-error, late-unresolved and late-committed tests |
| Bounded worker admission, observation freshness, connection retention | Saturated limiter, cleanup-delay and repeated-cancellation tests |

ATDD first observed a missing module, then 11 explicit behavioral failures against a
stub, before implementation. Final `unittest discover` passes **117 tests**, including
**16 recovery tests**; 23 create handler tests also passed before the reuse refactor.
No expected assertion was weakened to dismiss a failure. Three generated code/test
parity checks pass. Blind review raised five issues; all were checked and fixed in
this item, including the preliminary native qualifier's budget/observation ordering.
See the [delivery notes and individual triage](../../../_bmad-output/implementation-artifacts/spec-kdg-operation-recovery.md).

Native qualification is a dedicated SELECT-only executable on the same retained
fixture/database/run, with actual runtime login and PostgreSQL read-only transactions.
It consumes historical create identifiers and existing applied-candidate provenance;
it does not rerun migration, seeding or durable-write qualification. Six native cases
pass. Counts before/after remain capture10 / outcome10 / history10, revision0002 and
foreign sentinel intact. First failed own-read receipt is retained; corrected receipt
is `capture-commit-own-read-cbd2b630b5e74ccb906430f8b86d3ec3.json`. Read-only mode is
checked before and after. Known run was resumed and stopped normally; no resource
cleanup. Historical source receipts are unchanged, including the old metadata-hash
discrepancy. This delivery makes no new cluster-wide metadata-inventory claim.

Committed edit recovery has synthetic coverage only: no existing edit outcome is in
the retained fixture. MockTransport is synthetic Access, not live authority evidence.
No API route is mounted, active migration promoted, or release approved. Future HTTP
embedding owns bounded connection acquisition, validated single-valued query/headers,
no-store responses and safe error adaptation. ADR-0020 release compatibility/recovery,
real Access and native cancellation/commit uncertainty remain separate gates.

Reusable impact: existing generated transaction code/tests are reused unchanged and
parity-checked. Outcome disclosure is KDG policy; a new universal recovery framework or
scaffold is unwarranted. No shared UI, agent-context or ADR change; contracts and handoff
updated here. Approved dependencies and TypeScript7.0.2 are unchanged. Fingerprints/HMAC
remain deferred; no Leave/editor, production, real-account/access, provisioning,
deployment/pilot or cleanup work.

Exact commands, source digests and retained report references are in the
[source-bound receipt](evidence/operation-recovery-20261025.json).
