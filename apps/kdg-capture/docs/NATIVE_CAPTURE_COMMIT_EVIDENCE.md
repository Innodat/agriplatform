# Restricted-runtime durable create qualification — 2026-10-25

The actual unmounted create/retry handler now passes durable PostgreSQL qualification
on the explicitly approved retained synthetic KDG fixture. Ordinary restricted-migrator
Alembic upgraded its ledger from `0001_kdg_foundation` to
`0002_kdg_capture_storage`. Two qualification datasets, each with five committed synthetic capture/outcome/history
triplets, and their supporting parents and private append-only receipts remain retained. The known run
was stopped normally afterward. No application handler or shared helper needed a fix.

The target is exactly run `99b7231c-0a5b-4bdb-98e8-3329564c526a`, localhost port 55482,
database `kdg_schema_659350f762c8494c9241b7b1c8ea9566`, existing KDG roles and fixture
`platform/deployment/.local/kdg-native-focused-20261023/fixture-cff53592f5ca43a1a0cc65398957140f/fixture.json`.
Credentials remain under the original custody adapter and never enter this document.
Read [the source-bound receipt](evidence/native-capture-commit-20261025.json).

## Execution and durable effects

`migrations/tests/capture_commit_fixture.py` validates the original private custody,
exact target and restricted identities. Its test-only Alembic configuration combines
`versions` and `candidates`. Before connecting or migrating, the qualifier requires exactly
one test head 0002 and its exact parent 0001. It uses the existing env, command policy,
owner lock and restricted migrator for ordinary `upgrade head`; there is no stamp,
DDL bypass, active configuration edit or candidate promotion. Active discovery still
has head 0001. Before upgrading, the actual runtime handler with MockTransport Access
failed at missing storage with native SQLSTATE 42P01, rolled back and left ledger 0001.

Migration and qualification require separate explicit CLI flags. A migration failure
records its phase and observed revision and blocks qualification. Explicit retry first
reconnects to reconcile the real revision; it never automatically reverses applied DDL.
A latest failed/missing migration receipt blocks qualification even if a 0002 ledger is
present. The applied candidate hash must match a prior successful actual-upgrade receipt
bound to this fixture; existing-head reconciliation cannot mint that provenance. The successful migration receipt is a new transition record; original receipts
and the unresolved historical metadata-hash discrepancy were preserved.

The fixture administrator seeds only synthetic KDG parents: one questionnaire, published
version, child, assignment and eligibility observation. It creates no Identity/Auth,
application admission or Access grant. A private qualification-start receipt records all
synthetic parent identities, selected command operation/capture IDs, attempt identity and
sources before the first seed write. Final success/failure links to that start receipt
and retains completed-case evidence. Runtime sessions
use actual `kdg_capture_runtime` login/session identity; no administrator role switch
executes the handler. The migrator and operator identities are separately checked.

Each qualification run committed five captures, five compact outcomes and five immutable
revisions. Ten of each now remain across the two retained datasets.
The first writer in one race inserted all three records, then hit a real native
constraint failure: its transaction rolled back while the waiting valid writer committed.
A different-operation/shared-capture loser rolled back without an orphan outcome/history.
Only the fixture assignment was later deactivated, under the child coordination lock,
to prove current stored-child authority. These recorded synthetic rows and complete
candidate tables, RLS, constraints, triggers, grants and ledger 0002 remain in the fixture.
No database, schema or role was provisioned, no broader privilege granted, and no prior
resources, data or historical evidence was cleaned up.

## Acceptance traceability

All eight native groups ran and passed; these are actual restricted connections and
commits, with Access responses supplied exclusively by `httpx.MockTransport`.

| Requirement | Passing native group / observation |
| --- | --- |
| Absent storage fails without writes; verified 0001 upgrades through existing policy | Migration preflight 42P01; ordinary restricted Alembic transition 0001→0002 |
| Fresh closed writer is visible independently with owner, actor, pinned version, attribution and linked history/outcome | `fresh_commit_independent_restricted_triplet` |
| Discard delivery and retry changed target/body: original receipt, no duplicate effects | `discarded_delivery_changed_body_original_receipt` |
| Concurrent identical/different bodies: first committed request wins | `overlapping_duplicate_identical_body`, `overlapping_duplicate_different_body` |
| Bounded contention recovers on explicit retry | Identical-body race deliberately exceeds the second request's two-second lock cap; it observes `operation_busy`, then reauthorizes and recovers the first receipt |
| Native failure after inserts rolls back and waiting valid writer commits | `native_failure_after_inserts_waiter_commits` |
| Different operation IDs sharing a capture ID leave one triplet and no orphan receipt | `different_operations_shared_capture_safe_loser` |
| Replay checks stored child and current membership/assignment despite unusable incoming child/answers/eligibility | `assigned_replay_current_stored_child_membership`; membership mismatch and inactive stored assignment both deny |
| Foreign organization/account invisible; runtime DDL, ledger and privileged role switches denied | `foreign_scope_ddl_ledger_role_switch_denied`; SQLSTATE 42501 for privilege refusals |

