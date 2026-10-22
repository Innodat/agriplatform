---
title: Current organization permission check for KDG
type: feature
created: '2026-10-22'
status: done
route: dispatch
review_loop_iteration: 0
baseline_commit: 1da72d2a48c6599b47e405094b173b19c407b194
context:
  - AGENTS.md
  - platform/docs/architecture/contracts/kdg-shared-readiness.md
  - platform/docs/architecture/contracts/identity-access-execution-substrate.md
---

<frozen-after-approval reason="user approved the lean usable organization check and continuing bounded synthetic implementation">

## Intent

Deliver one usable KDG-facing organization permission check through existing Access:
POST /v2/check backed by a current membership-bound SQL reader. Implement additional
consumer variants when needed; Leave must later prove its own required authorization.

## Boundaries & Constraints

Preserve the canonical KDG wire, nine exact permissions/resource mappings, current
account/profile/org/member, global/org enablement, exact nonrevoked membership-bound
grant, and durable actor setup after authority. Bearer determines account; distinct
KDG service policy restricts endpoint, exact permissions and configured organization.
No implicit read/edit permissions, actor creation, employment or arbitrary target.
Keep private reader ownership, forced scoped RLS, bounded read-only transactions,
provider waits before DB execution, safe errors/no-store and strict duplicate/unknown
field rejection. No browser Access credentials or reusable decision token.

Extend existing controlled Access migration tooling, with coordinated exact mutable
Identity/Access verifier recognition of only the approved reader extension. Historical
migrations/references and prior receipts remain unchanged. Admin preparation adds only
access_migrator's SET-only, non-inherited, non-admin edge to the existing reader. No
runtime role assumption or broad Identity privilege. Unknown/drift state refuses;
failed migration rolls back and permits explicit forward retry.

Synthetic local/CI only; preserve concurrent work, Docker resources and previous
frames. No real-account/access change, production migration, infrastructure/deployment/
pilot, cleanup/reset/prune/push, Leave/editor, account/person checks, discovery, target
APIs or KDG business-write activation. Approved dependencies including TS7.0.2 stay.

## I/O & Edge-Case Matrix

| State/request | Required behavior |
| --- | --- |
| Authorized current KDG member/grant/app | Exact declared v2 success; membership decimal string, UTC time, fresh decision UUID, correct resource scope |
| Revoked/missing grant, wrong org, disabled app, retired/rejoined member | access_denied; no stale membership/grant fallback; re-enable restores only valid authority |
| Authority valid, actor mapping absent | identity.actor_setup_required; no mutation or setup disclosure before authority |
| Invalid caller/bearer/body/scope or unavailable sources | Declared safe service/auth/validation/unavailable response; no arbitrary selectors, duplicate keys, raw errors or secrets |
| Unsafe role/ACL/catalog, migration failure/repeat | Refuse unchanged; exact approved extension only, atomic rollback, repeat preservation and explicit retry |

</frozen-after-approval>

## Code Map

Paths below are under services/access/.

- main.py/create_app/auth and new organization_check.py: strict v2 DTO/policy/query adapter. Minimal KDG_SERVICE_KEY/KDG_ORG_ID server config; absent disables, malformed partial configuration refuses safely. Keep legacy PtS activation gated.
- migrations/versions/0015_organization_check.py and existing access_baseline/access_registration_baseline/access_registration_catalog: extend exact14→15 through existing tooling. One STABLE SECURITY DEFINER access.check_organization_permission(text), private reader owner, fixed search path, current Identity projection plus registry/admission/current-member grant. Selected column rights, scoped RLS, runtime EXECUTE only.
- tools/prepare_access_check_reader_execution.sql: existing prepare_access_operator_roles.sql true-admin/version-aware SET-only pattern; no runtime memberships.
- identity-migrations/identity_baseline.py: existing verified_access_command_extension/target normalization patterns. Acyclic exact metadata validation of staged/installed Access reader bundle before tolerating its edge/dependencies; normalize only verified differences for immutable20 comparison. Existing command recognition must accept exact15.
- pyproject.toml/uv.lock: approved runtime/test subset using existing uv/cache; historical Identity lock unchanged. export_openapi.py/openapi.json: existing owner export pattern, no new generator.
- tests/test_organization_check.py/qualify_organization_check.py: existing bridge/assign/revoke helpers and fixture plumbing. ORGANIZATION-CHECK.md/ORGANIZATION_CHECK_EVIDENCE.md: owner runbook/evidence.

## Tasks & Acceptance

- [x] Existing owner migrations/verifiers/preparation: controlled14→15 and reader authority, preserving Identity20/Access14 data/history and exact prior commands.
- [x] Existing FastAPI v2 route, strict models/service policy and owner OpenAPI: Given verified current authority, return the KDG contract; given each denied/malformed/unavailable state, return its safe declared outcome with no mutation.
- [x] Focused ATDD/TDD and actual SQL→HTTP native qualification: observe missing route/routine before behavior edits; exercise runtime-role isolation, grant revoke, disable/re-enable, membership retirement/rejoin and actor precedence. Prove upgrade/repeat/rollback/drift/retry and independent retained sources/log/state.
- [x] Runbook/evidence and mutable KDG/substrate handoffs: record scaffold, shared UI, context, docs and ADR impacts; reviewed focused/affected verification and local scope-only commit.

