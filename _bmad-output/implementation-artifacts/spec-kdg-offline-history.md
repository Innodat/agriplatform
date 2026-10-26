---
title: 'KDG atomic offline own-history consumption'
type: 'feature'
created: '2026-10-26'
status: 'done'
baseline_commit: 'f31ab11a6e38a458eee191864b9fcc41f83afea1'
route: 'dispatch'
review_loop_iteration: 0
context:
  - '/home/ck/repos/innodat/agriplatform/AGENTS.md'
  - '/home/ck/repos/innodat/agriplatform/apps/kdg-capture/AGENTS.md'
  - '/home/ck/repos/innodat/agriplatform/apps/kdg-capture/docs/OWN_HISTORY_PAGES_EVIDENCE.md'
---

<frozen-after-approval reason="user authorizes continued implementation without repeated internal approvals">

## Intent

The candidate history API has no local consumer or exact offline read observation.
Implement its connected offline foundation: successful pages carry verified seven-day
own-read evidence and an isolated KDG IndexedDB consumer commits history safely for
same-account reopening. This is the persistence part of approved Story2.1, not its UI.

## Boundaries & Constraints

Always use the same current verified Access evidence as the successful page, including
account/actor/membership, organization and own-account scopes, literal own-read
permission, decision ID, checked_at and expires_at exactly seven days later. Existing
entry Context remains explicitly not an offline lease. Current server authorization
and deadlines remain unchanged. No local clock can manufacture server evidence.

Commit complete validated page baselines, immutable definitions, download progress and
exact read observation atomically in ordinary IndexedDB transactions. Newer revisions
win; immutable creation/owner/child/version facts and definitions cannot change. Pending
local content, IDs, base snapshots and conflict data survive imports verbatim. A history
download never acknowledges an operation or marks pending work Synced. Missing rows
never delete data. Explicit date bounds remain fixed; provide a phone-calendar helper
for today and previous29 dates. Empty, partial, unavailable and complete remain distinct.

Pin account/org and session generation through transaction completion. Known denial
locks persisted viewing while retaining data; logout closes access and prevents late
unlocks. Reopening same-account cached data requires a valid exact stored observation,
wall-time sanity and monotonic elapsed checks within a process. Expiry, rollback,
implausible clock or account mismatch fails closed. Outage does not become denial.
Only current verified own-read can explicitly restore a denied partition.

Synthetic local/CI only: isolated Chromium/IndexedDB fixtures are allowed. No UI/editor,
Leave, browser/queue/default-startup activation, service worker, actual PostgreSQL/native
driver/Docker qualification, real accounts/Access, provisioning, deployment/pilot,
production or cleanup. Preserve dependencies including TypeScript7.0.2, concurrent work
and historical evidence. Fingerprints/HMAC stay deferred. Never read/run/copy the
preexisting untracked `apps/kdg-capture/migrations/tests/schema_fixture.py`.

## I/O & Edge-Case Matrix

| Scenario | Expected behavior |
|---|---|
| Successful pages and offline reopen | Original definition/current permitted baseline readable under exact seven-day own-read observation; no stronger renewal |
| Repeat or older response | Deduplicate stable IDs; newer server revision/observation wins; immutable collisions refuse whole page |
| Existing pending overlay/conflict | Preserve local content, base/version references and IDs exactly; no receipt/queue changes |
| Partial download/empty final page | Atomic progress reflects only committed page chain; no missing-row deletion or false complete on failure |
| Abort/quota/invalid page | Prior committed cache/observation/progress survive; safe unavailable outcome, no partial success |
| Foreign namespace/late account/logout/denial | Refuse reading/import/unlocking; preserve locked work; current verified same-user recovery only |
| Expiry/rollback/restart | Enforce scoped observation and sane wall/monotonic time; no local renewal |
| Concurrent imports/session lock | Ordinary transactions serialize; stale execution cannot unlock or publish after fence |

</frozen-after-approval>

## Code Map

