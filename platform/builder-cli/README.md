Current Auth maintenance, 2026-10-23: [the Auth parity record](AUTH_PATTERN_EVIDENCE.md)
adds a neutral lifecycle/React hook and generated behavioral tests to the active application
renderer. KDG uses managed copies checked against the current templates, including tests.
Use selected Node with `scripts/sync-kdg-auth.mjs --check` from this directory; use --write
through that script after template updates. Builder tests enforce parity. Reusable consumer
fixes update scaffold code/tests alongside the consuming delivery, not after app completion.
The separate legacy templates/web AuthContext is now explicitly retired; it is not a safe
copy path. Older proof descriptions below are historical within their original scopes.

# platform/builder-cli

Capability-scope direction: [ADR-0053](../docs/architecture/decisions/0053-capability-scoped-access-in-mixed-scope-applications.md)
requires scope per protected capability, including mixed-scope applications. Generate
typed scope checks and optional organization navigation; never force every application
through membership or infer public API authority from tables. Prove account and
organization variants in first-consumer fixtures before promotion. Not implemented.

**Status:** Read-only P1/SERVICE recipe preflight plus an internal disposable service
and application bootstrap harnesses. Public generation remains undelivered; all patterns stay candidates.

## Disposable service bootstrap

`test:generation` is the service candidate-bootstrap entry. It accepts no arguments or
write target, validates a synthetic service recipe through existing preflight, and
creates a private fresh `platform/deployment/.local/scaffold-generation/proof-*/output`.
Every previous output is preserved, including failures. Application recipes and
nonempty extensions are refused by the internal renderer. Historical backend templates
remain intact. No public generator, candidate flag, regeneration or installation journal
is implemented. Health/error proof does not implement service authentication/current Access.

From repository root with the selected Node26.11.1/npm12.2.0 on PATH:

```bash
export SCAFFOLD_UV="$PWD/platform/deployment/.local/kdg-toolchains/0cc4bc48-505e-41c1-8876-25b2d49b5694/payload/uv/uv"
export SCAFFOLD_PYTHON="$PWD/platform/deployment/.local/kdg-toolchains/0cc4bc48-505e-41c1-8876-25b2d49b5694/payload/python/bin/python3"
export UV_CACHE_DIR="$PWD/platform/deployment/.local/python-baseline-qualification/cache"
npm run test:generation --workspace platform/builder-cli
```

Explicit absolute executable/cache paths are required. The harness checks uv0.13.1
and ordinary CPython3.15.0 and never selects host Python or downloads a runtime.
The current qualification scope is Linux x86_64; generated uv resolution is Linux-only.
Output owns its minimal pinned pyproject and independently uv-resolved lock, with
FastAPI/Uvicorn/Pydantic runtime dependencies and pytest/httpx only in the test group.
No application requirements, baseline fixture lock, database packages, browser files,
broad Supabase settings or repository server imports are used.

The clean subprocess environment excludes ambient PYTHONPATH, plugins, credentials and
proxy settings. Bounded commands resolve offline, check the lock, then install frozen,
offline and wheel-only into **two absent virtualenvs**, each running isolated generated
version and real-loopback HTTP tests. Socket refusal fails the proof. Tests check
health200, unknown404, invalid422, unexpected500, protocol status/headers, numeric code
compatibility and sentinel-free responses/diagnostics. Probe routes exist only in tests.
Source and lock hashes must remain unchanged after each environment's verification.

`proof.json` records recipe/source/template identities, generated-versus-seed hashes,
uv-owned lock provenance, exact subprocess commands/environment/results and log hashes.
It always declares `bootstrap_only:true` and `generation_ready:false`. Failure retains
partial outcomes and safe stage diagnostics; no deletion or recovery is attempted.
`main.py` is the create-once owner seed; adapters, test/guidance and pyproject are generated.

Impact decisions: scaffold gains narrowly scoped service templates/renderer/harness;
shared UI has no changes because this output has no browser; generated agent guidance
lists actual commands and authority limits while root context stays unchanged;
documentation records bounded bootstrap/qualification; existing ADR0059/0031/0023
cover the change and accepted ADRs remain unchanged.

## Disposable application bootstrap

`test:generation:application` is a separate internal proof with no arguments or output
flag. Its pure renderer accepts validated application recipes without extensions and
returns an explicit generated/owner-seed file map. The API reuses the service HTTP
templates; service output and refusal behavior remain unchanged. Historical web
templates are unchanged. Candidates remain `bootstrap_only:true/generation_ready:false`.

From the repository root with the selected Node26.11.1 on PATH:

```bash
export SCAFFOLD_NPM="$PWD/platform/deployment/.local/kdg-toolchains/ad277eef-a10e-4aac-bb82-5743653fb2e0/payload/npm/bin/npm-cli.js"
export SCAFFOLD_UV="$PWD/platform/deployment/.local/kdg-toolchains/0cc4bc48-505e-41c1-8876-25b2d49b5694/payload/uv/uv"
export SCAFFOLD_PYTHON="$PWD/platform/deployment/.local/kdg-toolchains/0cc4bc48-505e-41c1-8876-25b2d49b5694/payload/python/bin/python3.15"
export SCAFFOLD_NPM_CACHE="$PWD/platform/deployment/.local/web-baseline-qualification/network-cache"
export UV_CACHE_DIR="$PWD/platform/deployment/.local/python-baseline-qualification/cache"
export SCAFFOLD_CHROMIUM="$PWD/platform/deployment/.local/web-baseline-qualification/browsers/chromium_headless_shell-1248/chrome-headless-shell-linux64/chrome-headless-shell"
node "$SCAFFOLD_NPM" run test:generation:application --workspace platform/builder-cli
```

All tools, caches and the existing Chromium must be explicitly selected. No runtime,
browser or package download fallback is allowed. Versions and executable identities are
recorded. Every attempt that reaches output creation receives a new private
`platform/deployment/.local/scaffold-application/proof-*` directory; failures and all
previous output remain. Missing tools/cache and wrong versions refuse before output.

