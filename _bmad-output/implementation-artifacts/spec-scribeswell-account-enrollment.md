---
title: 'Scribeswell verified-account enrollment and Studies check'
type: 'feature'
created: '2026-10-23'
status: 'done'
route: 'dispatch'
baseline_commit: '4fbbcc39d2eb9749f5987acd61acfef1b0131145'
review_loop_iteration: 0
context:
  - '{project-root}/platform/docs/architecture/contracts/scribeswell-study-enrollment.md'
  - '{project-root}/apps/scribeswell/docs/PERSONAL_NOTES_V1.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

Implement and qualify the Access/Identity handoff at PERSONAL_NOTES_V1.md:85:
explicit personal Studies enrollment and current scribeswell.studies.use authority.
Use the linked enrollment contract; recipient/invitation sections remain undelivered.

User clarification agreed: readers retain Supabase Auth, identity.users profile and a
durable account actor. Organization/employment/PtS/person links are not prerequisites.
ADR0053 permits future organization Studies with separate capabilities, ownership and
grants. Personal access never implies organization access; no org implementation now.

## Boundaries & Constraints

Always verify current live account/verification and eligible current profile; reuse
valid adopted actor IDs. Missing mappings use a separate current-account-only Identity
setup routine/pool, not the operator account_actor.ensure command. Separate Identity
and Access commits retain partial completion; actor existence grants no permission.
Keep trusted service executor and verified user initiator distinct. Use ordinary
constraints/RLS/Alembic, existing locks and safe errors; no new policy engine.

Never accept browser target account/actor/email/org/permission selectors, trust JWT
roles/email alone, recreate profiles, resurrect revoked grants or create studies during
enrollment. Keep KDG checks, operator privileges and public Bible reading compatible.
Preserve concurrent work, historical evidence/resources and dependencies including
TS7.0.2. No note/editor CRUD, recipient API, Leave/PtS migration, real accounts/access,
production/deployment/pilot, cleanup or fingerprint/HMAC changes.

Native qualification needs a new narrow test-only exception beyond prior KDG authority:
resume the known retained loopback run; prepare an isolated Access/Identity test DB,
restricted DB roles and synthetic local Auth accounts for actual provider/profile-hook
proof. Retain everything; stop normally. No real accounts or general provisioning.

## I/O & Edge-Case Matrix

| Scenario | Expected behavior |
| --- | --- |
| POST /v2/enrollments/scribeswell-studies with only operation_id | Verified bearer plus Scribeswell service key;200 original committed acknowledgement, created/unchanged, account/actor/fixed permission |
| Same-operation or concurrent enrollment | At most one initial grant/event; same operation returns its original disposition after fresh eligibility |
| POST /v2/check with fixed permission and authorization_scope:{kind:account} | Canonical account_id/actor_id/permission/authorization_scope/decision_id/checked_at only; no org/person/member placeholders |
| Revoked/suspended/disabled or replay after denial | Deny without recreating grant or changing retained outcome |
| Missing/deleted/system/keyed profile, conflicting actor, unverified account | Safe refusal; no repair or invented authority |
| Wrong caller/target fields/duplicate JSON/incompatible scope | Reject before setup/write; never try another scope |
| Dependency failure/deadline/unknown commit | Safe unavailable, no positive decision/rollback claim; retry original operation with fresh eligibility |

All new outcomes private,no-store. Closed error_id variants:401 authentication_required;
403 service_access_denied/access_denied/identity.verification_required;422
validation_failed;503 authorization_unavailable/identity.setup_unavailable/
dependency_unavailable. Existing KDG error adapters remain compatible.

Access total3s including receive/verification/SQL/commit; provider work at most2s
within it. Fits Scribeswell total5s/Access3s. Lock waits≤1s, statements≤2s, positive
settings capped by remaining monotonic time. Identity also retains its5s observation
ceiling. No external waits under write locks; cancellation is not proof of rollback.

</frozen-after-approval>

## Code Map

- services/access/main.py and organization_check.py own existing v2 dispatch; no duplicate route or account/org fallback.
- Identity head0021 adds current-account setup alongside the unchanged operator command from0018; current Studies evidence reads selected live Auth eligibility fields.
- Access head0016 adds retained account grants separately from organization grants; deployment/manifest.json and host preflight enforce the Studies opt-in.

## Tasks & Acceptance

