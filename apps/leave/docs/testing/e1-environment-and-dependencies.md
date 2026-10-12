# E1 development, test environment and dependency proposal

**Status:** Local-first topology approved 2026-10-02; dependency ownership and command targets specified; compatibility pins and executable bootstrap remain open
**Date:** 2026-10-01
**Scope:** First draft slice, under existing Phase 1 readiness gates

## Working-tree evidence

Leave has documentation but no implementation package or test command. PtS has pinned
Python direct requirements, a local Supabase setup and disposable PostgreSQL test
instructions. Its Playwright config uses placeholder Auth settings and desktop/mobile
viewports; this is not Leave full-stack or supported-browser evidence. Scribeswell and
PtS web manifests use differing TypeScript/Playwright ranges. The root npm workspaces
include Scribeswell but not Leave/PtS; do not assume root build/test covers them.

Access and Content images use Python 3.12 and install `apps/pts/requirements.txt`.
This is existing dependency coupling, not a template for a new owner. A build-time
requirements dependency is distinct from importing another owner's runtime server,
but service-owned dependency declarations are needed when changing these owners.
Existing versions are compatibility inputs, not verified recommendations to copy.

Sources: [PtS setup](../../../pts/docs/LOCAL_SETUP.md),
[PtS requirements](../../../pts/requirements.txt),
[PtS browser config](../../../pts/web/playwright.config.cjs),
[Scribeswell manifest](../../../scribeswell/web/package.json),
[Access image](../../../../services/access/deployment/Dockerfile).
No service, database, browser or package installation was started during this planning.

## Proposed minimum topology

Use one dedicated local Leave development stack with synthetic identities and data:
Leave web → Leave FastAPI → private Access and People HTTP services, with local
Supabase Auth and PostgreSQL. Identity, Access, People and Leave retain separate schema
ownership, migration histories and restricted runtime roles even when sharing the
local database instance. Browser business calls go through Leave, never directly to
shared tables. E1 needs neither Content uploads nor notifications/workers; add those
at their first consuming epic. Existing shared application navigation remains subject
to its integration contract, not a reason to start unrelated application backends.

Allocate distinct project/container/volume names and free ports. Do not reset or reuse
the prepared PtS/Scribeswell local database. Keep private services on the local private
network; expose only required local developer endpoints. Configuration explicitly lists
the test target, credentials and callback URLs. Fixture/reset helpers must verify the
allowlisted disposable target before writing, with no production fallback.

CI uses fresh isolated instances of this topology, owner-controlled migration/bootstrap
and a synthetic fixture manifest. Restrict cleanup to the test instance/run. Maintain
fixtures for two organizations, including a for-profit organization, and the states in
[E1 acceptance mapping](./e1-acceptance-map.md). Runtime test requests use restricted
roles; bootstrap authority is separate and unavailable to application processes.

Use real Access/People HTTP calls and database persistence for the main browser journey.
Most automated journeys may authenticate synthetic accounts through local Supabase;
this does not change the production Entra sign-in policy. Focused domain tests may
inject authentication, but cannot stand in for current-grant/service-boundary tests.
Fault injection can drop a response after a verified real commit, not replace the
commit with a mocked success. Use an actual supported PostgreSQL version/extensions,
not SQLite, for RLS, constraints, revision and concurrency evidence.

## Real sign-in and human acceptance

Keep a separate integration check of Entra → Supabase → Leave callback, organization
selection and session recovery with dedicated test users and nonproduction credentials.
It may use this local stack with registered callbacks if supported, or a dedicated
nonproduction Supabase target if required. Confirm provider/callback feasibility before
selecting the target; no hosted project or standing staging environment is assumed or
created here. Do not use the three production PtS users as destructive test fixtures.
A local password login cannot satisfy the real Entra integration gate.

Representative human UAT uses synthetic scenarios in an isolated environment. Actual
Safari/iOS/Android and current/previous released-browser qualification remain separate
from Playwright engine/emulation runs, as already agreed. Record actual binaries/OSs;
no device fleet or paid service is selected by this proposal.

## Dependency and command ownership

