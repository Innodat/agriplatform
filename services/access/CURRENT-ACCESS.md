# Current typed capability access

ACCESS-B adds current registered account and organization decisions and People's
identity context to the existing Access service. A decision is a point-in-time
observation, never a token to replay instead of checking a protected action.
Actual downstream PtS adoption, People management, Directory adoption and Leave
business journeys remain separate gated delivery.

The canonical check is `POST /v2/check` with the current end-user bearer and a distinct
server-only `X-Service-Key`. Its closed body contains `permission` and
`authorization_scope`, either `{ "kind": "account" }` or
`{ "kind": "organization", "org_id": "<UUID>" }`. The bearer determines the account;
no actor, account or person selector is accepted. Duplicate JSON keys, extra fields,
zero or malformed organization IDs and incompatible scope are rejected.

| Server credential | Exact capability policy |
| --- | --- |
| `LEAVE_SERVICE_KEY` | `leave.request.own.read`, `leave.request.own.manage`, organization scope |
| `PTS_SERVICE_KEY` | `pts.poetry.read`, `pts.poetry.export`, `pts.poetry.documents`, account scope |
| `REFERENCE_SERVICE_KEY` | `reference.record.read`, `reference.record.create`, organization scope; synthetic `reference.account.read`, account scope |
| `PEOPLE_SERVICE_KEY` | Only `POST /v2/identity/organization-context` |
| `DIRECTORY_SERVICE_KEY` | Only `GET /v2/applications` |

Each optional new credential enables only its listed policy. Keys must be distinct
printable non-whitespace ASCII, including separation from KDG, Studies, Directory
and Content credentials. Missing keys disable their callers. Prefixes confer no
permission. Configure `CAPABILITY_ACCESS_DATABASE_URL` with the restricted
`access_runtime` login before enabling any of these callers. Existing KDG and Studies
credentials, their declared resources, and their existing wire errors remain separate.
KDG retains its configured organization and exact nine permissions. Studies retains
its fixed `scribeswell.studies.use` capability and explicit enrollment behavior.
The legacy PtS `/v1/check` remains unavailable pending coordinated consumer adoption.

Provider verification establishes the current account before a SQL transaction opens.
Each operation reads current profile, admission, registered scope and exact grants.
Organization checks additionally require the current organization and membership,
organization application enablement and that membership's exact bound grant. An old
membership's grant never authorizes rejoining with a new membership. Account checks
neither select nor union organization membership, person links or grants.

Authority absence returns `403 access_denied` before actor/person setup disclosure.
Authorized missing actor returns `409 identity.actor_setup_required`; Leave own
capabilities additionally require a person and otherwise return
`409 identity.person_link_required`. Account responses contain only the common UUID,
permission, scope, decision ID and UTC observation time fields. Leave own responses
add a positive decimal-string membership, person and matching own-person resource.
Reference organization responses use an explicit organization resource and do not
require a person or employment.

People's context input is exactly `{ "org_id": "<UUID>" }`. Its response contains
account, actor, organization, decimal membership, nullable person, observation ID and
UTC time. It observes current identity membership without application admission or a
capability decision; People must retain its incoming caller and own-resource checks.

Authenticated canonical callers receive failures containing only `error_id`, safe
`error` and closed `details` fields. An unknown credential on `/v2/check` consistently
retains the legacy `{ "detail": { "code": "service_access_denied" } }` envelope,
including when canonical callers are enabled; the consumer adapter treats that
unrecognized envelope as dependency unavailable.
The typed adapter maps service-policy denial to dependency failure, independently of
end-user denial. Unknown or malformed dependency responses also map to unavailable.
All current responses are private/no-store. Request reception is limited to 64 KiB
and three seconds; execution is limited to five seconds, live provider verification
to two seconds, SQL/connection execution to two seconds and SQL lock waits to one
second. Dedicated asynchronous connections close after each transaction; transaction
local context never becomes an authorization cache. Operational warnings contain
only generated trace references and selected error identifiers.

## Controlled migration and release

Apply Identity25 before Access18 through the existing coordinated migration command.
Prepare the private `access_capability_reader` as a NOLOGIN, NOINHERIT role without
administrative flags. Its only membership is the `access_migrator` SET-only edge
(`ADMIN FALSE, INHERIT FALSE, SET TRUE`). Identity25 grants only Identity schema usage
and execution of the two new current projections. Access18 grants selected local
read columns and scoped RLS, owns three fixed read-only functions with the private
reader, and grants their execution only to `access_runtime`. Runtime receives no
DML/DDL, setup commands or migration-history access. Existing KDG/Studies functions
remain unchanged. Catalog verification preserves exact prior roles and source checks;
new root-rehearsed references must be independently published before activation.

