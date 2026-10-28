# Explicit retained actor display runtime

`main:create_app` now mounts the reviewed
`POST /v2/identity/actor-displays` owner contract. The route is present in the
active OpenAPI even when disabled. Existing isolated candidate exports remain
separate and unchanged. This source integration grants no real credentials or
production activation; local native/socket evidence belongs to the consuming
Story 3.1 delivery.

The factory reads server environment policy once, or takes the explicit
`actor_display_configuration` mapping. An explicitly empty mapping stays disabled
and never merges ambient display policy. No connection or migration runs during
construction. Requests with disabled policy return private403 before body or
native-reader I/O.

| Server input | Rule |
| --- | --- |
| `KDG_ACTOR_DISPLAY_SERVICE_KEY` | Required active dedicated display credential when enabled; existing32–256 visible ASCII bound |
| `KDG_ACTOR_DISPLAY_PREVIOUS_SERVICE_KEY` | Optional distinct previous credential during coordinated rotation |
| `KDG_ACTOR_DISPLAY_ORG_ID` | Required fixed canonical nonzero organization UUID |
| `IDENTITY_ACTOR_DISPLAY_DATABASE_URL` | Required complete explicit private PostgreSQL URI or libpq conninfo, with host, port, database, password and exactly `identity_actor_display_runtime` |

Omit all four inputs to disable. Any partial, blank, invalid, privileged-login or
duplicate-key policy refuses construction with only
`actor_display_configuration_invalid`. Both display keys must differ from every
other supplied `*_SERVICE_KEY`; neither permits other owner operations. The native
reader retains its existing refusal of ambient service/host-address selectors.
Connection representations, policy values and raw diagnostics remain private.

Coordinate Identity28 through the existing controlled migration lane before an
enabled instance is activated. A failed migration blocks activation; preserve its
data and evidence, reconcile the failure, then retry forward. Startup does not run
migrations, create roles or verify them using a privileged fallback. The reader
uses its restricted projection at request time under the original three-second
operation deadline and closes each owned unpooled connection.

The coordinated fresh upgrade exposed one Access19 catalogue compatibility issue:
only `discovery_functions` differed. Its published ten-row observation included
inherited EXECUTE on `handle_new_user()`, `log_audit()` and `set_audit_fields()`;
Identity28 deliberately removes those three unsafe trigger-attachment permissions.
The Access verifier now recognizes the exact `identity.actor_displays(uuid[])`
signature and requires all three permissions to remain absent. It adds only their
historical tuples to a comparison copy before checking the unchanged reference.
Raw snapshots retain the actual seven-row observation; unrelated function changes,
restored helper execution and every other catalogue difference still fail. No
historical migration/reference or database privilege is changed by this repair.
The marker uses only `pg_proc`/`pg_namespace` metadata with exact function kind and
one `uuid[]` input; it never resolves the Identity function through `regprocedure`.
Qualification must prove that actual `access_migrator` lacks Identity schema USAGE
before and after a successful controlled Access19 retry/repeat, while previous and
current consumers still work. No cross-owner USAGE grant is needed or permitted by
this compatibility repair. Controlled upgrade/repeat and consumer evidence remain
required independently of the focused catalogue doubles.

For rotation, add the new active key while retaining the old key as previous,
switch the KDG backend, verify new-key requests, then remove previous and verify
old-key denial. The fixed-organization policy applies equally to both keys.
Configuration is server-held; never send it to the browser or copy real values
into examples, proof output or source control.

`deployment/verify_runtime.py` and the Docker context allowlist include the runtime,
HTTP, contract and native reader modules. Frozen bundles bind each source to its
authoritative owner input; a missing or stale display module refuses verification.
Regenerate `openapi.json` through `export_openapi.py` and derived wire types through
the existing platform client generator. The active export includes concurrent
owner routes, including People setup; do not replace it with the isolated display
schema.

Scaffold: reuse the proven native reader, owner router, controlled migrations and
frozen package verifier; no new neutral runtime pattern is promoted. Shared UI:
unchanged. Agent context: existing owner/lifecycle rules suffice. Documentation:
this configuration runbook and KDG's active-read guidance. ADR: implements the
existing release, transaction, logging, error and actor decisions without changing
accepted ADRs. Native permission, owner TLS, real Auth and browser/device evidence
are distinct from focused factory tests; Story3.1 remains incomplete until its full
acceptance matrix passes.
