---
title: Enforce one-way membership retirement
type: bugfix
created: '2026-10-20'
status: done
route: dispatch
review_loop_iteration: 0
baseline_commit: c70a5d02096c3c22d582d3bd277134962bd02e51
context:
  - /home/ck/repos/innodat/agriplatform/AGENTS.md
  - /home/ck/repos/innodat/agriplatform/platform/docs/architecture/contracts/identity-access-execution-substrate.md
---

<frozen-after-approval reason="standing bounded shared implementation approval">

## Intent

Prevent a retained retired membership from becoming active again or acquiring a different
retirement timestamp through ordinary UPDATE, seed upsert or retry. This implements the
accepted E1 null-to-retired invariant before owner retirement/join commands. Add13 after12
through the existing Identity migration/reference/qualification owner.

## Boundaries & Constraints

Extend the existing guard with a stable23514 error identity_membership_retirement_immutable,
constraint org_member_retirement_immutable, when UPDATE has OLD.deleted_at nonnull and
NEW.deleted_at IS DISTINCT FROM OLD.deleted_at. Preserve original binding/retention and
revision semantics, function identity/owner/ACL/search_path/invoker and both triggers.
Do not rewrite any row, old revision/reference/pin, unique constraint, seed or reader.
A live member may still undergo the existing null-to-retired write; existing initial
legacy timestamps are preserved. This is a structural prerequisite, not a new authorized
retirement API: server-time/audit/expected-revision owner commands, protected-writer
transition, partial active uniqueness, explicit fresh-ID rejoin and active seed lookups
remain gated. Legacy upserts against active membership still work; attempts to revive a
retired membership must fail atomically rather than overwrite it. Document that deliberate
refusal and retain real-target activation/previous-writer disposition under ADR-0020.
No new credential/service/framework/generator, dependency changes, Leave/editor, real
accounts/access/provider, production/provision/deploy/pilot, reset/prune or push.

## I/O & Edge-Case Matrix

| Scenario | Expected |
| --- | --- |
| Actual unchanged12 unretire or retime a retired member | Observe gap in rollback-only synthetic transactions before13 |
|13 retired member clear/change timestamp, mixed multirow/CTE, seed-style upsert | Stable refusal and complete row/role/audit/history preservation |
|13 unchanged retirement/noop, active update/seed and null-to-retired | Existing binding/server revision/reader behavior; original timestamp retained on noop |
| Ordinary authenticated/runtime direct protected writes | Existing42501 denial; no new role edge or privileges |
| Clean/adopt/exact12/repeat, unknown/drift, injected migration failure | Exact new function-only catalog delta or old catalog/history/data unchanged |

</frozen-after-approval>

## Code Map

Existing versions/0012_membership_retention.py is immutable source. Add
services/access/identity-migrations/versions/0013_membership_retirement.py using only
CREATE OR REPLACE guard; reuse full12 function and insert one UPDATE check after binding
validation before revision calculation. No trigger/FK SQL in13.
identity_baseline.py extends current independent trusted reference chain/head; preserve12
as supported historical. qualify_identity_baseline.py adds one branch to existing recorder
by following12 known-source rollback and exclusive-publication pattern, verifying12 before13.
New membership-retirement-reference.json starts absent and only root records/pins it.
Reuse qualify_membership_retention.py/binding/Profile private fixture, role restoration,
exact source witness and migration helper. Prefer small retirement subclass rather than
another generic harness. Existing retention fixture keys and nine-case protocol may be
reused, with membership_retirement_reference replacing only reference-case name.
Previous canonical commit c70a5d02096c3c22d582d3bd277134962bd02e51 has27 owner py/json files (root verifies actual count).

## Tasks & Acceptance

- [x] Child: focused test_membership_retirement.py observes missing13/head RED first;
implement new revision, baseline/head/reference chain/recorder and targeted CPU tests.
Adjust previous retention test to regard12 as historical and13 as required head.
- [x] Child: qualify_membership_retirement.py characterizes actual12, verifies exact
function-only delta, one-way retirement/refusal and preserved active seed/read/binding/
retention behavior, clean/adopt/previous/repeat/failure/drift/unknown. Actual failure uses
existing private event-fixture pattern raising after CREATE FUNCTION, exact rollback and
successful recovery. Do not run DB/Docker; root alone supplies fixtures/reference/pin.
- [x] Root: record independent13 reference and actual characterization/matrix, run affected
suite and both composers, three reviews, source/custody/safe-output audit, normal retained-
data stop, five impact decisions and requirement-test evidence in owner runbook/evidence,
KDG navigation/inventory, then scoped local commit. Child only edits code/tests; root owns
documentation/spec/proof/lifecycle/pin.

Given a retired member, when any supported direct write changes its retirement timestamp,
then it refuses atomically. Given active/upsert/read/noop paths, then unchanged supported
behavior remains. Given failed migration, then activation blocks and previous state stays.

## Implementation Notes

