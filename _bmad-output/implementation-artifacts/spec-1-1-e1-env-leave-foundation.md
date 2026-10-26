---
title: 'E1-ENV: isolated Leave foundation'
type: 'feature'
created: '2026-10-26'
status: 'in-progress'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: 'f31ab11a6e38a458eee191864b9fcc41f83afea1'
context:
  - 'AGENTS.md'
  - 'apps/leave/docs/implementation-handoff.md'
---

<frozen-after-approval reason="Approved E1-ENV criteria; user requests autonomous implementation and epic-level reviews">

## Intent

Leave lacks an executable isolated foundation. Reuse the proven thin native Supabase
CLI route. Normal development shares the existing KDG stack; destructive acceptance
uses a distinct disposable target and portable synthetic foundation smoke fixture.
User approved this topology on 2026-10-26 after discussing the duplication.
Authoritative scope is E1-ENV in epics.md and the approved
environment contract; this execution record does not replace those sources.

## Boundaries & Constraints

Preserve KDG behavior, historical tooling/resources, unrelated dirty changes and all
accepted ADRs. Use CLI2.120.0, PostgreSQL17, existing local Docker/network/private-state
guards, separate migration/runtime credentials, explicit target/run identity and safe
output. Synthetic fixture data is disposable and has no real grants/employment meaning.
User authorized routine implementation choices and review after epics, superseding
routine spec/dirty-worktree approval stops. No commits, customer operations, production,
provider changes, full Identity/Access bootstrap or application startup migrations.
No new environment engine; extend existing owners. Entra and browser proof remain later
gates. Wider workspace adoption must remain explicitly tracked if not delivered here.

## I/O & Edge-Case Matrix

| Scenario | Expected behavior |
| --- | --- |
| Shared development | Reuse documented KDG target/run without reset or fixture mutation of its existing data |
| Disposable acceptance prepare/up/verify | Separate project, namespace and ports; real local Auth/PostgreSQL reachability |
| Changed/foreign/production target or run marker | Refuse before fixture/lifecycle writes |
| Explicit synthetic fixture setup and smoke | Two synthetic Auth accounts sign in; two organizations include for-profit; restricted SQL roles isolate rows |
| Runtime migration/owner escalation | Actual PostgreSQL denies DDL/owner assumption |
| Setup failure or unknown fixture state | Dependent smoke refuses; no automatic repair/reversal or false readiness |
| Vendor/SQL/Auth failure | Bounded safe error; credentials/payloads never printed |

</frozen-after-approval>

## Code Map

- `platform/deployment/native_cli.py`: thin native route; reuse private run marker,
  local Docker environment, bounded vendor execution/network checks. Current schema
  and .local/kdg path are KDG-specific; preserve legacy route.
- `platform/deployment/dev.py`: reuse validate/read/Parser/configuration/project_identity;
  legacy preparation remains KDG-specific and unchanged.
- `platform/deployment/schema/development-target-v1.json`: closed KDG contract. Introduce
  separate closed Leave schema rather than relaxing arbitrary ports/owners/targets.
- `platform/deployment/tests/test_native_cli.py`: existing temporary-root fake vendor
  acceptance; extend with Leave cases without host Docker in unit suite.
- `platform/deployment/ENV_NATIVE_CLI_EVIDENCE.md`: existing real lifecycle evidence;
  does not prove synthetic Auth or restricted SQL. Current private Access fixtures are
  not portable; use a small explicitly named foundation fixture owner instead.
- `package.json`, `package-lock.json`, `apps/pts/web/package.json`: ENV owns the
  approved PtS root-workspace adoption. Keep existing PtS runtime and TypeScript
  dependency ranges; do not align versions or change app source speculatively.
- `platform/deployment/install-frontends.py`, `tests/test_install.py`: current installer
  runs per manifest; batch workspace selectors into one root locked install while
  preserving generic prefix support. Test mixed modes, workspace batching and no apps.
- `apps/pts/deployment/manifest.json`, `.github/workflows/production.yml`,
  `platform/deployment/tests/test_production_workflow.py`: switch PtS install/browser
  invocation to workspace. Preserve deployment selection, base paths and all gates.

## Tasks & Acceptance

- [x] Add initially failing Leave-target acceptance; extend native route with checked-in
  `environments/leave-local.json`, matching schema and separate private run namespace.
- [x] Add a bounded `platform/deployment/leave_foundation.py` synthetic setup/smoke
  command using validated native target/run, local CLI credential capture and existing
  Docker CLI transport. Setup uses only a dedicated disposable fixture schema/roles;
  no business-owner implementation imports. Keep credentials private or in memory.
