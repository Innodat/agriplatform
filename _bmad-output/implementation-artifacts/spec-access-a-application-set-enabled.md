---
title: Protected Access application enablement
type: feature
created: '2026-10-21'
status: done
route: dispatch
review_loop_iteration: 0
baseline_commit: 71599a57aae331339149483514409da8ed760bda
context:
  - /home/ck/repos/innodat/agriplatform/AGENTS.md
  - /home/ck/repos/innodat/agriplatform/platform/docs/architecture/contracts/identity-access-execution-substrate.md
---

<frozen-after-approval reason="standing bounded synthetic implementation approval">

## Intent

Deliver application.set_enabled through the existing protected owner route, including mutable application revision/attribution/audit guards. Add Access0007; no consumer activation or grants.

## Boundaries & Constraints

Reuse parser/JCS/SHA256, roles, bounded READ COMMITTED runner/CLI. Require current original-session application.set_enabled/platform/app authority; registration authority confers none. Serialize retry→authority→existing app lock; recheck after waits. Only retry-lock timeout is busy. Replay precedes current revision checks; changed input conflicts. Exact-target lookup requires current authority; missing unresolved, wrong target denied. Four command/scope namespaces stay independent.

Missing app conflicts. New operations require expected revision even when desired enabled already matches. Changed increments once, derives executor/time, preserves app identity/creation attribution and all permissions/entries/grants. Unchanged preserves all application fields with no event; changed at bigint max conflicts, unchanged at max valid. Typed receipt retains {target:{app_id},disposition:changed|unchanged,revision:decimal,event_id}; changed requires UUID, unchanged null.

Changed row/outcome/access.application_availability_changed event commit atomically. Exact transition {before:{enabled,revision},after:{enabled,revision}}, revision strings. Database guards enforce OLD/NEW linkage, actor/time and required event; routine binds reason/evidence to canonical input. No digest inversion claim. Retain single-event subset. Only command owner gains UPDATE(enabled); operator exact routine EXECUTE only. Guard application identity/creation/revision/time, raw writes and missing/forged evidence; retain DELETE/TRUNCATE and permission/entry immutability.

Recognize exact clean/1/2/3/4/5/6/7 without normalization; preserve populated data/receipts and all historical migrations/references. Metadata-only Identity18 verification selects7 without Access data reads. Unknown state/defaults/roles/source drift refuses. Preserve concurrent work and native resources. No new framework/dependencies, real targets, infrastructure/deploy/pilot/push/reset/prune, Leave/editor, grants/org enablement/consumers.

## I/O & Edge-Case Matrix

| Scenario | Expected |
| --- | --- |
| Enable/disable/re-enable; legacy attribution; matching state; missing/stale including stale unchanged; max revision | Exact managed fields/transition/receipt, unchanged preservation, conflict no effects |
| Identical/changed retries, four-command UUID reuse, lost COMMIT response, lookup target | Original independent receipts, current-authorized recovery, no leakage |
| Narrow/wildcard/wrong command/app/login; disabled/revoked principal/authority | Execute/replay/lookup refusal, witnessed revocation after retry wait |
| Duplicate/distinct/changed concurrent operations, same expected revision, register/enable contention, retry/authority/domain locks | One revision transition; correct unchanged/conflict and bounded classification for execute/lookup |
| Invalid SQL/JCS/booleans/revisions/isolation; spoofed GUC/raw DML; independent forged/missing update/outcome/event fields | Exact safe guard refusal and atomic rollback, no unrelated earlier guard masking |
| Populated6 upgrade/7 repeat, prior heads, real previous6 adapter, Identity18, catalog/source drift | Original data/receipts retained; exact new metadata verified; unexpected state refuses |

</frozen-after-approval>

## Code Map

Paths under services/access:
- migrations/versions/0007_application_set_enabled.py: command/authority, row/deferred evidence guards; explicitly extend guard_command_evidence/require_command_event.
- migrations/access_baseline.py, access_registration_baseline.py, access_registration_catalog.py: preserve explicit6 branches (HEAD currently6), derive7 source-pinned catalog/ACL/trigger/function metadata. identity-migrations/identity_baseline.py: installed-routine metadata selection.
- access_operator.py/operator_cli.py: typed mutable receipt, execute/outcome dispatch. Parser unchanged. tests/test_application_enable_input.py closed-execution assertions intentionally evolve; retain Identity/validation protections.
- tests/qualify_entry_permission_register.py: reuse fixtures/custody/retained checks. Add tests/qualify_application_set_enabled.py and tests/test_application_set_enabled.py; retain inherited behavior.

