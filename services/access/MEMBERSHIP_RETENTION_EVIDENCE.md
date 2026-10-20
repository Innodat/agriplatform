# Retained membership history evidence

Bounded Identity ID-B prerequisite, 2026-10-20. Accepted E1 selects retained membership
instances and restrictive organization/profile/member-role references. See
[Build](../../_bmad-output/implementation-artifacts/spec-id-b-membership-retention.md) and
[owner runbook](IDENTITY-MIGRATIONS.md). Retirement/rejoin, uniqueness/seed transition,
owner commands/live-account verification and Access/WRITE/server KDG remain gates.

Revision12 replaces the three existing cascade FKs with RESTRICT after exact prior
shape checks. It extends the existing revision guard/row trigger to reject DELETE and
uses the same function from one statement TRUNCATE trigger. This closes actual legacy
service-role destructive paths without a new service/function/credential/permission.
Existing binding/revision, mutable seed/unretirement, readers and standalone trusted
legacy role DML remain. The original profile→Auth FK stays unchanged; its source is
NO ACTION, so no unsupported historical Auth cascade is assumed. This does not promise
physical account deletion, protection from owner DDL or full role-audit/lifecycle safety.

Eleven prior revisions/references/source pins, original SQL and composer output remain
immutable. No existing business row is rewritten by this migration. Supported writes
and application contracts remain separate from the deliberately refused physical
membership deletion paths. No production migration, real account/access/provider,
provision/deploy/pilot, reset/prune, Leave/editor or push is authorized by this proof.

## Requirement-to-test mapping

| Requirement | Evidence |
| --- | --- |
| Observe real history loss before12 | Actual unchanged11 direct member/org/profile DELETE and membership TRUNCATE CASCADE, synthetic rollback-only data |
| Retain active/retired/roleless and dependent history | Actual restricted access_runtime/service_role refusals; stable retention error, complete row/role/audit/history state |
| Structural restrictive references and compatibility | Exact FK definitions; parent deletion23503; original Auth FK unchanged; seed/mutable/read checks and ordinary-role denial |
| Atomic migration and custody | Clean/adopt/exact11/repeat, drift/unknown, reader-lock refusal, actual early/late DDL failure/rollback and FK drift; exact prior25 source files and only intended catalog changes |
| Isolated operational proof | Existing bounded SQL/private fixture protocol, exact SET-only role/object restoration witnesses, root-only sequential execution |

Root frame starts at platform/deployment/.local/identity-baseline/member-retention-gg7wb3qd/.
Only synthetic scratch data is used. Database execution does not prove HTTP/provider/
JWT-signature, real-target adoption or full runtime readiness. All prior frames,
receipts/state/data/resources and concurrent source documents remain retained.

## Five impact decisions

- Scaffold: extend existing owner migration/reference/recorder/qualifier pattern. No
  new generator, framework or universal soft-delete facility.
- Shared UI: no consuming UI or shared component change.
- Agent context: existing AGENTS.md instructions suffice; owner runbook and KDG next
  session record verified limits/commands and remaining work.
- Documentation: owner evidence/runbook, ownership inventory and KDG navigation record
  actual delivery, deliberate delete refusal and unproved lifecycle/activation gates.
- ADR: accepted structural integrity, membership history and migration/recovery contracts
  apply; no new decision or accepted ADR edit.

## Verification

Reviewed-source actual qualification PASS42.081s, with source unchanged. All715 affected
tests PASS30.33s (no skips); both composition routes exit0. Three independent BMAD
review layers complete; verification/documentation patches pass, with no deferrals.
Approved dependencies, including TypeScript7.0.2, stay unchanged; no root npm claim.


Initial actual11 characterization reaches42501 on TRUNCATE because service_role already
lacks that privilege. Source grants only DML there; supabase_auth_admin has existing ALL
on org/member/role. Failed diagnostics/source and exact restoration witnesses are retained.
Fixture correction preserves service-role denial and exercises truncation via the existing
Auth-role privilege in a separately recorded owner-prepared rollback lane. No privileges
or migration behavior are altered to manufacture a passing fixture.


