---
title: Private organization check-reader Identity bridge
type: feature
created: '2026-10-22'
status: done
route: dispatch
review_loop_iteration: 0
baseline_commit: 7afa7f773789e7529c4891d09e5bb59797c84b13
context:
  - AGENTS.md
  - platform/docs/architecture/contracts/identity-access-execution-substrate.md
---

<frozen-after-approval reason="standing bounded prerequisite implementation approval and next instruction">

## Intent

Prepare the missing private Access check-reader role and Identity-owned permission
bridge needed before membership-safe organization checks. Deliver only this dependency;
effective Access SQL/HTTP checks and consumer activation follow separately.

## Boundaries & Constraints

Use existing true-admin SQL preparation and controlled Identity20 after immutable19.
Prepare access_check_reader NOLOGIN/NOINHERIT/NOSUPERUSER/NOCREATEDB/NOCREATEROLE/
NOREPLICATION/NOBYPASSRLS, without memberships or existing dependencies. Refuse existing
role names without repair. User-approved amendment: Identity20 first restricts execution
on six existing callable routines, preserving exact supported callers, then grants
Identity schema USAGE and EXECUTE on
identity.current_account_organization(). Use the existing projection owner's SET-only
migration edge for grants on its function; do not broaden migrator authority. Do not grant
current_account_actor(), target projections, owner-role assumption or raw reads/writes.

Keep current projection definition, nullable internal actor, trusted user/account/org
context and forced RLS unchanged. Preserve Identity19 and all older migration/reference
bytes, Access14 data/clients and concurrent work. Schemas stay unchanged, including
existing public.get_user_roles. Access exact foreign-function recognition must accept
the verified new Identity ACLs without admitting drift. Preserve bodies/owners/policies.
Only callable legacy ACLs and approved bridge privileges change. Check actual effective
privileges including PUBLIC, role flags/memberships, dependencies and ledger exclusion;
unknown/drift state refuses before mutation, repeat preserves exact populated state.

No Access migration/wrapper/HTTP activation, app grant, target/discovery policy, account
reader, generic generator/framework or dependency change. TypeScript7.0.2 baseline stays.
Synthetic local/CI only; no production/real accounts/access, provision/deploy/pilot,
Leave/editor, reset/prune/resource deletion, credential changes or push.

## I/O & Edge-Case Matrix

| Scenario | Required result |
| --- | --- |
| Correct empty prepared role and exact Identity19 | Controlled20 grants exact schema/routine access; business/history unchanged |
| Missing/unsafe/nonempty role or ACL/catalog drift | Refuse transactionally, no normalization or applied20 |
| User account/org context, current member | Same exact projection result, nullable actor remains internal evidence |
| Missing/malformed/setup/wrong account/org or retired/deleted target | Same fail-closed projection behavior |
| Raw tables/ledger, other projections, writes or role escalation | Denied with actual restricted role; no new runtime authority |
| Hook/role lookup/profile policies/ensure/join/retire/Access14 commands | Existing authorized callers work; new reader cannot invoke sensitive helpers |
| Upgrade/repeat/failure/forward retry | Preserve data/Access14 and prior grants, bounded rollback, explicit controlled retry |


Approved six-routine non-owner execution recipients:
- custom_access_token_hook(jsonb): supabase_auth_admin.
- public.get_user_roles(): authenticated.
- create_user(text): none.
- authorize(identity.app_permission): authenticated, service_role, postgres,
  identity_account_projection_owner, identity_target_projection_owner,
  identity_account_verification_owner, identity_command_owner.
- membership_join_profile_allowed(uuid), membership_join_org_allowed(uuid): identity_command_owner.
Use existing authority-owner SET edge for effective REVOKE on the last two. Keep pure
current_org_id/current_member_id and trigger-only routines; verify exact known definitions
and classify reachability accurately. No blanket default-ACL/schema-wide change.

</frozen-after-approval>

## Code Map

Restore/extend /tmp/check-reader-bridge-blocked-candidate using the approved SQL/rationale
/tmp/check-reader-public-execute-proposal.sql and .md. Identity0020/baseline owns ACL,
head/history/role/catalog/reference changes. Access baseline's exact foreign-routine
verification must recognize verified20 ACLs while retaining19. Historical sources/pins stay.
Reuse tools/prepare_identity_target_roles.sql for empty-role preparation. New tests and
qualify_check_reader_bridge.py use existing grant-assign/Identity owner helpers; never
copy old direct member inserts or add an export/bypass CLI. Schemas/bodies stay unchanged.

Root owns native execution, independent rollback-only reference rehearsal/pinning,
CHECK_READER_BRIDGE_EVIDENCE.md, mutable handoffs, full checks/reviews/stop/commit. Agent
owns code/tests/runbook. Wait for root inherited-hook RED signal before production edits.
Native fixture is Access-style with cases reference/bridge, private runtime/Identity
operator credentials, fresh Identity19 and empty Access schemas; use supported owner
commands to populate. No private .local search/output; selected safe diagnostics only.
Expose check_reader_bridge_catalog_snapshot and trusted reference APIs for root pinning.

