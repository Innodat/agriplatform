# Owned corpus migration history

Owned head `scribeswell_0003` adds the
[dormant transactional controller](CORPUS_CONTROLLER.md) after the
[writer-fence foundation](CORPUS_WRITER_FENCE.md) in `scribeswell_0002`. It verifies
the exact `scribeswell_0001`, `scribeswell_0002` or `scribeswell_0003` starting profile
before upgrading to the dormant head. Enforcement stays
false, routines remain owner-only and epoch/controller tables are empty. The baseline
description below remains the prerequisite for initial adoption.

Scribeswell's owned Alembic baseline adopts an existing, qualified corpus schema.
It does not create or import the corpus. Initial installation still uses the
reviewed legacy schema SQL and direct-role bootstrap; all subsequent Scribeswell
DDL belongs to the owned history. Never add forward changes to the legacy SQL.

The baseline records `scribeswell_0001` only after checking its supported catalogue
and restricted migration authority. The new `scribeswell.alembic_version` is a
technical owner-only ledger. Adoption preserves corpus rows, IDs, sequence state,
reader/importer grants and policies. The adoption baseline itself enables neither
writer enforcement, sealed source evidence nor publication activation. Studies remains gated on those later
contracts and separate Access account enrollment.

## Target preparation and supported profile

Production preparation requires a concrete reviewed target plan under platform
ADR-0016, ADR-0017 and ADR-0020. Local verification does not authorize production
SQL or deployment. Before controlled adoption:

1. Qualify the existing schema against the independently pinned legacy SQL and
   direct-role bootstrap reference. Missing, partial, extra or drifted objects,
   unsupported ACL/default-ACL profiles and malformed/unknown ledger state stop
   adoption. Never regenerate the reference from a target to make it pass.
   The supported reference executes both pinned inputs as fixture `postgres`
   before transferring corpus ownership to `scribeswell_migrator`; original
   bootstrap-owner default ACLs remain. Another bootstrap-owner/profile requires
   explicit qualification rather than automatic normalization.
2. Explicitly provision `scribeswell_migrator` through the approved secret channel.
   It must be the actual login/current role, own the Scribeswell schema and its
   tables/views/sequences, and have no superuser, bypass-RLS, database/role creation,
   replication or unsafe membership authority. Ownership preparation is a separate
   reviewed operation; the migration runner never creates roles or transfers
   ownership. Preserve all legitimate existing consumers and sequence values.
3. Rehearse preparation and adoption on a disposable representative copy. Record
   exact catalogue/profile qualification, original ownership/ACL evidence, previous
   reader/importer compatibility, migration failure and recovery evidence. Review
   existing default privileges explicitly; new ledger privileges must not expose
   it to business roles.
4. Arrange a stable schema window. The migration's advisory lock serializes
   cooperating migration runs, not arbitrary administrator DDL. Keep external
   service waits outside the migration transaction.

## Controlled execution

The existing host release coordinator registers a separate `scribeswell-owned`
migration group. Its nonroot image is built from
`apps/scribeswell/deployment/Migrations.Dockerfile`. Its private
`scribeswell-migrations.env` contains exactly `SUPABASE_URL` and
`SCRIBESWELL_MIGRATION_DATABASE_URL`, using the prepared migration role, matching
Supabase project and explicit TLS. Keep this file outside version control and
separate from `scribeswell.env`; runtime must never receive migration credentials.

Use the existing serialized host release entry point with immutable reviewed
images and fresh bootstrap/compatibility evidence. Registration changes the
migration compatibility fingerprint; refresh evidence after rehearsal. Do not run
adoption independently on API startup or invoke a competing generic coordinator.
The registry names Scribeswell's adapter, migration dependency file and imported
validators as additional compatibility inputs; the host also hashes registered
migration Dockerfiles and owned history/reference files. Keep that input list
current when adding migration-image behavior dependencies.
The app adapter bounds the complete database workflow, including connection and
inspection, and writes safe owner revision evidence to a fresh host-provided
`/evidence/migrations.json`. Existing evidence is preserved, not overwritten.

Native Alembic supplies the adapter's internal invocation and guarded local tests;
production execution uses the bounded adapter through the host coordinator.
Supported execution is upgrade to head, including replay validation.
Stamp, downgrade, offline generation and unrelated commands are rejected. Replay
checks the catalogue again rather than trusting a stored revision alone. Head
replay deliberately requires false enforcement, empty epoch/bindings/controller
tables and shipped owner-only ACLs. Fixture-only controller activity is not an
approved active release profile; operational-state qualification and coordinated
caller/importer transitions remain separate gates.

