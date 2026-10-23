# Caller preparation tool contract

Status: **pure parser implemented locally; admission verifier and preparation
executor remain specified designs**. The [owner handoff](CORPUS_CALLER_PREPARATION.md)
remains authoritative for provenance, scope, atomic mapping and recovery. Its
29-case isolated rehearsal proves a local protocol with synthetic actor evidence;
it does not prove this proposed supervision or live admission. The earlier 228-test
result belongs to that rehearsal delivery, not this document.

A **request** declares the intended preparation. **Admission** establishes that the
current executor may perform it using independently retrieved owner evidence.
A **deadline** limits how long an invocation may work. An **acknowledgement** is the
reply confirming a completed database commit; losing it does not undo the commit.
These distinctions determine the first bounded implementation slice below.

## Closed request version 1

The pure `parse_preparation_request(raw)` accepts exactly Python `bytes`
(not text/bytearray/other types) containing one UTF-8 JSON object, at most 8192 bytes before
decoding, nesting depth at most 4 (root object depth 1). Reject a UTF-8 byte-order
mark, empty/whitespace-only input and invalid UTF-8,
duplicate keys at every level, nonfinite numbers (including numeric overflow),
trailing JSON values, missing/extra fields and wrong types. Do not coerce booleans,
floats, numbers, nulls or strings into another field type. Only these nine root
fields are allowed, all required:

| Field | Exact contract |
|---|---|
| `schema_version` | Integer `1`, excluding boolean and float values |
| `command` | String literal `caller.prepare_initial` |
| `run_id` | Nonnil canonical lowercase hyphenated UUID string identifying this execution attempt |
| `custody` | Exactly the existing six-field object accepted by `migrations/release_profile.py:validate_custody`, including its integer version, UUID and ASCII field bounds |
| `preparer_actor_id` | Nonnil canonical lowercase hyphenated UUID string for the independently established actual preparation executor, separate from the corpus service actor |
| `target_plan_ref` | Durable reference to the approved exact target/compatibility/recovery plan |
| `identity_observation_ref` | Durable reference to owner-produced complete actor/Identity target/provenance evidence |
| `session_authorization_ref` | Durable reference connecting current authorized preparer/run to the actual execution session and target |
| `release_binding_ref` | Durable reference to reviewed source, qualified immutable image and selected release profile |

Each of the four reference fields is a string matching ASCII
`[A-Za-z0-9][A-Za-z0-9_.:/-]{0,255}` exactly. Reuse custody's existing field rules
without extending that schema or changing its digest. References contain no
credentials, request payloads or bearer URLs. They identify owner records; the
parser never opens a path/URL, queries a service, imports Identity server code,
resolves authorization or reads environment variables. A parsed value must be
immutable, including its nested custody; it is an untrusted declaration.
The `PreparationRequest` and nested `PreparationCustody` value expose the table's named
fields, contain no mutable dictionaries/lists and suppress payload repr. Use
`backend/caller_preparation_input.py` and
`tests/test_caller_preparation_input.py` for the first consuming delivery.
Reject all invalid input with a dedicated `PreparationRequestError` exposing only
a `.code` and string message both exactly `scribeswell_preparation_request_invalid`,
without submitted data,
driver text or chained decoding/validation exception context. It is a local parser
error, not an HTTP contract or proof that any owner rejected the command.

`run_id` is an attempt reference, not a database idempotency key or controller
operation ID. Retries/reconciliation must retain the original attempt and inputs.
A genuinely new authorized execution gets a new run only after uncertainty is
resolved; a new UUID cannot bypass conflicting or partially prepared state.

No timeout override, actor display name, email, organization, enabled flag, revision,
SQL, generic action, `verified:true`, verification callback or authorization token
belongs in this request. Initial preparation writes revision 1, disabled mappings
only. Existing coherent history or mutable updates belong to another contract;
this initial tool refuses rather than alters them. Exact matching initial rows may
be reused without any timestamp/revision/attribution changes. For this initial
contract, every declared custody/scope value and every row's creation/update actor
must match the request, including the current `preparer_actor_id`; all four revisions
are 1 and all enabled flags false. A different currently authorized preparer is
refused as a preparation conflict, never silently substituted into old attribution.
Allowing another preparer to reuse prior preparation needs a later explicit contract
with its retained provenance; the present rehearsal does not prove that case.

## Private target and trusted admission

Credentials travel separately from the retained request, in an explicit frozen
preparation target: `kind`, `database_url`, `binding`. Each value is a nonempty ASCII
string of at most 8192 bytes with no whitespace/control characters. Use
`local_disposable` or `supabase` kinds only. The actual login is
`scribeswell_migrator`, never the corpus operator or administrator. The existing
[command target](CORPUS_OPERATOR.md) enforces a different role and cannot be reused
unchanged. Reuse the platform's pure project/TLS binding contract with the required
migrator role, without importing another owner's server implementation.

