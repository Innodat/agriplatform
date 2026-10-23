# Controller-history native replay

Status: locally implemented, independently reviewed and verified. The delivery
record holds actual evidence; operational activation gates remain below.

`controller-history-v1` qualifies controlled native replay of already prepared
`scribeswell_0003` with coherent committed controller history. It is a validation
profile, not actor/caller preparation, source auditing, enforcement activation,
importer transition, publication or a production release command.

Use `baseline.preflight_controller_history(connection, expected_actor)` inside an
explicit caller-owned writable `READ COMMITTED` transaction on the actual restricted
migration connection. Reuse the exact current custody dictionary from
[prepared replay](PREPARED_CONTROLLER_PROFILE.md). For native Alembic rehearsal:

```python
config.attributes['scribeswell_validation_profile'] = 'controller-history-v1'
config.attributes['scribeswell_prepared_actor'] = expected_actor
command.upgrade(config, 'head')
```

The existing [migration prerequisites](MIGRATIONS.md) apply. Local custody matching
does not independently verify Identity. All earlier/absent/invalid ledger states
reject. Omission remains strict `dormant`; explicit `prepared-controller-v1` remains
false-enforcement/empty-history only. There is no CLI, environment or host selector
for either native profile. Host integration, externally verified live custody and
production role/writer preparation remain separate gates.

The exact pinned catalogue, restricted migration/operator authority and three
owner-granted nongrantable operator ACL additions are identical to prepared replay.
Every other catalogue field, ACL/default/effective privilege and safety check stays
binding. Principal and three exact-source command authorities must match current
custody; disabled mappings and either enforcement boolean are preserved. No grants,
configuration, history, corpus, sequence or source state is repaired or changed.

Accept empty epoch/history or one complete expected-source history. Generations
start at1 and are contiguous through the current epoch. Each attempt has exactly
one begin/recover origin and at most one seal; recover references its immediate
predecessor, retires it and creates the next generation. Only the highest generation
is current; its attempt, input digest and state match epoch. Closed current attempts
require a seal; retired predecessors may have been sealed before recovery.

Every semantic request passes the existing pinned native grammar and matches its
stored operation/source/input/predecessor. Every result must equal the exact original
compact receipt, including types and transition state. Creation and final-update
actor/time agree with origin/seal/retirement events; epoch attribution agrees with
initial creation and the current final event. Epoch timestamps must be finite.
Historical executor/revision evidence is retained: it need not equal the current
executor after a valid higher-revision rotation. Revisions remain positive, bounded
by corresponding current policy revisions and ordered consistently with commands.
A receipt cannot claim the exact current revision of a disabled principal or command
authority; legitimate older-revision history remains valid while paused.
A historical receipt never authorizes replay under a replacement executor; the
existing command/lookup functions still apply current authority and executor checks.

At most10000 attempts and20000 outcomes are qualified. Bounded cap+1 count probes
reject excess history with `scribeswell_history_limit_exceeded`, without cleanup or
partial success. Validation uses set-based server queries and returns no history
payload to the client. This is an initial rehearsal limit; extending it needs measured
qualification rather than deleting protected records. Committed write-binding debris
rejects. A coherent history is not proof that the scripture matches an artifact or
that externally supplied custody was verified.

Before coordination, reuse safe `pg_catalog,pg_temp` search order and local statement
five-second/lock two-second ceilings, retaining existing shorter nonzero caller bounds.
Acquire migration advisory lock, then the controller's existing `(31003,1)` advisory
lock, then seven `SHARE` table locks in prepared-profile order. The controller lock
prevents an active transition holding attempt writes from waiting on an epoch table
lock held by validation. Existing bound writers can finish, commit and clean bindings
before validation checks them. Ordinary readers remain compatible; configuration/state
writers serialize. Stable owner DDL/cluster-role administration remains an operational
prerequisite. There are no external waits or scripture scans under these locks.

These are per-statement/lock ceilings, not an end-to-end connection, validation or
COMMIT deadline. The native caller owns transaction completion and rollback after
failure. Operational supervisor/host wiring and its transport deadlines remain gated.
Success evidence `scribeswell_validated_profile` appears only after pre/post validation
and successful commit. Reused evidence clears even on invalid/offline/unsupported
attempts. SQL/driver failures expose fixed safe identifiers without raw payloads.
A lost COMMIT acknowledgement requires reconciliation against actual state; it never
proves rollback. Tests distinguish a fault before commit from a real commit followed
by injected acknowledgement loss, and retain durable effects in the latter case.

Qualification is recorded in the [delivery record](../../../_bmad-output/implementation-artifacts/spec-scribeswell-controller-history-profile.md) and
`tests/test_controller_history_profile.py`; run against the disposable fixture in
[MIGRATIONS.md](MIGRATIONS.md#reproduce-local-qualification), sequentially with other
PG suites. Fixture actors, grants and enforcement are synthetic and do not authorize
live preparation. Public reading and standalone account creation are unaffected.
Active/history native replay alone closes neither full ST-38 nor D-1–D-5.

Impact decisions: app documentation/canonical handoff only; no scaffold/shared UI,
agent-context or ADR promotion. Applied revisions/references/source/importer and
Access/KDG, Leave/factory owner boundaries are unchanged. No image build, browser,
provider, production adoption or publication verification is implied.
