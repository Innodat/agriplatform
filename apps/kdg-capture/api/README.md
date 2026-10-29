# KDG current-context API

Bounded read-only API prerequisite of Story 1.1. This is neither the complete entry
story nor a domain persistence, browser authentication, offline or release implementation.
The existing builder renderer/installer supplied the HTTP/error/export seeds; this
app owns main.py/context.py. Never edit generated safe_errors.py or generated contracts.

`create_app(org_id=..., access_url=..., service_key=...)` constructs the configured API;
all three values are server-controlled. Only HTTPS Access origins without credentials,
paths, queries or fragments are accepted. Use a restricted KDG service key. Browser
requests supply only their bearer, never a service credential. The module's default
app deliberately has no configured authority and refuses context with503; no live
configuration or deployment entry point was installed. The optional transport parameter
is a synthetic test seam and is never selected by request data.

GET /api/v1/context forwards the bearer to current Access /v2/check for exactly
capture.read.own in the configured organization. Access verifies bearer identity;
KDG validates closed typed authority and account/resource binding. It does not decode
JWT roles, read shared tables, cache decisions, or create an offline lease. Checks
are fresh per request. Access waits total at most3s including body; total execution
and request-body receipt at most10s. Encoded Access responses are refused before body consumption; identity response bytes are bounded16KiB. checked_at must
be UTC within the request interval allowing1s cross-host clock skew; monotonic asyncio
timeouts bound elapsed time independently. Client disconnect/process termination is
not a guarantee of transport cancellation. There are no business locks or writes.

Safe errors use the builder adapter's stable error_id envelope. Current Access's
legacy detail.code is adapted only for exact401 authentication_required,403 access_denied
and409 identity.actor_setup_required. Other downstream status/error combinations,
malformed/foreign evidence, timeouts and unavailable verification map to503
 authorization_unavailable. Caller query/body selectors return422; absent/malformed
bearer returns401. Every response carries private, no-store. No raw downstream messages,
credentials, decisions or request/response payload dumps are logged.

The Python owner uses pyproject.toml/uv.lock, approved direct baseline pins and an
independent environment. No root dependency/lock update is required. Tests use synthetic
httpx transports; they do not qualify real Entra, deployed network policy, current
restricted SQL, browser authentication or physical devices. The separately recorded
Access owner evidence supplies historical native SQL proof, not new consuming proof.

From repository root, with P the absolute owner environment's bin/python and N the
selected Node26.11.1 executable:

```sh
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 "$P" -I -B -m pytest apps/kdg-capture/tests/test_context_api.py -q -p no:cacheprovider
"$P" -B apps/kdg-capture/api/export_openapi.py --check
"$N" platform/api-client/src/cli.mjs --schema apps/kdg-capture/api/openapi.json --output apps/kdg-capture/contracts/generated --check
"$N" node_modules/typescript/bin/tsc --project apps/kdg-capture/tests/tsconfig.json
```

Generate by running the exporter and client tool without --check. Export uses -B,
not -I: its builder seed imports its sibling main.py. Client generation requires the
existing declared tool installation (upstream0.99.0/tool-only TS6.0.3); application
checks use approved TypeScript7.0.2. See ../docs/CONTEXT_API_EVIDENCE.md for selected
retained tooling paths, exact local verification and limitations. No package download
or dependency update fallback is authorized by these commands.

Scaffold impact: consume existing renderer/installer/errors/export/client generator;
no new generic pattern promoted. Shared UI: none in this API slice. Agent context:
root instructions suffice; actual commands are here. Documentation: this guide, evidence,
Build spec and appended handoff. ADRs: existing ownership/access/logging/API decisions;
no new or modified accepted ADR. Fingerprints/HMAC remain deferred.

## Explicit configured startup factory

