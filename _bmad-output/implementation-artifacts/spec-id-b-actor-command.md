---
title: Protected system actor registration with durable recovery
created: '2026-10-20'
type: feature
status: done
route: dispatch
review_loop_iteration: 0
baseline_commit: 8472909ed59e7aa90f4784e50c2e1e717e68977e
context:
  - /home/ck/repos/innodat/agriplatform/AGENTS.md
  - /home/ck/repos/innodat/agriplatform/platform/docs/architecture/contracts/identity-access-execution-substrate.md
  - /home/ck/repos/innodat/agriplatform/platform/docs/architecture/contracts/owned-write-and-secret-execution.md
---

<frozen-after-approval reason="standing bounded implementation approval">

## Intent

Deliver one complete protected `actor.register_system` command: an authorized operator
can register a system/service actor and recover its original compact committed receipt.
Use the existing Identity migration owner, strict parser, and private SQL routines with
a thin owner-local Python adapter; prove actual restricted-login atomicity and retries.

## Boundaries & Constraints

Preserve source revisions1–5, original references/pins, prior receipts/state/resources,
concurrent documents and existing behavior. Add identity_0006 through the current chain.
No seeds, real accounts/access/provider changes, generic CLI/target-preparation engine,
account ensure, membership implementation, Access/WRITE-wide framework, KDG/Leave/editor,
new service/generator or production/deployment. No automatic migrations/downgrades.

Adapter `services/access/identity_operator.py` exposes execute(connection, body:bytes)
and outcome(connection, operation_id). Caller supplies explicit trusted prepared target's
idle SQLAlchemy Connection; no implicit target/credentials/checkout. Only register_system
executes; parser's other commands reject before SQL. Frozen typed compact receipts;
acknowledge only after commit; missing outcome means unresolved, never proven failure.
Current original-session login authority required on execution, replay and lookup.
Initiator null until a separate verified surface exists. No payload/GUC/SET ROLE executor.

Implement fixed SECURITY DEFINER register and outcome routines, fully qualified objects,
search_path pg_catalog,pg_temp, READ COMMITTED only. New restricted NOLOGIN NOINHERIT
identity_command_owner, sole migrator SET-only/non-admin membership, true-superuser
preparation refusal before CREATE. Operator has fixed EXECUTE only, no raw business DML,
DDL, authority-map editing or owner assumption. Owner gets selected actor SELECT/INSERT,
outcome/event SELECT/INSERT and existing authority read only. Preserve account-map guard.
Narrow actor guard to authorize this owner's system/service INSERT with server-derived
executor/timestamps; migrator compatibility remains, no command-owner UPDATE/delete.

Use newer WRITE exact identity.operation_outcome/business_event fields and full scoped
NULLS NOT DISTINCT uniqueness, immutable guards, local RESTRICT actor/outcome FKs,
strict compact typed results/event linkage and bounds. Only platform/register rows now;
no fake org, profile/label payload event or automatic expiry. ENABLE/FORCE RLS with
original-session current executor/platform policies for command owner, migrator inspection
policy for existing data_state capture. Atomic actor + outcome + event; unchanged identical
id/key/kind/display returns new unchanged outcome without event. Any differing registration
conflicts. Original replay result survives later controlled label changes. Unsupported
stored versions/algorithms are retained and verification-unavailable, never treated missing.

Python rfc8785==0.1.4 computes normalized-UUID JCS of the complete typed v1 command,
including evidence_ref:null when absent. SQL reconstructs this ONE fixed command envelope
from typed args (Postgres string quoting) and compares exact canonical UTF8 bytes, then
server pg_catalog.sha256; never trust supplied digest. Test Unicode/control fixtures.
Outcome transaction lock follows WRITE's exact v1 JCS→SHA256→first8 signed-big-endian64.
Acquire outcome lock before outcome reads; deterministic actor-id/key domain locks and
structural uniqueness arbitrate different operations. Only that exact outcome lock
wait maps operation_busy; domain lock/other timeout stays safe unavailable/uncertain.

Serialize authority configuration and invocation using the same transaction advisory
lock per original database_login (SHA256 of UTF8 identity:operator-authority:v1:<login>).
Revision6 replaces authority config guard preserving old semantics and acquiring this
lock; execute resolves preliminary executor, outcome lock, authority lock, then fresh
authority recheck before effects/replay. Lookup locks/rechecks authority before disclosure.
No network waits. Bound monotonic execution10s including parsing, SQL statements≤5s,
locks≤2s capped by remaining budget; reject busy connection/unsupported isolation.
Transaction-local settings clear on commit/rollback; unknown errors expose fixed safe
codes without SQL/driver values/chains. Transport/commit uncertainty preserves operation
identity and never promises rollback.

