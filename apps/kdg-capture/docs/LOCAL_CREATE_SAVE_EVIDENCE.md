# Atomic local create Save — synthetic candidate

This delivers the storage portion of approved Story1.5 and the setup persistence
needed by Story2.2. It does not complete either story or activate an editor, sender,
installed PWA or application startup.

## Implemented contract

`openHistoryStore` now upgrades the local database additively to schema3. Existing
records, opaque pending/conflict fields and definitions survive supported v1/v2
upgrades. `beginSetupRefresh` issues a durable scoped generation/nonce before HTTP;
`importProvision` accepts only the latest outstanding ticket and a validated actual
Provision response. Older responses cannot restore newer known denial; HTTP denials use the same durable
ticket comparison, so an older403 cannot lock newer successful setup. Immutable
questionnaire collisions abort the import. Nullable denial has no fabricated server
timestamp: request ordering handles publication, while original positive Access
observations retain their own times.

`openCreate(child_id)` pins the original questionnaire, child, assignment/reference,
account/actor/membership and exact read/create observations in memory. It writes no
unfinished answers. `saveCreate(reviewed, identities, input)` copies completed input
before awaits, validates the original questionnaire and generated create-command
shape/131072 UTF8-byte bound, excludes hidden false details, and commits local capture,
immutable create action and definition atomically. Distinct caller-provided capture
and operation UUIDs identify one attempt. Exact committed-result retries use current own-read and recover that attempt even
after original create/child expiry; new writes retain all creation checks.
changed reuse and collisions refuse. Multiple records for the same child/date remain
valid. No server revision, server audit timestamp or Synced state is invented.

Initial Save requires current exact read, selected create and child evidence; the
original pinned observations still expire independently. Own-edit is not required
for initial Save. Known create denial does not remove independent read authority. Scoped child loss
invalidates earlier open forms, retains its freshness floor through failed writes,
and requires newer verified evidence for fresh selection. Equal-generation durable
restoration wins over a stale process latch; strictly newer process failure still wins.
`read` exposes local content under `local_capture`, separate from actual `baseline`;
`readCreateActions` is scoped and bounded (default30/max100). Existing server-backed
edit operations refuse pending-only creates. Pending-create editing/delivery follows
separately, using the original immutable create operation.

`createSetupEntry` is an explicit unmounted Auth consumer. One lease, original total
deadline, session fence and abort signal span ticket acquisition, HTTP, import and
publication. It releases the lease on success/failure. A current partition denial invalidates the
owned handle; explicit restoration reopens the store and constructs a fresh entry.
No automatic request or sender is added.

## Verification and custody

Final commands, registered matrix checks, source hashes and retained failed/green
frames are recorded in `evidence/local-create-save-20261026.json`.
The focused proof uses actual isolated Chromium IndexedDB; the integration proof uses
the actual synthetic Python Provision HTTP endpoint through Auth into IndexedDB,
then Save/reopen and original-identity retry. It also exercises total timeout during HTTP and queued IndexedDB import/denial,
lease release, stale403 ordering, current durable denial/reopened restoration, safe
authorization outage and explicit retry without losing pending input.

Characterization of original-answer validation precedes extraction into the shared
KDG `validateAnswers`; affected read/Auth/storage proofs protect existing behavior.
Old selected-source capsules explicitly include new transitive Provision/create
imports. Historical proof files and earlier source capsules remain retained.

## Five delivery impacts

- Scaffold: existing builder-owned IndexedDB primitives reused unchanged. New domain
  permissions, questionnaire and command policy remain in KDG; no neutral defect
  requires a template change. Existing scaffold parity remains required.
- Shared UI: unchanged; this is an unmounted storage/consumer feature.
- Agent context: unchanged; existing owner and synthetic-scope guidance suffices.
- Documentation: this evidence, append-only contracts, README and prepended handoff.
- ADR: no new decision; existing scope, lifecycle, attribution, error, session and
  compatibility decisions govern this implementation.

## Limits and release prerequisites

Synthetic Auth/Access and database fixtures establish no actual PostgreSQL privileges,
rollback, native-driver performance or provisioning readiness. Prior native setup
issuance follow-up remains unchanged. Local schema3 is additive but older schema2
code cannot open it: browser update/connection coordination remains a release gate.
Real device eviction, physical durability and at-rest behavior are not qualified.
No cleanup/reset, dependency change, Docker work or real-account access occurred.
TypeScript7.0.2 remains the approved compiler. Fingerprints/HMAC remain deferred.

## Qualified result

All15 affected source-bound commands pass:141 focused Chromium IDB checks,18 integrated
setup HTTP/Auth/IDB groups,87 setup-client tests,73 edit delivery/29 delivery HTTP,
103 reconciliation,92 local edit Save,61 history,575 compiled Auth/client tests and
16 existing HTTP groups, plus five scaffold parities. The source capsules compile
strictly with TS7.0.2. Existing342 backend tests (313 prior plus29 Provision) are reused
with all85 effective backend/test sources unchanged; none is native qualification.

Two independent three-lens review rounds completed.27 individual finding rows have
24 addressed and three rejected with specific evidence; no new deferral. Concrete RED
frames precede the stale403, cross-command identity, ticket replay, edit-denial/collision,
queued-denial deadline and cross-page restoration corrections. One non-frozen Code Map
clarification re-derived the implementation while preserving all positive tests.

| Matrix row | Registered final evidence |
|---|---|
| Save/reopen | atomic_create_saved; fresh_realm_reopen_recovers_original_content_and_identity; actual completed capture/reopen groups |
| Setup ordering | published_setup_ticket_consumed; cross_realm_refresh_generation_blocks_older_positive_after_denial; actual older HTTP denial group |
| Pinned form | opened_questionnaire_survives_refresh; original_definition_and_reference_pinned; refresh_never_extends_original_token_expiry |
| Retry/multiplicity | same_attempt_retry_after_reopen; same_child_date_distinct_records_allowed; create_expiry_*_exact_committed_result_recovers |
| Validation | required_false_saved; hidden_details_removed_before_identity_without_mutating_caller; exact_create_utf8_limit_supported; invalid_wire_unicode_refused |
| Authority | independent expiry cases; child_omission_*; current_read_membership_change_blocks_pinned_create; second-page denial/restoration groups |
| Atomicity | record_action_atomic_rollback; inflight_account_change_leaves_no_action; create_expiry_true_initial_completion; actual queued publication deadline groups |
| Compatibility | populated_v1/v2_*; stale_handle_refuses_after_versionchange; unknown_newer_local_schema_never_reset; unsupported rows retained/paginated |

All earlier handoff/contracts bytes remain unchanged beneath the prepend/append.
170 protected files including root dependency manifests/lock, startup/Auth owners and
historical KDG documents retain their baseline hashes. Concurrent Scribeswell commits
remain the parent history; no unrelated changes are included in this local delivery.