Keep Playwright Test in TypeScript for browser acceptance, pytest for Python/API/database
contracts and focused UI tests for scheduling/input behavior. Use npm with an explicit
Leave workspace/lockfile ownership decision consistent with the repository. Python
owners declare their own runtime and test dependencies with reproducible resolution;
do not make People or Leave install an app's requirements as their dependency authority.
Separate existing Access dependency ownership with v1 compatibility evidence when
extending it; unrelated Content packaging need not block E1.

Before affected implementation readiness, record and validate an exact compatibility
set: Node/npm, Python, frontend compiler/build/runtime, FastAPI/Pydantic/SQLAlchemy/
Psycopg/Alembic, pytest, Playwright plus browser builds, Supabase CLI/container versions
and PostgreSQL/extensions. Check the new canonicalization dependency against the draft
fingerprint fixtures. Record direct and resolved dependencies and reproducible install
commands; a range in an existing manifest or a currently installed workstation binary
is insufficient. Do not select “latest” implicitly or claim a tested combination now.

Delivery must provide explicit owner commands for bootstrap, API/database tests,
browser tests, type-check/build and generated disposable-app verification. Run failing
acceptance first, then focused implementation tests and affected suites. Avoid root
`npm run dev/build` as verification. Documentation composition can be checked with
`python3 tools/py/run_compose_supabase.py --check-only`, but that is not approval to
apply the whole composed migration set or evidence that SQL ran successfully.

## Impacts and remaining evidence

Scaffold: promote the proven local configuration, restricted runtime clients,
owner-controlled fixtures and reproducible commands through the first-consumer item.
Do not build a general environment manager or complete HR suite. Shared UI: no new
component from environment selection. Agent context: existing silo/ATDD/readiness
instructions suffice. ADR: existing ownership, migrations, authorization and logging
rules apply; no accepted decision changed and proposed ADR-0043 is not assumed accepted.
Documentation: this bounded environment contract, tracker and acceptance map.

Remaining evidence: exact pins, auth callback feasibility, owner
baseline/provisioning integration, clean bootstrap, failure/cleanup isolation, actual
browser availability and measured workload targets. No environment or implementation
readiness gate is marked passed by this proposal.

