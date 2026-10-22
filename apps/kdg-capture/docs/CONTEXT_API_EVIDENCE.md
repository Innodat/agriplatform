# KDG current-context API evidence — 2026-10-22

Complete for this bounded API prerequisite; final reviewed closure is below.
This is the first bounded KDG HTTP consumer, the API prerequisite within Story1.1.
No KDG business persistence, whole-story entry, browser or offline readiness is claimed.

## Selection and authority

bmad-help resolved repository configuration and catalog, then selected [BD] bmad-build
for the selector-free current context API explicitly independent of /provision in
[approved Story1.1](epics.md#story-11-sign-in-and-enter-the-authorized-khula-context).
KDG was docs-only. Story1.2 persistence needs its own operator/immutable-version contract;
capture first-commit-wins does not convert that operator. No fingerprint work is selected.
[Current contracts](contracts.md), [shared owner contract](../../../platform/docs/architecture/contracts/kdg-shared-readiness.md),
[Access owner evidence](../../../services/access/ORGANIZATION_CHECK_EVIDENCE.md),
[neutral WRITE evidence](../../../platform/builder-cli/WRITE_FIRST_COMMITTED_EVIDENCE.md)
and ADR0061 were read. WRITE49 is neutral historical proof, not KDG capture acceptance.

Baseline full Git ID and all existing tracked source hashes are in
/tmp/kdg-context-preservation.json. The starting dirty tree is concurrent authorized
work and remains excluded. Existing builder renderer/installer provided three API
seeds: main.py, exporter and unchanged generated safe_errors.py. The manifest records
original seed hashes; owner main.py changes are permitted by installer ownership.
No general generator, new service, migration, database, grant, environment target,
Docker command, resource reset, real account or external provisioning was used.

## Behavioral ATDD and focused TDD

Before implementing /context, the acceptance exercised the actual health-only
scaffold with TestClient and expected an authorized current context. It failed with
HTTP404/error_id resource_not_found (not an import failure):

`timeout 60s env PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 P0 -I -B -m pytest apps/kdg-capture/tests/test_context_api.py -q -p no:cacheprovider`

Observed **1 failed0.56s**, test_authorized_context_is_current_and_exact,
assert404==200. P0 was the existing approved Access owner qualification environment.
The initial sandbox TestClient stalled and was interrupted; the confirming bounded
outside-sandbox run produced the behavioral RED before implementation. Its result is
retained in the session tool transcript; /tmp/kdg-context-behavioral-red.log is the
interrupted attempt, not claimed as a complete failing-test log.

Focused negative cases were written before implementation but not separately run RED;
initial combined run passed36. Subsequent focused schema TDD first observed **45 passed,
1 failed** at test_context_identifiers_publish_uuid_schema, KeyError format, before
adding UUID metadata. Confirming run passed46. Additional hostile-wire cases passed54.
This distinguishes observed behavioral/schema RED from test-first claims not executed.
No existing expectations were changed to dismiss an unexplained failure.

## Reproduction and current verification

P: absolute platform/deployment/.local/kdg-context-20261022/owner-env/bin/python.
P0: absolute platform/deployment/.local/access-organization-check-20261022/owner-env/bin/python.
N: absolute platform/deployment/.local/kdg-toolchains/ad277eef-a10e-4aac-bb82-5743653fb2e0/payload/node/bin/node.
U: absolute platform/deployment/.local/kdg-toolchains/0cc4bc48-505e-41c1-8876-25b2d49b5694/payload/uv/uv.
CP: payload/python/bin/python3.15 beside U's payload/uv directory.
C: absolute platform/deployment/.local/python-baseline-qualification/cache.
G: platform/deployment/.local/scaffold-application/proof-dI2Gy9/root/platform/api-client/src/cli.mjs.
D: platform/deployment/.local/kdg-context-20261022.
All commands ran from repository root. P/N/U abbreviations denote selected executables,
not shell defaults or downloads.

- `UV_CACHE_DIR=C U lock --offline --no-build --no-config --no-python-downloads --python CP --project apps/kdg-capture/api`: exit0,24 resolved packages. Independent app lock; published baseline/root and owner locks unchanged.
- `UV_PROJECT_ENVIRONMENT=<D/owner-env> UV_CACHE_DIR=C U sync --frozen --offline --no-build --no-config --no-python-downloads --python CP --project apps/kdg-capture/api`: exit0,22 installed approved distributions into a new environment, no download/build fallback.
- `timeout 60s env PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 P -I -B -m pytest apps/kdg-capture/tests/test_context_api.py -q -p no:cacheprovider`: **54 passed1.19s**, D/pre-review-tests.log. Existing httpx/TestClient upstream deprecation warning retained; no unapproved httpx2 dependency added.
- `P -B apps/kdg-capture/api/export_openapi.py`: exit0; same with --check: openapi_current. An earlier -I export failed safely because the unchanged seed expects sibling imports; documented command uses -B.
- `N G --schema apps/kdg-capture/api/openapi.json --output apps/kdg-capture/contracts/generated`: api_client_generated. Current checkout lacks installed tool dependencies, so its direct CLI refused api_client_tool_invalid. All four generator sources and installer were byte-compared with retained G and matched. G uses retained pinned upstream0.99.0 and isolated tool compiler6.0.3; no old resource/source is changed. Sandbox generation refused; normal outside-sandbox execution passed.
- `N node_modules/typescript/bin/tsc --project apps/kdg-capture/tests/tsconfig.json`: exit0 using existing application TypeScript7.0.2, strict typed own-scope/string-member/no-query contract fixture.

## Requirement mapping and limits

| Requirement | Consuming tests |
| --- | --- |
| A01 current exact entry, repeated request observes denial | test_authorized_context_is_current_and_exact |
| A14 selector/account/org/permission/actor/member/decision scope | selector_free, malformed_or_mismatched_authority, duplicate_authorization_header tests |
| A01 safe denial/setup/unavailable distinction | error_adaptation_is_closed_and_safe; transport_failure_is_safe |
| Bounded execution, strict source bytes and configuration | slow_access_has_one_bounded_total_wait; invalid_upstream_wire; invalid_configuration tests |
| Pydantic/OpenAPI/TypeScript consistency | context_identifiers_publish_uuid_schema; exporter/client --check; strict TS fixture |

The HTTP acceptance uses actual KDG ASGI/TestClient and synthetic httpx downstream
responses. It proves KDG's consumer request, binding, denial and fail-closed behavior,
not current real Access SQL or provider verification. Native historical Access evidence
remains source-bound to its owner. No consuming loopback socket, live provider, real
service credential or cross-owner database qualification is claimed. Runtime factories
accept explicit server policy; the default import app is unconfigured and refuses503.
Browser sign-in/return/accessibility and actual current SQL→KDG integration remain
Story1.1 follow-ups before whole-story completion. No first-commit-wins capture consumer,
frozen queue, domain assignment, device, backup/restore or release readiness is inferred.

Scaffold: consume existing seeds/installer/generator without pattern promotion. Shared
UI: unchanged. Agent context: root instructions suffice; actual commands in API README.
Documentation: this evidence, API README, Build spec and additive handoff. ADR: adopts
existing decisions without changing accepted bytes. Fingerprints/HMAC remain deferred.

## Final reviewed closure

Configured oneshot Blind Hunter completed. All nine findings were assessed in the
[Build triage](../../../_bmad-output/implementation-artifacts/spec-kdg-current-context-api.md#review-triage-log)
and patched; no new review deferral. Review correction tests observed **9 failed,
61 passed1.27s** before changes. After correction, **70 passed1.23s**. The source now
normalizes case-insensitive bearer schemes for the Access owner, rejects invalid
origin ports at construction and encoded responses before reading/decompression,
requires exact UTC timestamp grammar and publishes nonnil/bigint constraints. Added
stalled inbound, streamed-body close/deadline and exact freshness boundary proof.
Those previously passing timeout behaviors are not represented as repaired bugs.
A separate focused unexpected-error test first caught missing500 schema metadata;
it observed54pass/1fail before metadata/regeneration, while safe runtime500 already
worked. Generated errors remain byte-identical to their owning template.

Final exact checks use the commands above:

- KDG owner P matrix: **70 passed1.51s**, D/final-kdg-tests.log.
- P0 same flags with `services/access/tests/test_organization_check.py apps/kdg-capture/tests/test_context_api.py`: **130 passed3.05s**, D/final-affected-tests.log.
- `N G ... --check`: api_client_current; D/final-client-check.log.
- `P -B apps/kdg-capture/api/export_openapi.py --check`: openapi_current; D/final-export.log.
- Strict contract TypeScript check: exit0; D/final-types.log. Explicit compiler --version reports7.0.2.
- `P -B tools/py/run_compose_supabase.py --check-only`: exit0, dry run/no files changed; D/verification-2.log. No KDG database objects are added.
- Existing renderer/installer replay with the same three seeds: exit0, owner source and generated adapter preserved. No public generator readiness is implied.
- Scoped whitespace and custody checks pass. No root test/lint/CI or whole-repository build is claimed.

[Durable source/result custody](evidence/context-api-20261022.json) retains the canonical
baseline Git ID, selected unchanged protected source hashes, original builder seed
provenance, final tested API/DTO/type source hashes and non-sensitive executed result
excerpts with exact local-log digests. It also records the initially observed404
behavioral RED as a transcript witness, not a fabricated complete log. Local private
paths remain reproduction context, not the only surviving evidence.

The branch advanced concurrently through Scribeswell work during this session.
External tracked-byte changes in shared planning, Leave and Scribeswell were observed,
excluded and left untouched; no claim that all repository bytes remained static.
The original handoff tail, relevant shared owners/historical WRITE and published
baseline/root locks remain byte-preserved. No Docker/start/stop/reset/prune or cleanup
command ran. The only new environment is the isolated local Python qualification env.
The scoped local Build commit is not pushed.
