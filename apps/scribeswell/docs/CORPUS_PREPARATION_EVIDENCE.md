# Preparation worker result and attempt evidence

Status: **specified contract, not implemented or crash-qualified**. The
[request parser](CORPUS_PREPARATION_TOOL.md#implemented-parser-and-qualification)
is implemented; the worker, codecs, storage writer and admission mechanism below
are not. Historical 207/394 parser tests do not qualify them. Consume the existing
[owner handoff](CORPUS_CALLER_PREPARATION.md) and
[tool policy](CORPUS_PREPARATION_TOOL.md) without changing their request/custody,
60-second total/58-second work/2-second cleanup, direct-connection or owner rules.

A **worker result** is its bounded reply. An **attempt record** retains what was
admitted, observed and intended across failures. **Durable** means acknowledged
storage persistence, not merely a successful write into a process buffer. Neither
a checksum nor a correctly shaped record independently verifies its custodian.

## Encoding and bindings

All formats below are closed version 1 UTF-8 JSON objects: reject BOM, duplicate
keys at every level, extra/missing fields, wrong types, floats/nonfinite numbers,
invalid UTF-8, trailing JSON values and excessive byte/depth limits before effects.
Canonical encoding uses sorted object keys, compact comma/colon separators,
`ensure_ascii=True`, no newline, and no coercion. Arrays retain prescribed order.
Hashes are lowercase 64-character SHA256 hex over those exact canonical bytes.
A record's own digest is external to it; hash its complete canonical bytes,
including its previous-record and request/target binding digests.

UUIDs and durable evidence references use the existing request parser's canonical
nonnil UUID and bounded ASCII reference rules. Operational times and database
snapshot times are valid Gregorian UTC strings exactly
`YYYY-MM-DDTHH:MM:SS.ffffffZ`, years 0001–9999, no leap seconds or infinities. Operational
`recorded_at` comes from the execution clock; database attribution times come only
from server observations, never that clock. Do not widen unsupported values to fit.

`request_sha256` hashes the parsed request projected back to its exact nine named
fields, with its six named custody fields. It is semantic input identity, not raw
byte identity or authority. Retain original request bytes separately as specified
below. `target_sha256` hashes a credential-free target descriptor with exactly:

| Field | Type and rule |
|---|---|
| `kind` | `local_disposable` or `supabase` |
| `binding` | Existing target binding, local exact database or canonical HTTPS project URL with no trailing slash; ASCII length 1–8192 |
| `host` | Canonical lowercase ASCII DNS hostname, max 253, or literal 127.0.0.1/::1 |
| `port` | Integer 1–65535, default resolved explicitly to 5432; boolean excluded |
| `database` | Local exact binding, or `postgres` for Supabase |
| `login` | Literal `scribeswell_migrator` |

Local binding/database follows the tool's existing name rule and literal loopback
host requirement. Supabase binding is `https://<ref>.supabase.co`; host must be
`db.<ref>.supabase.co`, using the same nonempty lowercase alphanumeric project ref.
Poolers are refused. Credentials/URL query/transport secrets never enter this
projection or its public digest. Current credential authority and approved TLS
configuration must still be independently checked on every admission; the digest
is not proof of either. This defines projection identity, not a target parser.

## Private worker reply

One JSON object, at most 4096 transport bytes including whitespace, depth at most 2
(root object depth 1), all fields below required. Parent caps bytes **while reading**;
no unbounded pipe buffering, no stderr pipe (use null device). Worker exit must be 0,
reply must finish and be validated before the existing work deadline. Otherwise
parent reports unknown and performs bounded cleanup without automatic retry.

| Field | Exact rule |
|---|---|
| `schema_version` | Integer 1, excluding bool/float |
| `run_id` | Original canonical request UUID |
| `request_sha256` | Original normalized request digest |
| `target_sha256` | Original admitted target descriptor digest |
| `record_sequence` | Integer 2–4, excluding bool/float |
| `record_sha256` | Digest of the durable terminal attempt record below |
| `outcome` | `committed`, `reused`, `rejected`, `rolled_back` or `unknown` |
| `code` | Exact compatible safe code from the table below |

| Outcome | Allowed code | Required terminal evidence |
|---|---|---|
| `committed` | `preparation_committed` | Create mode, full prepared snapshot, successful driver COMMIT acknowledgement, durable terminal record |
| `reused` | `preparation_reused` | Reuse mode, exact unchanged original snapshot, acknowledged check transaction and durable terminal record |
| `rejected` | `admission_denied`, `target_mismatch` or `preparation_conflict` | No mapping writes issued; terminal directly after admission |
| `rolled_back` | `preparation_rolled_back` | Explicit rollback acknowledgement or independently established ended transaction/no effects; never inferred from a killed process |
| `unknown` | `outcome_unconfirmed` | Worker cannot establish completion; no success or rollback claim |

Parent checks run/request/target identity, terminal sequence/hash/outcome/code and
valid complete prefix obtained from its **trusted attempt custody**, not an arbitrary
path or a second worker assertion. A schema-valid forged reply or copied journal
is insufficient. A declared committed result without its matching durable record
stays unknown. Absence of a worker record/reply also stays unknown after possible
effects. Known parent rejection before launching is a separate local result; it
does not manufacture a worker record or imply earlier owner role/grant rollback.

This reply is private IPC, not a new HTTP API or controller receipt. Parent-owned
public diagnostics select only the safe outcome/code/run, digests and termination
observations; never copy arbitrary payloads or expose snapshots/credentials.

## Attempt record envelope and finite phases

A record accepts exactly Python bytes, at most 32768 **raw transport bytes before
decoding**, depth at most 8. Decoding must also require byte-for-byte equality with
canonical re-encoding: reject whitespace, alternate escapes/key order or any other
noncanonical spelling rather than normalize it silently. At most
four worker records and 131072 canonical bytes per attempt. Each record has exactly:

| Field | Exact rule |
|---|---|
| `schema_version` | Integer 1 |
| `run_id` | Same request UUID in every record |
| `sequence` | Integer 1–4, contiguous from 1 |
| `previous_sha256` | Null only for sequence 1; otherwise exact previous record digest |
| `request_sha256` | Same semantic request digest throughout |
| `target_sha256` | Same descriptor digest throughout |
| `recorded_by_actor_id` | Actual verified executing preparer, matching admitted request; supplied UUID alone is not attribution proof |
| `recorded_at` | Valid canonical UTC operational observation time |
| `kind` | `admitted`, `intent`, `prepared` or `finished` |
| `payload` | Exactly the corresponding shape below |

Every numeric value is an integer of its specified bounds; JSON booleans are never
integers. No optional/extension fields or arbitrary strings/errors are allowed.
Records link by digest; this detects accidental divergence under retained custody,
not malicious replacement/truncation by an untrusted writer. Preserve the original
request and entire acknowledged prefix; an endpoint hash alone does not prove it.

### admitted — sequence 1

Payload has exactly `request_b64`, `target`, `reviewed_commit`, `image_digest`,
`admission_ref`, `admission_class`. `request_b64` is strict canonical padded RFC4648
standard base64 of the original accepted request bytes (decoded at most 8192 bytes);
reparse it with the existing parser and require matching run/digest/preparer.
`target` is the descriptor above. `reviewed_commit` is the full canonical lowercase
40- or 64-hex Git identifier; `image_digest` is `sha256:` plus 64 lowercase hex.
`admission_ref` is a durable reference to the independently retained admission and
source/image/target pairing; `admission_class` is `synthetic_fixture` or
`owner_verified`. Neither enum nor reference establishes trust by parsing it.

Only an independently controlled fixture launcher may produce synthetic admission;
the first executable qualification must reject live targets/admission entirely.
`owner_verified` has no live producer/consumer implementation here and stays gated
on the existing owner channel/authentication/server identity/source/image proof.
Retain creation/initiator provenance in that record without inventing human actors.

### intent — sequence 2, before first mapping write

Payload has exactly `mode`, `session`, `before`, `intended`.
`mode` is `create` or `reuse`. `session` has exactly `session_user`, `current_user`,
`database`, `backend_pid`, `backend_start`, `server_identity_ref`, `ledger_head`,
`transaction_isolation`, `transaction_read_only`, `authority_observation_ref`:

- Both users are exactly `scribeswell_migrator`; database matches descriptor.
- PID is integer 1–2147483647; backend start is canonical server UTC.
- Server identity reference is a durable owner-qualified observation bound to the
  exact target/server and execution window, not a hash/URL self-assertion.
- Ledger head is literal `scribeswell_0003`, isolation literal `read committed`,
  and read-only is boolean false. These are actual checked transaction observations.
- Authority observation reference follows the bounded durable-reference rule and
  resolves through trusted custody to the retained restricted-role/ownership/ACL
  inventory for this exact session/target/run and source/release qualification.
  Capture/retain that inventory outside mapping locks; re-establish current checks
  before effects. Neither the reference nor its hash is itself authority proof.

These actual observations and the owner execution channel must bind the admitted
preparer/run; PID/start or `SET ROLE` alone grants no authority. Capture under the
handoff's migration advisory then principal/authority locks, before any insert.
No external service/store wait is allowed while those locks are held.

`before` and `intended` are named snapshots below. For create, before is empty;
intended has all four exact semantic row values with null database timestamps
(they have not been observed yet). For reuse, before/intended are the identical
complete existing rows with real timestamps. Current request preparer must match
all stored creation/update actors; another preparer conflicts without changes.
Partial/extra/conflicting probed configuration rejects before this phase, never
normalizes state or retains an unbounded dump. Keep probe bounds 2 principal/4 authority.

### prepared — sequence 3, postchecks before COMMIT

Payload has exactly `observed`, the complete actual four-row snapshot after all
protected postchecks. All timestamps are real server-returned values. Every
semantic value must match intent; create timestamps must be nonnull, creation/update
times equal **across all eight timestamp fields**: one identical server
`transaction_timestamp()` value for principal and all three authorities. Reuse
observation must equal before/intended including every timestamp/revision/actor. No external evidence wait
or controller transition advisory lock is introduced. Persist this second checkpoint
before COMMIT; it is a prepared **candidate**, never proof that COMMIT occurred.

### finished — terminal sequence 2, 3 or 4

Payload has exactly `outcome`, `code`, `proof`, using the reply's exact table and
meanings. `proof` has exactly `kind`, `evidence_ref`; valid combinations are:

| Outcome | Proof kind | Evidence reference |
|---|---|---|
| committed/reused | `commit_ack` | Nonnull durable reference to the actual driver COMMIT acknowledgement observation bound to this run/session |
| rolled_back | `rollback_ack` or `ended_no_effects` | Nonnull reference identifying which actual acknowledgement or independent ended-session/no-effects observation supports it |
| rejected | `pre_write` | Nonnull reference to the trusted worker's no-mapping-write observation |
| unknown | `unconfirmed` | Null, never a fabricated success/rollback proof |

Each nonnull reference follows the request's existing reference bounds and must
resolve in trusted custody before the terminal record is acknowledged. Codecs check
its type/binding only; the executor must retain the actual supported observation.
A rollback acknowledgement and independent no-effects observation stay distinguishable.
The reply remains eight fields and refers to this terminal record rather than
exposing its private proof record. The finite paths below remain mandatory.
Allowed paths are only:

| Prefix | Terminal outcomes |
|---|---|
| admitted → finished | rejected or unknown |
| admitted → intent → finished | rolled_back or unknown |
| admitted → intent → prepared → finished | committed(create), reused(reuse), rolled_back or unknown |

A terminal record after COMMIT is written only after acknowledgement. Failure to
persist it leaves the parent unknown even if the database committed. No record is
rewritten to convert intention into success. No committed/reused record may precede
prepared. No original worker record may follow finished. Recovery observations
are separately retained against the original prefix; they never overwrite it.

## Snapshot row schemas

A snapshot has exactly `principal` (null or PrincipalRow) and `authorities` (array).
Empty means null/empty array. Complete means one principal and exactly three distinct
authorities, ordered `corpus.begin`, `corpus.recover`, `corpus.seal`, all for the
request's source. No surplus rows, extra object keys or silent truncation. The
existing database columns are retained by name, not tuple offsets:

PrincipalRow exact fields:
`database_login`, `enabled`, `revision`, `executor_actor_id`, `actor_kind`,
`actor_key`, `preparation_evidence_ref`, `created_by_actor_id`, `updated_by_actor_id`,
`created_at`, `updated_at`.

AuthorityRow exact fields:
`database_login`, `source_id`, `command`, `enabled`, `revision`,
`created_by_actor_id`, `updated_by_actor_id`, `created_at`, `updated_at`.

Login is always `scribeswell_corpus_operator`; enabled is boolean false; revision
is decimal string `"1"` (wire bigint spelling, not a JSON float/bool). Principal actor
UUID/kind/key/preparation reference match unchanged request custody; each authority
source/command matches its exact requested scope. Creation/update actors are the
request's independently established preparer. UUID/label/reference bounds remain
unchanged. Database timestamp fields are canonical server UTC strings, null **only**
for the create-mode intent template. Empty snapshots occur only before create.
Actual complete snapshots have all eight timestamp fields nonnull. Reuse preserves
original immutable creation attribution, and never increments revisions.

## Proposed durable capture and crash rules

A trusted launcher allocates an exclusively owned local attempt directory mode 0700
using a retained approved custody root, never a request-supplied path. Reserve the
run identifier with create-only semantics; never overwrite/reopen the original
attempt for another execution. Same-run concurrent launch refuses. Credentials do
not enter the retained request, descriptors or journal. Use mode 0600 record files,
fixed generated names `000001.json`…`000004.json`, trusted directory descriptors,
no symlink following, no unexpected existing entries/alternate hardlink aliases.
Permissions are one part of trusted custody, not an admission mechanism by themselves.

One trusted worker writes the finite prefix. For each checkpoint: serialize under
the byte cap, write a fresh private temporary file in that owned directory, flush
and fsync its contents, publish the final name atomically with no replacement,
then fsync the directory. Only the acknowledged final file may permit the next SQL
phase. Partial/unpublished temporary files or a failed/uncertain sync are not
acknowledged evidence. Never report success from a hash computed before persistence.
No unbounded flush/retry loop or post-timeout final pipe drain is permitted.

Local persistence is charged to the same supervised work budget. The two short
local capture waits under mapping locks are an explicit bounded design exception
for recoverable operational evidence; remote publication stays after unlock under
[ADR-0022](../../../platform/docs/architecture/decisions/0022-short-transactions-and-external-service-calls.md).
The storage implementation must prove termination/failure behavior and recovery
on its actual local filesystem before effects rely on it. A killed child can leave
a durable candidate, an orphan backend or a real commit. A reap is not rollback.

If admitted persistence fails, do not connect. If intent persistence fails, do not
write. If prepared persistence fails, do not COMMIT; attempt bounded rollback,
otherwise remain unknown. If COMMIT/reply/terminal persistence is lost, retain
unknown and the original prefix. External owner-channel publication is separate:
its outage must not delete/clean the durable local record or erase committed state.
Retain nonterminal/unknown evidence until owner reconciliation and required
publication/retention policy acknowledge it; there is no automatic age-based cleanup.
Missing/corrupt/partial records block further writes/activation; do not fill gaps,
trust a disconnected tail, invent before-state or silently truncate to a valid prefix.

An admitted-only prefix has no journaled session or before-state. Recover its
request's `session_authorization_ref` through the trusted owner channel; it may
retain independently captured actual connection/session observations. If a trusted
launcher proves connection was never attempted, it can establish no local effect
without manufacturing a worker success. If connection may have occurred and exact
session identity is missing/unverified, the outcome remains unknown: no row comparison,
new preparation or inference from empty tables is allowed. Child reap alone is
insufficient. An incomplete intent capture is not a substitute before-state; only
independent owner investigation can establish the missing facts. This contract does
not claim every early crash can be resolved from the four-record prefix alone.

Recovery with retained session/before evidence first proves original backend/session
ended using target/server/PID/start under current owner authority, then compares actual complete state with before and
prepared under the same locks in a new bounded inspection. No prepared snapshot
means no trustworthy exact committed-candidate proof; do not infer completion from
semantic similarity. Exact candidate with retained provenance supports committed;
unchanged before-state supports no observed effect; exact no-op supports reuse only.
Partial/extra/mixed/conflicting state stops. No controller operation/outcome lookup,
new actor, automatic replay, repair, migration reversal or fence change is supplied.

This journal is **operational attempt/recovery evidence**, not an atomic database
business-audit record. A local file fsync and mapping COMMIT are separate durability
domains. Owned0003's controller outcome table does not audit preparation writes.
Any execution requiring consequential immutable audit must close its app-owned
atomic audit design/forward-migration compatibility proof under
[ADR-0025](../../../platform/docs/architecture/decisions/0025-record-attribution-and-audit-provenance.md)
before SQL effects; this document supplies neither that audit nor permission to edit
applied revisions. No live execution readiness is inferred from the journal design.

## First consuming delivery and evidence

The next bounded implementation is a pure app-owned codec/immutable value model for
these closed result/record/snapshot formats, deterministic serialization/hashing and
finite-prefix validation. It must use the existing request parser and have no
file/environment/network/database/admission/storage effects. Its single safe local
error code/message is `scribeswell_preparation_evidence_invalid`, with no submitted
payload or chained decoder/caller context. The codec validates declarations and
bindings; trusted custody, database observations and persistence require later proof.

| Given | When | Required future evidence |
|---|---|---|
| Literal valid create/reuse prefix and reply | Codec parses/encodes/hashes them | Exact immutable fields, independent known digest oracle, exact parent binding and ordered snapshot equality |
| Wrong fields/types/raw-versus-canonical bytes/depth/UUID/time/base64/digest/code/proof, different create timestamps across rows, reordered/missing/extra phase or row | Codec validates | Fixed safe failure, zero effects; no disconnected success |
| Matching hashes supplied from an untrusted source | Parent considers reply | No admission/persistence proof; trusted record channel still required |
| Local writes/sync/publish/parent die at each checkpoint | Physical capture is qualified | No later SQL phase without acknowledged checkpoint; possible committed effects remain unknown |
| Admitted-only prefix after possible connect, with missing independent session evidence | Recovery is attempted | Unknown; no invented session/before-state or snapshot comparison |
| Two launches with one run, alias/symlink or full/unavailable disk | Storage is qualified | Refuse overwrite/unsafe capture; bounded failure and preserved evidence |
| COMMIT succeeds but terminal/reply/publication fails | Executor/recovery is qualified | Retain original candidate; verify backend end and whole state; no rollback assumption or blind retry |
| Consequential atomic audit or real owner/server evidence is absent | Execution readiness is evaluated | Keep the relevant gate open; a valid codec/journal is insufficient |

These are future acceptance cases, not tests run here. No codecs, file writer,
supervisor, target/admission verifier, schema/migration or production operation is
implemented. Scaffold/shared UI/agent-context/accepted ADR impacts are documentation
only; no generic pattern is promoted. Agreed Studies UX, standalone signup and
separate Access/KDG/Leave/factory ownership remain binding.
