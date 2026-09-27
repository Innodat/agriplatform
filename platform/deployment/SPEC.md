---
title: Platform deployment on Netlify and Hetzner with staged CI/CD
type: feature
created: 2026-09-27
status: done
route: dispatch
baseline_commit: 94748c4d70c05f2a2c3856763a1895425d2bcb80
context:
  - AGENTS.md
  - platform/docs/architecture/decisions/0020-safe-schema-changes-and-release-recovery.md
  - platform/docs/architecture/decisions/0023-structured-operational-logs-and-sensitive-data.md
---

<frozen-after-approval>
## Intent

Build PLATFORM-WIDE release infrastructure, with app-owned deployment manifests and silo-specific backend images. First enabled apps: PtS and Scribeswell plus their shared access/content/directory dependencies. User explicitly corrected the initial app-only scope and requires automatic deployments when pushing main. Supabase Pro supports persistent staging, so GitHub main automatically deploys STAGING; production is explicit promotion of an exact successfully staged commit. Never fall back to production because staging configuration is missing. Keep Netlify Free frontends, Hetzner + standalone APISIX backend, and Supabase. Production domain scribeswell.com, API api.scribeswell.com, project gjbsnxmbhxsvcblzgfts (Pro, West EU/Ireland); DNS Dynadot. Terraform manages Hetzner infrastructure per environment; secrets, app releases and owner migrations remain separate.

Prepare and verify all reversible implementation now. No actual provisioning, production/branch creation, migrations/imports, remote push, public deploy or DNS changes before final concrete approval. Missing SSH/admin CIDRs, target accounts, staging project credentials and public Auth key are operator inputs, not permission to invent values. Staging has its own Auth/Storage/database and backend runtime; no production data/secrets copied automatically. Persistent branching incurs additional usage. Future workers/Temporal must fit manifests later; do not deploy nonexistent workers, Temporal, Kubernetes or Leave now.

## Boundaries & Constraints

Generic tooling under platform/deployment; application definitions/Dockerfiles under their silo, shared-service definitions under their service. Do not put all future backends into one app image. Preserve existing browser paths, shared Auth and API/database permission owners. Add configurable Bible API host with local fallback. Serve only approved frontend build artifacts. Per-process runtime secrets external to images/git/build output, Terraform/state/cloud-init and logs; migration authority isolated. APISIX only public backend ingress; access/content private, host/path allowlist, Admin/control unavailable, TLS with documented renewal. APIs keep enforcement; gateway adds no bypass. Keep source rights/notices and existing collected content intact.

CI checks/builds before deployment, records exact code/image identities and evidence; serialize environment releases without cancelling in-flight migrations. Coordinate declared owner migration steps in order before service activation, record before/after/outcomes and block activation on failure. Existing deploy_pts.py may be reused through a scoped owner adapter; never mistake it for platform/Bible migration coverage. Require explicitly completed initial schema/bootstrap evidence. No startup migrations, resets, seeds or automatic database downgrade. Retain previous version/recovery evidence. Production promotion must prove successful staging of the selected SHA, not merely accept a freeform ref. Missing secrets/target information fails closed. Netlify staging uses non-production deploys, so main never publishes scribeswell.com. Disable duplicate provider auto-deploy paths.

## I/O & Edge-Case Matrix

| Scenario | Expected behavior |
| --- | --- |
| App registration | Explicit app/service manifests; enabled first adopters only; invalid dependencies/paths/cycles rejected; Leave absent |
| Static release | Both SPA builds/assets and licensing retained; correct environment API/Auth URLs; private files excluded |
| Missing/secret browser config | Safe failure before publishing; isolated Vite envDir, no service-role or secret key in bundle |
| API local/production | Configurable API origin exercises CORS; local proxy fallback preserved |
| APISIX | Approved TLS host/public routes work; auth/org headers unchanged; internal/Admin/unknown paths denied and disallowed origins not allowed |
| Main push | Checks then immutable builds, ordered migrations, health-gated staging activation and Netlify staging alias; no prod access/fallback |
| Production promotion | Exact SHA has successful staging evidence; explicit protected/manual production path; prod config separate; unstaged SHA rejected |
| Migration/deploy failure | Subsequent owners/activation stopped; partial states recorded, no downgrade; no false success/staged marker |
| Infrastructure | Terraform validates offline/no credentials; scoped SSH; separate environment state/hosts recommended; no automatic app or DB activation |
| Runtime artifact | Separate non-root API images with required references, no secrets; only gateway ports; bounded logs/shutdown and health |
</frozen-after-approval>

## Code Map

