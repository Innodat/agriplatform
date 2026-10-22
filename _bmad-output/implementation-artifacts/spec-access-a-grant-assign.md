---
title: Protected organization grant assignment
created: '2026-10-22'
type: feature
status: done
route: dispatch
review_loop_iteration: 0
baseline_commit: 666211dfecb2bf3a255277941aeff81781d926be
context:
  - AGENTS.md
  - platform/docs/architecture/contracts/identity-access-execution-substrate.md
  - platform/docs/architecture/contracts/e1-controlled-provisioning-and-evidence.md
---

<frozen-after-approval reason="standing bounded prerequisite implementation approval and next instruction">

## Intent

Deliver organization grant.assign through existing Access owner migration/operator/CLI,
so explicitly authorized operators can create, preserve or deliberately rebind/regrant
one registered organization capability to an exact current membership, with atomic
server attribution, revision, audit and retry evidence. No effective reader is activated.

## Boundaries & Constraints

Use Access0013 after12, immutable older history, existing roles/outcome/event scaffolding
and strict parser. Resolve app from immutable organization permission registration;
check current principal and exact command/org/app/account policy before Identity reads,
then recheck after waits. Platform/other command authority never implies assignment.
Target-null means explicitly all accounts for that authority; reject nil target IDs.

Use existing Identity organization_account_target exact supplied account/member, trusted
setup context with absent caller account, no grant prerequisite or latest-member lookup.
Observe before local write/coordination locks; total observation lifetime5s, all retries
reobserve. No Identity waits under local business locks. Retirement races retain the exact
observed binding; replacement receives nothing without a new verified command. Preparation
may occur with disabled app/admission; assignment alone never enables access.

Expected absence/revision precedes no-op. New UUID-text ID/revision1; preserve existing
opaque IDs and creation fields. Changed/regrant increments revision, clears revocation
and binds supplied member; matching active binding unchanged has no event/revision bump.
Unknown original creation actor refuses explicit conflict rather than inventing history.
Server executor comes from protected mapping, not target actor/GUC/payload. No raw runtime
writer; command owner gets narrow required DML/RLS and statement/row/deferred evidence
guards. Atomic outcome/event and versioned canonical fingerprint preserve retry identity.

Preserve concurrent documents/data/resources and all older sources/receipts. No legacy
PtS-write compatibility, account grants/revoke, ACCESS-B/readers/PtS/Content/KDG activation,
Leave/editor, dependency changes, generator/service/framework, real accounts/access,
production/provision/deploy/pilot, reset/prune/cleanup or push. TS7.0.2 unchanged.

## I/O & Edge-Case Matrix

| Scenario | Expected behavior |
| --- | --- |
| Valid exact member without grants; disabled admission | Create explicit binding only, typed receipt and atomic audit |
| Same request/new operation/noop/stale absence or revision | Replay stable; expected state checked; unchanged no fake event; conflicts no effects |
| Revoked/replacement membership/opaque ID/overflow | Deliberate verified regrant only; preserve creation/ID; overflow refuses changed write |
| Wrong org/app/account/command or disabled authority | Deny before target observation/effects; GUC/role spoof cannot grant authority |
| Missing/retired/unmapped target; timeout/observation expiry | Refuse no effects; fresh execution rechecks, never substitutes membership |
| Authority/target/grant races and operation/authority/business locks | Bounded safe error, exact binding, serialized expected state and atomic rollback |
| Raw writer, alternate/multirow/forged or missing evidence | Constraints/guards refuse, entire transaction rollback |
| CLI/worker/receipt malformed target/irrelevant fields | Closed typed validation before dispatch, safe output and bounded recovery |
| Populated12→13/repeat/five prior commands; Identity19 | Preserve data/receipts/old behavior and metadata-only exact verification |
| Catalog/history/ACL drift, migration failure/custody | Refuse normalization; forward retry; source/log/state-bound single-use and retained proof |

