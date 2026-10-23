# Corpus caller preparation and evidence handoff

Status: **specified preparation contract; no live preparation performed**. The
[delivery record](../../../_bmad-output/implementation-artifacts/spec-scribeswell-caller-custody-handoff.md)
records document checks and review. The [host profile integration](HOST_VALIDATION_PROFILES.md)
is implemented and fixture-qualified; that evidence does not verify a live actor,
prepare a database login or authorize production execution.

## What must be connected

An **actor** is the durable name attached to an action's history. A **database
login** authenticates a connection. **Authority** determines which actions that
connection may perform now. These are three different facts. A service actor needs
no Auth account, person, employment, organization membership or application grant.
A **UUID** is a stable unique identifier, not a password. **Provenance** records how
an identity or observation was established. A **revision** is a row's change counter:
an update checks the old number before writing the next one.

**Custody** here means the retained, trusted evidence connecting those facts to
the intended targets and preparation. A UUID, file path, checksum, supplied actor
key or copied receipt is not proof of who produced it or where it was checked.
The **handoff** is the evidence one owner provides so the next owner can perform
its own checks without accessing the first owner's tables.

| Owner | Establishes | Does not establish |
|---|---|---|
| Identity owner | Stable actor UUID, kind `service`, actor key, creation/registration provenance and authoritative Identity target | Scribeswell database login privileges or corpus command authority |
| Scribeswell preparation owner | Actual restricted operator login, exact local principal/command mappings, preparation attribution and source scope | Actor identity by copying a UUID into a local row |
| Release owner | Approved target/image/source binding and selected prepared/history profile; successful committed validation evidence | Actor provisioning, an importer transition or publication readiness |

