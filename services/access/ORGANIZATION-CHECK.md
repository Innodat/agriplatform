# Current organization permission check

Access15 adds the KDG-facing `POST /v2/check`. This bounded delivery is synthetic
local/CI qualification only. KDG writes, target discovery/verification, account checks,
Leave, and coordinated PtS activation remain separate work.

Configure the server with a distinct printable-ASCII `KDG_SERVICE_KEY` and nonnil `KDG_ORG_ID` UUID.
Omitting both disables KDG checks. Partial/malformed configuration or reusing a PtS or
Content service key refuses app creation with a safe configuration code. Neither value
is a browser credential. Runtime uses `ACCESS_DATABASE_URL` with `access_runtime`;
provider user verification uses the existing `SUPABASE_URL`/`SUPABASE_ANON_KEY` adapter.
There is no startup migration or provider call inside the SQL transaction.

The request contains exactly `permission` and `authorization_scope` with exactly
`kind: organization` and `org_id`. Bearer authentication determines the account; no
account/actor/member/target selector is accepted. The distinct service policy permits
only the nine exact KDG literals and configured organization. Unknown/duplicate fields,
invalid UUIDs/scopes, malformed/deep JSON, oversized bodies and body receipt exceeding
three seconds fail safely. OpenAPI declares bearer and service-key authentication together. Service
policy denial is `service_access_denied`, independently of the user's authority.

The read-only bounded transaction sets verified account/organization context locally
and invokes only `access.check_organization_permission(text)`. It matches current
Identity profile/organization/membership, organization permission registered specifically
to `kdg_capture`, globally
enabled application, enabled organization admission and exact nonrevoked
membership-bound grant. An absent grant/current membership returns `access_denied`.
Only after those predicates succeed can an absent durable account actor return
`identity.actor_setup_required` (409). Nothing is created. Rejoin cannot use an old
grant; app re-enable restores only still-valid authority. Each success has a fresh UUID
decision, UTC time, positive bigint decimal membership and the exact own-account or
organization resource scope. All check responses use `Cache-Control: no-store`.

## Controlled preparation and upgrade

Retain Identity20 and Access14 history/source/receipt evidence. Use the existing
restricted Access migration login and reviewed synthetic target. As true administrator,
run `tools/prepare_access_check_reader_execution.sql` once against an existing safe
Identity20 reader. It adds only access_migrator's noninherited, nonadmin SET edge;
preexisting edges refuse unchanged. The receiving migrator must retain its restricted
flags and exact approved assumption paths before the grant. No runtime can assume this reader.

From `services/access`, run the existing controlled upgrade with protected
`ACCESS_MIGRATION_DATABASE_URL`: `uv run --locked alembic upgrade head`. The owner
verifier recognizes exact14 and exact15 only alongside earlier historical catalogs.
Migration15 grants selected reader columns and scoped forced-RLS policies, then
temporarily permits Access schema CREATE and assumes the private reader to create the
wrapper with its existing Identity rights. It restricts execution, resets the role and
revokes CREATE in the same transaction. The wrapper has fixed search path and private
definer ownership. Runtime's
old raw grants SELECT is revoked. `/v1/check` refuses with 503 until separate typed PtS
account adoption; it cannot bypass membership/admission/revocation checks.

The mutable Identity verifier recognizes only the exact staged reader edge or complete
installed15 metadata, without Access business/history reads or recursive owner verification.
It removes only verified reader differences when comparing immutable Identity20 evidence.
Unexpected roles, dependencies, policy/column/schema/function ACLs or catalog drift refuse.
Failure rolls the migration transaction back; preserve evidence and reconcile explicitly,
then retry forward. Never downgrade automatically or repair unknown state during upgrade.

## Verification and impact

Use the approved prepared CPython3.15/uv0.13.1 and owner `pyproject.toml`/`uv.lock`.
`uv run --locked python -m pytest tests/test_organization_check.py` covers all nine
resource mappings, strict input/service policy, actor precedence, safe failures, no-store,
provider-before-transaction ordering and valid OpenAPI references. Export the owner
contract with `uv run --locked python export_openapi.py`; check with `--check`.

`tests/qualify_organization_check.py` owns the actual SQL-to-HTTP synthetic proof using
existing bridge/assign/revoke fixture plumbing. Its named stages cover upgrade/repeat,
rollback/drift/retry, restricted runtime privileges, grant revoke, disable/re-enable,
membership retirement/rejoin, actor precedence and independent retained inspection.
These are transaction/body/pool/connect bounds; the existing provider adapter and
established database transport do not yet have a total operation deadline. Their
network-failure qualification is recorded before deployed Access operation.
See [owner evidence](ORGANIZATION_CHECK_EVIDENCE.md) for exact commands/results and
source/log/state custody; do not infer provider/device/hosted-CI or production readiness.

Scaffold: reuse existing owner migration, server context, export and verification patterns;
no generator implementation is added. Shared UI: no impact. Agent context: no changes.
Documentation: this runbook, owner evidence and mutable owner handoffs. ADRs: existing
accepted ownership, release, transaction, actor and error decisions suffice; no ADR edited.