</frozen-after-approval>

## Code Map

New migrations/versions/0013_grant_assign.py extends existing0009 authority/command/evidence
pattern. Mutable access_registration_baseline.py/catalog.py get exact13 branch; access_baseline.py
must explicitly preserve12 strict FK/CHECK/tombstone branches when HEAD advances. Identity
identity_baseline.py selects13 using schema-resolved assignment routine metadata before12;
no Identity migration/reference/privilege changes. Historical SQL remains unchanged.

Extend access_operator.py typed result/canonical account UUID/execute/outcome; operator_cli.py
closed Access worker/CLI dispatch and exact target binding. Existing grant parser remains.
Grant target keys exactly grant_id/account_id/permission/org_id/membership_id, no app_id.
Outcome selectors organization/account/member/permission; add account/member CLI flags.
Retain five current command wire contracts and Identity rejection of Access commands.

Add test_grant_assign.py, qualify_grant_assign.py, GRANT-ASSIGN.md. Reuse configure qualifier
for command/authority/concurrency/CLI/upgrade/drift; pregrant helper for supported Identity
ensure/join/retire/rejoin; strict qualifier for source/input/log/state custody. No generic
fixture framework. Report exact CASES/bootstrap needs before root prepares fresh fixtures.

## Tasks & Acceptance

- [x] Observe acceptance RED, implement migration/catalog/client/CLI and focused tests/native
qualifier/runbook using owner seams; preserve exact historical recognition and previous clients.
- [x] Root native/retained proof, reviews, affected regressions/composers, requirement/five-impact
records, normal stop, final custody audit and scoped local commit.

Given exact approved operator and current target, assignment creates one bound grant and
atomic evidence. Given stale/unauthorized/replaced input, it cannot change another binding.
No implemented assignment claims effective app admission or reader delivery.

## Implementation Notes

No intent gap; migration execution only isolated synthetic. Dispatch footprint spans owner
DDL/catalog/adapter/CLI and tests. Existing Identity dependency is delivered. Root owns
native RED/bootstrap/evidence/current handoffs/reviews/full checks/stop/commit; agent owns
implementation/tests/runbook only, no DB/Docker/agents/workflow/commit. Wait for root RED
before production edits; missing-feature tests may precede it. Freeze source for bootstrap.

Select compact event transition before/after membership_id/revoked_at/revision plus executor
attribution. Persist verified member revision/account actor/observation time in three nullable
private operation_outcome columns, required only for grant.assign; old commands retain NULL.
No display text in audit. Guard exact shape/freshness and paired grant/outcome/event; no
external verification inside deferred local evidence checks. Existing operator10s/SQL5s,
lock2s budgets/error semantics remain; only operation retry lock maps busy.

Five impacts: extend existing owner scaffold; no UI/context/ADR changes; owner evidence,
runbook and mutable shared/KDG/deployment handoffs. No new pattern engine. Standing approval
covers dirty tree/spec. Preserve54 historical and77 baseline production sources except
intended mutable files. Existing bootstrap/private portability limitations stay explicit.

## Spec Change Log

## Review Triage Log

