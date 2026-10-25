# Candidate recovery HTTP embedding — 2026-10-25

`write-candidate/recovery_http.py:create_candidate` explicitly constructs the candidate
GET `/api/v1/operations/{operation_id}?command_type=capture.create|capture.edit` API.
There is no exported module app, active startup import, route activation, environment
file, migration or dependency change. Existing context API/OpenAPI remains unchanged.
Tests use the existing approved qualification environment with SQLAlchemy/psycopg;
the active API manifest does not yet own those dependencies. Controlled owner adoption
is a later activation prerequisite, using the approved baseline.

The request accepts one canonical nonnil operation UUID, exactly one closed command
query item, exactly one bearer header and an empty streamed body. Unknown/duplicate
query selectors return422; absent/malformed/duplicate bearer returns401 with a Bearer
challenge. Every response, including routing and unexpected errors, is private/no-store.
Safe allowlisted error pairs use the existing generated envelope. Unexpected exceptions
produce the existing selected diagnostic event without payload or traceback dumps.

One original ten-second Budget starts before body receipt and Access. Current own-read
evidence precedes pool checkout. A single cancellation-safe worker owns checkout,
managed read transaction and release; final budget checks include release completion.
Slow checkout cannot renew evidence: the existing one-second freshness check refuses
stale authorization before business SQL. The original compact receipt or successfully
verified unresolved is returned only after transaction and release complete.

The candidate constructs a lazy ordinary SQLAlchemy QueuePool (size5, no overflow,
checkout timeout0.25s, no pre-ping/recycle/retry hooks), an explicit configured/default5432
port overriding ambient PGPORT, psycopg connect timeout3s and
read-only default transactions with bounded SQL waits. Configuration requires one
numeric PostgreSQL host and rejects failover/query overrides and ambient credentials.
This avoids DNS/failover waits in this candidate. Pool/driver waits are separate finite
phases; expiry or cancellation awaits worker unwind and is **not** a promise of an
instantaneous request response or driver cancellation. No late success is returned.
The standard FastAPI lifespan disposes the owned engine on normal or exceptional exit;
the embedding ASGI host must drain requests before lifespan shutdown. Native server
drain and release lifecycle qualification remain gated.

| Requirement | Focused behavioral evidence in `test_recovery_http.py` |
| --- | --- |
| Original create/edit receipts and verified absence | committed receipt, edit revision and unresolved tests |
| Strict single selectors/auth/body | closed query/UUID, exact bearer and body refusal |
| Current authorization before acquisition | denial blocks checkout; setup/auth/upstream-error adaptation |
| Safe unavailable on acquisition/release failures | pool/driver failure, failed release, unknown error pair |
| Original deadline/freshness | streamed-body timeout, checkout expiry, late release |
| Connection retained through repeated cancellation and actual budget expiry | checkout, SQL and release phases |
| Real ordinary pool behavior | actual in-memory QueuePool exhaustion and overlapping exclusive successful leases |
| Factory-owned engine lifecycle | disposal on normal and exceptional lifespan exit |
| Private errors and inactive route | unexpected-error log test, routing errors and active-API absence |

ATDD observed13 failures against an explicit NotImplementedError stub before behavior
was implemented. Final **141 affected tests** pass, including **24 HTTP cases**. Blind review raised
five findings; all are fixed, none deferred. A new lifespan test first observed the
missing-disposal failure before its fix. The source-bound receipt records results and
exact commands. Test requests use ASGITransport and Access MockTransport; connections and SQL
are recorded synthetic objects. Pool-exhaustion and overlapping-lease tests use a real QueuePool,
with an in-memory synthetic driver. No native driver handshake, live database, TCP
server, real Access or production deployment is qualified. Docker remained stopped;
no retained data, roles, schemas, migrations or historical native receipts changed.

Scaffold impact: existing generated safe errors and transaction primitives are reused
unchanged; all three KDG code/test parity checks pass. This candidate orchestration is
app-owned until another proven consumer justifies shared extraction. Shared UI and
agent-context impact: none. Existing ADRs suffice; no accepted ADR edits. Contracts and
handoff updated in this item. Approved dependencies and TypeScript7.0.2 unchanged;
fingerprints/HMAC deferred. No Leave/editor, real-account/access, provisioning,
deployment, pilot or cleanup work.

Next qualify this explicit candidate over the retained restricted read-only database
without seeding, migrations or API activation. Native driver/pool behavior, live Access,
native server drain/disposal, candidate schema/client adoption and ADR-0020 compatibility,
recovery and release activation remain separate evidence gates.


See [source-bound receipt](evidence/recovery-http-20261025.json) and
[individual review triage](../../../_bmad-output/implementation-artifacts/spec-kdg-recovery-http.md).
