---
title: 'Qualify KDG linked storage on retained PostgreSQL with rollback'
type: 'feature'
created: '2026-10-24'
status: 'done'
route: 'oneshot'
baseline_commit: '28942b879d33060b77b711b64ec4930eb28b1862'
context:
  - '{project-root}/apps/kdg-capture/AGENTS.md'
---

<frozen-after-approval reason="next authorized synthetic KDG native persistence qualification">

## Intent

Qualify actual PostgreSQL DDL/triggers/FKs/RLS and concrete capture→outcome→history SQL
using only the custody-verified retained fixture in run99b7231c-0a5b-4bdb-98e8-3329564c526a,
port55482, database kdg_schema_659350f762c8494c9241b7b1c8ea9566. Resume that existing stack,
never prepare/provision another fixture or change roles/databases/grants permanently.
Candidate remains outside active versions; ledger remains0001_kdg_foundation. Preserve
all historical evidence/source/resources. No production/real account/access, Leave/editor,
provisioning/deploy/pilot/cleanup, fingerprints/HMAC or dependency/TS7.0.2 changes.

Use the existing transaction helper to own a fresh transaction on a fixture administrator
connection. Inside, SET LOCAL ROLE migrator applies candidate DDL with actual Alembic
Operations; administrator seeds minimal synthetic parents (no app grants/Auth accounts),
then SET LOCAL ROLE runtime exercises concrete SQL and existing outcome adapter. Schema,
seeds and every operation are rolled back with a private sentinel, never COMMIT success.
Force SET CONSTRAINTS ALL IMMEDIATE before declaring a case passed so deferred checks
actually execute. Administrator seeding/role switching is fixture-only test machinery,
not application code or authorization. Report current_user runtime/session_user admin
honestly; do not claim restricted-session role-switch denials from this admin session.

Given a valid synthetic create, capture/outcome/history exist consistently in the same
transaction, stored original receipt resolves and forced constraints pass; rollback
removes every candidate object/row. Given missing/mismatched history, invalid target/
revision/initiator, malformed device time/blank parents, altered immutable facts, foreign
org/account, read-only/missing context, or unauthorized DDL/mutation, actual SQL must
refuse or disclose no rows. No-op edit receipts reference the existing revision without
inventing history. Do not branch on raw database messages or leak credentials/input;
use expected SQLSTATEs and safe case labels. Existing managed SQL helpers stay unchanged
unless native failure proves a reusable defect (then update templates plus adoption/tests).

ATDD first observes candidate storage absent on the old retained fixture. Add focused
behavioral native cases and meaningful offline CLI/error-oracle tests. Run unchanged
SELECT-only historical inspector before and after to verify actual restricted logins,
ledger-only schema/sentinel and preexisting cluster metadata. Native result is source-
bound to exact candidate/harness/helper plus fresh private report; do not relabel old proof.
Normal stop retains the resumed stack's data/resources. Refuse unknown custody/state;
never repair/reset/recreate a missing fixture or automatically retry lifecycle failures.

This bounded rollback qualification proves actual PostgreSQL execution, role-scoped
privileges/RLS, linkage/triggers and transactional rollback. It does not qualify durable
COMMIT acknowledgements, cross-connection replay/uniqueness races, current Access HTTP
or production owner orchestration. Concrete protected writers/committed concurrency and
ADR-0020 previous-code/migration coordination/failure blocking/recovery remain required
before migration promotion or any release activation.

</frozen-after-approval>

## Implementation Notes

bmad-help [BD] selects rollback-only native qualification after completed linked schema
candidate. Small reversible test harness plus focused tests and owner evidence; no
persistent schema/data mutation or irreversible operation. Existing fixture custody and
historical explicit run exception support resumption, not new provisioning. oneshot.

Scaffold: no new pattern; schema/domain scenarios remain KDG-owned, existing neutral
transaction/migration controls reused unchanged. Shared UI: none. Agent context: existing
instructions suffice. Docs: native evidence/current handoff/migration guide, exact
historical content preserved. ADR: no new decision. Baseline snapshot is retained at
/tmp/kdg-native-storage-before.json. Concurrent work is excluded from this delivery.


Investigation refinement: the historical inspector's old cluster-wide metadata hash no
longer matches. It was attempted without edits and remains a recorded failure, not
relabeled proof. Fresh read-only exact fixture/role/ledger/sentinel/privilege checks
establish current identity, then current before/after metadata preservation is verified.
The historical cause remains unresolved; no baseline was overwritten or state repaired.
This supports only the reversible rollback qualification, not migration promotion.

ATDD observed actual42P01 missing capture storage on the old fixture. Native qualification
then executed the candidate inside rollback transactions. Focused TDD first exposed
wrapped WriteError handling in the SQLSTATE oracle and a negative fixture constructing
invalid VerifiedContext before SQL. Both regressions passed after test-only corrections;
production helpers/error behavior remain unchanged. Optimized execution is refused before
I/O; the refusal initially came from historical inspector import and is now contained by
the explicit qualifier boundary before that import.

## Review Triage Log

1. **medium — patch:** invalid-hour test could pass from deferred missing-history23514.
   Added immediate-phase requirement so a later deferred failure cannot satisfy it;
   focused regression first failed before the oracle gained that distinction.
2. **medium — patch:** provenance/fabricated-history tests accepted undifferentiated23514.
   Added immediate-phase assertions plus a valid changed-edit control, isolating intended
   history guards from missing snapshot or blanket edit rejection.
3. **medium — patch:** no successful changed edit was qualified. Added parsed/validated
   date+answer revision2 update, exact original operation/receipt/history readback and
   forced constraints, then rollback its savepoint before independent negative cases.
4. **medium — patch:** creation only checked receipt, not persisted input. Added exact
   capture/history date, answers, original device string, account/actor/operation/outcome
   comparisons to parsed command and verified fixture context. Operation identity stays
   bound to the original parsed create/edit commands.
5. **medium — patch:** old inspector's earlier global hash failure skipped later ledger
   ACL proof. Fresh restricted-login checks now explicitly deny all ledger privileges
   for runtime/operator, independently of historical inspector outcome.
6. **medium — patch:** unexpected body failure skipped post-run inspection. Added an
   unconditional independent inspection attempt after disposal, preserves original error,
   and reports rollback_verified accurately. Focused failed-body test first saw only one
   inspection; it now sees both. Added failed-inspection case proving original error is
   retained with rollback_verified false rather than inventing restoration.
7. **low — patch:** source binding omitted custody/inspection dependencies. Private report
   now includes native_fixture.py and inspect_native.py along with actual owner modules.
8. **medium — patch:** independent table policies lacked seeded isolation checks. Added
   forbidden other-account assignment, history/eligibility counts under own/all modes,
   and foreign-org/missing-mode checks across all eight populated domain tables.

No finding deferred. Final45 focused offline tests pass; final27 native cases pass with
exact source binding and actual rollback. Durable commit/cross-connection races/current
Access and release activation remain unqualified. Existing source/schema/managed copies,
historical reports and dependency baseline remain unchanged outside this delivery.


Final stop returned completed/ok for the exact resumed run, preserving retained data and
resources. Current source hashes match the final27-case private native report.228 tracked
KDG/template/dependency files outside scope remain byte-identical;104 preexisting dirty/
untracked paths remain present, and previous handoff is an exact suffix. No active
migration/API/release, native fixture preparer, reset or cleanup was executed.
