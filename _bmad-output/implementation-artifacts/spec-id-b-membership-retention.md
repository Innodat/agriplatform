---
title: Retain membership history across destructive legacy paths
type: bugfix
created: '2026-10-20'
status: done
route: dispatch
review_loop_iteration: 0
baseline_commit: e124da80b9c0a3bbd3951d4ec1f248009502ac7d
context:
  - /home/ck/repos/innodat/agriplatform/AGENTS.md
  - /home/ck/repos/innodat/agriplatform/platform/docs/architecture/contracts/identity-access-execution-substrate.md
---

<frozen-after-approval reason="standing bounded shared implementation approval">

## Intent

Preserve retained membership instances and their cascading legacy role evidence through
existing direct/profile/organization deletion paths. Accepted E1 requires non-cascading
membership references and no hard deletion of retained instances. Deliver this structural
prerequisite through the existing Identity owner before lifecycle/rejoin commands.

## Boundaries & Constraints

Add identity_0012 after11. Replace ON DELETE CASCADE with RESTRICT on existing
org_member.org_id→org.id, org_member.user_id→users.id and member_role.member_id→org_member.id
FKs, preserving names/columns/update action/validation/deferrability and data. Verify exact
prior names/definitions against canonical11 before changing them; no broad constraint
rewrite or target normalization. Keep all other FKs, including profile→Auth, unchanged.

Extend existing guard_org_member_revision() with an initial TG_OP DELETE/TRUNCATE refusal:
23514, identity_membership_history_retained, org_member_history_retained. Extend existing
row trigger to DELETE and add one BEFORE TRUNCATE statement trigger using the same
function, closing the real legacy service_role TRUNCATE CASCADE bypass. Preserve existing
function owner/signature/invoker/ACL/search_path and all binding/revision behavior. Both
active/retired and roleless memberships are retained; blocked statements leave complete
rows/roles/audit/history unchanged. Owner DDL/trigger disabling is trusted administration,
not protected by this guard. No new function, privilege, login, credential or framework.

Preserve ordinary inserts/mutable updates, seed upsert/unretirement, current readers and
standalone trusted legacy member_role DML. Do not claim full role-audit or lifecycle safety.
Uniqueness/one-way retirement/rejoin/owner commands/actor attribution/adoption and Access/
WRITE/server KDG remain gated. Do not implement Leave/editor or real accounts/provider/
access, production migrations/provision/deploy/pilot, reset/prune or push. Preserve every
historical source/reference/pin, all concurrent work and prior failed data/resources.
Approved dependencies including TypeScript7.0.2 remain unchanged.

Extend existing baseline/head/rollback recorder with membership-retention-reference.json
and independent pin. Execute captured source, verify every prior catalog and staged-role
rollback, SQL deadlines/source custody/exclusive0600 publication/no auto-pin/optimized
Python refusal. Root alone executes sequential isolated DB/Docker work. Root prepares
fixtures; characterization/read/delete mutations rollback, including TRUNCATE. Migration
setup is explicit; no sequence-counter rollback promise. Exact temporary role/object
restoration uses existing private durable witnesses. Direct SQL is not HTTP/provider/JWT
verification or live-target adoption.

## I/O & Edge-Case Matrix

| Scenario | Expected |
| --- | --- |
| Actual unchanged11 direct member/org/profile DELETE and membership TRUNCATE CASCADE | Record real membership/role loss inside rollback-only synthetic transactions |
| New12 member DELETE/TRUNCATE, active/retired/roleless/multirow | Stable retention error, entire statement rolls back and all dependent evidence survives |
| New12 parent org/profile deletion and original Auth FK |23503 refusal under correct RESTRICT FK; Auth FK stays as actual baseline, no invented old Auth cascade |
| Supported inserts/updates/seed and current role/token/account readers | Existing binding/revision/roles and deletion filters stay; ordinary runtime/browser direct writes denied |
| Clean/adopt/exact11/repeat/drift/unknown/injected partial DDL failure | Verified12 or atomic refusal retaining prior source/rows/ACL/history/constraints/triggers |

</frozen-after-approval>

## Code Map

