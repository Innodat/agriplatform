---
title: Preserve the identity of existing membership instances
type: bugfix
created: '2026-10-20'
status: done
route: dispatch
review_loop_iteration: 0
baseline_commit: e8754cc9e53fc57cbc6b45d96725b5bc267b204a
context:
  - /home/ck/repos/innodat/agriplatform/AGENTS.md
  - /home/ck/repos/innodat/agriplatform/platform/docs/architecture/contracts/identity-access-execution-substrate.md
---

<frozen-after-approval reason="standing bounded shared implementation approval">

## Intent

Prevent an existing membership instance being repurposed by changing its id, org_id or
user_id. Exact membership grants/readers require a stable account/organization binding.
Implement this accepted E1 structural invariant through the existing Identity revision
guard before dependent lifecycle commands. No new authorization rule is invented.

## Boundaries & Constraints

Add identity_0011 after10. Replace only identity.guard_org_member_revision() body through
CREATE OR REPLACE, preserving owner, signature, invoker security, ACL, search_path and
existing trigger. Before any UPDATE revision logic, reject IS DISTINCT FROM changes to
id/org_id/user_id with SQLSTATE23514, stable message identity_membership_binding_immutable
and constraint org_member_binding_immutable. Identical assignments remain valid no-ops;
INSERT retains caller-supplied existing ID behavior and server revision1. Preserve existing
revision ownership/increment/no-op/overflow and multirow atomicity, audit hooks and other
mutable fields. No migration rewrites existing rows or locks/external IO in trigger.

Ten historical revisions/references/source pins, source SQL and composed outputs remain
immutable. Extend existing owner baseline/head and rollback-only recorder with independent
membership-binding-reference.json/pin. Execute captured source, verify every previous
catalog, staged-role rollback and source custody, bounded SQL, exclusive0600 publication,
no auto-pin and optimized-Python refusal. No new recorder/generator/service/framework.

Membership uniqueness, retirement/unretirement, hard deletes/CASCADEs, rejoin commands,
seed payload/upsert contracts and actor fields remain unchanged and gated. Characterize
existing supported seed ON CONFLICT and retained SQL-seed lookup; demonstrate they remain
compatible with this binding-only guard. Do not silently make a retired seed active-only
or pretend this completes lifecycle safety. Existing role/current-account/token consumers
and actor mappings remain intact. No app API or error contract changes here.

Root alone executes sequential isolated DB/Docker work with private durable witnesses and
exact temporary authenticated/service_role SET-only edge restoration. All fixture mutations
rollback. Real accounts/provider/access/production/provision/deploy/pilot/reset/prune,
Leave/editor and push are excluded. Preserve concurrent work, prior failures/data/resources.
Approved dependencies including TypeScript7.0.2 unchanged.

## I/O & Edge-Case Matrix

| Scenario | Expected |
| --- | --- |
| Unchanged10 valid-FK id/org/account reassignment | Record actual accepted mutation/revision before11 using rollback-only fixtures |
| Existing member changes any binding field, active or retired, combined with allowed update |23514 and exact original row/revision/roles/audit; no partial multirow update |
| No-op binding assignments; ordinary owner/attribution/retirement updates; INSERT | Existing behavior and server revision semantics, overflow atomic refusal retained |
| Legacy seed upsert/SQL-seed reference, restricted login/read consumers | Same IDs/roles and supported mutable behavior; ordinary browser/runtime direct writes denied |
| Clean/adopt/exact10/repeat/drift/unknown/injected revision failure | Verified11 or atomic refusal preserving original data/history, ACL/function definitions |

</frozen-after-approval>

## Code Map

Existing services/access/identity-migrations/versions/0004_current_account_organization.py
owns guard_org_member_revision and trigger; no binding guard exists. Its original SQL
and reference must stay. Original identity.org_member has unconditional unique(org,user),
profile/org FKs and cascades. scripts/seed.py seed_org_member uses conflict(org,user)
upsert is_owner/deleted_at; platform/supabase/seeds/001_identity.sql selects member for
admin role. Characterize actual10 then protect binding without altering these paths.

