# Explicit saved-edit delivery and recovery — 2026-10-26

The unmounted `createEditDeliveryEntry` coordinates one selected saved edit through
original-operation recovery, at most one PUT, durable receipt/conflict consumption
and current own-detail import. It uses one admitted Auth execution lease and one
total deadline, including storage and final publication. It starts no sender or UI.

`deliver({account_id, org_id, action_id})` returns an operation-level `acknowledged`
or `conflict` with `readback: imported | unavailable`, or a safe typed failure.
Acknowledged means the exact receipt was consumed durably. It does not claim newer
local changes are Synced. Unknown outcomes retain the original action and frozen
command; no replacement operation ID or automatic retry is generated.

The default and maximum total deadline is 30 seconds; each HTTP phase gets at most
10 seconds and never exceeds remaining time. Session replacement, abort and deadline
fence every storage/network boundary and publication. The lease is released once.
A storage transaction completes before HTTP begins. Completion-boundary uncertainty
can retain committed original-account work, recovered under its original identity.

Two narrow storage operations support this consumer:

| Operation | Behavior |
|---|---|
| `lookupPreparedEdit(scopeAndAction, execution)` | Point-read the exact supported frozen command under current own-read, including after edit-only expiry/denial; unsupported/blocked work is retained. |
| `importCurrentDetail(snapshot, pinnedRead, execution)` | Validate scope and bounded detail, then reuse baseline reconciliation without renewing either permission observation or restoring denial. |

Own-edit is checked again before each send. A recovered committed receipt can be
consumed under own-read without edit authority. Read denial locks the partition.
PUT denial is latched for editing before probing current read authority; a loaded
probe preserves reading, while denied/unavailable probes conservatively lock the
partition within the execution fence. Cancellation/deadline stops dependent writes;
the already-latched edit denial is retained. No data response grants permissions.

Exact conflicts retain the attempted command, reviewed base and proposal as Needs
attention. This consumer provides no rebase or conflict resolution. A retained
conflict blocks another send; authorized read/history/detail import can refresh it.
Concurrent explicit calls may submit the same operation; existing server idempotency
prevents duplicate effects. No exclusive sender claim or scheduling is implemented.

Scaffold impact: reuse existing builder-owned IDB completion primitives; orchestration,
operation policy and authority scope are KDG-owned. No demonstrated neutral defect
requires a new shared abstraction. Shared UI and agent context: unchanged. Docs append
contracts and prepend the handoff while preserving old evidence. ADR impact: existing
accepted contracts/decisions apply, with no new ADR or edits to accepted decisions.

Run commands, source hashes, assertion names and results are in the
[machine record](evidence/edit-delivery-20261026.json). Both new proofs use real
Chromium IndexedDB. The integrated proof exercises the existing candidate Python
HTTP API with synthetic Access/storage, including response loss, original-identity
recovery, real server denial formats and revision conflict. It checks ledger/history
counts and balanced fixture resources; this does not establish actual PostgreSQL
permissions, native rollback, physical-device persistence or release readiness.

Prerequisites are existing ignored approved artifacts: Node26.11.1, TypeScript7.0.2,
modules in `platform/deployment/.local/web-baseline-qualification/new-5/root`,
Playwright in `platform/deployment/.local/scaffold-application/proof-dI2Gy9/root`,
Chromium under `platform/deployment/.local/web-baseline-qualification/browsers`,
and Python in `platform/deployment/.local/access-organization-check-20261022/owner-env`.
See [web commands](../web/README.md). A clean checkout alone lacks these artifacts;
existing toolchain/CI owners must supply them. No installation is part of this work.
Actual delivery configuration is strictly compiled inside a selected-source capsule
with those approved modules and existing Auth `skipLibCheck` for upstream declarations.
The older root node_modules cannot qualify this Auth contract; its initial failed
compile is retained separately from behavioral RED and approved-toolchain GREEN.

Pending-create persistence/setup, durable claims, automatic delivery, queue/browser/
service-worker/default-startup integration and UI/editor remain further work. Leave,
real accounts/Auth/Access, native-driver/PostgreSQL/Docker qualification, provisioning,
migrations, deployment/production/pilot and cleanup remain outside scope.
Fingerprints/HMAC remain deferred; dependencies including TypeScript7.0.2 are preserved.

Final32 qualification jobs pass: 73 delivery checks,29 integrated HTTP checks,
103 reconciliation,92 Save and61 history checks,575 compiled client tests,
127 direct tests, four fixture guards and16 existing loopback groups. Seven strict
adapter/delivery configurations, twelve schema/client freshness checks and five
scaffold parities pass. Prior313 backend tests are reused only after matching all77
backend source hashes; no new backend execution is claimed. Review addressed seven
of nine findings; two were rejected with evidence, and no new work was deferred.

| Requirement | Executed checks |
|---|---|
| Exact first delivery and recovery | `recover_before_one_put_then_read`, `exact_frozen_put_bytes`, actual original receipt recovery and lost-response one-PUT sequence |
| Scope/unsupported/order safeguards | Point-read pre-IDB scope rejection, returned account/org/action/capture/serialized rejection, unsupported/predecessor no-PUT cases |
| Uncertain and denied authority | Malformed/auth/unavailable recovery; independent edit expiry; server edit/read denial; denial latched before probe timeout |
| Receipt/conflict durability | Durable acknowledgement with failed readback/import, failed receipt storage with no acknowledgement, actual server conflict retaining proposal |
| Bounded current execution | Slow storage/headers/body, one deadline across phases, abort/session suppression, entry lease release/error and late storage commit |
| Concurrent local work | Identical competing commands; adapter mutation; successor Save and successor delivery/third overlay while older readback is held |
| Compatibility/preservation | Existing storage/transport proofs, generated contract freshness, scaffold parity, final source hashes and append/prepend custody |

The exact latest review tests also fail against the retained pre-fix coordinator for
all three demonstrated bug assertions. The replay replaces only a selected source
inside an isolated capsule; it never replaces shared worktree files. Earlier sandbox
loopback infrastructure failures and verification-harness corrections are retained
separately from behavior RED. Concurrent unrelated scaffold changes were preserved;
only the first two affected custody records were refreshed after those changes.
