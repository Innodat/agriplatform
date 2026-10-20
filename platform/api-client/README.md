# App-owned OpenAPI contracts

This is build-time tooling, never a shared backend SDK. Each application owns its
Pydantic DTOs/routes, exported local OpenAPI, generated TypeScript contracts and thin
HTTP adapter. Browser business requests use that application's API (ADR-0001/0031).

The selected tool is `@hey-api/openapi-ts` **0.99.0**, invoked through its CLI with
only `@hey-api/typescript`. The actual TS7 API failure requires the tool owner's
isolated directly pinned `typescript` **6.0.3** payload; applications and
builder checks still use TypeScript **7.0.2**. npm can hoist the upstream CLI beside
root TS7, so a Node26 resolve hook in the CLI child maps only that upstream package's
bare `typescript` import to the qualified owner compiler6. The hook is not loaded
in application/compiler processes. There are no peer overrides or implicit downloads. Generated web manifests declare `@platform/api-client` as a development
dependency; resolution belongs to the shared root npm workspace lock.

After installing the declared root workspace dependencies, from a generated web:

```sh
# Run first with the API's own locked Python environment:
../api/.venv/bin/python ../api/export_openapi.py
npm run api:generate
npm run api:check
npm run test:client
npm run type-check
npm run build
```

The bin accepts exactly `--schema <local JSON> --output <generated directory>` and
optional `--check`. DTO edits require re-export before regeneration. Use the exporter
`--check` as well as `api:check` to detect stale schema and generated output. No public
OpenAPI route, remote reference or tool configuration discovery is needed. The wrapper
invokes the pinned CLI with an explicit temporary config and local-only schema. The
output must be a dedicated generated subdirectory outside the schema's directory.

Generated `types.gen.ts` and `index.ts` use the existing builder installer and its
`.generated-files.json`, lock, journal and recovery protocol. Source identity is the
schema hash; generator/template/recipe identities stay fixed. Check does not mutate
the target. Generated edits, missing ownership metadata and incomplete installation
refuse; ordinary regeneration preserves all adjacent owner/custom code. Do not edit
derived clients. Explicit dead-writer recovery uses the existing builder installer;
this wrapper never guesses recovery or creates a second journal.

Failures expose identifiers such as `api_client_stale`, `api_client_schema_invalid`,
`api_client_tool_invalid`, `scaffold_conflict` and `scaffold_recovery_required`; raw
schema/tool/exception text is never emitted. The generated owner health adapter keeps
HTTP failures and malformed responses safe, performs one bounded own-API GET and
uses generated `HealthResponse` while rendering only API availability.

Verification: `node --test platform/api-client/tests/*.test.mjs` under selected
Node26.11.1 after declared tooling installation; the existing builder application
proof runs fresh copied-workspace installation, stale DTO/type failure, regeneration,
custom preservation, tamper refusal and real browser success/outage. See
[EVIDENCE.md](EVIDENCE.md) for exact commands/results and compatibility qualification.

Scaffold impact: thin tool, owner DTO/export/client seeds, installer-owned derived
subdirectory and consuming proof. Shared UI: no promotion; availability is owner
presentation. Agent context: generated commands and ownership rules updated. Docs:
this runbook and consuming owner guidance. ADRs: existing0001/0031/0059 apply, accepted
decisions unchanged. Public generation, Auth/Access candidates and readiness remain
unpromoted. No business endpoint, database, release or application authorization is
implemented by this health-only proof.
