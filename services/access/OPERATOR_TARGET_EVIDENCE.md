# Prepared Identity operator target — bounded ID-B evidence

2026-10-20. Build: `_bmad-output/implementation-artifacts/spec-id-b-operator-target.md`.
Baseline: `b16ca2512f7792ebecae7dc722267622be150b0a`.

This increment wraps the existing strict input/actor command in one fixed local worker
bound to a private native disposable target. It adds no migration, role, credential,
account command, generator or dependency. Original parser/adapter, six revisions,
trusted references and dependency locks remain unchanged. Full ID-B is still open.

## Requirements and verification

| Requirement | Evidence |
| --- | --- |
| Explicit owner/run/ENV/hash/database/login/secret binding; exclusive preparation | `test_operator_target.py`, root actual `prepare.py` |
| Private regular single-link0600 files,0700 directories, no traversal/symlink | `test_operator_target.py` |
| Strict command before dispatch; safe closed output and original operation identity | `test_operator_cli.py` |
| Fixed isolated worker, minimal environment, explicit connection and restricted session | `test_operator_cli.py`, actual qualifier |
| Bounded process/output/interruption, uncertain outcome recovery | `test_operator_cli.py`; existing supervisor reused |
| Actual restricted-login commit/replay/outcome/refusal, no extra effects | `tests/qualify_operator_target.py` |

ATDD RED: two missing-module acceptance failures before implementation. Focused TDD
covers descriptor/input/response/session/process boundaries. Existing actor-command
qualification remains the underlying SQL/concurrency/atomicity proof; this slice does
not claim new SQL or rerun the prior27-stage migration matrix.

Root retained frame: `platform/deployment/.local/identity-baseline/operator-target-gf2ef2d8/`.
Native run: `99b7231c-0a5b-4bdb-98e8-3329564c526a`.
Fresh database: `idop_99b7231c0a5b4bdb98e83329564c526a`, head `identity_0006`.
Root controlled synthetic setup uses the existing migration route and restricted
operator credential with an explicit synthetic principal/authority. It creates no
new global role or credential, and touches no real Auth account/provider/application
grant. The descriptor and private fixture contain no public credential output.

Root setup initially calculated its repository parent incorrectly and failed before
DB/resource access. Corrected script then succeeds; original command error is recorded
in this Build/session. No original source/resource was repaired or replaced.

## Commands and limits

`OWNER_PYTHON` is the existing locked owner interpreter at
`platform/deployment/.local/identity-baseline/actor-command-zxycfmc4/owner-env/venv/bin/python`:
Python3.15.0, SQLAlchemy2.1.4, Alembic1.20.0, Psycopg3.3.6, rfc87850.1.4, pytest9.1.1.
No install or lock update; TypeScript7.0.2 remains selected.

```sh
OWNER_PYTHON=platform/deployment/.local/identity-baseline/actor-command-zxycfmc4/owner-env/venv/bin/python
"$OWNER_PYTHON" -I -B services/access/tests/qualify_operator_target.py --target platform/deployment/.local/kdg/99b7231c-0a5b-4bdb-98e8-3329564c526a/identity-operator.json --fixture platform/deployment/.local/identity-baseline/operator-target-gf2ef2d8/qualification-fixture.json
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 "$OWNER_PYTHON" -I -B -m pytest services/access/tests apps/pts/tests/test_release.py -q -p no:cacheprovider
"$OWNER_PYTHON" tools/py/run_compose_supabase.py --check-only
"$OWNER_PYTHON" tools/py/run_compose_supabase.py --identity-authority owned --check-only
```

Actual results, source hashes, review disposition and preservation are recorded below.
No hosted CI, physical network-failure injection, real operator adoption, production
release or full runtime/KDG readiness is claimed. The target is trusted private local
configuration; it is not protection against a compromised local UID or administrator.
Killing the worker may follow commit: preserve the original operation ID and recover
through current-authorized outcome. Unresolved does not prove rollback or permit a new ID.

Actual integration initially refused connection: passing `service=""` requests a literal
empty libpq service lookup. Sanitized root frames/category establish this before SQL;
no driver diagnostic/credential is printed. The correction omits that argument because
the fixed worker clears its environment and supplies all connection fields explicitly.
`passfile=/dev/null` remains. Original failed qualification and exact-command replay,
debug frame/category logs, private command files and initial source are retained.

Real process signal tests also caught selector retry swallowing `InterruptedError`;
the dedicated interruption exception now reaches existing supervisor cleanup. Both
SIGINT and SIGTERM tests verify child disappearance without an automatic retry.

## Five impacts