- Existing `apps/pts/deployment/RELEASE_PREPARATION.md` contains production inventory. Its only baseline dirty edit is parent-owned recording user project/domain choices; retain it.
- `apps/pts/web` is NOT in root workspaces; install/build via prefix and its lockfile. `apps/scribeswell/web` is a workspace. Root npm build is stale. Both use shared `platform/ui-business` and app-directory-client. Avoid publishing repository root. Place root `netlify.toml` and generic Node build tooling under `platform/deployment`; app manifests own frontend path/base; use an explicit clean output folder. Do not inherit ignored local Vite env values (isolate envDir/build environment appropriately).
- `apps/scribeswell/web/src/lib/api-client.ts` currently uses `BASE_URL + api/bible`; add a clearly named public override preserving fallback. `web/playwright.config.cjs` fixtures use local proxy; add focused production-origin test/config. Auth storage key `pts-auth` stays unchanged.
- `apps/pts/backend/main.py`, `services/access/main.py`, `services/content-service/main.py`: FastAPI; shared pinned dependency file `apps/pts/requirements.txt`; each API must get only needed source/environment. PtS invoked as `apps.pts.backend.main:app`, others separate app-dir `main:app`. `services/content-service/provider.py` owns S3. Directory and Scribeswell have own requirements; runtime `config.py` loads .env files only if copied (do not copy). Use Docker multi-stage targets or separate explicit Dockerfiles plus restrictive Dockerfile-specific ignore file. Scribeswell needs backend, `data/hebrew-lexicon`, and `scripts/hebrew.json`.
- Directory public `/api/apps`, `/api/me/apps`, `/api/me/context`; PtS `/api/poetry`, `/api/sources`, `/api/exports`, `/api/documents/*`; Bible `/api/bible/*`. Suggested gateway prefixes `/pts/`, `/directory/`, `/scribeswell/` stripped before upstream. Read exact service env names in main.py and example files. Keep service-key credentials scoped.
- `tools/py/deploy_pts.py`: access→content→PtS Alembic only; platform identity/Bible schema composition is separate. Existing `organization.json` preserves PtS / Psalms that Sings. Add platform runbook with links to owner procedures, do not invent production UUIDs or execute legacy deploy.sh.
- APISIX official current download page reports 3.18.0; verify available image/tag and pinned configuration against actual container. Use standalone YAML, no public Admin API. TLS certificate provisioning/renewal needs explicit tested procedure; no real certificates issued here. Gateway access logs must exclude query/body/auth/signed URLs. Terraform under platform/deployment uses official hetznercloud/hcloud provider, token from HCLOUD_TOKEN only; Ubuntu server, SSH key, firewall, required location/admin CIDRs, configurable initial 4vCPU/8GiB estimate. No account provisioning, DNS management or secret-generation resources.

- Root remote is GitHub Innodat/agriplatform, no existing .github workflow. Use GitHub Actions with staging/production environment scopes, registry immutable SHA tags/digests and SSH known-host verification. Tokens via environment, never inline generated scripts/logs. Repo is private potentially; document environment approval feature limitations and use explicit manual promotion regardless. Disable Netlify native main auto-publish and Supabase GitHub auto-migrations to avoid competing authorities.
- Partial prior implementation: `apps/pts/deployment/build-release.mjs`, `tests/release.test.mjs`, `tests/test_gateway.py` (intentionally red), root netlify.toml; both Vite config envDir changes; Bible URL override; release Playwright fixture. MOVE generic files to platform/deployment and refactor hardcoded project/site values into environment inputs. Parent's platform spec and apps/pts/deployment/RELEASE_PREPARATION.md retained. No other implementation agent active.

## Tasks & Acceptance

- [x] Freeze input contracts with failing focused manifest/build/routing/release tests before their implementations.
- [x] Add app/shared-service manifests and platform assembly/build tooling; backend images stay silo-owned, explicit artifact contexts; external API override preserves local mode.
- [x] Add APISIX/Compose rendering per environment and runtime env examples; certificate handling, CORS and only gateway exposure.
- [x] Add GitHub main→staging and manual verified-SHA production pipeline plus testable remote release coordinator; ordered migration adapter and failure evidence, concurrency and health gates; no unconfigured production fallback.
- [x] Add Terraform and secret-free bootstrap, firewall and ignore rules, state/SSH setup procedure without apply.
- [x] Add platform ADR referencing immutable 0015/16/17/20/23/27; update decision index; generic scaffold impact decisions and app onboarding docs. Explicitly document first schema/bootstrap/import approvals and persistent staging setup.
- [x] Verify builds, manifest/release failures, actual local APISIX Docker smoke and container startup, Terraform validate, affected browser/session regressions. Record gaps honestly.

Given an enabled app manifest and main push, its silo artifacts participate in a coordinated staging release after verification; no production deployment occurs. Given an exact successfully staged commit, manual production promotion uses production credentials and reruns required gates. New applications can register without importing another app's server implementation or editing generic deployment logic.

## Implementation Notes

