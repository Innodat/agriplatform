---
title: Reproducible Scribeswell source evidence candidate
type: feature
created: 2026-10-22
status: done
route: dispatch
review_loop_iteration: 0
baseline_commit: 30bce003e8a1c51c0c07cb3fb729ca54dedf6271
context:
  - AGENTS.md
  - _bmad-output/specs/spec-scribeswell-studies/data-and-saving.md
  - _bmad-output/specs/spec-scribeswell-studies/corpus-publication.md
---

<frozen-after-approval reason="Continuation authorized by user: happy, next; bounded implementation authorization persists">

## Intent

Build the read-only source-artifact prerequisite for exact highlight evidence (CAP-4/CAP-9, ST-37/ST-38 subsets). Produce reproducible per-verse digests from an explicitly selected full source artifact, using one reusable `verse_tokens.v1` encoder. Canonical Studies companions remain the product contract. This delivery provides a source candidate, never published database proof.

## Boundaries & Constraints

Always preserve exact `surface_he`, including slashes, diacritics and combining-mark order. Use the canonical compact UTF-8 positional JSON array and SHA-256 in data-and-saving; exclude database IDs/revisions. Reject noncontiguous positions, bool-as-int, empty tokens, invalid Unicode and malformed identities. Pure encoding validates representation/bounds only; source inventory/approved checksum qualify its input, not a complete independent reference catalogue.

Never connect to a database/provider, load dotenv, import database dependencies in the new CLI/library, alter scripture/source data or change importer write/transaction behavior. No Access, factory, signup, private writes, public API, migration, publication state, `source_revision` or database word IDs. Preserve other sessions' changes. Matching an artifact hash proves continuity, not scholarly provenance, authorization or active corpus state. Full database audit/fencing/publication remains gated.

## I/O & Edge-Case Matrix

| Scenario | Input | Required result / failure |
| --- | --- | --- |
| Encoding | Six existing synthetic vectors and valid explicit positional tokens | Exact fixture bytes and hashes; no Unicode normalization; changed text/order/context changes digest; IDs/revision are absent inputs |
| Malformed encoding | Duplicate/gapped/reordered/bool positions, empty sequence/surface, surrogate or invalid metadata | Safe validation failure, no partial result |
| Candidate | Full 39-book artifact, expected lowercase SHA-256, four explicit identity/version labels | One deterministic ordered verse inventory; exact raw checksum, counts, token counts and digests; no raw scripture bodies |
| Incomplete/unapproved source | Missing/extra/duplicate books, malformed words/structure/UTF-8/Unicode, checksum mismatch or excessive input | Reject before any destination write; no candidate or publication claim |
| Output | New destination / already-existing destination / write failure | Atomic create-only output; never overwrite another file; remove only owned temporary artifacts; stable safe error code and nonzero exit on failure |
| Isolation/compatibility | CLI with Python -S and no credentials; old importer public symbols | New CLI runs with standard library only; importer decoder/metadata/errors/dry-run behavior preserved under characterization |

</frozen-after-approval>

## Code Map

- `apps/scribeswell/tools/py/import_bible.py`: owns 39-book metadata, `is_hebrew`, `BibleImporter.decode_word`, `validate_book`; imports psycopg/dotenv today. Extract pure source definitions while retaining compatible importer names/static wrappers and error behavior. Keep run/import/write code unchanged.
- `apps/scribeswell/backend/services/oshb_morph.py`: existing canonical pure decoder; tools/py/oshb_morph.py is its compatibility wrapper. Reuse this owner module.
- `apps/scribeswell/backend/corpus_source.py` (new): extracted source metadata/decoder/validation, standard-library dependencies only.
- `apps/scribeswell/backend/corpus_evidence.py` (new): pure canonical encoder/digest and source-candidate builder.
- `apps/scribeswell/tools/py/build_source_evidence.py` (new): read-only CLI, bounded loading, safe reporting and atomic create-only output.
- `apps/scribeswell/tests/test_import_bible.py`: six baseline regressions; add characterization before extraction.
- `apps/scribeswell/tests/test_corpus_evidence.py` and `tests/fixtures/verse-token-digests-v1.json` (new): executable conformance; promote the six canonical planning vectors unchanged into an app-owned fixture so tests do not depend on untracked planning files.
- `apps/scribeswell/scripts/hebrew.json`: 13,096,412 bytes; reviewed SHA-256 `c2d8e9e565be4ee69f938b444e5e0dc37fdfd0d9ccb185d1a5f8d95fab91c498`; expected 39 books, 929 chapters, 23,213 verses, 306,785 tokens. Read-only input, never rewrite.