No intent gap; E1 explicitly prohibits unretirement through update/seed/retry. Only isolated
synthetic DDL/data is authorized; live activation remains gated. Existing dirty concurrent
work is protected under standing approval. Reuse owner tooling with no public interface.
Approved dependency pins including TypeScript7.0.2 remain unchanged.

## Spec Change Log

## Review Triage Log

| Finding | Verdict | Evidence and route |
| --- | --- | --- |
| Blind1 two-session retire/update/upsert | low | One-way enforcement is an ordinary row trigger over the locked row's OLD/NEW values; there is no application check-then-act path. Current matrix proves retired-write refusal. Adding committed-data recovery/two-session machinery for standard PostgreSQL row serialization has negligible benefit here; reject under low-finding complexity rule. |
| Blind2 backward/subsecond retirement | low | Actual matrix only changes forward by one second. Add two direct statement cases to demonstrate those inputs with the existing full-state checks; patch. |
| Blind3 equivalent-offset noop | low | Existing noop is self-assignment, so different representations of an equal instant are not recorded. Add one equivalent-offset timestamp write asserting complete row/revision equality; patch. |
| Blind4 production seed binding | medium | SQL matches current seed payload by root inspection and source receipt, but no checked-in test fails if that payload changes. Patch CPU test to execute only the actual seed_org_member AST function with a fake client, checking schema/table/payload/conflict target against the qualified contract; never import its credential-bearing top level. |
| Blind5 injected failure identity | medium | Generic safe migration refusal and successful recovery do not independently identify the firing point. Patch the private event fixture with one rollback-independent sequence witness, exact fixture-only permissions/restoration, and require its increment before claiming injected failure. No production diagnostic relaxation. |
| Blind6 function lock test | low |13 only replaces an existing function and reuses the unchanged bounded owner environment. No demonstrated blocking writer/caller failure or new timeout policy is identified. A new artificial system-catalog/function-lock harness adds complexity for negligible routine benefit; reject under low-finding complexity rule. |
| Blind7 reference integrity branches | medium | New reference reader tests exercise trusted success and migration drift but do not individually exercise missing/mutated reference and source-pins mismatch. Add focused refusal cases; patch. |
| Blind8 executable assignments | low | Prose gives exact paths but command block omits assignments. Direct root documentation patch. |
| Blind9 pending completion prose | low | Reviews/custody/stop were genuinely pending at review snapshot. Finalize receipts and navigation before completion; root documentation patch. |

Edge-case layer returned no findings; verification-gap layer found no gaps. Host thread
capacity required sequential review children; all three completed before triage and no
layer was skipped. Seven findings route to private-test/documentation patches, two low
complexity expansions rejected; no deferrals and no production SQL changes.

## Verification

OWNER_PYTHON=platform/deployment/.local/identity-baseline/actor-command-zxycfmc4/owner-env/venv/bin/python.
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 "$OWNER_PYTHON" -I -B -m pytest services/access/tests
apps/pts/tests/test_release.py -q -p no:cacheprovider. Run smallest RED/focused first.
Both tools/py/run_compose_supabase.py --check-only routes (default and --identity-authority
owned). Root source-bound synthetic matrix, previous-source hashes, every matrix row
covered/run, role/object restoration, protected paths and safe logs, normal stop. No root
npm or full HTTP/provider/live-target readiness claim. Five impacts: existing owner pattern
extends scaffold; UI has no consumer; agent context sufficient; owner/navigation docs
updated; accepted ADRs unchanged.

Initial verification: focused RED2 missing13/head; child107 focused CPU PASS. Actual12
characterization PASS; independent13 recorder PASS/pin63543e9abe478ddc277cb00f8f241b181dd3e88c8eb29be827fc17835c3cfab0.
Actual full matrix PASS36.146s source unchanged,756 affected tests PASS36.09s no skips,
both composers exit0. Every frozen matrix row ran/passed. Three review/custody/stop
completion follows. Historical26 immutable source/reference files match baseline.


Final reviewed verification: child51 focused retirement tests PASS. Fresh reviewed frame
platform/deployment/.local/identity-baseline/member-retirement-reviewed-wouby7kv/:
actual12 characterization PASS; full matrix PASS35.569s source unchanged; specific
post-function-install event marker, rollback/restoration/recovery PASS. All766 affected
tests PASS36.76s no skips; both composers exit0. All matrix rows verified. Three review
layers complete; seven findings patched, two low complexity expansions rejected, none
deferred. Production13 SQL/reference/pin unchanged through review. Exact commands and
requirement-to-test mapping/five impacts are in owner evidence. Final custody/normal
retained-data stop and scoped local commit receipts follow under that frame.

Final custody audit:2653 protected paths, none missing/unexpected; eight intended existing
paths changed and original concurrent work preserved. Executed source matches current
source. Normal wrapper stop completed for99b7231c-0a5b-4bdb-98e8-3329564c526a with all
data/resources retained; native-stop.json records runtime_ready=false.