The proof copies canonical root package/lock and existing workspace manifests with
local file-dependency paths preserved, adds the generated web workspace only in that
copy, and extends the copied lock through offline npm package-lock-only resolution.
One clean offline `ci --ignore-scripts --workspace apps/bootstrap-application/web
--include-workspace-root=false` installs the selected generated workspace using the
extended root lock. The checkout lock is never changed; no nested browser lock is used.
The web pins React/DOM19.3.0, Vite8.3.4/plugin-react6.1.2, TS7.0.2, matching React types,
Node types26.6.5 and development-only Playwright1.64.0. No shared UI or Auth packages.

The independent API lock resolves offline, checks, and installs frozen wheel-only into
one absent virtualenv. Generated API tests must pass. Explicit web type-check/build
then real Chromium use built Vite preview and the real owning loopback API. Desktop
and mobile screenshots, actual Chromium path/hash, semantic landmarks, keyboard skip
focus, Home/reload, responsive width, health response and failure-free browser/network
checks are retained. Child execution and browser/API teardown are bounded. Socket
failure fails the proof. Logs contain only synthetic tool/test output in private files.
`proof.json` records exact commands/results, source/output ownership and hashes, base
and extended root-lock provenance, browser identity and safe partial failures.

The shell is presentational banner/main/Welcome/Home only. No fake identity, grants,
Directory, data editor, forms, domain routes, database, providers, deployment, Leave,
normal generation is implemented. Explicit custom imports are qualified through the internal
installer below; the renderer still rejects nonempty extensions. The internal preservation installer
qualifies reruns and recovery only for disposable output. HTTP
health and presentation do not qualify current Access or full P1/SERVICE readiness.

Impact decisions: scaffold gains application templates and a private proof harness;
shared UI has no promotion before consuming proof; generated agent guidance lists
actual commands and limits, with root context unchanged; documentation records commands,
evidence and scope; existing ADR0059/0031/0023 and owner boundaries suffice, with no
accepted ADR changes.

## Internal scaffold preservation

`src/scaffold-install.ts` exports `installScaffold(output, files, identity)`,
`checkScaffold(output)` and explicit `recoverScaffold(output)` for disposable proof.
There is no public generate/recovery CLI or candidate bypass. Renderers still reject
extensions and unsupported recipes. Template upgrades, removal and ownership conversion
are refused. The identity records generator/template versions plus recipe/source hashes.

Initial installation preserves unrelated documentation and refuses planned collisions.
`.generated-files.json` records each generated file and create-once owner seed. Reruns
preflight every generated hash before replacement, preserve edited seeds and custom
files, and refuse missing or edited generated files. The same file set, classifications,
generator/template and recipe identity are required; source hashes may change. Owners
change the source template rather than repair generated output by editing it.

One local lock serializes installation. Complete old/new bytes are staged in an
owner-local journal before replacement; replacement is per file, never multi-file atomic.
A caught installation failure restores the previous complete set. Journal-backed recovery
covers interrupted replacement. Pre-journal or cleanup-window interruption can leave
uncertain state: preserve the tree and refuse automatic recovery. After interruption,
installation and `checkScaffold` refuse with `scaffold_recovery_required`. Explicit
`recoverScaffold` claims exclusive private recovery ownership with its PID, requires
the recorded writer to be dead, validates all journal targets
against recorded old/new bytes and ownership, then restores the previous set. Live
writers and live recovery owners give `scaffold_busy`. An interrupted recovery claim
is uncertain and cannot be stolen, even after its PID exits. Missing/invalid metadata or unknown edits fail closed with
`scaffold_recovery_uncertain`; preserve that tree for investigation rather than deleting
its lock or journal. Recovery preserves owner seeds/custom content; edits to an affected
newly created seed after interruption prevent automatic rollback.

This handles process failure in controlled synthetic trees with stable builder source;
it is not an adversarial filesystem service or power-loss durability guarantee. PID
reuse can conservatively block recovery; locks are never stolen automatically. Empty
directories may remain after rollback. `checkScaffold` is the proof's build admission
check, not a repository-wide build integration.

`tests/scaffold-preservation.test.mjs` covers collisions, reruns, generated updates,
later-file conflicts, unsafe paths/metadata/ownership, injected failure, actual killed
child recovery and live-writer exclusion. The existing application proof now installs,
visibly edits the owner shell, adds a custom file, reruns and checks byte preservation
before its clean installation/type/build/API/browser qualification. Final evidence binds
the installer and preserved output hashes. Run the normal builder tests; no extra proof
command is required.

## Explicit create-once extension imports

The same private installer accepts an optional fifth argument
`{ repositoryRoot, declarations: [{ source, destination }] }`, after its optional
fourth fault-injection test seam. These are the existing version1 recipe declarations;
`repositoryRoot` must be absolute and sources remain repository-relative directories.
The application proof renders its extension-free base map, then passes the actual
recipe declarations to this installer inside the existing writer/journal lifecycle.
There is no new public generation command, candidate bypass or execution of imported code.

Initial import plans every source entry and destination before staging business files.
Destination roots must be absent, including empty directories, and disjoint from all
generated/seed files and other import roots. Source/output overlap, symlinks (including
nested/dangling links), special files, escapes, `.git` and installer metadata are refused.
Names use portable ASCII letters/digits/underscore/dot/hyphen segments, without Windows
reserved names or trailing dots. Relative paths are at most 512 characters. Imports
accept valid UTF-8 text without binary control bytes, at most 1 MiB per file, 8 MiB
combined, 1,000 total source entries (files and directories), 16 tree levels and 100
explicit declarations. Binary assets and dependency discovery remain future needs. Text-file snapshots omit
empty directories. Qualification is for Linux case-sensitive filesystems. Initial
source and output trees must be quiescent except for the installer; hostile concurrent
source mutation is unsupported.

