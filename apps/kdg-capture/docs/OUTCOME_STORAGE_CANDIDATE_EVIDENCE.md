# KDG outcome storage candidate — 2026-10-23

Implemented an inert KDG-owned adapter in `../write-candidate/operation_outcomes.py`.
It uses the unchanged managed transaction helper; it opens no connection, applies no
schema and mounts no HTTP route. No persisted-outcome or release-readiness claim follows.
The current migration ledger has no capture/history tables. This is synthetic adapter
qualification against the selected future canonical outcome columns, not database proof.

## Contracts and boundaries

`lookup_private(conn,budget,key,context)` selects by exact organization, executor account,
handler command and operation. A successful missing row returns None; failed, duplicate,
foreign, malformed or unsupported records never become absence. Native UUID row values
are normalized; stored receipts remain strictly typed, closed v1 capture.create/edit
results with canonical nonnil UUIDs and decimal revisions 1–9223372036854775807.
Original stored capture/revision is returned without an incoming-body comparison.

`append(...,outcome_id,receipt)` requires an active non-autocommit write context and
matching command/operation. Its plain bound INSERT uses verified executor/initiator actor
and server time. It neither commits, upserts nor returns a successful acknowledgement.
The caller must reserve the internal outcome ID and lock/recheck before writing, then insert the outcome before linked revision/evidence rows and
commit capture, immutable revision/evidence and outcome in one owner transaction.

Private discovery is not authorization. Reuse the exact verified context installed by
the managed transaction helper. Before disclosure authorize the actual stored resource.
GET create-outcome recovery may use current own-read after create authority removal;
POST retry still requires current create authority. Neither HTTP policy is implemented.
None is not public unresolved, rollback proof or permission to allocate a fresh operation.
SQL failures have safe identifiers with suppressed exception context; model diagnostics
hide input. Never expose exception locals or Pydantic error dictionaries as public errors.
A row fetch finishing after the original deadline fails with execution_timeout, even
when absent. These checks do not prove native cancellation or PostgreSQL commit timing.

## Behavioral evidence and reproducible commands

P = retained `platform/deployment/.local/access-organization-check-20261022/owner-env/bin/python`.
N = retained `platform/deployment/.local/kdg-toolchains/ad277eef-a10e-4aac-bb82-5743653fb2e0/payload/node/bin/node`.
Run from repository root; no install or environment change is needed.

- `P -I -B apps/kdg-capture/write-tests/test_operation_outcomes.py`: 16 tests PASS.
- `P -I -B apps/kdg-capture/write-tools/test_transaction_context.py`: 26 tests PASS.
- `N platform/builder-cli/scripts/sync-kdg-write.mjs --check`: PASS.

ATDD first observed two behavioral failures: existing receipt was missed and no INSERT
was emitted. Both passed after implementation. Focused deadline TDD observed two delayed
fetch failures (present/absent), then passed after post-fetch deadline enforcement.
The final 16-test matrix covers exact SQL scope/bindings, original results, both commands,
closed metadata/result validation, revisions/UUIDs, absent versus duplicate/SQL failure,
read-only and mismatched contexts, attribution, plain INSERT, safe diagnostics and no
premature acknowledgement/following work after insertion failure. Synthetic connection
exit records show control flow only; they do not prove actual rollback or durability.
Source/log hashes are in [the evidence receipt](evidence/outcome-storage-candidate-20261023.json).

## Delivery impacts and remaining gates

- Scaffold: reuse the already promoted helper/tests unchanged; capture-specific SQL,
  DTOs and recovery authority stay KDG-owned. No new neutral pattern needs promotion.
- Shared UI: none; no user interface change.
- Agent context: none; existing ownership/parity instructions suffice.
- Documentation: current handoff/contracts, optional test guidance and this evidence.
  Historical handoffs/evidence remain intact.
- ADR: no new decision; implements the selected ADR-0061 first-committed contract.
  Story1.2 operator bootstrap retains its distinct fingerprint gate and replay policy.

Next implement the capture/revision/outcome schema and concrete authorized consuming
transaction together. Before activation qualify restricted-role RLS/immutability,
composite linkage, unique outcomes under concurrency, capture/history/outcome atomicity,
current resource authorization, native deadlines and ADR-0020 migration/recovery safety.
Do not apply a partial outcome-only migration. Native work requires its existing fixture
custody/authorization gate. Fingerprints/HMAC remain deferred. No database/Docker resource,
API startup, dependency baseline (including TypeScript7.0.2), real account/access,
Leave/editor, production/provisioning/deployment/pilot or cleanup change occurred.

## Independent review and preservation

The configured blind review returned six findings, all individually triaged in the
[delivery spec](../../../_bmad-output/implementation-artifacts/spec-kdg-outcome-storage-candidate.md).
Corrections enforce distinct internal/caller IDs, clarify immediate-FK insertion order,
reuse the original budget throughout tests, add duplicate-INSERT failure coverage, and
expand adapter formatting. The claimed runtime loader conflict was not reproducible:
the other loader is generated test support, not a runtime consumer. The supported import
path is documented: import this adapter and construct keys/contexts/transactions through
its `write` export. A second-import integration test verifies identical helper types.
No finding is deferred. The distinct-ID regression failed before correction; final
16 tests PASS in `/tmp/kdg-outcome-review-green.log`.

All 141 preexisting dirty/untracked paths remain present; 14 received concurrent edits
outside this delivery and were left untouched. The preceding handoff is an exact suffix.
45 historical/API/managed/dependency files are byte-identical to the baseline, including
existing outcome evidence, generated helper inventories and dependency manifests. No
broader test or native qualification is inferred from that preservation check.