## Implementation Notes

Root acceptance RED passed before behavior edits: actual /v2/check404 and catalog
absence of the organization routine on retained Identity20/Access14. Evidence:
/tmp/access-organization-check-red-confirmed.log; the initial schema-qualified
metadata probe refused owner schema access without mutation and remains retained.

No intent questions; standing user approval covers this goal and dirty-tree preservation.
Root owns native operations/evidence/full checks/reviews/commit; agent owns code/focused
tests/runbook and waits for root RED before behavior edits. Child runs no outer BMAD,
review or commit. Scaffold reuses owner patterns; shared UI/context/ADRs unchanged.
KDG business integration follows WRITE prerequisites; no consumer activation claim.

## Spec Change Log

## Review Triage Log

| Finding | Verdict | Evidence and route |
| --- | --- | --- |
| Blind1: incomplete body never finishes | medium | Stream has a size limit but no receive deadline; an authenticated caller can retain a request indefinitely. Patch a short body-read deadline with safe refusal and focused stalled-stream test. |
| Blind2: established connection ping has no total bound | medium | pool_pre_ping precedes transaction-local timeouts; connect_timeout only covers new connections. This existing main.py database transport behavior predates this delivery. Defer transport-level outage qualification; no full transport deadline claim. |
| Blind3: provider timeout is per I/O | low | Existing synchronous httpx adapter uses per-I/O timeout, not total deadline; a trickling provider could retain a worker. Pre-existing adapter behavior; defer total provider-operation bound rather than introduce a new transport layer in this item. |
| Blind4: malformed provider ID leaks undeclared500 | medium | UUID(123) raises AttributeError outside existing catches. Patch string validation and successful-but-malformed provider payload cases. |
| Blind5: configured non-ASCII key cannot reliably match HTTP header | low | Configuration accepts Unicode while ASGI headers decode Latin1. Patch printable ASCII startup validation and focused configuration cases. |
| Blind6: OpenAPI lacks combined service/bearer security | medium | Optional ordinary headers document neither authentication scheme nor their conjunction. Patch owner security metadata and schema assertions without changing wire behavior. |
| Blind7: current profile/org absence not proved through HTTP | medium | Native lifecycle proves memberships but does not remove profile/current organization while other authority remains. Patch separate retained synthetic reference cases with valid remaining grants and unchanged-state assertions around denied HTTP reads. |
| Blind8: installed column/RLS drift not exercised | medium | Native only role/function drift plus direct PUBLIC MAINTAIN verifier check. Patch representative column privilege and RLS-policy mutations, both owner refusals and unchanged state/catalog. |
| Blind9: preparation does not validate recipient | medium | New admin preparation checks reader but not receiving migrator flags/incoming assumption paths. Existing migration checks happen after GRANT. Patch recipient validation using existing owner role/edge contracts before mutation. |
| Blind10: evidence still says in progress | low | Delivery has not closed; final audit/review/stop remain genuinely pending. Complete normal evidence closure before commit; no behavior patch. |
| Edge1: malformed successful provider ID | medium | Numeric/object/list ID reaches UUID with AttributeError; same root cause as Blind4. Patch with its provider-shape cases. |
| Gap1: permission resource expectations reuse production sets | medium | Preverified finding: both unit/native expected scopes derive from OWN_PERMISSIONS, so a misclassification changes implementation and oracle together. Patch nine literal expected-scope pairs independent of production classifications. |
| Root1: KDG permission registered to another app | medium | SQL matches permission's registered app but does not bind it to kdg_capture; another enabled app can satisfy admission while KDG is disabled. Patch literal KDG app binding in this currently KDG-only reader and prove adversarial registration in separate reference case. |


## Verification

Use the approved prepared CPython3.15/uv0.13.1 and existing wheel cache. Root qualification
environment: platform/deployment/.local/access-organization-check-20261022/owner-env.
Run smallest failing check first, focused tests, full native/retained proof, affected
Access and PtS release/deployment adapter tests, both composition modes. Preserve
source/history/receipt custody; native lifecycle uses retained synthetic run
99b7231c-0a5b-4bdb-98e8-3329564c526a and stops normally without disposal. Do not add
exhaustive duplicate harness tests or claim portable hosted-CI/provider/device readiness.

Root also owns native qualifier orchestration (qualify_organization_check.py), agreed
with the implementation agent; the agent retains all runtime/migration/verifier code,
focused tests and owner runbook. This changes no frozen behavior or scope.


## Completion

All three review lenses completed; all patch routes passed focused/native verification.
Two pre-existing transport follow-ups are appended to BMAD deferred-work.md before
deployed Access operation. Final owner evidence records 60 focused contracts, 1,823
accumulated affected regression tests, fresh full native and separate retained proof,
composition/export checks, preservation audit and normal stop. Only this delivery's
29 paths are included in the local commit; concurrent work remains uncommitted.