Use identity_baseline.py, qualify_identity_baseline.py recorder and token-hook11 predecessor
pattern (currently10). Reuse qualify_token_hook.py compatibility function-row technique,
qualify_profile_fields.ProfileQualification SQL/fixture helpers and existing prior-evidence
protocol. New qualifier overrides hook paths with binding cases. PREVIOUS_FILES is exact23
old owner py/json files from baseline Git tree, not a filesystem glob. Root frame path is
read from /tmp/kdg-member-binding-proof. Root supplies private DBs and member-binding-fixtures.json
with characterization/clean, each account/other/spare/org/other_org/spare_org UUIDs and
member/other_member/other_org_member/role/deleted_role decimal strings; spare account/org
exist with no membership so old binding changes avoid FK/unique errors. Source11 pin stays
None until root recorder PASS. No DB execution by implementation child.
Original member_role FK prevents changing a referenced member ID; characterize id change
on a roleless row or rollback-only removal of synthetic dependent roles, without disabling
constraints. New guard must reject id changes even before existing FK checks.

## Tasks & Acceptance

- [x] Add versions/0011_membership_binding.py, head/reference/recorder and focused
test_membership_binding.py. Observe missing11/head ATDD RED before production SQL; focused
TDD protects previous custody chain and binding/revision contract.
- [x] Add qualify_membership_binding.py with existing IDENTITY_QUALIFICATION_DIR cases
characterization,membership_binding_reference,clean,legacy,previous,failure,unsafe,unknown,native.
Root builds exact old10 fixtures. Prove old mutations, actual restricted service-role
DML/denied browser/runtime writes, three binding fields/noop/retired/mixed/multirow cases,
unchanged row/audit hashes on refusal, revision/overflow/seed compatibility, exact only-guard
function delta, migration/adopt/data/ACL/history/rollback/refusal and signal cleanup.
- [x] Update owner IDENTITY-MIGRATIONS.md; root evidence/navigation/inventory and five
impacts, affected suite/both composers, three independent reviews, preservation audit,
normal retained-data stop and scoped local commit. No full ID-B/readiness claim.

Given a retained membership ID, when direct writes change its account/organization/id,
then the owner database rejects the entire statement without changing rows/evidence.
Given a supported mutable/noop/seed write, when binding is unchanged, then its previous
revision and role behavior stays. Given a failed upgrade, then previous data/history stay.

## Implementation Notes

No unresolved intent gap: immutable binding is explicit in accepted E1. Footprint is one
replacement guard migration/reference, existing owner baseline/recorder, focused test/
qualifier and documentation. Only isolated synthetic migrations execute, no real-target
irreversible effect. Standing approval covers bounded scope and current dirty concurrent
documents. Parent has rendered/read Build; child does not invoke another workflow.

## Spec Change Log

## Review Triage Log

All three context-free layers launched before triage. Host thread capacity permits one
reviewer at a time. Blind10 findings, Edge1, Verification0; no layer skipped.

