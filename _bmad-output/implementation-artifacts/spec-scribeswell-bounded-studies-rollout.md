---
title: 'Bounded private Studies rollout preparation'
type: 'feature'
created: '2026-10-28'
status: 'done'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: 'f1fd78025ad7bdad0e06db7129f5435a8d7c8fe5'
context:
  - 'apps/scribeswell/docs/OWNER_READINESS_HANDOFF.md'
  - 'apps/scribeswell/docs/PRIVATE_MIGRATION_REPORT.md'
  - 'platform/docs/development/migration-verification.md'
---

<frozen-after-approval reason="human-owned intent — routine checkpoints approved in invocation">

## Intent

Prepare a bounded rollout of private Studies writes for Scribeswell's existing sole consumer. Public reading is already deployed. Produce concrete candidate deployment configuration, fail-closed migration/readiness gates, focused local evidence and a data-preserving maintenance/recovery procedure before any production approval request.

## Boundaries & Constraints

**Always:** preserve unrelated work. Use qualified frozen Identity0026/Access0019, readiness v2 and the existing owner preparation contract. Default remains public read-only. Production private mode requires exactly one configured canonical account UUID plus fresh Access authority on every request; account restriction never grants authority. Disable self-enrollment in this bounded mode so other accounts cannot mutate Access through the app. Preserve public GET/OPTIONS Bible routes, existing services, credential separation, TLS and saved rows. Migration failure or unknown outcome and absent/stale readiness block activation. Retain exact source/image/proof references. A short explicit maintenance window is acceptable.

**Never:** deploy, run production SQL, push, change provider/signup settings, send external mail, alter accepted ADRs, adopt Identity0027/mixed service work, enable sharing, or run a broad upgrade rehearsal. Do not restore an old backup over saved writes, downgrade/stamp migrations, automatically roll back databases, or treat an operator boolean as live readiness proof. Production execution remains separately approved.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|---|---|---|---|
| Default | Studies disabled | Existing public reader; no private authority | Partial private config refused |
| Bounded production | One account, complete restricted config | Only fresh Access-approved matching account may use Studies | Others denied; enrollment blocked before upstream mutation |
| Preparation | Retained deployment config plus exact candidate inputs | Reviewable app-specific candidate and ordered maintenance commands | No remote side effects; missing target inputs reported explicitly |
| Gate | Wrong/missing private head report or readiness/source binding | Activation refused | Preserve reports, reconcile actual committed state |
| Recovery | Data saved at head0009, private mode disabled and restored | Public reading continues, saved private rows/receipts survive | Forward repair, no destructive schema rollback |

</frozen-after-approval>

## Code Map

- `apps/scribeswell/backend/config.py`, `main.py`, `personal_notes_access.py`: unconditional production refusal, private router construction, verified account authorization; add narrowly scoped production option, no owner replacement.
- `apps/scribeswell/deployment/`: app-owned rollout preparation/gate tooling and env example; pure `studies_release_contract.py` validates observed committed head0009.
- `platform/deployment/host-release.py`, `render_gateway.py`, `release.py`: existing whole-registry release currently intentionally refuses private production; do not loosen these global guards or invoke against mixed tree. Reuse contracts only; app-specific prepared overlay/runbook must preserve retained unrelated configuration.
- `services/access/studies_readiness.py`: owner-owned v2 source-bound artifact validator/preparation; use immutable archive `/tmp/studies-current-deb424b`, not edited live owner implementation. Original qualification `/tmp/studies-current-native-20261027-review/current/qualification.json`.
- `apps/scribeswell/tests/test_studies_migration_report_native.py`: fresh PG17 fixture and controlled private worker; reuse for focused first rollout and disable/re-enable preservation rather than historical upgrade matrix.
- `apps/scribeswell/docs/API_IMAGE_INTEGRATION_EVIDENCE.md`: prior shipped image qualifies development mode only; new production-capable image needs focused evidence and cannot inherit unchanged image identity.
- `apps/scribeswell/web/src/context/StudiesContext.tsx`: existing VITE_STUDIES_ENABLED opt-in; prepared frontend recipe must explicitly set private API URL and preserve deployed base/public API configuration. No product UI change.

## Tasks & Acceptance