- [x] services/access/studies_contract.py and studies_identity.py -- closed DTOs, bounded live-provider/current-profile evidence; qualify current verified-primary-account semantics without recipient/address matching.
- [x] services/access/identity-migrations/versions/0021_studies_account_setup.py and owning baseline/tests -- narrow runtime setup, reused actor or account-derived absent actor, profile/binding recheck, collision refusal, immutable outcome/event and attribution; preserve operator behavior.
- [x] services/access/migrations/versions/0016_studies_account_enrollment.py and owning baseline/tests -- account grants, receipts/events, uniqueness/immutability/FORCE RLS, restricted read/write routines; controlled app/permission registration before activation.
- [x] services/access/studies_access.py plus main.py/organization_check.py -- explicit enrollment/check integration, service allowlist, strict decoding, eligibility/replay, deadlines and safe cache/exception paths.
- [x] services/access/tests/test_studies_access.py and test_studies_identity.py -- first failing enrollment acceptance, focused TDD, existing KDG characterization, partial actor completion/revocation/deadline tests.
- [x] services/access/tests/qualify_studies_enrollment.py -- actual restricted-role/Auth-hook/provider proof; clean/populated upgrade, concurrency/revoke/lost response, adopted/colliding actors, deleted/unverified accounts, pool reuse, timeout/rollback/retry and independent retained inspection.
- [x] services/access/deployment/manifest.json and platform/deployment/tests/test_release.py -- opt-in readiness, Identity-before-Access ordering, failure blocks activation, previous consumers/recovery; no deployment execution.
- [x] services/access/export_openapi.py/openapi.json and owner/Scribeswell handoff -- generate contracts/types with existing tooling, return examples/error/deadline/role/recovery matrix and source-bound test evidence.

Given zero memberships, when eligible enrollment then fresh check execute, both succeed
with verified account/durable actor. Given actor-only completion, retry preserves that
actor and creates at most one grant/event. Given revocation/current denial, replay never
restores authority. Given migration failure, activation remains blocked and supported
public/KDG consumers remain usable.

## Implementation Notes

The implementation subagent completed the owner runtime, migrations, native proof,
generated wire, release preparation and consuming handoff. Root inspected the scoped
unified diff including untracked files at /tmp/scribeswell-implementation.diff.
The frozen intent is unchanged. Preservation snapshot: /tmp/scribeswell-enrollment-before.json;
concurrent Leave/platform planning remains outside the delivery scope.

Dedicated async psycopg connections replace the initially described pools without a
dependency change. Each transaction clears actor/organization context and closes its
connection. A hard socket deadline prevents the driver's cancellation cleanup from
extending the total request budget. Valid adopted actors remain unchanged; nullable
hook-created usernames use the safe profile-derived Account <UUID> label.

ATDD chronology limitation: the first eight failures were fixture TypeErrors rather
than a user-visible acceptance failure. A later immutable-baseline HTTP comparison
proved the same enrollment request returns404 before and200 after implementation;
this is retrospective evidence, not a claim of chronological behavioral RED. Native
failures and focused corrections are retained accurately in the owner evidence.

## Verification

Existing approved Access Python and Node26.11.1/TS7.0.2 only. Run failing enrollment
acceptance, focused Identity/Access and release regressions, OpenAPI/client checks,
both composition checks, native role/provider/upgrade/failure matrix and independent
retained inspection; record exact commands/results/source hashes.

Impacts: promote proven neutral scope/adapter tests only; no speculative scaffold engine.
Shared UI/context unchanged. Owner docs and Scribeswell handoff updated; ADRs unchanged.

Root independently verified the117-test focused delivery via its source/log evidence,
earlier103 focused cases,18 corrected historical cases,9 release tests/11 subtests,
OpenAPI freshness, generated type compilation under TypeScript7.0.2, and both composers.
Final SELECT-only inspection passed4grants/4initialevents/10receipts with zero memberships,
matching durable service executor and no runtime table writes. The retained run stopped
normally (completed, ok:true) after native verification; no cleanup was performed.
The additional full port-free Access/deployment regression reached91% without reported failures before its900-second limit (exit124); it is incomplete. The matrix, native and focused owner/release checks passed.
See services/access/STUDIES_ENROLLMENT_EVIDENCE.md for exact commands and native evidence.

- 2026-10-23 user explicitly approved and continued the displayed full spec and new isolated synthetic fixture exception. Frozen intent re-read unchanged; proceed without reconfirming. Preserve all concurrent changes.

- Execution handoff is inside the already rendered bmad-build step03; implement directly from this approved spec rather than restarting the workflow. Parent handles review/finalization/commit; do not commit or push. Retain safe private failure/proof logs, never print credentials. All native effects stay in the approved isolated synthetic fixture.


## Review Triage Log

