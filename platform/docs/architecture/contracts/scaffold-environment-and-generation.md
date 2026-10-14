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
publisher-selected image versions, freeze resolved image identities/digests during
ENV delivery and verify the selected PostgreSQL major matches the supported deployment
target. Do not replace its database with generic newest PostgreSQL or upgrade a live
project merely to follow library preferences. Existing root config's PostgreSQL17 is
reuse evidence, not authority over a newly qualified target. No image pull happens now.

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
Prepared target metadata records exact identities, config/source hashes and run UUID;
credentials stay in protected ignored secret files. owner_ids never confers authority.

Selected local host ports: web5188, API8188, Supabase API55481, database55482,
shadow55480, Studio55483, mail55484, device TLS8443. Refuse occupied ports; never attach
to an already-running PtS/Scribeswell database. Loopback endpoints stay loopback;
private services have container-network endpoints and owner credentials, not browser
access. Disable unused Studio/mail/Storage/realtime/analytics in the minimum fixture
when supported; no business schemas exposed through browser PostgREST.

Synthetic desktop origins are `http://localhost:5188` and Supabase
`http://localhost:55481`. The provider callback is
`http://localhost:55481/auth/v1/callback`; the app return is
`http://localhost:5188/auth/callback`. Those exact endpoints require separate
nonproduction Entra registration/configuration during authorized ENV delivery.
Local synthetic-password acceptance does not qualify Entra login.

Device proof selects LAN-only HTTPS aliases `kdg-capture.test` and `kdg-auth.test` on
8443, with app return `https://kdg-capture.test:8443/auth/callback` and provider
callback `https://kdg-auth.test:8443/auth/v1/callback`. ENV must provide explicit LAN
DNS/address routing, trusted test CA/device trust and exact host/path allowlists on
the existing gateway; no browser certificate-error bypass. Device and Auth backend
must reach Entra for online setup, then installed PWA capture can be tested disconnected.
The `.test` names select isolated local routing, not public hosting or production DNS.
If the actual provider/device refuses this target, record a replacement nonproduction
target and rerun its qualification; no automatic production or paid-service fallback.

Provider URI scheme/path rules and the two distinct callbacks are source-backed by
[Supabase Azure setup](https://supabase.com/docs/guides/auth/social-login/auth-azure)
and [Entra redirect rules](https://learn.microsoft.com/en-us/entra/identity-platform/reply-url).
LAN DNS/CA/provider registration is an execution assumption to qualify by 1.7, not
proof that phones or Entra were configured. Tenant/provider trust is separate from
membership/grants; no automatic tenant enrollment is enabled.

## Guarded environment command contract

Planned entry point is `python3 platform/deployment/dev.py`, from repository root:

| Subcommand | Required arguments | Effect after implementation approval |
| --- | --- | --- |
| prepare | `--target <target JSON> --run-id <UUID>` | Validate schema/path/allowlist/config and materialize run-local config/identity inventory; no migrations or owner commands |
| up | `--target <target JSON> --run-id <UUID>` | Verify prepared hashes/identities/ports, start only that isolated stack, run existing controlled owner migration coordinator then targeted owner fixture commands; report each stage |
| verify | `--target <target JSON> --run-id <UUID>` | Current service/owner fixture/readiness checks, no implicit grant repair; missing stage is failed/unqualified |
| stop | `--target <target JSON> --run-id <UUID>` | Stop only proven run-owned processes/containers, retain persistent volumes and evidence |
| reset | `--target <target JSON> --run-id <UUID> --confirm-target <target ID>` | Dispose/recreate only verified disposable run-owned data through its owner coordinator; preserve safe run evidence |

Every command refuses missing target/run, changed prepared target, symlink/path escape,
unexpected project/volume, production URL/credential, foreign owner or unmatched run
identity before mutation. No default target, root Supabase reset or guessed localhost
fallback. Secrets are referenced, never copied into reports. Command failures are
nonzero with safe stage/operation references; setup receipt is not consumer readiness.
API startup does not migrate. Supabase project startup does not apply repository-owned
SQL migrations/seeds; owned Alembic histories run through their explicit coordinator.
No automatically reversed applied migrations after later failure.

## Thin recipe and deterministic generation

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
with exact ID, template version and contract/test references. Initial candidate IDs are
`api.owner-http.v1`, `web.react-shell.v1`, `auth.organization-account.fixed.v1`,
`auth.organization-person.selected.v1`, `auth.service-owner.v1`,
`errors.safe-envelope.v1`, `db.owner-migrations.v1`, `db.scoped-write.v1`,
`saving.none.v1`, `history.creation-attribution.v1`. They declare engineering candidates, not proven capabilities.
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
