# PostgreSQL synthetic create-to-start authority

Supabase CLI 2.120.0, source commit
`753520fa7202ed5f8b25883a4c0aa7e5e9ad1fc4`:

- `apps/cli/src/command-internal/db-bootstrap/container-lifecycle.ts`:
  `create` returns the identifier used by `docker cp - <identifier>:/`, then `start`.
- `apps/cli/src/command-internal/db-bootstrap/postgres.service.ts`:
  one secret file `/etc/postgresql-custom/pgsodium_root.key`.
- `apps/cli/src/shared/functions/functions-docker.ts`:
  `containerArchiveBytes` strips leading slashes and uses `Bun.Archive`; the source
  and adjacent tests specify a regular file with mode 0644.
- `packages/stack/src/Defaults.ts`: `DEFAULT_POSTGRES_ROOT_KEY` is the public local
  default compared in memory by `startup_lifecycle.py`. Runtime transfer bytes
  never become source authority, a saved artifact, a hash, or output.

The fixture validates a bounded uncompressed USTAR member without extracting it.
The synthetic identifier consists of 64 `e` characters and has no daemon authority.
The one-second stdin deadline is inside the existing five-second wrapper deadline;
archive input is exactly 10240 bytes. Characterization of the previously qualified
pinned native executable outside the restricted sandbox observed: one USTAR header
(`ustar` plus NUL, version 00), type ASCII 0, uid/gid 0, empty user/group/link/prefix
fields, 64 bytes matching the public default, 448 zero member-padding bytes, and 9216 zero bytes after the padded data block. Header
mtime varies; it is validated as an octal field rather than used as authority.
The sandbox-only attempt delivered empty stdin and is not acceptance evidence.
No transfer bytes were saved. Independent Python tar fixtures verify validation
and rejection behavior. Fresh public qualification remains required after source
changes; characterization does not qualify the complete lifecycle.

Intentionally supported numeric fields contain octal digits with optional leading
spaces and optional trailing NUL/space padding. Digits after a terminator, leading
NULs, signs, base-256 encoding and non-octal bytes are refused. Device fields permit
either all NULs or an explicit octal zero in that format. Only the observed ASCII
`0` regular-file type is accepted; the legacy NUL type is refused. These rules
avoid interpreting a field differently from standard tar readers. No header time
value is used as authority; the entire supported octal range remains accepted.

## Fresh branch admission and synthetic acknowledgement

The same pinned commit's
`apps/cli/src/command-internal/db-bootstrap/start-database.ts` records
`volumeExists` before creation (line134) and selects fresh setup from that original
observation (line189). `container-lifecycle.ts` orders ensure-volume, container
create, root-key copy and start. Pre-acquiring the database volume selects the
existing-volume branch even if acquisition just created it.

The guarded `resources.invocation` therefore requires exact missing-volume404
before bridge mutation and again after image/bridge reobservation. It never creates
the volume. Existing or ambiguous metadata refuses; absence is a bounded observation,
not a reservation. Metadata acquisition remains a separate supported operation.

The private `fresh-lifecycle-positive` fixture stores `planned_volume` separately
from observed metadata and refuses supplied pre-acquired volume input. Its initial
probe truthfully returns missing. Only the exact project name and two pinned CLI
labels, after the full missing/image/network prefix, receive a synthetic create
acknowledgement. Immutable PostgreSQL request validation, in-memory root-key copy
and refused first start follow in that strict order. Duplicate, wrong or reordered
create/copy/start operations refuse. Existing and racing fixture volumes refuse
before acknowledgement or PostgreSQL create. Negative lifecycle controls independently
validate the original request and transfer before injecting their defect.

The CLI's two-label volume-create command does not establish the planned ENV
six-label ownership descriptor. The synthetic acknowledgement establishes sequence
only, never real freshness, ownership, initialization or executed setup SQL. Live
creation/ownership enforcement, execution-time rechecks, bootstrap/secret semantics,
initialized reuse and real lifecycle readiness remain open. No runtime bytes, request
body, environment or archive are saved or hashed; `runtime_ready=false` remains.

## Retained guarded CLI volume-owner integration

The separate `guarded-fresh` startup qualifier connects the pinned CLI's actual
missing probe and ensure-volume command to the ENV volume owner. It retains the
qualified run lock/evidence and one Docker connection/version across acquisition,
CLI execution and final joint observations, with the same five-second total daemon
deadline. Standalone fresh and metadata-acquisition qualifiers retain their contracts.

The generated private fixture accepts only the exact pinned two-label CLI command
after independently validating the complete prerequisite sequence. A closed private
handoff asks the parent owner to require absence and send its exact six-label local
volume request once. The owner validates the201 descriptor, reinspects by name and
requires no current container references. Current images and bridge are checked
before that operation and again with the volume/use observations before the CLI
receives acknowledgement. After the strict PostgreSQL create/copy/refused-start
sequence, final joint observations and owner evidence postchecks must still pass
before a proof can return. Subprocess waits run outside the immediate constructor.

The handoff has no daemon endpoint or arbitrary route selector. Its socket is derived
from the generated private workdir; filesystem custody, peer credentials, an in-memory
capability and exact ordered requests are checked. The capability and request bytes
are never saved, hashed or exposed. Malformed, duplicate, forged and repeated
handoffs refuse. Every blocking read/send uses the remaining guard budget; child
output remains bounded and discarded, and the proven process group is stopped on
all exits. Observed ownership fields are reported separately from planned metadata;
daemon timestamps, mountpoints and container details remain private.

The independent synthetic peer requires exactly70 ordered API exchanges on one
connection, including the owner POST and final image/network/volume/use checks.
Controls `guarded-existing`, `guarded-foreign`, `guarded-lost-response`,
`guarded-truncated-response`, `guarded-bad-ack`, `guarded-bad-descriptor`,
`guarded-changed`, `guarded-use`, `guarded-late-image`, `guarded-late-network`,
`guarded-late-volume` and `guarded-late-use` validate exact terminal refusals. Existing
volumes are never adopted by this fresh operation; uncertain mutation has no replay,
cleanup or later phase. A404,201 or matching labels still proves neither immutable
identity, reservation, empty storage nor qualified initialization. All daemon changes
and container acknowledgements remain private synthetic fixtures. Real Docker
mutation, container execution/SQL, bootstrap/secret semantics, initialized reuse and
runtime readiness remain unqualified; `up` stays gated and `runtime_ready=false`.