Original source20250815210000 creates three cascade FKs with automatic names
org_member_org_id_fkey,org_member_user_id_fkey,member_role_member_id_fkey. Source
20250815110000 profile Auth FK defaults NO ACTION, not CASCADE. Confirm catalog in scratch
old11. Existing0011 guard and0004 row trigger are immutable historical source. New12
replaces function/row trigger and adds statement trigger; no actor/projection body changes.

Reuse identity_baseline.py and qualify_identity_baseline.py recorder, qualify_membership_binding.py
source-bound witness/prior evidence/function-delta/row prechecks, ProfileQualification
bounded SQL/SET-only authenticated/service_role recovery. PREVIOUS_FILES is exact25 old
owner py/json files from full baseline Git tree. Root frame is /tmp/kdg-member-retention-proof.
Root supplies member-retention-fixtures.json, characterization/clean rows with the same
account/other/spare/org/other_org/spare_org and member/other_member/other_org_member/role/
deleted_role keys as binding qualifier. Spare profile/org have no members. Parent has
already rendered Build; implementation child runs CPU tests only, never DB/Docker.
Root owns new recorder/pin/actual/evidence/navigation/reviews; child owner runbook/code/tests.

## Tasks & Acceptance

- [x] Add versions/0012_membership_retention.py, baseline/head/reference recorder and
focused test_membership_retention.py; missing12/head ATDD RED before production SQL.
- [x] Add qualify_membership_retention.py using existing cases characterization,
membership_retention_reference,clean,legacy,previous,failure,unsafe,unknown,native. Characterize
actual11 through restricted login/service role. Prove exact FK definitions and only intended
catalog/function/trigger changes; destructive active/retired/roleless/parent/TRUNCATE/multirow
refusals, data/audit/roles, seed/mutable/read compatibility. Inject actual failure after first
FK replacement to prove atomic DDL rollback. Unknown uses rollback-only same-connection
preflight. Root alone prepares25-file prior execution and fresh synthetic targets.
- [x] Update owner IDENTITY-MIGRATIONS.md; root evidence/inventory/KDG navigation, five
impacts, full affected suite/both composers, three reviews, protected-source/private-output
audit, normal retained-data stop and scoped local commit. No broader readiness claim.

Given retained membership, when supported direct deletion/truncation or parent deletion
is attempted, then the entire write refuses and retained membership/role evidence stays.
Given failed upgrade, then old catalog/history/data stay and activation blocks. Given
ordinary seed/read/update paths, then their supported behavior remains.

## Implementation Notes

No intent gap: accepted E1 explicitly selects retention/RESTRICT. Only authorized synthetic
DDL/data verification runs; no real-target irreversible effect. Footprint is one owner
migration/reference, existing baseline/recorder, qualifier/tests and documentation.
Standing approval covers bounded implementation and existing dirty concurrent documents.

## Spec Change Log

Actual11 source-fact correction: service_role has SELECT/INSERT/UPDATE/DELETE only,
not TRUNCATE. Existing supabase_auth_admin has ALL on org/member/role. Initial
characterization correctly refused42501 on the fourth path and restored its exact role
edges; no mutation escaped. Keep service-role TRUNCATE denial and test truncation under
the existing Auth admin role through a separately recorded owner-prepared rollback lane.
No runtime privilege, production SQL, accepted intent or policy changes. The frozen
plan's service-role TRUNCATE assumption is historical and disproved by this actual check;
final evidence uses actual privileges. Function/trigger/FK retention scope stays.

## Review Triage Log

