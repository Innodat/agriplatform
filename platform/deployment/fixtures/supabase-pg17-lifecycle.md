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
