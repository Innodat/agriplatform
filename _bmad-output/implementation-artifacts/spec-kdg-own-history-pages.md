---
title: 'KDG protected own-history pages'
type: 'feature'
created: '2026-10-26'
status: 'done'
baseline_commit: '43e03e35c9c129eb2e472f677648e18a64f3b892'
route: 'dispatch'
review_loop_iteration: 0
context:
  - '/home/ck/repos/innodat/agriplatform/AGENTS.md'
  - '/home/ck/repos/innodat/agriplatform/apps/kdg-capture/AGENTS.md'
  - '/home/ck/repos/innodat/agriplatform/apps/kdg-capture/docs/OWN_CAPTURE_READBACK_EVIDENCE.md'
---

<frozen-after-approval reason="user authorized continuing KDG implementation without routine approval halts">

## Intent

Saved own-capture detail is available; history cannot yet be downloaded page by page. Add the protected history-page API, generated contract, isolated transport/Auth consumer and synthetic loopback proof using the existing original-definition detail semantics.

## Boundaries & Constraints

Recheck fixed-org `kdg_capture.capture.read.own` and verified account/actor before checkout on every page. Query only original-owner records, including inactive/unassigned children. Return current answers/provenance and exact original definition. No write acknowledgement, stronger authority or offline observation renewal follows a page.

Use explicit inclusive `from_date`/`to_date`, default `limit=30`, maximum100, optional cursor. The caller pins dates for the whole download (eventual phone default: today plus previous29 days); API never guesses phone time. Order descending immutable `(created_at,id)` with keyset continuation; date-only observations filter independently. Pages are not a cross-request snapshot; changes require refresh and absence never proves deletion.

Use a bounded canonical base64url JSON continuation with closed versioned shape, org/account/own-read/date/limit binding and last immutable tuple. Decode strictly and compare binding against current verified caller and validated query; all scope/filter predicates apply independently in SQL. This is untrusted navigation, not a signature or authority: changing position can only navigate the same currently authorized query. No HMAC, server cursor registry, TTL/worker affinity or cursor service. Explain this explicitly in current contracts.

Page envelope echoes bounds/limit, has full `CaptureDetail` items and nullable next_cursor. Bound actual UTF8 response to2MiB, each detail to existing512KiB and selected rows to limit+1. Return fewer items if needed for bytes, continuing after the last included item; no skipped row, partial item, false empty or lost continuation. One item plus envelope must fit. Use one original10-second budget through response construction/release, read-only worker ownership and safe private/no-store errors. Client accepts a page only after validating every item, order/filter/binding and continuation.

Synthetic local/CI only. No UI/editor/Leave, offline cache/observation renewal, browser/queue/default-startup activation, actual DB/native/Docker qualification, accounts/Access, migrations/provisioning/deployment/pilot/production or cleanup. Preserve concurrent work, historical evidence/resources and dependencies including TypeScript7.0.2. Fingerprints/HMAC remain deferred. Never read/run/copy/edit untracked `apps/kdg-capture/migrations/tests/schema_fixture.py`. Generated artifacts only through owners; no installs or broad native-importing tests.

## I/O & Edge-Case Matrix

| Scenario | Expected behavior |
|---|---|
| First/middle/final/empty page; tied creation times | Bounded deterministic descending own rows, exact continuation, honest empty final page |
| Fixed dates, old observations, edits between pages | Inclusive validated bounds; immutable ordering, current detail/original definition; no snapshot/deletion/receipt inference |
| Foreign account/org/filter/limit or malformed cursor | Safe typed422, no foreign data; current scope/filter always constrain SQL |
| Arbitrary valid own-scope position | Only rows satisfying current own account/org/date query; cursor grants nothing |
| Missing/denied/stale/setup/outage authority | Existing safe errors, authority before checkout, no provisional page |
| Unknown/duplicate query, body, invalid dates/limit/bearer | Strict bounded refusal, private/no-store |
| Row/byte cap and bad stored evidence | At least one valid fitting row, safe next page; invalid required evidence fails safely without partial success |
| Deadline/cancellation/release/serialization failure | Worker owns connection until unwind; no late/provisional page |
| Client malformed/duplicate/oversized/order/filter/identity mismatch | Whole page refused, no partial snapshot, retry/cache/write effects |
| Auth replacement and throwing caller getters | All results fenced before lease release; immutable current page only |

</frozen-after-approval>

## Code Map

- `docs/contracts.md` own-history and Pagination sections, `docs/epics.md` Story2.1: authoritative scope; offline/UI remain later.
- `write-candidate/capture_read.py`, `read_http.py`, `read_openapi.py`: reuse detail validation, current own-read, engine/private policy, bounded worker and final serialization check. No migration needed.
- `web/src/read.ts`, `read-entry.ts`: existing strict wire/immutable detail and execution lease; reuse domain validator without a generic runtime SDK.
- `web/tests/auth-proof.mjs`, `persistence-http-{fixture.py,proof.mjs}`: selected-source compiled Auth and actual loopback route/business-handler seam with synthetic storage.

## Tasks & Acceptance

- [x] Add `write-candidate/capture_history.py`, `history_http.py`, owner schema/exporter and focused `write-tests/test_history*.py`; scoped joined SELECT, typed cursor/filter/byte behavior and every matrix case.
- [x] Owner-generate `contracts/history-generated/`; add `web/src/history.ts`, `history-entry.ts`, strict type/runtime tests and adapter config. Preserve current detail behavior with existing characterization tests if extracting its local validator.
- [x] Extend selected-source Auth and loopback proof for multiple pages, dates/ties, current authority, original versions, byte continuation and late responses; no whole-silo copies.
- [x] Observe behavioral ATDD failure against an importable non-dispatching stub before implementation. Snapshot exact test/stub/source bytes plus hashes and logs before replacing it; then focused TDD. Missing imports/compiler failures are infrastructure only.
- [x] Root owns final evidence/JSON, appended current contracts, prepended handoff, scaffold/UI/context/docs/ADR impacts, complete verification/review and scoped local commit. Implementer reports exact sources/commands/logs and limits; no commit or final-doc edits.

