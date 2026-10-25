# Candidate recovery OpenAPI/client contract — 2026-10-25

The candidate exposes documentation matching its existing manual HTTP contract.
`recovery_openapi.py` derives metadata from FastAPI/Pydantic models, command literals,
canonical UUID metadata, signed-bigint bounds and the handler's safe error pairs.
`recovery_http.py` factors the same route registration for a schema-only app with no
engine or authority. Runtime factory policy, validation order and transaction behavior
remain protected by the existing24 characterization cases; no active route was added.

`export_recovery_openapi.py` writes deterministic candidate-only JSON or checks freshness
without writing. It needs no configuration/credentials, engine or Access client.
The existing platform generator installs separate types-only output in
`contracts/recovery-generated`, including its ownership manifest. Generated files are
never hand-edited; change metadata/export and regenerate. The active context schema,
generated types and startup remain unchanged. No API dependency adoption occurs here.

| Requirement | Evidence |
| --- | --- |
| Required closed command discriminator, canonical UUID, Bearer | Schema parameter/security assertions; existing strict HTTP boundary tests |
| UUID/revision exact string boundaries | Draft202012Validator rejects prefixes, suffixes, uppercase/nil UUID, trailing newline, leadingzero and signed-bigint overflow |
| Required serialized unresolved status and original v1 receipt | Actual create/edit at revision9223372036854775807 and unresolved validate against exported success union |
| Status-specific safe errors and headers | Every declared HandlerError pair through synthetic ASGI, full response schema and header validation |
| No export engine/network I/O | Fresh isolated process installs engine/http/socket sentinels before imports; repeat exports identical |
| Drift detection | Real committed artifact --check, missing/stale temporary checks and platform generated-type --check |
| Typed consuming contract | TS7.0.2 positives, status narrowing and12 negative compile cases |

ATDD observed5 contract failures before implementation. Final **158 affected tests**
pass, including **10 contract cases**. Candidate and active context TypeScript fixtures,
both schema freshness checks, candidate generation freshness and three scaffold parity
checks pass. Review raised6 findings, all fixed; individual triage is in the
[delivery record](../../../_bmad-output/implementation-artifacts/spec-kdg-recovery-contract.md).
No expected response was weakened to bypass the multi-request fixture issue discovered
during expanded success coverage; each outcome now uses a fresh synthetic pool.

The checkout lacks installed generator dependencies and its direct CLI safely refused
`api_client_tool_invalid`. As in earlier context evidence, the already retained G at
`platform/deployment/.local/scaffold-application/proof-dI2Gy9/root/platform/api-client/src/cli.mjs`
was used after all four generator sources and installer byte-matched current source.
G qualifies pinned upstream0.99.0 and tool-only compiler6.0.3; application compilation
uses existing TypeScript7.0.2. Standard schema validation uses existing
`/usr/bin/python3` with jsonschema4.10.3, version-checked by the test adapter. No install,
download, dependency manifest, lockfile or retained generator mutation occurred.

Generated types are compile-time contracts: UUID/revisions remain TypeScript strings,
Bearer tokens come from the future owning transport, and there is no generated runtime
SDK, response validator or browser activation. OpenAPI documents closed query behavior;
its parameter syntax alone does not enforce unknown/duplicate rejection. Schema closure
is qualified against actual synthetic wire bodies, not assumed from TypeScript.

Historical native receipts/capsules remain unchanged and bind their original versions.
The metadata owner is included in the native qualifier's future source capture; this
delivery does not rerun native qualification or refresh a historical proof. Docker stays
stopped, retained rows/ledger/sentinel/resources untouched. Native edit, cancellation,
TCP drain, real Access, API dependency/startup adoption and ADR-0020 activation remain
gates. No runtime handler storage/authorization fix was required.

Scaffold: existing generic types generator/ownership installer reused; no new generic
SDK or runtime mechanism. Shared UI, agent context and ADR: none. Contracts/handoff and
source evidence updated together. Fingerprints/HMAC deferred. No Leave/editor,
real-account/access, production, provisioning, deployment, pilot or cleanup work.
Exact commands and source/tool digests are in the
[source-bound receipt](evidence/recovery-contract-20261025.json).
