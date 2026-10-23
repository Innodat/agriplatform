# Bounded WRITE transaction context promotion

bmad-help selected the remaining shared transaction-context prerequisite before KDG
business persistence. bmad-build used its small reversible oneshot route: promote
existing primitives, no new business workflow or irreversible effects. The existing
dirty tree was authorized for preservation; only this delivery is included in its commit.

Canonical runtime/tests live under platform/builder-cli/templates/application/write-tools.
KDG consumes them through the existing preservation installer in its separate write-tools
root. Real application rendering emits the same two files and executes their tests after
installation. The KDG synthetic consumer uses only explicit trusted backend assertions;
it does not establish or expand user authority. No helper is imported on API startup.

The neutral functions are copied without semantic changes from the previously qualified
atomic_write.py example: WriteError, _uuid, VerifiedContext, Budget, _limits, execute,
transaction. Historical examples, database/native/Auth sources and inventories stay
unchanged. The new copy imports SQLAlchemy and standard-library modules only; it omits
OutcomeKey, lock hashing, receipts, domain SQL, rfc8785 and fingerprint helpers.

## Behavior and traceability

| Requirement | Executed check |
| --- | --- |
| Generated context and tests exist and execute after actual installation | write-context.test.mjs rendered-application acceptance |
| Template/consumer parity; owner files and manual edits preserved | write-context.test.mjs synchronization and conflict acceptance |
| Strict nonnil canonical IDs, bounded modes/time and redacted representation | test_context_is_strict_and_redacted |
| Exact org/account/actor/mode bound transaction-locally | test_binds_exact_transaction_local_verified_values; KDG owner consumption |
| One original deadline, observation within one second, positive clipped waits | observation/limit tests; test_restarted_local_attempt_keeps_original_budget |
| No nested transaction/autocommit/non-READ-COMMITTED entry | test_invalid_connection_modes_refuse_before_begin |
| SQL/commit failures safe; owner exceptions do not return success | failure tests; no sensitive exception rendering |
| Late commit acknowledgement remains uncertain | test_late_commit_acknowledgement_is_uncertain_not_rollback |

ATDD RED: actual renderApplication output lacked write-tools/transaction_context.py;
the acceptance assertion failed before implementation. `/tmp/kdg-write-context-atdd-red-unrestricted.log`
retains that behavior. The initial restricted Node runner exposed only a child-test
failure; it was rerun with the same approved toolchain outside the restricted sandbox
before implementation. Eleven focused synthetic tests then characterized the extracted
code. One renderer-inventory edit accidentally omitted two existing host files; the
failure was explained and both original expectations restored, adding only the two
intended WRITE files. Neither runtime behavior nor an unexplained expectation changed.

## Commands

N denotes retained Node26.11.1 at
platform/deployment/.local/kdg-toolchains/ad277eef-a10e-4aac-bb82-5743653fb2e0/payload/node/bin/node.
P denotes platform/deployment/.local/access-organization-check-20261022/owner-env/bin/python.
No installation, dependency manifest/lock change or TypeScript baseline change occurred.

- `N --test platform/builder-cli/tests/write-context.test.mjs platform/builder-cli/tests/application-renderer.test.mjs`
- `P -I -B platform/builder-cli/templates/application/write-tools/test_transaction_context.py`
- `P -I -B apps/kdg-capture/write-tools/test_transaction_context.py`
- `P -I -B apps/kdg-capture/write-tests/test_owner_context.py`
- `N platform/builder-cli/scripts/sync-kdg-write.mjs --write` then `--check`
- `N --test platform/builder-cli/tests/*.test.mjs`
- `N node_modules/typescript/bin/tsc -p platform/builder-cli/tsconfig.json`

## Limits and impacts

Synthetic connections record adapter calls only. These results do not establish actual
PostgreSQL rollback, RLS, transaction_timeout, pool cleanup or privileges. No DB/native
stack/role/account/schema preparation or external authority call occurred; previous
native proof remains historical. No business table, route, operator command, complete
WRITE/Story1.2, release/device/production readiness or generation-ready CLI is claimed.
Current setup fingerprint/retry gates are unchanged; fingerprints/HMAC remain deferred.

Scaffold: canonical helper/tests, application emission, installer parity and KDG adoption
updated together. Shared UI: no impact. Agent context: existing parity instructions
suffice. Documentation: this evidence, next-session, builder guide and migration guide.
ADRs: unchanged; apply existing transaction/context/attribution boundaries. Preserve all
concurrent work, historical resources/evidence and TS7.0.2. No Leave/editor, real-account/
access, production, provisioning/deployment/pilot or cleanup.


## Final results and review

- Canonical template tests:14 PASS in0.005s;
  `/tmp/kdg-write-context-canonical-final.log`.
- KDG emitted tests:14 PASS in0.008s; `/tmp/kdg-write-context-emitted-final.log`.
- KDG owner synthetic consumer:3 PASS in0.003s; `/tmp/kdg-write-context-owner-final.log`.
- Full affected builder suite:75 PASS,0failed/0skipped in9.586s;
  `/tmp/kdg-write-context-builder-reviewed.log`. This includes actual rendered/installed
  execution of the14 generated tests and installer conflict/preservation checks.
- Focused suite with explicit `SCAFFOLD_WRITE_TEST_PYTHON=P`:2 PASS in1.266s;
  `/tmp/kdg-write-context-explicit-python.log`. Default retained interpreter also passes.
- Strict TypeScript7.0.2:exit0; `/tmp/kdg-write-context-typescript.log`.
- Managed source/test parity:PASS; `/tmp/kdg-write-context-parity.log`.

The configured oneshot independent review completed; no configured layer was skipped.
Eight findings were individually triaged in the delivery spec. Seven direct test/docs
corrections were applied, including generated README prerequisites, owner-SQL error and
shrinking/late-response tests, import-form coverage, explicit test-interpreter selection
and these actual results. The claim that no consuming test command exists was disproved
by the existing documented command and successful execution. No review finding deferred.
No speculative catalog guards or new policy framework were introduced.

The extraction's seven symbol ASTs match the historical source exactly. All11 inspected
historical example/database/native/Auth source/manifest files remain unchanged. The
old next-session document remains an exact preserved suffix. All100 preexisting dirty/
untracked paths remain present; concurrent Scribeswell planning updates remain excluded.
The [receipt](evidence/write-context-20261023.json) records final commands/results and
source/log bindings, without credentials or runtime authority. This mutable evidence
chronology and its receipt are excluded from their own source inventory.


A final staged whitespace check found one trailing blank line in the canonical helper
and its emitted copy. The first local commit already existed; a separate local follow-up
removes it in the owning template, regenerates KDG and refreshes receipt bindings.
Runtime symbol ASTs are unchanged. Actual rendered/installed behavior and parity reran:
2 PASS, including14 emitted tests; KDG owner3 PASS. Logs:
`/tmp/kdg-write-context-whitespace-focused.log` and
`/tmp/kdg-write-context-whitespace-owner.log`. The scoped diff whitespace check now passes.