## I/O & Edge-Case Matrix

| Scenario | Expected behavior |
| --- | --- |
| Actual authorized operator LOGIN / new system or service | Server attribution; exactly one actor/outcome/event; committed receipt only after commit |
| Identical existing registration / different id,key,kind,label | unchanged receipt/no event / conflict/no effects |
| Same operation replay, changed payload, lost acknowledgement | Original receipt once / conflict / original lookup recovers |
| Concurrent same op, different op same target, outcome lock timeout | One effect, scoped outcomes; deterministic no-op/conflict; bounded operation_busy only for outcome lock |
| Disabled/unmapped/wrong-command principal, revoke before lookup/replay, competing configuration | No disclosure/effects; fresh authority serialized with config |
| Forged digest/canonical input/GUC/SET ROLE/search_path, foreign login | Reject; original authenticated identity governs |
| Unknown receipt versions, missing lookup, failed commit/transport | Verification unavailable / unresolved / truthful unknown outcome |
| Malformed args, alternate raw writes, wrong actor/outcome linkage, UPDATE/DELETE/TRUNCATE | Structural and privilege refusal, no changed retained evidence |
| Injected event/outcome failure, deadline/domain timeout, reused connection | Atomic rollback or explicit uncertainty; no leaked transaction context |
| Clean/adopt/prior-head5/repeat/drift/unsafe/failure | Exact new catalog; old data/source preserved; unsafe state refuses atomically |

</frozen-after-approval>

## Code Map

- services/access/identity_operator_input.py — strict immutable parser; reuse unchanged.
- services/access/identity-migrations/identity_baseline.py, versions/0001…0005 — existing source/canonical chain; immutable sources; staged role normalization needed for old references.
- services/access/tests/qualify_identity_baseline.py — captured-source rollback-only exclusive private reference publication; extend for command-reference.json, no auto pin.
- services/access/tests/qualify_operator_authority.py — reuse actual frames/login/upgrade/refusal patterns; add qualify_actor_command.py through existing inheritance, no new lifecycle runner.
- services/access/tools/prepare_identity_operator_roles.sql — safe true-admin preparation pattern.
- platform/deployment/.local/identity-baseline/actor-command-zxycfmc4 — root private frame/protected-before.json; all earlier frames retained.

## Tasks & Acceptance

- [x] services/access/tests/test_identity_operator.py — observe acceptance RED, focused adapter/fingerprint/timeout/error tests; record exact commands/results.
- [x] services/access/identity_operator.py; identity-migrations/versions/0006_actor_command.py; identity_baseline.py — implement fixed command/recovery with strict verification and old-head normalization.
- [x] services/access/tests/qualify_identity_baseline.py, qualify_actor_command.py, tools/prepare_identity_command_role.sql — independent reference recorder and actual full matrix; retain failure evidence.
- [x] services/access/IDENTITY-MIGRATIONS.md — actual owner API/preconditions/limits, recovery and five impact decisions.
- [x] Root reference pin/publication, actual qualified frame and previous-source upgrade, affected suites/composer, evidence/navigation/inventory, reviews and scoped commit.

Given a private prepared synthetic target, when current authorized operator executes,
then effects/event/outcome commit atomically and recovery returns only the original
scoped receipt. Given a forbidden/failed attempt, when executed or looked up, then no
receipt disclosure or partial effects occurs; uncertain commit is explicitly unresolved.
Given a prior verified owner target, when upgraded/refused, then old state is preserved.

## Ownership and Verification

Implementation agent owns services/access code/revision/helper/recorder/qualifier/tests/
preparation/runbook; must not install, run Docker/actual DB, spawn, commit, or alter trusted
reference/pin. Root owns manifest/lock/environment, actual fixture/SQL/Docker, independent
reference publication/manual pin, evidence/navigation/inventory/review/commit. Report
exact preparation/recording/qualification invocation and fixture requirements to root.

Use interpreter platform/deployment/.local/identity-baseline/actor-command-zxycfmc4/owner-env/venv/bin/python
with PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 and -I -B -m pytest services/access/tests
apps/pts/tests/test_release.py -q -p no:cacheprovider. Smallest RED first, affected tests,
then broader relevant checks. Root runs both existing composer --check-only routes.
Root independently observes actual missing routine RED on old head5 before migrating6.
Root fresh offline frozen environment adds only approved rfc8785; all existing pins stay.
Root maps every matrix row to executed tests; no stubs substituted for real login proof.
No new ADR needed: existing release/actor/structural/WRITE decisions suffice; record
scaffold/shared UI/context/docs/ADR impacts explicitly. Repository root context unchanged.

## Implementation Notes