Reference guidance: [Supabase local development](https://supabase.com/docs/guides/local-development)
describes CLI/container-based local services; [Playwright CI](https://playwright.dev/docs/ci)
describes reproducible package/browser installation and CI execution. These support
the approach, not compatibility claims about this repository's unbuilt Leave stack.


## E1 performance targets — proposal for discussion, 2026-10-02

The user approved the isolated local-first/CI topology and separate real Entra check.
This section proposes the measurable E1 workload/targets required by the spine; it
does not claim measured capacity or decide E3 calculations/E7 calendar/report targets.

User agreement, 2026-10-02: retain the initial timing targets below and investigate
measured misses before changing them. No benchmark or capacity result is implied.
For a signed-in user on a healthy connection, use these 95th-percentile targets:

| Measurement | Proposed target and boundary |
| --- | --- |
| Open an existing draft | At most 3 seconds from explicit open to saved input and editability rendered, including required Access/People/context/draft requests. |
| Save acknowledgement | At most 2 seconds from dispatch of an autosave to its committed acknowledgement processed by the browser. Includes shared checks and durable commit; excludes the separately agreed 1-second idle debounce. |
| Safe Close after pending edits | At most 3 seconds from Close to completion when no previous uncertain operation exists; includes immediate save flush. Never close by losing edits merely to meet the target. |

Thus ordinary idle-triggered autosave aims for Saved about 3 seconds after typing
stops. This does not change the 5-second continuous-typing trigger, coalescing, or
newer-input acknowledgement rules. The 10-second execution deadline and bounded
uncertainty recovery are failure bounds, not acceptable normal response targets.
Measure first browser load and actual Entra sign-in separately; do not quietly omit
them from usability evidence or include human credential-entry time in API latency.

Workload clarification, 2026-10-02: the user expects the largest organization to have
about 1,000 employees and supports retaining 500 employees as the normal test scenario.
Use 500 relationships for that baseline and add a 1,000-employee qualification scenario
against the same proposed latency targets. This is expected scale, not a hard product
limit. Keep another organization for isolation. Twenty simultaneous active draft
editors saving every 5 seconds (about 4 saves/second) remains a provisional load
assumption, not a user-confirmed concurrency forecast; total headcount alone cannot
establish simultaneous activity. Test higher-concurrency headroom separately and record
observed degradation rather than claiming unmeasured capacity.

Seed employee draft scopes and explicit retained-outcome history, initially 100,000
synthetic outcomes across each fixture, rather than measuring only an empty database.
History volume remains a test assumption to validate against retention and usage;
its sufficiency is not established by knowing employee headcount.

Record the machine/CPU/memory, database version, service process counts, connection
pools, fixture counts/distribution, network profile and actual browser. Start with a
defined healthy browser-network profile of 100 ms round-trip latency and 10 Mbps
bandwidth; report where shaping is applied so latency is not double-counted. Use real
shared services, current authorization and restricted roles. Use a 2-minute warm-up
and at least 10 minutes of measured steady traffic, with enough sampled open/close
journeys to report their percentiles meaningfully (at least 100 each). Report failures,
timeouts, sample counts and p50/p95/p99 alongside throughput, not just successful-request
latencies. Any unexpected failure invalidates a clean pass; expected fault scenarios
are reported separately. Preserve test-run data/artifact isolation.

Test slow/interrupted networks, competing tabs and service outages as correctness and
recovery scenarios; they need not meet healthy-network targets, but must preserve the
approved input/uncertainty behavior. Browser measurements cover interaction/rendering;
API load tests cover sustained load and database contention. The simple first slice
does not need a dedicated performance platform, caching authority, or speculative
calculation checkpoints. Choose tooling with the executable test plan.

Traceability: spine performance/browser gate, features §Operational Readiness and
E1-AC-01/04/06/07/08/13/15. Scaffold: reusable timing evidence and synthetic load
fixtures where proven, application-owned workload/thresholds. Shared UI: no new screen.
Agent context/ADRs unchanged. Latency targets agreed; concurrency/history remain qualification assumptions; no benchmark run.


### Rationale for proposed latency numbers

The exact 2-second save and 3-second open/close p95 thresholds are engineering proposals,
not prescribed industry standards or results measured from this stack. They budget for
network travel, current Access/People checks, database commit and rendering. Aim for
faster ordinary interactions; these are qualification ceilings, not intentional delays.
The p95 choice exposes slower experiences that an average hides, while p99 and failures
remain visible. It does not imply the slowest 5% of requests are unimportant.

[Nielsen's response-time guidance](https://www.nngroup.com/articles/response-times-3-important-limits/)
distinguishes roughly immediate feedback, maintaining flow around one second, and
attention loss with longer waits. It supports prompt feedback, not these exact save
thresholds. [Core Web Vitals](https://web.dev/articles/vitals) separately recommends
LCP within 2.5 seconds and INP at most 200 ms, assessed at p75. LCP/INP measure page
loading and interaction response, not durable autosave completion; do not relabel our
end-to-end save metric as either. Typing and immediate Saving/loading feedback must
remain responsive while the server operation proceeds. Subsequent user agreement accepts the initial latency targets. Concurrency/history
remain qualification assumptions, not verified forecasts.


## Dependency ownership and command contract — 2026-10-05

This resolves the ownership/command-layout part of ENV/P1/SERVICE planning. All paths
and new script names below are delivery targets, not files or commands implemented by
this document. Existing application installations and root workspace membership remain
unchanged during planning. Exact version selection and compatibility validation remain
required before the dependent story is ready; runtime passing evidence belongs to delivery.

### One dependency authority per deployable owner

| Owner | Planned dependency authority | Boundary |
| --- | --- | --- |
| Leave browser | `apps/leave/web/package.json` and its own `package-lock.json` | Standalone npm package, like PtS; do not also add it to the root npm workspace with a competing lock. Include TypeScript Playwright tests here. |
| Leave API | `apps/leave/backend/pyproject.toml` and `uv.lock` | Runtime dependencies and a `dev` dependency group containing pytest and development checks; own virtual environment. |
| People HTTP service | `services/people/pyproject.toml` and `uv.lock` | Independent install and image; never install Leave/PtS requirements. |
| Access service, when extended for E1 | `services/access/pyproject.toml` and `uv.lock` | Replace its PtS requirements dependency in the same delivery item, retaining v1 compatibility tests. Its owned Identity migration tooling may share this package; database ownership/credentials stay separate. |
| Directory, when extended for E1 | `services/app-directory/pyproject.toml` and `uv.lock` | Adopt its existing direct requirements into its own resolved lock in the owning integration story; no dependency on another service's implementation. |
| Builder and shared frontend packages | Their existing declared workspace/package boundary | Prove generated output installs independently; a consumer may not depend on undeclared root tools or another application's node_modules. |

Use uv projects for the new/affected Python owners; the repository already has a bounded
example in Scribeswell's poetry engine. Do not migrate unrelated PtS, Scribeswell or Content
packaging merely to standardize E1. A retained requirements export must be generated from
the owning lock for a proven downstream need, never maintained as a second dependency list.

Shared frontend packages remain build-time dependencies. For repository-local packages,
record package paths plus the exact repository commit (and patch identity for working-tree
evidence); the lock alone does not freeze mutable local source. The generated disposable
fixture must include or package the declared shared dependencies and install without a
root node_modules directory. Prove peer-dependency/React compatibility and regeneration
preserving custom code. Package publication is not required for this first slice.

### Required command surface

Run commands from the stated owner directory. New scripts and suite directories below
must be provided and documented by the owning delivery item, with useful nonzero failures.
They must not report success when required tests or services are missing.

| Location | Planned command | Required purpose |
| --- | --- | --- |
| Leave web | `npm ci` | Install the checked-in resolution without updating the lock. |
| Leave web | `npm run type-check`, `npm run build` | Explicit type verification and production browser build. |
| Leave web | `npm run test:unit` | Focused input/autosave scheduling checks; runner selected with compatibility baseline. |
| Leave web | `npm run test:browser:install` | Invoke the installed Playwright CLI for Chromium/Firefox/WebKit and required OS dependencies in the documented target; never fetch an unpinned CLI implicitly. |
| Leave web | `npm run test:browser` | TypeScript acceptance against the isolated real API/Access/People/PostgreSQL stack. |
| Leave web | `npm run test:auth-integration` | Separate real nonproduction Entra/Supabase callback and session-return check; missing configuration is explicitly unqualified, not a passing substitute. |
| Each Python owner | `uv sync --locked` | Install runtime plus its declared dev group without silently changing the lock. |
| Each Python owner | `uv run --locked pytest tests/unit` | Focused owner tests after the relevant acceptance failure. |
| Each Python owner | `uv run --locked pytest tests/contracts` | Owned HTTP/database contracts, actual restricted-role tests and applicable concurrency cases. |
| Each Python runtime image | `uv sync --locked --no-default-groups` | Runtime-only install from that owner's manifest/lock; build process separately pins uv/Python and proves import/startup. |

Suite layout applies where the owner has that test category; do not generate empty passing
suites. ENV must supply exact bootstrap/stop/reset commands and fixture paths together with
its disposable-target guard. These remain outstanding until the orchestrator layout is
verified; this table is not an invented existing environment manager. P1/SERVICE likewise
must supply a runnable disposable generation/regeneration command before promotion.
Migration commands use the controlled coordinator and separate identities, never API startup.

A browser install/engine run does not qualify actual Safari/iOS/Android or previous major
released browsers. Keep those agreed qualification checks separate. Human acceptance is
also retained; automation supplies repeatable evidence rather than approving user experience.

### Compatibility record and evidence

ENV owns a concise checked-in compatibility record linked here when prepared. Record
exact Node/npm/Python/uv versions, package lock identities, Supabase CLI/container identities,
PostgreSQL and required extensions, browser package/binary versions, OS/architecture and
local/CI configuration. Pin deployment images by immutable identity for the verified build;
record how deliberate updates refresh and revalidate this set. Record only safe configuration
names/references, never credential values or stored authenticated browser state in git.

Do not infer compatibility from the differing existing TypeScript/Playwright ranges, a
workstation version, or a successful resolver alone. Minimum delivery evidence is a clean
install with unchanged locks, generated app/service startup, type/build checks, real
restricted-service browser journey and relevant migration/contract tests. Include explicit
failure for a stale lock and a test that generated custom extensions survive regeneration.
No installation, dependency resolution, lock creation, container startup or tests were run
as part of this planning update. Exact compatibility pins and bootstrap/fixture commands
are still open; this section does not close those readiness gates.

Scaffold impact: P1/SERVICE emit the owned manifests, lock-generation instructions and
command surface, and prove them with the disposable reference. Shared UI: no new component.
Agent context: existing silo/ATDD instructions suffice. Documentation: this contract, builder
README, E1 acceptance map and tracker. ADR: existing ownership/release decisions apply;
no accepted ADR changes or new runtime service are required for package management.

Tool semantics checked against [npm ci](https://docs.npmjs.com/cli/commands/npm-ci/),
[uv locking/syncing](https://docs.astral.sh/uv/concepts/projects/sync/) and
[Playwright CI](https://playwright.dev/docs/ci). These sources support the command semantics,
not a claim that this repository's proposed version combination has been verified.
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 

## Dependency ownership and PtS integration — proposed 2026-10-08

**Frontend workspace integration approved, 2026-10-08.** Exact compatibility pins and
implementation evidence remain pending; hosting stays independently owned per app.

Working-tree inspection found two npm install roots: the repository workspace includes
platform packages, Scribeswell web and tools; PtS web has its own package-lock and is
absent from root workspaces. Its deployment manifest explicitly selects `install: prefix`;
install-frontends.py supports that path and production.yml invokes its local Playwright
binary and prefix test command. This explains the current mechanism, not a demonstrated
architectural requirement or a verified account of why the original author chose it.

User challenged leaving PtS separate. Recommend integrating PtS into the root npm
workspace alongside the new reference/Leave frontends, using one authoritative root
package-lock for that workspace. Apps retain their own manifests, scripts, build outputs
and independent runtime/deployment boundaries. A common install graph does not authorize
cross-app source imports or require simultaneous application deployment.

Do the change as one coherent tooling adoption item within ENV's affected-consumer work:
add the workspace, reconcile/resolve the root lock, update PtS's manifest install mode,
CI browser invocation and setup documentation, then remove the redundant PtS lock only
once clean-install and affected build/browser checks prove the replacement. Shared
package source references are versioned by the same repository revision. Avoid running
a full root npm install repeatedly for each selected workspace in release tooling.
Do not silently remove generic prefix support needed by other actual consumers; inventory
all manifest install modes first. Retain the old source/lock/release revision for recovery.

Observed lockfile differences include TypeScript 7.0.2 at the root versus 5.9.3 for PtS,
and different resolved React versions. These are file contents, not registry availability,
security or compatibility verification. One workspace lock does not require every app to
use an identical dependency version. First preserve intended behavior; deliberately align
shared React/peer/compiler/test tooling where the supported matrix requires it and prove
that with clean installs and actual builds/tests. Do not call current lock contents a
validated new baseline or introduce unrelated blanket upgrades.

For Python, keep runtime dependency declarations and resolved locks owned by each
backend/service. Recommend pyproject.toml plus uv.lock per owning project for new E1
components and touched shared services; separate runtime and test groups. Access and
Content currently install apps/pts/requirements.txt in their Dockerfiles: remove that
packaging dependency in their owning delivery, replacing it with each service's verified
own dependency set. Do not replace it with one universal runtime requirements file.
Where pip-based packaging remains, a requirements export must be generated from the
owning lock, not maintained as a competing source. Python dependencies cannot import
another owner's server implementation merely because builds share tooling.

Reproducibility direction: explicit pinned Node/npm and Python/uv versions, committed
resolved dependencies, and locked installs that reject stale manifests. Existing Node 24
CI and Python 3.12 container lines are compatibility candidates, not selected exact pins.
Check actual supported releases/registries and choose the exact set before readiness;
exercise fresh-install/type-check/build/API/browser paths during authorized delivery.
[npm ci documentation](https://docs.npmjs.com/cli/v11/commands/npm-ci/) and
[uv locked synchronization](https://docs.astral.sh/uv/concepts/projects/sync/) describe the
install mechanisms; they are not repository test evidence. Pin browser builds and
container/provider versions separately where required by the existing environment gate.

Scaffold: P1/SERVICE emit the selected owner manifests and reproducible install guidance;
ENV owns the common tooling/fixture foundation, with ACCESS/CONTENT package adoption in
their own stories. Shared UI package compatibility is checked against affected consumers;
no UI feature added. Agent context remains valid, including the stale root dev/build
warning. Update owner docs, deployment tooling tests and requirement/evidence links during
delivery; no accepted ADR change. Exact compatibility pins and commands remain open.
This inspection changed documentation only: no dependency installation, lockfile update,
manifest/code edit, registry validation, migration, build/test run or readiness pass.


Hosting clarification — 2026-10-08: user explains the intended public Scribeswell domain
and separate frontend hosting motivated the original split. Keep build dependency
ownership distinct from deployment/domain ownership: one npm workspace/lock can still
produce independently published Scribeswell, PtS and Leave frontends. Consolidation must
not collapse their public/auth boundaries or require shared frontend releases.

Current working-tree manifests/build tooling assemble PtS at `/` and Scribeswell at
`/scribeswell/` in a combined static artifact. These files are not evidence of live DNS
or current production routing. The accepted app-domain target therefore requires explicit
per-app publication/base-path/API-origin design; changing DNS alone does not implement it.
The user reopened whether a Boabab Scribeswell alias would be useful. Recommend keeping
scribeswell.com canonical and public, with PtS's launcher linking there; if an alias is
adopted, point its hosting configuration at the same Scribeswell deployment and redirect
one way to the canonical domain. Exact Boabab .app/.com choice and optional alias remain
for discussion; earlier no-alias scope is not silently replaced. Hosting must configure
both requested domains/TLS and any redirect; DNS aliasing is not an HTTP redirect or SSO.
No domain records, sites or deployment manifests were changed.


## Frontend publication target — approved 2026-10-08

User confirms public Scribeswell at `scribeswell.com`, without a Boabab Scribeswell alias
or redirect. This resolves the alias discussion above. Retain the accepted PtS-account
launcher rule under ADR-0047 as refined by ADR-0052/0053: the eligible menu entry links
to `https://scribeswell.com`; direct public reading requires no sign-in and does not
inherit a PtS admission requirement. No new registration or SSO behavior is implied.

Use a separately published Scribeswell frontend with its own target/site configuration,
while consolidating PtS and new Reference/Leave frontend dependencies into the shared
npm workspace/root lock. App-specific build outputs, domains, API configuration and
release targeting remain explicit. Dependency consolidation is not a combined hosting
requirement. Do not duplicate Scribeswell source or deploy two copies for PtS users.

Delivery reconciliation: ENV owns the npm workspace/install/test-tooling transition;
PTS-ADOPT and the deployment owner coordinate removal of the combined PtS/Scribeswell
static publication assumption. Preserve Scribeswell's public availability and correct
app-directory target, base paths, deep links, assets, API routes and HTTPS behavior in
that transition. P1 generates per-app deployment inputs; VERIFY later consumes that
proven publication pattern. Include actual affected Scribeswell tests in the shared
change. Explicitly size this deployment work before declaring PTS-ADOPT ready; no
silent additional story or dependency on the later reference app is introduced.

Validate independent artifact selection and per-app configuration, anonymous direct
Scribeswell entry, PtS-authorized launcher navigation, denied/unavailable menu cases,
and recovery to the previous publication. Exact hosting targets and existing live URL
inventory must be established during authorized delivery before cutover; do not invent
redirects for unknown legacy URLs. This records the agreed target, not DNS/site changes
or permission to skip planning/readiness. No accepted ADR changed.
