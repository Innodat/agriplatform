---
title: Bind legacy role lookup to the current active membership
type: bugfix
created: '2026-10-20'
status: done
route: dispatch
review_loop_iteration: 0
baseline_commit: f52352fc31337f5f15b1f249775e2dcebaf134b7
context:
  - /home/ck/repos/innodat/agriplatform/AGENTS.md
  - /home/ck/repos/innodat/agriplatform/platform/docs/architecture/contracts/identity-access-execution-substrate.md
---

<frozen-after-approval reason="standing bounded shared implementation approval">

## Intent

Harden existing public.get_user_roles() before membership lifecycle changes. Return
undeleted legacy roles only for the token's exact current account/organization/member,
with active profile, membership and organization. Fix ambiguous member_id naming.
Expense keeps its existing no-argument RPC and role:string rows. This compatibility
lookup is never current Access authority.

## Boundaries & Constraints

Add identity_0009 after8 through existing Identity owner. Replace only the existing
function body/search_path with fully qualified objects and pg_catalog,pg_temp. Preserve
its signature, return type, owner and exact ACL/effective permissions; no new grants,
roles, login or credential. Source canonical PUBLIC defaults remain characterized;
separate real-target revoked-PUBLIC differences are not normalized or adopted here.
Bind JWT sub via auth.uid(), org_id and member_id to exact joined rows; no fallback to
another membership, app GUC or JWT role-array authority. Empty/missing/nil context,
nonpositive member ID and inactive/foreign bindings return no rows. Retain existing
typed-cast errors for malformed UUID/bigint/out-of-range claims; never broaden errors
into authority. Read-only function, no mutations or implicit setup.

Preserve Auth token-hook behavior/metadata sourcing and unresolved invalid-selected-org
policy, profile hardening, seeds/upserts, mapping, audit and all other functions/objects.
No uniqueness/CASCADE/retirement/rejoin/Access/WRITE change. Eight previous revisions,
references and source pins immutable; no generated JSON edits. Extend the existing
rollback-only recorder with legacy-role-reference.json/new independent pin, full source
custody, all previous catalog checks, staged-role rollback proof, exclusive publication
and optimized-Python refusal before fixture access. No new recorder/framework/service.

Root alone executes isolated DB/Docker verification. Existing fixture protocol and
restricted access_runtime LOGIN temporarily SET authenticated/service_role via existing
SET-only fixture/recovery helper; exact restoration, private durable witnesses and
bounded SQL apply. Model database execution, not JWT/provider/HTTP verification. Synthetic
Auth/profile/org/member/role fixtures only; no real account/access change, production,
provisioning/deployment, reset/prune, Leave/editor or push. Preserve concurrent work and
all prior data/resources/failures. Approved dependencies including TypeScript7.0.2 stay.

## I/O & Edge-Case Matrix

| Scenario | Expected |
| --- | --- |
| Actual head8 characterization before9 | Record real helper outcome, including existing ambiguity42702 if present; no invented old success |
| Exact active profile/org/member and live roles | Existing role:string rows; deleted role excluded, no actor/person prerequisite |
| Foreign account/org/member, retired/deleted rows, missing/nil or replayed old token | No roles; never substitute another membership or trust stale admin arrays |
| Malformed UUID/member ID, overflow, pooled context reuse/search-path spoof | Existing safe typed errors or no identity; no leaks or writes |
| Clean/adopt/head8/repeat/drift/actual mid-revision failure | Verified9 or atomic refusal retaining old data/history; old ACLs/hooks/seeds unchanged |

</frozen-after-approval>

## Code Map

Existing identity-migrations/identity_baseline.py and tests/qualify_identity_baseline.py
own head/reference/rollback recording. Revision8/profile-reference are prior head; new
functions fingerprint should be the only catalog category difference. Original helper
source20250815180000 has ambiguous member_id and no currentness joins. Expense
web/src/contexts/AuthContext.tsx consumes role rows; generated types need no change.
Use qualify_profile_fields.py bounded SQL/temp-role/witness helpers and existing
ProjectionQualification prior evidence, current sys.executable. Previous19 exact owner
files come from full baseline commit. Original SQL/composed outputs remain untouched.

## Tasks & Acceptance

- [x] Add versions/0009_legacy_roles.py, baseline/head/reference/recorder extension,
focused ATDD RED then TDD custody/ACL tests in test_legacy_roles.py.
- [x] Add tests/qualify_legacy_roles.py using existing IDENTITY_QUALIFICATION_DIR:
characterization,legacy_roles_reference,clean,legacy,previous,failure,unsafe,unknown,native.
Root preps head8 characterization/prior fixtures and synthetic clean inputs. Prove actual
restricted role rows/refusals, typed errors, pool reuse, unchanged full data hashes,
exact ACL preservation, real migration/refusal/rollback and independent source custody.
- [x] Owner IDENTITY-MIGRATIONS.md; root evidence/navigation/inventory and five impacts;
full affected suite, both composers, three reviews, protected-file audit, normal stop,
scoped local commit. No full Identity/Access/KDG readiness claim.

Given a stale or foreign membership claim, when the existing RPC executes, then no
roles escape. Given an exact active binding, then the established return shape remains.
Given failed migration/drift, then activation refuses and prior rows/evidence survive.

## Implementation Notes

