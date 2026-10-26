# Online administrator conditional edit and recovery — 2026-10-27

The inert PUT `/api/v1/admin/captures/{capture_id}` and GET
`/api/v1/admin/operations/{operation_id}?command_type=capture.edit` implement the
backend Save/recovery portion of approved Story 3.2. Qualification and review are complete. The implementation uses existing commands, receipts, safe conflict metadata,
short transaction helper and executor-private storage; no schema change or activation.

PUT checks current organization read.all then edit.all, matching verified account,
durable actor and membership before checkout. First-read freshness, one three-second
pair cap and original ten-second total remain binding. Actual administrator all_write
updates date/answers under the original immutable questionnaire and matching revision.
Original owner, child, creation/device provenance stay fixed; immutable evidence records
the actual executor/initiator. Capture, receipt and history commit together. No-op adds
only a receipt; stale proposals, including stale no-ops, cannot overwrite current state.

Recovery needs current read.all and its separate read-only engine, even after edit.all
loss. Lookup remains organization/current-executor/command/operation private. Replay
and recovery authorize the stored target; changed retry path/body and later revisions
cannot substitute another effect or receipt. Absence returns unresolved without proving
noncommit. Stored-target failure is unavailable, never a receipt or absence claim.
No own/admin save-surface discriminator is inferred from existing receipt storage.
All responses/errors remain private/no-store. Final serialization is checked before a
timely-success response; release failure can leave a committed uncertain action whose
original receipt must be recovered before another write.

Actual loopback missing-route RED returned405 where200 was expected before implementation.
The retained positive proof exercises administrator/facilitator both orders, repeated
conflicts, reviewed replacement, overlapping requests, no-op, changed retry, read-only
recovery after edit loss, private executor/org isolation and synthetic rollback/failure
paths. Its storage is recorded Python state, not PostgreSQL; overlapping HTTP requests
do not establish database locks, RLS, driver cancellation or rollback. Fixture scores
were corrected to the existing 1–5 wire bound after an initial422; expected target404 and
rollback expectations were unchanged. Owned fixture shutdown is confirmed.

Scaffold: five adopted neutral code/test parities remain required; no new domain-neutral
mechanism is introduced. Shared UI/context and accepted ADRs unchanged. KDG all-edit SQL
and permission/record semantics stay local. Contract/types/tests/docs update together.
Native SQL/RLS/release, mounted online Save/Cancel/comparison, account/session rendering,
accessibility/device proof and historical Identity names remain outstanding. This does
not complete Story 3.1/3.2 or authorize migration promotion/startup.

Synthetic local/CI only; preserve concurrent work, historical evidence/resources and
TypeScript 7.0.2. No real accounts/services, native DB/Docker, provisioning, deployment,
production/pilot, installs/dependency changes or cleanup. Fingerprints/HMAC deferred.
Exact qualification commands, source hashes and traceability are recorded in the
[machine evidence](evidence/online-admin-edit-20261027.json).

Final qualification passes ten commands on one unchanged 322-source map: 185 focused
backend tests (47 new), 60 actual loopback checks, owner export/client freshness, strict
TypeScript 7.0.2 and five scaffold parities. All 307 prior implementation sources and 191
protected files remain unchanged; 23 prior proofs retain complete effective-source equality.
The strengthened loopback proof interrupts a response body after commit, recovers its
original receipt without another write, and submits competing same-executor/operation
requests against different targets with one effect and identical receipts. It checks
exact safe error IDs, a foreign-org private outcome, type-aware synthetic JSON equality,
final engine disposal and unchanged storage after the final response. Expected watchdog
failure still stops the owned fixture normally.

All three review layers completed before triage. Twelve individual findings were
addressed (two report the same disposal root cause), one false inherited-mode claim was
rejected, and none deferred. The direct corrections map stored-target SQL verification
failure to its existing 503 identifier and attempt both distinct engine disposals when
the first fails. Two focused failures were observed before correcting them. Recovery
SQL/commit/release, stale checkout and new PUT stream deadline have focused tests. The
stream test uses actual yielded body chunks; an in-memory mutation removing that check
fails consumption bounds, while unchanged production passes. Runtime capacity required
reuse of an available reviewer from an unrelated earlier delivery and parent application
of direct patches when the original implementation child could not resume; exact details
and evidence references are retained in machine/private review records.

The next E3 qualification boundary is native SQL/RLS/driver and the mounted online
portal/session/device work, which are excluded from this synthetic API delivery.
Historical actor-name display still needs an Identity-owned authorized HTTP contract.
No claim that the complete administrator workflow is ready for release follows.