For `local_disposable`, allow literal 127.0.0.1/::1 only, an exact declared database
name matching `[A-Za-z_][A-Za-z0-9_]{0,62}`, and matching decoded URL database/login;
`localhost` is not admitted. For `supabase`, require exact approved HTTPS project,
project/role database binding and TLS under the existing platform target contract.
For this preparation design, Supabase execution additionally requires the direct
`db.<project-ref>.supabase.co` endpoint; refuse every pooler endpoint even if the
shared validator accepts it. Do not infer session-pooling mode from a port or URL.
Backend PID/start recovery below relies on a session-preserving direct connection;
pooler/transaction-identity support requires a separately specified and qualified
extension. Existing command/migration tooling retains its own target policy.
Both reject malformed escapes, multiple hosts (literal or encoded), URL options,
ambient credentials and unexpected query keys; only single `sslmode` and
`connect_timeout` entries with the existing command-target syntax/ranges are allowed.
A URL/name does not establish exclusive disposable ownership or production custody.

A trusted owner-controlled launcher must retrieve the four referenced records
through the approved private owner channel and establish preliminary current
admission before opening the target connection. Complete session-bound admission
before any write; append actual backend observations to the same retained record. A caller-supplied file, path, matching hash, UUID, receipt or
`Verified...` object constructed from those values is insufficient. No live
admission implementation or general Identity verification API is presumed to exist.
The KDG disposable Identity CLI remains outside this application's implementation.

| Record | Required match before effects |
|---|---|
| Target plan | Exact authoritative Identity/Scribeswell environment pairing, source, actual database/server identity, authorized migrator/operator identities, privilege/ownership inventory, execution window, previous-version compatibility and recovery. The target supplied privately must match this plan. |
| Identity observation | Exact custody service UUID/kind/key, creation/registration provenance and original owner operation/acknowledged outcome or equivalent owner inspection; same authoritative Identity target and preparation evidence reference. Registration is not a read-only verification. |
| Session authorization | Current independently established preparer actor, authority for this initial preparation, run/target/window, actual approved execution mechanism and accountable owner. Actor existence alone grants no authority. |
| Release binding | Full canonical reviewed source commit and qualified immutable image identity, target/source pairing and explicit `prepared-controller-v1`; later resulting committed validation is attached after preparation, never required as a circular precondition. |

Evidence retrieval and external owner waits finish outside local write locks.
Observations apply to this bounded executing window only. Restarts/delays outside
the window require fresh admission; no stored request becomes a perpetual grant.
A coordinated owner DDL/role window must hold through preparation and qualification.
Do not turn a missing current check into permission to proceed.

Before mapping writes, bind observed `session_user=current_user=scribeswell_migrator`,
actual database and owner-qualified server/cluster identity, backend PID **and backend
start**, source/ledger head, writable READ COMMITTED transaction and restricted role
inventory to the admitted run and preparer. The target plan must define the permitted
server identity observation for its environment. `SET ROLE`, GUCs, shell usernames
and a caller-supplied actor cannot supply this proof. Retain the actual observations
through the trusted execution channel. PID alone risks reuse; actor-to-session
provenance still comes from that channel, not PostgreSQL actor fields.

The first executable scope is **pure parsing only**. A later supervised disposable
executor may use explicitly synthetic fixture admission from an independently owned
guarded cluster, labelled synthetic in its evidence, with live kinds disabled.
Production execution stays blocked until its concrete owner evidence channel,
authentication/current-authority checks, server identity method and qualified
source/image/target plan are supplied and proved. This design does not fabricate
those missing owner capabilities or authorize their implementation here.

## Proposed execution and deadline policy

The future app-local executor performs only initial mapping/reuse. Role, credential
and ACL installation are separate owner operations, already complete before entry.
It must use the handoff's single transaction, migration advisory lock then principal/
authority SHARE ROW EXCLUSIVE locks, bounded before-state probes and atomic four-row
writes/postchecks. Reject partial/conflicting state; never normalize enabled flags,
reset revisions, rotate immutable keys, change fencing or invoke the importer.

Adopt a fixed 60-second monotonic total from entry, reserving the last 2 seconds for
cleanup: work deadline at 58 seconds. These are preparation-specific proposed bounds,
not claims that existing preparation tooling implements them. Admission, bounded
parsing/serialization, owner checks, spawn, connect, SQL, COMMIT and parent response
validation share the same budget; no phase starts another 60 seconds. Work that cannot
fit before the work deadline is refused or stopped. Trusted owner checks that may
block must execute under supervision, before acquiring mapping locks.

