---
title: 'Build and publish frontends only when their inputs change'
type: 'feature'
created: '2026-09-28'
status: 'done'
route: 'dispatch'
baseline_commit: '09d45399841c812bb04e0238c065f485949a930c'
context: []
---

<frozen-after-approval>

## Intent

The user requests that Netlify build only for platform/app frontend changes. Apply
one conservative frontend-input change policy both to Netlify native build-ignore
and the planned GitHub-controlled production publication. Backend-only changes
must still run backend release gates and deploy services, retaining the existing
verified frontend without building/publishing it. Shared UI, dependencies and
frontend build/routing configuration count as frontend inputs.

## Boundaries & Constraints

Preserve main-only serialized releases, strict private SSH, ordered migration
coordination, API/gateway checks and publication failure handling. No live provider
changes, push, dispatch, data writes or native Netlify re-enablement in this item.
Existing release approval boundaries remain. Do not touch ignored operational
credentials, the separate connectivity-publication worktree, or pending status-doc
edits from the previous GitHub setup task. No schemas or accepted ADR changes.
Do not skip based only on push.before or the last attempted/failed build. Compare
production to the actual currently published frontend revision, its provider deploy
and public configuration. Treat uncertain/missing history/baseline as rebuild,
never as permission to skip. Initial release always builds. A manual force option
covers deliberate rebuilds without source changes. Explicit Netlify build hooks
bypass ignore by provider design; document that exception.

## I/O & Edge-Case Matrix

| State | Expected behavior |
| --- | --- |
| Only backend, migrations, server infra or general docs changed | Netlify native skip; CI retains verified frontend while backend gates run |
| App web/frontend files, shared browser packages, root dependency/lock/config or frontend tooling change | Build and publish combined frontend |
| Deleted/renamed frontend input or new registered frontend | Build, including old rename path |
| Missing/invalid/unavailable/nonancestor baseline; initial build | Build conservatively |
| Netlify cached/current ref equal (cache-clear/retry) | Build conservatively |
| A frontend change was never successfully published then a backend push follows | Build relative to published revision, not latest push |
| Manual force or changed public frontend configuration/key | Build |
| Retaining frontend but provider deploy/identity changes during release | Fail verification; no success evidence |
| Ordinary full publication has stale SHA/attempt/site | Reject as before |

</frozen-after-approval>

## Code Map

- `netlify.toml`: root native build command/publish folder; add dependency-free Node18-compatible ignore command (`./` script path), exit0 skip/1 build.
- `.github/workflows/production.yml`: currently unconditional install/build/browser/Netlify publish. Checkout full history; select before frontend steps. Split gateway smoke from frontend-only browser step; keep gateway/images/migrations/container tests unconditional. Do not filter entire workflow on frontend paths.
- `platform/deployment/record-production.py`: target-bound provider lookup, exact published deploy and release-identity checks, public API/CORS probe, success evidence. Preserve full-publish behavior; add explicit retained-frontend verification recording backend release SHA separately from frontend SHA/deploy/attempt. Never falsely label old assets with new SHA.
- `platform/deployment/build-release.mjs`: writes release-identity.json with SHA/site/API/Supabase/attempt. Add reproducible public-build-input fingerprint (including public Supabase key) so key rotations cannot be skipped; no privileged inputs or raw extra credentials in evidence.
- `platform/deployment/registry.json`, `apps/*/deployment/manifest.json`: discover registered frontend.path and routes. Include registry/manifests in input policy so mapping/removal changes rebuild.
- Browser inputs currently `apps/pts/web`, `apps/scribeswell/web`, `platform/ui-core`, `platform/ui-business`, `platform/api-client`, `platform/app-directory-client`, `platform/shared`. Support other app web/frontend folders and discover platform JS package roots to avoid omitting future shared packages. Root package.json/package-lock, package-manager/toolchain/frontend configs and build/publish/detector scripts are inputs. Pure deployment WireGuard/terraform/backend scripts are not frontend inputs.
- Existing Python production recorder/workflow tests and Node release tests are characterization protection. New temporary-git tests should exercise actual diff/history behavior, not only path regex mocks.

## Tasks & Acceptance