`runtime:create_app` is an owner-owned ASGI factory. Its context policy reads KDG_ORG_ID,
KDG_ACCESS_URL and KDG_SERVICE_KEY from the server environment at construction; all
three are required. Invalid/missing policy raises only kdg_context_configuration_invalid.
An explicitly supplied mapping overrides environment discovery, including an empty
mapping; it never merges ambient authority. Existing main:app stays unconfigured and
refuses503. No environment file, secret, grant, migration or deployment configuration
is installed by adding this factory. The optional Python transport argument remains
an explicit test seam, never a request option or automatic TLS bypass.

The bounded native acceptance is separate from normal unit tests:

```sh
"$ACCESS_PYTHON" -I -B apps/kdg-capture/tests/qualify_configured_context.py --run
```

It requires the already resumed retained synthetic run and authoritative reviewed3
Access fixture, approved Access environment, existing /usr/bin/openssl and loopback
sockets. It never invokes preparation or modifies retained business data. New exclusive
private proof directories retain certificates, logs and exact source capsules; no
resource deletion or automatic historical-proof refresh. Test-only trust verifies its
local certificate. Two isolated server processes communicate over actual HTTP/TLS;
Access uses restricted runtime SQL plus an explicit synthetic bearer verifier.

See [configured-context evidence](../docs/CONFIGURED_CONTEXT_EVIDENCE.md). Native Access
test-server draining has an explicit3s bound; a TLS idle-connection timeout warning is
retained. Process exit0 does not assert a fully graceful deployed drain. Earlier forced
termination attempts remain. Real provider/browser/device, rolling release and deployed
server timeout/pool behavior are separate gates.

For an explicitly configured **local** factory start, after supplying the three
server environment values through the approved local operator environment:

```sh
"$P" -I -B -m uvicorn --app-dir apps/kdg-capture/api runtime:create_app --factory --host 127.0.0.1 --port 8188 --no-access-log
```

This documents the entry point; it installs no target configuration and authorizes no
real service use. The native qualification separately exercises this exact import/
--factory resolution in a fresh process, with one unauthenticated401 then automatic
exit. Its ordinary TLS consumer uses an explicit private local CA test transport.
The optional `--interrupt-probe` qualification intentionally sends SIGTERM to its own
runner after both test servers start. It must retain failed/interrupted evidence,
bounded child exits and a successful independent after-inspection, then exit143.

## Configured administrator reads

The same explicit factory enables the reviewed administrator read handlers when
all three additional server inputs are supplied:

| Input | Rule |
| --- | --- |
| `KDG_ADMIN_READ_DATABASE_URL` | Explicit PostgreSQL URL for exactly `kdg_capture_runtime`; existing bounded numeric-host read engine policy applies |
| `KDG_IDENTITY_URL` | Fixed HTTPS Identity base URL, without userinfo, query, fragment or application path |
| `KDG_ACTOR_DISPLAY_SERVICE_KEY` | Dedicated32–256 visible ASCII display credential, distinct from every other supplied service key |

All three absent preserves context-only behavior and imports. Partial, empty,
invalid, wrong-role or duplicate-key activation fails construction with only
`kdg_admin_configuration_invalid`. Explicit mappings never merge ambient values.
The API lock declares SQLAlchemy2.1.4 and Psycopg[binary]3.3.6, matching the existing
approved native owner runtime; no dependency version upgrade is required.

Enabled routes are GET `/api/v1/admin/captures`,
GET `/api/v1/admin/captures/{capture_id}` and
GET `/api/v1/admin/captures/{capture_id}/audit-details`, alongside the existing
GET `/api/v1/context`. There are no administrative write routes. Each read checks
current exact organization `capture.read.all`; own access never supplies a
fallback. Audit-details releases its business connection before selected-ID
Identity lookup, then requires final matching current authority before publishing.
Existing safe errors, original deadlines, cancellation ownership, private/no-store
responses, immutable definitions and original audit attribution remain binding.

Construction performs no checkout or migration. The two candidate apps retain
their closure-bound lazy engines; FastAPI router composition retains both
lifespans and disposes each engine after requests drain. The existing context
client remains owned by its original lifespan. The optional `identity_transport`
argument is a synthetic seam like `transport`, never browser configuration or an
automatic TLS bypass.

