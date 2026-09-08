# Bible data repair

The importer fetched one page of verse IDs for a whole book, then silently skipped
words whose verse IDs were absent. The local API row limit is 1,000. Eight source
books exceed that limit. A regression with 1,200 verses reproduced exactly 1,000
imported words. The morphology loop separately expected dictionaries although the
source uses three-element lists. The live pre-repair audit failed at Genesis 1:
690 expected morphemes were absent.

## Repair and verification

From repository root, with `supabase` and `python-dotenv` installed:

```bash
python3 apps/scribeswell/tools/py/import_bible.py --source apps/scribeswell/scripts/hebrew.json --dry-run
python3 apps/scribeswell/tools/py/import_bible.py --source apps/scribeswell/scripts/hebrew.json
python3 apps/scribeswell/tools/py/import_bible.py --source apps/scribeswell/scripts/hebrew.json --verify-only
```

Use `--book Ps` for a selected book. Unknown or unavailable selections fail; they
never fall back to importing everything. Environment variables take precedence;
root `.env`, root `.env.local`, then backend `.env` supply missing values only.
Credentials are `SUPABASE_URL` and `SUPABASE_SECRET_KEY`.

The importer validates all selected input before writes, preserves existing IDs,
upserts by natural keys, and checks exact source-derived values and keys for chapters,
verses, words, and decoded morphemes. Pagination uses stable ordering and exact counts,
including when a server cap is smaller than the requested page. Counts changing
mid-read fail. A successful run means all selected records passed verification.

Writes are not one database transaction. An interrupted run can leave a partial
repair; it exits unsuccessfully and can be rerun. Unexpected extra records fail
verification rather than being deleted automatically. Avoid concurrent imports.
This verifies fidelity to the supplied source and existing morphology parser, not
independent scholarly correctness of that parser or source provenance.

The reader paginates words and returns HTTP 503 for empty/blank verses, gaps in word
positions, empty stored chapter lists, and missing morphology segments. Its existing
UI displays the error. A source audit remains necessary to detect missing trailing
words or entirely absent final chapters: continuity alone cannot prove completeness.
Unhandled API exceptions are logged server-side; credentials and stack traces are
not returned to the browser.

## Traceability

`tests/test_import_bible.py` covers row limits, pre-write validation, dry-run source
format, idempotency, read-only audit detection, invalid selection, and truncated
responses. `tests/test_reader_integrity.py` exercises the HTTP error contract and
multi-page reader data. The initial focused runs failed (3 importer tests and 2 API
tests), establishing the failures before the fixes.

Scaffold/shared UI: no changes; these are Scribeswell data rules. Agent context:
this document records fail-fast expectations; no generic workflow changes. ADR:
no platform architectural decision changed. Documentation: importer instructions
and this repair record supersede the stale tool path in the older technical overview.

## Observed result (2026-09-07)

Full repair and a separate read-only audit both exited 0. Verified 39 books, 929
chapters, 23,213 verses, 306,785 words and 471,674 decoded morphemes. Source SHA-256:
`c2d8e9e565be4ee69f938b444e5e0dc37fdfd0d9ccb185d1a5f8d95fab91c498`.
Exact command logs are in `verification/2026-09-07-data-{repair,audit}.txt`. The first
audit log's book counter is 0 because only the seeding branch incremented it; the
audit did compare all book values successfully. The reporting counter is fixed.
The affected suite passed: `python -m pytest apps/scribeswell/tests -q --disable-warnings`
with supabase, python-dotenv, pytest, fastapi, pydantic-settings and python-jose
installed through uv (8 passed; 13 third-party deprecation warnings).
