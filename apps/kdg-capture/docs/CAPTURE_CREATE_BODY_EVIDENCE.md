# KDG fresh capture transaction body — 2026-10-24

bmad-help selected the concrete owner write after native storage qualification.
`write-candidate/capture_create.py` now owns fresh-create SQL and consumes the existing
input models, original questionnaire validator, bounded transaction helper and outcome
adapter. The native qualifier calls this body rather than fixture-only create SQL.
It is a callable candidate, without a mounted API or active migration.

## Consuming contract

The owner verifies current organization admission, account, durable actor, membership
instance and exact `kdg_capture.capture.create.assigned` or `.all` through the existing
protected HTTP contracts before taking local locks. Both capabilities return
`own_account`: install `own_write`, never `all_write`. The body accepts the exact current
membership decimal ID and capability as backend evidence, not browser credentials or
an authorization verifier. Use `capture_create.write` for the same helper identity.
Create the original Budget before external checks and retain it through execution.

Inside `write.transaction(connection,budget,verified_context)`, call
`create_in_transaction(..., command, membership_id=..., permission=...)`. Let failures
escape so the caller rolls back; never catch a body failure and commit partial effects.
The returned receipt is PRIVATE and provisional until that enclosing transaction has
committed within the budget. This module does not send an HTTP acknowledgement.

The body takes the scoped operation lock, privately rechecks absence, then takes the
organization/child coordination lock. Existing outcomes raise
`operation_verification_unavailable` on this fresh-only boundary before incoming domain
semantics; the consuming handler must separately authorize the actual stored capture
and recover its original receipt. This deliberate internal stop is not the final POST
retry/recovery behavior. No incoming target, definition or eligibility authorizes replay.

Capture and operation UUIDs must be distinct, checked before locks.
Current local checks bind org/account/child and current membership to issued eligibility.
Historical observed-active evidence permits ordinary inactivity; historical child or
assignment revisions need not equal current revisions. No expiry or phone timing proof
is invented. Current assigned-create independently requires a current active assignment
for that exact membership instance; all-create needs no assignment and stays own-author.
Historical create permission supplies no current authority: historical all → current
assigned still checks assignment, and historical assigned → current all still needs
current all permission. This follows the contracts' separate historical evidence/current
authority rules; neither historical permission nor revision is a renewed grant.

The referenced immutable published definition is selected by exact original version,
never latest. Required answers, false values, optional details and exact device timestamp
use the existing validators. Plain inserts write capture, outcome, then linked revision;
server attribution and existing deferred integrity guards stay in force. Safe failures
include assignment_unavailable, child_eligibility_unavailable,
questionnaire_version_unavailable, validation_failed, execution_timeout and generic
internal_error. These are internal identifiers; the future HTTP adapter must use the
established machine-readable error envelope and compatible status mapping.

## Coordination and release limits

`child_lock` uses PostgreSQL transaction advisory locking on
`hashtextextended('kdg_capture:child:v1:' || org_id || ':' || child_id,0)`.
This is coordination identity, not a command fingerprint/HMAC. Every future KDG child
or assignment mutation command MUST acquire this same lock before reading/mutating,
after its operation lock, and hold it until transaction end. This avoids granting parent
UPDATE permissions just to take SELECT row locks. Collisions only serialize unrelated
work. It coordinates participating owner commands; arbitrary alternate SQL is not
serialized by this convention. No production mutation workflow is activated here.
Qualifier-only administrator mutations model participation before changing test state.

Original managed shrinking deadlines cap SQL/locks; a real second restricted connection
holding a synthetic child key produces bounded 55P03, mapped to safe internal_error.
This is advisory-wait evidence, not committed candidate-table cross-session visibility.
The runtime role executes candidate tables inside an administrator session, as in the
previous native proof. Restricted login identity/privilege checks remain separate.

Candidate remains outside active versions; head 0001 and schema ledger are preserved.
Durable commit/lost-response, committed duplicate/concurrent creation, current protected
HTTP evidence and stored-target replay qualification remain required. Parent mutation
commands must consume the lock before activation. ADR-0020 coordinated controlled
migrations, previous-version compatibility, activation blocked on migration failure and
explicit recovery evidence remain gates. No startup migrations or automatic reversal.
Historical global metadata-hash discrepancy remains unresolved and is not overwritten.
Fresh before/after fixture/role/ledger/sentinel checks establish this run's preservation.

## Behavioral ATDD and focused TDD

Initial missing-body acceptance failed at import. With the first body in place, the
removed-assignment acceptance failed because no refusal occurred and three inserts were
observed. Adding current assignment/member checks made that behavior pass. Focused cases
cover membership rejoin, inactive child compatibility, current all without assignment,
missing/foreign eligibility, original definition failures, absence-before-semantics,
lock order, own-author scope, safe rollback exit and late fetch. The fake connection
records calls only; it does not prove native rollback or RLS.

P is the retained
`platform/deployment/.local/access-organization-check-20261022/owner-env/bin/python`.
The final write suite has 57 passing tests, including 12 fresh-create behavioral cases.
The native suite has 43 passing cases: two published definitions with different question
IDs retain the selected older version; historical all/current assigned needs assignment,
historical assigned/current all works without active assignment; another-child reference
fails independently of account/member matching. Actual capture and outcome inserts are
observed before injected native history constraint 23514; savepoint rollback restores all
three tables to baseline. The second connection's rollback releases the advisory lock,
and subsequent acquisition succeeds. Final outer rollback restores ledger-only schema.

Review found the distinct-ID omission; its regression first failed, then passed after
adding the guard. All seven review findings were addressed, including the receipt and
missing evidence cases. One expanded native test initially missed required child seed
fields (23502); its failed run verified rollback. Correcting the fixture fields produced
the passing run without changing application policy or expected behavior.

Exact commands/results and native report/source hashes are in
[the receipt](evidence/capture-create-body-20261024.json).

- `P -I -B -m unittest discover -s apps/kdg-capture/write-tests -p 'test_*.py'`
- `P -I -B apps/kdg-capture/migrations/tests/qualify_capture_storage.py --run`
- Retained Node: `platform/builder-cli/scripts/sync-kdg-write.mjs --check`

Only the existing synthetic run 99b7231c-0a5b-4bdb-98e8-3329564c526a was resumed;
no fixture prepare, persistent migration/data, reset/prune, account/grant provisioning,
production, deployment or cleanup. Existing normal stop preserves resources.

## Reusable impact decisions

The shared bounded helper and scaffold copies remain unchanged and parity is checked.
Capture SQL, local eligibility and questionnaire semantics stay KDG-owned; promoting
these would couple application silos. No UI change or new generic agent instruction.
Existing accepted ADRs cover this boundary; no new ADR or duplicate architecture.
Dependency manifests/locks and TypeScript 7.0.2 remain unchanged. Prior evidence files
are historical immutable receipts; the next-session handoff prepends a new checkpoint.
