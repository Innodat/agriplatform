# Protected own-history pages — 2026-10-26

The candidate history endpoint extends current own-capture detail with bounded pages.
Each request rechecks current fixed-organization own-read authority and verified
account/durable actor before checkout. Returned records belong to the original owner
and retain their original questionnaire, current answers and stored attribution.
An inactive child or removed assignment does not remove still-authorized own history.

The caller supplies inclusive observation-date bounds and keeps them fixed while
traversing pages. The eventual phone consumer will calculate its default today plus
previous 29 calendar dates; this API does not guess phone time. Continuation uses
immutable server creation time and capture ID in descending order. Changed observation
dates or answers do not become ordering keys. Pages are separate current reads, not a
database snapshot; a refresh can be needed and missing rows prove neither deletion
nor loss of authority.

The cursor is a strictly validated, versioned base64url navigation value. Its decoded
account, organization, read mode, date filters and page limit must match the current
verified request. The database independently applies all authority/filter predicates.
The encoding is not a signature: an arbitrary valid position changes navigation only
within that authorized query. No cursor grants authority or authenticates a prior
request. This avoids a cursor registry, worker affinity, signing key or new service;
fingerprints/HMAC remain deferred.

Default page size is 30, maximum 100. A separate 2 MiB UTF8 response bound can reduce
the returned row count; continuation follows the last included record so the next
row is not skipped. Each full record retains the existing 512 KiB bound. A page
contains only completely validated records and uses safe errors instead of a
provisional or partly validated success. Readback does not acknowledge uncertain
writes, mark content Synced, merge an offline cache or renew an offline observation.

## Reproduction

Use the retained Node26.11.1 executable under
`platform/deployment/.local/kdg-toolchains/ad277eef-a10e-4aac-bb82-5743653fb2e0/payload/node/bin/node`
and Python under
`platform/deployment/.local/access-organization-check-20261022/owner-env/bin/python`.
The compiled Auth and loopback proofs require the approved npm capsule under
`platform/deployment/.local/web-baseline-qualification/new-5/root/node_modules`.
Owner API-client tooling is retained under
`platform/deployment/.local/scaffold-application/proof-dI2Gy9/root/platform/api-client/src/cli.mjs`.
Exact executed argument arrays, working directories, exit results and log hashes are
committed in the machine record, alongside pointers to the private source/log capsules.
There is no install or fresh provisioning qualification. The approved dependency
baseline, including TypeScript 7.0.2, remains unchanged.

## Requirement traceability and implementation evidence

| Requirement | Executed focused proof |
|---|---|
| Correct first/middle/final pages with tied creation times | `test_traverse_tied_original_history_without_loss` and actual loopback traversal |
| Inclusive dates, honest empty scope, default limit | `test_explicit_inclusive_dates_default_limit_and_empty_scope` |
| Cursor closure/binding and independent authority | `test_roundtrip_and_closed_binding`, `test_cursor_binding_is_checked_after_current_authority_before_checkout`, `test_changed_position_only_navigates_current_authorized_query` |
| Current authority on every page | `test_every_page_rechecks_denial_actor_setup_and_outage` |
| Original version/current revision after edit/unassignment | `test_current_revision_original_definition_after_edit_and_unassignment` |
| Row/byte continuation and microseconds | `test_byte_limited_pages_resume_without_skipping`, `test_microseconds_precede_inverse_uuid_order`, exact 2 MiB/+1 HTTP boundary |
| Strict safe request/error/timeout/cancellation | History HTTP body/query/bearer, failure-phase, release/serialization and exclusive-worker tests |
| No cancellation exception disclosure | Cancelled SQL/release canary tests plus private outcome representation test |
| Whole-page immutable client and Auth fences | Compiled history transport/entry tests and loopback late-header/body cases |

Initial implementation qualification passes 26 focused backend tests and 460 compiled
Auth/client tests, retaining the original 399 characterization cases. Thirteen actual
loopback requirement groups pass with synthetic authority/storage, 45 balanced
acquisitions/releases and five normal owned engine disposals; no forced stop occurred.
Four strict SQL-model fixture guards pass. Final coordinator commands, source/log
hashes and review dispositions are recorded in the
[machine record](evidence/own-history-pages-20261026.json).

Before implementation, `red-initial` captured exact stub/test/source bytes and hashes,
then observed two behavioral acceptance failures. Missing-import/compiler/sandbox
failures are retained as infrastructure evidence. The first post-extraction ESM
import-resolution check failed, then explicit compiled-module imports corrected it
without changing expected behavior. Separate retained cancellation canaries reproduced
Python3.15 shield exception/traceback logging, including raw SQL release context.

The app-owned worker now shields a private non-raising result/error outcome with a
redacted representation. It unwraps errors only for an uncancelled caller, preserving
existing safe HTTP mapping. Repeated cancellation still waits for exclusive worker
unwind; no acknowledgement or rollback claim follows cancellation. No loop-global
logging suppression or Python-internal patch is used. No equivalent builder-owned
shield helper exists; generated transaction/Auth owners remain unchanged.

## Qualification limits and impacts

Synthetic authority and SQL storage can establish control flow and wire agreement.
They do not establish actual PostgreSQL joins, permissions, rollback, driver
cancellation or TCP drain. Native original-version/join qualification remains a
separate prerequisite. There is no history UI, offline merge/observation renewal,
browser/editor/queue/default-startup activation, Leave, real accounts/Access,
DB/native/Docker qualification, migrations/provisioning, deployment/production/pilot
or cleanup in this delivery.

Scaffold: reuse existing Auth/transaction/schema-client owners; domain history stays
in KDG. Promote a neutral change only if its consuming behavior proves one is needed.
Shared UI and agent-context impacts: none. Documentation records current contracts
and exact evidence while preserving historical content. ADR impact: existing
decisions apply; no new platform decision or accepted ADR edit is needed.


Final post-review coordinator verification passes 276 synthetic backend cases, 461 compiled Auth/client
cases, 127 direct adapter/context/child cases and four fixture guards. Five strict
adapter configurations, ten owner schema/client freshness checks and four scaffold
parity checks pass under TypeScript7.0.2. The earlier standalone read transport suite
now runs against compiled output inside the Auth proof; its 52 cases remain covered.


Review preserves the finite maximum 101-row fetch strategy; the 2 MiB response bound
is not a 2 MiB process-memory promise. Production capacity and actual database behavior
remain unqualified. A streaming cursor framework was not added for an undemonstrated
resource failure. Incremental byte accounting removes repeated prefix serialization;
CPU-only construction happens after the read-only transaction completes.

Post-review focused coverage passes 36 backend and 62 added client cases (42 transport,
20 Auth entry). Direct handler validation/errors, between-page edits/inserts, malformed
cursor boundaries and the full degradation wire/schema cases are covered. Review
resolved ten findings, rejected one complexity increase with its rationale above, and
deferred one actual-PostgreSQL qualification group. Exact final commands and selected
source hashes are recorded alongside the preserved pre-review evidence.