The parent delivery owns empty/previous/failure/retry migration rehearsals, previous
client compatibility, controlled owner sequencing, image freeze and activation proof.
On migration failure block dependent activation, retain output/journal and reconcile
actual database state before explicit retry. Never run migrations on startup or
reverse applied migrations automatically. Old consumers that do not enforce current
checks remain gated until their consuming delivery; enabling an Access route alone
is not evidence that an application enforces it.

## Qualification and traceability

`tests/test_capability_check.py` covers the canonical matrix, caller policy before
provider/SQL, deny-before-setup, exact resources, closed input, unavailable failures,
repeated current reads and concurrent scope separation. Existing
`test_organization_check.py` and `test_studies_access.py` protect the prior consumers.
`tests/capability_types.test.ts` compiles against generated owner types and executes
malformed/foreign resource, identity, timestamp and error-taxonomy checks.
`tests/test_capability_qualification.py` protects private fixture and disposable target
binding and output/journal reservation. Unit doubles prove control flow; actual
permissions and revocation behavior require the native qualifier.

`tests/qualify_capabilities.py --fixture <private.json> --output <new-proof.json>`
consumes only the parent-prepared explicit fixture. It never provisions accounts,
reference catalogs or a database. It validates the actual retained Leave native
container/network guard, `55581` provider, `55582` database port and a scratch name
matching `acb_88a737ddad7b_[0-9a-f]{8}`. The `network` fixture field is the actual network
ID returned by the native guard. Inputs must be a regular, nonsymlink mode0600 file.
The fixture additionally requires `api_process_id`. Before forwarding credentials,
the qualifier inspects Linux `/proc` to establish that this exact process runs the
owning Access `main:app` through uvicorn, selects the owning source directory, has
matching restricted database/provider/service-key environment values and owns the
listening socket on the exact loopback API port. Environment contents are never
printed or published. The fixture is securely opened with `O_NOFOLLOW`; its parsed
document and initial digest use the same mode0600, current-owner regular-file bytes.
The complete packaged runtime source manifest is captured before effects, including
Studies identity/contracts/access/readiness and Identity preferences. Fixture and
source bytes are checked again before recording success.

Both evidence and `.journal.jsonl` paths are reserved before effects, never overwritten,
and incomplete evidence is retained on failure. Steps use explicit HTTP expected
status/fields/absence or SQL expected rows/refusal; the qualifier does not derive
permission expectations from the implementation. Every non-success case requires its exact independent `error_id`; an unknown
credential case declares `error_envelope: legacy`. Every success case explicitly
expects account/actor identity and its declared scope, membership, nullable or
required person and resource fields as applicable. Responses must have the exact
variant shape, nonzero UUIDs, positive bounded bigint membership and valid UTC time;
status-only success or denial is insufficient. Coverage labels provide traceability
and cannot substitute for these full independent oracles.

Concurrent groups support both HTTP requests and restricted SQL transitions, with
a barrier to synchronize launch. Every nested SQL URL and expected row/refusal
oracle is validated before any effect, and nested attempts are journaled before
workers launch. Repeated SQL statements on one connection exercise context reuse. Mutating owner
commands are explicit fixture-authored transitions confined to that scratch database.
Runtime SQL proofs use the actual restricted login. Required scenario labels are
listed in the qualifier's `COVERAGE` constant, including account-only access,
mixed scopes, cross-person isolation, revocation/rejoin/re-enable, People observations,
provider failure, setup precedence and restricted runtime denials.

The focused verification commands are:

```sh
P=platform/deployment/.local/access-organization-check-20261022/owner-env/bin/python
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 "$P" -I -B -m pytest -p no:cacheprovider services/access/tests/test_capability_check.py services/access/tests/test_capability_qualification.py services/access/tests/test_organization_check.py services/access/tests/test_studies_access.py -q
```

HTTP TestClient tests need ordinary host threading in this environment; sandbox-only
runs stall independently of application behavior. The parent delivery records native
proof paths, exact commands and remaining consumer gates with Leave delivery evidence.

Scaffold impact: reuse the proven typed HTTP/generated-contract patterns; no unused
runtime framework. Shared UI, agent context and ADR impact: unchanged. Documentation:
this owner runbook plus the parent-owned delivery evidence. Private credentials,
provider tokens and business payloads remain outside published evidence.

## Current organization and application discovery