2026-09-27: User expanded scope during implementation. Initial app-only files were partial, not committed or deployed. Refactored spec around platform delivery, preserving tests and API configuration work. User has authorized reversible implementation; final provision/deploy approval remains required. Terraform advice accepted as part of preparation. Pro persistent staging verified against https://supabase.com/docs/guides/deployment and branching billing docs. Micro branch starts $0.01344/hour, separate usage and no compute-credit coverage; do not silently provision.

Scaffold: document onboarding/manifest contract for unimplemented builder, no claims of working generator. Shared UI/agent context: no change. ADR: new platform deployment decision, accepted prior records immutable. This is release implementation under BMAD, not a competing generic delivery lifecycle. Implementation agent owns code/tests/runbook/ADR; parent owns spec/status/production inventory, review and live verification. Parent can execute escalation-bound tests. Do not recursively invoke skills or spawn additional implementers. Keep implementation explicit and minimal, run source-only tests yourself and send commands for Docker/HTTP/browser/terraform network checks promptly.

## Review Triage Log

Independent blind, edge and verification reviewers completed before triage. All findings checked against the current callers; all below route to corrections within the authorized platform release intent. No production operation occurred. Preserve working gateway TLS/allowlist/header/privacy checks, isolated images, manifest ownership and explicit promotion while correcting these gates.

| Finding | Verdict | Evidence / correction |
| --- | --- | --- |
| Blind1 actual DB/Storage target not bound | high | Preflight checks SUPABASE_URL only; database URLs and Storage endpoint can point elsewhere. Bind every runtime/migration/storage target to the approved environment project before any effect. |
| Blind2 CI/host public config diverges | high | SSH sends SHA/environment only; frontend origins/project can differ from external host config. Send a nonsecret public-config manifest and compare before migration. |
| Blind3 incomplete migration env permits partial writes | high | Only dotenv syntax checked, adapter reads owner URLs one at a time. Validate all required owner inputs before lock/migration. |
| Blind4 APISIX fetched after migrations | medium | Pinned gateway absent images.json pull loop. Pull/validate gateway before migrations. |
| Blind5 new frontend lacks dependency install | medium | Workflow installs only current two paths. Add validated manifest install policy and generic install runner. |
| Blind6 gateway only supports GET | medium | Generic route/methods and CORS hardcoded. Add validated manifest methods with current owners remaining read-only. |
| Blind7 health_path ignored/new services omitted | medium | Compose relies on image health while fixture hardcodes services and /health. Consume manifest health contract and smoke all registered APIs. |
| Blind8 dev server tests miss built artifact | medium | Release Playwright launches Vite dev server. Add actual assembled-output browser navigation/reload/assets verification. |
| Blind9 forced shutdown warnings absent | medium | Successful Compose can include forced termination. Capture supervisor termination outcomes and durable warning under ADR0027. |
| Blind10 truthy approval flags | high | all() accepts strings such as false/pending. Require literal JSON true plus nonempty approval reference. |
| Edge1 DB/Storage cross-target | high | Same reachable mixed-target state as Blind1; shared fix. |
| Edge2 missing later migration URL | high | Same preflight gap as Blind3; shared fix. |
| Edge3 CI/host public config mismatch | high | Same missing binding as Blind2; shared fix. |
| Edge4 Compose dollar interpolation | medium | Short-form env_file interpolates validated literal credentials. Use raw env-file semantics and require supported Compose version; verify dollar-containing fixtures. |
| Edge5 unbounded migration waits | medium | Adapter subprocess has no timeout; add bounded PostgreSQL lock/statement settings and subprocess timeout with failure/reconciliation evidence. |
| Verification1 preflight untested | medium | Only host path test replaces preflight. Exercise valid/stale/wrong target/approval states and assert rejection before Docker/state effects. |
| Verification2 adapter producer untested | medium | Host fixture fabricates evidence; test actual adapter entry function against controlled revision/migration failure and persisted outcomes. |
| Parent real static build blocked | medium | Scanner rejects Supabase client library's literal startsWith(sb_secret_) source, not an embedded secret. Match actual token-shaped secret values while keeping public-key validation; add regression. |

Observed local evidence before corrections: pinned APISIX traffic smoke passed TLS, host/path allowlist, Auth/org forwarding, CORS, no sensitive logs; fixed a false-positive Admin test (missing curl) and real socket-refusal rerun passed. PtS/Scribeswell/directory image builds passed. Terraform init succeeded after required sandbox escalation; validate requires escalation for provider socket. Netlify CLI23.6.0 exists in npm. The first real static build correctly reached assembly, then failed the overly broad scanner above; no artifact published.


## Completion evidence — 2026-09-27

All review corrections above are implemented. `target_contract.py` and host preflight
bind runtime/migration/Storage authority and CI configuration; manifests drive install,
methods and health checks; bounded owner migrations preserve partial outcomes; host
reports capture shutdown evidence. The artifact scanner recognizes token-shaped
secrets without rejecting Supabase client source. No review finding is deferred.

