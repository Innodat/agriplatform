# Protected current own-capture readback — 2026-10-26

The candidate detail API extends the existing create/edit/recovery path with the
current original owner's saved observation and its original questionnaire. It is an
explicitly imported candidate, with an isolated Auth consumer; activation remains
separate. Readback does not acknowledge an uncertain operation or change local saved
state. Original operation receipt recovery continues to return the original revision.

Current fixed-organization own-read authority and verified account/durable actor
precede database acquisition. An owned capture permits its child label even after
unassignment/inactivation; create/edit grants and current eligibility are unnecessary
for this read. Stored original questionnaire content supplies questions, order, labels
and scale. Attribution uses stable stored actor identifiers; no actor-name lookup or
new identity authority is introduced.

## Reproduction

Use the already qualified Node26.11.1 executable under
`platform/deployment/.local/kdg-toolchains/ad277eef-a10e-4aac-bb82-5743653fb2e0/payload/node/bin/node`
and Python under
`platform/deployment/.local/access-organization-check-20261022/owner-env/bin/python`.
The selected-source Auth and loopback proofs require the retained approved npm capsule
`platform/deployment/.local/web-baseline-qualification/new-5/root/node_modules`.
The owner API client generator is retained under
`platform/deployment/.local/scaffold-application/proof-dI2Gy9/root/platform/api-client/src/cli.mjs`.
These proofs do not install dependencies or qualify fresh provisioning. The approved
dependency baseline, including TypeScript7.0.2, remains binding.

## Requirement traceability

| Requirement | Focused evidence |
|---|---|
| Current own detail and original definition | `ReadAcceptance.test_current_own_detail_contains_original_definition_and_provenance` |
| Current revision independent of old receipt | `test_after_edit_current_revision_is_independent_of_receipts` and loopback create/edit/read/recover journey |
| Read after assignment removal | `test_read_ignores_assignment_active_and_create_eligibility` |
| Own account and organization isolation | `test_missing_and_foreign_have_same_safe_404` and explicit scoped SQL predicates |
| Current authority before checkout | `test_denial_and_bad_actor_never_select`, `test_current_denial_prevents_pool_checkout`, safe upstream setup/authentication tests |
| Strict private HTTP boundary | `test_closed_query_and_identifier`, `test_exact_bearer_header_and_challenge`, `test_nonempty_body_refused_before_authorization` |
| Safe failure for invalid storage | `test_bad_storage_never_publishes_partial_snapshot` |
| Deadline, cancellation and exclusive connection ownership | `test_expired_worker_retains_ownership_until_each_phase_unwinds`, `test_cancellation_keeps_checkout_sql_and_release_owned`, release/lifespan cases |
| Bounded immutable client snapshot and stale Auth suppression | `read.test.mjs` and `read-entry.test.mjs`, including exact 512 KiB UTF8 boundary, account replacement, malformed responses and bounded ignored transport |

## Executed evidence

Before review, focused implementation verification passed 36 Python cases (8 handler, 23 HTTP, 5
schema/wire), 44 transport cases and 18 Auth consumer cases. The initial selected-source
Auth capsule passed 389 compiled cases under strict TypeScript7.0.2. The synthetic
loopback passes nine requirement groups, including create/read/edit/read, unchanged
original definition/receipts, assignment removal, indistinguishable missing/foreign
records and safe acquire/SQL/commit/release/invalid-storage failures. Three fixture
guards check SQL scope, stored provenance and answer-copy isolation.

The initial importable non-dispatching backend stub produced genuine behavioral
failures. Its actual stub and log are retained. Original test bytes were not captured
before implementation; a reconstruction is explicitly labelled and is not represented
as an immutable original. No preimplementation client/loopback RED is claimed. A later
year-zero response-validation regression has its own actual failing source capsule/log
and focused green result. Exact commands, source/log manifests, final coordinator
checks and review dispositions are recorded in the
[machine record](evidence/own-capture-readback-20261026.json).

## Qualification limits and impacts

Synthetic Access and SQL storage establish boundary/control-flow behavior and wire
agreement. They do not establish actual PostgreSQL permissions, constraints, rollback,
driver cancellation or TCP drain. Readback does not provide list pagination, offline
cache merging or read-observation renewal. No browser/editor/queue/default-startup
activation, Leave, real accounts/Access, native qualification, Docker, provisioning,
migrations, production/deployment/pilot or cleanup is included. Fingerprints/HMAC remain
deferred.

Scaffold: reuse existing Auth, transaction and schema/client generator owners; domain
readback stays in KDG. Shared UI and agent-context impacts: none. Documentation records
the contract and exact evidence while preserving prior contracts/handoffs/evidence.
ADR impact: no new decision; existing authorization, safe errors, attribution,
transaction and release safeguards apply.


Final coordinator verification passes 240 synthetic backend tests, 399 compiled
Auth/client cases (including 52 read transport and 20 read Auth cases), 179 direct
adapter/context/child cases and three fixture guards. Nine loopback groups pass;
33 acquisitions/releases balance, four owned synthetic engines dispose normally,
no forced termination occurs and source hashes remain unchanged during proofs.
All four strict adapter configurations, eight schema/generated-client freshness
checks and four scaffold parity checks pass with TypeScript7.0.2.

Independent review completed all three lenses: nine findings addressed, one rejected
against existing foreign keys/read policies, two findings combined into one deferred
native qualification prerequisite. Review fixes preserve compact multilingual original
definitions, normalize aware PostgreSQL timestamps to UTC, align Python whitespace
semantics and integer error metadata, finish response serialization before the last
budget check, prove exact 512 KiB/+1 wire bytes and fence all Auth result branches.
There is no network-completion deadline promise.

Earlier aggregate coordinator harness limits and one unchanged 40 ms edit-test setup
failure are retained in the machine record. The final 240-case suite passed without
altering that test or its expected behavior. Protected dependency/startup hashes,
79 historical evidence files and the historical contract/handoff bytes are preserved.
