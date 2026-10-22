# Source evidence candidates

`tools/py/build_source_evidence.py` builds reproducible evidence from one explicitly
selected full OSHB source artifact. It uses the standard library only, also with
Python `-S`, reads no dotenv files, imports no database modules and opens no provider
or database connections. It never changes the source or importer write behavior.

Run from the repository root, choosing reviewed identity/version labels and a new
output path. The labels below illustrate explicit choices; the tool does not register
or approve them:

```sh
python3 -S apps/scribeswell/tools/py/build_source_evidence.py \
  --source apps/scribeswell/scripts/hebrew.json \
  --expected-source-sha256 c2d8e9e565be4ee69f938b444e5e0dc37fdfd0d9ccb185d1a5f8d95fab91c498 \
  --source-id oshb-candidate \
  --catalogue-version tanakh-candidate-v1 \
  --versification-id oshb-candidate-v1 \
  --tokenization-version oshb-export-candidate-v1 \
  --output /tmp/scribeswell-source-candidate.json
```

The reviewed checked-in artifact contains 39 books, 929 chapters, 23,213 verses and
306,785 tokens. The checksum binds the exact bytes read, hashed and parsed once.
Matching it establishes artifact continuity, not scholarly provenance or permission.

## Output contract

The UTF-8 JSON object has `kind: scribeswell.source_evidence_candidate`, `version: 1`,
`publication: false`, the four supplied labels, `source_sha256`, `counts` with
`books/chapters/verses/tokens`, and an ordered `verses` array. Each verse contains
`book` (the owning metadata's OSIS ID), `chapter`, `verse`, `token_count` and
`verse_token_digest`. Ordering follows `corpus_source.BOOK_METADATA`, then chapter
and verse, regardless of the source object's key order. Serialization uses compact
sorted-key JSON and one final newline. There are no clocks, UUIDs, raw scripture
bodies, database IDs, source revisions or publication state.

`backend/corpus_evidence.py` owns the reusable `encode_verse_tokens` and
`verse_token_digest` functions. Their positional payload is:

```text
["scribeswell.verse_tokens.v1",source_id,catalogue_version,versification_id,
 tokenization_version,book,chapter,verse,[[1,exact_surface_he],...]]
```

Encoding is compact UTF-8 JSON with `ensure_ascii=False`, no newline/BOM, standard
JSON escaping and SHA-256 lowercase hexadecimal output. Slashes, punctuation,
diacritics and combining-mark order are preserved without normalization. Database
word IDs and revision are outside the digest. The six synthetic conformance vectors
in `tests/fixtures/verse-token-digests-v1.json` are unchanged from the canonical
Studies planning vectors; they prove bytes and hashes, not biblical reference truth.

## Validation and filesystem behavior

- Source bytes: at most 32 MiB, strict UTF-8 JSON, no duplicate keys or non-JSON
  numeric constants; exactly the 39 known English book keys.
- Metadata and pure-encoder book IDs: ASCII `[A-Za-z0-9][A-Za-z0-9._:-]*`, at most
  64 characters. These are representation checks, not a complete reference catalogue.
- Nonempty chapter/verse/word lists; chapters 1–150, verses 1–176, tokens 1–512.
  Tokens explicitly enumerate contiguous integer positions 1…N; booleans fail.
- Every source word field (surface, Strong and morphology) must be nonempty,
  valid Unicode scalar text and at most 2,048 UTF-8 bytes, checked before decoding.
  Source words inherit the importer's three-string layout, exactly one Hebrew
  surface field and morphology checks recognizing POS and layout. These checks
  are permissive about feature completeness and whitespace segments; they do not
  validate the complete morphology grammar. Either historical surface/Strong order
  is accepted. The candidate proves exact surface continuity, not full morphology
  validity. Pure encoding applies the same byte bound to each surface.
- Expected checksum: exactly 64 lowercase hexadecimal characters; it must match
  before parsing. Structure and all verses validate before destination creation.

Output is create-only: a complete flushed/fsynced temporary file in the destination
directory is atomically hard-linked to the requested path. An existing file, directory
or symlink is never replaced. The temporary file is removed using its owned path;
unrelated files are untouched. The output directory must exist and support hard links.
Write/read/validation failures exit nonzero with a `source_evidence.*` identifier on
stderr, without source content or arbitrary exception details. Success prints
`source_evidence.candidate_created`. Argument errors exit 2; other failures exit 1.

`source_evidence.output_cleanup_failed` can occur after the complete destination has
already been linked: cleanup of its owned temporary file failed. Inspect the existing
destination, or recompute with the same source checksum and labels to a new path and
compare the bytes with the existing file. Never overwrite or delete the destination
automatically to recover from this error. Unrelated files remain untouched.

## Qualification and remaining gates

Run the affected suites with the repository's isolated test environment:

```sh
/tmp/scribeswell-studies-tests-py312/bin/python -m pytest \
  apps/scribeswell/tests/test_corpus_evidence.py \
  apps/scribeswell/tests/test_import_bible.py \
  apps/scribeswell/tests/test_word_inspector.py \
  apps/scribeswell/tests/test_reader_integrity.py \
  apps/scribeswell/tests/test_lexicon.py \
  apps/scribeswell/tests/test_direct_database.py -q
```

The candidate is only the source-artifact prerequisite for CAP-4/CAP-9 and ST-37/ST-38
subsets. The canonical Studies [data contract](../../../_bmad-output/specs/spec-scribeswell-studies/data-and-saving.md)
and [publication proposal](../../../_bmad-output/specs/spec-scribeswell-studies/corpus-publication.md)
retain product authority. Full independent database audit, writer fencing, migration,
restricted grants, source activation, coherent reader snapshots and live publication
proof remain gated. No skipped database test counts as database qualification.

Impact decisions: source tooling and tests remain app-local; scaffold/shared UI and
agent context require no changes. No ADR decision changes. This document describes
the executable tool and does not create a second feature lifecycle.
