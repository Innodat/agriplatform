# Online organization capture reads — 2026-10-26

This technical API subset of approved Story 3.1 adds a separately constructed,
unmounted administrator detail/history candidate. Qualification and independent review pass. It does not complete the portal, audit presentation or Story 3.1.

`GET /api/v1/admin/captures/{capture_id}` and `GET /api/v1/admin/captures` independently
require current configured-organization `kdg_capture.capture.read.all`. Verified account,
durable actor, membership and exact authorization/resource scope precede checkout.
Denied all-read never falls back to own-read. Existing own routes retain their original
owner predicate, offline observation contract and response behavior.

Detail retains the existing complete original-definition/provenance DTO. History uses
a separate closed envelope with verified organization/account, explicit inclusive dates,
limit, items and nullable continuation. It contains no offline observation or expiry.
Default limit is 30, maximum 100. Descending immutable creation-time/ID navigation uses
the existing canonical bounded cursor pattern, bound to current caller, organization,
all-read capability, dates and limit. Cursors are navigation rather than authority;
queries independently constrain organization and dates. Own/all cursors are incompatible.
Actual UTF8 detail/page limits remain 512 KiB/2 MiB, with continuation after the last
included item. Pages do not establish a cross-request snapshot or deletion evidence.

Existing transaction context and selected database policy source already recognize
`all_read`; no migration or schema change is introduced. The candidate uses the existing
read-only engine, short transactions, current Access check, one-second SQL-entry
freshness and ten-second total execution budget. Cancellation retains worker connection
ownership through unwind; release/serialization completion remain inside that budget.
Responses and errors are private/no-store and use existing safe identifiers.

An importable non-dispatching stub first returned 404 for an authorized cross-owner
request expected to return 200. Exact stub/test/log evidence remains private. Shared
helper extraction preserves strict own wrappers. A missing stored owner field retains
its original safe unavailable error rather than becoming a missing-record response.
The restricted runner stalled in unchanged worker tests; the same synthetic tests pass
with the required execution permissions, without a runtime or dependency workaround.

The first parent loopback proof passes 37 checks using actual candidate routes and
transport with synthetic Access and recorded storage. It traverses both owners' tied
records, excludes foreign organizations/dates, rejects cross-mode/caller cursors, proves
role loss before checkout without own fallback, checks durable provenance and strict
wire failures, and verifies balanced connections plus unchanged records/outcomes/history.
Normal owned fixture shutdown is verified. This establishes control flow and contracts,
not actual SQL filtering, database permissions, driver rollback or live authority.

Impacts: KDG-specific permission, record and questionnaire semantics stay local. The
existing Auth/transaction/IDB scaffold primitives remain adopted; five parity checks
are required. No demonstrated neutral defect calls for template changes. Shared UI,
agent context and accepted ADRs are unchanged; contract/types, handoff and evidence
are updated together. Actor names, audit events, portal/session presentation, native
permissions and controlled activation remain separate consuming work.

Synthetic local/CI only. Preserve concurrent work, historical evidence/resources and
TypeScript 7.0.2. No UI/editor/Leave, active startup/browser/worker/sender/queue integration,
real accounts/Auth/Access, native PostgreSQL/Docker, provisioning/migrations, deployment,
production/pilot or cleanup. Fingerprints/HMAC remain deferred. The prohibited preexisting
untracked migration fixture is not read, run, copied or hashed.

Final qualification passes 33 commands on one unchanged 277-source map: 377 synthetic
backend tests (342 existing plus 35 admin), 127 direct client tests, the 37-check loopback
proof and eight affected HTTP proofs. Eight OpenAPI exports/eight generated clients
are current; strict TypeScript 7.0.2 and all five scaffold parities pass. Twelve earlier
browser/store proofs have unchanged complete effective-source hashes and are reused.
All 182 protected historical/dependency files remain unchanged. The injected ten-second
harness stall exits with recorded failure and normal owned fixture shutdown in 10.43
seconds. Exact commands, result/source references and requirement mapping are in the
[machine record](evidence/online-admin-read-20261026.json). Review addresses seven findings, rejects three low-impact refinements and defers actual native SQL qualification before activation.

Review corrections keep new detail validation outside the SELECT transaction and prove
inactive/unassigned historical reads, exact business-query clauses, typed error wires and
pre-checkout cancellation. The raw request shares the proof deadline; a controlled pending
response aborts at 10.69 seconds with normal owned shutdown (the prior raw request took
16.33 seconds). The earlier 10.43 second forced-stall result is historical qualification of
the prepatch harness.

One final regression attempt exposed a preexisting history fixture that expired its 60 ms
budget before the intended SQL phase. A controlled 80 ms authorization delay reproduced that
failure. The corrected fixture expires the unchanged application budget after reaching each
selected borrow/SQL/release phase, preserving timeout, repeated cancellation, worker
ownership and exactly-one-release assertions. The same delayed characterization and final
377-test suite pass. Exact failed/passing logs are retained in the machine evidence; no
expected application result or production deadline changed.