**Execution:**
- [x] `apps/scribeswell/backend/{config,main,personal_notes_access}.py` — allow bounded production mode for one existing account, require private TLS, block enrollment before upstream calls, retain current checks.
- [x] `apps/scribeswell/deployment/studies_rollout.py` and tests — prepare app-only candidate configuration/commands from retained external target inputs; validate exact source/image/readiness/private migration bindings without production actions. Keep strict bounded input parsing and safe errors. Activation instructions require actual owner preparation and migration results; absent target inventory prevents executable activation approval.
- [x] `apps/scribeswell/tests/` — observe acceptance red, prove production restriction/denial/public independence and focused native saved-data preservation across disable/re-enable and failed migration refusal.
- [x] `apps/scribeswell/docs/BOUNDED_STUDIES_ROLLOUT.md`, handoff and evidence — exact ordered commands, maximum maintenance budget/stop conditions, affected owner scope, admission/preflight, verification, public-reader recovery and forward repair. Record unresolved live inputs honestly.

**Acceptance Criteria:**
- Given default config, when reading publicly or attempting private access, then existing public behavior remains and private routes remain absent.
- Given bounded production mode, when any account requests private work, then matching fresh verified authority is required and self-enrollment cannot mutate shared owners.
- Given missing/stale source-bound readiness or failed/unknown private migration, when preparing activation, then no executable activation is authorized.
- Given committed saved data, when private mode is disabled and restored on the same schema, then saved content, revisions and operation receipts remain intact and public reading succeeds.
- Given unrelated service changes, when preparing the rollout, then only explicitly selected Scribeswell/qualified Access/gateway inputs change; no broad release is prepared.

## Implementation Notes

Coordinator observed dirty main; user explicitly authorized preserving unrelated changes and approved routine BMAD checkpoints. Starting delivery ada6a2f is ancestor of baseline. No remote operations authorized by this build. Investigation found whole-registry Content/PtS gate and mixed Identity0027, motivating app-specific preparation only. Production target inventory, account UUID and secret configuration remain external inputs, never invented.

Parent verification: 105 affected tests passed in16.16s after explained worker-test environment isolation repair; previous combined run94 passed/1 failed on leaked MIGRATION env. Browser bounded4 passed8.4s; unchanged default enrollment2 passed10.6s. Frontend build and15-migration composition check-only passed. Actual local API default CMD enabled/disabled probes and all60 source hashes passed; migration image all40 bytes passed after actual nonroot permission failure was fixed in packaging. Native3 selected tests passed5.52s; separate owner qualification retained. No published registry digest, live production inventory or execution is claimed. Selected delegated model/effort Sol High; actual implementation model as requested by launcher, usage unavailable. Coordinator model/effort and total elapsed unavailable. User approved routine checkpoints; spec slightly exceeds suggested token range as one coherent release preparation.

## Spec Change Log

## Review Triage Log

| Source | Verdict | Evidence and route |
|---|---|---|
| Blind: effective Compose environment | high | Selected service inline environment has precedence over generated env_file; retained overrides survive. Could change bounded account/authority or disable private mode. Patch: reject selected inline overrides. |
| Edge: effective Compose environment | high | Same verified override root cause as blind finding; retained mapping is deep-copied then only env_file changes. Patch with same refusal. |
| Edge: relocated relative paths | medium | Compose is relocated into a new candidate directory while retained relative bind/env/config/secret paths are copied unchanged. Reachable supported input changes file resolution or fails activation. Patch: refuse unsupported relative/indirect topology in this bounded adapter. |
| Edge: implicit project identity | medium | No required explicit compose.name; new directory may select another project under documented commands. Patch: require recorded explicit name and compatible retained network selection. |
| Edge: copied gateway mount | medium | Code compares volume source with inventory-copy pathname, but runbook copies a deployed gateway whose original Compose source path differs. Correct inventory refuses. Patch: match one safe absolute APISIX-target mount. |
| Verification: operation receipt route | medium | Reviewer replaced operations URI in-memory and all42 rollout checks passed; existing browser/native tests bypass gateway. Patch: assert exact private URI coverage plus inherited upstream/rewrite. |

All6 findings were repaired and covered by the64-case tool suite (22 regressions first failed). Parent post-review affected suite passed127 tests in3.25s, with the existing TestClient warning. Native/schema/runtime/frontend were unchanged by these tool/test repairs, so no broader rerun was required. No deferrals or intent gaps. All fixes are bounded input refusals or direct predicate/test corrections without new public surface; generated candidate and runtime behavior remain the approved single-account rollout.

## Verification

Use `apps/scribeswell/.local/owner-integration-20261027/python/bin/python -B -m pytest` for focused new and affected tests. Native proof uses a uniquely owned disposable PostgreSQL17 with exact cleanup; exclude existing KDG/Leave fixtures. Build and inspect the changed candidate API image if local Docker permits. Run composition check-only. Record command results, source hashes, skipped checks and production limitations; collection is not proof.
