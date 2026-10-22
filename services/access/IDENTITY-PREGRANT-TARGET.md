# Existing pre-grant Identity target qualification

This bounded proof consumes `identity.organization_account_target(uuid,bigint)` at
Identity19/Access10. It adds no schema, role, privilege or production behavior.
The result is exactly account ID, membership ID, membership revision, mapped account
actor ID and display name for the active organization/profile/member. It verifies
Identity facts; it does not verify live Auth, Access authority or grant eligibility.
Protected grant assignment and consumer activation remain gated.

Root prepares a fresh private native fixture using the existing four-group loader
and imports `qualify_identity_pregrant_target.CASES` (only `clean`) before bootstrap.
Identity19 and the existing verified service actor must already be installed. Access
migration runs through the existing controlled Access owner route. Never substitute a
real target, alter shared roles/passwords or reset a historical frame.

The root-prepared directory contains the existing `credentials.json`, `run.json`,
bootstrap/auth helper sources, the exact private `root_qualification_driver.py`
executable and source/log custody witness, plus mode0600
`identity-operator-credential.json` and `runtime-credential.json`, each containing only
`{"password":"<existing protected fixture secret>"}`. The qualifier derives both
restricted login targets from the already validated clean database URL. Auxiliary
credential bytes are hashed, never printed. No previous-source package is consumed.
Generate bootstrap custody with this qualifier's `source_snapshot(proof)` after all
inputs and this documentation are final. Keep shell stdout/inspection logs outside the
proof directory: every `*.log` inside it is a frozen aggregate input/output.

Run with the existing owner environment, plugins/cache disabled for pytest:

```sh
PY=platform/deployment/.local/identity-baseline/actor-command-zxycfmc4/owner-env/venv/bin/python
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 "$PY" -B -m pytest -p no:cacheprovider services/access/tests/test_identity_pregrant_target.py -q
ACCESS_QUALIFICATION_DIR="$PROOF" "$PY" -I -B services/access/tests/qualify_identity_pregrant_target.py --all
ACCESS_QUALIFICATION_DIR="$PROOF" "$PY" -I -B services/access/tests/qualify_identity_pregrant_target.py --verify-retained
```

`--all` is single use, including incomplete attempts. Optimized Python refuses before
imports/I/O. The exact bootstrap log inventory and original digests are checked before
database work; those same original bytes are rechecked before acceptance, including
after controlled migration adds its separate log. Bootstrap source/log mismatches
and retained output mutations refuse before
database connections. A separate retained invocation checks exact source/log/receipt/state
custody and performs read-only Identity19/Access10 verification without seeding or migration.
A failed aggregate requires inspection and a new root-prepared frame; do not delete the
marker or overwrite prior artifacts.

The fixture creates synthetic Auth/profile references and organizations through explicit
fixture owners; actual `identity_operator` executes account actor ensure, membership join,
retire and explicit rejoin with separately provisioned fixture authorities. Unmapped
membership is created without deleting mappings. Profile/organization soft deletions and
restoration are deliberate fixture actions between point checks. Those actions may
advance the selected row’s existing update timestamp; the qualifier permits only that
timestamp and intended deleted-at change in the selected reference row, and rechecks
restored eligibility. Existing audit triggers may also append evidence for these
deliberate fixture writes. Every read probe still requires exact full-state
before/after equality, including audit rows; fixture writes and read effects are
verified separately. A separate deliberate `identity_migrator` fixture update changes
only the active membership timestamp; the existing trigger advances revision1 to2.
The matrix then requires exact active revision2 evidence, retirement explicitly uses
expected revision2 and retains retired revision3, and rejoin still proves a new
revision1 ID. This fixture write is recorded separately from read no-effects. No
grants or application admission are created. Reads use actual `access_migrator`, assert its original identity,
`SET LOCAL ROLE access_command_owner`, READ COMMITTED READ ONLY, and transaction-local
trusted organization/service context with absent or empty caller account. Valid user
context uses a separate caller account. This context is an assertion, never authorization.

Traceability is encoded in `read_cases` and the aggregate step labels: exact five values,
UUID spelling, incorrect/missing/invalid targets and contexts, unmapped/deleted/retired
references, rejoin with a new revision1 ID and permanently absent predecessor, pooled
LOCAL reset of all four app settings and original session/current roles after success
and refusal, actual return/reborrow of the same pooled backend (PID verified) with
clean settings/roles and no-context empty result, point-only command owner and actual runtime/operator denials. Every read
matrix compares full Identity tables/sequences, Access rows/history/receipts/events and
catalog snapshots before/after. A privileged synthetic observer explicitly verifies RLS
bypass so policies cannot conceal effects. Controlled current catalog verification is
separate from the consuming point checks.

Impacts: existing owner qualification scaffolding is reused; shared UI and agent context
need no change; this runbook documents the proof; no ADR decision or production source
change is required. Root owns evidence/handoffs, independent reviews, affected regression,
composition checks, preservation audit, normal native stop and scoped local commit.
