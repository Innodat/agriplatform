---
title: Restricted selected-organization Identity target projections
type: feature
created: '2026-10-20'
status: done
route: dispatch
review_loop_iteration: 0
baseline_commit: 48b95c9bfc8a199a84d3746c431312439b1a93e9
context:
  - /home/ck/repos/innodat/agriplatform/AGENTS.md
  - /home/ck/repos/innodat/agriplatform/platform/docs/architecture/contracts/identity-access-execution-substrate.md
---

<frozen-after-approval reason="standing bounded shared implementation approval">

## Intent

Implement the two selected-organization Identity target reads needed by Access, through
the existing Identity owner/migration chain. This delivers internal reads, not Access
eligibility, public pagination, grants or account provisioning. Preserve all concurrent
work, old SQL/references/pins, receipts/state/resources and approved dependency baseline.

## Boundaries & Constraints

Add revision identity_0007 after0006, with exact signatures/columns from the substrate:
organization_account_candidates(after_account_id uuid) returns account_id UUID,
membership_id bigint, membership_revision bigint, actor_id UUID, display_name text;
organization_account_target(target_account_id uuid, expected_membership_id bigint) same.
Only active selected org/profile/member and mapped account-kind actors qualify. UUID
keyset after is exclusive; NULL starts; no raw-candidate LIMIT. Point requires positive
exact membership ID, never latest/replacement. No role/email/person/extra profile data.
Missing/malformed/nil context or input yields no rows without unsafe casts or disclosure.

Use fixed STABLE SECURITY DEFINER, pg_catalog,pg_temp search_path, qualified objects,
restricted identity_target_projection_owner NOLOGIN with exact column reads. Add
permissive+restrictive selected-org policies to profile/org/member so old PUBLIC
policies cannot broaden reads; avoid profile/member recursion. No schema CREATE or
raw table reads for runtime. Existing current-account functions/semantics stay intact.
User context requires valid nonnil account/actor/org; setup requires actor/org and absent
account. Candidates accept user only; point accepts user/setup. These are trusted Access
backend assertions; authorization remains the owning Access wrapper's responsibility.
Only access_target_reader receives candidates; point also access_setup_target_reader
and access_command_owner. No ordinary access_runtime/operator/browser grant. Revoke
PUBLIC and all inherited/named defaults transactionally before exact grants.

Controlled role preparation stages those four restricted NOLOGIN roles (SET-only
membership to migrator for Identity definer only), no silent repair. Existing roles
must be verified. Root alone performs isolated synthetic role/DB/secret setup. No live
account/access/provider changes, production migration/provision/deploy/pilot, Leave,
questionnaire editor, new generator/service/dependency or generic verification framework.

Extend existing canonical baseline and existing reference recorder for new independent
rollback-only head7 reference; never modify six prior revisions/references/source pins
or accept arbitrary target/reference overrides. Verify prior heads including exactly
validated empty staged-role normalization, current effective privileges/role dependencies,
new reference/source hashes, clean/adopt/head6 upgrade/no-op and migration rollback.
Access public wrappers/filtered pagination and full ID-B remain gated.

## I/O & Edge-Case Matrix

| Scenario | Expected |
| --- | --- |
| Selected org with mapped active members; cursor/point | Ordered complete candidates; exact member/revision/account actor only |
| Wrong/deleted org/profile/member, unmapped actor, wrong member/invalid UUID | Empty; no substitute or cross-org rows |
| Setup/mixed/missing context, nil/cursor/point boundary | Setup point only; invalid/mixed/list refused empty |
| Ordinary/runtime/browser/default privilege or role assumption | Denied; exact definer/caller rights and no raw table exposure |
| Reused connection, SQL failure, search-path spoof, membership changes | No context leakage; fresh exact current rows/revision |
| Clean/adopt/head6 upgrade/repeat/drift/failure | Verified head7 or safe refusal/atomic rollback; old rows preserved |

</frozen-after-approval>

## Code Map

services/access/identity-migrations/identity_baseline.py owns canonical catalogs/history;
versions0003/0004 and tools/prepare_identity_projection_role.sql are existing patterns.
services/access/tests/qualify_identity_baseline.py owns exclusive reference recording;
qualify_current_account_organization.py supplies fixture/read/reuse/upgrade patterns.
Original parser/adapter/CLI need no change. No frontend/generator/client promotion yet.

## Tasks & Acceptance

- [x] Add versions/0007_organization_targets.py, extend identity_baseline.py and existing
reference recorder; add tools/prepare_identity_target_roles.sql, focused tests.
- [x] Add tests/qualify_organization_targets.py consuming explicit root private fixture,
with actual restricted LOGIN read/denial/context/currentness/ACL and migration matrix.
No resource/role/credential provisioning inside qualifier. Any synthetic temporary
fixed-function invocation grants must restore exact ACL bytes and be identified as
fixture-only; they do not deliver Access wrappers. Observe ATDD RED first.
- [x] Update IDENTITY-MIGRATIONS.md, root evidence/navigation/inventory, five impacts;
root executes fresh source-bound synthetic proof, affected regression/both composers,
three reviews, preservation, normal stop retaining data and scoped local commit.

