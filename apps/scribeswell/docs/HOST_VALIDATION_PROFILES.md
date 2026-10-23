# Controlled host validation profiles

The existing `scribeswell-owned` release job now carries explicit validation
selection through its bounded worker. [Delivery evidence](../../../_bmad-output/implementation-artifacts/spec-scribeswell-host-validation-profiles.md)
records tests and review status. This is locally implemented tooling; live actor
verification, database caller preparation, immutable image qualification and target
activation require their own evidence. No roles, grants, actors or enforcement
settings are installed by this job.

## External input contract

Keep `scribeswell-migrations.env` outside version control, mode0600, distinct from
runtime configuration. Its required keys remain `SUPABASE_URL` and
`SCRIBESWELL_MIGRATION_DATABASE_URL`, bound to the approved project/TLS and actual
`scribeswell_migrator` login. The only optional keys are:

| Key | Contract |
|---|---|
| `SCRIBESWELL_MIGRATION_PROFILE` | Absent defaults to `dormant`; explicit `dormant`, `prepared-controller-v1`, or `controller-history-v1` only. Empty/unknown values reject. |
| `SCRIBESWELL_MIGRATION_CUSTODY_JSON` | Required exactly for non-dormant profiles; forbidden for dormant. One-line JSON object, at most4096 UTF-8 bytes; duplicate keys, nonfinite numbers, extra/missing fields and invalid types reject. |

Custody uses the unchanged [prepared contract](PREPARED_CONTROLLER_PROFILE.md):
integer `schema_version:1`, `source_id`, nonnil canonical `executor_actor_id`,
`actor_kind:"service"`, `actor_key`, and `preparation_evidence_ref`. Use independently
verified current owner evidence, never an arbitrary UUID, shell username or browser
claim. Local syntactic validation and hash matching are not Identity verification.
Identity owns durable service actors under ADR-0056 and its controlled
`actor.register_system` contract; this application does not query its tables or
provision a competing actor/access path. No general live verification API is
presumed to exist. Live owner evidence remains an activation prerequisite.

The [prepared profile](PREPARED_CONTROLLER_PROFILE.md) requires exact existing0003,
false enforcement and empty history. The [history profile](CONTROLLER_HISTORY_PROFILE.md)
permits either enforcement value and coherent bounded committed history, including
paused mappings and historical executors, under its existing checks. Both retain
exact custody, catalogue, ACL and restricted-role qualification. Dormant remains the
only adopting/upgrading profile; selection is never inferred from target drift.
Native Alembic CLI still has no environment selector: these environment inputs
belong exclusively to the controlled adapter/host integration. Direct native Config
selection remains supported.

## Evidence and activation

The pure app-owned `migrations/release_profile.py` contract is consumed by build-time
host tooling and the app adapter. It imports no server/runtime implementation and
performs no database or external service calls. It also supplies native custody
parsing behind the original safe error wrapper.

Parent and worker use closed bounded JSON IPC. URL and parsed expected custody
travel over stdin; profile/custody environment keys and PG overrides are removed
from the child environment. Neither raw custody nor database URL is recorded in
release evidence. Safe `requested_validation` and committed `validation` objects
contain only `profile` and `custody_sha256`. The latter is null for dormant or SHA256
of custody encoded with sorted keys, compact separators and ASCII JSON escaping.
The accepted wire-size ceilings are checked around decoding. The inherited parent
`communicate()` still buffers stdout before checking its4096-byte ceiling; this is
not a hard peak-memory bound. Current worker replies use fixed small validated
shapes. The [existing deferred-work tracker](../../../_bmad-output/implementation-artifacts/deferred-work.md)
records separate supervisor transport work for a hard buffering cap.

The native migration clears old profile evidence and sets its validated-profile
marker only after preflight, replay/postcheck and successful COMMIT acknowledgement.
The worker requires that marker and exact head before producing success. The
parent requires matching selected profile/digest and before/after revisions.
Non-dormant before and after must both be `scribeswell_0003`.

Host activation additionally requires exact selected/requested/validated evidence,
boolean complete=true, one succeeded Scribeswell owner, valid revisions, successful
job exit and owned network cleanup. Revision-only evidence from an old image now
rejects even for dormant. Build/review compatible host and migration image together;
refresh compatibility evidence. The existing fingerprint includes the whole
migration contract, adapter/image inputs and host coordinator source. The existing
migrations-directory Docker COPY includes the pure helper; a Dockerfile is not
evidence that an image was built or deployed.

## Bounds and recovery

The parent retains the180s workflow budget with reserved termination time and
kill/reap handling. Native statement/lock ceilings remain unchanged. Timeout means
unknown, not rollback; failed acknowledgement may follow a real commit. Safe
known-before is retained when available; no failure gets a validated marker. Host
retains safe selected failure fields, discards arbitrary/malformed child payloads,
preserves earlier group results and blocks activation. Never reverse, stamp or
normalize a target to bypass a failure. Host preflight captures validated migration
inputs once, including project/role credentials and selected profile. It writes
create-only mode0600 snapshots in an owned mode0700 temporary state directory;
Docker and validation comparison use those same captured values. Later changes to
the source env file cannot change this attempt. Snapshots are removed before
activation and on failure, never retained in release evidence. Duplicate keys reject.
Keep owner DDL/role administration and runtime configuration stable during release.

Reconcile actual catalogue, ledger, custody and history through owner tooling,
then perform an explicitly selected replay in a fresh release/evidence directory.
Keep prior images/configuration and verify compatibility before recovery activation.
Do not overwrite old evidence or automatically switch profiles after rejection.

Tests use synthetic custody and an exclusively owned disposable PG17 fixture.
Host qualification uses its actual coordinator with Docker/activation calls replaced
by a harness and real supervised worker/database replay. It does not constitute a
Docker image run, production release or live Identity proof. Coordinated importer/
writer adoption, sealed full audit, publication and coherent reader proof remain
separate gates, as do private Studies and standalone signup provider activation.
