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