Given prepared synthetic owner/runtime roles, when migrated and read, then only exact
selected-org candidates/member bindings return. Given denied context/role or stale
binding, when read, then no disclosure. Given migration failure/drift, when attempted,
then activation refuses and all prior data/history/evidence remains.

## Implementation Notes

ATDD CPU missing TARGET_REVISION and actual restricted-login missing function42883
precede implementation. Root stages only four synthetic NOLOGIN roles, source-bound
previous15-file head6 rehearsals, and independent rollback-only reference through the
existing recorder. No prior revision/reference/source-pin/lock changed. Reference now
7e7dea28f7d1659b8793b7286de4dbddd7a22b81947db5644595f37e2f1299ae.

Reviewed direct corrections and preserved initial/reviewed failure are detailed in
ORGANIZATION_TARGETS_EVIDENCE.md. One recipient fixture hit the correct earlier old
projection guard; change only the test edge, preserve expected code/production guards.
Final fresh frame target-projections-final-ac1ivb5x full matrix PASS48.563s,432 tests
PASS11.67s, both composers PASS. Thirty source-bound steps, exact ACL and role recovery,
normal native stop retaining data;2605 originals audited, no missing/unexpected changes.
Three independent reviews complete, all ten findings individually handled, no deferrals.
Five scaffold/UI/context/docs/ADR impacts recorded in owner runbook/evidence; no ADR edit.

## Spec Change Log

## Review Triage Log

## Verification

Existing OWNER_PYTHON:
platform/deployment/.local/identity-baseline/actor-command-zxycfmc4/owner-env/venv/bin/python.
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 OWNER_PYTHON -I -B -m pytest services/access/tests
apps/pts/tests/test_release.py -q -p no:cacheprovider; both composer --check-only routes.
Root proof: platform/deployment/.local/identity-baseline/target-projections-2x4yhl18/;
2605 protected originals. Root native run99b7231c-0a5b-4bdb-98e8-3329564c526a.
No intent gap; isolated synthetic migrations/writes authorized, no real-target changes.


| Finding | Verdict | Route/evidence |
| --- | --- | --- |
| Blind1 optimized CLI reaches fixture first | medium | patch; main calls fixture before the method guard. Move the new-recording guard to actual CLI dispatch and test that entry. |
| Blind2 fixed ignored prior Python | medium | patch; explicit path names one local frame. Use this head's current canonical interpreter, retaining exact command/source evidence. |
| Blind3 UUID columns cast to text | medium | patch; selected-org equality cannot use ordinary UUID index conditions, including repeated per-profile member checks. Native equality with guarded context conversion is a direct correction; actual index-condition witness plus malformed-context proof protects it. |
| Blind4 committed temporary grant outside try | medium | patch; signal/exception in change() after commit can precede cleanup. Enclose grant in protected region, retain private before/after witness and bounded restoration, verify immediate post-grant failure. |
| Blind5 setup/user transitions | medium | patch; existing loop already covers both directions after commit, but explicit cross-context rollback/failure transitions are missing. Add those cases; no runtime change. |
| Blind6 unexpected named defaults | medium | patch; exact caller assertions don't exercise inherited unexpected default grants. Independent rollback-only source fixture proves stripping without relaxing preflight drift refusal. |
| Blind7 replacement membership | medium | patch; current retire/unretire proves currentness but no new-ID replacement. Rollback-only synthetic alternate-write fixture verifies old ID cannot substitute latest; no lifecycle feature or retained deletion. |
| Blind8 recipient unsafe rights | medium | patch; all four roles have mocked checks, but actual unsafe proof only covers definer. Add recipient membership/CREATE/read/external-execute fixtures with exact restoration/reconciliation. |
| Blind9 all staged roles after rollback | medium | patch; preflight/projection-only postcheck doesn't individually assert all staged-role emptiness. Recheck authority/command/target staged flags/dependencies before publication. |
| Blind10 final evidence pending | medium | patch; review snapshot deliberately precedes final source/stop/preservation results. Root populates actual reviewed receipts before acceptance. |

Three layers launched as slots became available; all reports precede triage. Edge and
verification-gap reviewers returned no findings. Ten individual findings accounted
for; same implementation agent handles direct patches, root finalizes evidence. No
new public contract/intent gap or deferred work. Prior revisions/references remain
immutable; only this delivery's new generated reference is regenerated by its owning
recorder if SQL changes, preserving the initial artifact/source/proof.
