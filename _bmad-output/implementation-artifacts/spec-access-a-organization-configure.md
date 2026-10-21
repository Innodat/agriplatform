---
title: Protected organization application configuration
type: feature
created: '2026-10-21'
status: done
route: dispatch
review_loop_iteration: 0
baseline_commit: fd8248f43a3355b9494e031128d2ffdafd0a8fb0
context:
  - AGENTS.md
  - platform/docs/architecture/contracts/identity-access-execution-substrate.md
---

<frozen-after-approval reason="standing bounded shared prerequisite approval and next instruction">

## Intent

Deliver protected organization_application.configure through existing Access storage/parser/operator/CLI and Identity19 verification: revision-safe configuration with atomic recoverable evidence. Admission/consumer activation stays gated.

## Boundaries & Constraints

Add Access9 after8; retain old migrations/references/data/four platform commands. Derive executor from original session_user and enabled protected authority: exact command/org, matching-or-explicit-all app, null target_account_id. No platform/other-command substitution. Check before Identity; set transaction-local setup org/actor/empty-account context, recheck after waits. No foreign table reads/new roles/Identity grants. Mutable Identity19 verifier selects exact9 by metadata only.

Identity observation expires five seconds from verification start, including waits/replay; expiry means unavailable. Every execution reobserves; missing/deleted org refuses. Historical lookup requires current org/app authority, not current org eligibility. Registered app need not be globally enabled; disable/re-enable preserves settings/grants.

Expected absence creates1; existing row conflicts. Expected revision must match before changed/unchanged; absent row conflicts. Change increments once with server actor/UTC; unchanged preserves attribution and event_id=null. Preserve creation identity/history, delete/truncate refusal, constraints/forced org RLS. Only command owner gains necessary local DML with authority/deferred-evidence guards.

Scope outcomes/retry locks by organization/executor/command/operation; canonical UUID scope and SHA256/JCS command fingerprint. Changed input with same key conflicts; other org/command cannot collide. Result target is exact org_id/app_id, disposition created/changed/unchanged, decimal revision and nullable event_id. Use access.organization_application_changed with compact before/after enabled/revision (before=null on create). Commit row/outcome/event together; missing/forged evidence rolls back. Preserve existing safe error distinctions; busy only for operation retry lock. No sensitive logs or raw driver exceptions.

Synthetic/local commit only; preserve concurrent work/resources, TS7.0.2 and ADRs. No reset/prune, real account/access changes, production/provision/deploy/pilot, Leave/editor, grants/readers/admission, new service/generator or push.

## I/O & Edge-Case Matrix

| Given / when | Then |
| --- | --- |
| Exact authority, active org and registered app / create or matching update | Created1 or changed next revision; atomic evidence; unchanged retains row |
| Wrong/missing/revoked principal/command/org/app, malformed direct SQL or context spoof | Safe refusal and no effects; check authority before Identity |
| Missing/deleted org, delayed observation/locks/replay or unsupported isolation | Conflict or unavailable per existing contracts; no partial write |
| Same operation retry/changed input; other org/app/command; scoped lookup | Exact replay or conflict, current authority, no substitution/leak |
| Concurrent create/update, revocation, response loss, revision overflow | One valid transition, safe conflict/recovery and unchanged unrelated rows |
| Raw/forged/empty/noop/UPSERT/MERGE writes; evidence omission/mismatch | Refuse unsupported paths; rollback entire attempted transaction |
| Populated8 upgrade9/repeat, actual old adapter, catalog/history drift/failure | Preserve data/receipts; exact verification; bounded rollback and forward recovery |

</frozen-after-approval>

## Code Map

Paths relative to services/access unless stated:
- migrations/versions/0009_organization_application_configure.py: extend0007/8 scopes, guards, evidence, local grants; never edit historical revisions.
- migrations/access_baseline.py: preserve explicit8 and add exact9 catalog/ACL/RLS/trigger/FK checks. identity-migrations/identity_baseline.py: select9 by routine metadata, no business reads.
- access_operator.py: reuse parser variants, scope-aware canonical/lock key, typed receipt, execute/outcome. operator_cli.py: existing isolated worker/CLI, strict response/target checks.
- tests/qualify_organization_application_configure.py: reuse storage/enablement and Identity19 fixture helpers; source-bound --all/--verify-retained. tests/test_organization_application_configure.py and affected suites: focused acceptance-first and preserved historical assertions.
- ORGANIZATION-APPLICATION-CONFIGURE.md, ORGANIZATION_APPLICATION_CONFIGURE_EVIDENCE.md: runbook/traceability. Root updates substrate contract, DEVELOPMENT and KDG handoffs/five impacts.

## Tasks & Acceptance

- [x] Observe baseline8 acceptance failure and focused RED; implement bounded owner command through existing surfaces.
- [x] Verify matrix, exact9/historical8 compatibility, actual restricted logins, source custody, rollback/recovery and separate retained proof.
- [x] Review, run affected regression/composition checks, record five impacts and scoped commit.

