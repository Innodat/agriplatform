# PtS implementation verification — 24 September 2026

The deployment target is the existing Supabase project. No live Supabase changes,
reader grants, storage upload or public deployment were performed. PostgreSQL 17
on localhost:55439 is an isolated disposable test fixture only. Its identity tables
are minimal contract fixtures; this does not establish compatibility with every
policy in an existing Supabase project. All source documents were treated as data.

## Content evidence

`/tmp/pts-venv/bin/python -m apps.pts.tools.verify_archive` and the same command with
`--root /mnt/c/wycliffe/PtS/PtS_Poetry_Library` verified 264 files / 222,505,940 bytes
against `reference/copy-manifest.json`. Both copies match exactly. The original is
unchanged. No poems were fetched or invented. Canonical counts are 312 records,
190 with text, 33 assistant-checked complete transcriptions, 275 witnesses and
19 source/rights pairs. No baseline discrepancy was found. Historical README/audit
counts remain intact as reference history. Thirteen source-less general reference
documents are preserved and exposed as collection references.

## Commands and results

- `python3 tools/py/run_compose_supabase.py --check-only`: passed; no generated
  assets changed, legacy migration composition remains intact.
- `npm run build --prefix apps/pts/web`: TypeScript and Vite passed. Final JS chunk
  is approximately 519 kB / 146 kB gzip; Vite emits its advisory 500 kB chunk warning.
  Restricted catalogue text/documents are not bundled.
- `PTS_TEST_DATABASE_URL=postgresql+psycopg://postgres:pts-disposable@127.0.0.1:55439/postgres PTS_TEST_RUNTIME_URL=postgresql+psycopg://pts_runtime:pts-disposable@127.0.0.1:55439/postgres /tmp/pts-venv/bin/python -m pytest apps/pts/tests -q`:
  **24 passed in 2.14 seconds**. Credentials in this command are disposable fixture
  values only. One dependency deprecation warning concerns Starlette/AnyIO's
  BlockingPortal alias, not a failed test.
- `LD_LIBRARY_PATH=/tmp/pts-browser-libs/usr/lib/x86_64-linux-gnu npm run test:browser --prefix apps/pts/web`:
  12 reader/session tests passed on desktop and mobile. After adding the final
  navigation/static-boundary cases, the same command with `-- --grep 'launcher works'`
  passed 2 further cases: **14 browser cases verified**. Synthetic catalogue and
  mocked Auth/directory/PtS responses are used; these are not live provider tests.
- App-directory TestClient preflight checks for localhost:5179 (PtS) and :5174
  (existing Scribeswell): both passed, preserving the existing allowed origin.
- `git diff --check`: passed.

Browser prerequisites were downloaded/extracted into a temporary directory because
this machine lacks libnspr4/libnss3/libasound. No system package installation was
performed. Install Playwright Chromium and its normal dependencies in CI; the
LD_LIBRARY_PATH workaround is specific to this environment. Desktop/mobile screenshots
were inspected; test screenshots contain only synthetic fixtures and stay in /tmp.

## Acceptance traceability

| Requirement | Verification |
|---|---|
| Exact baseline, IDs, text, history, rights/witness relationships | test_collection baseline; test_archive manifest; test_postgres full loaded library equality |
| Idempotent imports and retained reviewed content | test_postgres replay/conflict assertions; incoming versions retained |
| Current access, revocation, outages, organization isolation | test_api protected routes/outage; test_services membership revocation; real restricted roles, pooled rollback and concurrent organization tests |
| Stored documents through PtS HTTP | persisted attachment → real ContentClient → content TestClient, capability result and denied read assertions |
| Upload integrity and recovery | sealed-byte replay, retained canonical document precheck, atomic audit failure injection, explicit failed-identity replacement and signed-URL redaction tests |
| Search, all filters, direct links, copy, exports, notices | pure/API checks with actual library plus desktop/mobile Playwright flows |
| Session recovery and prior-user protection | same-user 401 refresh, account replacement, late parsed response and clipboard-rejection Playwright cases |
| Mobile filter Apply/Close/Back and navigation | provisional selection tests; browser Back/Forward; no horizontal overflow |
| Public asset protection and shared navigation | real Vite /@fs archive request denied 403; static route lacks collection; shared launcher link verified |
| Safe migration release | actual owner migrations; failure halts later owners; CLI evidence remains activation_allowed=false; owner revisions/outcomes and no evidence overwrite tests |
| Frontend contract consistency | generated OpenAPI DTO drift test and TypeScript build |