Initial complete actual matrix PASS23.657s with source unchanged. The exact canonical11
preflight/recorder chain validates prior FK definitions before applying12. Only the three
FK definitions, existing guard body/row trigger and new TRUNCATE trigger differ. Restricted
service-role DELETE refusals, separately prepared Auth-role TRUNCATE refusals, existing
TRUNCATE permission denials, active/retired/roleless/multirow/parent preservation, original
Auth FK, seed/mutable/current readers and new12 owner-only overflow all pass. Clean/adopt/
exact11/repeat and actual first-FK replacement failure/atomic rollback/recovery pass.
Unknown remains rollback-only same-connection owner preflight; no subprocess claim there.
New12 reference SHA2566476b2210402434fd4fa732a7ab882dc8ca02cdbc694c94955647f43d696cf81.
Initial affected regression PASS695/30.17s; subsequent reviewed verification is recorded
above. Initial and corrected/failed characterization artifacts remain retained.


## Reproduction and compatibility boundary

Frozen owner interpreter (Python3.15.0):
`platform/deployment/.local/identity-baseline/actor-command-zxycfmc4/owner-env/venv/bin/python`.
The reviewed frame is
`platform/deployment/.local/identity-baseline/member-retention-reviewed-5vf899h9/`.
Its private credentials remain mode0600 and are never printed. With the retained native
project running and approved isolated scratch fixtures prepared by root, these are the
exact verification commands from the repository root (OWNER_PYTHON is the path above,
PROOF is the reviewed frame):

```bash
IDENTITY_QUALIFICATION_DIR="$PROOF" "$OWNER_PYTHON" -I -B services/access/tests/qualify_membership_retention.py --characterize
"$OWNER_PYTHON" -I -B "$PROOF/run-qualification.py"
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 "$OWNER_PYTHON" -I -B -m pytest services/access/tests apps/pts/tests/test_release.py -q -p no:cacheprovider
"$OWNER_PYTHON" -B tools/py/run_compose_supabase.py --check-only
"$OWNER_PYTHON" -B tools/py/run_compose_supabase.py --identity-authority owned --check-only
```

Characterization requires unchanged11 scratch data and runs before the matrix upgrades
other scratch cases. Bootstrap and previous-setup scripts are retained proof preparation,
not rerunnable commands against already-created databases. The first frame retains the
one-time reference recording; do not regenerate or repin an accepted reference to rerun
verification. The reviewed frame retains `characterization.log`, source-bound
`actual-execution.json`/`actual-qualification.log`, `identity-qualification.json`,
`previous-execution.json`, `auth-helper-parity.json`, both composition logs, final
regression/review/preservation receipts and the normal retained-data stop receipt.

`previous-consumer-source.json` binds five known consumer sources byte-for-byte to Git
baseline e124da80b9c0a3bbd3951d4ec1f248009502ac7d: Access membership reader, Expense
role RPC/types, Python seed upserts and SQL seed inserts. Repository caller searches
found no production physical-delete consumer. Actual12 proof exercises unchanged
reader/helper and seed SQL behavior; no previous full HTTP application binary or real
target cutover is claimed. Real-target/external writers still require explicit
compatibility disposition, coordinated migration/activation and recovery under ADR-0020;
physical deletion intentionally refuses. This local increment grants no live activation.

The private `native` target is the inherited cluster/run/admin custody anchor, not a
ninth scratch database or a domain-migration target. Eight fresh synthetic cases carry
the proof; preserved native business data is not migrated by this qualifier.


Reviewed verification also proves conflicting-reader lock refusal in7.794s (25s bound),
exact old11 catalog/data/history after both first-FK and late-trigger injected failures,
then successful recovery. Actual FK drift refuses without normalization. Multi-target
CONTINUE and owner-only RESTART truncations preserve full org/profile/member/role/audit
state and sequence last_value/is_called. Numeric-distinct live/deleted role fixtures are
validated before execution. Early/late private event objects and restricted fixture role
edges have exact restoration witnesses. Both independent edge/gap reviews found no issues;
the blind review's eight verification/documentation patches are resolved, one negligible
standard-FK concurrency expansion is rejected, and the native-custody claim is disproved.
No findings are deferred. Five impact decisions remain as recorded above.

Final custody:2647 protected paths checked, no missing/unexpected changes; seven intended
existing paths changed and concurrent original work retained. Executed source matches
current source. Normal wrapper stop completed for99b7231c-0a5b-4bdb-98e8-3329564c526a
with all data/resources retained; native-stop.json records runtime_ready=false.
