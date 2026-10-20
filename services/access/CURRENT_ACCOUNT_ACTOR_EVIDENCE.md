# ID-B restricted current-account actor evidence

2026-10-20; baseline 814bf94362a38f2687c0dc732bffac3b405b188f.
This increment adds the internal Identity SQL projection, not an HTTP endpoint,
provisioning operation or application admission. Full ID-B remains open.

## Requirement to executed verification

| Requirement / spec matrix row | Executed coverage |
| --- | --- |
| Active mapped profile without person/org | Actual access_runtime LOGIN returns exact current account/actor/display triple; synthetic org remains empty |
| Active unmapped profile | Returns account with null actor/label; full Identity row hashes unchanged by all reads |
| Missing/deleted profile or invalid context | Missing/deleted, malformed/nil UUID, absent/wrong context all return no row; uppercase canonical UUID works |
| A cannot select B through actor/org assertions | Account A with actor B/arbitrary org returns A; reader RLS also remains A under legacy service_role JWT claim for B |
| Narrow runtime and reader authority | Runtime profile/actor/mapping reads, writes, SET ROLE and function replacement deny42501; reader Auth table SELECT denies42501; browser/Auth roles lack EXECUTE; runtime/reader lack permanent schema CREATE |
| Pooled connection and definer isolation | Same actual connection with SET LOCAL context clears on next transaction; caller temp tables and malicious search_path cannot forge result |
| Clean/adopt/previous release/retry | Revision3 clean and repeat pass; original source/Supabase ledger/adopted rows/external FK definitions and values survive; exact prior committed owner code establishes head2 and existing consumer/hook behavior survives upgrade |
| Unsafe preparation/failure/unknown history | Actual BYPASSRLS and runtime-reader membership refuse unchanged; event-trigger failure after policy/grant writes rolls back catalog/rows/ledger; reconciled retry passes; unknown head refuses unchanged |
| Trusted fixture / source preservation | Separate rollback-only known-source execution records revision3 digest and pinned catalog; corruption unit checks fail closed; original revisions/references/source pins/lock remain unchanged |

The unit acceptance first observed the missing projection. Actual restricted-login
acceptance RED is retained as SQLSTATE42883 in the initial frame. Focused TDD covers
revision/read contract, fixed-reference corruption, unsafe role flags/memberships/grants,
final-head selection, exact staged-membership normalization, grant ordering and missing
Auth bootstrap. The final affected suite passes **65 tests**; both legacy and owned
composer check-only commands pass. Unit string/guard checks are supplementary; the
actual role/query matrix above establishes behavior.

## Commands and retained artifacts

Existing normal Supabase CLI run 99b7231c-0a5b-4bdb-98e8-3329564c526a;
no per-container interception or separate lifecycle. Fresh seven-case proof:
`platform/deployment/.local/identity-baseline/current-account-fixed-648cdf23/`.
Initial failed frame retained:
`platform/deployment/.local/identity-baseline/current-account-087913b5/`.
Private credentials stay private fixture inputs, never command arguments or evidence.
Existing namespace/run/loopback/port guards validate URLs before qualification.

Canonical `OWNER_PYTHON`:
`platform/deployment/.local/identity-baseline/qualification-im60qj1l/owner-env-djguxc78/offline-venv/bin/python`.
Unchanged lock/interpreter retains Python3.15.0, uv0.13.1, SQLAlchemy2.1.4,
Alembic1.20.0, Psycopg3.3.6 and pytest9.1.1; TypeScript7.0.2 is unchanged.

With IDENTITY_QUALIFICATION_DIR set to the fresh proof directory:

- `OWNER_PYTHON -I -B services/access/tests/qualify_identity_baseline.py --record-projection-reference`
  executes pinned legacy sources, original integration, actor DDL and new projection
  DDL in a rollback-only transaction. Old catalog is checked before the new DDL;
  staged empty eligibility is checked again after rollback. Exclusive publication
  creates the new fixture and its own pin, never replacing the original references.
- `OWNER_PYTHON -I -B services/access/tests/qualify_current_account_actor.py`
  completes the full actual matrix. `identity-qualification.json` records exact migration
  argv, expected safe refusal codes, results and log hashes; `complete-execution.json`
  records the successful full invocation and runner hash. `previous-source.json` and
  `previous-execution.json` bind previous-owner bytes/launcher to baseline 814bf943.
- `OWNER_PYTHON -I -B -m pytest services/access/tests apps/pts/tests/test_release.py -q -p no:cacheprovider`
  with PYTEST_DISABLE_PLUGIN_AUTOLOAD=1:65 passed. The existing `focused-checks.py`
  records exact commands/results/log hashes exclusively in this fresh directory.
- `OWNER_PYTHON tools/py/run_compose_supabase.py --check-only` and
  `OWNER_PYTHON tools/py/run_compose_supabase.py --identity-authority owned --check-only`:
  both pass; no composition output changes.

