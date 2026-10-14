# Owned WRITE, recovery evidence and KDG secret execution

2026-10-14. Selected planning contract for existing WRITE/environment/security owners
and first consuming KDG stories. No runtime helper, database, secret, migration or
deployment is created. Inherits [Identity/Access substrate](identity-access-execution-substrate.md),
[errors/outcomes](api-errors-and-operation-recovery.md),
[controlled setup](e1-controlled-provisioning-and-evidence.md) and
[KDG fingerprint disposition](operation-fingerprint-security-evolution.md#kdg-initial-fingerprint-disposition--2026-10-14).
KDG command/receipt/prior-eligibility semantics remain app-owned in contracts.md.
Accepted ADRs remain unchanged; no central write/audit/operation service is introduced.

## Concrete outcome variants

One physical table per owning schema, not a cross-owner repository. Immutable outcomes
represent successful local commits only; rejected/failed attempts are safe diagnostics,
never success rows or permanent placeholder actions. Internal ID UUID is distinct from
caller operation_id. All typed fields NOT NULL unless explicitly nullable below.

| Variant | Exact identity/scope columns and uniqueness |
| --- | --- |
| KDG user command: kdg_capture.operation_outcome | id UUID PK; org_id UUID; executor_account_id UUID; executor_actor_id UUID; command_type text; operation_id UUID. UNIQUE(org_id,executor_account_id,command_type,operation_id). No client-supplied owner/org/actor. |
| Owner operator: identity.operation_outcome / access.operation_outcome | id UUID PK; scope_kind text CHECK platform/organization; scope_id UUID nullable only for platform; executor_actor_id UUID; command_type text; operation_id UUID. UNIQUE NULLS NOT DISTINCT(scope_kind,scope_id,executor_actor_id,command_type,operation_id). No fabricated operator account. |

Shared columns: command_version integer>0; fingerprint_version integer>0;
fingerprint_algorithm text CHECK sha256/hmac-sha256; fingerprint_key_id text nullable;
fingerprint bytea exactly32 bytes; result_version integer>0; result jsonb object ≤8192
UTF-8 serialized bytes; committed_at timestamptz server UTC; initiator_actor_id UUID
nullable only when no verified initiator. HMAC requires a valid non-null key ID;
SHA requires key ID null. Unsupported versions/algorithms are retained and blocked,
never interpreted as absent outcomes. All UUIDs nonnil, text excludes NUL, result is
strictly validated command-specific compact acknowledgement, never an arbitrary dict.

KDG capture v1 result is exactly capture_id/revision; command_type/version are in its
outer receipt as already selected. Operator result uses the command-specific target/
disposition/revision/event_id union in the substrate. Committed revision is the original
operation's result even if later state changes. No-op edit has unchanged revision/no
new capture revision; no-op setup has no invented transition event. Outcome returns
only after durable commit; HTTP/parser/timeout failures never prove a rollback.

No automatic outcome expiry/cleanup in first delivery. Later explicit retention must
preserve supported retries/restorable evidence and current domain policy. A generic
notification expiry window does not apply. No payload/answer copy or digest exposed
by receipt lookup. Recovery permissions follow each stored command/resource contract;
query command_type cannot confer permission. Foreign lookup reveals no existence.

Identity outcome/event executor and non-null initiator have local ON DELETE RESTRICT
FKs to identity.actor. Access/KDG actor references remain verified external IDs without
cross-owner FKs. Bootstrap inserts its classified actor before outcome/event rows in
the same transaction; no temporary nonexistent actor.

## Owner-local immutable transition evidence

Identity/Access use business_event, separate from diagnostic logs and outcomes:
event_id UUID PK; event_type text; event_version integer>0; created_at timestamptz;
scope_kind/platform-or-organization and scope_id nullable only platform;
executor_actor_id UUID; initiator_actor_id UUID nullable; outcome_id UUID local FK
RESTRICT; target_key text bounded512 ASCII bytes; target jsonb typed object;
transition jsonb typed allowlisted object;
reason_code text; evidence_ref nullable opaque text. Bound type/reason/ref to200/128/256
ASCII characters and target/transition together to8192 UTF-8 bytes. No update/delete
runtime authority. One outcome may link multiple legitimate transitions; event_type
and stable target_key distinguish them, with unique(outcome_id,event_type,target_key).
Each event model defines target_key as its canonical identifier tuple, never user labels
or a large JSONB index; target object must match that typed identity.

Identity event types v1: identity.actor_registered, identity.account_actor_established,
identity.membership_joined, identity.membership_retired. Target contains their exact
actor/account/member/org identifiers; transition only kind/key or old/new membership/
owner/lifecycle/revision as applicable. No full profile/email/auth verification document.
Access v1: access.application_registered, access.permission_registered,
access.entry_permission_registered, access.application_availability_changed,
access.organization_application_changed, access.grant_changed. Target is exact app/
permission or grant/account/member/org identity; transition is before/after enabled,
scope/binding/revocation and revision only. Register unchanged creates no event.
Actor establishment/rejoin history is real evidence, not derived from current rows.

KDG capture_revision is its already approved app-owned business snapshot: same-org
capture FK, unique(org_id,capture_id,revision), original owner plus actual editor actor/
account, operation identity and server time, exact original questionnaire version and
committed observation date/answers. It contains sensitive business content under KDG
authorization, never copied into generic business_event or logs. Explicit non-noop
create/edit records exactly one committed revision. Questionnaire/child/assignment
history uses owning story-specific events, not a universal whole-row dump.
Leave's ordinary draft-save/read evidence simplification remains unchanged.

KDG revision adds outcome_id and exact command_type/operation_id/executor account/actor.
Its composite local FK binds those values plus org_id to the corresponding outcome;
declare the referenced composite UNIQUE key including id on operation_outcome. The
actual editor matches that outcome executor. Scoped capture FK also binds its immutable
original owner through a corresponding capture UNIQUE key. Local constraints reject
wrong-org/wrong-executor/unrelated-operation history on alternate writes. No-op outcomes
have no new revision. Insert outcome before revision/event FK within the same transaction;
rollback preserves atomicity.

## Short transaction and duplicate execution sequence

1. Strictly validate shape, versions, typed IDs/bounds and caller/service identity.
   Resolve target identifiers from path/payload or a private scoped preliminary outcome
   read, then obtain current Access/operator/resource authority and required external
   observations before business locks. Preliminary metadata is never released before
   authority succeeds. One ten-second server-monotonic execution budget includes waits/
   rechecks; Access call ≤3 seconds, local-start observation gap ≤1 second, lock wait
   ≤2 seconds and SQL statement ≤5 seconds, each capped by remaining budget.
2. Begin owner-local transaction; set verified org/account/actor/read-or-write mode
   transaction-locally. Acquire a transaction advisory lock for the exact outcome key
   before reading outcome or effects, using a stable server SHA-256→signed64-bit lock
   key: first8 SHA-256 bytes interpreted as signed big-endian64 of UTF-8 JCS object
   {lock_version:1,owner_schema,scope_kind,scope_id,caller_kind,caller_id,command_type,
   operation_id}. caller_kind is account for KDG/actor for operator, scope_id null
   only platform; typed UUIDs use normalized wire strings. Keep lock v1 stable across
   supported overlapping releases. A hash collision serializes
   unrelated commands only; the actual unique table key still decides identity.
3. If a committed outcome exists, verify fresh pre-lock authority matches its actual
   stored resource/command and stays within the observation-start bound, then
   compare the original version/algorithm/key-specific fingerprint. Match returns its
   original receipt, mismatch conflicts. Missing verification material fails closed.
   If stored target differs from the checked target, release/rollback without disclosing
   a receipt, perform its exact network check and restart within the original budget.
   No network recheck runs under locks.
4. If absent, lock/update the actual local domain state in deterministic order, validate
   current assignment/member-binding evidence/version/lifecycle and expected revision.
   The outcome-key lock prevents competing identical operations; domain revision and
   structural constraints arbitrate different operations. Never substitute latest revision.
5. Mutate local business state, attribution/revision, required immutable evidence and
   compact outcome in the same transaction. Reserve outcome UUID in memory; outcome row
   may be inserted before its local evidence FK, but all rows become visible together.
   Any validation/constraint/evidence failure rolls back that entire local transaction.
6. Commit, then return acknowledgement. Resolve a lost acknowledgement through the
   original scoped outcome. Another attempt must obtain fresh authority and the same
   immutable payload. Never send external delivery while holding business locks.

Outcome and domain locks are transaction-scoped, never session advisory locks. Missing
RLS context fails closed; commit/rollback clears context; pooled-connection reuse tests
are mandatory. A blocked duplicate uses bounded lock wait: return HTTP409 operation_busy
with truthful uncertainty and original operation identity, not a fresh action. Concurrent
duplicates cannot commit effects twice even if a process crashes; final unique constraint
backs the helper. A genuinely denied/conflicted/invalid action takes its own error path.

## Runtime/operator/migrator privileges and safe errors

KDG uses kdg_capture_runtime, kdg_capture_operator and kdg_capture_migrator, separate
credentials. Runtime has narrow owner-table DML/SELECT and sequence privileges only
where domain writes require them; immutable outcome/revision tables grant INSERT and
authorized SELECT, never UPDATE/DELETE. Database immutability guards reject alternate
writes even through accidental grants. Migrator owns only KDG schema/history; operator
uses trusted owner command wrappers and exact authority mapping, not runtime or DDL.
Identity/Access retain their substrate principals; WRITE grants required local event/
outcome append/read columns to their exact command owners, not browsers/public roles.

All organization domain/outcome/revision tables have ENABLE+FORCE RLS. KDG writes check
fixed verified org; create owner account must equal verified app.account_id; original
owner/child/questionnaire are immutable. Own reads filter original account; online all
reads/edits use a distinct verified all mode established only after exact Access checks.
An HTTP mode/owner/role field cannot establish that context. Current runtime SQL setting
is a trusted backend assertion, not authentication against compromised backend credentials.
Operator global events use explicit platform scope, no nullable-org business shortcut.

Map only identified constraint names: duplicate-operation recovery after full rollback;
revision/lifecycle conflict409; malformed domain structure422; inaccessible foreign ID404
under disclosure policy. Unknown database errors return safe internal_error/trace ID,
preserve uncertain outcome and do not expose SQL/values/exception contexts. Only PostgreSQL
lock timeout in the documented outcome-key wait maps to operation_busy; broad exceptions
must not be relabelled as a retry or validation failure. Framework validation adapters
allowlist paths/error identifiers and strip input/context dumps. Preserve legacy error
families through their explicit adapters; generated OpenAPI/TypeScript stay synchronized.

KDG transport selection: browser mutation wait12 seconds; one automatic unknown-outcome
recovery cycle ≤15 seconds, at most3 scoped lookups and1 identical retry, each request
freshly authorized and deadline bounded. Definitive deny/validation/conflict never enters
that automatic cycle. After exhaustion show truthful pending/attention with manual Retry;
later edits stay behind unresolved predecessors. No autosave/draft recovery is added.

## Exact KDG fingerprint secret/configuration input

Use rfc8785==0.1.4 for JCS bytes; Python3.15 standard-library hmac/hashlib SHA-256 and
compare_digest for keyed fingerprint/constant-time comparison. The selected library
has no runtime dependencies; conformance checks use RFC8785 ordering/Unicode/number
fixtures rather than assuming Python sorted JSON is equivalent. Strict JSON/Pydantic
shape validation rejects duplicate keys, non-finite values, lone surrogates, unknown
fields, NUL and oversized bodies **before** canonicalization. Store typed bigints as
decimal strings. Preserve valid answer strings without Unicode normalization.

Public-safe configuration names: KDG_FINGERPRINT_ACTIVE_KEY_ID,
KDG_FINGERPRINT_SECRET_DIR, DEPLOY_ENV and KDG_OWNER_ID=kdg_capture. No key bytes in
environment strings, frontend builds, command argv, database, image layers or logs.
Production API mount is read-only `/run/secrets/kdg-fingerprints`; each key file is
`<key_id>.json` with exactly schema_version=1, owner_id, environment_id, key_id, key_b64.
Validate existing approved key-id grammar before joining paths; reject symlinks,
nonregular files, unknown fields, namespace mismatch and decoded length≠32 bytes.
Secret files are mode0400, owned by the actual KDG runtime UID10001; directory0700.
The mounted leaf directory is UID/GID10001-owned0700; its files are UID/GID10001-owned0400.
Root controls a separate host ancestor/staging/archive (root-owned0700), prepares the
readable leaf and projects it read-only into the container, where /run/secrets permits
traversal. A root-owned0700 mounted leaf is invalid. Do not weaken permissions to make
an unreadable key pass. Only the KDG container receives this mount; database/migrator/worker/other apps do not.
The root-controlled host staging/archive is never writable by runtime; the projected
leaf is read-only at the mount despite its runtime UID ownership.

Local/CI equivalent is ignored ENV run directory `secrets/fingerprints/<key_id>.json`,
with run-specific synthetic random keys and the same ownership/environment rules.
Missing active key blocks writes/activation; missing old referenced key returns503
operation_verification_unavailable and preserves original receipts. No key generation
on API startup, fallback key, silently reusing another environment or digest rewrite.
Ordinary rotated/old-release keys remain available according to the owning disposition.

Separate protected secret-backup manifest has schema_version=1, owner_id,
environment_id, backup_ref, key_ids, data_backup_ref, created_at, verified_restore_ref.
backup_ref/data_backup_ref/verified_restore_ref are opaque controlled recovery-record identifiers,
not credential-bearing URLs. Store an independently encrypted key archive through the
existing release recovery store with its separate operator-only decryption authority;
database dumps never contain keys or their decryption credentials. ENV/operator may
provision/mount/archive keys; only KDG runtime reads the active/verification files.
Owner-only recovery retrieves the matching secret manifest/archive and data snapshot,
proves old recorded retry/mismatch/wrong-key and current access, then permits activation.
Actual encryption key/backend/archive identity and restore transcript are explicit
release inputs, not an invented installed secret platform or automatic cloud backup.

## Acceptance and delivery boundary

WRITE proves actual role/RLS isolation, alternate-write UPDATE/DELETE/TRUNCATE refusal,
local nonexistent-actor/wrong-outcome linkage rejection, conditional races,
duplicate/new-command keys, no-op, receipt/audit failure rollback, commit/lost response,
timeouts and pool reuse. KDG A09/A14/A16 consume these, plus HMAC/JCS key restart,
overlap/rotation/rollback, missing/wrong-environment key, data+secret restore and log/
artifact leak-exclusion fixtures. Schema/readiness checks cannot substitute for them.
Controlled migrations preserve previous running version/queued payload interpretation,
block activation on failure and provide explicit recovery with no automatic downgrade.

Scaffold promotes proven neutral write/context/error/outcome/evidence/fixture helpers
through existing WRITE/P1/SERVICE, while KDG models/answers/policies remain app-owned.
Shared UI uses existing truthful save/sync/Retry conventions. Agent instructions record
actual owner commands and secret-free diagnostics; existing root rules suffice. Owner
docs/model/OpenAPI/runbooks stay authority during Build; ADRs are referenced, not edited.
No new worker/outbox, key service, audit server or generic offline runtime is required.
Real-data processing/device/retention policies remain 5.4 pre-pilot gates. This planning
selection does not authorize secrets, migrations, code, infrastructure or deployment.