- [ ] Add focused tests for target guards, command failure/output handling and owner
  setup-before-smoke boundaries; exercise real password login, restricted SQL rows,
  runtime DDL/escalation denial and setup failure against a fresh native Leave run.
- [ ] Record exact commands/results, five impact decisions and remaining gates in
  `apps/leave/docs/testing/e1-environment-evidence.md`; update Leave sprint status and
  tracker honestly, crediting only demonstrated criteria.
- [ ] Adopt PtS into the shared npm workspace/lock, batch workspace installation,
  update affected CI/tests and owner setup docs. Remove the redundant PtS lock only
  after isolated clean-install/build/browser verification proves the replacement.

Given a fresh explicit Leave target, when preparation and vendor startup complete,
then the isolated Auth/PostgreSQL foundation is reachable with reproducible commands.
Given synthetic owner setup, when smoke runs, then real Auth sign-in and SQL role/
organization isolation are demonstrated. Given unsafe input or failed setup, when
smoke is attempted, then it refuses safely and cannot claim application readiness.

## Implementation Notes

Current next code correction: root actual Auth password smoke returned typed
`email_provider_disabled` (422). Leave's disposable config must enable the email
provider using `[auth.email] enable_signup = true` while keeping global
`[auth] enable_signup = false` and anonymous signup false. KDG configuration must
remain byte-identical. The correction belongs only in dev.configuration's generator,
with initially failing Leave config acceptance and explicit public-signup denial
verification; never edit generated config or any live provider. Agent owns only
dev.py and test_native_cli.py for this correction and must wait for root's stopped/
network-cleaned confirmation before modifying generator output. Root retains native
fresh run, docs, npm proof and all other file ownership.

Approved continuation, 2026-10-26: user accepted shared development plus isolated
destructive acceptance and requested next. Keep the existing Leave target solely for
acceptance; document exact shared KDG target/run commands, preserving its target/marker
and existing data. No duplicate always-running Leave development stack. Root owns
documentation, native execution and completion of dependency/workspace adoption.
First implementation agent finishes the fixture command/tests only: strengthen permission
denial proof so transport/SQL syntax failures cannot count as permission denial; verify
SQLSTATE 42501 through ordinary PostgreSQL exception handling or selected diagnostic
codes, never print arbitrary stderr. Keep wrong-password proof bounded and safe.
Add characterization before corrections exposed by actual integration. Preserve all
unrelated dirty work; no KDG fixture/schema/account writes. Actual fixture setup runs
only against the disposable acceptance target.

Next implementation agent owns ONLY workspace adoption code/tests/docs from the Code
Map: add PtS root workspace, installer batching, PtS manifest workspace mode, workspace
Playwright invocations in CI, and PtS README setup commands. Root owns generated lock,
clean-install/build/browser proof and eventual redundant PtS lock removal, plus global
evidence/tracking. Observe failing installer/workflow acceptance before editing code.
Do not run npm in the checkout or change app source/shared UI. Root supplies selected
Node26.11.1/npm12.2.0 proof; pin CI to that exact pair (setup-node version and a separate
ignore-scripts npm12.2.0 install) instead of silently relying on Node24/bundled npm.
Keep publication/DNS/hosting, owners' Python packaging and app admission unchanged.

Initial investigation: existing native route is delivered; portable synthetic owner
setup and Leave target are missing. Sequential implementation, no new planning review.
Foundation fixture is an acceptance substrate, not Leave's business schema. Full ENV
completion must be assessed against all source criteria, including dependency adoption.

2026-10-26: 65 affected tests pass on stable source; composition, sprint validation and
scoped whitespace checks pass. Actual startup exposed exhausted Docker address pools,
not a port conflict. Candidate explicit subnet is unit-tested but not runtime-qualified.
The user questioned separate development stacks; root recommends shared KDG development
with disposable destructive acceptance. Further separate startup is held during topology
reconciliation. Existing KDG target marker matches by read-only check. No runtime smoke,
KDG writes or ENV completion is claimed; see the Leave environment evidence document.

## Spec Change Log

## Review Triage Log

## Verification

`PYTHONPATH=platform/deployment:platform/deployment/tests python3 -m unittest -v test_native_cli test_leave_foundation test_dev test_docker_gate`
must pass. Actual prepare/up/verify/setup/smoke/stop commands use one fresh UUID and
the existing retained pinned Supabase executable, retaining data on normal stop.
`python3 tools/py/run_compose_supabase.py --check-only` checks composition only.