- [x] Add dependency-free shared Node frontend-input detector and meaningful tests; wire native Netlify ignore.
- [x] Add production frontend selection using provider-bound published identity + configuration + git history. Persist non-secret plan for the run and actions output; explicit force input.
- [x] Conditionally install/build/browser-test/publish frontend in production workflow; retain API release verification when skipped. Upload decision evidence even on failures.
- [x] Extend release identity/recorder with retained-frontend verification; test baseline races, wrong provider/identity, changed config and separate SHA evidence.
- [x] Update deployment README and this record with behavior, override, first-build/uncertainty rules, recovery and test traceability.

Given a valid published baseline and only backend changes, when production runs,
then no frontend build or Netlify publish executes and the existing frontend is
verified after backend deployment. Given an unpublished earlier frontend change,
when a later push changes only backend files, then the frontend still builds.
Given any retained-frontend evidence mismatch, release success must not be recorded.

## Implementation Notes

User already authorized autonomous reversible implementation; no additional spec
approval is needed. Sole existing dirty file is the prior session's operational
PRODUCTION_STATUS.md; preserve it. Scope is local code/config only. Implementation
worker must not commit or push. Schema/scaffold/shared-UI/agent-context/ADR impacts:
no schema, UI or context change; shared deployment tooling becomes the reusable
scaffold convention, documentation updated, ADR0020 compatibility/recovery preserved.
Use ATDD: observe failing relevant acceptance before implementation, then focused
unit tests. Keep controls conservative rather than inventing provider success.

## Verification

Run focused Node detector tests and Python selector/recorder/workflow tests first,
then deployment Python suite, Node release suite, release.py check, composition
check and diff whitespace checks. External hosted behavior remains pending the
separately approved publication step; mocks are not live deployment evidence.


### Implementation and acceptance traceability (2026-09-28)

- Shared `frontend-inputs.mjs` drives native ignore and production history checks;
  its temporary-Git tests cover backend-only skips, unpublished frontend changes,
  registered and future app/shared inputs, deletion/rename old paths, mapping
  removal, invalid/equal/nonancestor/shallow history and native exit/force behavior.
- `record-production.py --select` saves `frontend-plan.json` and the Actions build
  output from provider-bound immutable/public identities and the shared public
  fingerprint. `--retained` verifies the selected baseline again around the API
  probe and records frontend/backend revisions separately.
- Production workflow uses full checkout and manual force; frontend operations are
  conditional, gateway/backend release gates remain unconditional, and decision
  evidence uploads on failures. Existing full-publish site/SHA/attempt guarantees
  remain protected by characterization tests.
- `test_frontend_selection.py` covers missing/wrong/config-changed baselines,
  provider/identity races, run-bound plans, secret-free evidence and separate SHAs.
  `test_production_workflow.py` covers the conditional/unconditional gate boundary.
- Public key rotation changes the SHA-256 public-input fingerprint without writing
  the key into evidence. README documents overrides, conservative first/uncertain
  builds, Netlify hook bypass, retained verification and recovery.
- Impact decisions: reusable deployment tooling is the future scaffold convention;
  no schema, shared UI, agent-context or accepted ADR changes. ADR-0020 migration
  compatibility, activation and recovery controls remain unchanged.

ATDD evidence: the new Node acceptance suite initially failed with
`ERR_MODULE_NOT_FOUND`; new Python selection tests initially failed with missing
selection functions; the workflow acceptance initially failed on missing full
history checkout. These failures were observed before the corresponding changes.

Focused verification:

- `python3 -m unittest discover -s platform/deployment/tests -p test_frontend_selection.py`
  — 8 passed.
- `python3 -m unittest discover -s platform/deployment/tests -p 'test_production*.py'`
  — 12 passed.
- `node --test platform/deployment/tests/frontend-inputs.test.mjs platform/deployment/tests/release.test.mjs`
  — 13 passed; Git subprocess tests required execution outside this workspace
  sandbox (sandbox reports EPERM).

Broader suite/check results and independent review are recorded by the parent
workflow at final handoff. No hosted release, live provider change or data write
was performed; external behavior remains pending separately approved publication.

## Review Triage Log

