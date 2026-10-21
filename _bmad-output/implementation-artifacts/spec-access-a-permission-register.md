---
title: Protected Access permission registration
type: feature
created: '2026-10-21'
status: done
route: dispatch
review_loop_iteration: 0
baseline_commit: 45ab5dfaeecc836c560e3b4985defea83b1a2957
context:
  - /home/ck/repos/innodat/agriplatform/AGENTS.md
  - /home/ck/repos/innodat/agriplatform/platform/docs/architecture/contracts/identity-access-execution-substrate.md
  - /home/ck/repos/innodat/agriplatform/platform/docs/architecture/contracts/owned-write-and-secret-execution.md
---

<frozen-after-approval reason="standing bounded synthetic implementation approval">

## Intent

Deliver protected `permission.register`: immutable literal permission/app/scope mapping and authorized recovery, granting no effective access.

## Boundaries & Constraints

Add Access0005 through existing owners; no new framework, roles, credentials or lifecycle. Preserve historical files/data/receipts, concurrent work, application behavior, Identity18, legacy grants and registry immutability. Verify exact clean/1/2/3/4/5; unknown/drift refuses without repair. Identity checks Access metadata only.

Require platform scope, existing app (disabled allowed), literal ASCII permission1–200 bytes including controls/DEL except NUL, account/organization scope and expected_absent=true. Identical mapping unchanged; app/scope reassignment conflicts. Derive attribution from original-session principal and exact permission.register/platform/app authority; application authority confers none. Check current authority before execute/replay/lookup and after waits. Serialize permission globally, authority edits and outcome key. Only retry-lock timeout is busy. Reuse bounded idle READ COMMITTED/commit-uncertainty/safe-error rules.

Atomically commit permission/outcome/access.permission_registered event, with database-enforced linkage and closed command-specific validation. Event stores executor/time, target/scope, reason/evidence. Typed receipt target {app_id,permission}, created/unchanged, revision=null, event UUID only for creation. Lookup requires explicit app+permission/current authority; wrong target denies, missing unresolved. Full-envelope SHA256/JCS includes scope/expected state and preserves literal ASCII/escaping.

Final WRITE refines E1: unique(scope_kind,scope_id,executor_actor_id,command_type,operation_id), NULLS NOT DISTINCT. Widen Access4 compatibly, preserving rows; application execute/lookup must select exact command/scope. Cross-command operation reuse never returns another receipt. Lock uses actual command.

Grant existing command owner only SELECT/INSERT permissions and exact operator routines. No raw operator/runtime registry access, foreign grants or DDL. Entry execution remains unsupported before target access. No dependencies, production/real accounts/access, deploy/provision/pilot/push/reset/prune, Leave/editor, enablement/grants/ACCESS-B/consumer activation.

## I/O & Edge-Case Matrix

| Scenario | Expected |
| --- | --- |
| Permitted new/both scopes/literal ASCII boundaries | Exact immutable mapping, attribution/event/outcome and typed CLI receipt |
| Identical existing/retry; app/scope/input conflict | Unchanged/no new event; original receipt; conflict with no effects |
| Missing app; wrong command/app/login; disabled/revoked principal/authority | Safe refusal; execute/replay/lookup disclose nothing and preserve state |
| Concurrent identical/changed retry and cross-app/scope permission collision | One effect, correct conflict/unchanged; bounded retry/authority/domain lock waits |
| Cross-command same operation; lost response; wrong-target/unresolved lookup | Command isolation; authorized original recovery; denial/unresolved without leakage |
| Direct malformed SQL/JCS; GUC/SET ROLE/raw DML; forged/missing evidence | Sanitized refusal, no partial writes or executor spoof |
| Populated4 upgrade/repeat and clean/earlier histories; drift/default/privilege attacks | Preserve exact prior data; known catalog passes, unexpected state refuses |

</frozen-after-approval>

## Code Map

Under `services/access/`:
- `access_operator_input.py`: RegisterPermissionCommand.
- `access_operator.py`, `operator_cli.py`: extend typed union/dispatch/lookup; reuse trusted runner/target/process bounds.
- `migrations/versions/`: preserve0001–4, add0005.
- `migrations/access_baseline.py`, `access_registration_baseline.py`, `access_registration_catalog.py`: HEAD currently means4; explicitly retain4/add5 exact checks.
- `identity-migrations/identity_baseline.py:verified_access_command_extension`: metadata-only4/5 selection.
- `tests/qualify_application_register.py`: reuse fixture/custody/snapshot/attack/CLI patterns. Prior frame supplies bootstrap patterns.

## Tasks & Acceptance

- [x] Add focused permission/CLI/catalog failing tests before code; retain output. Extend existing mechanics/add0005 and exact history checks.
- [x] Add `services/access/tests/qualify_permission_register.py`: fresh synthetic matrix, populated4 preservation, Identity18 repeat, custody/retained proof. Agent implements/prepares/debugs sequentially; root reviews/verifies/stops/commits.
- [x] Add permission runbook/evidence, mutable substrate/KDG handoff; record test traceability and five impacts (scaffold/UI/context/docs/ADR).