E1-DISCOVERY adds private `GET /v2/organizations?application=leave` for the Leave
credential and `application=reference` for the reference credential. Each caller can
select only its own registered application. `page_size` is a canonical integer from
1 to 100, default 100; `cursor` is a canonical 48-character base64url encoding of the
last organization UUID. The cursor carries position only. Each page reevaluates current
authority, filters eligibility before pagination and fetches one extra eligible row.
The response is `{organizations: [{org_id, name, membership_id}], next_cursor}`;
membership IDs are positive bounded decimal bigint strings. Names are display text.

The Directory credential can call only `GET /v2/applications`, without parameters or
organization selection. Its response is `{applications: [{app_id,
eligible_scope_kinds}], checked_at}`. Application IDs are unique and ordered; scope
arrays contain account, organization or both in that order. Both listing routines use
explicit registered entry capabilities. Administrative/export grants alone do not open
an application. No organization details, account selectors, grants or tokens appear in
the application aggregate. Zero memberships do not suppress account-scoped PtS access;
two accounts sharing a person retain independent discovery.

Both routes require the current bearer and exact permitted service credential before
opening a short read-only transaction. Duplicate/unknown query fields and malformed
cursors are rejected. Missing/deactivated profiles deny discovery independently of an
otherwise empty membership projection; actor/person/employment mappings are unnecessary.
The wrapper sets verified account context and a transaction-ID marker locally on its
dedicated connection, and executes one Access result statement. Missing, malformed or
inherited stale transaction context fails safely. This marker protects connection reuse;
the backend remains trusted to set verified identity under ADR-0018.

Successes and failures are private/no-store. The closed safe error envelope distinguishes
401 authentication_required, 403 service_access_denied/access_denied, 422 validation_failed,
503 authorization_unavailable and unexpected 500 internal_error. Malformed provider or SQL
results are unavailable, never empty success. The total provider-and-SQL execution budget
is three seconds, with at most two seconds each for provider and SQL and one-second SQL
lock waits. Discovery has no internal retry or positive cross-request grant cache.

Apply Identity26 before Access19 through controlled owner migrations. Stage
`identity_discovery_owner` and `access_discovery_owner` as NOLOGIN/NOINHERIT/NOBYPASSRLS
roles with no administrative flags and only their respective migrator's SET-only
membership (`ADMIN FALSE, INHERIT FALSE, SET TRUE`). Identity26 owns the narrow active
account and membership projections; Access19 owns the entry/admission/grant routines and
their account/membership RLS. Definer routines have fixed pg_catalog, pg_temp search paths,
qualified references and revoked PUBLIC/default execution. Runtime gains execution only
on the two Access routines, with no direct Identity projection or new table grant.
Like the established private Identity projection owners, the new Identity definer has
exact execution of the legacy `identity.authorize` helper so existing PUBLIC profile
policies can evaluate. Its restrictive account policies still constrain all returned
facts. That helper receives no additional runtime or PUBLIC execution grant.
The policies bind to private `access.discovery_memberships()`, owned and executable only
by the discovery definer. This lets the table-owning migrator install local policy
expressions without receiving Identity schema access.
The catalogue verification and both SQL routines reject more than 128 registered apps;
they never silently truncate eligible applications. Historical migrations and their
reference bytes remain unchanged. Migration failure blocks activation; reconcile before
retry, with no automatic rollback or startup migrations.

`tests/test_discovery.py` protects HTTP policy, closed input, dependency-result validation,
pagination, errors, no-store and provider/total-budget cancellation. The executable
`tests/discovery_types.test.ts` validates generated DTOs through the owner adapter.
`tests/qualify_discovery.py` reuses the private-file/native/process guards documented
above, but accepts only scratch names `dsc_88a737ddad7b_[0-9a-f]{8}` and fixed GET paths.
Its request fixture is `{caller, token, path, query?}` with an optional raw query string
without `?`; success independently expects all organization/page or application fields.
SQL and concurrent steps retain explicit row/refusal oracles. Seventeen mandatory coverage
labels in `COVERAGE` cover sparse/multiple-page eligibility, mixed scopes, revocation,
rejoin, exact caller/context/role isolation, PUBLIC denial, temporary shadowing, provider
failure and catalogue overflow. Coverage labels do not replace exact result assertions.
Evidence and journal are reserved before effects; source/fixture/process custody is
rechecked before success. The qualifier provisions nothing and publishes no credentials.

See [Leave discovery evidence](../../apps/leave/docs/testing/e1-discovery-evidence.md)
for actual results and remaining review/release gates. Directory/launcher adoption is
E1-LAUNCHER. Listing never authorizes a later application action. The neutral shared
API-client fixture now proves string bigint, nullable position and scope-array generation;
application policy stays with this owner. Shared UI, agent-context and ADR changes are
unnecessary for this increment.
