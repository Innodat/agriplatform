# Minimum scaffold environment and generation contract

2026-10-14. Selected ENV/P1/SERVICE planning baseline, under the sole owner's
acknowledged KDG/Leave handoff. This fixes command/input boundaries; none of the new
commands, JSON schemas, targets or manifests below is installed by this document.
It references existing owner items, not a new delivery workflow. Accepted ADRs stay
unchanged. [KDG shared readiness](kdg-shared-readiness.md) owns Access/WRITE decisions.

## Dependency authority and qualification

Use the [exact newest-stable direct baseline](scaffold-dependency-baseline-2026-10-14.md).
TypeScript compiler is 7.0.2, Node is 26.11.1 Current, Python is ordinary CPython
3.15.0 and uv is 0.13.1. The user explicitly chose newest stable versions; current
PtS locks do not cap the new foundation. Publisher metadata and binary availability
inform selection; affected PtS/shared-package regression and clean installation are
delivery acceptance before activation. No existing manifest/lock is changed now.

Repository frontends share root npm workspaces/package-lock; generated application
webs have no competing nested lock. Independent Python owners use pyproject/uv.lock
and their own virtualenvs. TypeScript7 runs via pinned local `tsc`; no downloaded
implicit latest CLI. Server OpenAPI generates app-owned TypeScript clients, not models
inferred from tables. Choose a CLI interface rather than importing the old TS compiler
API; any proven need for Microsoft's TS6 compatibility adapter is explicitly scoped.

Supabase CLI2.120.0 supplies its supported Auth/database container set; preserve its
publisher-selected image versions, record the CLI version and verify the selected
PostgreSQL major matches the supported deployment target. Normal local service lifecycle belongs to the pinned CLI. Exact
vendor Docker request/config snapshots and historical custom qualifiers are diagnostic
evidence, not prerequisites for this normal local route. Do not replace its database
with generic newest PostgreSQL or upgrade a live project merely to follow library
preferences. Existing root config's PostgreSQL17 is
reuse evidence, not authority over a newly qualified target. Local CLI startup may
retrieve its supported public images; it does not upgrade a live project.

## Explicit isolated environment input

ENV owns `platform/deployment/schema/development-target-v1.json` and
`platform/deployment/environments/kdg-local.json` as planned authority paths. The thin
target document has exactly: schema_version=1, target_id, environment_kind, owner_ids,
workspace_root, project_id_prefix, ports, origins, callback_urls, fixture_ref,
secret_refs, release_registry_ref. Unknown keys are rejected. environment_kind is
`local_disposable` or `ci_disposable`; production is not admitted by this command.
owner_ids initially contains identity/access/kdg_capture, with no People/Content/worker.
The same schema can describe a Leave/reference disposable target with its actual owners.

workspace_root is the absolute repository root resolved by ENV; generated work lives
under ignored `platform/deployment/.local/kdg/<run UUID>/`. project_id_prefix is
`agriplatform-kdg`; run UUID determines project/container/volume/network identities.
The thin native route records only target/config/run binding, allowing ordinary
vendor-managed .temp state and compatible source changes without requalifying every
repository file. It uses a fresh run; historical source-bound qualification runs are
not adopted. Credentials stay in protected ignored secret files. owner_ids never confers authority.

Selected local host ports: web5188, API8188, Supabase API55481, database55482,
shadow55480, Studio55483, mail15484, device TLS8443. Refuse occupied ports; never attach
to an already-running PtS/Scribeswell database. Loopback endpoints stay loopback;
private services have container-network endpoints and owner credentials, not browser
access. Disable unused Studio/mail/Storage/realtime/analytics in the minimum fixture
when supported; no business schemas exposed through browser PostgREST.

Synthetic desktop origins are `http://localhost:5188` and Supabase
`http://localhost:55481`. The provider callback is
`http://localhost:55481/auth/v1/callback`; the app return is
`http://localhost:5188/auth/callback` for a selected redirect-based Auth flow.
User clarification (2026-10-23): KDG does not use Microsoft Entra ID. Its selected
method is emailed six-digit codes for existing Supabase Auth accounts, with automatic
account creation disabled;
these reserved callback addresses do not force KDG to use OAuth or a redirect flow.
Numeric-code sign-in uses an Auth email template containing `{{ .Token }}`, then
`verifyOtp` with type email. Configure and qualify actual delivery before activation;
this synthetic slice sends no real mail and changes no running Auth service.
Entra is a future Leave requirement for two separate clients with their own Microsoft
Entra accounts. Their exact tenant trust, registrations and callback configuration
belong to authorized Leave planning/delivery, not this KDG slice. Local synthetic
password or OAuth tests do not qualify any real provider or client tenant.

