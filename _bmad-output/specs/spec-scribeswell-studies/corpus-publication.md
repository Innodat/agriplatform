# Corpus publication and highlight evidence — proposed contract

Derived from the Studies decision log and inspected source/importer/repository.
**Owner:** Scribeswell corpus/import and reader API; D-2/D-5. **Status:** publication
and reader proof remain proposed. Source/database-audit candidates, strict command
qualification and dormant writer-fence/controller foundations below are implemented
independently. Production caller/writer activation and publication remain gated.
Inherits [exact anchors](data-and-saving.md#exact-word-anchors) and architecture
AD-3/AD-8/AD-13. Accepted ADRs are unchanged. This extends the existing corpus owner,
not a new service or edition-library feature.

## Bounded source candidate

The [current delivery item](../../implementation-artifacts/spec-scribeswell-source-evidence-candidate.md)
qualifies the implemented [read-only source-artifact tool](../../../apps/scribeswell/docs/CORPUS_EVIDENCE.md)
separately from publication.
Its deterministic `scribeswell.source_evidence_candidate` v1 contains
`publication: false`, the exact raw-artifact SHA-256, explicit source/catalogue/
versification/tokenization labels, counts and ordered per-verse token digests.
It contains neither scripture bodies nor database IDs, a revision, audit seal or
activation status. Operator-supplied labels are not registered by this tool.

Input qualification requires the selected checksum, exact current 39-book inventory,
unambiguous JSON keys and valid source decoding. Bounds are 32 MiB source, 64-character
ASCII identity labels, chapter 1–150, verse 1–176, 512 tokens per verse and 2048 UTF-8
bytes per source word field, checked before morphology decoding. Source parsing
inherits the importer's permissive recognized-POS/layout checks, not complete
morphology feature validation. These are representation limits, not an independent
scholarly catalogue or source-provenance claim. Output is atomic and create-only;
malformed input or checksum mismatch creates no candidate. The CLI uses only the
standard library and reads no credentials or database. Atomic visibility does not
promise host-crash durability; a temporary cleanup failure may follow complete
destination creation. Reconcile by inspection and comparison with a newly computed
output, never by automatic overwrite/deletion.

A later independent database audit must compare actual complete inventory, exact
tokens and observed IDs against qualified candidate input under the fenced attempt.
Computing a source candidate cannot establish database correspondence or ready proof.

## Read-only database audit candidate contract

The [bounded delivery](../../implementation-artifacts/spec-scribeswell-database-audit-candidate.md)
implements comparison of qualified source bytes with one observed database snapshot,
documented in the [executable tool contract](../../../apps/scribeswell/docs/CORPUS_EVIDENCE.md#read-only-database-audit-candidates).
The final 160-test application suite passed without skips, including actual
PostgreSQL audit/compatibility cases. This contract
does not seal publication or prevent writes after that snapshot. Recompute the
source candidate from bounded raw input/checksum/labels before acquiring a database
connection; do not trust a submitted digest/inventory file. CLI requires the source
builder's seven explicit options and `SCRIBESWELL_AUDIT_DATABASE_URL`, read only
from the invoking environment, never dotenv or a command-line URL. Reuse the existing
runtime-role URL/TLS validation; require actual `current_user = scribeswell_runtime`
with neither SUPERUSER nor BYPASSRLS attributes.
Never use import/admin/service-role authority, role switching or new grants.
Before inventory reads conservatively establish full-row visibility from PostgreSQL
catalogue metadata: expected owning base tables; if RLS applies, an applicable
literal-true permissive SELECT/ALL policy and no applicable restrictive SELECT/ALL
policy. Include PUBLIC and effective role applicability. Fail if visibility cannot
be established; never bypass RLS. Controlled owner schema/policy DDL must remain
stable during the audit; concurrent owner DDL is not qualified. Ordinary concurrent
corpus DML remains supported without coordination/write locks. Reject invalid
Unicode/configuration before IPC; strip the audit URL and all libpq `PG*` variables
from the child's environment so ambient settings cannot redirect the validated
connection. Malformed worker responses use fixed safe failures.

Use one connection and explicit `REPEATABLE READ READ ONLY` before corpus reads.
Within that snapshot compare:

- All book rows with the complete owning metadata (including IDs and every field).
- Exact chapter and verse inventories against qualified source coordinates. Require
  positive observed chapter/verse IDs; resolve every relationship and check both
  denormalized verse book/chapter values against the actual parent chapter.
- Every word row, not an inner-joined subset: positive globally unique IDs,
  known verse, contiguous positions 1…N, bounded exact `surface_he`, expected token
  count and recomputed `verse_tokens.v1` digest. Missing/extra/malformed rows fail;
  unchanged IDs with changed text fail, regenerated IDs with identical tokens may pass.

Lemma, display text and morpheme validation remain with the existing importer; this
audit qualifies exact anchor surfaces and inventory only. No shared-service calls
or application coordination/write locks occur in the snapshot. Use streamed reads
in batches at most 1000; cap database rows to expected inventory plus one, with hard
ceilings 39 books, 6000 chapters, 50000 verses, 1000000 words. Reject excessive source
counts before connecting. Bound text projected from SQL to 2048 UTF-8 bytes (retain
a size/invalid indication rather than truncating valid-looking data). No unbounded
`fetchall` of words or arbitrarily large text transfer.

The database workflow has a 60-second monotonic deadline starting after source
qualification, including connect, snapshot reads and comparison; check it at bounded
batch/row work and before success. Connect timeout at most 5 seconds, lock timeout
at most 3 seconds, idle transaction timeout at most 15 seconds and each SQL wait at
most the smaller of 15 seconds and remaining budget. Server timeouts alone do
not bound DNS/client transport. Run the database snapshot in a supervised subprocess
after parent source qualification; pass its internal request/URL via stdin, never
argv, return bounded safe JSON only, and kill/reap it on the remaining total deadline.
Startup and IPC count toward that budget. Parent alone creates output after success;
no detached resolver thread or newer private driver wait API is required.
Close/rollback on error and
release the snapshot before serializing or creating output; no file/network wait
under the snapshot beyond its database queries. Bound output to 64 MiB. Reuse atomic
create-only publication and fixed safe errors; never log source bodies, DSNs,
credentials, SQL parameters or arbitrary exceptions. No partial candidate on audit
failure; filesystem cleanup outcomes retain the source tool's reconciliation rule.

Closed v1 output: `kind: scribeswell.database_audit_candidate`, `version: 1`,
`publication: false`, the four explicit identity labels, `source_sha256`,
`source_candidate_sha256` (SHA-256 of canonical serialized source candidate), equal
`counts`, and ordered `verses`. Each verse has `book/chapter/verse/token_count/
verse_token_digest` plus ordered `observed_word_ids` decimal strings. No database
URL, source bodies, clocks, UUID revision, current-state/activation claim or audit seal.
Use compact sorted-key UTF-8 JSON and one newline, same canonical verse ordering.

Acceptance needs real PostgreSQL: complete synthetic 39-book and full selected
artifact matches; missing/extra/malformed inventory and denormalization; reused IDs
with changed surfaces; regenerated IDs with unchanged surfaces; concurrent writes
during a repeatable snapshot followed by a failing fresh audit; actual read-only
enforcement, runtime login, deadline/query cancellation, bounded fetch and safe
failure/output cleanup. Run existing PostgreSQL/importer/reader regressions too.
This closes only the independent comparison prerequisite to ST-37/ST-38. Writer
fencing, sealed audit and activation remain the separate gates below.

## Brownfield constraint

The [importer](../../../apps/scribeswell/tools/py/import_bible.py) preserves IDs via
position upserts and commits each chapter separately. Its final file checksum is
not durable publication state. The [repository](../../../apps/scribeswell/backend/database.py)
uses autocommit reads unless a transaction is explicitly entered; a transaction
alone does not establish a repeatable snapshot. Current
[import/read grants](../../../apps/scribeswell/deployment/bootstrap/001_direct_database_roles.sql)
permit direct corpus DML and expose no manifest. Qualification must change those
supported writer paths before highlights depend on publication state.

## Proposed records and ownership

Names below describe logical records; DDL belongs to the corpus owner's controlled
migration history and must preserve previous-version reading compatibility.

| Record | Required invariant |
| --- | --- |
| Source publication | One per `source_id`: state `ready / updating / unavailable`, positive decimal-string generation, current attempt ID, optional active manifest revision. A retained old revision is not usable evidence while state is not ready. |
| Publication attempt | Owner-generated ID, source/generation, immutable approved input artifact checksum and catalogue/versification/tokenization identity, execution status, creation/update actor IDs and server UTC, initiator/executor evidence. One active fenced generation per source. |
| Manifest | Immutable nonnil UUID `source_revision`, source and catalogue/versification/tokenization identity, approved input checksum, complete supported verse inventory, activation attribution/time and owning attempt. Only complete audited manifests may become active. |
| Verse evidence | Manifest revision plus canonical verse, `verse_tokens.v1` digest, full contiguous position inventory and ordered observed database word IDs. No copied note body or historical full scripture edition is required. |
| Publication outcome | Owner operation identity/version and compact committed manifest revision; retry reconciles the original publication without creating a second revision or reactivating it after a later publication. |

The active manifest supplies current evidence. Existing note anchors retain their
already validated old digest/reference metadata; this contract requires neither
old full text nor an indefinitely browsable archive of previous manifests. Cleanup
must preserve any metadata needed to establish existing anchor/base evidence.

## Source mutation and publication

1. A restricted owner command begins an attempt, advances the source generation and
   marks it `updating` in a short transaction **before any source mutation**. Public
   reading continues under its existing completeness behavior. Exact-highlight
   evidence is unavailable during the update; no partial corpus claims a ready
   revision. Starting an attempt is explicit, not an API-startup side effect.
2. Each short chapter-write transaction verifies the current attempt/generation and
   permitted input before DML, retaining the existing chapter rollback boundary.
   All ordinary corpus writers, including supported direct SQL/import paths, must
   enforce that boundary in the database; a CLI convention alone is insufficient.
   No API reader/private-note role may start publication or mutate source data.
3. No remote/file/network waits or book-wide coordination transaction is needed to
   keep the gate closed. A durable attempt plus per-transaction fencing excludes
   stale writers. Resuming after interrupted execution obtains a fresh generation
   under owner recovery; a retired worker cannot continue with its old generation.
4. After imports, audit the **complete supported source** against the approved full
   artifact and catalogue, including every verse/token/ID and completeness checks.
   For the current reader this is its 39-book Tanakh source, not reference-only
   Matthew entries. A `--book` repair alone is never a complete-source publication;
   it must still pass the full audit before evidence is re-enabled.
5. Stage the manifest from that audited state while the generation remains fenced.
   In a short final transaction recheck current attempt/generation, completeness
   and sealed audit result, then atomically activate the manifest and set `ready`
   with its outcome/attribution. No writer may mutate between that audit and
   activation, or after activation without first closing the gate again.
6. Interruption, failed audit or uncertain completion leaves proof unavailable.
   Reconcile a possibly committed outcome before restarting. An explicit owner
   recovery can resume/repair and fully audit; it cannot merely toggle `ready`,
   silently reverse applied migrations or relabel partially changed rows as the
   previous edition. Public-read completeness failures retain their existing error
   handling; publication does not promise uninterrupted complete text during a
   malformed import.

Physical fencing must be qualified against the actual supported roles, pool reuse,
triggers/routines, rollback and direct alternate writes. Do not claim the current
roles already enforce it or add a long database lock across external work. D-5
must coordinate the new importer and old writer paths before activating evidence;
if compatible transition cannot be proven, design the explicit maintenance and
recovery window rather than break supported writers silently.

## Proposed additive reader evidence

Keep existing public Bible response fields/meaning. Propose one optional
`anchor_evidence` field on each verse-with-words; an absent/unknown field means
unavailable proof to new clients, not absent scripture. Closed v1 variants:

- Unavailable: `{version: 1, status: unavailable}`.
- Ready: `{version: 1, status: ready, source_id, source_revision,
  catalogue_version, versification_id, tokenization_version, reference,
  verse_token_digest}`. `reference` is D-2's canonical single-verse reference;
  `source_revision` is the active manifest UUID and digest is lower-case SHA-256.

Read source gate, active manifest, per-verse evidence and returned words in **one
bounded read-only repeatable snapshot**. Verify the returned ordered row IDs,
positions and digest against the manifest in that same snapshot. No proof can
combine a previous manifest with current changed word rows. Missing/unready/mismatched
proof returns unavailable metadata while valid public text may still render; it
must not turn a private-feature readiness fault into forced login/public outage.
Proposed DTOs/schema/client changes and previous-client compatibility still require
qualification; this document does not modify the current generated/public wire.

Proof is public source evidence, not an account grant or a bearer secret. On a new
or repaired private highlight, the server independently checks the current ready
manifest and exact submitted selection before private write locks. A cached public
response, equal word ID or client hash is insufficient. Changed proof requires
refresh/reselection; do not silently translate a new selection to a different
revision. An import beginning after a valid bounded observation can make that
recorded anchor unavailable/need review later, as D-2 already permits; this is not
a distributed-atomic promise across corpus and private-note transactions.

Existing anchors are evaluated against a coherent current manifest:

| Source/evidence | Anchor behavior |
| --- | --- |
| Ready, matching revision and exact evidence | Valid. |
| Ready, newer revision; same source/catalogue/versification/tokenization and exact full verse digest/positions | Owner-proven compatible; render against current IDs without rewriting historical note evidence. |
| Ready, incompatible verse or source/tokenization evidence | Needs review; keep note/reference and suppress misleading marks. |
| Updating, unavailable, missing or inconsistent proof | Unavailable; keep note/reference and do not infer deletion/change. |

Unchanged stored anchors may round-trip in a text-only note edit under D-2's trusted
base-evidence rule. New/repaired marks cannot bypass current proof by reusing an
old highlight ID. No partial aggregate save drops a newly added mark silently.

## Owned migration baseline prerequisite

The bounded baseline delivery adopts the existing supported schema into an
application-owned Alembic history, before writer-fence expansion. It is adoption
only: no corpus creation, row change, sequence advancement, ownership transfer or
reader/importer grant change. Initial legacy SQL remains a bootstrap/reference;
all forward Scribeswell DDL belongs to this owned history.

An explicitly prepared `scribeswell_migrator` must own the schema, tables, views
and sequences and have no superuser, bypass-RLS, role/database creation,
replication or unsafe membership authority. Compare the complete supported
catalogue and ACL/default-ACL profile against an independently constructed pinned
reference, never a target-derived blessing. Check before ledger DDL and on replay;
missing, partial, extra or drifted objects and unknown/malformed ledger fail closed.
Include internal foreign-key trigger presence/enabled state and effective PUBLIC
and default-grant authority outside the owner. A constraint definition alone does
not prove enforcement. This baseline's qualified server profile is PostgreSQL 17.
Do not alter corpus data, current sequence values, original policies or grants.
The new ledger is owner-only despite existing default grants. Reject stamp,
downgrade, offline, non-head upgrade targets and unrelated Alembic operations. Use one short bounded
transaction with owner serialization; advisory coordination does not fence
uncooperative administrator DDL, which requires a stable operational window.

The app-local bounded migration adapter participates in the existing host release
coordinator as `scribeswell-owned`. It validates project/role configuration,
suppresses credentials and raw database exceptions, records safe actual owner
revision evidence and blocks activation on failure or unknown outcome. Failed
execution retains only safe known-before observations, never an inferred after state.
The existing compatibility fingerprint covers owned history/reference, registered
migration Dockerfiles and explicit Scribeswell adapter/dependency/validator inputs.
Future revisions must deliberately extend revision-aware validation and the runner.
Timeout cleanup is bounded; uncertain outcomes require reconciliation, never automatic
reversal. API startup runs no migrations. Production role/ownership preparation,
target profile qualification and controlled adoption remain explicit release gates.
Disposable PostgreSQL must prove failed-adoption rollback, replay/serialization,
owner-only ledger, unchanged corpus and previous-reader/importer compatibility.

This baseline is implemented; its [delivery record](../../implementation-artifacts/spec-scribeswell-owned-migration-baseline.md)
records 231 application tests passing with no skips on disposable PostgreSQL 17,
25 platform tests/42 subtests, independent reference reproduction and composition
check-only evidence. The migration image is not built and no production target is
prepared or adopted. The baseline did not implement writer fencing, audit sealing or publication
activation; later foundation deliveries below retain their separate evidence. The
baseline closes neither ST-37 nor ST-38 by itself.

## Dormant writer-fence expansion contract

The implemented bounded expansion is `scribeswell_0002`, independently qualified on
PostgreSQL 17. It installs fencing infrastructure with enforcement **false**, no
source/attempt business rows and no ordinary caller execution grant. Existing
corpus rows, IDs, sequences, grants, importer and public API keep their behavior.
It provides no publication assurance until a later coordinated writer transition.

Three owner-private structures serve the existing single corpus. Source labels use
the existing ASCII `[A-Za-z0-9][A-Za-z0-9._:-]{0,63}` evidence namespace:

- A singleton deployment control row with enforcement false. This technical
  schema/release configuration uses operational migration evidence under ADR-0056.
- An initially empty singleton epoch gate, with bounded source label, positive
  bigint generation, nonnil attempt UUID, approved artifact SHA-256, state
  `updating / closed`, and server UTC creation/update actor fields. No real rows
  were inserted by0002. Actor verification remains an Identity-owner gate;0003
  below separately implements dormant begin/recovery commands without real actors.
- A transient binding registry carrying actual session login, backend PID, full
  `xid8` and the exact epoch tuple. It is transaction coordination, explicitly
  exempt from business actor fields. Deferred end-of-transaction cleanup and
  rollback leave no committed bindings; forcing early constraint execution can
  remove authority, never create it.

A fixed owner-private binding routine accepts the source/generation/attempt/input
digest tuple and checks a matching updating gate, actual `session_user =
scribeswell_import`, and current transaction/backend. The routine's shipped EXECUTE
privilege stays owner-only; tests alone temporarily grant it to the restricted
import login and seed synthetic attributed gate rows to qualify future enforcement.
No synthetic production actor, cross-owner Identity read or default role grant is
introduced. This binding records the declared approved input; complete source-byte
correspondence still requires the independent full audit.

BEFORE STATEMENT guards cover INSERT/UPDATE/DELETE/TRUNCATE on all five base tables,
including book seeding, COPY, upserts and zero-row statements. Every guard locks
the deployment control row FOR SHARE even when disabled. When enabled it requires
a valid protected binding and matching updating epoch held FOR SHARE through the
write transaction. Generation/state change uses a conflicting owner update lock;
FOR KEY SHARE is insufficient. Lock order is control then epoch. Missing control,
missing/closed/stale epoch, forged GUC, copied context, wrong login, later/pool-reused
transaction or missing binding fails closed with a fixed safe SQL error. A later
enforcement flip waits for any already-executing dormant legacy write to finish.
No lock is retained across file/network work or an entire import.

Fence and cleanup triggers use ENABLE ALWAYS and their state is catalogued.
Existing RLS still rejects COPY FROM before guard execution; binding does not make
that shipped path available. A fixture-only RLS adjustment qualifies the underlying
COPY guard separately and is restored afterward; no production RLS change follows.

Functions use fixed safe search paths and fully qualified objects. Revoke PUBLIC
and business-role table/function defaults; no runtime/importer direct access to
control/gate/bindings, and no ordinary role can disable triggers, assume owner or
mutate the structures. Trusted owner DDL still requires the stable release window.
The unchanged role bootstrap remains the initial baseline/reference; this expansion
does not add an importer EXECUTE grant that would contradict its current whitelist.

Migration preflight identifies absent/0001/0002 ledger states, compares the exact
starting catalogue, upgrades transactionally, verifies the exact dormant head and
revalidates on replay. Preserve the original revision/reference and pinned legacy
inputs. A new independently generated head reference includes exact routine
definitions/signatures/owner/security/config/ACL and trigger structure/state;
never derive it from a target. Adapter success and safe failed-before observations
support the new revision, preserving bounded execution and activation blocking.

Real PostgreSQL acceptance must prove clean and0001 upgrades, head replay/drift,
post-DDL rollback, denied ordinary access, unchanged dormant compatibility, enabled
synthetic missing/stale/closed contexts, alternate operations/all tables, pool reuse,
commit/rollback cleanup and concurrent writer/generation/control-flip ordering.
These tests establish the0002 foundation only. The later0003 controller below
implements fixture-qualified attempts/recovery/closure; production enforcement,
verified actor/caller setup, importer transition, sealed full audit and ready-reader
proof remain gates.

Its [delivery record](../../implementation-artifacts/spec-scribeswell-dormant-writer-fence.md)
records the actual missing-table red, original 71-test characterization, all three
independent reviews and resolved findings, final 321 application tests with no skips,
25 platform tests/42 subtests, independent old/head references and composition check.
Fixture-only enforcement proves committed writes and both transition orderings,
savepoint/disconnect/rebind cleanup, direct owner/ordinary role denials and drift
rollback. No migration image build or production adoption/enforcement occurred.

## Qualification and release gate

ST-12/ST-37/ST-38 require real importer/API/database evidence: initial full audit;
partial/import interruption; concurrent chapter/reader snapshot; mixed manifests;
same IDs with changed text; regenerated IDs with unchanged tokens; stale workers;
old/new command replay; alternate DML/pool reuse; atomic activation/outcome loss;
repair followed by full audit; and public reading with proof unavailable.

Beyond these bounded foundations, D-2 must close sealed-audit representation, OpenAPI schemas,
immutable evidence retention and measured read/write deadlines. D-5 must close
source-writer transition, restricted grants, controlled migrations, previous-reader
compatibility and failed-activation recovery. The existing role bootstrap's whitelist
must be deliberately updated and qualified with its owner, not bypassed by broad
credentials. No production data, role, API or source activation is changed here.


## Publication-command qualification contract

This bounded contract defines pure input preparation only. It grants no authority,
opens no database/network/file, changes no gate and produces no committed receipt.
That pure-input delivery introduced no controller or authority storage;0003 below
adds the dormant execution foundation. Real caller grants remain gated. Prepared
values cannot establish a seal or ready
proof, even when the same source bytes were previously audited.

`backend/corpus_publication_input.py` exposes `parse_command(raw: bytes)` and
`prepare_command(raw: bytes, source_raw: bytes)`. Both use immutable typed records
with suppressed payload repr. Preparation always parses the command first, then
recomputes the complete source candidate from exactly the supplied source bytes
using the existing source validator and canonical serializer. Return only the parsed
command, immutable source counts and SHA-256 of the serialized source candidate;
retain neither raw scripture nor mutable inventory. Callers must not treat object
construction or local JSON as verified authority. No CLI/output artifact or runtime
integration is added.

Every command uses a closed JSON object with required `schema_version: 1`, lowercase
canonical nonnil UUID `operation_id`, `command`, `scope`, `payload`, `reason_code`
and `evidence_ref`. Scope is exactly `{kind: source, source_id}`. Identity labels use
the existing 64-character ASCII source namespace. Evidence is 1–256 ASCII characters
matching `[A-Za-z0-9][A-Za-z0-9_.:/-]*`. Approved reasons are `source_import`,
`source_recovery`, `source_seal`, `synthetic_fixture`; the first three must match
begin, recover and seal respectively, while synthetic_fixture permits any variant.
The complete body is at most65536 bytes: strict UTF-8, no BOM, duplicate keys at any
level, unknown/missing fields, non-JSON constants, floats, booleans-as-numbers,
NUL/surrogate text or deep nesting. All invalid command inputs return only
`corpus_publication.input_invalid` without echoed input/decoder details.

| Command | Exact payload |
| --- | --- |
| `corpus.begin` | `expected_absent: true`, `input` containing exactly `source_sha256`, `catalogue_version`, `versification_id`, `tokenization_version`. |
| `corpus.recover` | `expected_generation`, `expected_attempt_id`, `input` with the same four identity fields. |
| `corpus.seal` | `expected_generation`, `expected_attempt_id`, `input` with the same four identity fields. |

Digests are64 lowercase hexadecimal characters. Generations are positive canonical
decimal strings at most9223372036854775807; expected attempt is a lowercase canonical
nonnil UUID. UUIDs are operation/attempt identifiers, never actor assertions. Preparation
of every variant, including seal, verifies the complete raw artifact/checksum/inventory;
source errors keep their existing safe `source_evidence.*` identifiers. A supplied
candidate/audit object is not source input. Artifact SHA is provenance, distinct from
command retry comparison/fingerprints. No fingerprint protocol is implemented here.

The qualified controller semantics below use begin for initial epoch creation only; recover requires
an exact existing source/attempt/generation and advances to a fresh generation and
attempt, including for a later ordinary replacement import. Seal requires that exact
updating tuple and closes it after active writers finish. All transitions follow
control-then-epoch locking in short transactions without source/network waits. Begin
cannot overwrite an existing epoch, recover cannot reopen the old generation and
seal cannot activate a manifest. Controller-generated attempt IDs and server timestamps
are never payload overrides. Original same-operation outcomes are immutable; changed
input conflicts, replay never reactivates retired state and lookup requires current
authority. KDG-only ADR0061 does not change publication semantics. The controller below closes exact semantic comparison/receipt; outer
supervisor/transport bounds remain activation work.

Actor/caller preparation consumes Identity ownership: verify a stable classified
service actor UUID/kind/key and preparation provenance externally through the existing
controlled actor setup contract, then map the actual original database session login
to that verified executor and enabled exact-command/source authority in protected
Scribeswell-owned state. No supplied actor, role name, GUC, infrastructure credential
or arbitrary evidence file verifies identity. A verified human initiator is separate;
without trusted verification it is absent. Current authorization and revocation must
serialize with execution and receipt lookup. There is no delivered general Scribeswell
service-actor projection to call, no cross-owner reads/FKs, and no Access capability
grant from actor existence. Caller role, physical mapping/privileges and real preparation
are explicit gates before execution. Existing dormant-head migration replay remains
unchanged and cannot accept active operational state by implication.

## Dormant executable controller contract

This bounded delivery implements native transactional commands plus a Python
adapter; this section supersedes the earlier statement that physical execution and
retry storage are unspecified. It does not authorize caller preparation or operational
migration activation. New `scribeswell_0003` ships empty controller tables, no ordinary
EXECUTE grant, false enforcement and no actors or epochs. Existing readers/importer
and original source/bootstrap/revisions0001/0002/reference profiles remain unchanged.

### Protected execution and records

A future separately prepared dedicated `scribeswell_corpus_operator` LOGIN is the only
ordinary command caller. Verify actual session_user and current caller role flags:
LOGIN, NOINHERIT, no SUPERUSER/BYPASSRLS/CREATEDB/CREATEROLE/REPLICATION or memberships.
A caller name alone is insufficient. No role is created or granted by this migration.
Fixtures alone provision this exact absent role with temporary command EXECUTE; refuse
pre-existing fixture roles before mutation and clean up only owned resources.

- `corpus_operator_principal`: database_login primary key, enabled/revision, externally
  verified nonnil executor actor UUID, fixed service classification, immutable stable
  actor key (`[a-z][a-z0-9_.:-]{0,127}`) and preparation evidence reference,
  creation/update actor UUIDs/server UTC.
  Only controlled Scribeswell-owner preparation writes it after Identity verifies the
  durable actor. Stored UUID/key/reference is custody, not an Identity verification API.
  No current-account projection, foreign-owner table access/FK or synthetic Auth account.
- `corpus_operator_authority`: exact login/source_id/command primary key, local principal
  FK RESTRICT, enabled/revision and creation/update actor/UTC. Commands are only
  corpus.begin/recover/seal; sources use existing labels, no wildcard/all-source grant.
- `corpus_attempt`: fresh nonnil server UUID, source/generation unique, immutable approved
  input checksum and catalogue/versification/tokenization labels, state updating/closed/
  retired, creation/update executor actor/UTC. Retain completed/retired history. A verified
  human initiator is absent in this slice; never accept it as caller input.
- `corpus_command_outcome`: immutable local login/operation UUID key, exact semantic
  command JSONB, original executor, principal/authority revision evidence, original
  compact result, creation actor/server UTC and local attempt/source/generation FK.
  Input contains identifiers/version labels/reason/evidence only, no scripture or secrets.
  JSONB equality of the closed typed semantic envelope implements exact-input comparison;
  no JCS/hash/fingerprint claim or raw JSON lexical comparison. Key reuse with changed
  input or rebound executor conflicts. Historical receipts do not confer current authority.

Enforce local primary/unique/FK/check invariants, positive bigint revisions/generations,
non-nil actor/operation/attempt IDs, finite UTC attribution and bounded safe labels/refs.
Keep existing standalone epoch schema compatible with0002 fence qualification; its
cross-record current-attempt consistency is a protected controller transition rule.
No ordinary caller has direct DML, table SELECT, DDL/owner assumption or mapping write.
Owner schema administration still requires its stable release window.

### Native command execution

`execute_corpus_command(request jsonb) -> jsonb` and
`lookup_corpus_command_outcome(request jsonb) -> jsonb or SQL NULL` are owner-only
SECURITY DEFINER routines with fixed pg_catalog search_path and fully qualified names.
All helper routines are owner-only too. Native JSONB input independently validates the
same closed semantic envelope/types/bounds/reason pairing as the strict byte parser;
raw-byte duplicate/encoding checks belong to that parser. No caller actor/time override.
Required SQLSTATE/messages:42501 access denied,22023 invalid command,P0001 conflict,
55000 unavailable, with fixed safe machine identifiers and no submitted details.

Order: current principal and exact source/command authority FOR SHARE; serialize the
login/operation retry with a bounded advisory transaction lock; inspect prior outcome.
A matching original outcome returns unchanged after current authority and executor
checks, even after later transitions; changed input conflicts. Never reapply a transition.
A lookup serializes with in-flight execution and returns only the original receipt or
NULL; it needs no source bytes or new grant. Revocation updates must wait for current
execution/lookup shares; later operations deny. Retain actual executor/revision evidence.

For a new command, require enforcement true and retain control FOR SHARE, then serialize
absent-epoch creation with one corpus advisory transaction lock and lock epoch FOR UPDATE.
This preserves control-before-epoch order with binder/guards. All corpus transitions
serialize because the physical corpus remains singleton, regardless of source labels.
No transaction spans source parsing, network, external Identity verification or full audit.

- Begin requires no epoch; allocates attempt UUID and generation1, updating epoch and
  attempt with executor/UTC. Existing epoch always conflicts, including another source.
- Recover requires exact existing source/generation/attempt in either updating or closed
  state; retires old attempt and allocates new updating attempt/generation+1 with the new
  approved input identity. Reject bigint overflow without mutation. Cross-source recovery
  and stale tuple conflict; never reset generation or reuse the old attempt.
- Seal requires exact current updating source/generation/attempt and all four approved
  input identity fields. It closes both epoch and attempt after existing writer locks
  release. No ready state, manifest, audit attestation or scripture mutation is created.

Commit epoch/history/outcome atomically. Injected failure rolls them all back. Result is
exactly `{version:1, operation_id, command, source_id, executor_actor_id, attempt_id,
generation, state}`; generation is a decimal string, state updating/closed. This result
inside a transaction alone is not commit proof: caller must observe successful COMMIT
or reconcile durable same-operation lookup. Old returned outcomes never reopen old state.

### Python adapter and bounds

`backend/corpus_publication.py` exposes execute_command(connection,raw,source_raw) and
lookup_outcome(connection,raw), using the existing strict qualifier/parser respectively.
Require an idle caller-owned psycopg connection before source work; execute always
requalifies full raw source before any SQL/lock. Construct the semantic request from
parsed immutable fields, never caller-built PreparedCommand. Use bound parameters and
one READ COMMITTED transaction, reject incompatible isolation; no dotenv/URL/env reading,
connect/provision/CLI, raw SQL interpolation or imported owner implementation.
Use local statement timeout5s, lock timeout2s and idle-transaction timeout5s; routines
also require a writable READ COMMITTED transaction. Validate exact returned shape,
identity/source/executor/attempt/generation/state safely; no original request payload dump.
Return safe frozen receipt values only after transaction exit succeeds; lookup may
return None. Fixed failures map SQLSTATE to access_denied/input_invalid/conflict/
unavailable or unknown_outcome under `corpus_publication.*`; remove raw driver exception
chaining. Command/source parser errors retain existing safe identifiers. SQL bounds do
not bound DNS/client transport/COMMIT: no general operator CLI is exposed here; outer
supervised invocation and unknown-outcome recovery qualification remain activation gates.

### Migration qualification and remaining gates

Add a revision-specific0003 reference generated from independently pinned fresh fixture
plus actual reviewed0002/0003 DDL, never a target. Preserve existing reference.json and
reference-head.json bytes as0001/0002; extend generator with explicit revision selection
while keeping default and legacy --head behavior compatible. Preflight/adapter recognize
all three known revisions. Upgrade from any earlier exact profile transactionally to0003;
head replay still requires false enforcement, empty epoch/bindings/controller tables and
exact shipped owner-only ACL/profile. Fixture operational changes deliberately fail this
dormant-only replay check: active-state release profiles are not qualified by this slice.
Failure blocks activation; preserve known-before evidence and no automatic reversal.

Actual PostgreSQL tests must cover parser-to-DB begin/recover/seal, full history/outcome
atomicity and rollback, original/changed-input replay after later transitions, concurrent
same/new operations, authority revocation, role/GUC/SET ROLE/other-source denial, overflow,
writer-first and transition-first sealing/recovery, stale writer exclusion, unchanged
legacy reader/importer,0001/0002 upgrades,0003 drift/replay/rollback and all references.
No production actor/caller/grant/adoption/enforcement, importer transition, sealed full
audit/publication/reader proof or private Studies is implied. Access remains separate.


The [controller delivery record](../../implementation-artifacts/spec-scribeswell-dormant-corpus-controller.md)
records actual PostgreSQL acceptance red, prior-profile characterization, independent
three-lens review and completed fixes. Final root full regression passed614 tests;
final focused controller run passed136, including four restored malformed-receipt
cases added after full collection. These cover the current app collection together,
with no skipped acceptance. Platform deployment checks passed25 tests/42 subtests;
composition check-only and independent three-reference reproduction passed. This
qualifies dormant transactional behavior, including native size bounds, complete
rollback snapshots, changed recovery identity, all seal comparisons, both authority
orderings and competing transitions. It does not qualify production actor/caller
preparation, an active release profile, outer transport supervision, importer
transition, sealed full audit or publication/reader proof. Those remain the next gates.


## Supervised invocation contract — implemented locally

Derived from canonical decision154 and implementation evidence156. App-local Python
execute/outcome entry
points wrap the existing controller. Inputs are original command bytes, complete
source bytes for execution only, and an explicit target. Supabase targets bind an
HTTPS project URL to the exact operator database URL using the platform pure target
contract. Declared local_disposable targets bind literal loopback, exact database name
and exact operator login. This declaration does not prove disposable custody, verified
Identity attribution or operational readiness; use controlled prepared fixtures only
for qualification. No target/credential discovery, CLI, provisioning or activation.

An isolated child receives secrets through stdin, excludes ambient PG/Python/app
credential settings, revalidates inputs/target and fully qualifies source before connect.
The parent owns a fixed60-second total budget including bounded kill/reap cleanup.
Bound output and suppress stderr; release a typed receipt only after child COMMIT and
parent validation. Any lost/timed-out/malformed response remains unknown; missing
current-authorized lookup remains unresolved. Preserve original operation/input, never
retry automatically or infer rollback. No arbitrary actor or timeout override.

Prove actual restricted-login transitions, current-authorized lookup, commit-success
with lost response reconciliation, no connection on invalid source, target negatives,
environment/credential isolation, malformed/oversized output and blocked child cleanup.
This closes transport supervision only; external actor/caller custody, active release
profile, coordinated importer transition and sealed publication/reader proof remain
open. Existing dormant migration references and enforcement defaults stay unchanged.


Local supervisor evidence:80 operator cases and root367 affected tests passed without
skips after review fixes. Explicit libpq password authentication disables implicit
client certificates, GSS and passfile discovery; single DNS-host binding excludes
libpq multiple-host syntax and uppercase schemes normalize before connection.
Structured warnings distinguish confirmed forced termination/reaping from unverified
termination. The60-second admission-measured budget charges synchronous bounded
admission/encoding/Popen, but only child work and transport waits are preemptible;
no hard real-time or descendant process-tree guarantee is made. The trusted child
creates no descendants. Actual committed-response loss reconciles through original
lookup; connection and transaction-commit-entry stalls use focused fault injection.
Final root full regression passed698 tests/no skips in178.52s; root affected
acceptance367 passed and platform deployment25 tests/42 subtests passed. The exact
temporary PostgreSQL17 container was stopped after verification. Eight independent
review findings are resolved with no deferrals. All production custody, active-profile
and downstream publication gates remain open.


## Prepared-controller replay contract — implemented locally

Decision160 qualifies one staging state before active enforcement. Expose
`baseline.preflight_prepared(connection, expected_actor)` for controlled owner-native
validation and allow Alembic Config attributes `scribeswell_validation_profile` equal
to `prepared-controller-v1` plus `scribeswell_prepared_actor`. Omitted profile remains
`dormant`; unknown/None profile, custody supplied in dormant mode or missing prepared
custody fails. Do not add an environment, CLI or host selector. Existing host adapter
continues dormant-only and cannot activate a prepared target by inference. This is
controlled native rehearsal qualification, not completed production release wiring.

The custody input is an exact dict with schema_version integer1, source_id,
executor_actor_id, actor_kind service, actor_key and preparation_evidence_ref. Apply
existing safe source/key/ref bounds and canonical nonnil UUID rules; reject unknown
fields, bool/float versions, overrides and malformed values. It carries independently
verified Identity-owner facts, not proof of verification. No Identity table/API
implementation, actor registration, caller/grant provisioning or certificate authority
is added. A matching local UUID/reference is never an Identity verification claim.

Reuse existing pinned-input, PostgreSQL17, actual migrator/ledger, isolation and
migration-lock checks without relaxing the dormant entry point. Require existing
exact owned0003; prepared mode cannot adopt/upgrade earlier or missing ledgers.
Preserve reference.json, reference-head.json, reference-controller.json and all applied
revision bytes. Compare full pinned controller catalogue, allowing only three exact
ACL cells to add operator USAGE on the owned schema and EXECUTE on execute/lookup
controller entry functions. Normalize those ACL cells semantically if needed but
validate privilege/grantor/grantability exactly; every other snapshot field/ACL stays
strict. Never strip all ACLs, infer a profile from target drift, regenerate a reference
from a target, repair grants/state or treat version alone as proof.

Require actual restricted operator LOGIN flags, no incoming/outgoing memberships,
no unsafe role/database settings, ownership, database/schema CREATE or other explicit
or effective business authority within/outside this silo. Only fixed schema USAGE
and two function EXECUTEs are added; helpers, tables, columns, sequences and owner
assumption stay unavailable. Reject cross-owner direct/default grants even without
current schema USAGE and callable PUBLIC security-definer authority where reachable.
Ordinary pg_catalog/system reads and standard PUBLIC CONNECT/TEMP are not app grants.
Keep current migrator restrictions. Validate principal row against all expected actor
custody fields, exactly three begin/recover/seal authority rows for the one source,
positive revisions, nonnil attributed actors and finite timestamps. Enabled/disabled
principal and authority flags are allowed current facts, never rewritten or re-enabled.

Require singleton controlfalse and empty epoch, binding, attempt and outcome tables;
reject all true/enabled-history states. Require a caller-owned writable READ COMMITTED transaction with local statement5s
and lock2s ceilings before coordination, preserving shorter nonzero caller bounds. A
fresh connection must fail without starting a transaction. Establish local search path
pg_catalog,pg_temp before inspections to prevent temporary/public catalogue shadows. Reuse the migration advisory lock and acquire
SHARE table locks in fixed order on principal, authority, control, epoch, attempt,
outcome and write-binding. These block configuration/state mutation and authority
insert phantoms during bounded validation, while native reader/importer row-share
locks remain compatible. A stable owner DDL/role window is still required; table
locks do not serialize arbitrary cluster role administration. No external waits or
source scan/audit occur under locks. Validation
reads state and takes transaction locks; it performs no preparation DML/DDL. Native
head replay retains existing Alembic ledger ACL guarding and changes no business data.
Record successful profile in `config.attributes['scribeswell_validated_profile']` only
after both pre/post validations and transaction commit succeed; no partial success or
new durable ledger. Clear reused success evidence before every invocation, including
offline and unsupported attempts.

Prove default dormant characterization first, then actual prepared-profile acceptance
failure before implementation. Qualify native0003 replay and direct checker, all exact
ACL/role/custody/scope/state denials, disabled mappings preserved, earlier-version
rejection, full catalogue/business/sequence/ledger preservation, fault rollback and
serialization against local configuration changes. Original reader/importer authority
must remain compatible. Existing host selection, live Identity/caller verification,
enforcementtrue/history release profile, importer transition and publication/reader
proof remain gates; no readiness inferred from this local profile.


Local implementation and reviewed evidence are recorded in
[the prepared replay delivery](../../implementation-artifacts/spec-scribeswell-prepared-controller-profile.md)
and [app contract](../../../apps/scribeswell/docs/PREPARED_CONTROLLER_PROFILE.md).
Effective PUBLIC wrapper/server USAGE, tablespace CREATE and nonordinary parameter
privileges reject. Protected core routine EXECUTE cannot exceed PostgreSQL-owned
initdb ACLs for the exact pg_proc identity; ordinary builtins remain available.
Global/reachable PUBLIC table/sequence default grants reject even for empty schemas;
ordinary function/type defaults remain. These inspect metadata only. Independent
review corrected seven findings and refuted one using existing structural protection;
none deferred. Synthetic custody remains a fixture stand-in, never live Identity proof.


## Controller-history replay contract — implemented locally

Decision168 adds native `controller-history-v1` with the same exact closed custody
bundle and ACL/role/catalogue restrictions as prepared-controller-v1. Entry point
`baseline.preflight_controller_history(connection, expected_actor)` and explicit
Alembic Config profile plus `scribeswell_prepared_actor` validate exact existing0003.
Dormant/prepared behavior and default CLI/host remain unchanged; neither environment
hints nor target drift select a profile. No earlier ledger adoption, actor/grant
preparation, enforcement change, importer transition, Identity verification, host
integration or publication occurs. Local custody still consumes separately verified
owner facts; this is rehearsal qualification rather than production authorization.

Accept either enforcement boolean and exactly one current principal/three expected-
source command authorities, preserving disabled flags. No epoch means no attempts
or outcomes; otherwise require one expected-source epoch and a complete contiguous
generation chain from1 through its generation. At most10000 attempts/20000 outcomes
are qualified; exceeding the cap fails safely without deletion or partial validation.
All other attempts are retired; the last matches epoch attempt/source/generation/
input/state. No committed bindings are allowed. Require finite epoch timestamps.

Every attempt has exactly one originating begin (generation1) or recover outcome
(later generations), and at most one seal outcome. Recover references the immediately
preceding attempt/generation. Closed current attempts require a seal; updating ones
forbid it; retired predecessors may have been sealed first. Requests obey the existing
closed native command grammar; stored results equal the exact compact receipt built
from original operation/command/source/executor/attempt/generation and transition
state. All four approved input fields match their attempt. Require original creation
actor/time and final update actor/time to match corresponding origin/seal/retirement
events; epoch creation matches initial begin and its update matches current origin/
seal. Original executor and revision evidence stays historical: positive revisions
cannot exceed current principal/exact-command authority revisions, but historical
actors need not equal the current executor. A successful receipt cannot claim the
exact current revision of a disabled principal/authority; valid older-revision
history stays admissible while paused. Current custody rotation never rewrites
old receipts or makes rebound-executor replay authorized. No source text audit is
performed; coherent protected records are not proof of external provenance.

Use caller-owned writable READ COMMITTED transaction, safe pg_catalog,pg_temp
path and existing statement5s/lock2s ceilings preserving shorter bounds. After the
migration advisory lock acquire existing controller advisory lock(31003,1) before
the seven SHARE table locks in prepared order. This avoids taking epoch table SHARE
while a controller transition holds attempt ROW EXCLUSIVE and awaits epoch mutation.
Hold local configuration/history stable; wait for existing bound writers to commit
and clean up. Verify bindings empty afterward. Native readers remain compatible.
Use bounded set-based SQL and bounded cardinality probes, not unbounded payload
fetches or Python per-record SQL. These are statement/lock bounds, not an end-to-end
transport/COMMIT deadline; the caller owns the transaction and operational supervisor
qualification remains separate. Stable owner DDL/cluster-role window still required.
No external calls/source scans under locks; safe fixed errors and rollback on failure.

Native replay validates before/after and publishes profile evidence only after
commit, clearing reused evidence on every attempt. Test real begin/seal/recover
chains, paused/disabled mappings and actor rotation; corrupt/missing/orphan records;
exact preservation and meaningful rollback/commit faults; cap boundaries; both
transition/validation orderings and bound-writer cleanup. Characterize prepared
behavior before shared-helper extraction. Final root full897/no skips246.21s and
focused94 history cases/no skips35.52s passed, including a literal10000/20000
positive and literal one-over denials. Platform25/42 and composition pass. Impacts:
no scaffold/shared UI/agent-context/ADR promotion; app and canonical docs updated.
Access/KDG, Leave/factory, accepted UX and standalone signup stay untouched.


[The delivery record](../../implementation-artifacts/spec-scribeswell-controller-history-profile.md)
retains actual red, harness corrections and full-capacity query-timeout discoveries.
Preaggregation and projected event windows corrected the measured planner failure
without schema, ANALYZE or timeout changes. The initial host thread limit required
standalone user-run reviews; all three returned and were triaged before corrections.
Eight accepted findings including one duplicated verification gap were resolved,
one native JSON-null claim refuted with real denials, none deferred. Three individual
ordering mutants prove the new in-bound revision tests observe each predicate.
Actual changed-source recovery/seal, actor rotation between origin/seal and post-
replay receipt lookup/identical retry are qualified. Commit evidence distinguishes
pending-row rollback before commit from real DBAPI commit followed by injected
acknowledgement loss: durable effects stay, no success is published, and explicit
rehearsal reconciles actual state. Native history validation verifies neither live
actor identity nor scripture correspondence; operational host/custody/importer and
sealed-audit/publication/reader readiness remain open.

## Operational host validation — implemented locally, reviewed

Canonical decision178 selects the next bounded integration, tracked in
[its delivery record](../../implementation-artifacts/spec-scribeswell-host-validation-profiles.md).
The controlled `scribeswell-owned` adapter/host now carries explicit profile and
closed expected custody through bounded stdin IPC; dormant stays default and the
native CLI still has no environment selector. Non-dormant requires exact existing0003.
`SCRIBESWELL_MIGRATION_PROFILE` accepts dormant/prepared-controller-v1/controller-history-v1;
`SCRIBESWELL_MIGRATION_CUSTODY_JSON` is required exactly for non-dormant, at most4096
UTF-8 bytes with duplicate/nonfinite/unknown fields rejected. Parse the unchanged
six-field custody contract; no local parsing or digest is Identity verification.

Only native post-commit profile evidence permits worker success. Parent and host
require exact selected/requested/validated profile plus sorted compact ASCII custody
SHA256 (null for dormant), exact revision and boolean complete success; old revision-
only evidence now blocks activation. No raw custody/URL is recorded. Host selects
safe failure observations, blocks unknown outcomes, preserves prior groups and
requires owned network cleanup. Duplicate environment keys reject; validated migration inputs are captured once
and privately frozen for this attempt, with temporary snapshots removed before
activation/on failure. Keep owner/runtime administration stable during release. The existing180s supervisor bounds
connection/checks/commit response with termination reserve; native SQL bounds stay.
No automatic reverse, profile switching, target normalization or stale evidence reuse.

This extends the earlier native-only delivery boundary, using one app-owned pure
build-time contract and the existing coordinator. Migration helper/image inputs and
host coordinator source enter compatibility fingerprints; old image evidence rejects.
Scaffold impact is this existing release consumer, no new factory runtime/pattern;
no shared UI/agent-context/new ADR. Live Identity/caller preparation, image/target
qualification, importer/writers and sealed publication remain gates. No Access/KDG,
Leave/factory, UX/standalone signup or applied revision/reference/source change.
Evidence179–181 records actual reds, characterization, corrected fixture/timeout
harnesses and pre-review full932/no skips236.49s, focused37/18.60s and platform66/42/7.55s.
Actual host coordinator plus bounded worker/database replay is proved with Docker/
activation calls replaced by a harness; no image run or live Identity proof is
inferred. Real COMMIT followed by injected acknowledgement loss leaves a durable
marker, no validation success, and permits explicit reconciliation. Forced supervisor
expiry stops only the owned test child after backend observation and proves SIGKILL/
reap/backend disappearance; native lock expiry/retry remains separately tested.
All three independent reviews returned; evidence182–183 records individual triage
and completed corrections.
Seven bounded findings are patched, one UTF8 claim refuted by unchanged-code tests,
one pre-existing stdout-buffering issue deferred in the existing tracker. Current
wire-size rejection follows communicate buffering, not a hard memory cap; worker
replies retain fixed bounded shapes and deadlines. Host now captures migration
inputs during preflight into private0600/0700 temporary snapshots, used by Docker
and evidence comparison and removed before activation/on failure. Source-file edits
cannot switch this attempt. Final-write failure clears success-only evidence,
nonfinite overflow/CRLF reject, and valid selection survives bad URL diagnostics.
Actual host coverage now includes denied, paused and rotated history. Focused24,
affected107/26 and platform70/42 pass. Final root full944/no skips294.43s passes
all47 host-profile cases plus897 retained application cases. Seven review fixes
complete, one finding refuted, one pre-existing defer. Exact owned disposable
fixture stopped/removed; no image/live owner/production verification inferred.

## Caller preparation handoff — specified, not executed

Decisions186–187 adopt the [app-owned preparation contract](../../../apps/scribeswell/docs/CORPUS_CALLER_PREPARATION.md)
as a load-bearing companion. Read it before consuming or preparing corpus operator
custody. It separates durable actor identity (Identity), actual database login and
local current command authority (Scribeswell), and committed profile evidence
(release owner). A service actor requires no Auth/person/employment/organization or
Access grant. The completed host-profile implementation does not establish live
identity or authorize preparation.

Owner-produced private evidence must bind preparation reference/window/UTC custodian,
authoritative Identity target/source/login, exact service UUID/kind/key and creation
provenance, complete registration command/original operation/acknowledged receipt
and event or equivalent owner inspection, explicit pairing to Scribeswell target,
actual migration/operator logins, source/three command authorities/revisions/flags,
real local preparation attribution and exact release source/image/profile evidence.
An unchanged registration may have no new event; retain original creation provenance.
Safe references/digests in release evidence do not authenticate a supplied record.
Retrieval and verification use the owners' approved protected channel; no signature,
JSON wire format, HTTP endpoint or automatic verifier is invented here.

Identity registration/recovery exists, but its compact receipt lacks actor kind/key,
original command fingerprint and target binding. Registration may create an actor;
do not use it as read-only verification. Current CLI target support is disposable
KDG/idop only, not live Scribeswell. Scribeswell performs no Identity table reads or
cross-owner runtime imports. Verify owner evidence before local locks, re-establish
provenance/target pairing on restarted windows and arrange stable owner administration;
do not claim distributed atomic verification. Concrete live plans must establish
authorization, bounds, compatibility and recovery before execution.

New local preparation uses disabled principal/authorities and false enforcement;
actual preparation executor attribution need not equal the service actor being
prepared. Preserve existing valid/paused/history states. Consume exact restricted
login/three-cell ACL/full authority checks and unchanged six-field custody schema;
select explicit prepared/history replay, never fall back to dormant. Successful
qualification does not enable commands/fencing/importer binding or publish text.
Conflicts, wrong target, missing provenance, unsupported proof or owner outage stop
before local effects. Unknown outcomes retain original operation/command for owner
reconciliation, never blind retry/new actor. Current authority governs execution,
replay and lookup without resurrecting revoked access. Decision188 qualifies live
rotation: owned0003 freezes kind/key/preparation reference and Identity retains unique
established keys, so a real replacement requiring a different key/reference blocks
pending a separately reviewed forward change. Synthetic UUID-rotation fixtures do
not establish live Identity compatibility; preserve old executors/outcomes.

The adopted companion lists Given/When/Then evidence for full handoff, forged/copied
records, mismatches/missing provenance, uncertainty, actual restricted-login denials,
paused/rotated history and restarted windows. These are required future preparation
and rehearsal cases, not passed live tests. The handoff delivery changed documents only; the later isolated local mapping
rehearsal adds bounded native software evidence, with synthetic owner identity. D1–D5,
actual owner/target/image preparation, importer/writers/publication and private
Studies remain gated. Access/KDG/Leave/factory, UX and standalone signup stay owned.


Independent caller-handoff review resolved five documentation gaps (decision188).
The adopted contract now specifies explicit revisions (new1, expected old+1), actual
preparer/session/target/run evidence with explicit insert/update actor attribution,
and one bounded READ COMMITTED transaction covering protected before-state and all
four mapping rows. Existing migration advisory then principal/authority SHARE ROW
EXCLUSIVE locks serialize cooperating preparation; no transition advisory lock or
external waits under them. Probe at most2principal/4authority rows and reject extras.
Prior role/secret preparation remains separately accounted. Local COMMIT uncertainty
has no controller outcome lookup: prove original session ended, compare complete
intended/before/actual state under fresh locks, block partial/conflict/unverified
termination and requalify profile. Identity recovery retains its original operation.
A subsequent isolated local mapping rehearsal exercises the transaction/concurrency/
failure protocol using actual PostgreSQL sessions and synthetic actor provenance.
Actual independent owner/session identity proof remains future qualification. No
production runner, owner implementation or applied revision changed.


The isolated local mapping rehearsal now passes29new cases and the affected
prepared/history suites pass228/no skips127.55s after review (evidence194).
It qualifies disabled atomic initial preparation, exact no-op, rollback, real
backend serialization/all three lock timeouts, native replay preservation,
restricted operator execute/lookup denial and ended-session COMMIT reconciliation.
Six review evidence gaps were fixed, none deferred. The first affected run had
223passes/one retained capacity statement-timeout; isolated26 and final228 pass
without changing production deadlines or expected results. Actor/session binding
is synthetic; the helper lives only under tests. Live Identity evidence, target/
image qualification, total execution/COMMIT deadlines and production preparation
remain open. This changes no D1–D5, owner, standalone signup or UX requirement.


The [app-owned preparation tool design](../../../apps/scribeswell/docs/CORPUS_PREPARATION_TOOL.md)
is adopted as companion21 (decisions197–199). Its parser is now implemented locally;
its admission/executor portions remain specified designs.
It closes the nine-field request/immutable parser error boundary, separate private
migrator target and trusted owner admission, proposed total execution/COMMIT bounds
and original-session recovery. References/UUIDs/parser values never prove authority.
Direct connections are required for proposed execution; pooler recovery is outside
this contract. Initial reuse requires the same preparer attribution or conflicts.
The initial parser implementation has no owner/file/network/DB effects;
specified worker result wire, unproved durable evidence capture and actual fixture admission
must close before SQL effects. Live owner channel/server identity/image/target proof,
Access/KDG/Leave/factory ownership, UX, standalone signup and D1–D5 stay unchanged.
No new runtime tests or live operations were run for this documentation delivery.


The preparation request parser is now implemented locally (decision203), consuming
the adopted tool contract's first two acceptance rows. It returns immutable nested
declarations through the app namespace and directly reuses unchanged pure custody
validation. Normal code loading is separate from parse calls; no referenced file,
owner, environment, network or DB is accessed during parsing. Equal preparer/service
UUIDs are permitted declarations, never authority. Repository-only import availability
is qualified separately from future runner packaging. The earlier tool document was
design-only; target/admission/deadline/result-wire/durable-attempt/executor and live
readiness remain specified/gated. UX, standalone signup, owner boundaries and D1–D5
are unchanged. Exact commands/results/review live in the
[parser delivery record](../../implementation-artifacts/spec-scribeswell-preparation-request-parser.md).


Reviewed parser evidence (event205): focused207passes2.23s and affected pure
394passes/11native cases deliberately deselected5.98s, with207new/187retained cases.
Six independent review findings were patched, none deferred; an actual two-case
caller-exception retention red preceded its fix. The safe error clears the real
caller/decoder context; depth/import/environment/command/UUID coverage is explicit.
No DB/image/provider/native/whole-app qualification is claimed. Existing pure
custody, applied revisions and owner implementations are unchanged.


The [worker result/attempt contract](../../../apps/scribeswell/docs/CORPUS_PREPARATION_EVIDENCE.md)
is adopted as companion22 (decisions208–209). Its original documentation delivery
ran no runtime tests; the five contract-review findings were fixed. The consuming
pure codecs are now implemented (decision213/event214), preserving the existing
request parser. They validate immutable values, canonical records/hashes, exact
original request and independently expected target, phase/proof/row/session
bindings, create timestamp equality and unchanged reuse. Partial prefixes are
readable; a worker reply requires matching terminal evidence. Encoders revalidate
manual values; one safe error clears decoder and active caller context. Fixed
independent digest oracles and isolated stdlib/no-I/O checks executed.

Final reviewed codec tests (event215):212focused2.41s; independently recreated
Python3.12/pytest9.1.1-only environment212passed2.20s. Affected pure tests606passed
8.57s with11native cases deliberately deselected. Eight verified blind-review
coverage/setup findings were patched, no deferrals or post-review codec behavior
change. Exact commands/setup and intermediate environment/collection failures are
in the codec delivery record and adopted app contract. Historical207/394 parser
evidence remains historical.
Correct hashes and schemas never prove custody or acknowledged persistence;
admitted-only missing session evidence remains unknown. File journaling is not
atomic database business audit: applicable ADR0022/0025 qualification stays required
before effects. Production storage/SQL/supervision/admission, real target/image/database and
crash qualification remain open. No live operations, UX/signup/owner changes,
Access/KDG/Leave/factory implementation or D1–D5 closure is inferred.11CAP/38ST and
all22companions remain stable. Byte/depth probes with multiple invalidities prove
safe rejection, not independent coverage of redundant guards.


### Local fixture record capture — implemented boundary

Decision218/event219 close the next app-local fixture storage contract in the
adopted [attempt-evidence document](../../../apps/scribeswell/docs/CORPUS_PREPARATION_EVIDENCE.md#fixture-storage-contract--bounded-consuming-slice),
without copying its filesystem/API schema here. Trusted root fd, exclusive run
reservation, owner modes, bounded canonical prefix validation, nonblocking locks
and no-clobber file-sync/publication/directory-sync acknowledgements are implemented
only for synthetic local fixtures. Failed appends poison the writer and retain
all residue. Read-only reopening returns validated retained bytes, including an
empty reservation, never proof of the original acknowledgement or no external
effect. No resume/cleanup/replay/live admission/SQL path exists.

Actual ATDD red preceded implementation. Final72storage tests passed7.80s;
affected pure suite678passed20.15s with11native database cases deliberately
excluded. Seven blind-review timing/coverage findings were addressed, no deferrals.
First and later-record process deaths preserve earlier acknowledged bytes; stalled
sync is terminated by the test harness after readiness, not a delivered supervisor.
Exact commands, intermediate fixture failure, setup and local ext2/ext3 evidence
are in the adopted app contract and delivery record. Existing codecs/request parser
remain unchanged. Physical power-loss, production filesystem, kernel I/O deadlines,
real owner/target/image admission, atomic business audit and supervised SQL effects
remain gated.11CAP38ST22companions, agreed UX/standalone signup and separate
Access/KDG/Leave/factory ownership remain intact; no D1–D5 closure is claimed.


### Synthetic communication supervisor — implemented boundary

Decision222 and events223–224 close the app-local
[fixture supervisor contract](../../../apps/scribeswell/docs/CORPUS_PREPARATION_TOOL.md#fixture-communication-and-supervisor-contract).
It exchanges already supplied synthetic terminal declarations through a fixed
isolated stdlib child. Parent independently validates original request/target/
prefix/reply; no parent storage/owner reads, new persistence acknowledgement or
SQL occurs. Frozen `fixture_reply_validated` observations prove communication only,
including when embedded fixture labels say committed/reused. The private closed
transport and unchanged codecs retain separate ownership and meaning.

All phases charge one58work/60total/2remaining-cleanup budget from public entry;
stdin65536/stdout4096 caps apply during transfer, stderr is discarded, no final
drain/retry or public timeout/command/env/callback override. Reaping after a kill
request requires observed SIGKILL before forced-stop attribution; natural exits
in that race stay child_exited. Final total deadline is rechecked after cleanup;
unverified termination remains explicit. OS/spawn scheduling is charged on return,
not claimed hard realtime preemption.

Actual acceptance red preceded implementation. Seven blind findings were fixed,
none deferred; two behavior regressions observed red2failed1.81s then green2passed
1.81s. Final83focused6.76s and761affected15.01s with11native database cases excluded;
63/741 are pre-review evidence. Real isolated malformed/overflow/live refusal,
well-formed mismatched bindings, byte bounds/backpressure, elapsed stalls and
repeated actual forced reaping/fd stability are exercised; fake clocks verify
shared and shrinking budget arithmetic. Exact commands/setup/intermediate failures
are in the adopted tool/evidence documents and delivery record. Existing codecs,
request parser and fixture store remain unchanged. Actual storage/SQL/owner/image/
server/current authority/atomic-audit and physical crash/deadline integration gates
remain open.11CAP38ST22companions and UX/signup/Access-KDG-Leave-factory boundaries
are preserved; no D1–D5 closure or production executor availability is inferred.


Supervised synthetic capture now integrates the existing store and shared bounded
supervisor (direction227/event228). The [owning contract](../../../apps/scribeswell/docs/CORPUS_PREPARATION_EVIDENCE.md#supervised-fixture-capture-contract)
closes version2 fd/transport/ack semantics without changing version1 or DB schema.
Child-only append acknowledgements, close and exact independent readback precede
reply; parent status fixture_records_acknowledged is not preparation SQL success.
Unknown retains every reservation/residue and never upgrades readable files to a
lost original acknowledgement.152capture+legacy/830affected checks passed,11native
cases excluded; six review findings addressed. Real owner/current authority/image/
server/atomic-audit/SQL and physical power-loss gates remain open. Delivery now
returns to Studies business readiness rather than automatically extending tooling.