Root independently records/publishes the new reference and manually pins
 ebe11f9cd4dbed35496488e6eb21b5c6af4c3c8f767447fd1e1ad7fb2c2c1188.
Actual restricted-login missing-routine RED observed on head5. Final fresh
actor-command-final-y2n1fdt9 passes24 named stages112.925s, source unchanged;
328 affected tests/no skips and both composers pass. Five impacts and each matrix
row map to executed tests in ACTOR_COMMAND_EVIDENCE.md. All original sources,
references/pins, prior frames and concurrent work are retained. Root fixture/source
recording/observer corrections and failed attempts remain documented in that evidence.

Typed Python receipts follow the selected common envelope. No CLI/credential/target
factory is installed: caller supplies the explicitly trusted prepared idle connection.
10s monotonic/5s SQL/2s lock budgets do not interrupt synchronous transport/commit waits;
prepared caller must configure bounded transport. No wall-clock return guarantee or
physical lost-network proof is claimed; actual commit + simulated lost ACK is qualified.

All three independent review layers are complete. Reviewed-source
actor-command-reviewed-hux72mlh passes27 actual stages42.639s with source unchanged;
330 affected tests/no skips and both composers pass. Direct deadline/doc/verification
patches below are resolved with no deferrals. Normal stop retains all data/resources;
final protected-file/source audit and scoped commit close this delivery.

## Spec Change Log

## Review Triage Log

| Finding | Verdict | Evidence / route |
| --- | --- | --- |
| Blind1 deadline after setup replies | medium | _run configures statement timeout before the second returned setup call and has no deadline check immediately before business SQL. A delayed setup can dispatch work after budget expiry. Direct deadline refresh/check and focused regression; patch. Caller-owned transport limitation remains explicit. |
| Blind2 malformed receipt row length | false | Both fixed SQL routines return TABLE(result,command_version,result_version,committed_at); one_or_none therefore supplies exactly four columns on this trusted owner boundary. No submitted input can alter that row shape. Content/version validation remains strict. |
| Blind3 validation exception contract undocumented | low | execute deliberately reuses existing CommandValidationError while outcome uses OperatorError command_invalid. Public owner callers need both documented safe contracts; direct runbook correction, patch. |
| Blind4 second authorized executor absent | medium | Current successful fixtures have only identity_operator. Exact scoped uniqueness/lookup across two current executors is unproved; add second actual preexisting synthetic login temporarily authorized in this test database, restore exact grants; patch. |
| Blind5 concurrent futures need overlap witness | medium | Submission alone permits sequential execution, so it does not demonstrate exclusion. Add held-lock/two-waiter observation inside existing bounds; patch. |
| Blind6 distinct actor IDs/shared key and shared ID/different keys | medium | Existing concurrent conflicting payload changes label only. Add both key/id races with distinct authenticated principals so shared per-login authority locking cannot mask domain locks; patch. |
| Blind7 replay/lookup authority race | medium | Only new execution races config; committed receipt paths lack a simultaneous revocation check. Extend existing actual observer matrix; patch with Gap1. |
| Blind8 actual statement cancellation absent | medium | Existing actual waits are advisory-lock timeouts, not server57014. Add controlled slow synthetic trigger, exact SQLSTATE witness, rollback and same-connection recovery; patch. |
| Blind9 connection reuse after failure absent | medium | Current physical-connection defaults check follows successful lookup, whereas failure helpers allocate new connections. Add same-connection conflict/outcome wait/event-failure checks; patch. |
| Blind10 fixed JCS escape boundary fixtures | medium | Actual SQL canonical comparison uses one mixed label, omitting quote/backslash/all control escapes/2028/2029 and present evidence. Add direct Python/server execution+stored fingerprint fixtures; patch. |
| Gap1 outcome lookup versus concurrent revocation | medium | Preverified absence: removing lookup's authority lock would leave current tests passing. Same root cause as Blind7; patch. |
| Gap2 event reason/evidence not asserted | medium | Preverified absence: replacing submitted reason/evidence by default/null would pass current counts and parser tests. Add exact stored-field assertions with nondefault reason/present ref, alongside canonical fixtures; patch. |

Edge-case hunter reports no findings. Each finding above is individually triaged before
grouping. All retained findings route to direct code/test/documentation patches within
the demonstrated private owner boundary; no new public API, intent gap or deferred work.


Review closeout: all retained findings patched. The additional actual fixture uses the
already existing synthetic access_runtime login, exact temporary wrapper grants with
byte-identical restoration, and explicit now-disabled protected configuration rows.
No new role/credentials or production application access. Runtime migration/helper/
reference bytes remain unchanged after review; only adapter deadline checks, tests and
documentation changed. Current-source27-stage/330-test evidence covers each patch.
