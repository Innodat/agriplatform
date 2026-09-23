# platform/builder-cli

**Status:** Placeholder — Phase 3

CLI tool for scaffolding features and enforcing platform patterns.

## Purpose
- Automate boilerplate: one command creates router + service + page + hook
- Enforce consistency: validate-patterns fails CI if patterns are violated
- Reduce AI reliance: generated artifacts carry the structural knowledge

## Database and API direction

New application templates follow [platform ADR-0014](../docs/architecture/decisions/0014-python-database-access-and-api-models.md): SQLAlchemy/Psycopg database access and separate Pydantic API contracts. Prove the pattern before implementing generation. Opt-in routine CRUD must preserve permissions, tenant scope, revisions and caller-owned transactions; domain commands remain explicit.

Database introspection may assist persistence mapping but must not automatically expose table fields in API schemas. Frontend contracts derive from FastAPI OpenAPI. The historical command sketch below is not an implemented generator or authority to bypass this boundary.

## Database attribution and audit conventions

Table/model generation must follow
[platform ADR-0025](../docs/architecture/decisions/0025-record-attribution-and-audit-provenance.md):

- Mutable business tables: server-managed `created_at`, `created_by`, `updated_at`,
  `updated_by`; UTC instants and stable person/service actor references, not names.
- Immutable tables: creation attribution and append-only behavior; no misleading
  update columns. Other table categories require explicit applicability decisions.
- Preserve creation attribution and integer revisions. Do not expose writable audit
  fields in generated API input models. Cover every generated write path, including
  bulk/import, workers and operational commands, not just ORM object updates.
- Keep immutable consequential audit separate from last-change fields. Operational
  audit includes command name and deployed release, with initiator/executor distinction;
  source file/line details belong to diagnostics.
- Generate and verify model/migration/context behavior together before template
  promotion. Actor spoofing, rollback and immutable-record checks are required.

These are required generator contracts, not implemented CLI capabilities. Do not modify
Supabase-managed tables or invent a second person directory to satisfy the convention.

## Transaction and service-call direction

Follow [platform ADR-0022](../docs/architecture/decisions/0022-short-transactions-and-external-service-calls.md):
keep business transactions short and external calls outside coordination/write locks
by default. Current authorization precedes the protected action; current domain
validation, business effects, audit and durable outbound intent commit together.
Deliver required effects through the established outbox after releasing locks.
Document justified exceptions and their bounded failure/retry behavior. Prove this
pattern before adding generator support; this CLI remains a placeholder.

## Operational logging direction

Follow [platform ADR-0023](../docs/architecture/decisions/0023-structured-operational-logs-and-sensitive-data.md):
use selected structured fields for action/outcome/timing/error and safe correlation
context. Exclude sensitive business content, credentials and payload dumps across
normal and exception paths. Keep business audit separate, restrict operational access
and test sensitive-value exclusion. Promote proven API/worker logging defaults during
delivery; no logging generator or telemetry provider is implemented by this guidance.

The [observability and future AI investigation direction](../docs/operations/observability-and-ai-investigation-direction.md)
keeps operational monitoring outside applications, defines basic backend OpenTelemetry
and operational signals for MVP, and defers the product comparison and AI workflow.
No specific telemetry stack or AI repair framework is selected for scaffolding yet.

## Durable event compatibility

Follow [ADR-0028](../docs/architecture/decisions/0028-event-payload-versions-and-queued-work-compatibility.md):
generate/prove minimal event type and payload-version envelope support alongside
stable event/operation identity. Keep payload models application-owned and validate
supported versions explicitly. Test old queued and failed/retryable payloads across
releases; retain and flag unsupported versions. No schema registry or generic payload
editor is required. Compatibility applies to producer/consumer rollout and rollback,
not just database schema changes. These remain generator implementation requirements.

## Outbox table ownership

Scaffold each outbox in its owning application's schema under platform ADR-0003/0016,
not a shared cross-application SD schema. Shared mechanics do not imply shared runtime
tables. Receiver services own their delivery records behind service contracts. Leave's
[concrete application](../../apps/leave/docs/architecture/decisions/0116-owned-outbox-and-obsolete-notification-intent.md)
keeps notification relevance local; do not put domain-specific skip rules in a generic
worker template. Table names remain an owning implementation detail.

## Delivery recovery direction

Follow [platform ADR-0024](../docs/architecture/decisions/0024-durable-delivery-retries-and-audited-recovery.md):
bounded retries, retained failures and authorized audited recovery through normal
worker processing. Keep event identity stable for unchanged retries, retain attempts,
and avoid repeating the business action. No support CLI/UI implementation or execution
transport is selected here; prove reusable mechanics in delivery before scaffolding.

