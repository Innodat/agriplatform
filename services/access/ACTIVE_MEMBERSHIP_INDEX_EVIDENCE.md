# Staged active-membership index evidence

Bounded ID-B prerequisite,2026-10-20. See
[Build](../../_bmad-output/implementation-artifacts/spec-id-b-active-membership-index.md),
[E1](../../platform/docs/architecture/contracts/identity-access-employment-e1.md#membership-retirement-and-rejoining--concrete-e1-design-2026-10-04)
and [runbook](IDENTITY-MIGRATIONS.md).

Revision14 adds only UNIQUE btree index org_member_active_org_user_uidx on
identity.org_member(org_id,user_id) WHERE deleted_at IS NULL. It retains the original
org_member_org_id_user_id_key and its full unique index, all rows/guards/roles/readers,
source history and seed behavior. This is compatible expansion under ADR-0020; canonical14
still forbids historical duplicates. It does not deliver rejoin or final E1 replacement.

The existing Python seed sends only an on_conflict column list through the installed
PostgREST client. Removing the full constraint now would break its upsert. A read-then-
insert replacement could implicitly rejoin a retired member and race another writer.
Do not invent a seed RPC or new command engine to bypass the accepted owner lifecycle.
Retain the existing full constraint until authorized owner commands, seed/provisioning
lookups and previous-writer compatibility/recovery are coordinated. Current SQL seed's
unqualified lookup and integration deleted_at SELECT privileges also require deliberate
transition. No old seed is used to revive retired membership.

## Requirement-to-test evidence

| Requirement | Verification |
| --- | --- |
| Actual13 baseline | Characterization binds canonical13 inventory, original unique constraint/backing index/dependencies, missing new index, legacy active seed and retired-duplicate refusal |
| Add only the intended index | Exact canonical snapshot/reference delta; full original unique constraint retained; unchanged rows, functions, ACLs and triggers |
| Partial-index behavior independently of original constraint | Owner-prepared rollback-only removal without CASCADE, SET service_role writes, named new-index23505, multiple retired histories and no role copying, exact final restoration |
| Staged actual concurrency | Two independent restricted logins/SET service_role; observed blocking, one retained committed synthetic member, safe loser23505 under coexisting protections |
| Release/custody safety | Clean/adopt/exact13/repeat, drift/unknown, actual index-DDL failure marker/atomic rollback/restoration/recovery,29 previous source files, protected paths/safe output |

The isolation lane is owner-prepared synthetic DDL, never restricted-login DDL or an
application rejoin command. It restores the original full constraint/data by rollback.
The concurrency lane retains both constraints: its23505 may name either index and does
not claim isolated-partial-index attribution. Exactly one new winner is deliberately
retained as synthetic fixture data; original rows/roles remain. No live account/Auth
provider/JWT-signature/HTTP application or full runtime qualification is claimed.

## Five impact decisions

- Scaffold: existing owner migration/reference/qualification pattern; no new generator,
  framework, generic lifecycle service or unaudited seed RPC.
- Shared UI: no interface/component consumer in this prerequisite.
- Agent context: current repository rules suffice; no AGENTS.md edit.
- Documentation: owner evidence/runbook/inventory and KDG continuation record staged
  limits, actual proof and remaining command/seed gates.
- ADR: accepted E1 and ADR-0020 staged compatibility apply; no accepted ADR edits.

## Verification

Initial proof: platform/deployment/.local/identity-baseline/active-member-index-a5wfxm1j/.
Reviewed proof: platform/deployment/.local/identity-baseline/active-member-index-reviewed-_dfnt87r/.
Frozen owner Python3.15.0 and approved dependencies including TypeScript7.0.2 unchanged.
Exact commands from repository root, with the private synthetic frame prepared by root:

```bash
OWNER_PYTHON=platform/deployment/.local/identity-baseline/actor-command-zxycfmc4/owner-env/venv/bin/python
PROOF=platform/deployment/.local/identity-baseline/active-member-index-reviewed-_dfnt87r
IDENTITY_QUALIFICATION_DIR="$PROOF" "$OWNER_PYTHON" -I -B services/access/tests/qualify_active_membership_index.py --characterize
"$OWNER_PYTHON" -I -B "$PROOF/run-qualification.py"
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 "$OWNER_PYTHON" -I -B -m pytest services/access/tests apps/pts/tests/test_release.py -q -p no:cacheprovider
"$OWNER_PYTHON" -B tools/py/run_compose_supabase.py --check-only
"$OWNER_PYTHON" -B tools/py/run_compose_supabase.py --identity-authority owned --check-only
```

Root prepares eight fresh scratch cases through existing private fixture protocol. The
native alias anchors run/admin custody; no native domain migration occurs. Characterize13
before upgrades. Bootstrap/previous-setup are retained preparation scripts, not rerunnable
against already-created databases. Record the independent14 reference once through the
existing rollback-only recorder, inspect/pin it, and never regenerate accepted references
for routine verification. Preserve all29 canonical previous py/json source files from
0e460f65afd8e92c32b974412d0ea648f915eced (mutable runner changes only in current tree).
Retain exact required/fired/restored fixture witnesses and original frames/resources;
ordinary sequence consumption is not reversible. Private credentials are never printed.
Actual source hashes, characterization, matrix/regression/composition/review/custody and
normal stop receipts are retained below the frame. No root npm verification claim.

Initial actual matrix PASS42.258s, source unchanged;834 affected tests PASS41.56s no
skips; both composers exit0. Three independent review layers completed; final results below. No production migrations,
accounts/access/provider, infrastructure/deploy/pilot, reset/prune, Leave/editor or push.


Initial characterization TypeError came from driver Row serialization after rollback/role
restoration; focused real-Row coverage now protects JSON publication. The failed log/source
and partial witness stay retained. Root pin inspection initially overlooked the index
pg_class relation; an unpinned attempted upgrade refused and rolled back to13 with no
new index, confirmed read-only. Canonical14 adds exactly one index row and one relation
row, with exact name/kind/owner/flags/ACL/options. Corrected pin:
b710b943ecb95e4b7cbce9eb77debad8f1ad181c40a2532ff87cd85be317033b.


The complete matrix is single-use once its concurrency winner commits. Rerunning against
the same spare org/account deliberately refuses; a matching witness is not automatic
adoption or replay authority. Preserve its required/result receipts and row, inspect
uncertain outcomes without mutation, and prepare fresh scratch cases for another proof.
Do not reset/delete a winner or invent resume/reconciliation behavior to make a repeat
pass. Final verification uses the separate reviewed frame, retaining the first winner,
initial failed records and all original data/resources.


Final reviewed verification: source-bound actual matrix PASS46.265s, source unchanged;
all846 affected tests PASS38.42s, no skips; both composer routes exit0. Observed writer
lock caused bounded migration refusal in7.746s with old13 state retained, then index-DDL
injection/fired-marker/rollback/restoration/recovery passed. Missing/wrong-predicate index
preflight refused without normalization in rollback-only direct-owner lanes; no subprocess
or invalid-catalog fabrication claim. Multirow partial-index refusal rolled back its valid
row too. Replacement retirement/new active insertion retained all history/roles in the
rollback-only lane. Concurrent canonical inserts observed blocking and retained one new
fixture winner; loser23505 named the original full unique constraint.

Focused failure-path tests prove loser startup, unobserved blocking and commit failure
release winner/worker/fixture state. Observer polling yields up to20ms between queries;
actual pg_blocking_pids proves ordering. Catalog branch tests prove every role/privilege
guard precedes comparison and each refusal stops it. Test sources/methods:
ActiveMembershipIndexQualification.characterize/compatibility/index_isolation/concurrency/
blocked_index_ddl/index_drift_refusal/upgrades_and_failures and
services/access/tests/test_active_membership_index.py. Existing retirement writes/read/
seed/retention checks run unchanged under14.

Three independent BMAD layers complete. Nine blind findings were addressed by focused
verification/documentation patches; the requested duplicate upgrade-call unit test is
disproved as a gap by required actual migration routes. Edge/gap layers found no issues.
No findings are deferred. Production14 SQL/reference/pin remained unchanged through
review. Initial failures/partial witnesses and first winner stay retained. Final source,
review/regression/composition/custody/stop receipts and snapshots are in the reviewed frame.

Final custody:2659 protected paths, none missing/unexpected; seven intended existing
paths changed and original concurrent work retained. Executed source matches current
source. Normal wrapper stop completed for99b7231c-0a5b-4bdb-98e8-3329564c526a, retaining
all data/resources and both initial/reviewed synthetic winners; runtime_ready=false.
