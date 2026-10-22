---
title: Qualify existing pre-grant Identity target dependency
type: chore
created: '2026-10-22'
status: done
route: dispatch
review_loop_iteration: 0
baseline_commit: 5dd7d1b6a8605c12552ac3c0cbace87bac84c421
context:
  - AGENTS.md
  - platform/docs/architecture/contracts/identity-access-execution-substrate.md
---

<frozen-after-approval reason="standing bounded shared prerequisite implementation approval">

## Intent

Qualify the existing identity.organization_account_target(uuid,bigint) dependency at
current Identity19/Access10 for later protected grant assignment. Its SQL, policies
and access_command_owner EXECUTE grant already exist; add current consuming proof,
not another migration or verification service.

## Boundaries & Constraints

Preserve all production sources, schema, roles, credentials, privileges, historical
migrations/references and existing user/setup semantics/callers. Probe from actual access_migrator with SET LOCAL ROLE
access_command_owner in short READ COMMITTED READ ONLY transactions. Assert original
and current roles; set transaction-local trusted setup org/service actor with absent
or empty account. Context is a trusted backend assertion, not authorization. Actual
Access grant authority/observation deadline/write coordination remain later command work.

Point returns account_id/membership_id/membership_revision/actor_id/display_name from
active org/profile/member and account-kind mapping. No grant/person/employment/admission
is needed. No latest-member fallback or caller-account switching. It checks those
Identity facts, not live Auth or Access capabilities. Keep valid user context supported.

Prepare synthetic mappings/members through actual identity_operator using existing
account_actor.ensure and membership.join/retire commands, with explicit owner fixture
authorities and root's protected existing secret. Derive target from the validated
fixture URL. Build unmapped cases without deleting protected mappings. Deliberate
profile/org fixture soft-deletions/restoration occur between read-only checks.

No grants, real-target/production/deploy/pilot, Leave/editor, new framework/dependency,
cleanup/reset/prune or push. Preserve concurrent work and historical resources/proof.

## I/O & Edge-Case Matrix

| Scenario | Required proof |
| --- | --- |
| Active mapped member, zero Access grants/admission | Exact five values; setup with absent/empty account; UUID spelling accepted |
| Wrong org/account/member, null/nil target, null/nonpositive/missing member | No row; typed invalid UUID/bigint refuses without fallback |
| Unmapped member, soft-deleted profile/org, retired membership | No row; restoring supported fixture reference rechecks current state |
| Supported retire then explicit rejoin | New ID/revision1 succeeds; old ID remains absent despite retained mapping/history |
| Missing/malformed/nil org/actor/context, setup with account; user missing account | No row; valid user context with separate caller account remains compatible |
| Point-only caller, actual Access runtime/operator | Command owner point allowed, list/raw tables denied; runtime/operator direct point/list denied; no role/ACL changes |
| Reused pool/connection and read side effects | LOCAL state clears; every read matrix leaves Identity/Access rows/catalogs/history/receipts/events unchanged |
| Source/log mutation, optimized Python, repeated --all, retained state | Safe pre-I/O refusal; fresh single-use aggregate and separate read-only retained inspection |

</frozen-after-approval>

## Code Map

Under services/access/tests, add qualify_identity_pregrant_target.py and
test_identity_pregrant_target.py. Reuse current configure/base four-group fixture loader,
engine/migrate/Access snapshot/safe failure reporting, existing identity_operator.execute
and account-ensure/join/retire envelopes. One clean CASES entry suffices; root bootstrap
imports it. Capture full Identity table state using a privileged synthetic observer so
RLS cannot hide effects, plus existing Identity19 catalog verification and Access10
snapshots. Bind all consumed helper/owner/bootstrap/auxiliary credential sources and
generated logs. No previous-source package is needed. Add only
services/access/IDENTITY-PREGRANT-TARGET.md runbook; root owns evidence/handoffs.

## Tasks & Acceptance

