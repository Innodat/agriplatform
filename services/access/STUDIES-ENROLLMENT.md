# Personal Studies enrollment and current authorization

The Access owner implements explicit personal enrollment and the account variant of
`POST /v2/check`. Scribeswell owns its separately delivered opt-in routes/editor; invitations, recipient
resolution and notification delivery remain later work. Public Bible reading has no dependency
on these routes. No environment, real account, production grant or deployment was
activated by this delivery.

Scribeswell alone sends its restricted service key plus the current end-user bearer.
Enrollment accepts exactly `{"operation_id":"<canonical lowercase nonnil UUID>"}` at
`POST /v2/enrollments/scribeswell-studies`. The committed200 acknowledgement contains
`operation_id`, `status: committed` and `result` with `disposition: created | unchanged`,
`account_id`, `actor_id` and fixed `permission: scribeswell.studies.use`. Retry the
original operation after an unavailable/unknown result; never infer rollback or issue
a replacement operation. A replay freshly checks eligibility and retained revocation,
then returns its original disposition. The receipt grants no current authority.

The subsequent current check accepts exactly:

```json
{"permission":"scribeswell.studies.use","authorization_scope":{"kind":"account"}}
```

Success has exactly `account_id`, `actor_id`, `permission`, `authorization_scope`,
`decision_id` and `checked_at`. There are no organization/member/person placeholders
or resource-scope fallback. Each executing protected action needs a fresh check plus
Scribeswell's own resource authorization. Browser inputs never select a target account,
actor, address, organization, permission or executor during enrollment.

Enrollment and all recognized Studies-caller check outcomes use
`Cache-Control: private, no-store`. Existing KDG checks preserve `detail.code` and
`no-store`. On the shared check route, a missing/unknown service credential cannot
select the Studies contract: it retains KDG's existing403 `detail.code:
service_access_denied` envelope and `no-store`. Recognized Studies callers receive the
closed `error_id` envelope below. Consumers must treat either unknown-caller envelope
as a denial, never attempt another scope. Enrollment itself always uses the new envelope.

| HTTP | Closed Studies `error_id` |
| --- | --- |
|401|`authentication_required`|
|403|`service_access_denied`, `access_denied`, `identity.verification_required`|
|422|`validation_failed`|
|503|`authorization_unavailable`, `identity.setup_unavailable`, `dependency_unavailable`|

Errors contain fixed `error: Request could not be completed` and `details: null`.
Provider/SQL/request contents are never serialized or logged by these adapters.
Malformed, duplicate, oversized and unknown-field JSON refuses before Identity writes.
Confirmed Auth ineligibility uses stable Identity SQLSTATE `IS003` mapped to403 `access_denied`; missing current verification uses `IS006` mapped to403 `identity.verification_required`. A missing/deleted/system/keyed profile or conflicting actor uses503 setup unavailable; neither
login nor checking creates or repairs profiles/actors. Supabase's live user endpoint
establishes the account and current verified primary email; JWT role/email claims are
insufficient. Identity additionally observes current selected Auth eligibility fields.
The pending address is not used as a recipient match; recipient protocols are undelivered.

## Restricted owner execution

| Connection role | Permitted Studies routine | Returned internal fields |
| --- | --- | --- |
|`identity_studies_reader_runtime`|`identity.studies_account_evidence()`|`account_id`, nullable `actor_id`; no row means refusal|
|`identity_studies_setup_runtime`|`identity.prepare_studies_account(operation_id)`|`account_id`, `actor_id`; no row means refusal|
|`access_studies_runtime`|`access.enroll_studies_account(operation_id, actor_id)`|`disposition`, `account_id`, `actor_id`; no row means denial|
|`access_studies_runtime`|`access.check_studies_permission(actor_id)`|`account_id`, `actor_id`; no row means denial|

Only the verified server adapter supplies transaction-local `app.context_kind=user`
and `app.account_id`; actor/organization context is cleared. Each owner uses a separate
async psycopg connection, closed after the transaction. There is no cross-request pool
or context reuse and no new pool dependency. Runtime roles have no table/column write
privileges or owner-role memberships. NOLOGIN owners have the selected internal grants
needed by their fixed routines. The setup role cannot invoke operator provisioning.

A valid adopted actor mapping is reused unchanged. An absent mapping derives its actor
UUID from the eligible profile account ID; a missing/blank username uses the safe
profile-derived label `Account <UUID>`. An existing unmapped colliding actor refuses.
Identity setup and Access assignment commit separately. Actor-only completion has no
Studies permission; retry freshly observes eligibility and resumes the same actor.
Identity reuses the delivered operator account/actor locks without changing operator
commands. Durable setup/assignment events and receipts distinguish the service executor
from the verified account-actor initiator. Initial grant/event uniqueness is enforced
in PostgreSQL; all new retained evidence tables use FORCE RLS.

Access starts a monotonic3-second total budget before receiving the body, including
provider verification, owner SQL and commit. The live provider call has at most2 seconds;
Identity's5-second observation ceiling remains an additional upper bound. Lock waits
are at most1 second and statements at most2 seconds, shortened to positive remaining
milliseconds. Async cancellation closes the dedicated libpq socket at the total deadline,
so psycopg's5+5-second cancellation cleanup cannot extend the request. Closing/cancellation
is not proof of server rollback. Unknown commits remain unavailable and use same-operation
recovery with fresh eligibility. No external service wait occurs under these write locks.

## Controlled release preparation

Default service configuration leaves Studies disabled and existing KDG/public consumers
usable. Opt in only after controlled, compatible migrations and owner preparation.
`prepare_studies_runtime_roles.sql` is explicit administrator preparation with no
password/actor/account/grant seeds; existing roles refuse for owner verification.
`prepare_studies_auth_evidence.sql` is separate Auth-owner selected-column preparation,
not a provider schema change. Set separate credentials privately; never place them in
argv or evidence. Ordinary Identity Alembic runs before Access Alembic. Access16 refuses
without the Identity-owned setup routine. Failed migration blocks activation; no startup
migrations, automatic downgrade or automatic reversal occurs.

Authorized owners separately verify the durable service actor, then prepare the two
protected principal rows using that same UUID. Identity requires kind `service` with a
registered actor key. The rows record creation/update actor and server UTC time, revision
and a nonnil release-operation UUID; their executor binding is immutable. No production
principal provisioner or new enrollment-admin API is supplied. Missing preparation must
remain a release refusal, rather than borrowing operator or universal credentials.

After source-bound qualification and successful owner upgrades, run the read-only owner
preparation using private migration URLs in the environment:

```sh
P services/access/studies_readiness.py --qualification /private/retained.json \
  --release-id approved-release-reference --output /private/studies-readiness.json
