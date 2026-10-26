# Candidate offline own-history consumption — 2026-10-26

History downloads now have an isolated local consumer. Successful pages carry exact
own-read evidence from the same verified Access decision that authorized the page.
The evidence binds account, durable actor, membership, organization, own-account
resource scope, permission and decision ID. Expiry is checked_at plus seven days.
Entry `/context` remains current online evidence without an offline lease.

The KDG-owned IndexedDB store imports complete validated pages, original immutable
definitions, current server baselines, progress and the scoped observation in one
ordinary transaction. It preserves pending/local/base/conflict fields verbatim and
does not create a queue, acknowledge an operation or mark pending work Synced. Older
server revisions cannot replace newer baselines; missing rows never delete records.
All local business keys include the account and organization namespace.

The explicit download coordinator uses the existing protected history transport.
Network work finishes before the local transaction; signal/session checks continue
through import completion. Durable partition generations prevent late responses in
another JavaScript realm from undoing a denial or logout. Ordinary handle closure is
separate from logout. Denial/logout retain locked data; explicit current same-user
verification is required for recovery. An outage does not manufacture a denial.

Local viewing checks the exact stored observation, persisted wall-time watermark and
process-local monotonic elapsed time. This is managed application policy, not trusted
server authorization or protection against same-origin JavaScript/device access.
No local clock manufactures an observation or extends another capability.

The reusable request/transaction completion primitives and their tests belong to
`platform/builder-cli/templates/application/web/offline-tools`. KDG adopts generated
copies through `sync-kdg-offline.mjs`; new application scaffolds receive the same code
and tests. A request result does not acknowledge a transaction, and a request error
event alone is neither transaction completion nor abort. KDG retains its schemas,
authorization, generations, merging and retention policy.

Verification uses retained Node26.11.1, TypeScript7.0.2, approved dependency capsules
and isolated Chromium with synthetic records/authority only. Exact commands, results
and source/log references are recorded in
[the machine record](evidence/offline-history-20261026.json).

The candidate has no UI, service worker or default-startup integration. No real Auth,
Access, PostgreSQL/native-driver/Docker qualification, provisioning, deployment,
production/pilot or cleanup occurred. Physical-device durability, eviction and at-rest
protection remain unqualified. Fingerprints/HMAC remain deferred. Earlier evidence
and concurrent work remain preserved.

A failed metadata write cannot establish a durable denial. The current process retains
its known lock and reports the failed write as unavailable; it does not claim that
information survived a storage system which refused it. Local reads use bounded
keyset pages (default30, maximum100) for records and progress, without deleting data.


Final verification passes 277 backend tests (37 history), 475 compiled Auth/client
cases, 127 direct cases, four fixture guards, thirteen loopback groups and 61 isolated
IndexedDB checks. Five strict TypeScript7.0.2 configurations, ten schema/client owner
freshness checks, five scaffold parities and ten primitive/renderer/owner tests pass.
All executed command source sets remained unchanged during verification. The final
matrix audit additionally asserts that both nonempty coordinator pages are persisted.

| Requirement | Executed evidence |
|---|---|
| Exact seven-day evidence | `test_exact_access_observation_is_seven_days_without_another_check`; 14 strict transport cases |
| Original definitions/reopen | `complete_baseline_original_definition`, `same_account_reopen`, `new_js_context_reopen` |
| Preserve pending/uncertain state | `pending_base_ids_conflict_verbatim`, `pending_create_only_enriched_without_acknowledgement` |
| Atomic failures and immutable collisions | `actual_transaction_abort_atomic`, `later_collision_aborts_earlier_row`, revision/definition collision cases |
| Partial/resumed pagination | `coordinator_two_pages_partial_resume_and_denial`, `partial_progress`, `empty_final_complete_no_deletion` |
| Account/session/denial fence | Foreign scope, cross-realm epoch, HTTP403, active abort and oncomplete predicate/signal cases |
| Expiry/clock recovery | Rollback/monotonic/expiry checks, persisted clock lock after reload and explicit newer online restoration |
| Bounded concurrent storage | `bounded_local_pages_125_rows`, `concurrent_imports_newer_wins`, initialization-abort cleanup |

Review addressed sixteen findings and rejected one proposed metadata-retention system
as unnecessary complexity without a demonstrated capacity failure. No new review work
was deferred. Fifteen review regressions were observed failing before fixes; pending-only
create preservation received a separate RED. Initial server RED source/test bytes were
saved before implementation; its retained log is explicitly a later exact-source replay.
The generated helper also has a retained behavioral RED before its correction.

An unchanged create test failed because its 40ms real deadline could expire before
Auth/client/worker setup reached the selected phase. It now expires the same ten-second
budget with its existing fake clock after that phase begins, retaining all ownership
and safe-timeout assertions. The original full-suite failure remains recorded. An
isolated failed-run log was overwritten by the follow-up runner; its tool-output excerpt
is labeled as such, alongside the complete independent full-suite failure.
