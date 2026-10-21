---
title: Protected Access application registration
type: feature
created: '2026-10-21'
status: done
route: dispatch
review_loop_iteration: 0
baseline_commit: d307b63a9f97467f958baf5f77cd4af9cd1474d5
context:
  - /home/ck/repos/innodat/agriplatform/AGENTS.md
  - /home/ck/repos/innodat/agriplatform/platform/docs/architecture/contracts/identity-access-execution-substrate.md
  - /home/ck/repos/innodat/agriplatform/platform/docs/architecture/contracts/e1-controlled-provisioning-and-evidence.md
---

<frozen-after-approval reason="standing bounded synthetic implementation approval">

## Intent

Deliver protected `application.register` through existing Access owners: disabled applications, authorized durable recovery, no effective access.

## Boundaries & Constraints

Add Access0004, local principal/authority maps and immutable outcome/event storage; separate restricted LOGIN access_operator and NOLOGIN authority/command owners prepared explicitly before migration. Original session_user/protected enabled mappings select executor and exact command/platform/app authority (null app means all). No caller overrides or Identity table access/FK; bootstrap supplies verified actor UUIDs.

New registration creates disabled revision1 with server UTC time/executor attribution and atomically linked event/outcome. Existing app returns unchanged/current revision, no mutation/event. Preserve registry UPDATE/DELETE/TRUNCATE refusal. Immutable evidence and required created-event linkage must be database-enforced. Use current authority before effects, replay and lookup; app-bound lookup needs explicit app_id. Recheck after waits; serialize authority changes. Versioned SHA256/JCS input/retry namespace is Access-local and includes complete envelope; same operation changed input conflicts. Missing receipt is unresolved, never failure. Only retry-lock timeout means operation_busy; other waits unavailable. Bounded READ COMMITTED transactions; sanitized errors.

Extend existing target/CLI mechanics with explicit --owner access, only this executable command. Bind disposable run/owner/config/hash/database/login/private access.env; no ambient libpq/environment discovery. Preserve Identity behavior; separate credentials/authority. Other parsed Access commands reject before connection. Typed receipt: {app_id}, decimal revision, event UUID/null; no payload/fingerprint.

Preserve historical migrations/references/receipts/resources and concurrent files. No reset/prune, existing data deletion, real accounts/access, production/provision/deploy/pilot/push, Leave/editor, dependencies, permission/entry execution, enablement/grants/readers or generic framework. ACCESS-A/B consumer activation stays closed.

## I/O & Edge-Case Matrix

| Scenario | Expected |
|---|---|
| Restricted operator/new app | Disabled revision1, exact executor/time, one atomic event/outcome, typed CLI receipt |
| Same retry / changed input / existing app | Original receipt / conflict with no effects / unchanged current app, no event |
| Exact/wildcard app authority; wrong command/app/login; disabled/revoked mappings | Current permitted metadata only; deny wrong/stale authority including replay/lookup |
| Concurrent retry/app registration; held retry/authority/app locks | Single effect, correct conflict/unchanged; bounded waits, correct busy classification |
| Lost response / unresolved lookup / wrong-app lookup | Authorized original compact receipt / unresolved / denial without leakage |
| GUC/SET ROLE/raw DML/ACL/default-grantee attacks | No executor spoof, owner assumption or data/evidence mutation |
| Injected failure, malformed SQL/CLI/canonical/receipt | Atomic rollback and sanitized refusal, no partial evidence |
| Clean/1/2/3 upgrade and populated4 repeat; unknown/drift | Exact known catalogs/data preserved; unknown state refuses without normalization |

</frozen-after-approval>

## Code Map

Paths under services/access:
- `migrations/access_baseline.py`, `migrations/env.py`, `migrations/versions/` — exact controlled catalog/ACL/role/history checks; preserve0001–3.
- `identity-migrations/versions/0005_operator_authority.py`, `0006_actor_command.py`, `identity_operator.py`, `identity_operator_target.py`, `operator_cli.py` — existing implementation patterns.
- `access_operator_input.py` — closed parser; characterize existing separation before CLI expansion.
- `tests/qualify_access_registry_storage.py`, `qualify_actor_command.py`, `qualify_operator_target.py` — proof reuse.
- Private `platform/deployment/.local/identity-baseline/access-registry-reviewed-20261021/` — bootstrap/credentials patterns, never replay. Native99b7231c-0a5b-4bdb-98e8-3329564c526a was normally stopped after final verification; sibling access-registration-red-20261021 retains initial CLI/native exact3 RED.

## Tasks & Acceptance

- [x] Extend exact owner baseline and add0004 plus explicit role preparation; outer CLI/native RED before all source edits; five adapter/CLI unit RED before implementation. The history unit RED preceded helper edits but followed the initial SQL draft, a recorded inner-loop limitation. No authority seeds.
- [x] Add `services/access/access_operator.py`, owner-aware target binding and narrowly extend `operator_cli.py`; characterize CLI before refactoring.
- [x] Add focused tests and native `tests/qualify_application_register.py`; fresh preparation/custody, matrix coverage, retained inspection. Agent implements/prepares/debugs sequentially; root verifies/stops/commits.
- [x] Add `APPLICATION_REGISTER_EVIDENCE.md`, owner runbook and mutable substrate/KDG handoff notes: requirement/test evidence, five impacts; no UI/context/ADR change.

Given permitted operator, when invoked, then atomic registration/recovery succeeds. Given denial/failure, when invoked, then no effects/leaks. Given known history, when upgraded, then unrelated state survives.