## Notification retention defaults

Apply [ADR-0029](../docs/architecture/decisions/0029-notification-retry-expiry-and-retention.md)
only to notification delivery: original-event retries expire after 90 days, terminal
outbox/attempt details remain 90 days, and receiver deduplication remains at least
90 days after acceptance and while unresolved. Reject expired events even after their
deduplication records are removed. Replacements are newly authorized notification
intents, not repeats of domain actions. General command/event retention remains separately
specified; no runtime cleanup or generator support is implemented by this guidance.

## Worker identity and shutdown direction

Follow [ADR-0026](../docs/architecture/decisions/0026-worker-service-identity-and-ngo-scope.md):
use owner-specific restricted worker identities across permitted NGOs, narrow discovery
and explicit per-item transaction scope. Do not generate per-NGO worker keys or a
universal platform worker credential.

Follow [ADR-0027](../docs/architecture/decisions/0027-bounded-worker-shutdown-and-deployment-reporting.md):
stop new claims, allow bounded completion and verify abrupt-stop recovery. Deployment
supervision records forced stops in the deployment report and structured logs, even
when the worker cannot. Report recovered processing only with evidence. Coordinate
timeouts and retain existing retry/deduplication guarantees. Prove these hooks before
template promotion; no current generator or supervisor behavior is claimed.

## Attachment recovery direction

Follow [ADR-0030](../docs/architecture/decisions/0030-recoverable-content-attachment-association.md):
separate uploaded/finalized content from a persisted domain association. Reuse content
and operation identity on association retry; validate scope/readiness server-side and
block required-document confirmation until attached. Prove attaching/retry UI state
and duplicate-safe recovery before template promotion. Content cleanup must coordinate
with pending associations and protect saved drafts/submitted records; exact cross-service
lifecycle contract is a delivery prerequisite, not an implemented generic helper.

## API error contract direction

Follow [ADR-0031](../docs/architecture/decisions/0031-machine-readable-api-errors-and-localized-presentation.md):
stable machine-readable identifiers and safe typed details drive frontend behavior,
not English message parsing. Align Pydantic/OpenAPI, framework error adapters, generated
TypeScript and localized shared handling, including unknown-identifier fallback.
The current template's numeric `code` is not this new semantic identifier contract;
choose wire fields and compatibility before implementation. Update owning templates
and tests, not generated outputs. No runtime format change is made by this guidance.

## Authentication return flow

Follow [ADR-0032](../docs/architecture/decisions/0032-session-recovery-and-return-navigation.md):
shared shell/API-client renewal, validated return location and same-user/NGO permission
checks restore the prior page and recoverable form context. Keep sensitive values out
of return URLs; application drafts retain their own policy. Refresh consequential
state and never auto-confirm after sign-in or duplicate an uncertain prior operation.
Prove these cases before template promotion; this guidance implements no auth flow.

## Draft lifecycle protection

Follow [ADR-0033](../docs/architecture/decisions/0033-draft-lifecycle-and-late-save-protection.md):
check expected revision and editability atomically, never upsert closed/missing drafts
from late autosaves, and require explicit new-draft creation. Finalization commits with
its local domain effects. Provide lifecycle-conflict hooks that stop autosave and retain
local edits while applications supply states/navigation. Verify old create retries and
concurrent submission/discard, not just stale update revisions. Prove the pattern before
generation; no generic workflow engine or runtime lifecycle change is implemented here.

## Single-active-draft creation

For workflows opting into one active draft per defined domain scope, follow
[ADR-0034](../docs/architecture/decisions/0034-atomic-single-active-draft-creation.md).
Generate/prove database enforcement and atomic create-or-resume handling, rather than
read-then-create logic. Concurrent creators must share one draft without overwriting
its values. Applications supply scope and draft-count rules. Test races, separated
NGOs/owners and old create retries after closure. Do not impose a universal one-draft
rule or introduce shared runtime draft tables. No generator support exists yet.

## Structural database integrity

Follow [ADR-0035](../docs/architecture/decisions/0035-database-structural-integrity-and-application-rules.md):
scaffold required fields, declared checks/references and scoped uniqueness in both
persistence models and reviewed migrations. Tenant-owned local relationships enforce
matching NGO scope; shared/global references need explicit treatment. Do not invent
cross-service foreign keys or derive every business rule from column names. Keep
complex policy decisions in workflows with existing authorization/transaction safeguards.
Verify concurrent/alternate write paths, cross-NGO rejection and safe API error mapping;
RLS and friendly API validation remain necessary. Generation is not implemented here.

