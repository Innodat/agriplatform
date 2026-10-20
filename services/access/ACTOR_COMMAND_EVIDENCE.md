# ID-B protected system actor command evidence

2026-10-20; baseline8472909ed59e7aa90f4784e50c2e1e717e68977e.
This bounded increment delivers one protected actor.register_system command and scoped
original-receipt recovery through the existing Identity owner. It does not complete
ID-B, prepared-target/CLI integration, account linking, membership hardening, Access,
the broader WRITE pattern or server-backed KDG. No real account/provider/access change.

## Requirement-to-test traceability

Every row of the Build matrix maps to executed checks below. The actual qualifier uses
identity_operator LOGIN, never a migrator success presented as runtime authorization.

| Requirement / matrix row | Executed verification |
| --- | --- |
| New system/service registration, atomic attribution and receipt | CommandQualification.command_matrix: actual operator LOGIN, Unicode/control display text, system+service, normalized UUID replay, server creation/update actor/time, exactly one actor/outcome/event |
| No-op and id/key/kind/label conflicts | Same method: new unchanged outcome/no event; each differing registration conflicts; original receipt survives controlled later label update |
| Same operation/changed payload/lost acknowledgement | Same method and lost_acknowledgement: original replay, fingerprint conflict, actual PostgreSQL commit followed by simulated lost acknowledgement, original lookup and retry recover same receipt |
| Concurrent duplicates/different operations/domain conflicts | two_executor_matrix: actual distinct original logins, same operation UUID scoped independently, held locks and both backend/blocker witnesses, created+unchanged for same target, created+conflict for shared ID/different key and shared key/different IDs; exact temporary grants restored |
| Current authority and configuration races | Same method and authority_serialization: unmapped/disabled/wrong-command-only principal, principal+authority disable/re-enable, execute/lookup denial, actual advisory waiter for new execution, replay and lookup, then committed revocation and fresh denial with evidence unchanged |
| Canonical forgery/GUC/search path/foreign session | isolation_and_forgery: forged canonical bytes, spoofed actor GUC/temp objects/search path, SET ROLE from unmapped original migrator session; no executor substitution |
| Unknown versions/missing result/uncertain commit | structural_evidence exercises command/result/fingerprint versions and algorithm retention; missing lookup returns unresolved None; lost_acknowledgement proves commit uncertainty, not rollback |
| Alternate writes, integrity and immutable evidence | isolation_and_forgery and structural_evidence: raw reads/writes/DDL/role assumption denied, UPDATE/DELETE/TRUNCATE guards, separately isolated FORCE-RLS/CHECK and physical FK23503, valid event control plus singly invalid target/outcome/executor/transition linkage |
| Failure/deadline/wait/pool reuse | timeouts_and_atomicity: exact outcome wait gives busy, domain/authority waits unavailable, injected outcome/event failure rolls back all effects; failure_connection_reuse observes actual57014 cancellation/atomic rollback and the same backend/defaults/identity/recovery after conflict, busy and event failure; test_identity_operator.py checks delayed-setup budget refresh and safe uncertain commit errors |
| Migration clean/adopt/prior-head5/repeat/unsafe/drift/rollback | upgrades_and_failures: exact prior committed source/interpreter evidence, preserved old rows/member hashes and external state, clean+adopt+prior upgrade/repeat, unknown history, unsafe LOGIN/PUBLIC database CREATE, injected revision6 DDL failure rollback and reconciliation, ACL drift refusal/reconciliation |
| Reference/source custody and preparation | --record-command-reference: captured-source rollback-only generation and exclusive publication; test_actor_command_qualification.py checks every source mutation/no overwrite/no auto pin/private permissions; actual preparation success plus nonsuperuser42501/existing-name42710 refusal |

## Commands, targets and receipts

OWNER_PYTHON is the fresh locked interpreter:
`platform/deployment/.local/identity-baseline/actor-command-zxycfmc4/owner-env/venv/bin/python`.
Exact Python3.15.0/uv0.13.1; only approved rfc8785==0.1.4 was added through the existing
owner manifest/lock. Fresh offline frozen/no-build sync passes; every previous locked
package record remains identical. dependency-proof.json and lock-check.log retained.
TypeScript7.0.2 and all other approved pins remain unchanged; no older environment removed.

Initial frame: platform/deployment/.local/identity-baseline/actor-command-zxycfmc4/.
Intermediate frame: platform/deployment/.local/identity-baseline/actor-command-full-jc809src/.
Final pre-review frame: platform/deployment/.local/identity-baseline/actor-command-final-y2n1fdt9/.
Native run99b7231c-0a5b-4bdb-98e8-3329564c526a resumed with existing dev.py up, explicit
kdg-local target and retained CLI2.120.0. Scratch databases are fresh command1_/2_/3_
namespace on the isolated loopback target. Prior frames/databases/resources are retained.
Private credentials remain mode0600 configuration, never command argv or diagnostic dumps.

- `OWNER_PYTHON -I -B <initial-frame>/actual-red.py`: actual restricted operator on exact
  prior head5 gets42883 for both missing routines, no writes; actual-acceptance-red.json.
  Focused adapter acceptance first observed missing-module RED before implementation.
- `OWNER_PYTHON -I -B <initial-frame>/record-reference-attempt5.py`: independent ignored
  owner copy runs existing --record-command-reference recorder, captured source revisions
  1–6, all original references/pins and helper identity, rollback-only on command_reference.
  Generated bytes published exclusively, then new pin manually set to
  ebe11f9cd4dbed35496488e6eb21b5c6af4c3c8f767447fd1e1ad7fb2c2c1188.
  Repository original reference bytes and pins remain unchanged. trusted-publication.json.
