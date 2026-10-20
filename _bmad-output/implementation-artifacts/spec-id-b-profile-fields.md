---
title: Protect authenticated profile security and attribution fields
type: feature
created: '2026-10-20'
status: done
route: dispatch
review_loop_iteration: 0
baseline_commit: 630d1ae86db175c10806a3c3e3662962052aa978
context:
  - /home/ck/repos/innodat/agriplatform/AGENTS.md
  - /home/ck/repos/innodat/agriplatform/platform/docs/architecture/contracts/identity-access-execution-substrate.md
---

<frozen-after-approval reason="standing bounded shared implementation approval">

## Intent

Narrow existing authenticated profile writes so ordinary users cannot supply Identity
security/actor/creation-attribution fields. Deliver through the existing Identity
owner and revision8, preserving supported legacy writers and row authorization.
This is protected-column hardening, not new account provisioning or profile lifecycle.

## Boundaries & Constraints

Add identity_0008 after0007, column ACL only: authenticated INSERT(id,username),
UPDATE(username,deleted_at). Revoke its table-level INSERT/UPDATE and existing column
INSERT/UPDATE before exact grants. Explicit protected columns (even unchanged values)
refuse; no JWT admin claim/GUC/legacy authorize opens column rights. Verify effective
privileges include PUBLIC/inheritance; unexpected surviving protected rights fail closed,
never repair unlisted principals. Preserve existing SELECT rights/absence, DELETE rights,
RLS, defaults, audit/Auth hooks, other tables/functions and trusted service_role rights.
No new SELECT grant merely to enable a previously unsupported query. Preserve existing
soft-delete/unretire behavior; future lifecycle hardening stays open.

Protect UPDATE id/actor_key/is_system/is_platform_admin/created_by/created_at/updated_by/
updated_at and INSERT fields except id/username. Existing defaults and audit trigger
manage ordinary attribution; do not change shared audit functions used by Expense/CS.
Controlled migrator and explicit postgres System/Migrate seed grants remain unchanged.
Auth hook creates profiles as before; retained create_user helper gains no Auth INSERT
or new invocation authority. Account/actor/membership mappings and read projections
remain untouched; broad trusted legacy service_role scope is not redesigned here.

Characterize actual head7 before applying8: authenticated role effective rights,
own username/deleted_at writes, missing-profile insert/default/audit, and protected-field
forgery. Use root-prepared synthetic Auth stub/profile fixtures, no real accounts. Actual
restricted LOGIN may SET LOCAL ROLE authenticated/service_role only through temporary
SET-only/non-inherited fixture edges, current/session identities recorded, exact edge
restoration and private recovery receipts. These model PostgREST role execution, not
provider/JWT verification. Root alone executes DB/Docker/role setup; qualifier creates
no infrastructure/login/credential. Standard Auth schema USAGE in scratch fixtures is
vendor parity setup, not new Identity migration authority.

Extend existing baseline and existing rollback-only reference recorder with independent
profile-reference.json/new pin; never modify seven prior revision/reference/source pins.
Guard optimized recorder CLI before fixture access; capture full source chain, verify
prior catalogs and staged roles, exclusive publication/no auto-pin. No new generator,
framework/service/dependency or generic recorder. Preserve concurrent files/resources.
No real account/access/provider changes, production migrations/provision/deploy/pilot,
Leave/editor, automatic downgrade/cleanup or push.

## I/O & Edge-Case Matrix

| Scenario | Expected |
| --- | --- |
| Head7 characterization; protected UPDATE/INSERT after8 | Preserve original observations;42501 for protected attempts, no partial profile/audit/map effects |
| Own username/deleted_at and INSERT(id,username) | Existing row policy/default/audit behavior; no new read rights |
| Same-value/mixed writes, upsert/ON CONFLICT, wrong account, spoofed claims | Exact column policy and existing RLS; no elevation or partial effects |
| Auth hook/legacy seed/service role/current-account and target reads | Compatible existing behavior/identities; no new Auth authority |
| Clean/adopt/head7 upgrade/repeat/drift/failure | Verified head8 or refusal/atomic rollback; existing rows/history preserved |

</frozen-after-approval>

## Code Map

Existing identity-migrations/identity_baseline.py and revision7/ref recorder in
tests/qualify_identity_baseline.py own catalog/history/captured source. Reuse existing
qualify_organization_targets.py/ProjectionQualification fixture and prior-evidence
pattern, current sys.executable rather than ignored fixed paths. Original source
20250815110000 profile policies/grants/Auth hook; 20250815170000 audit trigger; seed
001_identity.sql and revision1 LEGACY_INTEGRATION_SQL are compatibility owners.
No original parser/adapter/CLI, generated client types, API or shared UI changes.

## Tasks & Acceptance

- [x] Add versions/0008_profile_fields.py, new baseline/reference/recorder branch and
focused custody/ACL tests. ATDD RED before implementation; characterization precedes
risky privilege changes. Migration SQL preserves all unrelated ACLs/defaults/objects.
- [x] Add tests/qualify_profile_fields.py using existing IDENTITY_QUALIFICATION_DIR.
Cases characterization,profile_reference,clean,legacy,previous,failure,unsafe,unknown,
native. Root prepares char/head7 prior fixtures. Qualify actual normal role writes/
refusals/audit, exact restoration, compatibility/pooled reuse, legacy/head7/mid-revision
failure/no-op/drift. No new role/login/credential provisioning in qualifier.
- [x] Owner IDENTITY-MIGRATIONS.md; root evidence/navigation/inventory and all five
impact decisions; actual source-bound proof/full affected tests/both composers,
three reviews, protected-file audit, normal stop and scoped local commit.

