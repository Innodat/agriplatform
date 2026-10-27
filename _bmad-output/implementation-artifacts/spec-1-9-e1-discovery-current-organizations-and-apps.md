---
title: 'E1-DISCOVERY: Discover currently accessible organizations and apps'
type: feature
created: '2026-10-27'
status: done
route: dispatch
baseline_commit: e2b3445f09e93827199ef06b504d03c10b605a46
review_loop_iteration: 0
context:
  - '{project-root}/AGENTS.md'
  - '{project-root}/platform/docs/development/migration-verification.md'
  - '{project-root}/platform/docs/architecture/contracts/application-admission-and-discovery.md'
  - '{project-root}/platform/docs/architecture/contracts/identity-access-employment-e1.md'
---

<frozen-after-approval reason="approved delivery intent; implementation spec awaiting checkpoint approval">

## Intent

Return the verified account's currently eligible organizations and protected apps
through Access and a narrow Identity projection. Listing never authorizes later actions.

## Boundaries & Constraints

Require permitted service credentials and current bearer before short read transactions.
Preserve isolation, membership binding, typed errors, no-store and existing consumers.
No mapping/employment prerequisite, positive cache, broad Identity reads, duplicate grants,
provisioning, Directory/launcher adoption, production activation or commits. Preserve
historical migrations, unrelated work and fixtures; KDG is not an acceptance target.

## I/O & Edge-Case Matrix

| Scenario | Result |
| --- | --- |
| Leave/reference service lists its registered app | GET /v2/organizations returns organizations:[{org_id,name,membership_id}], next_cursor; UUID IDs, decimal bigint membership, UUID order, eligible organization entry capability required. |
| Multiple pages or changed authority | At most 100 eligible rows; opaque position cursor; recheck each page; no frozen snapshot or cross-user disclosure. |
| Directory service lists apps | GET /v2/applications returns applications:[{app_id,eligible_scope_kinds}],checked_at UTC; unique ordered app IDs, canonical account/organization scope array, explicit entry capabilities only. |
| Zero memberships; mixed scopes | Account PtS remains discoverable; each scope independent; no organization details in app aggregate. |
| Empty, disabled account, invalid caller/token/input, outage | Distinguish successful empty from access_denied403, service_access_denied403, authentication_required401, validation_failed422, authorization_unavailable503; unexpected500 internal_error. Safe {error_id,error,details:{}}. |
| Spoofed identity; missing/malformed SQL context | Reject override/duplicate parameters and invalid context; never enumerate another account. |

</frozen-after-approval>

## Code Map

All paths below are relative to `services/access/`, owner of both histories.
Reuse main.py/caller_policy.py, studies_identity.py verification and identity_context.py
transactions; action bind() incorrectly requires mappings for this use. Identity25/
Access18, registry/entry mappings and both grant variants exist. Discovery routes and
identity.current_account_memberships do not. Content predecessor is done.

## Tasks & Acceptance

- [x] `tests/test_discovery.py` -- failing-first matrix tests; entry-vs-admin grants, revocation and malformed dependency data.
- [x] `identity-migrations/versions/0026_discovery.py`, `migrations/versions/0019_discovery.py` -- append current_account_memberships/discover_organizations/discover_applications, narrow RLS/grants; extend `identity-migrations/identity_baseline.py` and `migrations/access_baseline.py` with new discovery catalogue helpers/references. Preserve historical pins.
- [x] `discovery.py`, `discovery_contract.py`, `discovery_query.py`, `caller_policy.py`, `main.py` -- closed routes, exact service/app policy and multirow reads. Directory only applications; Leave/reference only their organizations.
- [x] `contracts/adapter.ts`, `contracts/generated/`, `openapi.json` -- synchronize validated DTOs/types via existing generators and executable typed fixtures.
- [x] `tests/qualify_discovery.py` -- guarded native migration/HTTP/SQL/role/compatibility proof; retain source-bound evidence.
- [x] `deployment/verify_runtime.py`, `tests/test_deployment_package.py`, `CURRENT-ACCESS.md`, Leave evidence/tracking -- package modules and record verification/impact decisions.