## Tasks & Acceptance

- [x] tools/prepare_access_check_reader.sql, Identity0020/baseline and Access verifier:
exact ACL prerequisite/bridge with transactional pre/postconditions and historical paths.
- [x] test_check_reader_bridge.py/qualify_check_reader_bridge.py: focused TDD, actual
restricted-role matrix, compatible Auth/Expense/projection/operator/Access14 callers,
rollback/repeat/drift/context/retained proof and exact source/log/state custody.
- [x] CHECK-READER-BRIDGE.md and root evidence/handoffs: controlled order/recovery,
requirement-to-test mapping, five impacts, full verification/review and local commit.

Given exact19, when controlled20 succeeds, only approved ACLs/history change. Given
unauthorized context/operation, deny without effects. Given drift/failure, refuse with
complete rollback; explicit controlled retry preserves data and prior supported clients.

## Implementation Notes

User approved amended scope and continuing dirty tree. No intent gap. Route dispatch;
synthetic only. Baseline snapshot /tmp/access-check-reader-preservation.json. Root frame
platform/deployment/.local/identity-baseline/check-reader-bridge-approved-20261022.
Independent reference case rehearsal rolls back; root pins trusted20 before controlled
bridge qualification. No manual ledger stamping. Scaffold extends owner tooling; no
shared UI/context/ADR changes. Owner documentation/handoffs updated. Private-bootstrap
portability remains an existing limit. Preserve previous candidate and failed frames.

## Spec Change Log

2026-10-22: user approved the six-function ACL prerequisite after confirming schemas
stay unchanged. Frozen scope amended accordingly; retain historical sources, bounded
bridge and no activation. Previous failed candidate/frame remain preserved.

## Review Triage Log

All three layers returned before triage; edge and verification-gap reported none.

| Finding | Verdict and evidence | Route |
| --- | --- | --- |
| Blind1: arbitrary failure satisfies refusal | medium: identity() only checks nonzero, so unrelated safe failures could pass. Assert known identifier for each case. | patch |
| Blind2: forged admin claim shape | medium: user_role does not exercise authorize() user_roles array. Correct negative fixture. | patch |
| Blind3: current point-target denial absent | medium: older organization_target is covered but organization_account_target is omitted. Add direct denial. | patch |
| Blind4: policy dependency omitted | medium: new role inherits query limited to a/o; r dependencies outside Identity are not inventoried. Extend only reader query and prove rejection. | patch |
| Blind5: other-database dependencies | false: inherited query explicitly documents independent per-database owner histories; fresh CREATE ROLE is globally empty, subsequent per-database bridge preparation intentionally coexists across isolated namespaces. Another database's ACL does not confer current-database rights. Clarify runbook scope directly. | reject |
| Blind6: service_role caller absent | medium: ACL is pinned but actual preserved caller probe omits service_role. Add direct authorize call with existing claim shapes. | patch |
| Blind7: six previous commands only replay | false: this deliberately proves previous receipt compatibility; fresh revoke, new join and ensure execute post20. ACL changes affect Identity helper callers, directly exercised by authorization/profile/point/ensure/join/retire probes, not unchanged bodies of all Access commands. No observed broken new command path. | reject |
| Blind8: future timeout waits for worker | medium: context manager waits up to90s before releasing lock despite30s future timeout. Set shorter child deadline and assert elapsed bound for lock probes. | patch |
| Blind9: remaining unsafe flags untested | medium: exact flag tuple rejects them but focused suite does not independently mutate those inputs. Add parameterized verifier checks. | patch |
| Blind10: closure records pending | low: review ran before closure; finish evidence/task/checkpoint records as part of root closure. | patch |

## Verification

Prepared Python: platform/deployment/.local/identity-baseline/actor-command-zxycfmc4/owner-env/venv/bin/python.
Focused tests first; native reference rehearsal then independent controlled19→20/repeat/
rollback/privilege/context matrix and separate retained read-only check. Affected Access
suite plus PtS release and migrate-adapter tests; both composition modes. Record all
commands and results, sources/logs/state custody, preserve older frames, normally stop
run99b7231c-0a5b-4bdb-98e8-3329564c526a via existing lifecycle. No portable CI claim.


Verification closure:69 focused and1745 affected tests PASS; both composition modes
exit0. Independent reviewed reference rehearsal,11 final native stages, separate
read-only retained check and root source/log/state audit PASS. Three review lenses
complete; all findings triaged, narrow patches verified, none deferred. Normal local
stop exit0 preserves data/resources. Final proof and exact receipts/commands are in
services/access/CHECK_READER_BRIDGE_EVIDENCE.md. No consumer activation is claimed.