Device proof selects LAN-only HTTPS aliases `kdg-capture.test` and `kdg-auth.test` on
8443, with app return `https://kdg-capture.test:8443/auth/callback` and provider
callback `https://kdg-auth.test:8443/auth/v1/callback`. ENV must provide explicit LAN
DNS/address routing, trusted test CA/device trust and exact host/path allowlists on
the existing gateway; no browser certificate-error bypass. Device and Auth backend
must reach the selected Auth service for online setup, then installed PWA capture can
be tested disconnected. No KDG Entra connectivity or registration is required.
The `.test` names select isolated local routing, not public hosting or production DNS.
If the actual provider/device refuses this target, record a replacement nonproduction
target and rerun its qualification; no automatic production or paid-service fallback.

For future Entra consumers, provider URI scheme/path rules and the two distinct
callbacks are source-backed by
[Supabase Azure setup](https://supabase.com/docs/guides/auth/social-login/auth-azure)
and [Entra redirect rules](https://learn.microsoft.com/en-us/entra/identity-platform/reply-url).
KDG LAN DNS/CA and its selected Auth method remain execution assumptions to qualify
by 1.7, not proof that phones or real accounts were configured. Entra registration
is not a KDG gate. Tenant/provider trust is separate from
membership/grants; no automatic tenant enrollment is enabled.

## Guarded environment command contract

The supported thin route uses `python3 platform/deployment/dev.py` with explicit
`--supabase <CLI2.120.0 executable>`, `--target <JSON>` and `--run-id <UUID>`.
The explicit executable selects normal vendor lifecycle; old no-executable invocations
remain compatibility paths for historical qualifiers. No new generic orchestrator.

| Subcommand | Effect |
| --- | --- |
| prepare | Validate disposable target and create fixed config plus small native marker; refuse legacy/unmarked workdirs |
| up | Check ports/local Docker/loopback bridge, invoke normal supabase start in the exact workdir/network |
| verify | Invoke status, check local database TCP and Auth health; no application-readiness or authenticated-SQL claim |
| stop | Invoke normal project-specific stop, preserving development data; no --all or --no-backup |
| reset | Require --confirm-target equal target_id; invoke explicitly local db reset --no-seed; no remote reset or environment disposal |

A project-specific bridge with host_binding_ipv4=127.0.0.1 supplies local-only port
binding. Pass the same explicit network to start/status/stop/reset, including database
recreation. Force the local Docker socket and private run-local CLI state/config;
do not inherit remote Docker contexts, Supabase credentials or experimental routing.
Capture vendor output because status/start may contain credentials; emit safe stage,
exit and target/run summaries. Failures do not authorize automatic recovery/pruning.

The native marker/config are checked before lifecycle commands. Refuse invalid or
foreign targets, production settings, changed config, symlink/path escape, wrong CLI
version and occupied startup ports. No Docker request interception or per-container
vendor Config allowlist. Historical resources/receipts remain preserved and are not
adopted through the new route. Retiring historical code/resources is separate work.

Supabase local DB reset is destructive to this explicit synthetic database. It does
not dispose an environment, run repository Alembic histories or prove owner recovery.
Repository migrations/seeds stay disabled in generated Supabase configuration;
existing owner migration/fixture coordinators run separately after service startup.
No API-startup migration or automatic reversal of applied migrations. Supabase service
availability is distinct from Identity/Access/KDG authorization, provider/device and
release readiness. No production/account/provider provisioning is authorized.

## Thin recipe and deterministic generation

The first bounded implementation is `validate:recipe` in the existing builder.
It checks version1 input structure and safe repository references only. Candidate
pattern validation reports `generation_ready:false`; it is not the normal generator
or a bypass of consuming proof. Full generation behavior below remains a delivery
contract until implemented and verified. Only patterns needed for the initial
application/service input are catalogued; later choices enter with consumers.

The next bounded bootstrap uses `test:generation` to render a service-only health/
safe-error shell into fresh disposable output and qualify its own Python lock and
independent installations. Its pure renderer has no write target; only the harness
writes a fresh ENV proof directory. Applications and custom extensions are refused.
No normal `generate` command, owner-root installation, regeneration or journal
recovery is delivered by this bootstrap. Catalogue candidates remain unpromoted:
service authentication/current Access and complete P1/SERVICE proof are still required.

The application-shell bootstrap adds the focused internal test entry
`test:generation:application`. It renders a presentational web shell and owning HTTP
shell into fresh disposable output, qualifies a copied root workspace with an npm-
extended root lock, and uses an explicit existing Chromium executable. The checkout
root lock and historical web templates stay unchanged; no nested browser lock, real
Auth/Access behavior, public generation or candidate promotion follows from this proof.

The next bounded preservation increment uses the existing application proof and
rendered ownership map. Its internal installer stages a complete plan, records a small
ownership manifest/journal and preserves edited create-once seeds and unrelated files.
Generated conflicts refuse before replacement; failed/interrupted installations must
recover their previous complete generated set before reuse. This does not open normal
owner generation, promote candidates or implement extension import. The public command
and complete extension/release behavior below remain their own delivery gates.

The bounded extension increment imports explicitly declared UTF-8 source modules
through the existing internal installer and application proof. Initial copying validates
source entries and disjoint destinations before mutation; imported files then become
application-owned, with initial provenance retained. Reruns preserve edits/additions/
deletions without requiring original sources. Existing extension-free ownership manifests
remain supported; extension-bearing metadata is explicitly versioned. Binary assets,
later imports/upgrades/dependency inference and normal public generation remain pending.
This is build-time copying, not a runtime plugin system or readiness promotion.

The next P1 increment implements app-owned client generation from offline owner
FastAPI OpenAPI using the existing platform/api-client build-tool owner and upstream
CLI. Its isolated compiler compatibility alias is recorded in the dependency supplement;
app type checks remain TS7.0.2. Generated contracts have their own subdirectory managed
by the existing installer; owner DTO/routes and thin adapters remain create-once code.
The disposable app proof must exercise real browser own-API HTTP, contract drift,
regeneration/custom preservation and safe unavailable behavior. This does not promote
Auth/Access, expose Supabase business reads, or open public scaffold generation.

P1/SERVICE retain the version1 keys/paths in the shared addendum. Exact types:
schema_version=1; owner_id matches `[a-z][a-z0-9_]{1,63}`; owner_kind is application/
service; sources/contracts are unique nonempty arrays of repository-relative existing
authority-document paths; patterns is a unique nonempty array of registered pattern
IDs; extensions is an array of `{source, destination}` records: source is an existing
repository-relative custom module directory, destination is relative to output root;
deployment_manifest is its owner-controlled manifest path (planned manifest may be
absent on first generation, but requires explicit owner/path and later validation).
Bound each array to100 and path/ID strings to512 characters. No arbitrary template
code, embedded DDL/OpenAPI/payloads, runtime grants or secret values.

Pattern catalogue is `platform/builder-cli/schema/patterns-v1.json`, owned by builder,
with exact ID, template version and contract/test references. The full planned candidate set is
`api.owner-http.v1`, `web.react-shell.v1`, `auth.organization-account.fixed.v1`,
`auth.organization-person.selected.v1`, `auth.service-owner.v1`,
`errors.safe-envelope.v1`, `db.owner-migrations.v1`, `db.scoped-write.v1`,
`saving.none.v1`, `history.creation-attribution.v1`. They declare engineering candidates, not proven capabilities.
The preflight currently implements only API, web shell, fixed-account/service-owner
auth, safe errors and saving.none. Selected-person, database and history candidates
remain proposals until their consuming implementation; they are not registered by
the current command.
KDG selects the literal account.fixed pattern; Leave selects person.selected;
service-only output selects service-owner and has no browser navigation. Schema requires
exactly one supported auth/navigation combination. The initial read-only context slice
selects saving.none explicitly and creation-attribution for any reference record seed;
it does not implement a capture form. Later proven saving.explicit-form/request-autosave/
immediate and history.immutable-domain variants require their own exact catalogue IDs
and mutually exclusive selection for the generated consuming surface. No universal app
saving/history default is inferred. Mixed-surface composition is outside the initial read-context generator; extend the
single thin recipe schema only with consuming proof, never silently apply one saving
profile to every surface. Recipes remain pattern selections, not domain specs.
Authoritative contract paths supply rules/evidence, never a prose parser deciding choices.
Unsupported/contradictory pattern groups fail rather than invent a default.

Normal app generation accepts only catalogue entries whose referenced required proof
is recorded. Bootstrap proof is generated in the disposable verification harness using
candidate templates and owner fixtures; `test:generation` owns that narrow internal
exception. No public candidate bypass flag, new readiness engine or live-app waiver.
Proven offline/save/status patterns enter in the first-consuming KDG item after proof.

`npm run generate --workspace platform/builder-cli -- --config <recipe> --output <path>`
accepts exactly those two required arguments, optionally `--check` (preflight/no write)
or `--regenerate` (existing output). Unknown/mixed check-regenerate switches fail.
Normal initial generated destinations must be absent at a verified allowed workspace
location; an owner root may already contain documentation/custom files, which are
preserved. Preflight refuses any collision rather than treating the whole app root as
empty or deleting it. Disposable proof uses an ENV-owned run directory. Output can never overlap a recipe,
shared owner source or another application. No automatic directory deletion.

Generate through a temporary sibling and validate expected output/owner. Serialize
one generation per output root and install through an owner-local journal/recovery
manifest; do not assert multi-file replacement is atomic. Record old/new hashes and
recover an interrupted installation to its prior complete set before another generation
or build. Generation status remains incomplete until every planned file is installed.
Unrelated documents/custom files remain usable and untouched. Generated manifest
`.generated-files.json` records generator/template/recipe/source IDs and generated
file hashes plus explicit generated-vs-owner-seed classification, no secrets. Generated
adapters/clients carry the generated warning and are replaced only by their owning tool.
Model/route/domain entry modules are create-once owner seeds without that warning:
after first creation they are code-owned, never refreshed/overwritten by regeneration.
OpenAPI-derived clients remain generated; model/DTO/route seeds never become outputs
inferred from tables. Existing source code is not forced back to its initial seed hash. Regeneration preflights all previously generated files and
refuses undeclared edits, missing manifest or extension overlap; custom files remain
unchanged. Extension source is copied to destination only on initial explicit import;
destination thereafter is app-owned and always preserved. Regeneration never recopies
source over edits. A disposable package includes declared destinations and dependencies,
not references to the original app directory. Reject escapes/symlinks and any overlap
between extension/generated/seed destinations. Stage/check the complete diff and record
journal recovery before replacement; restore original generated set on failed installation
without deleting custom/seed changes. A file promoted from seed/custom to generated needs
explicit reviewed ownership conversion, not a silent classification change. Source templates have authority, never generated
output edits. Owner models/OpenAPI are code authority after Build.

`npm run test:generation --workspace platform/builder-cli` proves application and
service output, unsupported recipes, candidate proof boundaries, regeneration/custom
preservation, locked clean install/type/build/start and synthetic current Access paths.
Tests may package shared workspace sources into a disposable workspace/root-lock
installation root; no hidden dependency on repository node_modules. SERVICE generates
only the owning HTTP service; no imported server implementation or application package.

## Impact and gates

Scaffold: existing generator/schema/templates/tests/command owners implement this
contract together. Shared UI: neutral shell/errors only; no survey/Leave domain UI.
Agent context: generated instructions list actual owner commands and chosen contracts;
root rules suffice. Documentation: this mutable contract/exact pin record and consuming
owner runbooks. ADR: existing0059/ownership/ATDD/release decisions, none edited.

Planning selection closes direct versions and command/recipe/extension boundaries.
Delivery proves full resolution/native binaries, actual image set/DB target, owner
locks, target guards, provider/device qualification and affected PtS/shared regressions.
Identity/Access/WRITE physical schema/adoption/privilege/operator/secret decisions remain
separate readiness inputs. No implementation or runtime test occurred in this update.