`app.openapi()` composes the existing owner-exported route schemas and refuses
ambiguous component definitions. The configured contract is exported offline by
`export_configured_admin_openapi.py` to `configured-admin.openapi.json`; its
`--check` mode detects staleness without constructing a database engine. Existing
`main:app`, `openapi.json`, context-generated types and isolated administrator
contracts retain their independent compatibility boundaries.

The local migration policy retains `kdg-local` at port55482. A fresh Story3.1
synthetic run explicitly uses target `kdg-story31-synthetic` with
`KDG_MIGRATION_SYNTHETIC_PORT` matching its canonical selected URL port and differing
from55482. All prior loopback, disposable-environment, restricted-migrator and
`kdg_schema_<32hex>` database checks remain. This creates no resources, performs no
automatic migration, and authorizes no retained-target cleanup or production use.

Impacts: existing bounded owner/scaffold primitives reused without new generic
promotion; shared UI unchanged; current agent context sufficient; configuration,
schema and owner runbooks updated; existing ADRs remain unchanged. Focused HTTP
tests use synthetic authority/storage; full native/TLS/Auth/browser evidence and
remaining Story3.1 acceptance belong to their explicit qualification.

## Inert questionnaire definition candidate

questionnaire.py owns the schema-version1 definition model needed before Story1.2's
first persistence/read slice. parse_definition accepts bounded UTF-8 JSON, rejects
unknown shapes/duplicate keys or IDs/coerced scalars, and raises only
kdg_capture.invalid_questionnaire_definition at its public domain boundary. Raw model
validation diagnostics are internal; the later HTTP boundary owns safe field paths.
Rating/boolean/text are ordinary Pydantic discriminated models, not a form engine.

initial_definition requires four explicit stable canonical question UUIDs. It returns
only the approved Afrikaans definition with exact order/defaults; it allocates no IDs,
creates no published record, reads no target/configuration and performs no I/O. The
immutable Python model is not a database immutability guarantee or a rendered form.
Use model_dump(mode='json', exclude_none=True) for plain definition serialization.

No new HTTP route/OpenAPI/client schema is exposed yet. The future version endpoint and
write adapter must reuse this owner model after their remaining readiness gates pass.
This does not implement answer validation, scoped persistence, publication/replay,
operator authority or provisioning. Fingerprints/HMAC remain deferred.

```sh
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 "$P" -I -B -m pytest apps/kdg-capture/tests/test_questionnaire_definition.py -q -p no:cacheprovider
```

P is the existing approved platform/deployment/.local/kdg-context-20261022/owner-env/bin/python.
No install or dependency/lock change. See ../docs/QUESTIONNAIRE_DEFINITION_EVIDENCE.md.

## Capture command input boundary

`capture_commands.py` is app-owned pure validation for future create/edit persistence.
Use parse_create/parse_edit before outcome lookup, then validate_answers with the exact
original QuestionnaireDefinition only for a fresh action. Do not validate retry answer
semantics before recovering a currently authorized committed outcome. Opaque eligibility
reference is not a grant. No handler/router, authorization or database writes are added.
Safe CommandError identifiers are validation_failed and unsupported_command_version;
never expose raw validation dictionaries or exception locals. Default model serialization
preserves omitted boolean details and exact entered text/device time. See
[capture evidence](../docs/CAPTURE_COMMAND_VALIDATION_EVIDENCE.md). Run optional unit tests:
`env PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 "$P" -I -B -m pytest -q -p no:cacheprovider apps/kdg-capture/tests/test_capture_commands.py`
using the retained owner environment above.

Pydantic field freezing does not freeze the nested answers dictionary. Keep parsed
commands private and revalidate with validate_answers immediately before consuming a
fresh write; its instance revalidation protects modified/constructed nested models.
These models are not an immutable queued-command envelope or authority evidence.

## Configured own APIs — 2026-10-28