- [x] Add acceptance-first qualifier/tests for every matrix row without production edits.
- [x] Run fresh actual current-head proof and separate retained inspection; verify zero
grant activation, supported lifecycle commands and read-only behavior.
- [x] Complete independent reviews, affected regression/composers, requirement/five-impact
records, normal stop and scoped local commit while preserving concurrent work.

Given a mapped active member with no grant, when the existing private point check runs,
then exact current target evidence is available. Given retirement/rejoin, when the old
member ID is queried again, then it never substitutes the replacement. Successful
qualification establishes this dependency only; protected grant execution remains gated.

## Implementation Notes

No intent gap. Characterize existing behavior; harness RED is not a runtime defect.
Agent owns only new qualifier/test/runbook: no DB/Docker/commit/agents/workflow. Freeze
after focused RED/GREEN. Root owns fresh native bootstrap, protected existing
identity_operator/runtime fixture secrets, evidence/substrate/DEVELOPMENT/KDG handoffs,
final verification and commit. No production files may change. Snapshot
/tmp/pregrant-target-preservation.json pins52 historical and75 production sources;
preserve concurrent evolution. Standing approval covers this spec/dirty tree. Existing
bootstrap portability remains deferred. Existing qualification scaffold only; no UI,
context or ADR changes; TS7.0.2/dependencies unchanged.

## Spec Change Log

## Review Triage Log

| Finding | Verdict / route | Evidence |
| --- | --- | --- |
| Blind1 driver source | medium / patch | Documented root driver executes main but was outside source_snapshot; bind its bytes. |
| Blind2 bootstrap log mutation during execution | medium / patch | Original digests checked only before DB work; recheck before acceptance. |
| Blind3 global fixture-write delta | low / rejected | Helper intentionally verifies selected fixture reference; supported fixture writes produce audit rows. Full state is asserted around every read. Validating every setup-write audit delta would add a separate writer qualification without a demonstrated unintended mutation. |
| Blind4 individual LOCAL settings | medium / patch | No-row result can mask partial leakage; assert all four settings and role independently. |
| Blind5 pool checkout | medium / patch | A checked-out connection was reused, but no actual return/reborrow occurred; add that boundary. |
| Blind6 active revision2 | medium / patch | Active expected revisions were always1; add a controlled fixture timestamp update and exact2, retaining rejoin1 proof. |
| Blind7 sequence is_called | low / rejected | Reads run in asserted READ ONLY transactions, which prohibit nextval/setval. No sequence mutation path was demonstrated; adding sequence internals does not improve the bounded projection proof in everyday use. |
| Blind8 unsafe credential files | medium / patch | Existing protected reader is reused, but mode/symlink refusal lacks direct focused coverage. |
| Edge1 extra bootstrap log | medium / patch | Subset-only original log check accepts an extra pre-aggregate file; exact pre-DB inventory shares custody root cause with Blind2. |

Verification-gap lens found no findings. All findings were individually assessed before
grouping. Six patch groups (log findings combined), two low complexity-expanding proposals
rejected under the workflow's practical-use rule. No intent gap, production change, new
ADR or new deferred work. Same implementation agent re-engaged for bounded patches.

## Verification

Use existing actor-command-zxycfmc4/owner-env/venv/bin/python under deployment .local/
identity-baseline. Focused first, then full affected Access/PtS release/migrate-adapter
pytest with plugins/cache disabled; both composition dry runs. Root fresh --all then
--verify-retained, source/log/frozen/production/history audit and normal stop.

Root pre-review verification: seven native stages plus separate retained inspection
passed; 1453 affected tests passed in40.40s; both composition modes exited0. Matrix
audit maps every row to the executed methods in owner evidence. Independent review,
final retention/normal stop and scoped commit complete the remaining task.

Final reviewed verification:13 focused tests pass;1459 affected tests pass in46.68s;
eight native groups plus separate read-only retained inspection pass. All123 source
and3 generated-log bindings independently match. Both composition modes exit0; native
run stopped normally with data/resources retained. All52 protected historical and75
production sources remain unchanged. No new deferral; exact9-file local commit follows
final source/frozen/concurrent custody audit.
