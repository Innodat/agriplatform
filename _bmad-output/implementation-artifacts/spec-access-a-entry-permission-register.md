---
title: Protected Access entry-permission registration
type: feature
created: '2026-10-21'
status: done
route: dispatch
review_loop_iteration: 0
baseline_commit: cdfa6f3792f7e7880ae84b13aae92a2ef8ee6ad3
context:
  - /home/ck/repos/innodat/agriplatform/AGENTS.md
  - /home/ck/repos/innodat/agriplatform/platform/docs/architecture/contracts/identity-access-execution-substrate.md
  - /home/ck/repos/innodat/agriplatform/platform/docs/architecture/contracts/owned-write-and-secret-execution.md
---

<frozen-after-approval reason="standing bounded synthetic implementation approval">

## Intent

Deliver protected `entry_permission.register`: immutable app/permission entry mapping with atomic evidence/recovery, granting no access.

## Boundaries & Constraints

Add Access0006; preserve historical files/data/receipts, concurrent work, application/permission behavior and Identity18 metadata-only verification. Accept exact clean/1/2/3/4/5/6; unexpected state refuses without repair. No new roles/credentials/lifecycle/framework.

Require platform scope, app_id, literal ASCII permission1–200 bytes (controls/DEL allowed, NUL forbidden), expected_absent=true. Verify existing exact permission/app association; both permission scopes and disabled app are valid. Missing/wrong association conflicts without writes; identical entry unchanged. Multiple explicit permissions per app are allowed. Never create/reassign permissions, change scopes, enable apps or grant access.

Derive executor/time from original-session principal and exact enabled entry_permission.register/platform/app authority; other command authority confers none. Recheck after waits; retain authority serialization, command/scope-specific outcome uniqueness and stable outcome locks. Serialize exact entry mapping. Only retry-lock timeout is busy; preserve bounded idle READ COMMITTED, late/lost-commit uncertainty and sanitized errors.

Entry/outcome/access.entry_permission_registered event commit atomically with database-enforced required linkage and closed event/result validation. Receipt target {app_id,permission}, created/unchanged, revision=null, event UUID only for creation. Lookup requires explicit exact target/current authority; wrong target denies, absent unresolved. SHA256/JCS binds full envelope and literal escaping. Same UUID across all three commands has independent execute/replay/lookup.

Entry transition is {}; type/target express immutable binding creation. Routine binds reason/evidence to canonical input; row guards validate structure/values/linkage. Retain the existing single-event registration subset, without generic multi-event WRITE claims.

Grant existing command owner only SELECT/INSERT entry rows and exact routines to operator. Preserve raw operator/runtime, role-assumption, foreign-data and registry mutation refusals. No dependency changes, production/real accounts/access, infrastructure/deploy/pilot/push/reset/prune, Leave/editor, enablement/grants/ACCESS-B or consumer activation.

## I/O & Edge-Case Matrix

| Scenario | Expected |
| --- | --- |
| New/both scopes/multiple entries/literal boundaries | Exact binding, server attribution/evidence and typed CLI receipt |
| Identical retry/new operation; changed input; missing/wrong association | Original receipt/unchanged/no event; conflict/no effects |
| Wrong command/app/login, disabled/revoked principal/authority | Execute/replay/lookup refuse without leakage; witnessed wait revocation |
| Concurrent duplicate/distinct/changed attempts; held locks | One binding, correct conflict/unchanged, bounded busy classification |
| Three-command UUID reuse, lost response, lookup target/unresolved | Independent original recovery in both orders; no foreign receipt |
| Malformed direct SQL/JCS/NUL, spoofed context/raw DML, forged/missing evidence | Safe refusal, exact guard assertions, atomic rollback |
| Populated5 upgrade/6 repeat, earlier heads, old clients, Identity18, drift | Preserve data/receipts; exact known catalogs pass; unknown state refuses |

</frozen-after-approval>

## Code Map

Under `services/access/`:
- `access_operator_input.py`: RegisterEntryPermissionCommand, unchanged.
- `access_operator.py`, `operator_cli.py`: extend union/dispatch/lookup; reuse runner/JCS/--permission=<literal>.
- `migrations/versions/`: preserve0001–5; add0006 routines/linkage/ACL.
- `migrations/access_baseline.py`, `access_registration_baseline.py`, `access_registration_catalog.py`: retain5/add6 exact checks; HEAD currently means5.
- `identity-migrations/identity_baseline.py:verified_access_command_extension`: metadata-only4/5/6 selection.
- `tests/qualify_permission_register.py`, `qualify_application_register.py`: reuse custody/snapshots/attacks/old adapter. Entry SELECT is now legitimate; test forbidden UPDATE.