| Finding | Verdict | Evidence and route |
| --- | --- | --- |
| Blind1: unconditional commit-freshness runbook wording | low | Real wording ambiguity: PostgreSQL deferred checks can be forced early, while the supported adapter owns its transaction and never does so. Evidence already states this limit. Patch runbook to match it. |
| Blind2: previous client only replays after upgrade | medium | upgrade_previous replays/looks up pre13 operations but does not create new ones through the old adapter. Patch native fixture with fresh old-client commands, including both changed enablement paths. |
| Blind3: no positive exact authority | medium | Matching app/account authority is disabled without positive assignment/recovery. Patch before disabling it; broad mapping remains disabled. |
| Blind4: authorization ordering not observed | medium | Snapshots prove no writes, not absence of Identity observation. Patch with blocked Identity relation: denied request returns before projection and authorized request safely times out. |
| Blind5: Identity exception mapping untested | medium | Native lock tests start after projection; no actual projection exception exercises new AC004 mapping. Patch bounded blocked projection and complete rollback. |
| Blind6: inactive organization/profile integration absent | medium | Projection itself has separate soft-delete coverage, but assignment integration lacks it. Patch owner fixture soft-delete/refusal/restoration cases. |
| Blind7: competing changed expected revision absent | medium | Existing concurrency proves expected absence only. Patch simultaneous explicit rebind against the same existing revision; one changed event/revision, one conflict. |
| Blind8: observation evidence boundaries absent | medium | guards covers missing/old values, not future/infinite/nil/nonpositive branches. Patch existing rollback-only malformed evidence vectors. |
| Blind9: native canonical escaping absent | medium | Client parser tests special ASCII but native assignment uses plain permissions. Patch registered escaped permission execute/replay/exact lookup agreement. |
| Blind10: final evidence incomplete | low | Review diff was staged before final aggregate/retained/stop/custody records; partial current records now exist. Patch by completing final evidence after verification, not claiming it early. |
| Edge1: manually early deferred checks bypass delayed-commit TTL | low | Real PostgreSQL behavior for manually controlled SQL, outside the supported adapter which rejects caller-owned transactions and commits without SET CONSTRAINTS. Root evidence already acknowledges it; same runbook overclaim as Blind1. Patch precise supported/default-deferred wording, no unforceable commit-hook claim or new framework. |
| Gap1: exact app/account authority success untested | medium | Preverified mutation evidence shows always-deny restricted policies pass existing negatives. Same missing positive case as Blind3; patch native assignment plus recovery under only matching policy. |

All12 findings individually classified before grouping. Groups Blind1/Edge1 and
Blind3/Gap1 share roots; Blind4/Blind5 share the blocked-projection fixture gap. Remaining
findings are separate direct test/document corrections. No intent gap, production
permission expansion or new public surface is needed. No deferral.

## Verification

Prepared Python: platform/deployment/.local/identity-baseline/actor-command-zxycfmc4/owner-env/venv/bin/python.
Focused TDD then actual native --all/separate --verify-retained, Access tests + PtS release
+ migrate adapter, both composition modes. Run99b7231c-0a5b-4bdb-98e8-3329564c526a; root
fresh templates from strict-grant-final-20261022, protected Identity operator credential
from grant-registry-red-20261022 if required. Never copy generated credentials/state/logs.
Record consumed private bootstrap dependencies; no portable CI or logical-restore claim.


Implementation allocation: root owns access_operator.py/operator_cli.py and focused client
checks (test_grant_assign_adapter.py plus affected CLI/input tests). Implementation agent
owns migration/catalog/baselines/native qualifier/runbook and their focused tests. Files
are disjoint; no additional agent. Fixed SQL seam:
assign_organization_grant(operation uuid,org uuid,account uuid,member bigint,permission text,
absent boolean,revision text,reason text,evidence text,canonical bytea), and
organization_grant_assignment_outcome(operation uuid,org uuid,account uuid,member bigint,
permission text), both return existing four receipt columns. Identity dependency filtering
must admit only exact intended grant column UPDATE dependencies after full Access catalog
verification; keep rejecting unrelated rights. Root native RED still precedes production.


Final result:1519 affected tests PASS53.60s; both composition checks exit0. Final
source-bound nine-case native proof passes13 stages and separate retained inspection;
128 sources/24 diagnostics/state digest verified. Three review lenses completed,12
individual verdicts, all direct test/doc corrections applied, no deferral. Normal local
stop completed with data/volumes/history retained. Final audit preserves54 historical
sources,71 unchanged production files, six intentional current-owner edits and all
concurrent work. Owner evidence records exact commands, limitations and impact decisions.
Scoped conventional local commit completes this item; no push or consumer activation.