Given a synthetic authenticated self profile, when writing protected fields after8,
then permission denies without partial state. Given an allowed existing write, when
executed under its real role/RLS, then existing behavior and server attribution remain.
Given schema/history/privilege drift or migration failure, then activation refuses and
original rows/source/evidence remain. No full ID-B/Access/WRITE/KDG readiness claimed.

## Implementation Notes

Revision8 restricts profile input with ACLs only; existing policies and writer/default
behavior remain. Actual head7 first confirms security/creation-field forgery succeeds.
CPU RED6 failures observed; full affected462 PASS21.68s and both composers PASS.
Complete fresh actual matrix PASS54.756s, source unchanged, in profile-fields-accepted-ds2j_k23.
Original failed frames are retained with explained fixture corrections and exact recovery.
Live compatibility delta verifies only four ACL catalog categories change. Comment-only
correction regenerates only new reference via owner recorder:05ccb6afc5c546d18ea16747a59d4e63c6f8576718d885b43ecc03e676779868.
Prior references/revisions/source pins immutable. Scaffold extends existing owner pattern;
UI none; context unchanged; docs/evidence/navigation/inventory updated; ADR unchanged.
Root completes independent reviews, reviewed-source checks and normal-stop/preservation
receipts before commit. No permission scope expands.

## Spec Change Log

## Review Triage Log

All three independent layers launched before triage; thread capacity admits one child
at a time. Blind10 findings; Edge0; Verification0. No layer skipped.

| Finding | Verdict / route | Evidence |
| --- | --- | --- |
| B1 grant before cleanup scope | medium / patch | PUBLIC/table grant commits before snapshot/try; snapshot failure strands fixture authority. Move scope before mutation. |
| B2 missing ACL/trigger recovery witnesses | medium / patch | Committed synthetic ACL/event-trigger mutations lack the durable original-state recovery receipts used by role fixtures. Record before and after. |
| B3 administrative deadlines | medium / patch | self.sql has connect timeout only; GRANT/REVOKE and event DDL can wait on locks through cleanup. Add bounded transaction settings. |
| B4 preexisting anon privilege removal | false / reject | Supported upgrades_and_failures calls inherited_privilege only after successful canonical head8 reconciliation. Full effective-column catalog includes anon, so unexpected protected grant refuses upstream before this method. No new guard needed. |
| B5 unchanged protected values coverage | medium / patch | Only two Boolean same-value inputs execute; extend existing denial loop with owner-observed same values for every protected column. |
| B6 independently spoofed app GUC coverage | medium / patch | Existing role helper always matches subject/context; explicit privileged/mismatched GUC assertions in scope are unexecuted. Add fixture variants. |
| B7 audit baseline | medium / patch | Aggregate count permits prior rows in the consuming fixture protocol; baseline IDs and prove only new successful effects. |
| B8 creation/update attribution comparisons | medium / patch | Presence/current actor checks omit preserved creation fields and advancing update timestamp. Compare before/after supported edits. |
| B9 pool receipt exceeds proof | medium / patch | Existing connection remains checked out with same account. Prove pool return/recheckout, different account and app-context reset. |
| B10 service INSERT compatibility | low / patch | Exact unchanged catalog protects INSERT rights but actual role compatibility only exercises UPDATE. Add rollback-only missing-profile INSERT to existing fixture. |

Each accepted correction is local verification/fixture code, no new public surface or
production SQL decision. Same implementation agent reengaged for focused patches;
root performs final complete verification. No deferred finding.

## Verification

OWNER_PYTHON=platform/deployment/.local/identity-baseline/actor-command-zxycfmc4/owner-env/venv/bin/python.
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 OWNER_PYTHON -I -B -m pytest services/access/tests
apps/pts/tests/test_release.py -q -p no:cacheprovider; both composer --check-only routes.
Root proof platform/deployment/.local/identity-baseline/profile-fields-vt3hulju/;
head7 previous17 files at baseline commit,2612 protected originals. Native run unchanged.
No intent gap; synthetic-only mutations authorized; no public API/schema fields added.


Final reviewed-source actual22-stage matrix PASS43.923s, source unchanged, in
platform/deployment/.local/identity-baseline/profile-fields-reviewed-y531afuh/.
474 affected tests PASS17.74s, no skips; both composers exit0; whitespace check PASS.
Three independent reviews:10/0/0 findings; one false, nine patched; no deferrals.
Every matrix row maps to executed root characterization/actual stages plus focused tests.
Final receipts cover source, secret absence, preserved2612 originals/concurrent edits,
normal retained-data native stop and scoped commit. Original7 revisions/references/pins
and all failed frames remain. No production/account/provider/access/Leave/push scope.

Normal native stop completed exit0 with retained data. Final preservation audit checks
2612 original files: none missing, seven intended existing files changed, no unexpected
changes; concurrent brainstorming memlog edits preserved. Executed source matches current
bytes. Credential-output check passes for URLs/tokens/password-bearing forms, excluding
short vendor-password coincidences in legitimate role names. Final source manifest and
reviewed diff retained. No required work remains for this bounded profile increment.
