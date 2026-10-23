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

`runtime:create_app` is an owner-owned ASGI factory. It reads exactly KDG_ORG_ID,
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