**Acceptance:** Given authorized synthetic history, when a caller traverses actual HTTP pages, then it receives only correctly scoped current records with original definitions and resumes without loss at row/byte limits. Given failed or replaced authority, when a page completes late, then no stale/partial page is published. Existing create/edit/recovery/detail behavior stays protected.

## Implementation Notes

No unresolved intent gap or irreversible action. Cohesive cross-layer scope selected with bmad-help; continuation authorization covers routine gates. Internal names/error identifiers are implementer choices consistent with existing contracts.

Concrete qualification finding: retained Python3.15 shield logs raw worker exceptions after cancellation despite later retrieval. App-owned `capture_create_handler._complete_worker` must retain ownership while shielding a private redacted non-raising outcome, then unwrap outside shielding for ordinary error mapping. Characterize cancelled SQL canary leakage first; no loop-global suppression, runtime baseline change or generic worker framework. No corresponding builder template helper found.

## Spec Change Log

## Review Triage Log

All three fresh review layers completed before triage. The verification reviewer started after a slot became free; no findings were acted on before all layers returned.

| Finding | Verdict / route | Evidence |
|---|---|---|
| B1 explicit null limit | low / patch | `captured.limit ?? 30` normalizes runtime null to30 despite the declared integer input. Extend the existing invalid optional-value check and no-dispatch case. |
| B2 buffered result working memory | low / reject | `.all()` deliberately bounds selection to limit+1 (maximum101) before a bounded2MiB response. The report identifies finite excess working data, not an observed memory failure or a promised2MiB RSS bound. A new streaming cursor/memory framework adds complexity for no demonstrated everyday failure; preserve explicit limits and qualify capacity separately before activation. |
| B3 repeated serialization | low / patch | Candidate pages serialize the already included prefix again. Track encoded item byte counts and cursor/envelope overhead incrementally with the existing final exact serialization check; no new public surface. |
| B4 CPU work in read transaction | medium / patch | `_page` validates and repeatedly serializes after SELECT while the transaction remains open. Move CPU-only construction after read-only transaction completion; retained rows still describe the same SELECT and no authority/write behavior changes. |
| B5 between-page changes untested | low / patch | Existing edit case mutates before history read, not between pages. Add date-change/newer-insert continuation and refresh coverage for the declared non-snapshot semantics. |
| B6 direct handler path untested | medium / patch | New `HistoryHandler.execute` has validation/auth/context/error adaptation beyond the HTTP path, which bypasses it. Cover its public direct handler behavior with focused synthetic tests. |
| B7 degradation schema/wire coverage | low / patch | Actual history contract checks cover200/403/422; the changed endpoint's401/409/503/timeout families should also validate against the generated contract using existing safe-error fixtures. |
| B8 cursor boundary cases absent | low / patch | Existing decoder guards reject reversed dates, zero IDs and noncanonical1.0 version, but cases do not execute these distinct boundaries in both languages. Extend existing tables without adding production guards. |
| B9 next_cursor schema syntax | low / patch | Query cursor schema has base64url syntax; response cursor has lengths only. Apply the same owner metadata pattern to nullable next_cursor and add schema refusal cases. |
| B10 exact commands only ignored manifest | medium / patch (root) | Public JSON points to private argv/cwd/results. Keep exact command arrays and results in tracked evidence as well as hashed private logs; this permits reproduction after restoring approved tool capsules. |
| E1 null page item misclassified | low / patch | `Object.keys(null)` throws TypeError before the closed-object validator, producing verification_unavailable for known malformed data. Validate the object before property access, with a whole-page invalid_response case. |
| VG1 native history selection | medium / defer | Preverified gap: SQL-string doubles implement own filtering and cannot detect a new active-child/assignment predicate in real SQL. Actual PostgreSQL qualification is explicitly excluded; retain native own-scope/original-version/keyset/unassignment cases as an activation prerequisite. |


## Verification

Use retained Node26.11.1 and Python from readback evidence, owner API-client CLI and approved npm capsule; no install. Private evidence root: `platform/deployment/.local/kdg-own-history-pages-20261026`.

Focused behavioral RED/green, strict TypeScript7.0.2, schema/client owner freshness, full compiled Auth `--unit-only`, selected loopback proof and four scaffold `sync-kdg-{auth,write,database,native-database}.mjs --check`. Backend regressions explicitly name the17 synthetic modules in readback evidence plus new history modules; exclude schema/native/commit qualification modules. Allow realistic harness time for schema subprocesses; retain failures without changing unexplained expectations. Native SQL/permissions remain unqualified.

Final qualification: 276 synthetic backend, 461 compiled Auth/client, 127 direct and
four fixture cases pass; thirteen loopback groups pass with normal shutdown. All five
strict TypeScript7.0.2 configurations, ten schema/client owner checks and four scaffold
parity checks pass. Final source hashes stayed unchanged throughout verification.
Ten review findings addressed, one rejected with evidence, one native qualification
group deferred. Tracked command/results and exact private source/log capsule references:
`apps/kdg-capture/docs/evidence/own-history-pages-20261026.json`. No activation or native
qualification claim; frozen scope/accepted decisions and historical evidence preserved.
