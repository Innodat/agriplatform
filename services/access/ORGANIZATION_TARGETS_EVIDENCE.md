# Selected-organization Identity target reads — bounded ID-B evidence

2026-10-20. Build: `_bmad-output/implementation-artifacts/spec-id-b-organization-target-projections.md`.
Baseline: `48b95c9bfc8a199a84d3746c431312439b1a93e9`.

Revision7 adds only the two contract-selected internal target reads through the existing
Identity owner. Account provisioning, Access admission/grants/eligibility/public paging,
remaining membership lifecycle/hardening and full ID-B/KDG readiness remain separate.
No extra verification service, generator, dependency, browser surface or account API.

## Requirements to executed proof

| Requirement | Verification owner |
| --- | --- |
| Exact selected organization, active profile/member/org/account actor | `qualify_organization_targets.py` actual restricted-login reads |
| Ordered complete candidates/exclusive UUID cursor; exact member point binding | Same actual qualifier; focused migration/contract tests |
| Invalid/mixed/missing/nil context; user vs setup separation | Same actual read/pooled reuse matrix |
| No ordinary/browser/raw-table or role-assumption authority; fixed definer/search path | Actual role/ACL/privilege and spoof fixtures; canonical target catalog |
| Clean/adopt/head6 upgrade/no-op/drift/failure atomicity; original rows retained | Actual existing migration route and fixture matrix |
| Independent trusted reference, immutable prior source/reference pins | Extended existing reference recorder; source and preservation hashes |

Root proof: `platform/deployment/.local/identity-baseline/target-projections-2x4yhl18/`.
Native run:99b7231c-0a5b-4bdb-98e8-3329564c526a. Seven fresh scratch DBs use
`ida_99b7231c0a5b_target1_` prefix; all previous DBs/resources retained.

`previous-source.json` snapshots15 exact Git files from the baseline. The unchanged
previous owner route migrates previous/failure/unknown to head6 before any new role
staging; command/output hashes and exact interpreter are in previous-execution.json.
Actual runtime acceptance RED: missing function SQLSTATE42883 under access_runtime,
recorded in actual-atdd-red.json. Agent CPU RED precedes implementation separately.

Root stages four empty restricted NOLOGIN roles through true local supabase_admin,
with only a SET-only/non-ADMIN/non-inherited Identity definer edge to identity_migrator.
No new LOGIN, credential, Auth account, membership or application grant is created.
Role source SHA/actual flags/edge are in target-role-preparation.json. These roles are
synthetic preparation, not evidence of deployed Access wrappers or live adoption.

Initial prior-source packaging accidentally included the concurrently created new
revision7 from a filesystem glob. Git correctly refused that nonexistent old path.
Root switches to the exact Git file list, verifies every partial copied byte, and
completes the manifest. Fresh bootstrap still completed once; no resources are replaced.

## Commands, source and limits

OWNER_PYTHON is the existing frozen owner interpreter at
platform/deployment/.local/identity-baseline/actor-command-zxycfmc4/owner-env/venv/bin/python.
It retains Python3.15.0/SQLAlchemy2.1.4/Alembic1.20.0/Psycopg3.3.6/rfc87850.1.4/pytest9.1.1.
No install or lock changes; TypeScript7.0.2 and existing approved ports remain selected.

```sh
OWNER_PYTHON=platform/deployment/.local/identity-baseline/actor-command-zxycfmc4/owner-env/venv/bin/python
IDENTITY_QUALIFICATION_DIR=platform/deployment/.local/identity-baseline/target-projections-2x4yhl18 "$OWNER_PYTHON" -I -B services/access/tests/qualify_identity_baseline.py --record-target-reference
IDENTITY_QUALIFICATION_DIR=platform/deployment/.local/identity-baseline/target-projections-2x4yhl18 "$OWNER_PYTHON" -I -B services/access/tests/qualify_organization_targets.py
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 "$OWNER_PYTHON" -I -B -m pytest services/access/tests apps/pts/tests/test_release.py -q -p no:cacheprovider
"$OWNER_PYTHON" tools/py/run_compose_supabase.py --check-only
"$OWNER_PYTHON" tools/py/run_compose_supabase.py --identity-authority owned --check-only
```

Root alone performs actual fixture preparation/recording/qualification. Qualifiers
consume the existing private native fixture protocol and do not create infrastructure,
roles or credentials. New reference is recorded from exact captured known source in a
rollback-only clean DB via the existing recorder, not approved from an arbitrary target.
All prior reference files/revisions/source pins stay immutable. Access callers later
need coordinated owner delivery/role/catalog evolution; these primitives do not admit
an application or make an account/membership eligible.

Context GUCs remain trusted backend assertions. Actual restricted LOGIN/temporary fixed
function grants, when used for a fixture, are explicitly identified and exact ACL bytes
restored; no fixture convenience grants are delivered as runtime authority. No production,
hosted CI, provider callback, real-data adoption or full shared readiness is claimed.

## Five impacts

Scaffold: existing owner migration/canonical-reference/qualifier pattern; no generator
promotion or generic runtime. Shared UI: none. Agent context: existing rules suffice.
Documentation: owner runbook, evidence, Build, KDG navigation and ownership inventory.
ADR: existing ownership/actor/access/structural/release decisions govern, none changed.


## Initial actual acceptance