| Finding | Verdict / route | Evidence |
| --- | --- | --- |
| B1 duplicate/missing member fixture can collapse multirow case | medium / patch | Shape validation allows repeated member IDs and does not inspect rows. Validate distinct IDs and actual expected account/org bindings before execution. |
| B2 permitted row may execute after rejected row | medium / patch | Existing unordered UPDATE may fail on first row. Add a data-dependent modifying CTE whose permitted update must return before rejected update; no instrumentation framework required. |
| B3 derived id lacks headroom/collision check | low / patch | Fixture allows max bigint then adds1000000; reserve headroom and verify derived ID unused, avoiding unrelated PK/range errors. |
| B4 combined binding changes absent | medium / patch | Individual fields and is_owner mixtures are covered; add two/all-field reassignments to the same rollback-only refusal loop. |
| B5 null binding changes absent | medium / patch | Add each NULL assignment to prove stable binding error before NOT NULL/FK checks. |
| B6 overflow asserts through owner fixture | low / reject expansion | Existing overflow branch is unchanged and has no caller/authorization dependence. Owner-only rollback DDL is explicitly documented and needed to create otherwise unreachable max revision. Restricted service-role paths prove other write semantics. Moving max setup across connections would add privileged committed-fixture/recovery machinery solely for this uncommon verification variant; no restricted-overflow claim is made. |
| B7 post-refusal/retired reader integration limited | medium / patch | Existing read checks run after refusals and confirm original active binding. Add explicit retired member reader denials to the same bounded fixture, preserving remaining lifecycle behavior. |
| B8 concurrent migration/writer test absent | low / reject expansion | This isolated delivery proves controlled migration-before-activation, atomic rollback and unchanged supported mutable writers; it does not claim hot live cutover or cancellation of preexisting privileged binding writes. Real activation remains separately gated under ADR0020. A new concurrency/release fixture exceeds the practical current proof without an identified changed caller defect. |
| B9 latest witness not bound to current inputs | medium / patch | Prior function hash binds schema only. Bind witness to current proof/run/fixture digest and assert actual three recorded transitions before accepting it. |
| B10 provisional regression/review docs | low / patch at completion | Reviews were intentionally still running at diff capture. Finalize exact632 initial regression result and final reviewed-source results/dispositions before commit. |
| E1 same missing/duplicate member precondition | medium / patch, grouped B1 | Same absent fixture-integrity check permits one-row evidence; retains independent verdict, shares B1 correction. |

Eight direct correction groups (one root documentation completion), two low verification
expansions rejected; no SQL, public surface, architectural/intent change or deferral.
Same implementation agent patches tests/qualifier; root reruns full reviewed-source
verification and preserves every initial receipt/frame.

## Verification

Frozen OWNER_PYTHON=platform/deployment/.local/identity-baseline/actor-command-zxycfmc4/owner-env/venv/bin/python.
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 "$OWNER_PYTHON" -I -B -m pytest services/access/tests
apps/pts/tests/test_release.py -q -p no:cacheprovider. Both composer --check-only routes.
Source-bound actual fixture/recorder, exact historical23 files, matrix audit, reviews,
preservation/private-output receipts, normal stop retaining all data; no root npm checks.


Initial proof: missing11/head ATDD RED before SQL;55 new focused tests pass. Actual
unchanged10 all three valid-FK reassignments accepted and rolled back; restricted-login
characterization PASS. Reference recorder PASS, new11 pin43bf6d868efb7234ebd8199d884f7cafcca018a2fd274df6329187381a6827f3.
Complete actual matrix PASS25.681s source unchanged; both composers exit0. Initial root
ledger privilege refusal before mutation retained; no grants added. Unknown-history
case uses same-connection rollback-only actual owner preflight. Ordinary migration
setup and seed sequence consumption remain explicit as in existing harness; mutation
read/characterization fixtures roll back. Final reviews/regression/custody remain.


Final reviewed-source actual matrix PASS29.541s source unchanged in
platform/deployment/.local/identity-baseline/member-binding-reviewed-zpge73fv/;19 recorded
stages include fresh input-bound unchanged10 characterization and all expanded refusal/
reader/migration cases. All649 affected tests PASS29.76s, no skips; both composers and
whitespace check PASS. Eight correction groups verified, two low extensions rejected,
none deferred. New11 SQL/reference/pin unchanged. Exact source/function/ACL/data and
temporary-edge custody pass; all five impacts recorded. Normal retained-data stop and
preservation/private-output/final-source receipts complete the bounded delivery.2641
protected originals remain, seven intended existing changes, original concurrent work
preserved and zero unexpected changes. No full Identity/Access/WRITE/server KDG readiness
or live/provider/HTTP/JWT-signature/production approval is claimed.