The optional manifest `extensions` object has explicit `schema_version: 1` and an
`imports` array of `{ source, destination, files }`; `files` maps relative imported
paths to their initial SHA-256 values. This inventory records create-once custom
ownership/provenance separately from generated and seed authority. Reruns require
identical declarations and recipe identity; they use installed metadata without
reading, enumerating or requiring the original source or checking custom hashes.
Owner edits, additions and deletions persist. An extension-free legacy manifest stays
valid, but adding imports to installed output or converting ownership is refused.

Import replacements share journal-backed rollback and live writer/recovery exclusion.
Initial import recovery validates known unchanged bytes before removing them; unknown
owner edits refuse recovery safely. Known newly created empty import directories are
removed during rollback so retry can start cleanly. Existing uncertainty and durability
limits above still apply.

`tests/scaffold-extensions.test.mjs` exercises import provenance, no-source replay,
owner maintenance, unsafe inputs, collision/ownership/version refusals, SIGKILL after
imports and manifest, unknown edits, and real ENOSPC during import replacement. The
registered application proof imports a typed module, changes its behavior, removes an
imported file, adds an owner file, moves the original source away, and reruns before
strict type/build/API/browser checks assert the imported owner-rendered text. Commands
and exact tool baseline remain those above; all patterns remain unpromoted.

## Supported recipe preflight

Use Node **26.11.1**, npm **12.2.0**, TypeScript **7.0.2**, Zod **4.6.7** and
@types/node **26.6.5**. Install through the root npm workspace/lock; no nested lock.
Node runs the TypeScript source directly; no downloaded CLI is needed.

```bash
npm run validate:recipe --workspace platform/builder-cli -- --config <recipe.json>
npm run test --workspace platform/builder-cli
npm run type-check --workspace platform/builder-cli
npm run schema:export --workspace platform/builder-cli
npm run schema:check --workspace platform/builder-cli
```

`validate:recipe` accepts exactly `--config <path>`, absolute or relative to the caller.
Recipe references resolve against the repository root. Success prints
`{"recipe_valid":true,"generation_ready":false}`. Failure exits 1 with a safe JSON
`error` identifier: `arguments_invalid`, `config_unreadable`, or `recipe_invalid`.
Diagnostics never echo recipe content, paths or parser errors. Validation reads the
config and inspects reference metadata; it does not read referenced authority content,
write a manifest, grant authority or generate files.

The [Zod source](src/recipe.ts) is the schema authority. The checked-in
[scaffold-v1.json](schema/scaffold-v1.json) exports structural JSON Schema; Zod
refinements and filesystem validation additionally enforce composition, distinct
references, owner-local manifests, safe paths and non-overlapping extensions.
Exported JSON Schema alone is insufficient for full validation. The
[pattern catalogue](schema/patterns-v1.json) lists six explicitly unproven candidates;
contract and preflight test references are not runtime/template proof.

