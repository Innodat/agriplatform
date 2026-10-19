# ENV post-Auth API default-privilege request boundary

This increment constructs the next source-derived setup request inside the existing
ENV owner and verifies that the existing transport refuses it. It executes no new
SQL, resumes no CLI, and adds no Docker route or public control. This is request
construction/refusal proof, not observed CLI SQL, SQL semantics or completed setup.

## Source and scope

Pinned Supabase CLI 2.120.0 source commit
`753520fa7202ed5f8b25883a4c0aa7e5e9ad1fc4`:

- [db-setup.ts](https://github.com/supabase/cli/blob/753520fa7202ed5f8b25883a4c0aa7e5e9ad1fc4/apps/cli/src/command-internal/db-setup.ts):
  applyDatabaseOverlay calls webhooks, API privileges, Vault and optional roles.sql
  in order. With the existing config, webhooks is disabled and
  api.auto_expose_new_tables=false selects START_REVOKE_API_PRIVILEGES_SQL.
- [db-config.toml-read.ts](https://github.com/supabase/cli/blob/753520fa7202ed5f8b25883a4c0aa7e5e9ad1fc4/apps/cli/src/command-internal/db-config.toml-read.ts):
  absent experimental.webhooks means disabled; adding an explicit false section
  would be rejected. Configuration remains unchanged.

Cached setup SHA256 is
`d82ed106aa3bea8613e639175d20a05eb27fdad49762bf8637217d6d0d50fca4`;
config-reader SHA256 is
`de5f8fd3890c0a525b87a98588d7d3a77b3a0eb47caf77f7e3e0dcf8c0a5426b`.
An independent extraction matched all417 SQL bytes including boundary newlines:
SHA256 `438b7e8bf360f0d66c629c5ff102a9fb52584758be94be722d6cb490b216dacc`.
The source SQL revokes default table, sequence and function privileges for future
postgres-owned public objects from anon/authenticated/service_role. No application
migration, user/account change or executed privilege change is part of this increment.

Reproduce the byte comparison from the repository root using the cached immutable
db-setup.ts (if absent, download the exact linked commit's file to that path first):

```sh
python3 - <<'PY'
from pathlib import Path
import hashlib, re, sys
sys.path.insert(0, 'platform/deployment')
import startup_lifecycle
raw = Path('platform/deployment/.local/cli-poststart-qualification/primary-source/db-setup.ts').read_bytes()
assert hashlib.sha256(raw).hexdigest() == 'd82ed106aa3bea8613e639175d20a05eb27fdad49762bf8637217d6d0d50fca4'
sql = re.search(rb'export const START_REVOKE_API_PRIVILEGES_SQL = `([^`]+)`;', raw).group(1)
assert sql == startup_lifecycle.API_DEFAULT_PRIVILEGES_SQL.encode()
print(len(sql), hashlib.sha256(sql).hexdigest())
PY
```

Observed:417 bytes, SHA256438b7e8bf360f0d66c629c5ff102a9fb52584758be94be722d6cb490b216dacc.
This separate source comparison complements the deterministic offline test literal;
it does not depend on that test's duplicated expected string.

The owner wraps that exact SQL in a closed synthetic psql exec envelope using its
existing disposable PostgreSQL identity. The actual CLI would use its already-open
host PostgreSQL session; this envelope is deliberately an owner-derived profile.
It is not an intercepted CLI request or a new way to resume that session.

## Acceptance and implementation

After successful Auth precondition, job completion/disposal and postcondition,
FreshGuard constructs the request, validates every key/type/value, and calls only
the pure dev._docker_request serializer/allowlist validator. It requires exactly
docker/docker_request_invalid. It never calls session.exchange with that body.
Unexpected admission or another error prevents qualification. Existing final custody
checks run before setting both catalog and request-refusal facts. The consumed
postcondition attempt cannot replay. Finish also requires the new fact.

Successful existing auth-catalog and cli-db-backend controls expose
api_default_privileges_request_refused=true. Other controls gain no fact or authority;
fresh_setup_completed and runtime_ready remain false. No deadlines, SQL executor,
process boundary, connection or cleanup policy changed.

| Requirement | Test evidence |
| --- | --- |
| R1: after successful Auth verification, construct/refuse without dispatch | test_post_auth_default_privileges_request_acceptance_without_dispatch |
| R2: exact source SQL and closed execution options | test_default_privileges_request_matches_pinned_sql_and_closed_envelope; source-check.json |
| R3: malformed envelopes/SQL cannot qualify | test_default_privileges_request_rejects_envelope_and_sql_mutations; test_default_privileges_bad_construction_cannot_qualify_or_replay |
| R4: unexpected allowlist admission/error cannot qualify | test_default_privileges_accidental_admission_cannot_qualify; test_default_privileges_wrong_refusal_cannot_qualify |
| R5: failed catalog never reaches construction; missing fact blocks finish | test_default_privileges_failed_catalog_never_constructs_request; test_default_privileges_missing_fact_blocks_finish |
| R6: existing process result, catalog/backend ordering and no additional exec | ExecutionSupervisor catalog/backend positive and predicate-failure process tests |
| R7: custody change at construction cannot publish either fact | test_default_privileges_health_change_during_construction_blocks_success |
| R8: new failure paths cannot return process success; adjacent controls omit fact | test_default_privileges_request_process_failures_cannot_return_success; existing migration/boundary positive process tests |

ATDD RED: the R1 test errors because the fact is absent; focused six-test RED also
retained before implementation. GREEN follows without changing expected behavior.
Ignored records are under .local/post-auth-overlay-qualification: acceptance-red.log,
focused-red.log, focused-green.log, acceptance-green.log, source-check.json and the
verification logs. The initial141-test run passes5.769s; the explicit acceptance
repeat passes1 test0.064s. Final verification/review results follow below.

| Verification record | Result | SHA256 |
| --- | --- | --- |
| acceptance-red.log | expected failure,1 test0.017s | 9405dc1eeb24b3320b50d94b6b0a63fab7a7bad71c62101535fe0e2544a96631 |
| acceptance-green.log | PASS1 test0.064s | e87a3624b9ff6e37854d66ac2b9be4b54fd9776a804b023f94a14be04934c3a8 |
| pinned-tests-final.log | PASS142 tests2.863s | e5c140876da4e90b1c63f9db3b793d38d32d83523284f7a10d081cc3bb484763 |
| process-tests-final.log | PASS4 tests71.731s | 843d2bf449654e5892cb21751a5fb2c0c7e99174e6dd15eae77fc77332cba170 |
| review-process-tests.log | PASS3 tests26.859s | 0bc77c484ad5acec11ca3de9a39f4d7b67e82a6c164b296b56a1df5269bd98eb |
| source-check-command.log | PASS417-byte exact source match | 7c6a2f5880e39889b2feeedfda61c340c025bdd97a353dfd32460236b93e3432 |

The142-test owner run includes the acceptance test. Total149 tests in the three
final verification groups; the separate acceptance repeat is not counted again.
The four-test process run precedes only review additions to test fixtures/assertions,
not production changes. The three-test review group covers both new failure scenarios
and two adjacent positive result shapes on final test source. The earlier four-test
process run82.926s is retained too; a second run was needed because explicit no-extra-
exec assertions were added while the first was active.

One independent oneshot blind reviewer returned five findings, individually triaged
as low coverage/reproducibility gaps and patched: reproducible pinned-source check,
health change during construction, replay/finish checks on both new error paths,
process refusal coverage and adjacent result-shape absence. None newly deferred.
Separate edge-case/verification-gap layers were skipped under the oneshot route.

## Verification commands

```sh
python3 -m unittest discover -s platform/deployment/tests -p test_pinned_execution.py -k test_post_auth_default_privileges_request_acceptance_without_dispatch
python3 -m unittest discover -s platform/deployment/tests -p test_pinned_execution.py
PYTHONPATH=platform/deployment/tests python3 -m unittest test_resources.ExecutionSupervisor.test_auth_catalog_process_order_and_same_pg_disposal test_resources.ExecutionSupervisor.test_auth_catalog_process_predicate_failures_do_not_qualify test_resources.ExecutionSupervisor.test_cli_db_backend_process_order_and_same_pg_disposal test_resources.ExecutionSupervisor.test_cli_db_backend_process_predicate_failures_block_job
PYTHONPATH=platform/deployment/tests python3 -m unittest test_resources.ExecutionSupervisor.test_default_privileges_request_process_failures_cannot_return_success test_resources.ExecutionSupervisor.test_auth_migration_cli_terminated_before_dispatch_and_owned_disposal test_resources.ExecutionSupervisor.test_auth_poststart_real_private_handoff_and_refused_job_dispose
```

Process tests use private synthetic Unix-socket/fake-daemon fixtures and child
processes, requiring local socket permission. They use no real Docker resources.
No full deployment suite or fresh actual pinned-CLI/Docker run is claimed on this
source. Earlier638-test and actual-runtime receipts remain prior-source evidence.

## Impacts and remaining gates

- Scaffold: the existing deployment/lifecycle owner gains one closed profile and
  refusal fact; no generator, service, template or application behavior changes.
- Shared UI: no browser surface or reusable UI impact.
- Agent context: existing instructions cover this owner/boundary; no context changes.
- Documentation: runbook, KDG continuation and memlog point to this evidence/spec.
- ADRs: existing release safety, structured diagnostics and scaffold ownership
  decisions apply; no new architectural decision or accepted ADR edit.

Next: qualify bounded synthetic execution and independent default-ACL semantics,
then remaining post-Auth setup/CLI continuation and full runtime/scaffold acceptance.
The existing no-continuation boundary stays enforced. ENV/P1/SERVICE and dependent
Identity/Access/WRITE/server-backed KDG gates remain open. TS7.0.2, mail15484,
concurrent documents, source, receipts/state and retained Docker resources remain
protected. No production action, cleanup, deployment or real-data use occurred.
