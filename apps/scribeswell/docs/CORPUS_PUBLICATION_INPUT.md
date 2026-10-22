# Publication command input qualification

`backend/corpus_publication_input.py` implements the pure input prerequisite in the
[canonical owner contract](../../../_bmad-output/specs/spec-scribeswell-studies/corpus-publication.md#publication-command-qualification-contract).
That contract owns exact wire fields, limits, reason pairing and future execution
semantics. This module uses only the standard library and the existing pure source
validator. It performs no file, environment, credential, database or network access.
It supplies no CLI or output artifact.

## Python API

With `apps/scribeswell/backend` on the Python import path:

```python
import json
from corpus_publication_input import parse_command, prepare_command

# The caller supplies complete source_raw bytes and a separately reviewed
# expected_source_sha256 from approved artifact metadata.
body = {
    "schema_version": 1,
    "operation_id": "12345678-1234-1234-1234-123456789abc",
    "command": "corpus.begin",
    "scope": {"kind": "source", "source_id": "tanakh"},
    "payload": {
        "expected_absent": True,
        "input": {
            "source_sha256": expected_source_sha256,
            "catalogue_version": "catalogue-v1",
            "versification_id": "versification-v1",
            "tokenization_version": "tokens-v1",
        },
    },
    "reason_code": "source_import",
    "evidence_ref": "release:approved-source/1",
}
raw = json.dumps(body).encode("utf-8")
command = parse_command(raw)
qualified = prepare_command(raw, source_raw)
assert qualified.command == command
assert qualified.counts.books == 39
```

`parse_command(raw: bytes) -> Command` returns `BeginCommand`, `RecoverCommand` or
`SealCommand`. Each exposes `schema_version`, `operation_id`, `command`, `scope`,
`payload`, `reason_code` and `evidence_ref`. `SourceScope` exposes `kind` and
`source_id`; each payload's `input` is a `PublicationInput` with `source_sha256`,
`catalogue_version`, `versification_id` and `tokenization_version`. `BeginPayload`
contains `expected_absent`; `RecoverPayload` and `SealPayload` contain
`expected_generation` and `expected_attempt_id`, retained as canonical strings.

`prepare_command(raw: bytes, source_raw: bytes) -> PreparedCommand` parses first,
then recomputes the complete source candidate for every variant, including seal.
The result contains exactly `command`, `counts: SourceCounts` (books, chapters,
verses, tokens) and `source_candidate_sha256`, the SHA-256 of the existing canonical
serialized source candidate. It retains no raw scripture or candidate inventory.
All returned records are frozen, slotted dataclasses with suppressed payload repr;
no mutable caller-owned data is retained. Direct construction of these records does
not validate them and establishes no authority.

Malformed commands raise `CommandValidationError`, whose `code` and string are
always `corpus_publication.input_invalid`, without decoder exception chaining or
submitted details. Command bytes are bounded to 65536. Closed objects, exact types,
ASCII identities/evidence, canonical lowercase nonnil UUIDs, lowercase SHA-256,
positive canonical bigint generation strings and command/reason pairing follow the
owner contract. Duplicate keys, floats/constants, BOM, invalid Unicode, NUL,
unknown/missing fields and actor/time/ready overrides fail safely. Source failures
retain the existing safe `source_evidence.*` identifiers. Candidate/audit JSON cannot
substitute for complete raw source; checksum and complete inventory are revalidated.

## Remaining execution gates

Prepared values prove only input qualification. They do not prove current authority,
database correspondence, execution, a sealed audit or publication. Identity owns
external verification of the stable classified service actor and preparation
provenance. A future controller must map the actual original database login to that
verified executor and enabled exact-command/source authority in protected owner
state, with current revocation checks. No supplied actor, role name, GUC, credential
or evidence file verifies identity. A human initiator needs separate trusted
verification. No general Scribeswell service-actor projection is delivered.

Caller principals/grants, actor setup, controlled execution/recovery, replay/outcome
storage, writer transition, audit sealing and ready-manifest activation remain
separate gates. Dormant migration replay and the importer/API are unchanged. This
is an ST-38 prerequisite, not completed publication acceptance.

## Verification and impacts

Requirement-to-test coverage is in `tests/test_corpus_publication_input.py`: all
three variants and reason pairing; envelope/scope/payload/input closure and types;
byte/string/UUID/digest/generation limits; safe malformed JSON/Unicode failures;
immutable records and caller mutation; command-before-source ordering; changed,
incomplete and candidate/audit source rejection; full checked-in artifact; and a
fresh standard-library-only interpreter with forbidden import/I/O probes.

Create the app-local Python 3.12 environment using the
[existing setup instructions](CORPUS_EVIDENCE.md#qualification-and-remaining-gates),
then run from the repository root:

```sh
apps/scribeswell/.local/audit-venv/bin/python -m pytest \
  apps/scribeswell/tests/test_corpus_publication_input.py \
  apps/scribeswell/tests/test_corpus_evidence.py -q
```

The delivery run observed the expected missing-module acceptance failure before
implementation. The delivery record records focused results, review strengthening
and final application regression with exact commands; skipped database cases do not
count as qualification.

Scaffold, shared UI and agent context require no changes or promotion. Documentation
is this app-local API guide; accepted ADRs are unchanged. No migration, release,
HTTP/browser or cross-service contract behavior is introduced. The delivery record
owns final regression evidence and outstanding publication gates.