Final integration found two further issues, corrected before completion:
- Local Compose 2.28.1 cannot support raw env files. Cloud-init now installs upstream
  Compose 2.39.4 with pinned x86_64/aarch64 SHA256 checksums. The local gateway test
  used the verified x86_64 binary through a temporary DOCKER_CONFIG, without changing
  the system installation. YAML parsing and `sh -n` validate bootstrap syntax; an
  actual newly provisioned host still needs cloud-init completion verification.
- The shared-session fixture returned verse-shaped data for `/books/Gen`, creating
  a chapter-navigation error and an ambiguous alert assertion. Added the missing
  book/chapter fixture response; kept the original sign-out assertion. Red: 10/11;
  green: 11/11. Added this suite to staging CI.

| Requirement | Exact command / evidence | Result |
| --- | --- | --- |
| Manifest, preflight, migration adapter, promotion, logs | `python3 -m unittest discover -s platform/deployment/tests -p 'test_*.py'` | 23 passed |
| Static configuration and artifact contracts | `node --test platform/deployment/tests/release.test.mjs` | Passed |
| Schema composition remains valid | `python3 tools/py/run_compose_supabase.py --check-only` | Passed, no writes |
| Isolated static output | `DEPLOY_ENV=production PUBLIC_SITE_ORIGIN=https://scribeswell.com PUBLIC_API_ORIGIN=https://api.scribeswell.com VITE_SUPABASE_URL=https://gjbsnxmbhxsvcblzgfts.supabase.co VITE_SUPABASE_ANON_KEY=sb_publishable_fixture node platform/deployment/build-release.mjs` | Both frontend builds and artifact scan passed; fixture public key only |
| Built SPA paths/assets/external API | `PUBLIC_API_ORIGIN=https://api.scribeswell.com LD_LIBRARY_PATH=/tmp/pts-browser-libs/usr/lib/x86_64-linux-gnu npm exec --workspace=apps/scribeswell/web -- playwright test --config playwright.release.config.cjs` | 1 passed |
| Reader behavior | `LD_LIBRARY_PATH=/tmp/pts-browser-libs/usr/lib/x86_64-linux-gnu npm run test:browser --workspace=apps/scribeswell/web` | 92 passed |
| PtS behavior | `LD_LIBRARY_PATH=/tmp/pts-browser-libs/usr/lib/x86_64-linux-gnu npm run test:browser --prefix apps/pts/web` | 46 passed |
| Shared sessions | `LD_LIBRARY_PATH=/tmp/pts-browser-libs/usr/lib/x86_64-linux-gnu npm exec --workspace=apps/scribeswell/web -- playwright test --config playwright.session.config.cjs` | 11 passed |
| Reader API regression | `apps/scribeswell/.local/venv/bin/python -m pytest apps/scribeswell/tests/test_reader_integrity.py apps/scribeswell/tests/test_import_bible.py apps/scribeswell/tests/test_word_inspector.py apps/scribeswell/tests/test_lexicon.py -q` | 26 passed; existing TestClient dependency deprecation warning |
| Runtime packaging | All five manifest Dockerfiles plus `apps/pts/deployment/Migrations.Dockerfile`, built with `docker build -f <Dockerfile> -t agriplatform-<id>:release-check .` | Six images built |
| API liveness/isolation | `python3 platform/deployment/tests/container_smoke.py` | All five registered APIs healthy/non-root, required references present, private env/archive absent |
| Gateway TLS/routing/access/logging/literal env | `DOCKER_CONFIG=/tmp/platform-docker-config python3 platform/deployment/tests/gateway_smoke.py` | Passed, including Admin/control socket refusal; fixtures removed |
| Infrastructure | `terraform -chdir=platform/deployment/terraform init -backend=false`, `fmt -check`, `validate` | Passed, provider lock retained; no plan/apply |

Temporary browser libraries were missing after a session restart; initial browser
launches failed before tests could run. Restored Ubuntu packages into /tmp and reran
successfully. No test expectation was weakened to accommodate that environment failure.

Remaining operational work is intentionally outside this implementation: create or
select Netlify/Hetzner accounts and a paid persistent Supabase staging branch; review
separate environment Terraform plans, state/SSH/runner egress and TLS; configure
scoped runtime/migration credentials and GitHub environments; approve owner bootstrap,
imports, PtS organization and provider access tests; then run actual staging CI and
approve production promotion. GitHub Actions, provider aliases, fresh cloud-init,
real TLS renewal and live Supabase/Auth/Storage permissions have not been exercised
against a cloud target. No cloud resource, database, DNS, public site or remote git
branch was changed. ADR-0043 remains Proposed pending operational acceptance.