`runtime:create_app` now optionally composes the established own setup, create,
edit/context, operation recovery, history and detail handlers. Supply both
`KDG_OWN_DATABASE_URL` and `KDG_QUESTIONNAIRE_ID` alongside the existing fixed-org
Access settings. The database URL must select the exact `kdg_capture_runtime` login
and satisfy the existing numeric-host/bounded-connection policy; the questionnaire
must be a canonical nonnil UUID selected by the server. Neither value is a browser
selector. Partial/invalid settings fail closed with `kdg_own_configuration_invalid`.
Omitting both preserves context-only or administrator-only behavior.

The composed own routes are GET `/api/v1/provision`, GET/POST `/api/v1/captures`,
GET/PUT `/api/v1/captures/{capture_id}`, GET
`/api/v1/captures/{capture_id}/edit-context`, and GET
`/api/v1/operations/{operation_id}` with its required command discriminator. Their
existing independent current Access checks, scope/ownership, original-definition,
first-committed retry, deadlines, cancellation/drain and safe private/no-store
behavior stay with their owning handlers. No administrator write route is composed.
GET/POST and GET/PUT sharing a path remain separate operations; duplicate methods
and conflicting component definitions are refused.

Each candidate retains its closure-owned lazy engine and lifespan. Construction and
startup perform no checkout, migration, seeding or automatic delivery. The context
client and all enabled engines close after host request drain. Candidate0003 must be
applied through controlled migration before native provision activation; a failed
migration blocks activation and requires explicit reconciliation/forward retry.

The new configured schema gives each own owner's DTOs a stable `Own<Owner>` prefix,
rewriting local references and discriminator mappings without changing any isolated
owner declaration or generated client. This preserves differing existing declarations
that use the same component name. `export_configured_own_openapi.py` exports own-only
`configured-own.openapi.json` and combined own/administrator `configured.openapi.json`
without constructing an authority or engine. Existing configured administrator and
isolated schemas remain independently owned and unchanged. Combined types live in
`../contracts/configured-generated/` and are generated only by the platform API-client
owner; the runtime still validates every boundary independently of TypeScript.

Using the approved Python and retained Node/API-client owner from repository root:

```sh
"$P" -I -B apps/kdg-capture/api/export_configured_own_openapi.py --check
"$N" platform/deployment/.local/scaffold-application/proof-dI2Gy9/root/platform/api-client/src/cli.mjs --schema apps/kdg-capture/api/configured.openapi.json --output apps/kdg-capture/contracts/configured-generated --check
"$P" -I -B -m pytest apps/kdg-capture/tests/test_configured_own.py apps/kdg-capture/write-tests/test_provision_migration.py -q -p no:cacheprovider
```

This API prerequisite does not mount the own capture/history PWA, introduce offline
all-read authority or complete Story3.1. Actual restricted native/HTTP qualification,
controlled rollback/retry and previous-running-consumer compatibility are recorded
separately by the coordinator. Existing retained fixtures/evidence remain unchanged.
Scaffold: existing transaction/migration tools reused, no neutral change. Shared UI
and agent context unchanged; owner documentation/exports updated; existing ADRs apply.

Native1000-child setup exposed an N+1 query timeout under the original ten-second
budget. Provisioning now selects the same bounded ordered IDs, acquires their exact
existing advisory keys in one UUID-ordered query, rereads the complete selected child/
assignment set in a separate post-lock READ COMMITTED statement, then issues references
in one atomic INSERT. Each statement still uses the original remaining-budget limits.
Returned rows are matched by opaque reference and child, with exact completeness and
uniqueness checks before response validation/commit; RETURNING order is not assumed.
No migration, cap, authority, time budget or wire contract changed. PostgreSQL's
[SELECT-list evaluation guarantee](https://www.postgresql.org/docs/17/sql-select.html#SQL-SELECT-LIST)
places the volatile lock expression after UUID sorting because that expression is not
a sort/group/distinct key. Existing namespace/version and coordinator locks remain.
Actual load success is established separately by the coordinator's restricted native
proof; recorded-connection count tests establish control flow, not native latency.
