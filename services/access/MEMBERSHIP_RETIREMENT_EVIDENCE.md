# One-way membership retirement evidence

Bounded Identity ID-B prerequisite,2026-10-20. Accepted E1 prohibits reactivation of a
retired membership through ordinary updates, seed upserts or retries. See
[Build](../../_bmad-output/implementation-artifacts/spec-id-b-membership-retirement.md),
[contract](../../platform/docs/architecture/contracts/identity-access-employment-e1.md#membership-retirement-and-rejoining--concrete-e1-design-2026-10-04)
and [runbook](IDENTITY-MIGRATIONS.md).

Revision13 changes only the existing revision-guard body. On UPDATE, a nonnull old
deleted_at cannot become null or a different instant. Refusal is23514,
identity_membership_retirement_immutable, org_member_retirement_immutable. Existing
binding/retention guards and revision rules remain; no trigger/FK/grant/role changes.
No row, initial legacy timestamp or historical revision/reference is rewritten.

This is a structural prerequisite. Existing active-to-retired SQL still works; authorized
server-time/audit/expected-revision commands and protected-writer transition are not yet
delivered. Active legacy seed upserts remain compatible. A retired-member upsert attempting
reactivation now deliberately refuses atomically, preserving the original row, roles and
evidence. Do not use legacy seeds to revive retired membership. Partial active uniqueness,
active seed lookups and fresh-ID explicit rejoin remain separate delivery items. The old
unconditional unique constraint remains. Full ID-B/Access/WRITE/server KDG stays gated.

Under ADR-0020, real-target adoption/activation still needs explicit old-writer disposition,
coordinated migration and recovery. This synthetic proof does not claim previous complete
HTTP application compatibility, provider verification or real-target cutover. No live
migration, account/access/provider changes, infrastructure/deploy/pilot, reset/prune,
Leave/editor or push is authorized. Dependency pins including TypeScript7.0.2 stay.

## Requirement-to-test evidence

| Requirement | Covering verification |
| --- | --- |
| Observe previous12 unretirement and retiming | MembershipRetirementQualification.characterize / verify_characterization; actual12 restricted login/service role; rollback only |
| Refuse clear/change retired timestamp atomically | MembershipRetirementQualification.writes / retirement_reject: direct, mixed row/CTE, seed upsert; full state comparison |
| Preserve supported behavior and authority boundary | writes / seed_compatibility / inherited read_compatibility; test_actual_seed_function_matches_qualified_membership_upsert |
| Migrate or refuse safely | upgrades_and_failures / compatibility / function_drift_refusal / failure_fixture; actual function-DDL failure witness/rollback/recovery |
| Preserve custody/source |27-file canonical previous source, independent13 reference, role/event restoration, protected source/safe outputs and retained-data stop |

## Five impact decisions

- Scaffold: extend the existing owner migration/reference/qualifier pattern; no generator,
  framework or generic lifecycle service.
- Shared UI: no consuming interface or shared component change.
- Agent context: current repository rules suffice; no AGENTS.md change.
- Documentation: owner runbook/evidence, inventory and KDG continuation record actual
  behavior, deliberate legacy-seed refusal and remaining gates.
- ADR: apply accepted E1, structural integrity and release-recovery decisions; no accepted
  ADR edits or new architecture decision.

## Verification

Initial frame: platform/deployment/.local/identity-baseline/member-retirement-_dry3272/.
Final reviewed frame: platform/deployment/.local/identity-baseline/member-retirement-reviewed-wouby7kv/.
Frozen OWNER_PYTHON=platform/deployment/.local/identity-baseline/actor-command-zxycfmc4/owner-env/venv/bin/python
(Python3.15.0). Exact final reviewed-source commands from repository root:

```bash
OWNER_PYTHON=platform/deployment/.local/identity-baseline/actor-command-zxycfmc4/owner-env/venv/bin/python
PROOF=platform/deployment/.local/identity-baseline/member-retirement-reviewed-wouby7kv
IDENTITY_QUALIFICATION_DIR="$PROOF" "$OWNER_PYTHON" -I -B services/access/tests/qualify_membership_retirement.py --characterize
"$OWNER_PYTHON" -I -B "$PROOF/run-qualification.py"
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 "$OWNER_PYTHON" -I -B -m pytest services/access/tests apps/pts/tests/test_release.py -q -p no:cacheprovider
"$OWNER_PYTHON" -B tools/py/run_compose_supabase.py --check-only
"$OWNER_PYTHON" -B tools/py/run_compose_supabase.py --identity-authority owned --check-only
```

Root alone starts/verifies the existing normally stopped native project and prepares eight
fresh scratch cases. The native alias is the inherited cluster/run/admin custody anchor;
no native domain migration occurs. Characterization runs before upgrades. Preparation
scripts are retained evidence, not repeatable commands against existing databases.
The one-time rollback-only reference recorder uses the existing qualifier branch; after
independent pinning, ordinary verification never regenerates an accepted reference.
Private credentials stay private. Actual execution/source hashes, prior source/execution,
characterization, regression, composers, review, custody and normal stop receipts remain
under the root frame. Original failures and previous frames/resources remain preserved.

Initial actual matrix PASS36.146s, source unchanged;756 affected tests PASS36.09s, no
skips. Both composer routes exit0. Previous12 characterization and independent13
reference recording PASS. Pin63543e9abe478ddc277cb00f8f241b181dd3e88c8eb29be827fc17835c3cfab0.
Historical26 source/reference files match baseline (mutable runner excluded). Three
independent review layers completed; final results are recorded below.


The source-bound previous-consumer receipt compares the actual Python seed, SQL seed,
Access reader and Expense role RPC/types to baseline c70a5d02096c3c22d582d3bd277134962bd02e51.
The CPU seed contract test executes only the real seed_org_member function AST with a
fake client, without module initialization, environment loading, account creation or
network calls. Actual database verification uses the corresponding seed-style SQL;
it does not execute full Python/Supabase HTTP seed provisioning.


The review patch adds backward/microsecond timestamp refusals, equivalent-offset noop,
three reference-reader integrity refusals and source-executed seed request checks.
The event fixture's initially uncalled sequence increments only after observing the new
retirement guard, before the injected exception; the migration must produce both safe
refusal and that witness. Fixture-only identity_migrator USAGE ends when the private
sequence is dropped. Event/function/sequence required/fired/restored witnesses preserve
custody; no production/runtime privilege changes are introduced. This marker does not
promise ordinary application sequence consumption can be reversed.


Final reviewed verification: actual matrix PASS35.569s with executed source unchanged;
all766 affected tests PASS36.76s (no skips), both composition checks exit0. The specific
injected event fired after guard replacement, its marker survived transaction rollback,
and all temporary objects were restored before successful recovery. All frozen matrix
rows ran and passed. Independent edge/gap reviews found no issues. Seven blind findings
were patched; two negligible test expansions were rejected. No findings are deferred.
Production13 SQL, generated reference and pin stayed unchanged through review patches.
Final review/custody/normal-stop receipts and reviewed-source snapshots are retained in
the final frame; initial execution/recording/characterization remain in the first frame.

Final custody audit:2653 protected paths, none missing/unexpected; eight intended existing
paths changed and original concurrent work preserved. Executed source matches current
source. Normal wrapper stop completed for99b7231c-0a5b-4bdb-98e8-3329564c526a with all
data/resources retained; native-stop.json records runtime_ready=false.
