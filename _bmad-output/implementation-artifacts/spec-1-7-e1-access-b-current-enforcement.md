---
title: 'E1-ACCESS-B: Enforce current typed capability access'
type: feature
created: '2026-10-27'
status: done
route: dispatch
baseline_commit: 2586a22e0e97f39f2742b4d73c2d6a130d744c98
review_loop_iteration: 0
context:
  - '{project-root}/AGENTS.md'
  - '{project-root}/platform/docs/development/migration-verification.md'
---

<frozen-after-approval reason="approved Leave delivery; autonomous implementation and next ACCESS-B">

## Intent

Complete current Access decisions for registered account/organization capabilities and
People's verified organization context, so stale sign-in/grants cannot authorize actions.
Reuse ACCESS-A configuration and existing KDG/Studies behavior; qualify before activation.

## Boundaries & Constraints

Always preserve owner boundaries, current provider authentication outside DB transactions,
exact caller/capability/scope policy, deny-before-setup disclosure, restricted read-only SQL,
closed typed wire/errors, immutable historical migrations and controlled release recovery.
User permits necessary KDG development changes (not live); destructive proof stays disposable.
Never add discovery/business UI, E5 approval/context branches, actual PtS consumer cutover,
automatic provisioning, cached-positive/JWT-role fallback, universal credentials or commits.
Preserve unrelated dirty work.

## I/O & Edge-Case Matrix

| Scenario | Input/state | Result |
| --- | --- | --- |
| Account | Exact registered account grant/admission | Common identity/permission/scope/decision/time only; no person/member fields |
| Leave own | Current org/member/admission/bound grant | Required person, decimal membership, own-person resource |
| People | People credential, exact org, current membership | Nullable person; identity observation, no app decision |
| Wrong caller | Valid user, foreign service/capability |403 service_access_denied before identity disclosure |
| Missing grant/setup | Both absent |403 access_denied; authorized missing actor/person gets409 setup |
| Revocation | Disable/rejoin/new account | Current independent scope only; no old grant resurrection |
| Invalid/unavailable | Duplicate/unknown input, bad scope/provider/SQL |422 validation or401 auth or503 unavailable; never false denial |
| Existing consumers | KDG configured org; Studies fixed capability | Preserve their declared variants, authority and enrollment |

</frozen-after-approval>

## Code Map

Authority: epics.md3617–3714 and consolidated adoption; canonical wire in
`platform/docs/architecture/contracts/identity-access-employment-e1.md`965–1073,1168–1225;
caller matrix in `application-admission-and-discovery.md`637–703. Initial Reference IDs
are reference.record.read/create; mixed fixture also uses reference.account.read.

`services/access/organization_check.py` owns KDG and Studies dispatch; `main.py` composes
routes/auth. Preserve KDG exact nine permissions/configured-org/own_account or org resource
and Studies fixed scribeswell.studies.use/enrollment/error envelope. Do not overlap ambiguous
OpenAPI request alternatives. New canonical errors use error_id/error/details; retain
existing KDG detail.code and Studies error semantics. Reference organization resources
use explicit {kind: organization, org_id}, with no person/employment requirement. `studies_identity.py` supplies proven async dedicated psycopg
connections and bounded live-provider checks; reuse infrastructure without Studies setup.
Identity3/4/22 projections provide current actor/org/person with nullable setup evidence.
Access15 SQL hardcodes KDG; Access17 supplies account grants. Append Identity25/Access18;
use dedicated private access_capability_reader with exact staged role/ACL verification.
Current catalog helpers/baselines must recognize coordinated new heads without weakening
old roles/source checks. Root independently publishes any new references.

## Tasks & Acceptance

- [x] `services/access/tests/test_capability_check.py` -- observe general request rejection first; protect matrix and existing consumers.
- [x] `services/access/capability_contract.py`, `caller_policy.py` -- closed DTOs and validated explicit service policy. Leave own.read/manage; PtS poetry.read/export/documents; Reference record.read/create plus synthetic account.read; People context only. Unknown/duplicate/ambiguous credentials or policy entries fail closed. KDG/Studies credentials remain separate. Optional new server keys enable only their exact policy; no prefix grants.
- [x] `services/access/capability_check.py`, `identity_context.py`, `main.py` -- canonical checks and People-only POST /v2/identity/organization-context; service check before provider, then current SQL authority before setup. Common UUID/UTC fields; Leave own person resource; People exact org input and nullable person. Select 64KiB/3s body and5s execution bounds, provider<=2s, SQL<=2s/lock<=1s; safe no-store errors/logs. No provider wait in DB transaction.
- [x] `services/access/identity-migrations/versions/0025_capability_reader.py`, `migrations/versions/0018_current_capabilities.py`, owning catalog helpers/baselines -- minimal projection execution and scoped local reads; separate generic account/org checks against registered scope, app/org enablement and exact grants. Runtime has no DML/DDL, owner history or setup authority. Return nullable setup only after authority. Preserve previous KDG/Studies functions.
- [x] `services/access/contracts/adapter.ts`, `tests/capability_types.test.ts` -- typed consumer validates exact permission/scope/identity/resource and safe error taxonomy; service denial maps to dependency failure. Root exports owning OpenAPI and regenerates existing client types with pinned platform/api-client; no generated hand edits. Promote only proven neutral adapter fixtures, no unused runtime framework.
- [x] `services/access/tests/qualify_capabilities.py` -- consume root-prepared explicit private fixture, reserve outputs/journal before effects, validate actual Leave container/network/scratch binding. Real provider+restricted DB proofs: mixed scopes, zero-membership account, no cross-scope/person union, denial/disclosure, revoke/rejoin/re-enable, People context, concurrent ordering and reused context. No fixture provisioning/reference recording inside qualifier.
- [x] `services/access/CURRENT-ACCESS.md`, deployment package inputs/tests and Leave evidence -- root owns fixtures, native reference/upgrade/release/image proof and packaging; child implements business code/tests/runbook only. Root proves controlled clean/previous/failure/retry and supported old clients; old non-enforcing consumers stay gated for planned coordinated adoption, never falsely credited as enforcing.