## Tasks & Acceptance

- [x] Observe RED; deliver0007/adapter/CLI with TDD/characterization.
- [x] Fresh native matrix/populated preservation/previous6 client/retained proof; trace all rows to tests.
- [x] Add APPLICATION-SET-ENABLED.md/APPLICATION_SET_ENABLED_EVIDENCE.md; update current substrate/KDG/runbooks and five impacts.

Given valid authority/revision, changes commit atomically. Stale/forbidden input has no effects. Historical state/receipts survive upgrades/replay.

## Implementation Notes

Approved synthetic run99b7231c-0a5b-4bdb-98e8-3329564c526a is up/runtime_ready=false; preserve dirty tree. Root RED: set-enabled-red-20261021 (CLI unsupported/native42883). Preservation: /tmp/set-enabled-preservation.json. Agent implements/tests/prepares sequentially; root reviews/verifies/stops/commits after source-frozen handoff. No nested workflow/agents/commit/later writes. Reuse entry-register-reviewed-20261021 bootstrap scripts, fresh namespaces/custody, never old credentials/state/witnesses. Preserve failures; bootstrap portability deferred. Actual old adapter: set-enabled-previous-20261021/bootstrap_previous_entry_adapter.py.

## Spec Change Log

## Review Triage Log

| Finding | Verdict / route | Evidence |
| --- | --- | --- |
| Blind1 independent sessions | low / patch | Current contention shares one authority lock; add a second already-existing synthetic login/controlled owner role to exercise separate authority locks, with no new roles or credentials. |
| Blind2 later wait revocation | low / patch in part | Revocation can commit while command waits on an authority lock already held by the revoker; test that denial. During application wait the command already holds the same authority serialization lock needed by revocation, so committed revocation there is unreachable; reject that portion. |
| Blind3 populated grant preservation | low / patch | Functional grant snapshots are empty. Seed one legacy synthetic grant and prove it survives all toggles/replay. |
| Blind4 concurrent unchanged state | low / patch | Concurrent matching commands assert disposition only; add full application/event equality. |
| Blind5 register contention witness | low / patch | Futures alone permit sequential completion. Hold app lock, witness both waiters, then release. |
| Blind6 outcome insertion rollback | false / reject | enablement_attacks mutates outcome revision/disposition/executor/event before INSERT, asserts exact outcome-guard rejection after UPDATE and compares full before/after snapshots. This already proves failure at outcome insertion rolls back row/outcome/event. |
| Blind7 independent event fields | low / patch | Existing injections cover selected fields but not every new link/value independently. Add after.enabled/string revision, operation, scope and outcome-link mutations with exact guard refusal. |
| Blind8 malformed worker error safety | low / patch | New malformed-worker assertion checks exception class only. Restore fixed args/context/cause/redaction using each existing error family. |
| Blind9 authority SQL | low / patch | Linked example creates registration authority only; add exact narrow enablement preparation/revocation example with verified inputs. |
| Blind10 previous5 client | low / patch | Actual previous6/4 clients run; prior entry stage with previous5 was replaced. Extend replacement using existing pinned previous5 adapter, without reusing populated exact6 seeding. |

All three lenses collected before triage. Edge and verification-gap lenses returned no findings. Changes are bounded test/document corrections; no new public surface/roles/credentials or intent change. No new deferral.

## Verification

Python: platform/deployment/.local/identity-baseline/actor-command-zxycfmc4/owner-env/venv/bin/python. Pytest disables plugins/cache; -I -B -m pytest -p no:cacheprovider. RED→focused→native/retained; root services/access/tests plus PtS release/migrate-adapter tests. Both composition dry runs (default; --identity-authority owned --no-seeds). Record commands/results/hashes; whitespace/preservation and normal stop. No broader readiness.

Final root verification: reviewed test/runbook patches complete; fresh39-stage native matrix and separate retained/79-source custody PASS; independent real CLI recovery PASS; normal stop completed/runtime_ready=false.1264 affected tests PASS35.67s and both composition dry runs PASS. Historical46/parser/frozen hashes and tracked concurrent13 unchanged; evolving untracked Scribeswell work preserved/excluded. No new deferral; existing bootstrap portability remains deferred. Exact commands/results/five impacts: services/access/APPLICATION_SET_ENABLED_EVIDENCE.md. No real-target configuration, grants, consumers or activation.
