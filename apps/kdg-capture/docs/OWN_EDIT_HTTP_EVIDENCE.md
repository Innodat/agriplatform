# Candidate own-edit HTTP and replay — 2026-10-25

The explicitly constructed `write-candidate/edit_http.py:create_candidate` now exposes
`PUT /api/v1/captures/{capture_id}`. It remains separate from active API startup and
browser/editor/queue wiring. The unchanged qualified `capture_edit` body handles fresh
writes; the new handler coordinates current authority and committed replay.

Both current `kdg_capture.capture.read.own` and `kdg_capture.capture.edit.own` checks must
succeed before acquiring a database connection. Existing closed Access decoding binds
fixed organization and own-account resource scope; both observations must identify the
same verified account, durable actor and membership instance. Both checks share an
at-most-three-second window. The earlier monotonic observation is retained for the
existing one-second transaction-entry freshness check. These are current observations,
not an offline lease. Tests supply synthetic Access evidence; no real account binding
or real authorization-service qualification is claimed.

One original ten-second Budget covers streamed command bytes, Access, worker admission,
connection acquisition, SQL, commit and acknowledgement. Requests require one Bearer
header, one application/json Content-Type (ordinary parameters allowed), no query items,
a canonical path UUID and strictly parsed bounded JSON. Duplicate
keys, unknown fields, unsupported versions and malformed inputs fail safely before
outcome discovery. The body ceiling is131072 UTF-8 bytes, including chunked bodies.
Configured pool checkout, connection establishment and server-statement waits are
bounded; numeric database hosts avoid DNS/failover waits. Every writer owns its
connection exclusively. Cancellation waits for worker unwind, including repeated
cancellation during acquisition, SQL, commit or release. Response completion may await
worker unwind beyond the executing deadline. Synthetic tests establish control flow;
native driver cancellation, TCP drain and resulting network unwind bounds remain unqualified.

Inside one transaction the scoped capture.edit operation lock and private outcome
lookup precede fresh writes. A committed duplicate authorizes the actual stored own
capture, then returns its original receipt/target/revision. A different incoming valid
path, stale expected revision or domain-invalid answers cannot select the replay target
or trigger fresh-action validation. The client must reconcile any receipt-target
mismatch under the existing frozen-command contract. Missing/foreign/malformed stored
evidence refuses privately. Fresh actions use original version validation, revision
checks and receipt-only no-op behavior without create/assignment/active-child requirements.
No provisional receipt crosses failed commit or late acknowledgement.

Fresh stale input returns409 `kdg_capture.capture_revision_conflict` with string
`current_revision` alongside the existing safe error envelope; no answer snapshot.
Missing/foreign fresh captures share404 `capture_unavailable`. Other errors use fixed
status/identifier allowlists. Responses, including routing/unexpected errors, are
`private, no-store`; authentication errors retain `WWW-Authenticate: Bearer`.

`edit_openapi.py` describes runtime-validated JSON through Pydantic models and local
boundary metadata. Offline `export_edit_openapi.py` exports/checks the candidate schema
without credentials, engine or network. Existing platform API-client tooling generates
`contracts/edit-generated` through its owning installer; generated files are not edited.
Per-code errors discriminate revision metadata; TypeScript7.0.2 consuming tests include
12 negative cases. Schema agreement tests cover actual success, conflict and denial.
Schema annotations do not replace streaming/duplicate-key/runtime validation.

Behavioral ATDD first observed pending transaction NotImplementedError (12 tests,
nine errors); the separately retained replay log is labeled as a replay. Contract ATDD
observed three pending schema failures. Final verification: **46 focused tests included
in265 affected tests**, three scaffold parity checks, current schema/generated checks
and TypeScript7.0.2 consumer checks pass. Exact commands, source/log hashes and matrix
traceability are in the [record](evidence/own-edit-http-20261025.json).

Scaffold: existing neutral transaction, Access-decoding, worker and API-client machinery
are reused unchanged. KDG capability pairing, stored ownership and SQL stay application
owned. Shared UI, agent context and ADR: no change. Documentation: this evidence, receipt,
append-only contract and prepended handoff. No dependency install, Docker/native action,
schema/migration, provisioning, real Access/account, Leave/editor, production, deployment,
pilot or cleanup occurred. Historical source receipts, concurrent work, resources and
TypeScript7.0.2 remain preserved; fingerprints/HMAC deferred.

Native qualification of this new PUT orchestration/replay, current real Identity/Access,
native contention/cancellation/TCP drain, active startup/client adoption and ADR-0020
compatibility/recovery/activation remain separate gates. Earlier native own-edit-body
proof does not qualify this new HTTP boundary. Three independent review layers completed: ten findings addressed, one rejected with evidence, none deferred.
Reviewed fixes align JSON media type, populated answer schema/types, streamed byte limits,
commit cancellation and stored-target scope evidence. Exact commands replace optional
notation; driver-wait wording preserves the native drain limit.