| Boundary | Required ceiling |
|---|---|
| Connect/authentication | At most 5 seconds and remaining work time |
| PostgreSQL statement/lock waits | At most 5 seconds/2 seconds respectively and remaining work time; never widen a shorter caller/target setting |
| Idle transaction | At most 5 seconds and remaining work time; no external owner wait within it |
| COMMIT, byte transfer and complete child work | Same parent work deadline; SQL timeout alone does not bound commit acknowledgement |
| Direct-child kill/reap | At most 2 seconds and remaining total time; unverified termination remains explicit |

Do not set a positive sub-millisecond remainder to zero (PostgreSQL zero disables
timeouts); refuse when a positive bounded value cannot be represented. Recompute
remaining time before each blocking phase; active parent supervision bounds a
phase whose lower-level timeout cannot express the remaining precision. Bounded
synchronous admission/Popen and OS scheduling may overrun while control is away:
charge their time, stop on return, report truthfully. This is not a hard real-time
preemption guarantee. No caller-selected extension or automatic restart is allowed.

Use an isolated trusted child with fixed app import roots/environment, credential
and request transfer over private stdin only, stderr redirected to the null device
(with no pipe or retained buffer), explicit
password-only libpq credential policy, no passfile/client certificate/GSS discovery,
and unchanged validated TLS trust. Bound total encoded private request transport
at 65536 bytes; parent and child reject overflow during streaming, before buffering
more. Cap response transport at 4096 bytes **while reading**, reject duplicate keys,
invalid types, oversized/nonfinite/forged response and nonzero exit. Do not copy the
host migration parent's deferred unbounded buffering behavior. Supervise only the
trusted direct child; it must create no descendants.

The worker may acknowledge success only after exact mapping postchecks and driver
COMMIT acknowledgement. The parent must validate the result against original
run/request/target binding before reporting it. An original no-op is also a completed
read/check transaction and must be acknowledged before reporting reuse. Mapping
success is not release qualification: run the existing prepared host validation
separately after locks release; its failure blocks readiness without reversing
committed preparation.

## Outcomes and recovery

These are semantic outcomes; a closed child/result wire schema must be specified
with the supervised executor delivery before it is implemented. The next pure
parser depends only on the request table above, not a provisional result format.

| Outcome | Evidence required | Further action |
|---|---|---|
| Rejected before effects | Parent established invalid input or failed admission before the child could connect/write | Fix input/evidence; no new local mapping effect claimed. Earlier owner role/grant operations are separate. |
| Confirmed transaction failure | Explicit rollback acknowledgement or independent proof original transaction ended without local effects | Preserve before-state/failure evidence; no automatic retry. |
| Committed initial preparation | Acknowledged COMMIT, exact complete disabled bundle and validated request-bound response | Retain preparation evidence; require separate committed profile qualification. |
| Reused initial preparation | Acknowledged check transaction and exact unchanged initial bundle | Preserve existing provenance/revisions/timestamps; do not claim a new insert. |
| Unknown | Timeout, lost/malformed/forged response, uncertain COMMIT, process/transport failure or unverified termination | Block new writes/activation, retain original attempt and reconcile. |

Killing/reaping a child never proves its database backend ended or that COMMIT
rolled back. Supervisor warnings distinguish `forced_termination_reaped` from
`termination_unverified` and never claim resumed processing without evidence under
[ADR-0027](../../../platform/docs/architecture/decisions/0027-bounded-worker-shutdown-and-deployment-reporting.md).
A safe denial returned before writes may be preserved; after possible effects,
missing trustworthy acknowledgement remains unknown even if local process exit was 0.

Before writes, retain a protected append-only attempt record through the approved
owner evidence channel: original request, run/target/source/image binding, actual
session identity (PID/start/target), preparer/admission provenance, locked whole
before-state and exact intended four-row values. Retain server-owned timestamp
observations when available; recovery must not invent them from client time.
Required evidence retention must be acknowledged before allowing mapping COMMIT;
its failure aborts the transaction. Never wait on an external evidence store under
mapping locks: the executor design must provide bounded local durable capture
within the trusted launch custody, with later owner-channel delivery after unlocking.
The actual custody/storage implementation must be qualified before relying on it.

After uncertainty, establish through the exact owner/target/session identity that
the original transaction/session ended and cannot later commit. If inspection is
unavailable, PID/start cannot be matched or termination is unverified, retain unknown.
In a fresh bounded admitted transaction under the same locks, compare the complete
actual principal/three-authority rows with intended and before-state, including
revisions/attribution and retained server timestamps when known. Exact intended
state with trusted provenance supports committed; unchanged before-state supports
no observed local effect. A no-op may match both and establishes reuse only, never
a new write. Partial/extra/mixed/conflicting state stops for owner investigation.
Never auto-repair, blindly replay, clear history or call a nonexistent preparation
controller outcome API. Original Identity-registration recovery remains separately
owned and uses its original operation, not this preparation run.