Scaffold: existing native preparation/bounded-process/Identity owner pattern only;
no generator promotion or generic runtime. Shared UI: no consuming surface/change.
Agent context: existing rules suffice. Documentation: owner runbook, evidence,
Build record, KDG navigation and ownership inventory. ADR: existing accepted ownership,
release, actor, logging and structural/WRITE decisions suffice; no ADR changed or added.


## Actual results and retained source

`prepare.log`: exclusive descriptor preparation PASS. `fixture-setup.json` and
`fixture-migration.log`: fresh synthetic database, unchanged existing Alembic head6
PASS. `original-command-recovery.json`: the original failed command ID commits after
the connection-argument fix. `qualification-corrected.json`: full CLI matrix PASS,
including current revoked authority execute/lookup denial and restored authority.
The qualifier restores enabled authority but its guarded revision/timestamps advance;
all other Identity tables remain identical after that check.

Root `tests-corrected.log`:373 passed3.49s, no skips. Earlier372-pass and failed actual
frames remain retained. Both `composer-legacy.log` and `composer-owned.log` exit0.
`corrected-source-hashes.json` and `corrected-source/` bind the executed source;
`initial-source/` preserves the failed service-argument version. Local proof artifacts
are retained under the root frame above, never packaged as public credentials.
`safe-output-check.json` verifies credential absence in selected public logs/results.
`preservation-initial.json`:2597 original nonignored files, no missing files, exactly
four intended existing documentation files changed. Original SQL/reference/lock/source,
concurrent Leave/PtS/Expense/brainstorming files and previous evidence remain unchanged.

Three-layer review and final reviewed-source verification/preservation follow below.


## Reviewed-source acceptance

All three BMAD review layers completed: Blind8, Edge0, Verification2. Every finding has
an individual verdict/evidence in the Build triage log. Direct corrections strengthen
the qualifier's optimized-mode checks, exact row/table/link effects, refusal exit status,
owner SQL/deadline/restoration evidence, unsafe worker session tests and actual
post-commit response-loss recovery. No deferred work or unresolved finding remains.

Final root affected suite: **387 passed4.79s, no skips** (`tests-reviewed.log`). Both
composition routes pass again (`composer-legacy-reviewed.log`, `composer-owned-reviewed.log`).
The exact reviewed qualifier command above passes (`qualification-reviewed.json`):
`committed_response_loss_recovered`, `revoked_execute_lookup_denied`,
`authority_enabled_restored`, and `unchanged_after_replay_lookup_refusal` are all true.
Its fixed internal test commits through the actual restricted worker, saves a private
post-commit witness, suppresses its response and stalls until the existing12s bound.
Normal outcome/replay recover that exact receipt; all old rows/unaffected tables and
new actor/event/outcome identities/links are checked. There is no public fault flag.
This does not simulate a physical network partition or prove kernel-level cleanup.

Reviewed runtime/test source is retained in `reviewed-source/` and
`reviewed-source-hashes.json`; final source-custody/preservation receipts confirm it
matches execution. The final evidence/documentation snapshot is recorded separately.
The optimized-fixture test proves rejection before network even with -O. The qualifier
uses explicit checks, fixed120s one-shot deadline, statement5s/lock2s owner limits,
SIGINT/TERM restoration, and private before/after authority witnesses. SIGKILL or failed
restoration requires explicit current-state inspection, as documented in the runbook.

Exact initial ATDD command was the affected command above restricted to
`services/access/tests/test_operator_target.py services/access/tests/test_operator_cli.py`.
`test_missing_target_is_safe_and_no_network` and `test_invalid_arguments_safe` failed
because their modules did not exist. That RED output is retained in the implementation
agent tool transcript; no standalone RED filesystem log is claimed. Reviewed focused
suite (including `test_operator_target_qualification.py`):57 PASS3.42s.

The first stop attempt added -I to the native ENV script; its sibling import failed
before any resource action. The corrected existing native invocation uses -B without -I;
this is a command correction, with no change to the ENV wrapper. Failed/successful
attempts remain recorded. Normal stop result and final protection audit follow.

Final normal native stop: `native-stop-corrected.json`, completed exit0 with data
retained and runtime_ready false. No reset/prune/removal. `preservation-final.json`
checks2597 original files: zero missing/unexpected changes and exactly four intended
existing documentation files changed. Six reviewed runtime/test files still match
actual execution. `safe-output-reviewed.json` verifies credential absence in final
selected outputs; `failed-attempts.json` retains safe classifications/corrections.
All prior receipts/state/source/failed frames and Docker resources remain preserved.
Final diff whitespace check passes. No production migration, infrastructure/deployment,
account/provider/access change, real-data pilot or push occurred.
