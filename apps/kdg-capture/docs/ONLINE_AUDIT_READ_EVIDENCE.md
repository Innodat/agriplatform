# Online audit metadata API — 2026-10-26

This technical subset of Story 3.1 adds an inert read-only
`GET /api/v1/admin/captures/{capture_id}/events` candidate. Implementation, focused
qualification and independent review pass. It does not close historical actor-display names,
portal presentation, native database permissions or full Story 3.1.

Every page checks current configured-organization `kdg_capture.capture.read.all`,
verified account/durable actor/membership and exact organization scope before checkout.
There is no own fallback, offline observation or business cache. The original
10-second budget covers current authorization, acquisition, read-only transaction,
release, validation and final response construction. Worker cancellation retains
connection ownership through unwind. Existing safe errors and private/no-store apply.

The closed page exposes verified reader/org/capture, original owner/creator,
creation time, latest modifier/time/current revision, limit, events and continuation.
Events expose revision, create/edit type, actual executor actor, nullable initiator
actor and server-recorded time. Stable actor IDs are attribution, never permission or
finished display names. Capture stamps and event stamps come from different statements;
neither is an exact PostgreSQL commit instant and they must not be forced equal.

One scoped SELECT reads the capture header and a bounded lateral revision selection.
It reads immutable capture revisions directly; joining executor-private operation
outcomes would wrongly hide other accounts' events. No-op edits and retries do not
create fictitious revision events. No answers, questionnaire snapshots, receipt,
operation/outcome IDs, eligibility evidence or operational logs are returned.

Numeric revision DESC navigation uses limit+1, default 30/max 100. A closed canonical
cursor of at most 2,048 bytes binds current caller/org/capture/read.all/limit/position.
SQL scope is independent of navigation. Pages are at most 64 KiB actual UTF8, with no
cross-request snapshot promise. A refresh obtains current newer events. Missing or
foreign records share safe 404; malformed evidence fails without partial disclosure.

Scaffold: permission/record/event semantics are KDG-specific and stay local; adopted
Auth/write/database/native-test/offline primitives and tests retain their five parity
checks. No new neutral mechanism is established. Shared UI, agent context, schema and
accepted ADRs remain unchanged. Contract, generated client, docs and evidence move
together. Historical actor labels need a separate permitted Identity HTTP contract;
assignment targets and current-account lookup are unsuitable for historical names.

Synthetic local/CI only, with recorded storage and mock Access. No actual SQL/RLS,
driver rollback or live identity proof is claimed. No UI/editor/Leave, active startup,
queue/sender/worker/browser activation, real accounts/services, native PostgreSQL/Docker,
provisioning/migration execution, deployment/production/pilot or cleanup. Preserve
concurrent work, historical evidence/resources and TypeScript 7.0.2. Fingerprints/HMAC
remain deferred. The prohibited untracked migration fixture is never accessed.

Final qualification passes ten commands: 115 focused backend tests, 43 actual HTTP
checks, owner export/generated freshness, strict TypeScript 7.0.2 and five scaffold
parities. All 277 earlier implementation sources are unchanged; earlier 377-test/33-command
evidence and 21 browser/store/HTTP proofs remain source-bound. All 185 protected files
remain unchanged. Exact commands, requirement mapping and result/source references
are recorded in the [machine evidence](evidence/online-audit-read-20261026.json).

Review: ten findings addressed, one disproved continuity-guard proposal and one
low-impact extra mocked overflow case rejected; no new deferred finding. Exact actor
IDs/nulls, semantic provenance, timezone instants and final HTTP serialization failure
are proved. A controlled lost-initiator mutation passed the old test and fails the
strengthened test, while unmodified production passes final verification. The final
proof forced-stall exits as expected at 10.64 seconds with normal owned shutdown.
Native SQL/RLS/driver and historical Identity labels remain unqualified prerequisites.
