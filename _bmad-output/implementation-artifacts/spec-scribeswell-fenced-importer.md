---
title: 'Bind corpus importer transactions to approved attempts'
type: 'feature'
created: '2026-10-26'
status: 'done'
route: 'oneshot'
review_loop_iteration: 0
context: []
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

Connect the existing Bible importer to the dormant database writer fence. An explicitly supplied source/attempt/generation/checksum binding must be validated before writes and bound on the same database transaction before book seeding and every chapter's writes. Fenced mode qualifies the exact full 39-book source bytes against the approved checksum before applying an optional single-book repair. No later source reread may change what was approved or reported. Stale/rejected binding fails the write rather than continuing unbound. Read-only verification and dry-run never bind or mutate.

Preserve legacy unbound invocation while enforcement remains off, existing ID-preserving upserts and chapter rollback boundaries. This does not enable enforcement, grant execute permission, provision callers, claim successful publication, or implement a competing Access path. Add focused application-side tests; actual database permissions/concurrency/migrations and integration remain deferred to the agreed final phase. All unrelated working-tree changes are preserved.

</frozen-after-approval>

## Implementation Notes

- Existing Database.transaction binds nested repository calls through ContextVar, yields no connection; use Database.connection inside it for the fixed parameterized bind_corpus_write call. seed_books currently writes outside any transaction and needs one bounded transaction. import_book already has one transaction per chapter.
- Optional immutable ImportBinding with closed validation plus four all-or-none CLI flags. Fenced writes require run() to qualify one bounded byte read through existing full source qualifier before enabling writes. Internal import_book/seed_books may not bypass that qualification. Legacy callers are unchanged. No statement or grant added to old migrations.
- Footprint: importer, new focused test file, existing contract addendum and delivery evidence. No intent gap or irreversible action; no shared UI/scaffold/agent-context/ADR change. App-specific behavior only. Read-only investigation confirmed closed epoch can support a later sealed-audit interval; that separate transition remains pending.

- Baseline `/tmp/scribeswell-implementation-python/bin/python -m pytest -q apps/scribeswell/tests/test_import_bible.py`:12pass3.10s. New test collection initially failed for absent ImportBinding; explicit model stub yielded15genuine failures2.11s. Implementation27pass2.17s; expanded tests found qualification guard occurring after old inventory validation (1fail32pass), corrected to reject direct fenced writes before reads;33pass4.13s.
- Independent review5rows: four verified correction roots, one premature finalization claim rejected. Before corrections the wider importer/manifest/highlight/input suite242pass12.78s. Six review-directed genuine failures1.88s demonstrated five publication-qualification bounds and unsafe morphology stderr. Reused full-source qualifier with local discarded preflight labels;41importer tests pass3.37s including actual Database ContextVar wrapper connection reuse and post-write chapter rollback.
- Final `/tmp/scribeswell-implementation-python/bin/python -m pytest -q apps/scribeswell/tests/test_fenced_importer.py apps/scribeswell/tests/test_import_bible.py apps/scribeswell/tests/test_corpus_manifest.py apps/scribeswell/tests/test_highlight_evidence.py apps/scribeswell/tests/test_corpus_publication_input.py`:250pass6.87s exit0; runner8.41s,11source/test before-after hashes equal. Exact argv, result and fingerprints retained in apps/scribeswell/docs/evidence/fenced-importer/. No browser build necessary for Python-only changes.
- Environment-only offline installation in temporary Python3.12 venv restored psycopg/psycopg-pool/python-dotenv and python-jose dependencies from cache. First optional reader-integrity attempt failed collection for missing jose. After installation its rerun stalled without result; exact owned PID86902 did not exit on SIGINT, so SIGTERM stopped it. Cause unverified; no reader/API pass inferred. No native SQL, migration, credentials, actual owner integration or KDGports used. Previously open anonymous mobile-scroll failure retained.

## Review Triage Log

- Medium / patch: fenced preflight used weaker validate_book bounds than publication; five red boundary cases, reuse full-source qualifier, now pass.
- Medium / patch: malformed approved morphology could escape through CLI traceback; red secret-marker stderr proof, safe ImportBindingError normalization, now pass.
- Low / patch: fake repository did not prove actual ContextVar connection reuse; actual Database wrapper with fake pool now asserts one lease and bind/write on same connection, without native enforcement claims.
- Low / patch: binding refusal tests did not prove failure after writes; late morpheme fault rolls back that chapter, retains previous chapter and books, clears run qualification.
- False: missing final evidence/status was observed during in-progress review, before finalization; no completed-delivery claim existed then. Final exact commands/results and requirement map are now retained.