- `docs/contracts.md:170,220,370`, `docs/epics.md` Story2.1 AC2–6: owner truth.
- `write-candidate/capture_history.py`, `history_http.py`: same verified Context is available in `_transaction`; add closed observation to HistoryPage without a new Access call.
- `history_openapi.py`, `export_history_openapi.py`, `history-openapi.json`, `contracts/history-generated`: regenerate via owners only.
- `web/src/history.ts`, `history-entry.ts`, `read-validation.ts`: reuse closed whole-page validation/Auth fences; export validated page helper if necessary, no general SDK.
- No IndexedDB implementation exists. Introduce KDG-owned `web/src/history-store.ts` and optional small `history-download.ts` coordinator; ordinary version1 IDB schema, explicit caller-owned close/lock. Preserve local fields without introducing a queue producer.
- `web/tests/auth-proof.mjs`, `persistence-http-proof.mjs`, history transport/entry fixtures: synchronize new required observation and selected-source lists. Reuse retained Chromium and tool capsule for standalone `history-store-proof.mjs`; never whole-silo copies.

## Tasks & Acceptance

- [x] Extend server history observation DTO and exact Access-derived expiry with focused Python RED/green; owner-regenerate schema/client and update fixtures/contracts tests.
- [x] Extend strict client validation and implement isolated transactional store/download consumer plus focused type/behavior tests; observe behavioral ATDD failure before implementation.
- [x] Run actual isolated Chromium IndexedDB proof: reopen, atomic abort, preservation, revision/definition collision, scope/session/denial/time, progress and concurrent imports. Record source/log hashes and exact commands; no physical durability claim.
- [x] Run affected Python, compiled Auth/client, loopback, strict TypeScript and scaffold parity checks; root owns final docs/evidence/handoff, review and scoped commit, preserving other dirty paths.

Given a permitted page and protected pending work, when import commits and the store
reopens offline, then original questions and latest baseline are available without
changing pending work. Given invalid/stale/denied execution or transaction failure,
when import cannot commit, then no partial page, false completion or renewed authority
is exposed.

## Implementation Notes

No unresolved user intent or irreversible action. Use small direct application functions,
not a configurable cache engine. Exact DTO/store method names are engineering choices.
Scaffold: no existing offline store owner; domain logic remains KDG; assess any proven
neutral fixture for promotion with this consumer. Shared UI/context: none. Docs: update
current contracts/handoff/evidence preserving old bytes. ADR: inherited decisions;
no accepted ADR edits. Private evidence root is
`platform/deployment/.local/kdg-offline-history-20261026`; baseline hashes already saved.
Implementer may add a focused implementation-evidence JSON there and tests, but root
owns final evidence/docs/spec task status and commit. Do not stage/commit others' work.

## Spec Change Log

## Review Triage Log

## Verification

Use retained Node26.11.1, TypeScript7.0.2 approved npm capsule, existing Python owner
environment and API-client CLI from prior evidence. No installs. First RED snapshots
must capture exact test/stub bytes and output; infrastructure failures do not count.
Then focused TDD, affected full suites and four `sync-kdg-*.mjs --check` owners.
Record every matrix row's executed proof. Physical-device/at-rest/storage-eviction
and actual PostgreSQL behavior remain unqualified.

Reusable first-consumer promotion: request/complete IDB primitives and their generated
behavior tests live in builder templates under `application/web/offline-tools`, adopted
through `kdg-offline-pattern.ts` and `sync-kdg-offline.mjs`. Application rendering now
includes them and a local-storage test command; domain store policy remains KDG.
A concrete RED characterized premature error-event settlement before transaction
completion/abort. Root owns this isolated promotion; private evidence root-neutral-red.


Review layers completed before triage (verification layer started after a slot freed).