| Finding | Verdict | Evidence and disposition |
| --- | --- | --- |
| Blind 1: root .yarn directory inputs omitted | low | Root filename rules cover yarn configuration but not its directory inputs. Current installer uses npm, so no current production dependency is missed; the direct path-policy correction and test are cheap and consistent. Patch. |
| Blind 2: tools workspace/helpers may be missed | false | tools/package.json does not exist; active installer/build commands consume registered frontend packages and the explicitly watched deployment scripts. No actual unwatched frontend helper/import was identified. Root workspaces mentioning tools alone does not establish a browser input. Future changes introducing new build dependencies must extend this policy. |
| Blind 3: baseline failures have indistinguishable reason | medium | Catch-all rebuild is safe but masks authentication/configuration/selector failures in operator evidence. Reuse existing safe error-code mapping while preserving rebuild behavior. Patch. |
| Blind 4: real Python-to-Git selection boundary mocked | medium | Successful selector cases replace changes(), so reversed SHA arguments would silently rebuild all backend releases. Add temporary-Git integration coverage. Patch. |
| Blind 5: initial published-baseline race not covered | medium | Before/after retained tests do not execute a changing first/final site response during selection. Add transport sequence test. Patch. |
| Blind 6: CLI plan/output/retention handoffs untested | medium | Direct function tests omit plan persistence and exact Actions output consumed by conditions. Add main-entrypoint tests for selection and retained evidence failure/success. Patch. |
| Blind 7: native force is case-sensitive unlike CI | low | Native TRUE differs from Python lowercasing; normalize the same existing input, with override test. Patch. |
| Blind 8: artifact-publication recovery does not branch for retention | medium | Retained release has no newly built public-release directory; existing command sequence assumes one. Add exact retained verification recovery procedure. Patch. |
| Verification 1: Actions output not exercised | medium | Confirmed lowercase output is an untested workflow contract; covered by Blind 6 patch, independently logged. |
| Verification 2: selector/Git integration mocked | medium | Confirmed real Python bridge is bypassed; covered by Blind 4 patch, independently logged. |
| Root: README states native builds already disabled | low | Read-only provider evidence says enabled; distinguish planned policy from current status, and qualify full-publication exact-SHA wording. Direct documentation correction. |

| Root live contract: deploy_ssl_url may be a mutable branch alias | high | Read-only production API inspection returned `https://main--boabab.netlify.app` for the ready production deploy. Treating that field as the immutable permalink would force every selection to rebuild and reject valid publication. Patch: construct the documented atomic permalink from authenticated deploy ID and validated site name, keeping identity/race checks; regress the observed alias response. Official format: https://docs.netlify.com/deploy/deploy-types/deploy-previews/ . |

Edge-case reviewer returned no findings. All three layers ran independently.


### Final verification and review resolution

All accepted review patches are complete. CLI tests now exercise plan JSON,
exact Actions outputs and retained success/failure evidence; real temporary Git
histories exercise Python-to-Node selection. Initial-selection races and the live
Netlify branch-alias response have regression tests. Overrides and root toolchain
inputs are consistent, fallback diagnostics are safe, and recovery explicitly
branches for retained frontends. No accepted review issue remains open.

- `python3 -m unittest discover -s platform/deployment/tests -p 'test_*.py'`: **78 passed**.
- `node --test platform/deployment/tests/*.test.mjs`: **13 passed** (approved outside-sandbox Git subprocess execution).
- `python3 platform/deployment/release.py check`: passed.
- `python3 tools/py/run_compose_supabase.py --check-only`: passed, no database changes.
- `git diff --check`: passed.
- `env DEPLOY_ENV=staging PUBLIC_SITE_ORIGIN=https://site.example.test PUBLIC_API_ORIGIN=https://api.example.test VITE_SUPABASE_URL=https://fixture.supabase.co VITE_SUPABASE_ANON_KEY=sb_publishable_releasefixture RELEASE_SHA=09d45399841c812bb04e0238c065f485949a930c GITHUB_RUN_ID=1 GITHUB_RUN_ATTEMPT=1 node platform/deployment/build-release.mjs`: combined frontend build/audit passed using test-only public inputs; generated identity includes the new fingerprint. Existing bundle-size warnings remain.
- Read-only actual Netlify API metadata plus HEAD of its documented atomic
  permalink verified HTTP200 without redirect. This caught and corrected the
  incorrect assumption that deploy_ssl_url must itself be immutable. No provider
  configuration, publication, deployment, workflow dispatch or data writes occurred.

Hosted activation remains pending the separate production publication approval;
local fixture/build verification does not claim the filter is already live.
