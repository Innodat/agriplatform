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