| Finding | Verdict | Evidence and route |
| --- | --- | --- |
| Blind1 reproducible evidence | low | Evidence lacks exact commands/interpreter and durable receipt references; direct documentation completion patch. |
| Blind2 pending verification prose | low | Evidence/navigation still describe pending checks after initial PASS; direct documentation completion patch, finalized after reviewed verification. |
| Blind3 previous consumer compatibility | medium | Exact catalog compatibility and SQL helper proofs exist, but previous consumer source/caller disposition is not yet recorded. Patch evidence with baseline-bound known consumer inventory and limits; real-target activation remains gated under ADR-0020. |
| Blind4 parent-delete/insert concurrency | low | New behavior uses native RESTRICT FKs rather than a check-then-act path; direct parent refusals are verified. Extra two-connection permutations would add test machinery for standard RI without a demonstrated race in an application caller; reject under low-finding complexity rule. |
| Blind5 lock contention | medium | Three ALTER TABLE replacements acquire exclusive locks; current qualifier has no conflicting reader and cannot substantiate bounded migration refusal in that case. Patch existing synthetic failure case under existing timeout. |
| Blind6 late DDL rollback | medium | Current event fixture aborts after first FK, leaving replacement function and triggers unexercised on failure. Patch one private late-phase injection using same rollback/state comparison. |
| Blind7 actual FK drift | medium | Canonical catalog comparisons exist, but actual drift fixture changes only profile ACL. Patch rollback-only old11 FK drift/preflight proof without normalization. |
| Blind8 TRUNCATE forms | medium | Current matrix only uses single-target CASCADE; explicit multi-target/RESTART forms are not recorded. Patch existing rollback lanes, retaining Auth-role versus owner sequence-authority distinctions. |
| Blind9 fixture role identity | medium | Numeric validation does not require role/deleted_role distinct and inherited row checks do not establish both intended role rows; patch private fixture validation and precheck. |
| Blind10 native unused | false | Native is the inherited private protocol's existing-cluster/admin URL custody anchor; bootstrap creates eight scratch cases and no native database. Removing it breaks fixture URL/run validation; executing owner migrations against preserved native data is unnecessary and outside isolated proof. |

Edge-case review returned no findings. Verification-gap review returned no gaps. Each blind finding was assessed separately before grouping. Survivors route to private-verification/documentation patches, with no public surface or production migration changes and no deferrals.

## Verification

Frozen OWNER_PYTHON=platform/deployment/.local/identity-baseline/actor-command-zxycfmc4/owner-env/venv/bin/python.
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 "$OWNER_PYTHON" -I -B -m pytest services/access/tests
apps/pts/tests/test_release.py -q -p no:cacheprovider. Both composer --check-only routes.
Source-bound actual matrix,25 historical files, requirement/matrix audit, review layers,
protected source/private outputs and normal stop retaining all data; no root npm claim.


Initial verification: missing12/head ATDD RED before production SQL;118 focused retention/
binding tests pass after source-privilege fixture correction. Actual11 four destructive
paths characterized and rolled back, existing service/profile TRUNCATE denials preserved.
Reference recorder PASS, new12 pin6476b2210402434fd4fa732a7ab882dc8ca02cdbc694c94955647f43d696cf81.
Full actual matrix PASS23.657s source unchanged; all intended FK/function/trigger deltas,
restricted DELETE/Auth-role TRUNCATE refusals, mutable/seed/reader and atomic migration
proof pass. Both composers exit0; regression/review/preservation/normal stop remain.


Reviewed patch verification:66 focused retention tests PASS before root execution.
Fresh frame platform/deployment/.local/identity-baseline/member-retention-reviewed-5vf899h9/
uses eight new scratch cases and exact25-file old11 execution; unchanged11 characterization
PASS. Actual reviewed matrix PASS42.081s, source unchanged, conflicting lock refusal7.794s
within25s, early/late DDL rollback/recovery, FK drift and explicit truncation forms PASS.
All715 affected tests PASS30.33s, no skips. Both composers exit0. Three review layers
complete; eight blind findings patched, one low-complexity expansion rejected and one
claim false; no deferrals. Reproducible commands, receipts, previous consumer compatibility
limits and five impacts are recorded in services/access/MEMBERSHIP_RETENTION_EVIDENCE.md.
Historical24 files other than the mutable baseline runner are byte-identical; canonical
new12 pin unchanged. Final custody audit and normal retained-data stop recorded below.

Final custody:2647 protected paths checked, no missing/unexpected changes; seven intended
existing paths changed and concurrent original work retained. Executed source matches
current source. Normal wrapper stop completed for99b7231c-0a5b-4bdb-98e8-3329564c526a
with all data/resources retained; native-stop.json records runtime_ready=false.