## Tasks & Acceptance

- [x] Characterize exact/swapped Hebrew source fields, slash/diacritic preservation and invalid morphology before extracting pure code. Preserve existing importer tests.
- [x] Add subprocess acceptance for the missing CLI and observe failure before implementation; add focused encoder/validation tests first.
- [x] Implement source-only candidate envelope: `kind: scribeswell.source_evidence_candidate`, `version: 1`, `publication: false`, explicit `source_id/catalogue_version/versification_id/tokenization_version`, `source_sha256`, counts (`books/chapters/verses/tokens`), ordered `verses` entries (`book/chapter/verse/token_count/verse_token_digest`). No clocks/UUIDs; deterministic compact sorted-key JSON plus newline. Order by current owning BOOK_METADATA then chapter/verse, regardless of source mapping order.
- [x] CLI requires `--source`, `--expected-source-sha256`, the four metadata labels and `--output`. Read/hash/parse the same bounded bytes once; reject duplicate JSON keys. Limits: source 32 MiB, metadata ASCII `[A-Za-z0-9][A-Za-z0-9._:-]*` including hyphen, at most 64 characters; chapters 1..150, verses 1..176, at most 512 tokens/verse and 2048 UTF-8 bytes/surface. These are qualification bounds, not scholarly canon validation. Explicit metadata labels are not registered/approved merely by this tool.
- [x] Prove all matrix rows, source isolation and full checked-in artifact output; run affected importer/decoder/backend regression checks. No skipped database tests may count as database qualification.
- [x] Write `apps/scribeswell/docs/CORPUS_EVIDENCE.md` with output contract/commands/limits/gates; root updates canonical memlog/companions and delivery evidence, preserving existing changes.

**Acceptance:** Given approved source bytes and explicit labels, when the CLI is executed twice to different new files, then output bytes and all expected counts match, and neither source nor database is modified. Given malformed or mismatched input, when invoked, then it exits nonzero with safe diagnostic identifiers and creates no output. Given ordinary importer callers, when source decoding/import regressions run, then existing behavior is unchanged.

## Implementation Notes

No product intent gap or irreversible action is needed. Footprint is app-local source parsing/evidence/tool/tests/docs. Scaffold/shared UI: none; app-factory remains owner work. Agent context: no root change. ADR: existing source-integrity/release boundaries unchanged. Documentation: canonical companions plus executable app contract; no duplicate feature lifecycle. Source candidate is upstream of independent full database audit and current publication proof, never a new authority path.

Test Python: `/tmp/scribeswell-studies-tests-py312/bin/python` (Python 3.12, isolated pytest/owner backend dependencies installed). Root baseline: importer six cases passed in isolated uv; direct system pytest initially lacked psycopg. Python 3.12 importer/word-inspector baseline: 11 passed, one existing Starlette/httpx deprecation warning. Root owns canonical updates and this delivery record; implementation agent owns app files/tests/docs. No extra workflow activation; root rendered bmad-build exactly once for this run.

## Verification

Implementation agent observed characterization green (12 importer cases) before extraction and 10 expected failures for the missing CLI/encoder before implementation. Final core command:

