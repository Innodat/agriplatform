---
title: Explicit prepared target for Identity operator invocation
type: feature
created: '2026-10-20'
status: done
route: dispatch
review_loop_iteration: 0
baseline_commit: b16ca2512f7792ebecae7dc722267622be150b0a
context:
  - /home/ck/repos/innodat/agriplatform/AGENTS.md
  - /home/ck/repos/innodat/agriplatform/platform/docs/architecture/contracts/identity-access-execution-substrate.md
  - /home/ck/repos/innodat/agriplatform/platform/docs/architecture/contracts/e1-controlled-provisioning-and-evidence.md
---

<frozen-after-approval reason="standing bounded implementation approval">

## Intent

Make the existing actor.register_system execution/recovery usable through a thin
owner-local CLI bound to an explicit prepared disposable native ENV run. Preserve
all source, working-tree changes, original references/pins, receipts and resources.
No new dependency, schema/migration, role/grant bootstrap, account/membership/Access
command, generic lifecycle service/generator, Leave/KDG/editor or production use.

## Boundaries & Constraints

Add services/access/identity_operator_target.py and operator_cli.py, reusing existing
Identity parser/adapter and dev.directory/read_at/check_private/decode/schema validation,
native_cli.check_run/write_private and images.bounded_command. No replacement process
supervisor or ENV lifecycle. Root alone prepares/uses actual synthetic DB and secrets.

A private version1 descriptor is exactly native run/identity-operator.json under
platform/deployment/.local/kdg/<canonical UUID>/. Fields: schema_version:1,
owner_id:identity, environment_kind matching local_disposable/ci_disposable,
run_id, environment_target_ref, target_sha256, database, database_login:identity_operator,
secret_ref. environment_target_ref selects the existing checked-in
platform/deployment/environments/kdg-local.json; hash, workspace, native marker/config,
owner and kind must match. Database is exactly idop_<full run UUID hex>; connection
host is literal127.0.0.1, port comes only from validated ENV target. No endpoint override.
secret_ref is the exact identity.env path expanded from ENV's existing secret_refs.
Secret file: one literal IDENTITY_OPERATOR_PASSWORD=<nonempty value> line, optional
final newline, no interpolation, extra variables, NUL or embedded newline; bounded1KiB.
No URL/credentials in descriptor, argv, command document, output or errors. No ambient
PG/SQLAlchemy/Identity URLs, service config, defaults or Supabase status discovery.

Provide prepare_target(environment_target,run_id), callable by controlled setup, to
validate native preparation and existing private secret then exclusively write descriptor
using existing helper; no DB/role/credential creation, overwrites or repair. Loading
revalidates everything each invocation. Descriptor/secret regular single-link0600,
current UID, private0700 run/secrets directories, no symlink component/traversal.
Invalid/missing/changed/unsafe inputs refuse before connecting. Preparation records
configuration binding, not application readiness or trust against a compromised local UID.

CLI execute --owner identity --target <descriptor> --command-file <JSON> and
outcome --owner identity --target <descriptor> --command actor.register_system
--operation-id <UUID>. Other owners/commands/unknown or malformed arguments fail closed
without echoing values. Validate bounded input through existing strict parser before
worker/network dispatch; no caller actor override. Use the existing owner lock/interpreter.

One fixed isolated worker revalidates target then opens SQLAlchemy NullPool connection
with explicit URL.create/discrete host/port/db/login/password, connect_timeout3,
READ COMMITTED, startup statement_timeout5s/lock_timeout2s; disable libpq service/password
file/environment discovery and TLS/GSS negotiation for this loopback synthetic route.
Before effects verify actual session_user/current_user, database and safe restricted
login flags/memberships, then rollback read verification to idle and invoke existing
execute/outcome. No automatic migration/seed/grants/retry/reset. Parent launches only the
fixed worker with minimal environment, private bounded stdin (no secret), output cap8192
and existing supervisor12s deadline plus its2s cleanup. SIGINT/TERM enters cleanup;
interrupted/timed-out/invalid child response can mean committed effects: preserve original
operation identity, never promise rollback or automatically retry. Child stderr is hidden.

Render only a strict validated compact committed receipt (versions/time included),
{operation_id,status:unresolved} for absent lookup, or allowlisted safe code and known
operation_id. No arbitrary child/driver/parser text or traceback. Success only after
worker commit and clean completion; unresolved/unavailable never authorizes a new ID.

## I/O & Edge-Case Matrix

| Scenario | Expected |
| --- | --- |
| Prepared synthetic target, actual restricted LOGIN, execute/replay/outcome | Original typed committed receipt, one effect/event/outcome |
| Unknown operation/current revoked authority | Unresolved / safe denied, no disclosure |
| Missing/changed/hash/run/owner/env/db/login/secret mismatch or unsafe file | Refuse before worker/network/write |
| Malformed/unsupported input, missing args, ambient PG credentials | Closed safe failure; no ambient redirect |
| Connect/read/commit stall, interruption, excessive/malformed child output | Bounded cleanup, no success or secret leakage, original ID retained for recovery |
| SQL failure and normal success | Safe exact codes, no arbitrary diagnostics, existing atomicity/recovery retained |

</frozen-after-approval>

## Code Map

- services/access/identity_operator.py and identity_operator_input.py — unchanged protected command/receipt/parser owners.
- platform/deployment/dev.py:directory/read_at/check_private/Parser, native_cli.py:check_run/write_private — native private preparation; never historical validate_prepared.
- platform/deployment/images.py:bounded_command — existing bounded stdin/output/process group owner; reuse, no lifecycle qualification requirement.
- services/access/IDENTITY-MIGRATIONS.md — existing lock and manual controlled setup/recovery; append actual target/CLI contract.
- platform/deployment/.local/identity-baseline/operator-target-gf2ef2d8 — root proof/protected2597 files, prior frames retained.