## Review and execution notes

Three independent BMAD review lenses found and triaged 19 findings; resolutions are
recorded in SPEC.md. Fixes preserve the original scope and existing platform work.
Additional regression tests exposed a mobile filter close/refresh bug and signed-URL
exception leakage; both were fixed. One interrupted test artifact had trailing NUL
bytes and was repaired before final execution. The first pure collection
implementation preceded a runnable failing test while dependencies were unavailable;
this is an ATDD process deviation. API absence and later review regressions were
observed as failures before their corresponding fixes; no unexplained expected
result was changed to dismiss a failure.

The initial fixture and temporary tools disappeared between sessions; verification
was rerun after recreating them. `tools/prepare_test_database.py` makes the fixture
reproducible and refuses existing initialized databases. It is not a deployment tool.

## Before activating against Supabase

1. Review/bootstrap separate owner/runtime/import credentials and apply the narrow
   identity-owner bridge to the selected Supabase project; verify current membership
   policies with actual Entra/Supabase tokens and revoked membership/grants.
2. Run coordinated Alembic migrations with a fresh evidence path. Reports distinguish
   `migrations_complete` from activation authorization and capture partial outcomes.
   Verify compatibility/recovery against the actual prior project state.
3. Configure a private Storage bucket, global and bucket limits of at least 128 MiB,
   S3 credentials and allowed origins. Run the read-only bucket configuration checker.
   Test the actual 85 MiB source, SHA-256 preservation, 900-second upload and
   300-second read expiry, clock tolerance, in-flight transfers and staging replay.
   Mock S3 tests do not prove these provider-specific behaviors.
4. Assign explicit Reader permissions to approved existing organization members,
   import canonical JSON and upload declared source documents through the content
   service. Re-run end-to-end access/document checks before activation.

Source notices and reuse restrictions remain authoritative reference information;
authentication, noncommercial intent and assistant checks confer no additional rights.

## Versioned reader cache and compact layout (2026-11-05)

PtS explicitly persists only collection, individual-poem and Sources corpus JSON.
The list opts into `lean=true` (`citations={}`); default API reads, fresh copy citations,
exports and private-file routes retain their existing contracts. No authentication,
source-rights or file-custody decision is cached. Every conditional route checks
current account capability before a 304. Weak validators include account, selection,
semantic projection version, schema and all represented source/rights evidence;
volatile export-generation timestamps are excluded. Changes download a new body.

The helper keys by app/API/account/query/format, checks payload shape and bounds all
PtS entries to four / 4,000,000 estimated UTF-16 bytes. Corruption, quota and unavailable
storage fall back to network/memory. Confirmed denial, sign-out and account/session
replacement clear protected state/cache and invalidate late writes. Ordinary view
navigation only clears the view. A new load never displays persisted bytes during
an access outage. Browser storage removal remains best effort if storage is blocked;
a future display still requires current server authorization.

Focus/visibility checks coalesce while in flight and within one second. Existing
poems, filter state, scroll and open details remain while a conditional read runs.
A reserved accessible status line prevents text movement. Token rotation revalidates conditionally
instead of downloading an unchanged collection. One 60-second total deadline bounds fetch, auth
refresh and body parsing; obsolete filter/navigation reads are aborted and cannot
replace the latest result. Retry starts a fresh bounded request.

The reader keeps one header identity, removes the repeated title/purpose paragraph,
and collapses optional result statistics. Per-poem usage, text quality, sources,
licence evidence, references and citation/export actions remain available. Domain
layout stays local; shared loading guidance and the opt-in helper are documented in
`platform/docs/development/browser-caching.md`. No scaffold generator/schema switch,
agent-context change, accepted ADR edit, migration, corpus mutation or deployment.
This is an ordinary compatible backend/frontend release; activate the backend first
to get conditional reuse (the lean query is additive and old readers remain supported).

Read-only local corpus projection measurements (compact JSON, not hosted network):
33 research poems 334,666 → 261,157 bytes (22.0%); 190 texts 2,055,827 → 1,452,034
(29.4%); 312 all entries 2,634,481 → 1,825,134 (30.7%). These compare existing full
responses with omitted duplicate citations. They do not establish live latency or
proxy behavior. Native TestClient and HTTPS browser mocks prove authorized 304 and
reuse semantics; no production provider or live-service latency was exercised.

Executed evidence (Node 24.11.1 / npm 11.19.1; Python 3.12):