`/tmp/scribeswell-studies-tests-py312/bin/python -m pytest apps/scribeswell/tests/test_corpus_evidence.py apps/scribeswell/tests/test_import_bible.py apps/scribeswell/tests/test_word_inspector.py -q`

Result: 61 passed, one existing Starlette/httpx deprecation warning, 12.90s. Includes two full-artifact runs under Python `-S`, empty environment, exact counts/checksum and identical output. No database/publication or scholarly verification claim.

Broader agent command added `test_reader_integrity.py test_lexicon.py test_direct_database.py`; it stalled at the first HTTP TestClient case after the core checks and was interrupted (exit 130). Isolated `timeout 25 /tmp/scribeswell-studies-tests-py312/bin/python -m pytest apps/scribeswell/tests/test_reader_integrity.py -vv -o faulthandler_timeout=10` timed out (exit 124) in Starlette `TestClient.__enter__` / AnyIO `run_sync_from_thread`. No production HTTP code changed; root qualification follows. `git diff --check -- apps/scribeswell` passed.

## Review Triage Log

All three reviews reported before triage. Blind/edge reviewers received only the task diff; edge alone also received this delivery account. New verification-review launch hit the host thread limit, so the completed account-entry agent was reused with explicit instructions to disregard its unrelated account context; it had no source implementation context. Edge review returned no findings. Each filed finding is judged independently below, before grouping.

| Finding | Verdict | Evidence and route |
| --- | --- | --- |
| B1: NUL filesystem arguments bypass safe failures | false | The reviewed CLI is invoked by OS argv; NUL cannot be present in an exec argument. Python subprocess rejects it before the CLI starts. Calling main with synthetic argv is not a demonstrated CLI input. No new guard for an unreachable case. |
| B2: morphology can allocate millions of objects | medium | Confirmed parse_morph_code allocates one dataclass per slash segment and decode_word materializes each as a dict. A below-32-MiB malformed word can amplify memory before its surface is checked. Patch: bound every source word field to 2048 UTF-8 bytes before decode (current maxima in codepoints are 27/12/18), and test no decoder invocation on oversized fields. No importer policy change. |
| B3: recognized POS does not validate full morphology grammar | low | Confirmed existing decoder accepts partial feature strings; compatibility intentionally preserves it. Patch documentation to name importer-compatible recognized POS checks and explicitly disclaim complete morphology feature validation; do not change existing importer grammar. |
| B4: whitespace-only morphology segment passes | low | Confirmed parser trims/skips whitespace segments, inherited unchanged. Same documentation correction as B3 states this permissive boundary. Strict morphology revalidation is not required for exact source surfaces and would change the preserved decoder contract. |
| B5: no directory fsync/crash durability | false | Output contract promises atomic create-only visibility, not persistence through host/filesystem crash. Temp-file fsync plus hard-link establishes complete visible file without replacement; the candidate is reproducible. No unsupported crash-durability claim is made. |
| B6: unlink failure after successful link has uncertain completion | low | Confirmed finally can report output_cleanup_failed after a complete destination was created. Patch: test that branch and document destination inspection/recompute-to-new-path comparison, no overwrite or automatic deletion. Existing safe identifier remains. |
| B7: duplicated synthetic fixtures lack automatic canonical equality | false | Root compared decoded fixture objects: all six are identical. Promoting them to app-owned executable truth deliberately removes the dependency on pre-existing untracked planning files; canonical documentation will reference the executable fixture and retain the historical planning artifact. Runtime test must not depend on untracked planning state. |
| V1: emitted CLI digests lack independently pinned expectations | medium | Pre-verified gap: helper goldens bypass candidate integration and existing CLI assertions check counts/order/reproducibility only. Patch tests to independently pin output digests for actual slash-bearing multiword source and distinct coordinates/labels; mutation to display_he must fail. |
| R1: lexicon metadata AST consumer broken by extraction | medium | Root full affected run: 84 passed, two existing lexicon failures in corpus_bounds (StopIteration) because it searched importer AST for moved BOOK_METADATA. Patch the existing caller to consume the extracted pure metadata directly; retain existing expected outputs. Repository-wide Python/JS reference search found no other AST metadata consumer. |