Safe public diagnostics expose only stable outcome/code, run identifier, phase,
selected request/target digests and bounded termination observations. No URLs,
credentials, raw requests/receipts, full mapping snapshots or driver/traceback text.
Complete sensitive provenance belongs in protected evidence under
[ADR-0023](../../../platform/docs/architecture/decisions/0023-structured-operational-logs-and-sensitive-data.md).

## Acceptance and delivery boundary

| Given | When | Required evidence |
|---|---|---|
| Exact version 1 request | Pure parsing succeeds | Immutable nested value, unchanged six-field custody; zero environment/file/network/DB/owner effects |
| Duplicate/extra/missing keys, wrong scalar type, bad UUID/ref, invalid UTF-8, depth/byte overflow or nonfinite value | Parsing is attempted | Stable safe rejection before effects; no payload/credential diagnostic |
| Copied references or incomplete/mismatched owner records | Admission is attempted | No write; unsupported live verification cannot become synthetic success |
| Another authorized preparer proposes reuse of the original initial bundle | Admission/checks run | Conflict without changing original attribution or any row |
| Pooler endpoint or a backend identity without session-preserving target proof | Target validation/admission runs | Reject before writes; no PID-only pooler recovery claim |
| Actual target/session differs or role was assumed | Child reaches SQL | Refuse; preserve only safe failure references |
| Empty dormant head and trusted fixture admission | Initial preparation/reuse executes | Exact atomic disabled bundle and real attribution/session evidence; native profile/corpus/history preserved |
| Connect, lock, owner lookup, source check, COMMIT or pipe stalls, or unbounded child stderr output | Deadline expires | No fresh budget; bounded cleanup, truthful unknown and no automatic retry |
| Commit succeeds but reply is lost, forged or oversized | Parent completes | Unknown; original attempt retained; independently verify backend end before exact reconciliation |
| Child reaped but backend end unverified | Recovery is attempted | Unknown/no new writes; never infer rollback from reap |
| Missing/extra/mixed state, changed revisions or ambiguous no-op | Original session ended and owner observes state under locks | Conflict/unchanged/reuse/committed remain distinct; no repair; fresh profile required |

The first two rows are implemented by the pure app-owned parser and its acceptance
tests; the remaining rows are future executor/admission qualification. Parsing
consumes the existing pure custody validator without authenticating owner records.
Subsequent
supervisor work must close its result wire, durable-attempt capture and actual
fixture admission before implementing SQL effects; live owner integration remains
separate. No scaffold/shared UI/agent context or accepted ADR change is required by
this documentation slice. Studies UX, standalone account creation and separate
Access/KDG/Leave/factory ownership remain unchanged.


## Implemented parser and qualification

From a trusted repository Python import root:

```python
from apps.scribeswell.backend.caller_preparation_input import parse_preparation_request

request = parse_preparation_request(request_bytes)
```

The result is a frozen slotted `PreparationRequest` containing a frozen slotted
`PreparationCustody`. Both suppress payload repr. Preparer and corpus actor are
separate responsibilities; equal UUID declarations are valid syntax, never evidence
of authorization. The existing `migrations/release_profile.py` custody validator
is imported directly through this app's namespace and remains unchanged. The module
uses only the standard library plus that pure contract, and does not modify import
paths. Normal Python code loading is separate from parsing; calls perform no
explicit file/environment/network/database/owner effects.

`tests/test_caller_preparation_input.py` supplies an independent literal wire
fixture; exact success/immutable/error checks; encoding/framing/size/type/object/UUID/
reference/number/duplicate/depth cases; custody-validator/digest agreement; and a
fresh isolated `-I -S` interpreter with explicit trusted repository root, unrelated
working directory and empty environment. Error tests also cover invocation while
the caller handles another exception: the safe error retains no decoder/caller
exception chain. The isolated test blocks runtime-owner
imports, environment reads and explicit I/O after normal module loading.

Run `python -m pytest apps/scribeswell/tests/test_caller_preparation_input.py -q`
with the repository root available. The
[parser delivery record](../../../_bmad-output/implementation-artifacts/spec-scribeswell-preparation-request-parser.md)
records exact observed red/green commands, regression results and review triage.
Final focused qualification passed 207 cases; the affected pure suite passed 394
cases with 11 retained native cases deliberately excluded. Six review findings
were resolved, none deferred. No database/native execution was run for this parser.
This is internal/repository-qualified availability: existing runtime images do not
include the required pure migration module, and consuming runner packaging must
prove its own clean imports. No runtime endpoint, deployment/image, private target
parser, owner admission, deadline supervisor or preparation SQL is provided.