## Tasks & Acceptance

- [x] Add failing focused entry/CLI/catalog tests before code; retain RED. Extend existing mechanics/add0006 with exact historical preservation.
- [x] Add `services/access/tests/qualify_entry_permission_register.py`: fresh matrix, populated5/6, actual previous0005 adapter, Identity18, custody and retained proof. Agent implements/prepares/debugs sequentially; root reviews/verifies/stops/commits.
- [x] Add entry runbook/evidence; update current shared instructions, substrate and KDG handoffs. Record traceability and scaffold/UI/context/docs/ADR impacts.

Given valid authority/association, when executing, then mapping/evidence commit together. Failures disclose nothing. Given known history, when upgrading/repeating, then behavior/data survive.

## Implementation Notes

Root RED retained at private entry-register-red-20261021. Actual run99b7231c-0a5b-4bdb-98e8-3329564c526a is up/runtime_ready=false. Python: platform/deployment/.local/identity-baseline/actor-command-zxycfmc4/owner-env/venv/bin/python. Fresh namespaces/custody. Bootstrap portability remains deferred. Root final preparation follows final source-frozen handoff; no later edits. Existing approval covers dirty-tree preservation/work.

## Spec Change Log

## Review Triage Log

| Finding | Verdict / route | Evidence |
| --- | --- | --- |
| Blind1 distinct-operation race | medium / patch | Existing duplicate creates the mapping first; distinct operations only prove unchanged. Add initially absent mapping and exact effects. |
| Blind2 scoped authority success | medium / patch | Only wildcard success and other-app denial are native entry cases. Add exact-app-only create/replay/lookup. |
| Blind3 original login boundary | medium / patch | Prior wrong-login cases invoke permission routines; entry routines need explicit calls under an unregistered session. |
| Blind4 principal revoked during wait | medium / patch | Entry wait tests revoke authority only; add principal revocation for execute/lookup after a witnessed retry wait. |
| Blind5 direct lookup validation | medium / patch | New SQL lookup validates independently; direct malformed inputs/isolation have no entry-native cases. |
| Blind6 lookup lock classification | medium / patch | Entry lock classification invokes execute only; separately implemented lookup needs retry and authority lock cases. |
| Blind7 forged event fields | medium / patch | Entry-specific attack changes transition only; add independent type/target/actor/operation/link failures asserting intended guards. |
| Blind8 retained aggregate source | medium / patch | Retained branch checks aggregate status but omits equality of its source inventory to captured witness. Add explicit equality and rejection test. |
| Blind9 concrete authority preparation | low / patch | Entry runbook refers to an application-only SQL example; add narrow entry authority SQL using verified inputs. |
| Blind10 Code Map historical HEAD note | low / reject | This records the preimplementation code map; proposed remedy edits this Build spec and is rejected by Step04. Current runbooks explicitly name6. |
| Verification1 creation race | medium / patch | Preverified: absent mapping race is missing; same root cause as Blind1. Both outcomes must recover with one creation/event. |

Edge-case lens returned no findings. All layers collected before triage. Patch groups preserve the frozen intent and add no public surface.

## Verification

RED→focused GREEN→fresh native matrix/separate retained check. Root repeats the affected regression and both composition commands recorded in services/access/PERMISSION_REGISTER_EVIDENCE.md. Verify frozen intent,43 historical/13 tracked/40 untracked concurrent hashes; normal dev.py stop. Record commands/results; pins unchanged.


Final verification (2026-10-21): all review patches completed; no unresolved current-item findings. Root fresh bootstrap and32 native groups PASS; separate retained state/source inspection PASS; independent isolated CLI lookup matches saved receipt; normal native stop completed/runtime_ready=false. Affected Access/PtS release/migration-adapter regression:1236 passed in42.03s. Both composition dry runs PASS. Final proof/evidence: services/access/ENTRY_PERMISSION_REGISTER_EVIDENCE.md and private entry-register-reviewed-20261021/root-verification.json. Historical43/tracked concurrent13 and frozen intent unchanged. Concurrent untracked Scribeswell planning edits preserved and excluded; no source files outside this item staged. Existing bootstrap portability remains deferred. Five impact decisions recorded; dependencies unchanged.