Survivor groups: bounded pre-decoder source fields (B2); permissive morphology documentation (B3/B4); cleanup-result qualification (B6); candidate digest integration verification (V1). All are small app-local patches, add no public surface and guard demonstrated states. No intent gap, spec loopback or deferred work.

## Final verification and traceability

Root reproduced the HTTP stall on an extracted tracked baseline under `/tmp` using the same bounded reader command (exit 124); outside the sandbox, `timeout 45 /tmp/scribeswell-studies-tests-py312/bin/python -m pytest apps/scribeswell/tests/test_reader_integrity.py -q` passed 2 tests in 0.63s. No HTTP production workaround or dependency change was introduced.

The first full root affected command completed with 84 passed / 2 failed (18.74s): both lexicon regressions explained by R1. The same exact command after the caller fix passed **86 tests, no skips**, one existing Starlette/httpx deprecation warning, **24.39s**:

```sh
timeout 60 /tmp/scribeswell-studies-tests-py312/bin/python -m pytest apps/scribeswell/tests/test_corpus_evidence.py apps/scribeswell/tests/test_import_bible.py apps/scribeswell/tests/test_word_inspector.py apps/scribeswell/tests/test_reader_integrity.py apps/scribeswell/tests/test_lexicon.py apps/scribeswell/tests/test_direct_database.py -q
```

Executed outside sandbox after demonstrated TestClient restriction. These tests use in-memory owner repositories/test clients; no actual PostgreSQL test was run and no skip is counted as qualification. No frontend surface changed, so no frontend/browser suite was rerun for this slice.

| Requirement | Actual evidence |
| --- | --- |
| ST-37 encoding prerequisite | Six unchanged executable fixture vectors; invalid identity/coordinates/positions/Unicode tests; independent Node compact-JSON/SHA-256 recomputation of all six plus both CLI hashes passed. |
| Source comparison prerequisite to ST-37/ST-38 | Full checked-in artifact subprocesses under `-S`, `env={}`; two byte-identical candidates; 39 books / 929 chapters / 23,213 verses / 306,785 tokens; unchanged reviewed source SHA-256. Synthetic multiword/slash-bearing Gen 1:1/1:2 emitted hashes independently pinned. |
| Validation/output safety | Checksum, duplicate keys, JSON/Unicode/structure/bounds, oversized pre-decoder fields, missing source, arguments, existing/symlink output, injected destination race, write failure and cleanup-after-link tests. Root race test passed 1/1 before full run. |
| Compatible extraction | Characterization before refactor; existing importer/word inspector, reader, lexicon full-rebuild and direct database adapter regressions passed. Lexicon AST caller updated to pure metadata; standalone `python3 -S apps/scribeswell/tools/py/build_lexicon.py --help` passed. |
| Review fixes | Same implementation agent patched B2/B3/B4/B6/V1 (4 focused tests passed) and R1 (2 existing failing tests passed); root inspected patched diff and rewrote task-only review diff, then ran final affected suite. No deferred findings. |
| Documentation/context | Canonical bmad-spec log/companions updated, preserving all 11 CAP and 38 ST IDs; app tool contract documents bounds, operator labels, cleanup and remaining publication gates. No scaffold/shared-UI/agent-context/ADR change required. |

New source-word qualification bound applies to all three fields before decode; pure encoder surface bound remains 2048 bytes. The extracted importer intentionally preserves its existing permissive morphology behavior. Real database fencing/audit/publication, catalogue/provenance approval and Access account contracts remain open. Canonical updates live within the pre-existing untracked planning tree and remain excluded from the task-only commit, as with the preceding slice; other sessions' changes and pre-existing app README edits are untouched.
