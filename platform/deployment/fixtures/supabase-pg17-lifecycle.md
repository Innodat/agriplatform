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