Given implementation is verified synthetically, when real consumers are considered, then grants, ACCESS-B and coordinated PtS/KDG activation still require their own completed gates.

## Implementation Notes

No intent gap; five seconds/compact transition are internal choices from existing patterns. Standing approval covers dirty-tree continuation. /tmp/org-config-preservation.json binds baseline/concurrent/history. Root owns DB/Docker/preparation, old-source packages, final evidence/qualification/commit. Agent owns code/tests/qualifier/runbook only: no DB/Docker/commit/nested workflow. Native run99b7231c-0a5b-4bdb-98e8-3329564c526a is up; organization-configure-20261021 under platform/deployment/.local/identity-baseline retains actual Access8 missing-routine RED. Fresh fixture bootstrap remains private, not a portable CI claim.

## Spec Change Log

## Review Triage Log

| Finding | Verdict / route | Evidence |
| --- | --- | --- |
| Blind1 freshness after writes | medium / patch | Last check precedes INSERT/UPDATE/FK/evidence work; a subsequent lock wait can exceed the observation before return. Add final check and rollback proof. |
| Blind2 inherited source custody | medium / patch | source_snapshot omits four imported qualifier helpers; supplemental root witness protects this run but standalone retained validation needs their hashes. |
| Blind3 previous adapter all four commands | medium / patch | upgrade_previous executes only set_enabled through old8 module. New evidence guard handles all four, so verify actual old adapter register/permission/entry behavior too. |
| Blind4 populated prior permissions/entries | medium / patch | Those before-upgrade tables/receipts are empty; comparisons are vacuous. Populate and replay actual previous8 receipts across9. |
| Blind5 concurrent identical retries | medium / patch | Current concurrent documents have distinct operation UUIDs. Add same-operation simultaneous execution with one transition/outcome/event and identical receipts. |
| Blind6 forged evidence | medium / patch | Omission test exists, but no wrong scope/target/executor/revision/disposition/transition probes. Exercise existing exact guards and whole rollback. |
| Blind7 MERGE boundary | medium / patch | New native suite has UPSERT/empty/noop but no current9 MERGE actions. Add matching/nonmatching/empty negative cases, without a generic SQL classifier. |
| Blind8 spoofed context/original login | medium / patch | Authority negatives do not supply adversarial GUC context. Prove settings cannot grant rights or disclose receipts and another login cannot impersonate the mapped operator. |
| Blind9 direct SQL boundary | medium / patch | Six cases omit invalid encoding/JSON/duplicates/size/argument mismatches/isolation. Reuse known fixed malformed-case patterns at the DB boundary. |
| Blind10 pending final evidence | low / patch (root) | Draft evidence still contains future results and lacks final reproducible commands; root completes it before delivery. |
| Edge1 expiry/conflict priority | medium / patch | After business/row lock waits, missing app/revision conflict can precede expiry check. Recheck expiry before eligibility/revision conflict, preserving authority denial priority. |
| Edge2 inherited source custody | medium / patch | Same omission independently established; include all actual imported helper modules in standalone source_snapshot. |
| Gap1 cross-org recovery collision | medium / patch | Preverified: same-operation two-org execution assertions never look up either colliding receipt. Add exact independent lookup/replay comparisons for both original documents. |
| Root replay-read expiry | medium / patch | SELECT saved outcome/app existence may itself wait after an earlier clock check; replay/fingerprint/missing-app branches must recheck before returning/conflicting. Same lifetime cause as Blind1/Edge1. |

## Verification

P=platform/deployment/.local/identity-baseline/actor-command-zxycfmc4/owner-env/venv/bin/python. Focused pytest RED/GREEN, native matrix plus separate retained inspection, actual previous8 adapter, source/log custody. Root regression: PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 P -I -B -m pytest services/access/tests apps/pts/tests/test_release.py platform/deployment/tests/test_migrate_adapter.py -q -p no:cacheprovider. Both tools/py/run_compose_supabase.py --check-only modes(default; --identity-authority owned --no-seeds). Preserve50 historical bindings/concurrent bytes; normal stop. Record scaffold/UI/context/docs/ADR impacts; no shared UI/client/generator/context rule/new ADR expected.

Root pre-review native13 groups passed in organization-configure-proof-20261021, including actual old8 adapter/CLI/Identity19 repeat and observation/revocation. Affected regression1344 passed52.89s. Supplemental root-helper-before.json independently binds four unchanged inherited helpers, root driver and actor receipt; current qualifier snapshot omits those four helper files. Final review verification pending.


Final reviewed verification: fresh organization-configure-accepted-20261021 passed16
native groups and separate read-only retained inspection, with160 matching source
bindings and78 exact baseline Git files. Final focused18 passed; affected regression
1348 passed59.61s; both composition checks exit0. All review findings above are patched,
including seven late-wait expiry/rollback cases and actual previous8 four-command
compatibility before/after9. No intent gap or new deferral. Owner evidence records
commands, source/log custody, preservation and scaffold/UI/context/docs/ADR decisions.

Native stop completed normally; data/resources retained. Scoped local commit only; no push.
