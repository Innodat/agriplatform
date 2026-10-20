---
title: Exclude retired organizations from existing token membership claims
type: bugfix
created: '2026-10-20'
status: done
route: dispatch
review_loop_iteration: 0
baseline_commit: b790051bf93417640702ff450aff9d4e9b398575
context:
  - /home/ck/repos/innodat/agriplatform/AGENTS.md
  - /home/ck/repos/innodat/agriplatform/platform/docs/architecture/contracts/identity-access-execution-substrate.md
---

<frozen-after-approval reason="standing bounded shared implementation approval">

## Intent

Make existing identity.custom_access_token_hook emit membership/role/owner claims only
for an active membership in a nonretired organization, as the accepted E1 membership
contract requires. Exclude retired organizations from fallback selection and org_ids.
Preserve existing metadata selection and wire shape. This is legacy Auth integration,
never current Access authority.

## Boundaries & Constraints

Add identity_0010 after9 through existing Identity owner. Replace only this hook's body
and search_path, using fully qualified names and pg_catalog,pg_temp; preserve signature,
owner, ACL/effective permissions and every other function/object. Join active organization
in fallback, exact account/member lookup and org_ids enumeration. An explicit current_org_id
remains the selected ID; if invalid/foreign/retired it receives no member/roles/owner and
never silently falls back. Existing active-org slug resolution remains. Missing/JSON-null
selection uses existing owners-first/created_at ordering over eligible memberships; no
new tie breaker or policy. Preserve top-level event.user_metadata sourcing, JSON claim
keys/null/array/boolean shape, unrelated claims/event fields, existing UUID cast errors,
profile lifecycle behavior and role-deletion filtering. No new profile requirement,
actor/person mapping, role grant, login, credential or API. No writes from the hook.

Nine historical revisions/references/source pins and original SQL/composed files are
immutable. Extend the existing rollback-only recorder with token-hook-reference.json and
independent pin, full source custody, previous catalog checks, bounded SQL, staged-role
rollback, exclusive publication and optimized-Python refusal. Root alone runs DB/Docker;
reuse prepared private isolated databases, bounded SQL and exact temporary-edge restoration
with durable private witnesses. No generator, service or alternative fixture framework.

No membership uniqueness/CASCADE/retirement/rejoin command, live-account adapter,
Access/WRITE, server KDG, Leave/editor, real accounts/providers/access, production,
provision/deploy/pilot/reset/prune/push or dependency changes. Preserve concurrent work,
all data/resources/receipts/failures. Approved TypeScript7.0.2 stays.

## I/O & Edge-Case Matrix

| Scenario | Expected |
| --- | --- |
| Unchanged head9 with retired selected org/fallback/org_ids | Record actual old claims demonstrating the missing organization filter before10 |
| Active own selected membership/live roles | Existing member/role/owner/org_ids shape; deleted role excluded; unrelated fields preserved |
| Retired org/member, foreign account/member, explicit invalid selection | No invalid member/role/owner authority; retired org absent from org_ids; explicit selection never replaced |
| Missing selection and active alternative | Existing owners-first/created_at fallback among active memberships in active orgs only |
| Missing/nil account, malformed UUID, no roles, spoof/pool reuse | Denial/empty claims or preserved typed error; no cross-account or search-path leak or writes |
| Clean/adopt/head9/repeat/drift/mid-migration failure | Verified10 or atomic refusal preserving historical rows, ACLs, hooks and histories |

</frozen-after-approval>

## Code Map

Original hook: platform/supabase/migrations/20250815210000_platform_multitenancy_orgs.sql,
lines115 onward. Exact selection is coalesce(explicit UUID, first undeleted membership);
only slug currently checks org.deleted_at. Existing E1 contract membership retirement
section requires active membership and organization. Legacy RPC was fixed in9; leave it.

Existing services/access/identity-migrations/identity_baseline.py owns constants, head,
reference chain. tests/qualify_identity_baseline.py owns the recorder branches. Use9
migration/reference and tests/test_legacy_roles.py as focused custody examples. Reuse
qualify_legacy_roles.py and qualify_profile_fields.ProfileQualification for actual role,
bounded SQL, private witnesses and SET-only fixture edges; do not modify shared helpers
unless needed. PREVIOUS_FILES is the exact21 old owner py/json files at baseline commit;
get them via git tree, not an open-ended filesystem glob. Prior-frame bootstrap templates
in platform/deployment/.local/identity-baseline/legacy-roles-final-x3t9_a5_/ show the root
route. Root proof starts at token-hook-qv4fbmr4/ in the same parent. Tests use exact native
auth.uid/auth.jwt definitions in scratch DBs; no vendor native function changes.

## Tasks & Acceptance

- [x] Add versions/0010_token_hook.py, new baseline head/reference/recorder branch and
focused test_token_hook.py. Observe acceptance RED before production SQL implementation.
- [x] Add tests/qualify_token_hook.py with existing IDENTITY_QUALIFICATION_DIR protocol:
characterization,token_hook_reference,clean,legacy,previous,failure,unsafe,unknown,native.
Root prepares synthetic profile/org/member/role fixtures and exact head9 prior source;
qualifier must not create databases, roles or credentials. Characterize old9; prove new
hook directly under supabase_auth_admin through restricted access_runtime fixture SET
edge, exact ACL/function compatibility, data hashes, source custody, typed errors,
selection/role/pool/spoof rows and real migration/refusal/rollback. Direct SQL is not
provider/JWT-signature/HTTP verification. Use rollback-only fixture mutations.
- [x] Update owner IDENTITY-MIGRATIONS.md; root records evidence, inventory, contracts
and KDG navigation, five impacts, full affected tests/composers, independent reviews,
preservation audit and normal retained-data stop. Scoped local commit only.