The same person may carry several operational responsibilities, but the evidence
must retain which owner established each fact. Follow
[ADR-0056](../../../platform/docs/architecture/decisions/0056-durable-actor-registry-separate-from-login-accounts.md),
[ADR-0025](../../../platform/docs/architecture/decisions/0025-record-attribution-and-audit-provenance.md)
and the existing [controller custody rules](CORPUS_CONTROLLER.md#transactions-retries-and-custody).

## Required retained preparation record

This is an operational handoff record, **not a new JSON wire format, signature
scheme, HTTP endpoint or executable verifier**. Keep its complete evidence in the
owners' approved access-controlled storage. An authorized preparer must retrieve
the owner-produced evidence through that channel and check its binding; accepting
a caller-supplied file or matching two self-declared hashes is insufficient.

| Required fact | Evidence and ordering |
|---|---|
| Preparation identity | Stable preparation reference, preparation window/run identifier, UTC verification time and responsible owner/custodian. The reference must resolve to retained evidence, not a transient shell path. |
| Authoritative Identity target | Explicit environment/project/database identity, actual owner execution/inspection login and owner-qualified migration/source revision. Bind the observation to the target actually contacted; a URL in a document alone is insufficient. |
| Stable service identity | Exact nonnil canonical actor UUID, kind `service`, stable actor key and creation attribution/provenance. Preserve the established identity across runs; never infer it from an account, shell user or display label. |
| Registration provenance | Owner-retained complete validated registration command and original operation identity, its acknowledged committed receipt, target/source/executor binding and linked event when created; alternatively, owner-controlled inspection with equivalent exact identity and creation evidence. An unchanged registration may have no new event: retain the existing creation provenance too. |
| Scribeswell target | Explicit approved environment/project/database, actual `scribeswell_migrator` preparation/validation role and actual `scribeswell_corpus_operator` login. Record how authoritative Identity evidence is paired with this target; cross-environment or unestablished pairings stop. |
| Local scope and permissions | Exact source ID, principal actor tuple/evidence reference, three command authorities, enabled flags/revisions, local preparation executor attribution, and privilege/profile observations. Retain original state for recovery. |
| Preparation execution binding | Owner-retained evidence linking the independently verified preparer actor to the actual database session/login, Scribeswell target and preparation run. A nonnil attribution UUID or an actor-existence check alone does not prove who performed the writes. |
| Release binding | Before execution: exact reviewed source commit, compatible immutable image identity and approved selected profile. After local preparation and replay: resulting committed host validation evidence. Actual image/target rehearsal remains required before activation; a checked-in Dockerfile is insufficient. |

Establish Identity provenance and target pairing before local preparation effects.
Retain later observations against the same durable preparation reference as each
ordered step completes; do not overwrite earlier owner evidence. An incomplete
record does not establish completed readiness. Host validation evidence is produced
after local preparation, not used as an impossible prerequisite for those writes.

Do not put credentials, connection URLs containing passwords, raw command payloads
or owner evidence dumps in operational logs or public release evidence. Use safe
references and the existing profile/custody digest there. Keep sensitive retained
commands accessible only through the owning evidence channel under
[ADR-0023](../../../platform/docs/architecture/decisions/0023-structured-operational-logs-and-sensitive-data.md).

## Consume the existing Identity contract

Identity implements protected `actor.register_system` and original-operation
recovery; see [its registration contract](../../../services/access/IDENTITY-MIGRATIONS.md#protected-actor-registration-and-recovery-identity_0006).
The strict command includes actor UUID, kind, key, display name and
`expected_absent:true`. Execution can create a missing actor or return an identical
existing registration unchanged. **Do not run registration as a read-only
verification command.** Creation requires its separately authorized owner operation.

The compact result supplies actor UUID, created/unchanged disposition, optional
event ID, versions and commit timestamp. It does not return the actor kind/key,
original command fingerprint or target binding. Thus a detached receipt is
insufficient: the Identity owner must retain and establish the complete provenance
above. The owner preparation precedent is
[Identity verification before local mapping](../../../services/access/APPLICATION-REGISTER.md).
Its synthetic bootstrap SQL is not a live Scribeswell provisioning instruction.

The [implemented Identity target CLI](../../../services/access/IDENTITY-MIGRATIONS.md#explicit-disposable-identity-operator-target)
supports the checked-in KDG disposable target and `idop_<run>` databases. It cannot
verify an arbitrary live Scribeswell target. No general live verification API is
assumed. Scribeswell must not import Identity's server/adapter implementation or
query Identity tables; the Identity owner performs its own inspection/registration.
Any future runtime integration must use an explicit owner-supported contract.

If registration acknowledgement is lost, retain the original operation and complete
command. The same authorized owner executor uses original-operation recovery under
current authority. Missing outcome is unresolved, not rollback. Do not invent a new
operation or actor to escape uncertainty. Conflicting identity, unverified target,
unavailable evidence or unsupported receipt verification stops preparation.

## Ordered Scribeswell preparation

1. **Bind the reviewed targets and owner evidence first.** Select existing verified
   service identity or separately authorize its owner-controlled registration. The
   concrete target plan must record execution bounds, ownership/privilege inventory,
   previous-version compatibility and recovery before live work. No live target or
   authority is selected by this document.
2. **Verify Identity evidence outside local write locks.** New or restarted preparation
   windows re-establish owner provenance and target pairing. Arrange a stable owner
   DDL/role window through preparation and release qualification. This is not a
   distributed transaction or an automatic perpetual permission token; do not hold
   Scribeswell business locks while waiting for Identity or another external owner.
3. **Prepare the restricted login through the approved owner/secret channel.** The
   real session/current login must be `scribeswell_corpus_operator`, with no elevated
   role, membership, ownership or cross-owner authority. The exact admitted ACL
   overlay is schema USAGE plus EXECUTE on the execute/lookup entry functions, all
   owner-granted and nongrantable. Consume the full
   [prepared profile](PREPARED_CONTROLLER_PROFILE.md), including effective PUBLIC
   permissions and role checks; this paragraph is not a substitute SQL validator.
4. **Write local mappings with real preparation attribution.** Map that login to the
   verified UUID/kind/key and retained preparation reference; scope exactly three
   authorities to the selected source: `corpus.begin`, `corpus.recover`, `corpus.seal`.
   New preparation starts with principal/authorities disabled and enforcement false.
   Apply the transaction and revision rules below; timestamps are server-managed,
   while revisions are supplied explicitly. Attribute the
   preparation to its actual independently verified executing actor, which need not
   be the corpus actor being prepared; never self-attribute merely for convenience.
   Do not add synthetic human initiator evidence. Existing valid records/disabled
   states/history are inspected and preserved, never normalized to fit this sequence.
5. **Qualify the selected profile through controlled release tooling.** Newly prepared
   empty-history `scribeswell_0003` uses explicit `prepared-controller-v1`. Existing coherent
   history uses explicit `controller-history-v1` with current custody. Both consume
   the unchanged six-field expectation below, and require committed host evidence.
   Never downgrade to dormant or infer a profile from target drift to bypass rejection.
6. **Stop at readiness.** Passing these checks does not enable commands or fencing,
   grant importer write binding, import text, seal an audit or publish a revision.
   Enabling execution belongs to the separately coordinated writer/importer transition
   and its actual target compatibility/recovery proof under
   [ADR-0020](../../../platform/docs/architecture/decisions/0020-safe-schema-changes-and-release-recovery.md).

The local principal and all three authorities are one short caller-owned writable
READ COMMITTED transaction, not four autocommit statements. After external evidence
verification, acquire the existing owned-migration advisory lock, then lock
`corpus_operator_principal` and `corpus_operator_authority` in that order with
SHARE ROW EXCLUSIVE table locks. Read and retain the whole before-state only after
those locks; refuse unexpected, partial or conflicting configuration before writes.
Use bounded cardinality probes (at most two principal/four authority rows); any
extra rows reject instead of producing an unbounded configuration dump.
Use the existing migration lock identity from `baseline.py`; do not acquire the
controller transition advisory lock while modifying principal/authority records.
This preserves command lock ordering rather than waiting for Identity under locks.
Keep all four row writes and post-write state checks in that transaction; any
failure rolls them all back. Earlier role/secret/grant preparation is a separate
owner operation whose effects may remain and need explicit reconciliation.

Supply revision `1` for each newly inserted row. Existing rows are never reset to `1`.
For any separately authorized mutable update, match the observed prior revision,
require exactly one affected row, and supply prior+1 within bigint bounds; a stale
revision or overflow rolls back the transaction. Leave exact no-op reuse untouched.
The database requires a strictly higher revision but does not allocate one. Preserve
creation attribution and supply the real verified preparation executor for update
attribution; the server supplies timestamps. The owner execution record must bind
that actor to the actual session/run, not a payload/GUC/shell-user assertion.
For inserts, supply that same actual preparer in both creation/update actor fields;
the current trigger does not derive those actor IDs for the owner.

The concrete executor must bound transaction/lock/statement waits and commit
acknowledgement in its approved target plan. Concurrency, failed-write rollback,
lost acknowledgement and actual session attribution remain required rehearsal
proof; these instructions do not claim an implemented preparation runner.

| Existing custody field | Required source |
|---|---|
| `schema_version` | Integer `1`, unchanged |
| `source_id` | Exact approved Scribeswell source scope |
| `executor_actor_id` | Canonical stable service UUID established by Identity owner evidence |
| `actor_kind` | Literal `service`, independently established |
| `actor_key` | Exact stable key established by the Identity owner |
| `preparation_evidence_ref` | Safe durable reference resolving to the complete owner/preparation record above |

The [existing host input contract](HOST_VALIDATION_PROFILES.md) owns field bounds,
strict JSON, profile selection and digest computation. Its parser validates syntax;
its database checker matches local protected state. Neither authenticates this
external record, fetches owner evidence or makes a local file trustworthy.

## Changes and recovery

Disable/revoke through protected current-authority configuration; actor retention
alone never restores command access. Keep current revision checks on execution,
replay and lookup. Owned0003 makes principal login, kind, actor key and preparation
reference immutable, and permits only the fixed operator login. An ordinary update
cannot replace that key/reference. Identity also retains unique established actor
keys: a new service UUID cannot simply borrow the old actor's key.

Native history fixtures prove UUID-rotation consistency with unchanged local
kind/key/reference; they do not prove a live replacement actor with that tuple
exists. Any replacement must independently satisfy the full owner identity tuple
and local immutable constraints. If it requires a different key/reference, stop:
a separately reviewed forward Scribeswell change and migration/compatibility proof
must authorize it first. Never edit applied0003, disable its guards, reset rows or
reuse an old Identity key to bypass this gate. Retain supplemental owner evidence
without overwriting prior provenance. Use the history profile for existing coherent
history/paused states; never rewrite original executors or operation bytes to make
an old operation run as a replacement.

Any mismatch, owner-evidence outage or uncertain preparation/commit blocks further
preparation or activation. Preserve safe failure references, partial owner outcomes
and prior state. Reconcile actual state with the responsible owners; restart using
fresh evidence and a fresh release directory only after reconciliation. Do not
blindly overwrite a mapping, create another actor, auto-retry a consequential command,
auto-reverse an applied migration or treat missing evidence as permission.

Local mapping writes have **no controller operation ID/outcome lookup**. On lost
local COMMIT acknowledgement, identify the attempt by the retained preparation/run
reference, exact intended four-row writes and protected before-state. First prove
the original database transaction/session has ended and cannot later commit; if
termination is unverified, the outcome stays unknown and further writes stay blocked.
Under a fresh bounded owner transaction and the same serialization locks, compare
the full actual principal/three-authority state, revisions and attribution with both
the intended result and before-state. Exact intended state with provenance supports
committed preparation; unchanged before-state establishes no observed local effect
after the original session is known ended. Partial/mixed/conflicting state stops for
owner investigation, never automatic repair or blind replay. Retain all observations,
then require fresh selected-profile qualification before claiming readiness.

## Required acceptance evidence

These scenarios are **required future preparation/rehearsal evidence**, not passed
live tests. Existing fixtures prove local custody/authority/profile behavior only.

| Given | When | Required result |
|---|---|---|
| Owner-produced full evidence for the paired targets | Restricted local preparation and selected profile replay execute | Exact service identity/login/scope match; source/history unchanged; committed validation recorded |
| Copied receipt/UUID/hash or non-owner-produced record | A preparer attempts to establish custody | Refuse external identity verification; no local mapping/grant change |
| Wrong environment, kind/key, target pairing, missing creation provenance or unsupported verification | Any handoff is consumed | Stop before local effects; retain safe failure reference |
| Identity registration acknowledgement is lost | Same authorized owner recovers the original operation | Preserve original operation/command; no new actor/blind retry; missing outcome remains unresolved |
| Local mapping COMMIT acknowledgement is lost | Owner establishes ended original session and compares intended/before/actual whole state under locks | Exact, unchanged-before, partial/conflicting and unknown cases remain distinct; no nonexistent controller lookup or blind replay; fresh profile required |
| Concurrent local preparers or a failure on any authority insert | The single mapping transaction executes with protected before-state checks | Only one consistent preparation commits; all four writes roll back on failure; earlier role preparation remains separately accounted |
| A supplied preparation actor UUID is valid but lacks actual-session binding | Local writes are proposed | Refuse attribution proof until the owner binds actual executor/session/target/run |
| A real restricted operator login | Direct table/cross-owner/escalation attempts and exact permitted entry calls are tested | Effective forbidden authority denied; authorized calls retain current local checks |
| Paused authority or a proposed replacement actor/key/reference | Validation or owner preparation occurs | Coherent paused history validates without granting access; incompatible replacement blocks pending a reviewed forward change; old operations never rebind |
| Evidence becomes unavailable or preparation restarts | A new window is attempted | Re-establish owner provenance/target pairing before local effects; activation stays blocked |

No owner API, live registration, login/grant installation, image qualification,
enforcement transition or production rehearsal is implemented by this document.
Public reading, standalone account creation and the separate Access/KDG/Leave/factory
work retain their existing requirements and owners.

## Isolated local mapping rehearsal

`tests/test_caller_preparation_rehearsal.py` exercises the local initial-mapping
protocol through a **test-only** helper, `tests/caller_preparation_rehearsal.py`.
It uses actual restricted `scribeswell_migrator` sessions in a newly created,
guarded PostgreSQL17 database. Owner setup creates the operator role and grants
separately. The four mapping rows are written by the migrator together under the
migration lock followed by principal/authority SHARE ROW EXCLUSIVE locks, with
READ COMMITTED, statement/lock/idle-transaction bounds and explicit revision1.
Existing immutable migrations and prepared replay perform their normal checks.

| Local requirement | Executable rehearsal evidence |
|---|---|
| Initial disabled state, server timestamps, explicit distinct preparer, native committed profile and preserved corpus/fence/history | `test_initial_mapping_commits_disabled_and_native_replay_preserves`, `test_mapping_transaction_holds_expected_locks_and_server_timestamps` |
| Exact reuse preserves all row values; real login observations and restricted operator denials | `test_exact_reuse_is_noop_and_records_actual_synthetic_session`, `test_actual_owner_session_required_not_set_role_impersonation` |
| Every insertion failure and postcheck failure rolls back all four rows; separate role/grants remain | `test_failed_insert_rolls_back_whole_bundle`, `test_failed_postcheck_rolls_back` |
| Partial/extra/conflicting rows refuse without repair | `test_unexpected_before_state_refused_without_repair` |
| Actual competing backends block, then reuse the winner or reject a conflict; advisory/principal/authority waits fail bounded | `test_concurrent_preparers_serialize_before_observation`, `test_mapping_lock_timeout_is_bounded_and_no_writes` |
| Real commit followed by injected acknowledgement loss; ended-session committed/unchanged/partial/extra/conflicting observations versus active-session unknown; no retries | `test_lost_acknowledgement_requires_ended_session_and_exact_observation` |
| Unsupported transaction shape including DBAPI autocommit refuses | `test_unsupported_transaction_shape_refused`, `test_dbapi_autocommit_with_logical_transaction_is_refused` |

The run record's actor/session binding is **synthetic and fixture-owned**. It is
not independent Identity verification, an authenticated owner evidence channel or
proof that an arbitrary supplied actor performed a live preparation. There is no
external receipt consumer or production preparation runner. The lost-response
case deliberately throws after an actual successful driver COMMIT; it is not an
induced network outage. Lock/statement/idle bounds are not a proved total execution
or COMMIT acknowledgement deadline. Actual image/host preparation, provenance
retrieval, live target pairing and the complete handoff acceptance matrix above
remain required. The rehearsal does not close live readiness or authorize enablement.

To repeat, use a fresh dedicated local PostgreSQL17 **cluster with all fixture
roles absent**, never a shared development/production database. Set
`SCRIBESWELL_TEST_DATABASE_URL` to that cluster's control database and run with a
Python environment containing the application's migration/backend/test dependencies:

```sh
python -m pytest apps/scribeswell/tests/test_caller_preparation_rehearsal.py -q
```

The existing guarded fixture checks the local host, PostgreSQL17 owner login and
absent roles before creating its random database. It drops that owned database
and its fixture roles afterwards. The harness that creates the cluster must also
remove its exact owned container; the tests do not discover or stop other containers.


## Preparation tool design

The [preparation tool contract](CORPUS_PREPARATION_TOOL.md) specifies a closed
request, separate trusted owner admission and private target, proposed total/COMMIT
deadlines and original-session reconciliation. It is a written design, not an
implemented parser or runner. The first implementation boundary is pure parsing;
owner evidence verification, supervised SQL execution and live readiness remain open.