ATDD RED: missing revision9/head (two focused failures). Actual unchanged8 own/foreign
lookups return42702, recorded before9 with exact temporary-edge restoration. Existing
recorder produces independent new ref182564ba568ea4a2c16285aa0bdcb37dac1fe0600165f8d2ac20bc94a4c10052;
root pins only new constant. Actual complete matrix PASS49.34s source unchanged,17 stages
plus recorder, initial-source snapshot retained. 503 affected tests PASS13.44s no skips;
both composers exit0. Every matrix row maps to executed characterization/read/migration
cases. Existing function owner/ACL/signature retained; only functions catalog changes.
Root completes independent reviews, final reviewed-source verification and normal-stop/
protection receipts before local scoped commit. Five impacts in owner runbook/evidence:
existing scaffold pattern, UI none, context unchanged, docs updated, ADR unchanged.

No intent gap in this narrowed helper-only increment. Token-hook selection policy is
preexisting remaining work, not changed implicitly. Root proof:
platform/deployment/.local/identity-baseline/legacy-roles-9ihk9x80/;2624 protected files.
Standing approval covers the existing dirty unrelated documents and this concrete scope.

## Spec Change Log

## Review Triage Log

All three context-free layers launched before triage; capacity permits one child at a
time. Blind9 findings; Edge0; Verification0. None skipped.

| Finding | Verdict / route | Evidence |
| --- | --- | --- |
| B1 spoof result equals legitimate role | low / patch | Matching admin sentinel weakens independent spoof observation; use a distinct sentinel in the existing fixture. |
| B2 arbitrary characterization errors pass | medium / patch | Exception class capture permits42501/42883 to count as historical characterization. Retain raw witness first, then assert this approved target's known42702 observations. |
| B3 multiple active role rows absent | medium / patch | Existing fixture has one live and one deleted role; revive the second rollback-only to prove complete row-set behavior. |
| B4 valid identity without role arrays absent | medium / patch | Current claims always carry admin array; add absent/empty/unrelated variants showing identity lookup independence. |
| B5 native Auth context inputs absent | medium / patch | Root read-only inspection confirms native auth.uid prioritizes request.jwt.claim.sub and auth.jwt prioritizes request.jwt.claim, unlike minimal scratch stubs. Root copies only these exact native helper definitions to final scratch fixtures; test conflict/coherent legacy forms and complete pool reset, preserving existing Auth helper authority rather than inventing a new login protocol. |
| B6 recorder SQL deadlines absent | medium / patch | New rollback-only recorder executes DDL/catalog queries without local deadlines. Add existing bounded transaction settings and focused verification. |
| B7 category comparison weaker than only-function claim | medium / patch | functions category can contain multiple changed definitions. Compare actual per-function head8/head9 rows, requiring only public.get_user_roles definition/search_path to differ and owner/ACL unchanged. |
| B8 publication directory fsync | low / reject | A host crash can lose the development artifact's directory entry; current exclusive publication makes no crash-survival promise and missing reference fails closed before activation. Extending filesystem durability for this uncommon host failure adds recovery complexity beyond practical delivery needs; no runtime authority/data loss occurs. |
| B9 signal/cleanup-failure tests absent | medium / patch | Existing tests cover ordinary exceptions only; directly invoke installed SIGINT/TERM handlers and simulate restoration SQL failure to prove handlers reset, required witness retained and no false restored witness. |

Eight local verification/recorder corrections; no production SQL decision, new public
surface or deferred finding. Same implementation agent reengaged; root owns final actual
and regression verification. Vendor helper definitions/observations are retained in the
initial proof, no native Auth function or account is modified.

Post-review actual acceptance exposes a native-only blank-sub cast before the declared
empty guard (7.244s failure, source unchanged). Raw safe diagnostic confirms22P02 on
sub=''. A new focused RED/GREEN adds only the missing CASE guard before auth.uid,
within the frozen empty-context contract. No expected result is weakened. Root preserves
failed-source and regenerates only new9 reference before fresh full actual verification.

## Verification

OWNER_PYTHON=platform/deployment/.local/identity-baseline/actor-command-zxycfmc4/owner-env/venv/bin/python.
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 OWNER_PYTHON -I -B -m pytest services/access/tests
apps/pts/tests/test_release.py -q -p no:cacheprovider. Both tools/py/run_compose_supabase.py
--check-only and --identity-authority owned --check-only. Root source-bound actual
qualifier and recorder; native normal stop, all receipts/resources retained.


Final reviewed-source native-parity actual PASS59.688s,20 recorded steps, source unchanged,
in platform/deployment/.local/identity-baseline/legacy-roles-final-x3t9_a5_/.
New9 reference regenerated only via owner recorder:983d00ac73bfc9d86188ce166cece3c246926f169b9993af0141a527d8bbd0aa.
523 affected tests PASS37.65s no skips; both composers and diff whitespace PASS. Every
matrix row has executed coverage. Eight review corrections and the native blank-sub
actual RED/GREEN fix are verified; one low finding rejected, none deferred. Five impacts
recorded; no broader Identity/Access/WRITE/KDG readiness or permission scope change.

Normal native stop completed exit0 with data retained. Preservation audit checks2624
originals: none missing, seven intended existing files changed, two concurrent memlog/
Scribeswell README changes preserved, zero unexpected changes. Executed source still
matches current files. Credential-output check passes with short vendor-password role
name coincidences excluded. Final source manifest, reviewed diff and scoped local commit
receipt retained. No required work remains for this bounded helper-only increment.