Controlled reader-role preparation executed only on this isolated synthetic cluster.
To establish the exact previous release on the fresh cases, its one newly staged
migration-owner membership was temporarily revoked then restored in finally; recorded
before/after membership is identical. This is fixture preparation, not migration behavior.
The separate synthetic Auth owner delegates schema USAGE WITH GRANT OPTION to the
migration login; revision3 itself grants only reader USAGE transactionally. No Auth
table read/write, ownership or role is conferred. controlled-preparation.json records
these facts before migration. Missing delegation refuses early with a safe identifier.

Initial actual failures are retained: SET-only membership cannot grant EXECUTE after
function ownership transfer, and the legacy PUBLIC profile policy invokes auth.role()
and needs Auth namespace USAGE. The code grants before transfer and explicitly requires
the narrow controlled Auth bootstrap. Both fixes have focused RED/GREEN and complete
fresh actual acceptance; no legacy policy/owner authority was silently widened.
The initial additional projection reference remains preserved privately. The initial pre-review
independently generated reference SHA256 was
8fc2413eb12cd0a5b46ad7829c4186ae1f143dd71852e57c47279502b8d35fa7.
No target export/approval bypass or historical expected-result replacement.

## Limits and impacts

GUCs are verified backend assertions, not authentication against compromised DB
credentials. The Access API has not adopted this projection; its legacy actor GUC
still means Auth account. No native sign-in/provider/JWT integration is claimed here.
Existing broad legacy grants are characterized, not hardened by this increment.
Actor classification/adoption/provisioning, protected operator binding/outcomes,
membership retire/rejoin, Access v2/WRITE and server KDG remain separate work.
No real account/access/provider changes, production migration, deployment or pilot.

Scaffold: existing Identity owner-local migrations/fixture, unpromoted; no new generator.
Shared UI: none. Agent context: existing actor/account rules suffice, unchanged.
Documentation: owner runbook, this evidence, mutable ownership inventory and KDG handoff.
ADR: existing0018/0020/0056 and selected substrate suffice; no accepted ADR changes.
All pre-existing receipts/state, failed frames and concurrent documents remain retained.
Reviewed completion and final preservation/lifecycle results follow.


## Reviewed completion

All three BMAD layers completed. Nine blind findings received individual triage:
eight patch groups and one false claim about integration SQL reinstalling hooks
(the fixed integration source contains only grants, restoring fixture-revoked bridge
privileges). Edge and verification-gap layers found no issues; no implementation deferred.
One additional patch removes denied Auth schema-shape rows from privilege evidence:
Identity checks effective grants, without pinning Supabase-owned schema structure.

Fresh reviewed frame:
`platform/deployment/.local/identity-baseline/current-account-reviewed-_e_mbs5u/`.
A complete seven-case actual matrix passes, including new rollback/statement-error
connection reuse and full projection authority snapshots across injected rollback.
Prior evidence now verifies all seven physical/manifest files against exact Git objects,
the committed known launcher/command, exact receipt cases and actual log digests.
The new recorder executes captured revision bytes and refuses changed helper/pins/DDL,
preserves foreign temporary files and emits a digest without rewriting helper source.
Root explicitly reconciles captured source hashes before applying the one-line pin.
Earlier emitted references and all failed diagnostics remain retained privately.

Final generated reference SHA256:
6cc6467bef0ba9c744cb53f9c2bb8542412a660c1a161f2be76fd3fa1d0a85a9.
All four upgraded cases pass full postcondition checks against final source/reference.
Additional rollback-only PUBLIC table SELECT and column SELECT grants are detected
individually by the new Auth categories, with exact snapshots restored afterward.
The initial administrator-context comparison exposed search_path-sensitive deparsing;
the corrected negative probe first verifies the baseline using the actual migration
role/path, then observes only the expected Auth privilege-category changes. No production
or real account data changed. Native Auth has 271 columns versus the five-column scratch
fixture; both have an empty effective reader grant set, proving denied shape independence.
`final-projection-checks.json` retains these results. Operational qualification is
PostgreSQL 17 only; older membership spellings remain unqualified compatibility paths.

Final **90 affected tests** and both composer check-only commands pass, recorded in
this frame's focused-checks.json. Requirement matrix rows above all have executed coverage.
Final preservation/lifecycle audit is recorded below.

Final preservation audit checks all 2564 prior files: only 7 intended
existing files changed; all 2557 others remain byte-identical, including concurrent
work. Original revisions 1/2, both old references, source pins, owner lock and Access
runtime are byte-identical to baseline 814bf943. Normal Supabase CLI stop passes;
read-only resource audit confirms its database volume, owned bridge and configuration
remain, with no active project containers. No reset, volume removal or explicit resource
cleanup was performed. Receipts: preservation.json, native-stop.json, resource-retention.json.