Each concurrent case uses bounded barriers after the first writer's inserts and before
the second writer's contended SQL. A separate runtime connection observes the second
backend's `pg_stat_activity.wait_event_type = Lock` before releasing the first writer.
This establishes overlap rather than inferring it from thread timing. Context variables
carry writer identity into the handler's AnyIO worker. Every MockTransport callback checks
that its owned connection has no transaction; HTTP never runs under business locks.
Fresh restricted read sessions verify exact counts and linked owner/actor/version/input
snapshots after the writer closes. A final independent reconnect confirms five triplets in the final dataset and ten across
both retained datasets,
head 0002, matching source bindings and the foreign sentinel. Current before/after metadata
digests agree; this does not resolve the earlier global-hash mismatch.

## Commands and offline verification

From repository root, P is
`platform/deployment/.local/access-organization-check-20261022/owner-env/bin/python`.
N is
`platform/deployment/.local/kdg-toolchains/ad277eef-a10e-4aac-bb82-5743653fb2e0/payload/node/bin/node`.

```sh
timeout 45s "$P" -I -B -m unittest discover -s apps/kdg-capture/write-tests -p 'test_*.py'
"$P" -I -B -m unittest discover -s apps/kdg-capture/write-tests -p test_capture_commit_qualification.py
"$N" platform/builder-cli/scripts/sync-kdg-write.mjs --check
timeout 60s "$P" -I -B apps/kdg-capture/migrations/tests/qualify_capture_commit.py --migrate-retained
timeout 60s "$P" -I -B apps/kdg-capture/migrations/tests/qualify_capture_commit.py --qualify-retained
```

The initial acceptance test failed because the qualifier did not exist. Final focused
harness tests: 21 pass. Complete affected write suite: 101 pass, 2.353s. Offline tests cover
exact graph isolation/refusal, explicit separate phases, failure reporting/redaction,
qualification blocking, pre-seed intent journaling, the actual missing-table oracle,
wrong-triplet-count rejection, complete stored-field comparisons, alternate/failed target
absence, final per-dataset counts and candidate-bound migration provenance. Existing
handler deadline/admission/cancellation and fresh-body regressions also pass. Scaffold
write parity `--check` passes; generated copies/templates are unchanged. A sandboxed
worker run stalled and was interrupted; the bounded unsandboxed suite passed. No test
failure expectation was changed to dismiss an unexplained failure.

Known-run lifecycle used `python3 platform/deployment/dev.py up` and `stop`, both with
`--target platform/deployment/environments/kdg-local.json`, the exact run ID above and
`--supabase` pointing to the absolute pinned toolchain path ending
`/payload/supabase/supabase`. Subprocess diagnostics were captured rather than printed.
Both operations succeeded. No preparer, reset, cleanup or downgrade ran. An initial
ad hoc SELECT-only final inspection incorrectly created its context before its Budget;
the existing freshness guard refused it without business writes. Corrected budget/context
ordering passed the independent inspection; this was a qualification setup error.

## Fixture transition and remaining gates

This fixture is deliberately 0002 although active migration discovery remains0001.
Old ledger-only inspectors and rollback qualifiers describe their historical source
and cannot run against this transitioned fixture; do not rewrite them, invoke old
preparers or attempt to restore a ledger-only baseline. Resume only the known retained
run and use the new custody/phase adapter. Successful migration/data stay retained even
if a later qualification fails; reconcile revision/effects before explicit retry.

This proves synthetic durable create/retry and native concurrency through the unmounted
handler. Real Access/capability registration, API mounting, connection acquisition,
request/header/body/error adaptation, private/no-store behavior, native cancellation
under commit uncertainty, GET own-read recovery and release activation remain separate
gates. The existing synthetic cancellation/deadline safeguards are preserved. ADR-0020
previous-version compatibility, coordinated migration failure blocking and explicit
recovery remain required before an actual release; no production backup/recovery or
activation readiness is claimed. Fingerprints/HMAC remain deferred; bootstrap unchanged.

Scaffold impact: existing write helper parity verified, no reproduced generic defect
and no template change. Shared UI: none. Agent context: none. Documentation: this evidence,
receipt, migration README and session handoff. ADR: no new decision or accepted ADR edit.
No dependency install/lock change, TypeScript 7.0.2 change, Leave/editor, real account,
production, provisioning/deployment or pilot action. Concurrent work remains preserved.

## Review fixes and final rerun

All nine findings were addressed in the qualification harness/tests/evidence. No schema,
handler, dependency or shared-helper change was required. Failure recording keeps the
observed revision (including unavailable reconnect), original exception and one detailed
receipt reference. Source inventories include executing custody/models/migration inputs.
Explicit assertions now cover alternate capture/history absence, failed-writer history,
waiting-operation linkage, original child/questionnaire/date/eligibility/membership,
history command/revision and final five/five/five counts before qualification success.
The reviewer rechecked migration provenance and failure recording and confirmed the fixes.

Final explicit migration phase reconciled 0002 against the original successful upgrade;
it applied no additional DDL. The corrected-source native qualification then passed all
eight groups in a separately journaled dataset. SELECT-only independent inspection
confirmed both retained datasets, sources, provenance, roles and foreign sentinel.
All three scaffold sync checks pass. The known run was stopped normally again.

One initially unmocked focused-test failure appended only a private failure receipt;
no database operation occurred. Its missing mock was corrected and the receipt retained.
The public receipt preserves the entire initial checkpoint and references both native
runs rather than rewriting earlier proof or removing earlier synthetic data.