All three review layers reported before triage. Each finding is recorded separately.

| ID | Verdict | Evidence and route |
| --- | --- | --- |
| Blind1 | false | Access16 deliberately requires controlled role preparation and Identity21 before migration, documented in STUDIES-ENROLLMENT.md. Failure blocks activation and does not stop the prior running consumers. Reviewer clarified that no compatibility defect was demonstrated; reject. |
| Blind2 | low | Readiness can be copied between targets, but host preflight independently checks project/roles and runtime checks current principals/grants. Reviewer confirmed no required target-binding contract or unauthorized access; optional evidence hardening would add configuration complexity for operator mis-preparation, reject. |
| Blind3 | medium | prepare() compares only four source hashes although qualification records the helpers, baselines and release adapters too. Changing those executable sources leaves preparation accepted. Patch: compare every recorded authoritative source using safe repository paths. |
| Blind4 | low | verify_extension does not detect arbitrary migration-owner alteration of function bodies or removal of triggers. Runtime roles cannot make those changes; controlled migrations and native behavior remain the release contract. Reject additional catalog inventory for hypothetical privileged DDL, consistent with the accepted ordinary PostgreSQL verification approach. |
| Blind5 | medium | retain_qualification() labels all cases true after checking only some proof fields and attaches current hashes to prior stage files. A later source edit can therefore relabel stale execution. Patch: bind stage proofs to executed sources and validate required case evidence before retention; preserve old records. |
| Blind6 | false | Principal tables are operational release configuration, with server attribution/revision and immutable binding. The runbook explicitly requires retained release/operation evidence for principal changes; consequential account grant/setup events are immutable. No requirement mandates a duplicate principal-event table; reject. |
| Blind7 | medium | Direct create_app() only enforces completeness when the service key is truthy, whereas host preflight rejects keyless partial Studies inputs. Patch the startup completeness condition and test it. |
| Blind8 | low | The trusted Supabase response is buffered without a byte limit. No oversized provider response or ordinary failure is demonstrated; adding a custom transport/body policy for a hypothetical upstream response is unnecessary complexity here; reject. |
| Blind9 | medium | Studies exception paths return safe errors but omit diagnostic operation/trace evidence, making actual dependency failures untraceable. Patch with selected structured operation/error identifiers only, never raw exceptions, credentials, account data or payloads. |
| Blind10 | low | Native qualification intentionally binds the approved retained synthetic fixture; a fresh arbitrary fixture is not accepted. Turning it into a general provisioner adds parameters/guards outside the authorized test exception. Reject generalized fixture provisioning; retain portable focused tests and exact historical fixture evidence. |
| Edge1 | high | prepare_studies_account reads Auth before advisory-lock waits and only rechecks the profile after them. A committed Auth ban/deletion/unverification during contention can be missed. Patch: repeat the existing eligibility check after lock acquisition before local writes/acknowledgement, with an actual contention regression. |
| Edge2 | false | Same claim as Blind1, separately assessed: runtime opt-in does not exempt controlled schema migration prerequisites. The current release refuses unprepared activation while the previous running version remains available; reject. |
| Verification1 | medium | Preverified gap: existing host tests never enable Studies; a regression omitting the three conditional roles from database_url validation is undetected. Patch the actual host.preflight/deploy tests for valid input, every wrong role/project, missing inputs and stale readiness, before release effects. |

Surviving entries are direct corrections to existing validation, evidence and tests. They add no public API or new policy/authorization surface. Blind3 and Blind5 share stale source-evidence acceptance; the remaining patches have separate root causes. No intent/spec loopback is needed.


## Review Resolution

All surviving patches are complete and independently verified. Auth freshness now
rechecks after each existing advisory wait; actual RED reproduced the missed change
before implementation, then nine contention cases passed. Current stage proofs bind
executed sources and required observed cases; preparation checks the entire owning
source inventory. Startup completeness and safe diagnostic correlation are tested,
and actual host preflight covers the three Studies roles/project boundaries.

Root final focused result:143tests and49subtests passed in3.15s. OpenAPI/generated
client freshness, TypeScript7.0.2 and both composition dry runs pass. Corrected-source
native clean/populated/failure/repeat/provider/replay/deadline/race qualification passes.
Root verified36source/8proof/19log hashes, plus independent SELECT-only inspection:
4grants,4initialevents,9receipts,zero memberships,no runtime table writes. The retained
run stopped normally again; all resources/history remain. No confirmed review fix is
deferred; the separate full-suite timeout and original ATDD/exploratory-race limitations
remain explicit in the evidence rather than described as passes.