Acceptance: Given the matrix, when actual HTTP/provider/PostgreSQL and typed clients run,
then matching decisions/errors, exact current scope and nondisclosure pass. Given supported
previous clients and migration failure, when rehearsing release, then protection remains
and dependent activation is blocked until explicit recovery. No downstream app journey claim.

## Implementation Notes

No unresolved product choice. KDG permission expansion is user-authorized; use only when
needed, preserving unrelated data. Pre-edit290-file capture: .local/leave-access-b-20261027.
Existing Leave run88a737dd-ad7b-429a-a83c-5d103716d659 uses55581/55582; KDG owns55481/55482.
No repeated planning approvals: user requested autonomous work with delivery reviews.
Scaffold: reuse proven typed HTTP/package patterns; shared UI/context/ADRs unchanged;
owner docs/evidence updated. Actual People management/E5 remains its later consuming work.

## Spec Change Log

## Review Triage Log

| Finding | Verdict / route | Evidence |
| --- | --- | --- |
| B1 existing PtS environment startup | medium / patch | Existing runtime.env.example sets PTS_SERVICE_KEY but omits the now-required capability DB; update the concrete coordinated configuration and characterize startup. |
| B2 unknown-caller envelope | medium / patch | Unknown credentials cannot identify KDG or canonical service. Preserve legacy detail.code for unrecognized credentials; valid canonical caller policy errors remain canonical and clients fail dependency-safe on unknown formats. |
| B3 API process/DB/provider fixture binding | medium / patch | Database/container guard does not establish loopback API owner/configuration; require an explicit process binding before transmitting tokens or issuing SQL. |
| B4 fixture read/hash race | medium / patch | Parsing and hashing separate reads can bind evidence to different fixture bytes; securely open once and hash the parsed bytes. |
| B5 source custody | medium / patch | Post-only hashes omit actual provider/DB implementation; capture complete runtime sources before execution and verify unchanged afterward. |
| B6 concurrent transition ordering | medium / patch | HTTP-only groups cannot race a SQL revoke in the retained runner; allow guarded SQL in synchronized groups and prove committed denial with root-controlled native synchronization. |
| B7 status-only fixture oracles | medium / patch | Generic labels do not prove success identity/resources or denial identifiers. Require complete success bindings and exact error IDs; labels remain traceability supported by explicit fixture oracles. |
| B8 organization/context variant validation | medium / patch | Native runner enforces only account response shape; validate all exact variants and required expected identity/resource bindings. |
| B9 bounded timeout verification | medium / patch | Bounds exist but focused suite lacks cancellation/cleanup tests for reception/provider/connect/SQL; add small directly exercised timeout cases. |
| B10 reproducible evidence commands | low / patch | Evidence is still provisional and P is not expanded; record final counts and exact Python/TypeScript commands before delivery. |
| E edge layer | false / none | Edge reviewer returned no findings. |
| V1 foreign organization-context client | medium / patch | Verification layer demonstrated missing negative account/org binding assertions; add independent mismatches throwing AccessDependencyFailure. |
| Root Studies generated-name compatibility | medium / patch | Executed compile fails because new model collisions rename AccountDecision. Give new canonical models unique class names and regenerate, preserving the prior Studies type export. |
| Root Access historical source chain | medium / patch | Access18 checks17 source/ref but no longer compares17's predecessor_sources map. Preserve all recorded1–16 source checks without replaying old catalog verification. |

## Verification

P=platform/deployment/.local/access-organization-check-20261022/owner-env/bin/python.
Use -I -B, PYTEST_DISABLE_PLUGIN_AUTOLOAD=1, pytest -p no:cacheprovider; failing-first,
affected tests, then services/access/tests plus apps/pts/tests/test_release.py. Check both
composers (owned --no-seeds), exported/generated contracts and consumer compilation.
Native root alone stages original restricted logins; preserve failed frames and journal IDs.
Rebuild frozen Access package/image after API inputs change; no startup migrations.

Native verification:25 HTTP/SQL checks plus9 supplemental scenarios,32 exact prior-client replays,5 current owner-catalog pairs,66 historical files preserved; clean chains and coordinated failure/retry passed. Frozen hardened image passed including Studies synthetic startup; API/TestClient focused155 and adapter executable checks passed. Owner packaging8 and characterized migration regression196 passed. Broader regression is recorded in the private delivery frame.

Final verification after all review patches:2,154 owner/PtS tests passed in93.42s with one existing warning; separate shared release9 passed/11 subtests. All13 findings fixed, none deferred. Retained qualifier27 steps and source17 inputs passed, controlled uncommitted/committed revoke proof passed, final7 boundary checks passed; five current catalog pairs and66 historical files preserved. Final frozen image passes ordinary, Studies synthetic and updated canonical manifest startup plus stale/forged bundle rejection. OpenAPI/generated drift, all3 typed consumer proofs, both composers and manifest check passed. No commit by explicit handoff instruction.