## Private content capability lifetimes

Follow [ADR-0036](../docs/architecture/decisions/0036-private-content-signed-operation-lifetimes.md):
shared content configuration defaults to 5-minute private read/download capabilities
and 15-minute upload capabilities. Renew through authorized service contracts and
preserve existing form/content recovery. Verify provider-specific expiry/in-flight
behavior and secret-safe diagnostics; no generated business administration setting.
These are planning defaults, not applied runtime configuration.

## Migration direction

[Platform ADR-0015](../docs/architecture/decisions/0015-alembic-migration-authority.md)
selects Alembic for project-owned schemas. Templates must include owned-schema
filtering and migration verification. Align bootstrap/reset, seed and CI commands
when implemented; the existing SQL composition tool remains transitional tooling.
Do not apply both migration systems to the same owned objects. Supabase-managed
schemas are outside autogenerated project schema changes.

Each app/service has its own schema, revision files and migration-version table
under [ADR-0016](../docs/architecture/decisions/0016-owned-migration-histories-and-coordination.md).
The shared deployment entry point coordinates explicit dependencies; generation
must not let one owner manage another owner's schema.

Provision separate restricted runtime and schema-changing deployment identities
under [ADR-0017](../docs/architecture/decisions/0017-runtime-and-migration-database-authority.md).
API/worker environments must not receive migration credentials. Verify permissions
using actual runtime identities, including cross-owner and tenant-denial cases.

Establish verified NGO/actor context per database transaction under
[ADR-0018](../docs/architecture/decisions/0018-transaction-scoped-tenant-context.md).
Include fail-closed tenant RLS and pooled-connection reuse tests; worker identity
and tenant scope are explicit. No connection-wide current-NGO state.

Protected requests check current membership/permissions through the shared access
capability under [ADR-0019](../docs/architecture/decisions/0019-current-server-side-authorization.md),
then application-specific resource rules. Include revoked-access and unavailable
verification tests; login claims or visible controls alone do not authorize actions.

[ADR-0021](../docs/architecture/decisions/0021-revocation-and-in-flight-operations.md)
defines revocation ordering: already-authorized short executions may finish;
queued or delayed new execution requires fresh authorization. Provide bounded
execution and auditable authorization timing. Define timeout values before delivery.

## Mandatory release safety

All generated applications and services follow
[ADR-0020](../docs/architecture/decisions/0020-safe-schema-changes-and-release-recovery.md).
Provide a controlled migration step, prevent competing executions, and block new
API/worker activation when required migrations fail. Report per-owner revision
outcomes. Preserve previous-version compatibility through staged schema changes;
incompatible changes need planned maintenance and explicit recovery. Do not run
migrations at API startup or automatically downgrade after deployment failure.
Include verification hooks and recovery guidance in shared delivery tooling.
These are required implementation targets, not existing CLI capabilities.

## Planned commands
```bash
create-feature <name>     # scaffold full feature (UI + API + types)
generate-models [table]   # persistence mapping assistance; explicit API schemas remain separate
validate-patterns         # lint: check generated files, prompt sizes, naming
```

## Planned structure
```
platform/builder-cli/
  src/
    commands/
      create-feature.ts
      generate-models.ts
      validate-patterns.ts
    templates/           ← Handlebars/EJS templates for scaffolding
    lib/
      supabase-introspect.ts
      codegen.ts
  bin/
    platform-cli.ts
  package.json
```

## Phase
Built in **Phase 3** after FastAPI + codegen (Phases 1–2) are stable.

## Operational alert scaffolding

Follow [ADR-0037](../docs/architecture/decisions/0037-operational-alerts-and-incident-grouping.md)
when promoting proven monitoring templates: configurable per-application thresholds,
separate API/worker/delivery signals, grouped ongoing incidents and verified recovery.
Provide failure/recovery verification hooks. Do not generate business administration
screens for technical alert settings. This is a future scaffold requirement.

## Finalized content identity

Shared content clients and provider contract tests follow
[ADR-0038](../docs/architecture/decisions/0038-finalized-content-byte-identity.md).
Finalized content identity binds verified bytes through association and reading;
outstanding upload capabilities cannot mutate that identity. Replacement uses a new
identity and authorized audited association change. Prove provider behavior and races
before promoting adapter scaffolding; no new UI pattern is required.
