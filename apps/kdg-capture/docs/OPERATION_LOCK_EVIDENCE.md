# Scoped WRITE operation-lock promotion

bmad-help [BD] selected the next small organization/account operation-lock prerequisite.
bmad-build uses its small reversible oneshot route: extend the existing managed helper
and emitted tests, without a new schema, API, outcome store or retry orchestrator.

## Contract and compatibility

OutcomeKey uses exact owner schema, organization, executor account, handler-defined
command and nonnil canonical operation UUID. The lock tuple includes lock_version1,
organization scope and account caller kind. Validated schema/command and UUID values
are ASCII; compact sorted standard JSON is byte-identical to the required JCS for this
closed shape only. It is not a general JCS implementation. The historical vector stays
`-5169148205731144946`;100 independently generated supported tuples also match the
existing approved rfc8785 serializer. That serializer is used only by the offline
comparison, never imported by the emitted helper and no dependency is installed.

The scope/operation identity SHA256 selects a signed64-bit transaction advisory lock.
No payload/answers are hashed or compared; this is not fingerprint/HMAC work. A collision
serializes unrelated operations; actual database uniqueness must determine outcome
identity. The owner calls outcome_lock inside its verified transaction and retains its
original Budget. Context shape is not authentication/authorization. KDG still owns its
fixed organization, service admission and exact action/resource evidence.

Malformed or foreign key/context refuses before any adapter SQL. Waits cap against the
remaining original budget. Only SQLSTATE55P03 raised by advisory-lock acquisition maps
to operation_busy; limit-setup or other SQL errors remain safe internal_error. Expiry
before SQL and a late lock acknowledgement never yield timely success. None of these
exceptions proves a database rollback or missing committed outcome.

## ATDD and focused TDD

The actual renderApplication acceptance failed before implementation because emitted
context lacked scoped locking (`/tmp/kdg-operation-lock-atdd-red.log`). The copied
historical lock adapter then failed two strict-context subcases with AttributeError and
one expected internal_error because limit-setup55P03 was mapped to operation_busy
(`/tmp/kdg-operation-lock-focused-red.log`). Focused corrections preceded GREEN:
explicit type guards and a narrower acquisition-error handler, without changing the
historical source. Expectations were not relaxed.

| Requirement | Executed tests |
| --- | --- |
| Stable encoding and original signed lock value | literal vector, independent canonical byte vector,100-case offline JCS comparison |
| All five identity dimensions preserved | key-dimension tests; KDG capture.create versus capture.edit |
| Closed ASCII types/bounds and exact org/account match | invalid/noncanonical/bounds/context tests with zero SQL on refusal |
| Transaction-scoped bound lock SQL and original-budget caps | exact advisory statement/parameters, shrinking limits |
| Safe busy/error distinction | acquisition55P03 versus setup55P03,57014,42501/unknown; ordinary execute55P03 remains generic |
| Exhausted/late execution | no SQL after expired budget; late lock result prevents COMMIT in synthetic adapter |
| Actual copied adoption | rendered/installed helper tests, managed parity/conflicts and KDG-owned consumer |

## Verification commands

N is retained Node26.11.1:
platform/deployment/.local/kdg-toolchains/ad277eef-a10e-4aac-bb82-5743653fb2e0/payload/node/bin/node.
P is platform/deployment/.local/access-organization-check-20261022/owner-env/bin/python.
Approved dependencies and root TypeScript7.0.2 remain unchanged.

- `P -I -B platform/builder-cli/templates/application/write-tools/test_transaction_context.py`
- `P -I -B apps/kdg-capture/write-tools/test_transaction_context.py`
- `P -I -B apps/kdg-capture/write-tests/test_owner_context.py`
- `N platform/builder-cli/scripts/sync-kdg-write.mjs --write` / `--check`
- `N --test platform/builder-cli/tests/*.test.mjs`
- `N node_modules/typescript/bin/tsc -p platform/builder-cli/tsconfig.json`

Final counts and review results follow below. The [delivery receipt](evidence/operation-lock-20261023.json)
records command bindings and retained source/log hashes, excluding this mutable chronology
and the receipt itself from their own source inventory.

## Limits and impacts

No PostgreSQL/Docker/native connection, roles/database preparation, real account/access,
business table/API or production/deployment/pilot/cleanup operation occurs. Synthetic
connection tests prove adapter calls only: no native lock contention, lock release,
RLS, unique constraint or atomic outcome/evidence/domain effect is qualified here.
Earlier native examples remain historical; the new managed copy needs its own consuming
database proof. Current stored-resource authority, first-committed recovery and supported
receipt versions remain unimplemented. Story1.2 bootstrap keeps its separate retry/
fingerprint gates, while fingerprints/HMAC remain deferred.

Scaffold: helper/tests and actual rendered/installed proof updated with KDG adoption
in the same item. Shared UI: unchanged. Agent context: existing parity instructions
suffice. Docs: this evidence, receipt, current handoff and builder/generated-app/KDG
migration guidance. ADRs: unchanged; existing WRITE/ADR0061 scope retained. Historical
examples, the seven prior context primitives, migration/native/Auth inventories and
concurrent work remain preserved. Prior context receipts remain historical when the
managed source/provenance hashes change; they are not rewritten as current proof.


## Final results and independent review

- Canonical helper tests:26 PASS in0.013s; `/tmp/kdg-operation-lock-review-green.log`.
- KDG emitted helper tests:26 PASS in0.012s; `/tmp/kdg-operation-lock-emitted-final.log`.
- KDG-owned consumer:4 PASS in0.007s; `/tmp/kdg-operation-lock-owner-final.log`.
- Full affected builder suite:75 PASS,0failed/0skipped in16.245s, including actual
  rendered/installed helper tests and preservation/parity;
  `/tmp/kdg-operation-lock-builder-final.log`.
- Strict TypeScript7.0.2:exit0; `/tmp/kdg-operation-lock-typescript-final.log`.
- Managed parity:PASS; `/tmp/kdg-operation-lock-parity-final.log`.
- Deterministic100-case compatibility check:PASS;
  `P -I -B platform/builder-cli/tests/check_operation_lock_compatibility.py`,
  `/tmp/kdg-operation-lock-compatibility-final.log`. Program, fixed historical literal,
  deterministic tuple generation and the installed oracle are explicit; no general
  canonical-JSON or new native qualification is claimed.

The configured oneshot independent review completed with all seven findings assessed
separately. Direct fixes cover late limit response, inactive/autocommit refusal, error
propagation inside owner transactions, redacted key representation and complete
reproducible evidence. The caller obligation to reuse the exact installed context is
explicit and tested by KDG's key/scope consistency assertion. It is not replaced by a
custom context registry, per-lock authority query or claim of backend compromise defense.
No review finding is deferred. Tests for late setup and invalid connection states failed
before the corrections (`/tmp/kdg-operation-lock-review-red.log`); no expectation relaxed.

The seven prior context symbol ASTs remain identical;14 historical example/database/
native/Auth source/inventory files remain byte-identical. All101 preexisting dirty/
untracked paths remain present. Existing next-session content is an exact preserved
suffix. Concurrent Leave/Scribeswell work is excluded from this local delivery. Approved
dependency manifests and TypeScript7.0.2 are preserved. No native/Docker/provisioning
operation occurred; no actual lock contention, unique outcome or business write is claimed.