Recipes contain exactly `schema_version`, `owner_id`, `owner_kind`, `sources`,
`contracts`, `patterns`, `extensions` and `deployment_manifest`, as specified in the
[thin recipe contract](../docs/architecture/contracts/scaffold-environment-and-generation.md#thin-recipe-and-deterministic-generation).
An application explicitly selects API, web shell, fixed account auth, safe errors and
`saving.none`; a service selects API, service-owner auth, safe errors and `saving.none`.
Other catalogue proposals remain unsupported. No defaults are inferred. Manifest paths
must sit below `apps/<owner>/deployment/` or `services/<owner>/deployment/`;
owner underscores may also be represented by hyphens. A first manifest may be absent.

A complete service example, runnable from the repository root:

```bash
cat > /tmp/scaffold-recipe.json <<'JSON'
{
  "schema_version": 1,
  "owner_id": "example_service",
  "owner_kind": "service",
  "sources": [
    "platform/docs/architecture/decisions/0059-schema-validated-scaffold-configuration.md"
  ],
  "contracts": [
    "platform/docs/architecture/contracts/scaffold-environment-and-generation.md"
  ],
  "patterns": [
    "api.owner-http.v1",
    "auth.service-owner.v1",
    "errors.safe-envelope.v1",
    "saving.none.v1"
  ],
  "extensions": [],
  "deployment_manifest": "services/example-service/deployment/manifest.json"
}
JSON
npm run validate:recipe --workspace platform/builder-cli -- --config /tmp/scaffold-recipe.json
```

The result is `{"recipe_valid":true,"generation_ready":false}`; the manifest and
its missing parent directories remain absent. Preflight checks extension directory
paths only; it does not scan or copy their contents.

Impact decisions: scaffold preflight/schema/tests added; existing template behavior
unchanged. Shared UI and agent context need no change for this build-time validator.
Documentation is updated here; ADR-0059 applies without a new architecture decision.
Generation, install/build/start qualification of generated owners, runtime Access,
provider/device proof, Identity/Access/WRITE and Leave remain separate work. There is
no `generate` stub or candidate bypass.

The remaining guidance records historical plans and future requirements. Its planned
commands and template claims do not describe delivered generator behavior.

The existing ENV owner provides a [native disposable Supabase route](../deployment/DEVELOPMENT.md) via `python3 platform/deployment/dev.py prepare --supabase <CLI2.120.0 executable> --target <JSON> --run-id <UUID>`. Its service availability checks are separate from application readiness and scaffold generation.

CLI tool for scaffolding features and enforcing platform patterns.

## Purpose

New templates use organization-neutral names under
[ADR-0039](../docs/architecture/decisions/0039-organization-neutral-tenancy.md), retaining
established `org_id` contracts. NGO is not the generic tenant code entity. Under
[ADR-0040](../docs/architecture/decisions/0040-shared-employment-core-and-application-settings.md),
applications needing employees consume shared employment through authorized HTTP
clients; templates must not duplicate a common employee master or generate cross-owner
table access. Prove reference/client and contract-test patterns before promotion;
applications without employment needs do not acquire an HR dependency.
[ADR-0041](../docs/architecture/decisions/0041-shared-supervisor-department-and-location.md)
adds optional scoped department/location and manual supervisor references to the shared
employment contract. Prove null-versus-unavailable handling, reference/history and
client compatibility tests; do not generate a chart engine or Leave routing rules.
- Automate boilerplate: one command creates router + service + page + hook
- Enforce consistency: validate-patterns fails CI if patterns are violated
- Reduce AI reliance: generated artifacts carry the structural knowledge

## Database and API direction

New application templates follow [platform ADR-0014](../docs/architecture/decisions/0014-python-database-access-and-api-models.md): SQLAlchemy/Psycopg database access and separate Pydantic API contracts. Prove the pattern before implementing generation. Opt-in routine CRUD must preserve permissions, tenant scope, revisions and caller-owned transactions; domain commands remain explicit.

Database introspection may assist persistence mapping but must not automatically expose table fields in API schemas. Frontend contracts derive from FastAPI OpenAPI. The historical command sketch below is not an implemented generator or authority to bypass this boundary.

### Thin application scaffold configuration — proposal, 2026-10-12

**Direction accepted under [ADR-0059](../docs/architecture/decisions/0059-schema-validated-scaffold-configuration.md), 2026-10-12.** Exact schema/path/pattern versions and implementation remain readiness inputs.

The user proposes structured app choices to connect requirements gathering, generation
and enforcement. Recommend a small version-controlled `app.scaffold.json`, validated
against a versioned JSON Schema, rather than a duplicate executable feature specification.
This format/path is proposed, not an implemented generator input or new mandatory gate.
Product specs/ADRs/UX remain authoritative; BMAD remains the delivery workflow.

Populate it incrementally from approved requirements/design and update it with each
consuming story. Record schema/app identity; selected proven pattern IDs/versions; explicit
capability scope/owner contract references; surface presentation/saving conventions;
record mutation/history policy where applicable; source requirement/story/test references;
and bounded documented customization decisions. Do not encode every field/widget/business
rule or implement a new runtime form/workflow engine. Unknown requirements stay unresolved
until design, not silently turned into permissive generator defaults.

Saving has three semantic choices from ADR-0051: request draft autosave, explicit whole-
form save, and immediate simple preferences. Inline/drawer/page is presentation, not an
additional saving mode. History choices remain per record/action: mutable attribution,
required domain change events and draft consequential lifecycle evidence cannot be disabled
by a convenience toggle. Capabilities here are static metadata, never actual user grants.
Entity/table/API fields reference their owner-controlled schema/migration/OpenAPI inputs;
do not maintain a second column definition or expose every table as public CRUD.

The generator consumes supported validated choices, emits proven owner templates/client/
UI integration and required contract fixtures, and preserves custom extension modules.
Checks can reject unsupported combinations, missing mandatory declarations and documented
regeneration mismatches. A config claim alone cannot prove actual authorization, revision,
history or shared-component usage: owning ATDD/contract/browser/generated-output tests
must verify behavior. Record legitimate customization with rationale/evidence; an accepted
architecture change uses its linked superseding ADR, not an inferred approval for each
routine extension. Keep supported/custom extension boundaries explicit and inspectable.

Start with ENV/P1's actual shell/configuration inputs and WRITE/REF's first proven surface.
Add history/saving patterns as their first consumers provide implementations and evidence;
do not build a catalogue of hypothetical patterns up front or postpone the first slice
for a whole application-description language. Reference app validates the configuration/
pattern composition; actual Leave/PtS apps keep their own domain tests. Do not rewrite
existing deployment manifests or other generated schemas into this file; share/reference
stable IDs and validate alignment at the relevant delivery boundary.

Illustrative shape only (not a selected complete schema or implemented pattern):

```json
{
  "schema_version": 1,
  "app_id": "reference",
  "surfaces": [
    {
      "id": "example-editor",
      "presentation": "drawer",
      "saving": "explicit_save",
      "change_history": "domain_events",
      "source_refs": ["approved editor story"]
    }
  ]
}
```

[Backstage templates](https://backstage.io/docs/features/software-templates/writing-templates/)
provide a primary example of declarative inputs and JSON Schema validation;
[JSON Schema](https://json-schema.org/learn/getting-started-step-by-step) supplies the
standard schema vocabulary. These support the approach, not adopting Backstage or a
second workflow in this repository. Exact input schema/catalogue/enforcement scope,
ownership/compatibility and first-consumer sizing remain discussion/readiness inputs.
No schema, generator, app code or runtime validation implemented by this proposal.

### Generation inputs and custom behavior

For application APIs and shared HTTP services, the intended progression is an owned
service scaffold, persistence mappings/helpers for the tables required by the consuming
story, explicitly selected API inputs/outputs and routine operations, then custom domain
behavior. Table structure assists generation; it cannot determine caller permissions,
public fields or workflow rules. Use the owner's version-controlled schema/migration
inputs or a disposable database built from them; production introspection is not a
required generation step. The exact generation input format remains a delivery decision.

Keep generated output and hand-maintained behavior in explicit separate extension
modules. Regeneration must preserve custom behavior and fail safely on conflicts;
verify this with a disposable sample that adds a custom command before regeneration.
For example, a draft mapping can be generated, but save/discard commands must implement
the approved revision, lifecycle, authorization and operation-outcome contracts. Do not
expose a generic update route that bypasses those commands.

Non-API workers and scheduled jobs can reuse configuration, owned dependency/test
layout, safe logging and relevant persistence/client scaffolding. Their declared work
and event contracts drive handler generation; tables alone do not define a worker, and
some workers own no tables. Prove restricted worker identity, retry/event compatibility
and bounded shutdown with the first consuming story before promoting templates. E1's
service-only variant proves HTTP services; worker variants remain with later consumers.
These are planned capabilities, not an implemented generator or a new generic engine.

## Database attribution and audit conventions

Table/model generation must follow
[platform ADR-0025](../docs/architecture/decisions/0025-record-attribution-and-audit-provenance.md):

- Mutable business tables: server-managed `created_at`, `created_by`, `updated_at`,
  `updated_by`; UTC instants and stable person/service actor references, not names.
- Immutable tables: creation attribution and append-only behavior; no misleading
  update columns. Other table categories require explicit applicability decisions.
- Preserve creation attribution and integer revisions. Do not expose writable audit
  fields in generated API input models. Cover every generated write path, including
  bulk/import, workers and operational commands, not just ORM object updates.
- Keep immutable consequential audit separate from last-change fields. Operational
  audit includes command name and deployed release, with initiator/executor distinction;
  source file/line details belong to diagnostics.
- Generate and verify model/migration/context behavior together before template
  promotion. Actor spoofing, rollback and immutable-record checks are required.

These are required generator contracts, not implemented CLI capabilities. Do not modify
Supabase-managed tables or invent a second person directory to satisfy the convention.

### Reusable owner-local change history — approved 2026-10-12

Under ADR-0025, scaffold a common immutable change-record envelope and transaction-aware
writer, with explicit owner-defined event types and bounded before/after schemas. Common
fields cover event ID/type/version, organization or declared scope, typed target reference,
verified actor and optional initiator/executor distinction, UTC time, operation and reviewed
revision where applicable. The owner selects required reason/evidence fields and meaningful
changes; do not automatically capture arbitrary table/record payloads or sensitive fields.

The owning business mutation and required history commit in the same owner transaction.
The helper accepts that transaction and never commits independently or calls a central
audit service. Matching operation replay creates no duplicate event; unchanged operations
do not invent a changed-state event. Preserve current-row attribution separately. Domain
history can also be its audit evidence; do not copy it into a second generic audit table.

For People, reuse one employment_change table for period, supervisor and department/
location event variants with structural employment/org references. Other owners retain
their own history and may adopt the same envelope/writer/type conventions. No separate
history table per field or universal dynamic table-name/record-ID access API is required.
Broader owner-local target families follow proven consumers and declared constraints.

Promote templates/helpers, explicit model/migration inputs, event validation, contract
fixtures and authorized history-display conventions together with the first consuming
story. Verify transaction rollback/evidence failure, actor spoofing, current scope,
immutable persistence, bounded payloads and duplicate-safe retries. Display adapters use
approved fields and owner access rules, not raw JSON dumps. Physical columns versus typed
JSON and exact indexing remain owner design; no measured performance advantage is assumed.

This is an approved build-time scaffold direction, not an implemented generator/library,
new runtime audit service or authority to log every draft autosave. Existing draft attribution
and compact outcomes remain sufficient unless their owner requires a consequential event.
Apps/services retain HTTP runtime boundaries; copied/proven generic scaffold artifacts do
not import another owner's server implementation. Record scaffold/UI/agent/doc/ADR impacts
and proof with the first consumer; accepted ADRs are unchanged.

## Transaction and service-call direction

Follow [platform ADR-0022](../docs/architecture/decisions/0022-short-transactions-and-external-service-calls.md):
keep business transactions short and external calls outside coordination/write locks
by default. Current authorization precedes the protected action; current domain
validation, business effects, audit and durable outbound intent commit together.
Deliver required effects through the established outbox after releasing locks.
Document justified exceptions and their bounded failure/retry behavior. Prove this
pattern before adding generator support; this CLI remains a placeholder.

## Operational logging direction

Follow [platform ADR-0023](../docs/architecture/decisions/0023-structured-operational-logs-and-sensitive-data.md):
use selected structured fields for action/outcome/timing/error and safe correlation
context. Exclude sensitive business content, credentials and payload dumps across
normal and exception paths. Keep business audit separate, restrict operational access
and test sensitive-value exclusion. Promote proven API/worker logging defaults during
delivery; no logging generator or telemetry provider is implemented by this guidance.

The [observability and future AI investigation direction](../docs/operations/observability-and-ai-investigation-direction.md)
keeps operational monitoring outside applications, defines basic backend OpenTelemetry
and operational signals for MVP, and defers the product comparison and AI workflow.
No specific telemetry stack or AI repair framework is selected for scaffolding yet.

## Durable event compatibility

Follow [ADR-0028](../docs/architecture/decisions/0028-event-payload-versions-and-queued-work-compatibility.md):
generate/prove minimal event type and payload-version envelope support alongside
stable event/operation identity. Keep payload models application-owned and validate
supported versions explicitly. Test old queued and failed/retryable payloads across
releases; retain and flag unsupported versions. No schema registry or generic payload
editor is required. Compatibility applies to producer/consumer rollout and rollback,
not just database schema changes. These remain generator implementation requirements.

## Outbox table ownership

Scaffold each outbox in its owning application's schema under platform ADR-0003/0016,
not a shared cross-application SD schema. Shared mechanics do not imply shared runtime
tables. Receiver services own their delivery records behind service contracts. Leave's
[concrete application](../../apps/leave/docs/architecture/decisions/0116-owned-outbox-and-obsolete-notification-intent.md)
keeps notification relevance local; do not put domain-specific skip rules in a generic
worker template. Table names remain an owning implementation detail.

## Delivery recovery direction

Follow [platform ADR-0024](../docs/architecture/decisions/0024-durable-delivery-retries-and-audited-recovery.md):
bounded retries, retained failures and authorized audited recovery through normal
worker processing. Keep event identity stable for unchanged retries, retain attempts,
and avoid repeating the business action. No support CLI/UI implementation or execution
transport is selected here; prove reusable mechanics in delivery before scaffolding.

## Notification retention defaults

Apply [ADR-0029](../docs/architecture/decisions/0029-notification-retry-expiry-and-retention.md)
only to notification delivery: original-event retries expire after 90 days, terminal
outbox/attempt details remain 90 days, and receiver deduplication remains at least
90 days after acceptance and while unresolved. Reject expired events even after their
deduplication records are removed. Replacements are newly authorized notification
intents, not repeats of domain actions. General command/event retention remains separately
specified; no runtime cleanup or generator support is implemented by this guidance.

## Worker identity and shutdown direction

Follow [ADR-0026](../docs/architecture/decisions/0026-worker-service-identity-and-ngo-scope.md):
use owner-specific restricted worker identities across permitted NGOs, narrow discovery
and explicit per-item transaction scope. Do not generate per-NGO worker keys or a
universal platform worker credential.

Follow [ADR-0027](../docs/architecture/decisions/0027-bounded-worker-shutdown-and-deployment-reporting.md):
stop new claims, allow bounded completion and verify abrupt-stop recovery. Deployment
supervision records forced stops in the deployment report and structured logs, even
when the worker cannot. Report recovered processing only with evidence. Coordinate
timeouts and retain existing retry/deduplication guarantees. Prove these hooks before
template promotion; no current generator or supervisor behavior is claimed.

## Attachment recovery direction

Follow [ADR-0030](../docs/architecture/decisions/0030-recoverable-content-attachment-association.md):
separate uploaded/finalized content from a persisted domain association. Reuse content
and operation identity on association retry; validate scope/readiness server-side and
block required-document confirmation until attached. Prove attaching/retry UI state
and duplicate-safe recovery before template promotion. Content cleanup must coordinate
with pending associations and protect saved drafts/submitted records; exact cross-service
lifecycle contract is a delivery prerequisite, not an implemented generic helper.

## API error contract direction

Follow [ADR-0031](../docs/architecture/decisions/0031-machine-readable-api-errors-and-localized-presentation.md):
stable machine-readable identifiers and safe typed details drive frontend behavior,
not English message parsing. Align Pydantic/OpenAPI, framework error adapters, generated
TypeScript and localized shared handling, including unknown-identifier fallback.
The current template's numeric `code` is not this new semantic identifier contract;
choose wire fields and compatibility before implementation. Update owning templates
and tests, not generated outputs. No runtime format change is made by this guidance.

## Authentication return flow

Follow [ADR-0032](../docs/architecture/decisions/0032-session-recovery-and-return-navigation.md):
shared shell/API-client renewal, validated return location and same-user/NGO permission
checks restore the prior page and recoverable form context. Keep sensitive values out
of return URLs; application drafts retain their own policy. Refresh consequential
state and never auto-confirm after sign-in or duplicate an uncertain prior operation.
Prove these cases before template promotion; this guidance implements no auth flow.

## Draft lifecycle protection

Follow [ADR-0033](../docs/architecture/decisions/0033-draft-lifecycle-and-late-save-protection.md):
check expected revision and editability atomically, never upsert closed/missing drafts
from late autosaves, and require explicit new-draft creation. Finalization commits with
its local domain effects. Provide lifecycle-conflict hooks that stop autosave and retain
local edits while applications supply states/navigation. Verify old create retries and
concurrent submission/discard, not just stale update revisions. Prove the pattern before
generation; no generic workflow engine or runtime lifecycle change is implemented here.

## Single-active-draft creation

For workflows opting into one active draft per defined domain scope, follow
[ADR-0034](../docs/architecture/decisions/0034-atomic-single-active-draft-creation.md).
Generate/prove database enforcement and atomic create-or-resume handling, rather than
read-then-create logic. Concurrent creators must share one draft without overwriting
its values. Applications supply scope and draft-count rules. Test races, separated
NGOs/owners and old create retries after closure. Do not impose a universal one-draft
rule or introduce shared runtime draft tables. No generator support exists yet.

## Structural database integrity

Follow [ADR-0035](../docs/architecture/decisions/0035-database-structural-integrity-and-application-rules.md):
scaffold required fields, declared checks/references and scoped uniqueness in both
persistence models and reviewed migrations. Tenant-owned local relationships enforce
matching NGO scope; shared/global references need explicit treatment. Do not invent
cross-service foreign keys or derive every business rule from column names. Keep
complex policy decisions in workflows with existing authorization/transaction safeguards.
Verify concurrent/alternate write paths, cross-NGO rejection and safe API error mapping;
RLS and friendly API validation remain necessary. Generation is not implemented here.

## Private content capability lifetimes

Follow [ADR-0036](../docs/architecture/decisions/0036-private-content-signed-operation-lifetimes.md):
shared content configuration defaults to 5-minute private read/download capabilities
and 15-minute upload capabilities. Renew through authorized service contracts and
preserve existing form/content recovery. Verify provider-specific expiry/in-flight
behavior and secret-safe diagnostics; no generated business administration setting.
These are planning defaults, not applied runtime configuration.

## Migration direction

Follow the platform-wide [focused migration verification approach](../docs/development/migration-verification.md).
The opt-in application database helper supplies bounded owner serialization and basic
connection checks; Alembic owns revision resolution and PostgreSQL owns permissions.
Do not add a generic object/ledger whitelist for each application's business tables.
Promote reusable fixtures only when proved by a consumer, together with emitted tests.
KDG's isolated foundation now has native privilege/rollback/lock/retry acceptance;
business-table RLS and release readiness remain separate. Neutral native checks and
their offline denial-oracle tests are emitted under native-database-tools. KDG adopts
them via scripts/sync-kdg-native-database.mjs --write/--check in a separate managed root,
preserving the existing helper inventory. The owner retains explicit synthetic fixture
setup/target policy. Existing applications/services are not automatically rewritten.

[Platform ADR-0015](../docs/architecture/decisions/0015-alembic-migration-authority.md)
selects Alembic for project-owned schemas. Templates must include owned-schema
filtering and migration verification. Align bootstrap/reset, seed and CI commands
when implemented; the existing SQL composition tool remains transitional tooling.
Do not apply both migration systems to the same owned objects. Supabase-managed
schemas are outside autogenerated project schema changes.

Each app/service has its own schema, revision files and migration-version table
under [ADR-0016](../docs/architecture/decisions/0016-owned-migration-histories-and-coordination.md).
The shared deployment entry point coordinates explicit dependencies; generation
must not let one owner manage another owner's schema.

Provision separate restricted runtime and schema-changing deployment identities
under [ADR-0017](../docs/architecture/decisions/0017-runtime-and-migration-database-authority.md).
API/worker environments must not receive migration credentials. Verify permissions
using actual runtime identities, including cross-owner and tenant-denial cases.

Establish verified NGO/actor context per database transaction under
[ADR-0018](../docs/architecture/decisions/0018-transaction-scoped-tenant-context.md).
Include fail-closed tenant RLS and pooled-connection reuse tests; worker identity
and tenant scope are explicit. No connection-wide current-NGO state.

Protected requests check current membership/permissions through the shared access
capability under [ADR-0019](../docs/architecture/decisions/0019-current-server-side-authorization.md),
then application-specific resource rules. Include revoked-access and unavailable
verification tests; login claims or visible controls alone do not authorize actions.

[ADR-0021](../docs/architecture/decisions/0021-revocation-and-in-flight-operations.md)
defines revocation ordering: already-authorized short executions may finish;
queued or delayed new execution requires fresh authorization. Provide bounded
execution and auditable authorization timing. Define timeout values before delivery.

## Mandatory release safety

All generated applications and services follow
[ADR-0020](../docs/architecture/decisions/0020-safe-schema-changes-and-release-recovery.md).
Provide a controlled migration step, prevent competing executions, and block new
API/worker activation when required migrations fail. Report per-owner revision
outcomes. Preserve previous-version compatibility through staged schema changes;
incompatible changes need planned maintenance and explicit recovery. Do not run
migrations at API startup or automatically downgrade after deployment failure.
Include verification hooks and recovery guidance in shared delivery tooling.
These are required implementation targets, not existing CLI capabilities.

## Planned commands
```bash
create-feature <name>     # scaffold full feature (UI + API + types)
generate-models [table]   # persistence mapping assistance; explicit API schemas remain separate
validate-patterns         # lint: check generated files, prompt sizes, naming
```

## Planned structure
```
platform/builder-cli/
  src/
    commands/
      create-feature.ts
      generate-models.ts
      validate-patterns.ts
    templates/           ← Handlebars/EJS templates for scaffolding
    lib/
      supabase-introspect.ts
      codegen.ts
  bin/
    platform-cli.ts
  package.json
```

## Phase
Built in **Phase 3** after FastAPI + codegen (Phases 1–2) are stable.

## Operational alert scaffolding

Follow [ADR-0037](../docs/architecture/decisions/0037-operational-alerts-and-incident-grouping.md)
when promoting proven monitoring templates: configurable per-application thresholds,
separate API/worker/delivery signals, grouped ongoing incidents and verified recovery.
Provide failure/recovery verification hooks. Do not generate business administration
screens for technical alert settings. This is a future scaffold requirement.

## Finalized content identity

Shared content clients and provider contract tests follow
[ADR-0038](../docs/architecture/decisions/0038-finalized-content-byte-identity.md).
Finalized content identity binds verified bytes through association and reading;
outstanding upload capabilities cannot mutate that identity. Replacement uses a new
identity and authorized audited association change. Prove provider behavior and races
before promoting adapter scaffolding; no new UI pattern is required.

For workflows adopting bounded shared-input observations during draft preservation,
follow [ADR-0044](../docs/architecture/decisions/0044-bounded-shared-input-observations-for-draft-saves.md).
Prove total execution deadlines, source-version/observation evidence, fresh checks on
new execution and local revision/lifecycle protection in the first consumer before
promoting templates and disposable-sample tests. Applications classify eligible actions
and set their own time bounds; do not impose Leave's ten-second limit or draft rules
on every app, or extend the pattern to consequential actions. No new runtime capability
is implemented by this guidance.


## Leave first-consumer scope — planning, 2026-10-02

The [bounded E1 scaffold proposal](../../apps/leave/docs/implementation-plan.md#bounded-e1-scaffold-scope--proposal-2026-10-02)
assigns a minimum generator/reference foundation and same-item promotion of proven
shared mechanisms. Existing templates/examples are not a working CLI. Preserve the
generated authenticated slice and disposable-app checks; keep employee/Leave policy
out of generic output. Unused worker/provider features follow their first consumer.
No generator or application implementation is authorized by this planning note.


## Lightweight draft preservation

[ADR-0049](../docs/architecture/decisions/0049-lightweight-draft-preservation-and-compatibility.md)
separates bounded draft input persistence from later business validation. Do not make
missing calculation/submission settings an automatic draft-save blocker in templates.
Keep scope, authorization, structural input bounds, attribution, revisions and lifecycle
checks. Support application-declared obsolete-field clearing with notice and guarded
persistence; no generic destructive migration/reset policy or shared runtime draft engine.
Promote proven handling and disposable acceptance fixtures with the first consumer;
this guidance does not mean a generator or draft subsystem is already implemented.


Sign-in recovery clarification — 2026-10-05: under platform ADR-0032, use supported
authentication return navigation and fresh authorized saved-draft loading. Attempt normal
renewal first. Do not require a bespoke browser recovery record or 30-minute navigation
TTL for draft recovery. Preserve validated destinations and current account/access checks;
fall back safely when return context is missing. Unsaved typing need not survive full-page
sign-in; explain saved-only recovery honestly. Never automatically replay a lost write or
confirm a consequential action. Shared shell/scaffold owns generic return safety; the
application owns draft routes and revision/lifecycle handling, including delayed-save tests.


## First-consumer dependency and test commands

The [current E1 dependency/command contract](../../apps/leave/docs/testing/e1-environment-and-dependencies.md#dependency-ownership-and-pts-integration--proposed-2026-10-08) records the approved shared npm workspace/root-lock direction for frontends, with independent Python/uv owner locks. This supersedes the older standalone-browser install direction; generated disposable verification must still declare its installation root and dependency inputs explicitly. Generated output must install without undeclared root tools, expose explicit build/test commands and preserve custom extensions on regeneration. Prove lock consistency and runtime/dev separation before promoting templates. Do not copy another application's requirements into a service image. Exact compatibility pins and runnable generator/bootstrap commands remain delivery prerequisites; no manifests or templates are implemented by this note.


Draft failure presentation update — accepted 2026-10-05: platform ADR-0050 partially
supersedes ADR-0048; Leave ADR-0123 adopts it. Use inline Changes not saved with Retry
while editing; no Keep editing button. Prompt Stay / Close anyway only on exit when
bounded saving cannot be confirmed; switching uses Stay / Switch anyway. Confirmed saved
input closes immediately. Existing revision/lifecycle/retry and access protections stay
binding; no rollback or unsent-input survival promise. D2-B/D3 and shared scaffold/UI
fixtures must prove these cases. Earlier three-choice wording is superseded. This does
not decide whether a workflow needs a draft or change accepted draft scope.


## Saving conventions — accepted 2026-10-05

Follow [the accepted saving convention](../docs/architecture/decisions/0051-saving-conventions-by-workflow.md): autosave unfinished request input with
Draft saved feedback and separate explicit submission; use whole-form Save / Cancel for
business configuration; apply simple personal preferences immediately on separate surfaces.
Do not directly autosave selected fields inside an explicit-Save form. Existing Review /
Confirm and consequential action rules remain binding. E1 has no submission implementation.
No additional administrative draft system or universal draft requirement is introduced.
Prove behavior and promote reusable UI/scaffold patterns with the first consuming story.
Draft failure UX follows platform ADR-0050: inline Retry, exit-only Stay / Close anyway.


Content client direction — ADR-0054: browser control-plane adapters call the owning app
API; server-side clients authenticate to Content with restricted app identity. The app
checks user/domain authorization, Content enforces stored owner/resource scope and
readiness. Signed bytes transfer directly. Prove wrong-app/scope/operation and domain
denial fixtures with the first consumer before promotion; no callback engine or code
generation implemented by this guidance.


Private download direction — ADR-0055 supersedes earlier signed browser-read guidance:
provide authenticated app-to-Content streaming adapters with bounded memory, per-request
checks, safe headers and no cache bypass. Browser upload bytes remain direct/signed.
Preview/download auth and range/disconnect tests belong to first-consumer delivery.
No generated implementation or optional public-sharing mode exists yet.

## App-owned API client boundary

The application candidate now seeds typed health/error OpenAPI and an offline owner
exporter, plus a thin owner health adapter importing generated contracts. The web
declares @platform/api-client0.1.0 as development tooling; its pinned types-only upstream
CLI/TS6 compatibility compiler stay in that build-tool owner. App/compiler commands remain
TS7.0.2. See [the tool runbook](../api-client/README.md).

The existing application proof copies actual tool/builder sources into its disposable
root-lock workspace, exports before web type/build, observes stale DTO/type failure,
regenerates and checks custom preservation/tamper refusal, then proves real own-API
browser success and safe outage. No public generator or Auth/Access promotion follows.
The historical whole-service characterization hash was intentionally replaced with an
unchanged safe-adapter pin because typed main.py and the offline exporter are new owner
seeds; real health JSON and error behavior remain covered by the service runtime suite.

### Return selection candidate

The adopted Auth lifecycle template includes `createReturnSelection` and generated
behavioral tests for identity-safe, single-consumption return selection. Owners provide
explicit canonical route/safe-page configuration and fresh route-specific authorization;
no default domain routes, durable storage or navigation are generated. KDG consumes
this via the existing managed Auth parity group. See
[KDG consuming evidence](../../apps/kdg-capture/docs/AUTH_RETURN_EVIDENCE.md).

The managed Auth candidate also supplies the injected PKCE launch/callback coordinator
and its emitted acceptance/edge-case tests. Applications adapt their Auth SDK and fresh
route authority; no provider credentials or storage default is generated. See
[KDG consuming evidence](../../apps/kdg-capture/docs/OAUTH_CONTROLLER_EVIDENCE.md).


### Bounded transaction context candidate

Application candidates also emit `write-tools/transaction_context.py` and its synthetic
behavioral tests. This opt-in owner-copy prerequisite uses SQLAlchemy in the consuming
owner's separately approved environment and PostgreSQL17+ when actually executed.
It is not imported by generated API startup and adds no API dependency. Shape-validated
backend org/account/actor/mode is not authorization. The owner checks current access
before entry and retains its original ten-second budget through rechecks; local entry
requires an observation within one second, statement/lock waits cap at five/two seconds.
No fingerprint, receipt, domain SQL or shared runtime imports are supplied.

KDG consumes a separate managed root without changing historical migration inventories.
Use selected Node26.11.1 from repository root:
`node platform/builder-cli/scripts/sync-kdg-write.mjs --write` / `--check`.
Update the templates and generated tests together. Installer replay preserves owner
files and refuses manual managed edits. Synthetic tests prove adapter control flow;
actual database timeout/rollback/privilege/pool behavior needs consuming native proof.

The focused Node test accepts `SCAFFOLD_WRITE_TEST_PYTHON` as an explicit interpreter
path; supply the approved Python/SQLAlchemy environment used by the consuming owner.
When omitted it uses this repository's retained migration environment. It never installs
dependencies or prepares a database. Other historical suites keep their own prerequisites.

The candidate also includes the stable organization/account operation lock primitive.
OutcomeKey binds owner schema, org, account, server-defined command and operation UUID.
Invoke outcome_lock within the verified transaction; its lock settings retain the
original budget and only acquisition55P03 is operation_busy. Fixed ASCII tuple encoding
matches the historical lock-v1 value using standard JSON; no new dependency, command
fingerprint or HMAC is introduced. Lock collisions merely serialize unrelated work;
actual outcome uniqueness and atomicity remain consuming database responsibilities.
The caller must pass the context installed on that same active non-autocommit
transaction; input matching is not an independent connection-scope/authority check.
The deterministic optional compatibility program is
`P -I -B platform/builder-cli/tests/check_operation_lock_compatibility.py`, using the
approved WRITE-test environment's existing rfc8785 oracle. The emitted helper has no
runtime dependency on that serializer.
