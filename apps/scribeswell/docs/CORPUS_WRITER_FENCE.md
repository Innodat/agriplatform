# Dormant corpus writer fence

Revision `scribeswell_0002` adds a transaction-bound fence foundation to the owned
migration history. It ships with enforcement false, no epoch rows and no ordinary
execution grant for the binding routine. Existing corpus readers, importer,
sequences and grants retain their behavior. This is infrastructure for a later
coordinated writer transition; it establishes no ready publication or current
highlight evidence.

## Structures and ownership

All objects belong to `scribeswell_migrator` in the Scribeswell schema:

- `corpus_fence_control` is a private singleton deployment control. Its false
  initial value is technical release configuration, attributed through operational
  migration/release evidence under platform ADR-0025 and ADR-0056.
- `corpus_epoch` is an initially empty single-corpus gate. Its protected tuple
  identifies source, positive generation, nonnil attempt and approved artifact
  checksum, with an updating or closed state. Business rows require creation/update
  actor UUIDs and server UTC timestamps. This delivery creates no such production
  rows and supplies no actor-registration or begin/recovery command.
- `corpus_write_binding` is transient transaction coordination. It ties the exact
  epoch tuple to actual session login, backend PID and full PostgreSQL `xid8`.
  It is explicitly exempt from business actor columns. Deferred transaction-end
  cleanup and rollback leave no committed binding rows.

Runtime, importer, browser/Auth and legacy service roles cannot read or mutate
these structures or call their routines in the shipped state. Trigger invocation
uses the reviewed owner routines; it does not grant callers their privileges.
The binding routine remains owner-only until a separately qualified transition
deliberately changes its caller policy.

## Transaction protocol under synthetic enforcement

The acceptance fixture alone seeds synthetic attributed epoch rows, temporarily
grants the restricted import login execution of
`scribeswell.bind_corpus_write(text,bigint,uuid,text)`, and enables enforcement.
These fixture changes are not production provisioning or supported activation
commands.

The binder checks the exact source/generation/attempt/checksum tuple against the
current updating gate, using the actual `scribeswell_import` session login and
current backend/full transaction ID. Caller-set GUCs and copied IDs grant no
authority. Binding in one transaction cannot authorize another transaction,
including reuse of the same pooled connection. The checksum identifies the
declared approved artifact; the binder does not establish correspondence between
that artifact's bytes and every database row. A later full independent audit must
establish that correspondence.

`guard_corpus_write()` runs before statements affecting any of the five corpus
tables: book, chapter, verse, word and morpheme. INSERT, UPDATE, DELETE and TRUNCATE
share the same boundary, including COPY, upsert and zero-row statements. Existing
table privileges still apply; a binding grants no new DELETE/TRUNCATE authority.
PostgreSQL also rejects COPY FROM on the existing RLS-protected tables before
guard execution. Tests preserve that shipped denial and separately exercise the
underlying COPY guard with a temporary fixture-only RLS adjustment. Production
RLS is unchanged; a valid binding does not make that COPY path supported.
Fence and cleanup triggers use ENABLE ALWAYS; ordinary callers cannot use a
replication setting to skip them. Trigger state is included in head qualification.

Every guard retains a FOR SHARE lock on the deployment control even while disabled.
An enforcement change therefore waits for already-executing dormant transactions.
When enabled, a write also needs the protected binding and a matching updating
epoch held FOR SHARE until transaction end. A generation/state change waits for
that transaction; after it commits, a new transaction needs fresh matching context.
FOR KEY SHARE would not serialize non-key generation changes. Lock order is
control, then epoch. Missing control/epoch, closed/stale generation, wrong login
or absent/forged context denies safely with a fixed error.

`cleanup_corpus_write_binding()` removes transaction context at deferred completion.
Forcing deferred constraints early can remove a binding and cause later writes to
fail; it cannot create authority. Ordinary roles cannot disable the guards or
assume their owner. Trusted owner/schema administration remains subject to the
stable release window; this is not protection against an administrator replacing
the schema.

No database lock spans source-file parsing, network work or a complete import.
The future importer transition must bind book seeding as well as every existing
short chapter transaction. Existing chapter rollback boundaries remain required.

## Migration and qualification

Use the existing bounded migration image and host coordinator described in
[MIGRATIONS.md](MIGRATIONS.md). The history verifies the exact starting revision
and catalogue, applies the expansion transactionally, then verifies the exact
dormant head and owner-only ledger. Replay rechecks structure and dormant state.
Routine signatures, bodies, owner, security mode, search path and ACLs are part
of the reference alongside constraints and trigger presence/enabled state.

The original `scribeswell_0001` reference and legacy SQL/bootstrap pins remain
unchanged. The head reference is built independently from those pinned inputs and
the actual new expansion DDL in a fresh guarded PostgreSQL 17 fixture. Never
snapshot a target and replace the reference to bless drift. Keep the compatibility
input list current if the migration image gains further behavior dependencies.

Generate to separate fresh paths in the guarded disposable fixture to compare
both profiles without replacing checked-in assets:

```sh
reference_directory=$(mktemp -d)
python apps/scribeswell/migrations/generate_reference.py --output "$reference_directory/legacy.json"
python apps/scribeswell/migrations/generate_reference.py --head --output "$reference_directory/head.json"
cmp apps/scribeswell/migrations/reference.json "$reference_directory/legacy.json"
cmp apps/scribeswell/migrations/reference-head.json "$reference_directory/head.json"
```

The initial direct-role bootstrap is not the forward migration mechanism. This
delivery adds no importer EXECUTE grant that would conflict with its current
SECURITY DEFINER whitelist. Future activation must coordinate that authority
transition explicitly instead of bypassing bootstrap checks or rewriting old SQL.

Run the focused PostgreSQL acceptance and full application suite sequentially
against the dedicated disposable fixture using the Python environment described
in [MIGRATIONS.md](MIGRATIONS.md):

```sh
python -m pytest apps/scribeswell/tests/test_corpus_writer_fence.py -q
python -m pytest apps/scribeswell/tests/test_owned_migrations.py -q
python -m pytest apps/scribeswell/tests -q
```

The BMAD delivery record contains exact test commands/results and review triage.
Fixture enforcement tests qualify guard behavior, not a production transition.
No migration image build, live target preparation/adoption or activation is implied.

## Remaining release gates

Before real enforcement, close verified actor/executor binding through the Identity
owner contract, explicit attempt/recovery commands, artifact qualification and the
book/chapter importer transition. Inventory and coordinate every old writer,
including direct SQL/service-role paths. Extend the revision-aware validator and
runner to support the approved operational states; do not manually flip this
dormant profile in production.

Sealing must stop further writes before a full audit without retaining business
locks across the audit. A later activation command must recheck that same sealed
generation and atomically publish its complete manifest/outcome. None of those
commands, source revisions, ready-reader API fields or private Studies writes is
implemented here. Access enrollment stays with its separate owner session.

Migration failure blocks release activation. Preserve safe per-owner evidence and
reconcile uncertain outcomes before retrying; no automatic downgrade or reversal.
Previous reader/importer compatibility and controlled recovery must be rehearsed
on the approved target before release.