## Implementation Notes

Root observed CLI/native exact3 RED before source edits; native up, runtime_ready=false.

Implementation choice: Access-only optional eight-lowercase-hex synthetic namespaces derive a fresh database and descriptor inside the actual prepared run, preserving existing canonical targets and private access.env. There is no arbitrary database selector or second runtime lifecycle. Identity target behavior remains unchanged. Mutable Identity metadata validation recognizes only the exact prepared Access role bundle and exact local Access0004 catalog; historical migrations/references remain immutable.

Pre-review candidate proof is retained under application-register-candidate-20261021. Final fresh application-register-final-reviewed-20261021 passed 18 native groups, retained inspection and root real CLI lookup; 1210 affected tests, both composers and normal stop passed. Three review lenses completed, confirmed findings patched, none deferred. Earlier frames and their source witnesses remain historical, with limitations recorded in APPLICATION_REGISTER_EVIDENCE.md.

Implementation decisions during completion: existing access_command_owner was prepared by the delivered Identity target foundation (tools/prepare_identity_target_roles.sql; retained target-role-preparation.json). Coordinate its exact new Access-only role edge/privileges in mutable Identity guards, preserving historical versions/references and negative checks. Identity18 must genuinely reverify after Access4, using metadata only, without new cross-owner raw-read grants.

For fresh CLI proof preserve canonical debug database/descriptor. Access-only preparation may choose an optional bounded synthetic namespace, deriving database/descriptor within the same actual run. Reconstruct/validate that namespace, owner, run, config, login and secret on load; Identity behavior remains unchanged. No arbitrary DB selection, prepared-sibling-run substitution, reset or new generic lifecycle.

## Spec Change Log

## Review Triage Log

| ID | Verdict / route | Evidence and decision |
| --- | --- | --- |
| E1 | medium / patch | Access role verification checks flags/edges/database CREATE and local ACLs but accepts foreign raw-table/schema or privileged function grants. Check the three restricted roles' effective foreign privileges and prove rejection with rollback-only grants. |
| B1 | medium / patch, grouped E1 | Same missing effective foreign-privilege guard; local catalog ACL checks do not reject an Identity-table grant. |
| B2 | medium / patch | The adapter checks its ten-second deadline before transaction exit, leaving commit with an older statement budget. Rearm the remaining server statement budget before exit and check the deadline after commit; retain the shared CLI's hard process bound and uncertainty recovery. Test delayed commit separately. |
| B3 | low / patch | Exact registration function assertions omit probin and raw argument metadata present in the existing registry verifier. Add the fixed metadata fields directly without another verifier or public surface. |
| B4 | low / reject | Identity deliberately validates Access objects through metadata without any Access table reads. A forged Access ledger does not change the exact validated privileges/dependencies being excluded; introducing a cross-owner ledger grant solely to inspect an administrator-corrupted marker adds complexity without everyday harm. Access's own controlled route already checks history. |
| B5 | medium / patch | Native attacks do not exercise malformed canonical bytes/direct SQL arguments; add bound parameter cases proving AC005 and unchanged state. |
| B6 | medium / patch | Overlap covers identical retries and distinct operations/same app, but not one operation racing with different canonical input. Add a witnessed race asserting one durable result and conflict without loser effects. |
| B7 | medium / patch | Disabled principal execute denial already exists; disabled-principal replay/lookup and unchanged state are not independently checked. Extend that existing case. |
| B8 | low / reject | Both owners call the same unchanged dispatch process boundary, already exercised by real process timeout/termination tests. Native Access separately proves actual-commit response loss and durable recovery, plus real isolated CLI execute/lookup. Another native termination fixture adds machinery for a shared boundary already verified; keep these proof limits explicit. |
| B9 | medium / patch | Runbook currently says private password preparation and external actor verification without concrete owner-controlled steps/evidence. Document scoped synthetic preparation and exact verified actor handoff without creating another tool or authorizing real account changes. |
| B10 | medium / patch | Runbook prohibits reversal but lacks executable investigation/resume guidance for preparation/migration/postcondition failures. Document read-only inspection, preservation, controlled resume and closed activation gate. |
| V1 | medium / patch | Preverified Access-path regression gap: existing busy/isolation/autocommit assertions execute the separate Identity runner. Add parameterized execute/lookup tests preserving caller transaction and proving zero SQL/commit/rollback on refusal. |
| V2 | medium / patch | Preverified event-audit gap: native proof counts events but never compares stored reason/evidence with submitted values. Assert distinctive submitted values and exact persisted event context. |


## Verification

Canonical Python `platform/deployment/.local/identity-baseline/actor-command-zxycfmc4/owner-env/venv/bin/python`; isolated pytest, no plugins/cache. Focused RED/GREEN, fresh native aggregate and retained verification, then root affected `services/access/tests apps/pts/tests/test_release.py platform/deployment/tests/test_migrate_adapter.py -q`, both composers (--check-only; --identity-authority owned --no-seeds --check-only), whitespace/history/concurrent audit, normal dev.py stop. Preserve all prior proof frames.

Final result: 1210 affected tests passed in 34.16s; 18 fresh native groups and separate retained verification passed with unchanged 70-source custody, root real CLI recovery matched. Both composition routes passed; normal runtime stop completed without reset/removal. Eleven finding rows patched, two low findings rejected with evidence, none deferred. Five impacts and exact commands/results are recorded in APPLICATION_REGISTER_EVIDENCE.md.