Given valid authority/app, when executing, then mapping/evidence commit together; failures disclose nothing. Given supported history, when upgrading/repeating, then application behavior/data survive.

## Implementation Notes

Root CLI/native RED predates implementation: private permission-register-red-20261021. Actual disposable99b7231c-0a5b-4bdb-98e8-3329564c526a is up/runtime_ready=false. Canonical Python: platform/deployment/.local/identity-baseline/actor-command-zxycfmc4/owner-env/venv/bin/python. Use fresh namespaces, no fake runs/witness refresh. Existing approval covers bounded work/concurrent preservation.

Candidate delivery: Access0005, typed permission execution/recovery, actual-command
outcome isolation, exact 4/5 metadata verification and owner runbook/evidence are implemented.
Current private frame `permission-register-candidate2-20261021` passed fresh sequential
preparation, all 24 native groups and a separate retained inspection on unchanged 72 executed
sources. Focused affected adapter/CLI/input/catalog checks passed 238 tests. Earlier frames
remain preserved source-bound history. Root independent review/broad checks/normal stop/
commit remain the final delivery steps.

## Spec Change Log

## Review Triage Log

| ID | Verdict / route | Evidence and decision |
| --- | --- | --- |
| B1 | medium / patch | Shared application runbook still describes Access4/only application execution, contradicting the linked current permission preparation route; update current instructions and preserve historical evidence. |
| B2 | medium / defer | Fresh-checkout bootstrap portability predates this item: prior application qualification already depends on explicit private native/Auth/role preparation. Current evidence states this limitation; the new qualifier adds20-case inventory but does not deliver an environment bootstrap lifecycle. Record the existing prerequisite rather than add another generator. |
| B3 | medium / patch | The populated5 repeat seeds only application state. Seed actual permission/outcome/event before repeating, compare retained rows and recover its original receipt. |
| B4 | medium / patch | Application regression uses the current adapter; add actual baseline45ab5df adapter execute/recovery against5 with a pinned private source fixture captured before custody. |
| B5 | medium / patch | Revocation after a receipt-lookup retry wait is not exercised on the new SQL lookup path. Add a witnessed blocked lookup, committed revocation and denial without business-state changes. |
| B6 | low / reject | Execution holds the authority lock before entering the permission-domain wait, so revocation cannot commit during that wait. Existing domain timeout and authority serialization checks cover bounded refusal. Another interleaving fixture adds complexity for this already serialized state, without a demonstrated failure. |
| B7 | false / reject | Principals cannot be remapped: immutable Access4 guard compares executor_actor_id as identity, permits only enabled/attribution revision changes, and refuses DELETE/TRUNCATE. The proposed supported reassignment is unreachable. |
| B8 | medium / patch | Escaped NUL in canonical JSON lacks native coverage; add AC005/no-effects case. Literal NUL lookup already rejects before connection in test_permission_dispatch_and_lookup; PostgreSQL text cannot carry NUL to a SQL function, so preserve that client guard rather than invent a server-text path. |
| B9 | low / patch | The command routine binds reason/evidence to the verified canonical envelope; row guards validate allowed shapes/values and target/transition linkage, not an inverse fingerprint. Clarify this boundary in evidence without storing full commands. |
| B10 | low / patch | Receipt Boolean/ternary composition obscures the two result contracts; replace with explicit local branches, preserving the same closed validation and shared runner. |
| V1 | medium / patch | Preverified reverse-order gap: permission-first reuse followed by application execute is absent. Add both exact command replays/lookups, proving the changed application selection query independently. |


Root Step03 audit fixes completed before candidate2: pinned 0005 source and drift-before-import
test; explicit rollback-only authority fixture for forged/missing event tests with exact
`access_event_invalid` / `access_required_event_missing` assertions; application-only
permission denial and wrong-original-login execute/lookup denial. Final CLI literal audit
adds `--permission=<literal>` without relaxing other flag restrictions. Native candidate2
and focused tests prove all these cases.

## Verification

RED→focused GREEN→fresh native matrix/retained inspection. Root: isolated pytest services/access/tests apps/pts/tests/test_release.py platform/deployment/tests/test_migrate_adapter.py -q (plugins/cache disabled); both tools/py/run_compose_supabase.py --check-only routes (default; --identity-authority owned --no-seeds). Frozen intent/42 historical/13 concurrent hashes; normal dev.py stop. Record commands/results/limits.

Final root acceptance: fresh permission-register-reviewed2-20261021 passed 25 native
groups and separate retained inspection on unchanged 73-source custody. Real isolated CLI
lookup matched; actual previous adapter create/replay/recovery passed. Root 1225 affected
tests (33.69s), both composers, normal disposable stop, frozen intent, 42 historical,
13 tracked concurrent and 40 untracked concurrent preservation checks passed. Three review
lenses completed: eight findings patched, two rejected with evidence, one preexisting
bootstrap-portability prerequisite deferred. Earlier source-mismatch frame/witness retained;
no refresh/reset/removal, deployment or activation. Exact commands/results and five impacts
are in PERMISSION_REGISTER_EVIDENCE.md.