## Controlled prepared replay

The separate [prepared-controller profile](PREPARED_CONTROLLER_PROFILE.md) qualifies
an already prepared, false-enforcement, empty-history `0003` only through explicit
native Alembic Config attributes or the direct owner checker. It permits exactly the
operator schema USAGE and two entry EXECUTE grants against the original reference,
and matches independently supplied custody against protected local records. It does
not verify Identity, provision callers, adopt earlier revisions or enable enforcement.
The host adapter and ordinary CLI remain dormant-only and reject prepared targets;
there is no ambient environment selector. Native profile evidence is published only
after both checks and commit. The separate history-native profile below extends
local rehearsal; operational host release support remains a later gate.

## Controller-history native replay

The explicit [controller-history profile](CONTROLLER_HISTORY_PROFILE.md) additionally
validates empty or coherent committed history at exact0003, including paused states
and historical executor changes. It preserves the prepared profile's exact custody,
catalogue and privilege gates. Native Config selection remains deliberate; the
ordinary CLI/host stays dormant-only. This qualification changes no enforcement,
actor/grant, importer or publication state. Live custody, operational host integration
and coordinated production transition remain gates.

## Failure and recovery

Any failed or uncertain migration blocks activation. Preserve the host report,
per-owner before/after revisions, command/release identifiers and supervisor
warnings without credentials or raw database exceptions. Earlier owner success
remains applied and recorded if a later group fails.

A rejected adoption rolls back its transaction. A timeout or lost response can
leave outcome uncertain: reconcile current ledger and catalogue with restricted
authority before retrying through a fresh release attempt. Never infer rollback
from an unsuccessful client exit, overwrite the evidence, blindly stamp, or
automatically reverse an applied migration. Keep the previous image/configuration
available and confirm database compatibility before recovery activation.

Production role/ownership preparation, target profile qualification, actual
adoption and release activation remain open until their own recorded execution.
Disposable tests establish implementation evidence only. See the BMAD delivery
record for exact commands and results; no image build or production rehearsal is
implied by checked-in Dockerfile and registration.

## Reproduce local qualification

Create a Python 3.12 virtual environment and install
`apps/scribeswell/deployment/migration-requirements.txt`, the app backend
requirements and `pytest`. Set `SCRIBESWELL_TEST_DATABASE_URL` to a dedicated
disposable localhost PostgreSQL cluster with fixture-administrator authority.
The fixture refuses pre-existing known application roles before mutation, creates
a uniquely named database, and removes only its own database and roles. Run
database suites sequentially against that cluster.

```sh
python -m pytest apps/scribeswell/tests/test_controller_history_profile.py -q
python -m pytest apps/scribeswell/tests/test_prepared_controller_profile.py -q
python -m pytest apps/scribeswell/tests/test_owned_migrations.py -q
python -m pytest apps/scribeswell/tests -q
```

With the same disposable fixture prerequisite, independently generate a reference
to a fresh output path and compare it with the checked-in asset:

```sh
reference_directory=$(mktemp -d)
python apps/scribeswell/migrations/generate_reference.py --output "$reference_directory/reference.json"
cmp apps/scribeswell/migrations/reference.json "$reference_directory/reference.json"
python apps/scribeswell/migrations/generate_reference.py --head --output "$reference_directory/fence.json"
cmp apps/scribeswell/migrations/reference-head.json "$reference_directory/fence.json"
python apps/scribeswell/migrations/generate_reference.py --revision scribeswell_0003 --output "$reference_directory/controller.json"
cmp apps/scribeswell/migrations/reference-controller.json "$reference_directory/controller.json"
```

The default generator executes the pinned legacy SQL/bootstrap inputs in its new
fixture, then performs test-only ownership preparation. With `--head`, it also
applies the reviewed revision `scribeswell_0002` DDL under the prepared owner; that
source and its reference are covered by the release compatibility fingerprint. Historical
`--head` deliberately remains the `scribeswell_0002` reference selector. Explicit
`--revision scribeswell_0003` applies `0002` then `0003` DDL and generates the separate
controller reference; explicit `0001`/`0002` selectors are also supported. Original
reference.json/reference-head.json are immutable revision profiles. It accepts no
existing target as the reference source and refuses existing output. A mismatch requires investigation
and explicit profile qualification; do not replace the reference to dismiss it.
This baseline explicitly requires PostgreSQL 17 and rejects other server major
versions before adoption. The migration
image still requires a separate reviewed build and target rehearsal before release.