- Red: synthetic `apps/pts/tests/test_reader_cache.py` — 7 expected failures for
  missing validators, lean projection and CORS. Browser cache/layout checks failed
  on both projects; hung-body checks failed to stop loading before the deadline fix.
  Helper tests first failed on the missing module. Missing psycopg was resolved in
  isolated `/tmp/pts-reader-driver`; native TestClient/local HTTPS required sandbox
  escalation. No repository dependency or production environment was changed for it.
- `npm test --workspace @platform/browser-cache` — 5 passed. Scope/version/bounds,
  corrupt/quota/unavailable storage, shape checks, authorized conditional reads,
  cancellation/deadlines and stale completion guards.
- `PYTHONPATH=/tmp/pts-reader-driver python3 -m pytest apps/pts/tests/test_reader_cache.py apps/pts/tests/test_api.py apps/pts/tests/test_research_use.py apps/pts/tests/test_collection.py apps/pts/tests/test_contracts.py apps/pts/tests/test_archive.py -q`
  — 38 passed. Native authenticated 304 bodylessness, current denial/outage, changed
  text/rights/source/schema/projection, scoped validators, full/lean compatibility,
  export rights/citations, original corpus preservation and generated DTO consistency.
- `npm run test:browser --prefix apps/pts/web` — 178 passed, desktop/mobile. The final
  stable run covers filter/navigation/actions, conditional reload/focus/visibility,
  resize/scroll/disclosures, delayed 304 geometry, changed data, denial, token rotation,
  account replacement, malformed/quota caches, late writes and all existing private
  file/auth cleanup recovery. A virtual clock proves 30 seconds remains allowed and
  a hung body stops at 60 seconds, Retry works and latest filter selection wins.
- `npm run build --prefix apps/pts/web` — TypeScript/Vite passed; existing >500 kB
  bundle warning remains. New helper has its own TypeScript config because inheriting
  the stale root target initially failed on missing `apps/receipts-web`.
- `PYTHONPATH=/tmp/pts-reader-driver python3 -m apps.pts.tools.generate_contracts --check`
  — passed; DTO schema did not change, so generated files were not edited.
- `python3 tools/py/run_compose_supabase.py --check-only` — coordinator verified pass:
  15 migrations, 2 seeds, 5 function directories; no files changed or migrations run.

The first broad browser run exposed incomplete legacy empty-collection cleanup mocks
without the existing contract's `witnesses` array. Those payloads now include the full
empty response fields; protection assertions stayed unchanged. Removing the token
dependency initially left same-account cleanup recovery blank; preserving token-driven
conditional revalidation fixed it. A stable targeted recovery run passed 14 cases and
the final broad run passed all 178. No expected outcome was weakened. Tests prove
consumer behavior with doubles and native API transport, not live provider latency.


### Final review repairs and coordinator verification

All supported findings from three independent review lenses were fixed; none deferred.
Changed selections now clear old poems/counts/actions while same-selection revalidation
preserves reading state. Cached acquisition plans/leads/contact fields are validated
before Sources reuse. Focus cannot admit corpus requests or restore bytes while provider
sign-out is pending. Contract-faithful browser fixtures prove the lean request, persisted
lean body and fresh complete citation; aggregate-byte eviction has behavioral coverage.
Red failures were observed before the filter/Sources/sign-out fixes.

After repairs, coordinator execution of `npm run test:browser --prefix apps/pts/web`
passed **192 desktop/mobile tests** (1.3 minutes); `npm test --workspace
@platform/browser-cache` passed **6**; frontend build and scoped whitespace checks passed.
The earlier coordinator native API/contract command passed **38**, and generated-contract
and database composition checks passed. Existing bundle-size and installed TestClient
deprecation warnings remain. No live hosted timing, provider change, deployment or
migration was performed. The BMAD delivery record contains the individual review triage.

### Runtime source inventory correction (2026-11-05)

Release preparation identified `backend/reader_cache.py` missing from the explicit
runtime `SOURCES` tuple. Adding it also includes it in provenance `INPUTS` and the
packager's owner-code copy. `apps/pts/tests/test_runtime_sources.py` derives the
entrypoint's direct backend imports and checks both inventories. The focused command
`python3 -m pytest apps/pts/tests/test_runtime_sources.py -q` first failed with exactly
that missing module, then passed (**1 passed**) after the one-entry correction.
No broad suites, generated-file edits, packaging or deployment were run for this
repair; actual frozen-package/image verification belongs to the coordinator's isolated
release candidate. Existing unrelated workspace changes were preserved.