Given synthetic fixtures, when discovery runs, then prove shared-person accounts,
for-profit names, >100 contexts, sparse eligibility before pagination, revoke/rejoin/
stale grants, zero-membership PtS and mixed scopes. Given restricted roles, when SQL
runs/fails, then prove SELECT/SET ROLE/DDL/PUBLIC denials and context/temp isolation.

## Design Notes

No product intent gap. Select page_size 1–100 (default 100), strict bounded canonical
base64url last-org UUID cursor, reject duplicate/unknown query fields. Fetch one extra
eligible row. Validate at most 128 registered app IDs in catalogue verification and before result evaluation; overflow fails configuration,
never silently truncates. Three-second total discovery budget encloses provider/SQL.
Validate current active account separately from an empty membership projection.

Use dedicated NOLOGIN/NOBYPASSRLS definer owners, narrow columns, account-scoped RLS,
fixed safe search_path and revoked PUBLIC execution. Runtime gets only routine EXECUTE;
Identity26 precedes Access19. One current-state statement per result, no external wait
under SQL locks. Exact owning contract's canonical entry refinement supersedes older
“any capability” wording. Directory filtering/adoption remains E1-LAUNCHER.

## Implementation Notes

Approved and continued by the user on 2026-10-27. Baseline captures the current dirty
Access/scaffold bytes privately under `.local/leave-discovery-20261027/baseline/`;
VCS revision alone does not distinguish pre-existing work. No commits/activation.
Root owns native fixtures, dependency/environment preparation, final source/image proof
and evidence. Delegate owns implementation/tests/docs and exports generated contracts
through their tools. Preserve historical reference bytes and unrelated concurrent work.
Selected implementation gpt-6.1-sol/high; actual model, usage and timing unknown.
Pinned interpreter: `platform/deployment/.local/access-organization-check-20261022/owner-env/bin/python`.
Root prepared four new Identity25/Access18 clones and one genuinely empty owner case;
private selections/journal are in `.local/leave-discovery-20261027/`. Dedicated
identity_discovery_owner/access_discovery_owner roles are staged NOLOGIN/NOBYPASSRLS/
NOINHERIT with exact SET-only owning migrator membership; runtime has no membership.


## Spec Change Log

## Review Triage Log

| Finding | Verdict | Evidence | Route |
| --- | --- | --- | --- |
| Verification V1: successful reference organization discovery unverified | medium | Filed evidence confirms all successful organization assertions use Leave; reference tests only deny wrong selectors. Removing reference admission would leave those assertions passing and deny a supported caller. Verification gap accepted as filed. | patch: add exact positive reference HTTP test and native distinct-eligibility oracle; no runtime/public-surface change. |

All three context-free layers completed before triage. Blind: no supported findings.
Edge: empty findings. Verification: one finding, individually graded above before grouping.
No intent gap or bad-spec loopback; iteration remains0. No finding deferred.

## Verification

Run focused acceptance, affected Access/typed/PtS suites, generated drift, both composer
check-only modes and release.py check with pinned Python3.15/uv0.13.1. Root prepares
new guarded scratch cases on retained Leave run 88a737dd-ad7b-429a-a83c-5d103716d659
(Auth 55581/DB 55582); no reset/live grant. Prove clean/previous/repeat/failure/retry,
actual role denials, budgets, query timing/EXPLAIN, frozen package and hardened image.
Record commands/test traceability. Update proven typed scaffold fixtures; no shared UI,
agent-context or ADR change. Independent review precedes closure.


Root task and frozen-matrix audit passed before independent review. Native76steps/
17labels and actual image8HTTPcases passed. Full Access/PtS2222tests passed64.28s;
separate release9tests11subtests passed0.15s. Both composers, manifest, generated drift,
four typed suites and neutral generator fixture passed. Exact source/proof hashes and
requirement traceability are in [discovery evidence](../../apps/leave/docs/testing/e1-discovery-evidence.md).
Historical71migration/reference bytes remain unchanged. No commit/activation.


Review patch V1 complete: exact Reference success/freshness/selector test and fresh native
two-Leave/one-Reference HTTP proof passed. Final full Access/PtS2223passed52.74s; unchanged
runtime/image/migration hashes verified. All three reviews complete,1finding fixed,
0deferred, iteration0. Host APIs and exact Leave CLI acceptance run stopped normally;
fixtures retained. No commit or production activation. Ready for existing epic gate.