```

`P` denotes the locked owner Python interpreter. This routine refuses missing heads,
missing/disabled/mismatched executor principals, non-service Identity attribution,
missing Auth profile hook, unsafe runtime roles/raw table privileges, missing account
permission/application registration and stale qualification/runtime sources. It writes
only a new0600 evidence file; it performs no database writes or activation.

Provide its compact JSON verbatim as `STUDIES_READINESS_JSON`, plus
`SCRIBESWELL_SERVICE_KEY`, `STUDIES_ACCESS_DATABASE_URL`,
`STUDIES_IDENTITY_DATABASE_URL` and `STUDIES_IDENTITY_SETUP_DATABASE_URL` using the exact
roles above. Host-release preflight consumes this manifest opt-in contract and checks
all three database roles; default Access startup also rejects partial/stale readiness.
The actor binding cannot change silently after preparation, and disabled principals,
application availability, current account state and revoked grants still deny at runtime.
Recovery disables this opt-in or rolls forward while preserving actors, receipts and
acknowledged grants. Revocation is an explicitly attributed owner operation with
`revoked_by`, `revocation_operation_id` and server UTC `revoked_at`; no regrant/undo route
is delivered. Retain the release/operation evidence for principal changes and revocation.

## Wire generation and evidence

`studies_contract.py` owns closed DTOs. `export_openapi.py` generates `openapi.json`;
`contracts/generated` contains installer-owned TypeScript wire types, generated through
the existing `platform/api-client` CLI. This is an internal type artifact, not a browser
service-key adapter. The pinned tool uses its already qualified isolated TS6 payload;
consumer proof compiles under the unchanged root TypeScript7.0.2 and Node26.11.1.
No dependency baseline was changed. Do not hand-edit generated artifacts.

Focused Python tests cover the HTTP/Identity contract and existing KDG characterization;
`studies_types.test.ts` proves the exact account fields, scope, permission, disposition
and closed error union. The native single-use fixture qualifier retains separate initial
and final frames, real provider-issued token/profile-hook evidence, empty-owner and
populated upgrades, ordinary Alembic failure/rollback/repeat, first-enrollment races,
actor-only/adopted/collision/current-denial cases, real SQL deadlines, lost-response
recovery, revoked replay and actual restricted-role refusals. Independent retained
inspection is separate from the mutation stages. See delivery evidence for exact
commands/results and remaining operational limitations.

Scaffold: existing async owner and generated-type patterns only; no generator engine.
Shared UI and agent context: unchanged. Documentation: this runbook and owner/Scribeswell
handoff. ADRs: unchanged. Recipient/invitation delivery, note/editor CRUD, Leave/PtS
migration, real account/access changes and deployment remain outside this item.


## Scribeswell consumer status — 2026-10-23

The app now supplies its own bounded server HTTP adapter and explicit browser enrollment
proxy under a development/test opt-in. See
[personal-notes runtime](../../apps/scribeswell/docs/PERSONAL_NOTES_V1.md#opt-in-runtime-and-qualification--2026-10-23).
Its synthetic Access HTTP fixtures verify consuming bindings and SQL/browser behavior;
they do not replace this owner's retained authorization/provider qualification.
Production consumer activation remains refused pending coordinated integration/release
qualification. Enrollment remains explicit and signup/public reading grants nothing.