Given a retired selected organization, when Auth invokes this hook, then it emits no
member/role/owner authority. Given eligible fallback memberships, when metadata is absent,
then only an active organization can be selected. Given explicit foreign/retired ID,
then no replacement membership is selected. Given migration failure, then prior data
and history remain and activation refuses.

## Implementation Notes

No unresolved intent choice: explicit invalid selection and top-level metadata sourcing
are preserved from current code. Only additive isolated synthetic migrations execute;
production remains excluded. Footprint: one revision/reference, existing owner baseline/
recorder, focused test/qualifier and owner/navigation docs. Standing approval covers this
bounded implementation and existing dirty concurrent documents; no sprint tracker change.
Root records all actual proof; implementation child runs CPU tests only, leaves new pin
None until root recorder succeeds, and leaves root evidence/navigation work to root.

## Spec Change Log

## Review Triage Log

All three context-free layers launched before triage; host thread capacity permits one
reviewer at a time. Blind10 findings, Edge0 and Verification0; no layer skipped.

| Finding | Verdict / route | Evidence |
| --- | --- | --- |
| B1 recorder presented among repeatable commands | low / patch | Recorder correctly refuses existing pinned artifact; separate one-time generation prerequisites from repeatable qualification in runbook. No historical reference deletion. |
| B2 literal OWNER_PYTHON evidence command | low / patch | Evidence command reads as executable but lacks variable expansion; write the actual shell variable form. |
| B3 concurrent temporary global role edges | low / reject lock extension | New fixture reuses existing root-only sequential custody protocol; simultaneous same-cluster qualifiers are outside this supported execution route. Automatic cluster coordination across all historical qualifiers adds machinery for an uncommon unsupported developer invocation. State the existing single-root sequential requirement beside commands; preserve fail-closed edge checks and exact recovery witnesses. |
| B4 missing account UUID not validated | medium / patch | Fixture validation excludes missing key from canonical/distinct checks; validate all five IDs and verify synthetic missing profile absent before using it. |
| B5 no eligible fallback case absent | medium / patch | Retired selected with valid alternate is covered; add rollback-only all-orgs-retired fallback asserting complete empty/null shape. |
| B6 deleted member assertions incomplete | medium / patch | Current test checks role arrays only; prove null member/false owner, org_ids exclusion and fallback past deleted owner. |
| B7 no-active-role membership identity incomplete | medium / patch | Current role-retirement test checks arrays only; prove member/org/owner retained with empty roles. |
| B8 no profile prerequisite wording broader than fixture | low / patch | Existing membership FK requires identity.users row and cascades on deletion; no absent-profile fixture is structurally possible. Clarify no added active-profile check and retain FK, matching soft-deletion evidence. |
| B9 absent claims initialization untested | medium / patch | invoke assumes unrelated claim exists and all fixtures supply claims; permit absent input and assert complete generated claims without weakening unrelated-field preservation when supplied. |
| B10 role grant failure cleanup untested | medium / patch | Existing CPU tests interrupt inside body; add grant failure before/after committed mutation with exact cleanup/handler/witness assertions. |

Nine direct documentation/fixture-test corrections; one low automatic-lock extension
rejected under the lean current-stage scope. No production SQL/pin/public surface change,
intent gap or deferred finding. Same implementation agent handles patches; root reruns
reviewed-source actual acceptance and affected suite/composers afterward.

## Verification

Use frozen owner Python at platform/deployment/.local/identity-baseline/actor-command-zxycfmc4/owner-env/venv/bin/python.
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 OWNER_PYTHON -I -B -m pytest services/access/tests
apps/pts/tests/test_release.py -q -p no:cacheprovider. Both composer --check-only routes,
source-bound actual matrix, exact historical sources, three review layers, preservation,
private safe-output receipts and normally stopped native project with retained data.


Initial execution: CPU ATDD RED two missing10/head checks before SQL;44 new focused tests,
567 affected PASS22.38s no skips; both composers exit0. Actual unchanged9 characterization
confirms retired selected/fallback roles; full16-stage matrix PASS27.914s source unchanged,
including restricted Auth role, ACL/function comparison, read edge matrix and migration
rollback/refusal. Recorder reference f227a7839ba8e04fe1626254e91678c73cf3fc2aa5e38fdb0a5b1ec6a3633263
pinned only after PASS. First root receipt-grouping failure happened before mutation;
original receipts and failed attempt retained. Independent reviews/final custody remain.


Final reviewed-source complete matrix PASS30.111s source unchanged in
platform/deployment/.local/identity-baseline/token-hook-reviewed-p8m4d4yu/;19 recorded
stages include unchanged9 characterization and all expanded acceptance cases. All577
affected tests PASS26.24s, no skips; both composer routes and whitespace check PASS.
Nine direct review corrections verified; one low automatic-lock extension rejected,
none deferred. New SQL/reference/pin unchanged. Source custody, exact ACL/function/data
preservation and temporary-edge restoration pass. Five impacts recorded in evidence.
Normal retained-data stop and preservation/safe-output/final-source receipts complete
the bounded delivery.2635 protected originals remain, seven intended existing changes,
original concurrent work preserved and no unexpected changes. No full ID-B/Access/WRITE/
KDG readiness, production/provider or HTTP/JWT-signature proof is claimed.
