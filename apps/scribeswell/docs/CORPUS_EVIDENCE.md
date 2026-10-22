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

From the repository root, create a Python 3.12 environment and install the app's
backend dependencies plus pytest. These commands require Python 3.12 with venv
and package-index access; they do not depend on a prior session's `/tmp` files:

```sh
python3.12 -m venv apps/scribeswell/.local/audit-venv
apps/scribeswell/.local/audit-venv/bin/python -m pip install -r apps/scribeswell/backend/requirements.txt pytest
```

Run the affected suites with that environment:

```sh
apps/scribeswell/.local/audit-venv/bin/python -m pytest \
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
retain product authority. Sealed database audit, writer fencing, migration,
restricted grants, source activation, coherent reader snapshots and live publication
proof remain gated. No skipped database test counts as database qualification.

Impact decisions: source tooling and tests remain app-local; scaffold/shared UI and
agent context require no changes. No ADR decision changes. This document describes
the executable tool and does not create a second feature lifecycle.

## Read-only database audit candidates

`tools/py/audit_corpus_database.py` is an explicit checkout/operator tool using the
app's psycopg dependencies; it is not installed in the runtime image. Supply the
same seven options as the source builder and set `SCRIBESWELL_AUDIT_DATABASE_URL`
in the invoking environment to the existing `scribeswell_runtime` login URL.
The tool does not load dotenv, accept a command-line URL, switch roles, create
roles/grants, or change the source, importer, schema, public API or database rows.
Remote URLs retain the repository's runtime TLS validation. Actual `current_user`
must be `scribeswell_runtime`, with neither SUPERUSER nor BYPASSRLS. The
parent validates the URL and Unicode before launching a worker. Worker connection
settings come only from the validated URL and fixed bounded options: all ambient
libpq `PG*` environment variables are excluded, along with
`SCRIBESWELL_AUDIT_DATABASE_URL`. Credentials still pass through private stdin.
The shared runtime repository configuration is unchanged.
Before reading inventory, the auditor conservatively checks that the four relations
are base tables and row-level security cannot hide rows. Where RLS applies, an
applicable literal-true permissive SELECT/ALL policy and no applicable restrictive
SELECT/ALL policy are required, including PUBLIC and effective role policies.
Otherwise `database_audit.visibility_unproven` is returned; RLS is never bypassed.
Controlled owner schema/policy DDL must remain stable during an audit. Concurrent
corpus DML is supported; concurrent owner DDL has not been qualified.

```sh
apps/scribeswell/.local/audit-venv/bin/python apps/scribeswell/tools/py/audit_corpus_database.py \
  --source apps/scribeswell/scripts/hebrew.json \
  --expected-source-sha256 c2d8e9e565be4ee69f938b444e5e0dc37fdfd0d9ccb185d1a5f8d95fab91c498 \
  --source-id oshb-candidate \
  --catalogue-version tanakh-candidate-v1 \
  --versification-id oshb-candidate-v1 \
  --tokenization-version oshb-export-candidate-v1 \
  --output /tmp/scribeswell-database-audit-candidate.json
```

Source evidence is rebuilt from the raw artifact and explicit checksum/labels
before connecting; an existing candidate file is never accepted as proof. After the visibility guard succeeds and while controlled owner DDL stays stable,
the comparison reads all owned book/chapter/verse/word rows, including orphans, in one
explicit `REPEATABLE READ READ ONLY` snapshot. It requires complete book metadata,
exact chapter/verse inventories, positive unique IDs, valid parent relationships
and denormalized coordinates, contiguous positions and exact bounded surfaces
matching each source token digest. Lemma/display/morpheme qualification remains
with the importer. Changed text with reused IDs fails; regenerated IDs with equal
tokens pass and appear as newly observed IDs.

Reads use server cursors with batches at most 1,000 and limits of expected rows
plus one. Hard source/database ceilings are 39 books, 6,000 chapters, 50,000 verses
and 1,000,000 tokens. SQL projects text only when at most 2,048 UTF-8 bytes;
excessive fields fail instead of crossing the connection or being silently
truncated. Connect timeout is 5 seconds, lock timeout 3 seconds, idle transaction
timeout 15 seconds and each statement wait at most 15 seconds or remaining budget.
A supervised disposable worker also bounds DNS, connection and transport stalls
within the 60-second database workflow deadline. Credentials travel through
private stdin, never process arguments. Timeout kills and reaps the worker;
connection closure abandons its snapshot. Only the parent creates the destination,
after successful worker exit. No file operation occurs inside the snapshot.

The closed output has `kind: scribeswell.database_audit_candidate`, `version: 1`,
`publication: false`, the four labels, `source_sha256`, equal `counts`,
`source_candidate_sha256` (SHA-256 of canonical serialized source candidate), and
canonical ordered verses. Each verse retains source fields and adds ordered
`observed_word_ids` as positive decimal strings. There are no source bodies,
credentials, timestamps, revision IDs or activation claims. Compact sorted-key
UTF-8 JSON plus one newline is deterministic, capped at 64 MiB.

Creation and cleanup reuse the source tool's atomic create-only behavior and
reconciliation rule above, including `source_evidence.output_cleanup_failed`
after a complete destination may already exist. Source/filesystem diagnostics keep
their `source_evidence.*` identifiers; audit failures use fixed
`database_audit.configuration_invalid`, `authority_invalid`, `visibility_unproven`, `corpus_mismatch`,
`source_counts_exceeded`, `database_unavailable`, `deadline_exceeded` or
`output_too_large` identifiers. Success prints `database_audit.candidate_created`.
No arbitrary exception text is exposed.

The guarded database tests require `SCRIBESWELL_TEST_DATABASE_URL` pointing only
at a fresh disposable localhost PostgreSQL cluster. They refuse existing fixture
roles (`anon`, `authenticated`, `service_role`, `scribeswell_runtime`,
`scribeswell_import`), create one unique database and only those absent roles, and
remove owned resources. A fixture administrator must be able to create/drop the
database and these roles; never use a production or shared developer cluster.
Before running, explicitly set `SCRIBESWELL_TEST_DATABASE_URL` to that fresh
disposable local cluster's administrator URL (database path included). This is a
separate fixture credential from `SCRIBESWELL_AUDIT_DATABASE_URL`; omitted fixture
configuration skips database tests and does not qualify the audit. Run in the
Python 3.12 environment created above:

```sh
apps/scribeswell/.local/audit-venv/bin/python -m pytest \
  apps/scribeswell/tests/test_corpus_database_audit.py -q
```

This independently qualifies a historical source/database observation only.
Existing writers remain unfenced: a concurrent write may commit while the audit
successfully observes the old coherent snapshot. A later audit detects changed
surfaces. Writer fencing, sealed audit, controlled publication/activation and
reader evidence remain separate ST-37/ST-38 gates. App-local tooling/tests and this
owner document change; scaffold/shared UI, agent context and ADRs require no change.