- `OWNER_PYTHON -I -B services/access/tests/qualify_actor_command.py` with
  IDENTITY_QUALIFICATION_DIR bound to the final frame:24 named stages pass112.925s.
  actual-qualification-execution.json captures exact command, unchanged source hashes,
  log hash and exit0. Expected refusal subprocess exits are verified PASS stages.
- Exact prior-head5 preparation independently copies13 files from baseline8472909,
  compares them to git show, and actually executes unchanged source with the existing
  independently locked prior interpreter. Only the new SET-only command-owner edge is
  temporarily unstaged/restored for old code. Previous-source/execution/log evidence and
  prior-release-role-staging.json retain this; no old source or permission check relaxed.
- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 OWNER_PYTHON -I -B -m pytest services/access/tests apps/pts/tests/test_release.py -q -p no:cacheprovider`:328 passed12.27s, no skips.
- `OWNER_PYTHON tools/py/run_compose_supabase.py --check-only` and
  `OWNER_PYTHON tools/py/run_compose_supabase.py --identity-authority owned --check-only`:
  both pass, preserving existing composer routes. Initial-frame composer logs retained.

## Corrections and retained failures

Root initially omitted source-pins.json from its prior-source fixture, then used the
new interpreter where the existing evidence contract requires the exact prior one;
a subsequent exclusive receipt publication found an existing file. Corrected fixture
packaging/interpreter/receipt paths preserve all originals and actual source unchanged.

Rollback-only recording caught SQLAlchemy parsing fixed JCS :true as a bind and psycopg
rewriting raw %s literals. Trusted fixed SQL now uses exec_driver_sql with no_parameters.
A subsequent42501 required the original authority function owner to delegate its exact
EXECUTE grant using SET LOCAL ROLE/RESET ROLE. Rehearsal then passes. No privilege check
or canonical input expectation was relaxed; all failed source copies/logs remain.

Actual alternate-write test initially expected CHECK23514 where forced RLS correctly
refused42501 first. The corrected fixture proves RLS and CHECK separately, preserves
physical FK23503 assertions without unique-key masking, and tests each event field
against a valid matching pair without deferred-event masking. No production guard changed.

The first authority-race observer retained PostgreSQL activity-statistics snapshot before
the worker connected. Explicit snapshot refresh fixes observation; supplemental actual
serialization/lost-ack checks and final fresh full matrix pass. Original failing source-
bound frame/log remains. These passes explain fixture errors, not removal of evidence.

## Impacts and limits

Scaffold: existing owner-local migration/command/recorder/qualification pattern; no generic
promotion, generator or new service. Shared UI: none. Agent context: existing rules suffice.
Documentation: owner runbook, evidence, build record, navigation/inventory. ADR: existing
ownership/release/actor/structural/logging/WRITE decisions govern; no new or edited ADR.

The ten-second monotonic operation budget and server SQL≤5s/lock≤2s settings do not impose
a wall-clock return bound on a stalled synchronous supplied connection or commit reply.
The prepared caller owns bounded transport configuration; that integration remains gated.
Missing/unavailable outcomes do not authorize a new operation identity. No physical network
failure, provider sign-in, real operator adoption, production release or full ID-B readiness
is claimed. No implicit credentials/targets, expiry, retries, migrations or cleanup.

## Reviewed-source acceptance

Three independent BMAD layers completed (launched as agent capacity allowed, with triage
after all reports). Edge hunter: no findings. Blind hunter:10 findings, one refuted because
the fixed trusted routines always return exactly four columns; nine direct patches.
Verification reviewer: two confirmed gaps, resolved with the same revocation patch and
exact stored audit-field assertions. Every finding has an individual verdict/evidence in
the Build triage log; no deferred work or unresolved finding.

Reviewed frame: platform/deployment/.local/identity-baseline/actor-command-reviewed-hux72mlh/.
Exact source-bound full qualifier:27 named stages PASS42.639s. Full affected suite:
330 PASS1.98s, no skips. Both composition commands pass again on reviewed source.
The runtime patch refreshes the SQL budget and checks the monotonic deadline immediately
before business dispatch; delayed configuration reply tests prove expired setup dispatches
no business SQL. The caller-owned transport/commit limitation above remains explicit.

Additional actual proof: existing synthetic access_runtime login temporarily receives
only the two fixed wrapper grants in the fresh scratch DB, with protected explicit
principal/authority fixture rows. Original schema/function ACL bytes are restored exactly,
and that fixture authority is disabled. No new login, credential or real application
access is created. Same operation UUID produces independent scoped receipts; foreign-only
lookup remains unresolved. Forced two-backend/blocker witnesses cover same operation,
same target, shared key and shared ID. Replays/lookups wait behind both principal and
authority revocation and deny disclosure afterward. Slow synthetic trigger yields57014;
rollback plus same physical connection/defaults/identity/SELECT/recovery is verified.
Python JCS versus stored server SHA256 covers quote/backslash/control escapes,2028/2029,
supplementary and non-normalized text; nondefault reason/present ref persist exactly.

All previous frames, failures and source snapshots remain intact. Final source custody,
protected-file preservation and normal-stop receipts are retained in the reviewed frame.

Final preservation:2588 original nonignored files checked; exactly ten intended existing
files changed, no unexpected changes. Original migrations/references/pins, concurrent
Leave/PtS/Expense/brainstorming content, all prior receipts/state and Docker resources
remain preserved. Reviewed-source hashes still match actual execution. Native stop
completed exit0 with data retained; no reset, prune or cleanup. Diff whitespace check passes.