## Tasks & Acceptance

- [x] New owner modules and focused tests services/access/tests/test_operator_target.py, test_operator_cli.py — ATDD RED before implementation; prove matrix, actual process bounds and secret-free errors.
- [x] services/access/tests/qualify_operator_target.py — consume explicit root-prepared native target/current head6 fixture, actual CLI execute/replay/lookup/refusal and unchanged state; no resource/role/secret provisioning by qualifier.
- [x] Owner runbook — preparation syntax, fixed target limits/recovery and scaffold/UI/context/docs/ADR impacts.
- [x] Root actual synthetic proof, affected tests/both composers, evidence/navigation/inventory, three reviews, preservation/stop and scoped commit.

Given an explicit validated native target, when invoked, then only the selected owner
command runs under the verified restricted login. Given invalid binding/input, when
invoked, then no connection/effects occurs. Given uncertain worker completion, when
returned, then the original ID remains recoverable without a success/rollback claim.

## Ownership and Verification

Implementation agent owns new modules/tests/qualifier and owner runbook only; no install,
actual DB/Docker, roles/secrets, spawn, commit or original parser/adapter/migrations/ref edits.
Root owns actual target/secret/fixture preparation, docs/evidence/navigation and commit.
Report exact fixture and qualification invocation when ready. No intent gap; only
isolated synthetic writes authorized. No accepted ADR change or new decision needed.

Use platform/deployment/.local/identity-baseline/actor-command-zxycfmc4/owner-env/venv/bin/python
with PYTEST_DISABLE_PLUGIN_AUTOLOAD=1, -I -B -m pytest services/access/tests
apps/pts/tests/test_release.py -q -p no:cacheprovider. Smallest RED first, affected checks,
both existing composer --check-only routes; root actual qualifier after source freeze.

## Implementation Notes

ATDD two missing-module failures precede implementation; exact nodes/command and
transcript-only RED retention are in OPERATOR_TARGET_EVIDENCE.md. Source under existing
owner lock adds two owner modules, three focused test files and a root-consumed
qualifier. No original parser/adapter/migration/reference/lock is modified. Root's
initial actual connection failure exposes libpq empty-service lookup; remove that
argument and retain cleared environment/explicit fields/passfile protection. Real
signals also expose swallowed InterruptedError; dedicated interruption now cleans up.
All failed frames/source and exact original operation IDs remain retained.

Reviewed-source actual qualifier passes commit/response-loss/original-ID recovery,
exact one-effect/unchanged state, refusal status and revoked authority/restoration.
387 affected tests PASS4.79s, both composers PASS. Five impacts, exact commands and
limits are in owner runbook/evidence; no accepted ADR change. Remaining account,
membership/hardening, Access/WRITE/full ID-B/KDG readiness are separate bounded gates.

## Spec Change Log

## Review Triage Log


| Finding | Verdict | Route and evidence |
| --- | --- | --- |
| Blind1 optimized qualifier drops asserts | medium | patch; standalone `assert` performs fixture guards and verification calls, all omitted with -O. Explicit checks retain these without a new public surface. |
| Blind2 initial counts miss other writes | medium | patch; count-only after first execute does not compare existing rows/unaffected tables. Exact row-delta/relationship checks directly close the proof gap. |
| Blind3 SIGTERM skips authority restore | medium | patch; default SIGTERM can terminate during committed disable. Fixed interruption handling and private restoration witness/manual kill9 recovery cover this concrete synthetic window. |
| Blind4 unbounded owner SQL | medium | patch; connect_timeout does not bound owner snapshot/update waits. Fixed SQL/lock timeouts plus bounded one-shot qualification deadline correct this test harness. |
| Blind5 no committed response-loss proof | medium | patch; sleep-before-effects signal tests and clean recovery do not prove post-commit uncertainty. Add internal actual lost-response/recovery witness without a public fault surface. |
| Blind6 refusal status discarded | medium | patch; launcher ignores main return; include/check return status and exact safe response. |
| Blind7 nonexecutable OWNER_PYTHON examples | low | patch; literal name had no variable assignment. Root defines/quotes the actual interpreter variable. |
| Blind8 final evidence absent | medium | patch; draft promised results without final source-bound records. Root populates exact actual results/hash/protection/review/stop evidence before acceptance. |
| Gap1 worker verification call unprotected | medium | patch; deleting caller verification leaves fabricated helper checks green. Add actual worker-path unsafe-session execute/outcome tests with no adapter dispatch. |
| Gap2 unresolved/denied exit status | medium | patch; same proven launcher status omission as Blind6; one direct correction closes both, retaining individual rows. |

All three layers launched before triage (third after a slot became available). Edge
hunter returned no findings. Ten individual findings are accounted for; no intent gap,
new public contract or deferred work. Root and the same implementation agent perform
the direct corrections and root reruns affected/actual verification before acceptance.


Final root acceptance: all direct patches verified;57 focused and387 affected tests,
actual reviewed qualifier and both composers pass. Normal native stop exit0 retains
data/resources.2597 protected files: zero missing/unexpected, four intended existing
documentation changes; all original references/SQL/locks and concurrent work intact.
All six runtime/test hashes match actual execution. No deferrals, production/real-data
use, deployment or push. See OPERATOR_TARGET_EVIDENCE.md and retained proof receipts.
