# PtS Swahili Poetry owner design

The production target is the existing Supabase project: PostgreSQL, Supabase Auth
(federated Microsoft Entra), and a private Supabase Storage bucket. The disposable
PostgreSQL container is only a verification fixture, never a new production database.
The application boundary follows platform ADRs 0001–0005, 0011, 0014–0023, 0025,
0030–0032 and 0035–0038. No accepted decision is superseded.

## Ownership and contracts

- PtS owns `pts` and original collection objects, conflicts, import snapshots and
  document associations. Browser business data comes only from FastAPI. Pydantic
  OpenAPI generates the frontend DTO file with `tools/generate_contracts.py`.
- Access owns `access.grants`; its narrow identity-owner bridge reads current
  `identity.org` and `identity.org_member` rows. PtS never reads identity tables.
  Legacy membership has soft deletion rather than a separate active flag. Both
  organization and membership must be undeleted. Explicit permission grants are
  required even for owners/admins. The delivered Reader role is the reviewed set
  `pts.poetry.read`, `pts.poetry.export`, `pts.poetry.documents`; membership or an
  admin JWT alone grants none of them. There is no wildcard or future grant.
- Content owns `content.objects`, private bytes and operation audit. PtS owns the
  attachment row and requests read issuance only for its document association.
  Content repeats current document permission verification; no browser receives
  internal service credentials. Initial deployment is scoped to PtS, not a generic
  multi-application authorization framework.

`POST access/v1/check` receives the user's Bearer token, a server service key,
organization UUID and permission. It verifies the token using Supabase Auth's user
endpoint, then reads current membership plus grant on every request. Positive
results are never cached. Its actor/organization response is the only input to
transaction-local `app.actor_id`/`app.org_id`. Missing or malformed scope cannot read
RLS tables. Auth/access network timeouts are 5 seconds, SQL statements 5–10 seconds.
Revocation affects subsequent checks; an already authorized bounded operation may
finish under ADR-0021. An outage returns 503, denial 403, absent authentication 401.

Runtime roles are non-owner, non-superuser and NOBYPASSRLS. PtS runtime is SELECT
only, importer INSERT/SELECT only, content runtime has only necessary object state
writes and immutable audit INSERT, access runtime only restricted reads. Migration
roles own separate schemas and separate Alembic version tables. Runtime and import
identities cannot assume owners. The identity compatibility policy is a separate
identity-owner operation; no legacy migration history is rewritten.

## Preservation and imports

The original Windows folder is read-only. The ignored copy is verified against
`reference/copy-manifest.json`: 264 files, 222,505,940 bytes. Only canonical
`library.json` supplies records. JSONL, SQLite and embedded HTML are historical
snapshots, not additional poems. Original files and notices remain unchanged.

Each entity retains its complete JSON payload, including unknown metadata, text
newlines, historical spellings, work links, provenance and prior decisions. Separate
source/rights/poem/witness/document tables add database foreign keys; 13 legitimate
collection-wide reference documents have no source_id. All other top-level values
are retained in metadata; full incoming snapshots retain every original object.
Stored ordinal retains canonical array ordering. The importer serializes per-org
imports and never updates an existing entity. Exact replay is a no-op. Changed
existing payloads become explicit conflicts with the full incoming version; CLI
returns 2, including replay of an unresolved conflicting import. A reviewer must
explicitly reconcile conflicts in a future authorized correction workflow; no
review or rights clearance is inferred.

## Private immutable documents

The importer requests a content identity through HTTP using a distinct secret
bound to one configured organization. It receives a presigned S3 PUT to a staging
key for 900 seconds, uploads directly to Supabase Storage, then finalizes through
HTTP. Size ceiling is 128 MiB (supports the >85 MiB scan); the Supabase global and
bucket limits must both permit that size. The bucket must remain private.

Finalization claims state in a short database transaction, releases the transaction,
then copies staging to an unexposed sealed namespace. It streams and hashes the
sealed copy with bounded 1 MiB buffers, a 180-second total deadline and 30-second
provider read timeout. This server-side verification read is an explicit bounded
exception to the normal direct-transfer path. Hash and size must match. Upload
capabilities can only overwrite staging, never sealed bytes. The sealed key is
never signed for PUT; existing sealed objects are never replaced by retry. Ready
state and database identity fields are protected by a trigger. Readiness and its
consequential audit event commit atomically. Read GET capabilities
last 300 seconds and bind the sealed key, after fresh access checks.

No lease takeover can race a finalizer. A crash/uncertain provider completion keeps
`finalizing` and returns a recovery-required outcome. Operators must stop the old
finalizer and inspect the same sealed bytes before explicit recovery; do not reset
state while an operation may still run. The explicit owner recovery command retains
a failed identity and its bytes, atomically audits it, and allows a new identity for
the same expected hash through a partial unique index. Ready identities remain immutable. See README. No automatic deletion or expiry
cleanup is delivered: pending, finalized and attached objects remain retained. This
conservative retention avoids guessing application abandonment. An attachment retry
reuses finalized identity and checks existing association; a different content ID
never silently replaces it. No external service waits occur inside write locks.

The content owner records safe operation IDs, actor, organization and content ID;
never signed URLs, credentials, or payload dumps. Run servers without access logs
unless the deployment's log sink has equivalent request-header/URL safeguards.
Business payloads are separate from diagnostic output. Provider-specific expiry,
clock tolerance and in-flight behavior must be verified against configured Supabase;
mock adapter tests are not evidence of that provider behavior.

## Release and recovery

`tools/py/deploy_pts.py` requires all three migration URLs, runs access → content →
PtS histories, stops on the first error, never reverses applied migrations and never
starts an API. A unique release evidence file records code identity, each owner’s before/after
revisions and outcome, and whether migrations completed. It never authorizes activation.
Keep the previous application version active on failure. Initial schemas and additive
integrity/audit changes retain prior reader contracts; rollback means prior compatible
application code, not automatic schema reversal. An incompatible future change needs
an approved maintenance/recovery plan. A successful migration report alone is not
provider readiness or permission to publish this collection.

No worker or queue is introduced. Monitor the three `/health` endpoints and actual
request error rates externally; a process heartbeat does not prove access/provider
health. Start with three consecutive 30-second failed checks per owner before one
incident, recovery after two successful checks; tune through deployment operations.
No frontend availability polling or global content-outage state is introduced.

## Delivery impact decisions

- Scaffold: this feature proves transaction-local context, separate owned Alembic
  histories and current-access HTTP clients. A small reusable template/example is
  added, without claiming the placeholder builder CLI is implemented.
- Shared UI: use the existing AppLauncher and directory client. Reader/filter CSS
  remains application-owned; no speculative shared components or Leave work.
- Agent context: existing instructions suffice; no changes to AGENTS.md.
- Documentation: this design, README, environment examples and verification report
  own operating evidence. Historical source docs are data and remain unchanged.
- ADR: follows existing accepted decisions; no new or changed decision required.