| Finding | Verdict / route | Evidence |
|---|---|---|
| B1 post-commit caller fence | medium / patch | Transaction helper's final check sees generation only; import signal/predicate can change after final request. Carry the existing execution check through actual completion and abort pending transaction on signal. |
| B2 fresh clock recovery blocked | medium / patch | Bad deltas retain old anchors, so a new verified page fails forever against them. Establish fresh anchors on explicit newer verified online import, retaining strict cached-read checks. |
| B3 clock lock lost on reload | medium / patch | Rejected decision IDs are memory-only; restored plausible clock after reload accepts old evidence. Persist the clock-lock marker and require fresh verified evidence to restore. |
| B4 stale handle lock/logout | medium / patch | lock invalidates shared generation before current/epoch checks, even for closed/superseded handle. Make stale cleanup idempotent, compare durable epoch before writing, retain protected fresh sessions. |
| B5 equal-revision contradictory content | low / patch | Equal revision returns early without checking date/answers/update attribution. Compare revision-governed values; keep independently mutable child labels separate. |
| B6 coordinator wrong-scope denial | medium / patch | Denial bypasses import's pinned namespace check. Pass pinned request scope to the existing denial operation and refuse mismatch before invalidating any generation. |
| B7 progress metadata retention | low / reject | Query/continuation metadata accumulates, but no everyday capacity failure is demonstrated. Adding automatic retention/cleanup policy here adds lifecycle branches, and user excludes cleanup; preserve records/progress and defer any concrete retention policy to its approved consuming work. |
| B8 unbounded partition read | medium / patch | Reading all retained rows is the only local read API and grows during ordinary repeated downloads. Use ordinary bounded IDB key-range reads with simple continuation; no general cache/query engine or pruning. Bound returned progress metadata too. |
| B9 initialization failure leaks handle | low / patch | Initial metadata read/completion lacks later transaction cleanup. Close opened handle and consume completion rejection on initialization failure. |
| B10 coordinator integration coverage | medium / patch | Existing coordinator proof exercises one page/outage only. Add multipage, later-page failure/resume, HTTP403 and commit-boundary cancellation. |
| E1 failed lock persistence | medium / patch | Generation alone does not stop newly opened same-process handles after lock metadata abort. Retain process-local known-lock latch until fresh verified restoration; report failed durable write as unavailable. No promise to persist information when storage refuses all writes. |
| E2 completion cancellation | medium / patch | Same verified root cause as B1; signal/predicate must fence final publication and pending transaction. |
| VG1 coordinator continuation unverified | medium / patch | Preverified mutation dropping cursor passes existing suite. Covered by B10's two-page request/commit assertions. |
| VG2 HTTP denial to local lock unverified | medium / patch | Preverified deletion of store.deny branch passes existing suite. Covered by B10's current/reopened handle and preserved-record assertions. |
| I1 throwing/late coordinator callback | medium / patch | Implementer inspection: direct isCurrent call can throw and denial branch omits final fence. Reuse safe current predicate and fence before denial/publication. |
| R1 direct validator null limit | low / patch | Exported validateHistoryPage reintroduces nullish default although transport refuses null. Keep identical strict pending validation at store boundary. |

Engineering corrections keep the existing read/import/deny APIs and frozen intent.
Bound local reads using ordinary prefix keyset/count arguments and a next key rather
than a query framework. Preserve native-browser evidence, immutable definitions,
local pending fields, exact observation, independent namespaces and ordinary close.

Additional matrix audit R2 — medium / patch: a pending-create-only local row has no
server baseline; unconditional stored.baseline comparisons abort valid readback.
Characterize that legitimate state, enrich its server baseline and preserve all pending
fields/operation identity without acknowledging uncertain commit.

Final source-bound verification: 277 backend, 475 compiled Auth/client,127 direct,4
fixture guards,13 loopback groups,61 IndexedDB checks; five strict TS configurations,
ten owner freshness checks, five scaffold parities and ten owner/renderer tests pass.
All17 findings triaged:16 addressed,1 low-complexity retention proposal rejected;
no new deferred work. Exact commands, traceability and source/log references are in
`apps/kdg-capture/docs/evidence/offline-history-20261026.json`. The root corrected a
demonstrated preexisting40ms scheduling assumption using the existing fake clock,
without changing production timeout/ownership behavior or expected outcomes.
