# Online administrator edit context — 2026-10-26

The inert candidate `GET /api/v1/admin/captures/{capture_id}/edit-context` implements
only Story 3.2 AC-1's backend read subset. Qualification and independent review are complete. It does not authorize administrator Save/conflict/recovery implementation,
resolve historical actor names or complete Story 3.1/3.2.

Every request checks current configured-organization read.all then edit.all under one
three-second Access-pair deadline. Both decisions require exact organization scopes,
verified account/durable actor/membership, and matching identity across the pair. Denial
never falls back to own capabilities. No connection is checked out until both pass.
The first check's original monotonic observation must remain one-second fresh at SQL
entry; the second check and checkout cannot renew it. One original ten-second execution
budget covers streaming, checks, acquisition, transaction, release and final response.

The closed response contains only the original complete CaptureDetail and exact editable
fields observation_date/answers. The original child, owner/actor, creation provenance,
questionnaire/version and displayed revision remain intact. Current administrator and
original owner may differ. Inactive children and removed assignments do not veto
historical correction context. No read/edit observation, expiry, offline lease, receipt,
command or reusable authority is returned. Future writes must recheck their own authority.

Reuse the existing independently scoped administrator detail SELECT under all_read,
with its 512 KiB detail bound, validation after commit and read-only engine. The whole
context has a 544 KiB actual UTF8 fence. Cancellation retains worker ownership through
unwind; release/serialization failures cannot publish a late success. All responses
and safe errors remain private/no-store. No business record, event or receipt is written.

A missing-route actual-loopback request first returned404 where acceptance expected200;
its exact private driver, source-bound result and failure log are retained with confirmed
normal owned fixture shutdown. Independent ASGI RED is retained too. Positive loopback
uses actual API/transport with synthetic Access and recorded storage; it does not prove
native SQL filtering/RLS, driver rollback or live current identity.

Scaffold: permission-pair/record semantics stay KDG-specific; the five adopted neutral
code/test parity checks remain required. No new neutral mechanism is demonstrated.
Shared UI, agent context, schema and accepted ADRs are unchanged. Contract, generated
client, tests, docs and evidence are updated together. All-edit command/conflict/outcome
contracts, mounted portal/session behavior, native qualification and controlled activation
remain separate work.

Synthetic local/CI only. Preserve concurrent changes, historical evidence/resources
and TypeScript 7.0.2. No UI/editor/Leave, active startup/browser/sender/queue/worker
integration, real accounts/services, native PostgreSQL/Docker, provisioning/migration
execution, installs/dependency changes, deployment/production/pilot or cleanup.
Fingerprints/HMAC remain deferred. The prohibited untracked migration fixture is never
read, run, copied or hashed.

Final qualification: ten commands, 92 focused backend tests (22 new), 52 actual
HTTP checks, owner export/generated freshness, strict TypeScript 7.0.2 and five adopted
scaffold parities. All 292 prior sources and 188 protected files remain unchanged; 22
prior HTTP/browser/store proofs retain full effective-source equality. The proof checks
received wire bytes and final lifespan disposal, balanced connections and unchanged
storage. The watchdog negative records expected failure with normal owned shutdown.

All three independent review layers completed. Eight direct verification corrections
were made; one low duplicate-coverage suggestion was rejected. One pre-existing low
issue with explicitly injected closing test transports is recorded for the common handler
owner; default HTTP transport ownership is unaffected. Exact commands, logs and
traceability are in the [machine evidence](evidence/online-admin-edit-context-20261026.json).