Existing rollback-only recorder PASS; target reference SHA256
`d6f694d575e547c1b25072d520ae7bdd540949a35a576a45e33db345398723ec`,
recorded in record-target-reference.log/trusted-reference-publication.json. Root pins
only the new constant; old references/revision sources and pins remain unchanged.

Full actual qualifier PASS24.18s (`actual-execution.json`, source_unchanged true),
with commands/safe outputs in actual-qualification.log and identity-qualification.json.
This covers103 eligible candidates, exact UUID-order/cursor and member binding, user/
setup context separation, hidden/deleted/unmapped targets, malformed typed argument
rejection22P02, current revision/retirement/deletion observations, pooled rollback/
statement-failure cleanup, search-path spoof resistance, direct definer RLS, exact
caller ACLs/ordinary runtime raw-table and role denials, fixture-only EXECUTE grant
restoration, clean/repeat/legacy/head6 upgrades, unsafe bypass/member refusal, actual
Alembic injected mid-revision rollback retaining head6, unknown history and ACL drift.
Existing legacy unretire remains characterized; revision7 does not implement new-ID rejoin.

Initial root affected suite:425 PASS9.15s, no skips (`tests-initial.log`). Both composer
routes exit0 in composer-legacy.log/composer-owned.log. A prep-only later guard codifies
the true-superuser condition root already checked before execution; it creates no new
role changes or reference/source SQL differences. Its old executed digest remains in
role preparation receipt; guard test/current source are recorded separately.

Reviewed results, review disposition, final source/protection and normal stop follow.


## Review corrections and retained qualification failure

Three independent BMAD layers completed before triage: Blind10 findings, Edge0,
Verification0. Every finding has its own verdict/evidence in the Build triage log.
Direct fixes cover guarded native UUID equality/index conditions, portable canonical
interpreter matching, actual CLI optimization refusal, complete post-record rollback
checks, protected fixture grants and private restoration witnesses, mixed-context
recovery, unexpected named defaults, exact replacement IDs and recipient unsafe rights.
No deferred work or unresolved review finding is accepted.

The new SQL reference was regenerated through its owning recorder in
`target-projections-reviewed-ae9kihms`, SHA256
`7e7dea28f7d1659b8793b7286de4dbddd7a22b81947db5644595f37e2f1299ae`.
The initial uncommitted head7 reference is retained in the original proof as
`target-reference-initial.json`, with initial source snapshots/hashes. All six historical
references/revisions/source pins remain unchanged; no generated reference is hand-edited.

First reviewed actual matrix fails22.211s at the new recipient-membership fixture,
with source_unchanged true. It grants the historical account projection owner to a new
recipient, so the existing correct earlier guard returns identity_projection_role_unsafe.
The fixture intended to reach identity_target_role_unsafe. Its finally removes the edge;
logs and original frame remain. The corrected fixture grants only access_target_reader
to access_runtime, reaching the new guard. No expected code or production guard changes.
A focused failure-path test also proves restoration when the assertion fails.

Final verification uses a fresh retained frame
`platform/deployment/.local/identity-baseline/target-projections-final-ac1ivb5x/`.
Prior exact head6 source is re-executed under the canonical interpreter; only the new
SET-only Identity target-owner edge is temporarily absent to reproduce old tooling,
then its exact administrator/options are restored in finally. Commands/log hashes and
before/after edge receipts are retained; original source is never edited.

The prep guard's actual separate refusal proof is
`preparation-refusal-actual.json` in the initial frame: nonsuperuser postgres with
CREATEROLE receives fixed42501 before mutation and all four role flags are unchanged.
The code's new guard codifies root's original true-administrator precondition.


## Final reviewed-source acceptance

Final full actual matrix: **PASS48.563s**,30 recorded steps, source_unchanged true
(`target-projections-final-ac1ivb5x/actual-execution.json`, actual-qualification.log,
identity-qualification.json). This includes all added index/replacement/default/recipient
and cleanup cases; both expected refusal and subsequent canonical reconciliation pass.
The index witness forces enable_seqscan off only to prove an available UUID index
condition under the actual definer; it is not a production performance benchmark.

Final affected regression: **432 PASS11.67s, no skips** (`affected-suite.log`). Both
composer routes exit0. Focused reviewed tests44 PASS3.03s plus the targeted restoration
regression1 PASS0.43s; the complete final432 run includes all of them. The first CPU
acceptance failure was test_target_head_is_required_and_prior_command_remains_supported
with missing TARGET_REVISION before implementation, retained in agent tool transcript.
Actual RED42883 is retained separately; no standalone CPU RED logfile is claimed.

Normal native stop completes exit0 (`native-stop.json`) with runtime_ready false and
all data retained. Final preservation-audit.json checks2605 originals: zero missing or
unexpected changes, exactly eight intended existing files changed. All historical
migrations/references/source pins, locks, prior owner/CLI sources and concurrent
Leave/PtS/Expense/brainstorming files remain intact. Actual executed source hashes still
match current files. safe-output-check.json verifies prepared credentials absent from
selected proof outputs. Final source snapshot/hash and local commit receipt are retained
in that frame. Diff whitespace check passes. All review findings are resolved; no new
deferred work. No reset/prune/resource removal, production/account/provider/access use,
infrastructure deployment, real-data pilot or push occurred.
