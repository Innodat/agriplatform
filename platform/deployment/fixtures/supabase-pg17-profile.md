# Pinned first-create profile authority

Supabase CLI 2.120.0, source commit
[`753520fa7202ed5f8b25883a4c0aa7e5e9ad1fc4`](https://github.com/supabase/cli/tree/753520fa7202ed5f8b25883a4c0aa7e5e9ad1fc4).
All paths below are relative to that commit. This profile is Linux, PostgreSQL17,
empty db.settings, no restore, no OrioleDB, and no Bitbucket filtering.

- `apps/cli/src/command-internal/db-bootstrap/postgres.service.ts`:
  `buildPostgresStartContainerSpec`, `postgresEntrypointScriptPg15`, and
  `postgresSettingsToPostgresConfig` define env order, volume/port, healthcheck
  (10s/2s/3), restart, aliases, and the shell operand.
- `apps/cli/src/command-internal/db-bootstrap/docker-create-args.ts`:
  `buildStartContainerCreateArgs` fixes the exact option order and key-only env.
- `apps/cli/src/command-internal/db-bootstrap/container-lifecycle.ts`:
  `createContainer` appends project, compose-project, workdir labels in that order,
  merges Linux extra hosts, and passes the four env values to the child process.
- `apps/cli/src/command-internal/db-bootstrap/local-container-inputs.ts` supplies
  `host.docker.internal:host-gateway` for Linux.
- `packages/stack/src/Defaults.ts` supplies the public local JWT default.
  The postgres service fixes password `postgres` and host `/var/run/postgresql`;
  config auth.jwt_expiry defaults to 3600 and the generated ENV config does not
  override it. These public synthetic defaults are not user credentials.

[supabase-pg17-bootstrap.txt](supabase-pg17-bootstrap.txt) retains public bytes,
independently assembled from `postgresEntrypointScriptPg15` and the decoded
`START_DB_SCHEMA_SQL`, `START_DB_WEBHOOK_SQL`, `START_DB_SUPABASE_SQL` template
literals in `db-bootstrap/templates/db-{schema,webhook,supabase}.sql.ts`.
The three SQL strings have an added newline between each, followed by `EOF\n`,
the empty-settings header `\n# supabase [db.settings] configuration\n`, another
newline, and final `EOF` without trailing newline. The exec line retains its
space after `/etc/postgresql`. The leading newline is significant.

The resulting UTF-8 bytes are 9642 bytes with source-derived SHA256
`6f995b129657d28b15a97a1c8a957a7c0015a9865880747c25ad00e3b6d7dd86`.
This digest describes fixed public source, never observed runtime input. Runtime
validation compares exact bytes and does not hash rejected SQL/env values.
The actual pinned CLI must independently match this authority during fresh owner
qualification; captured argv never becomes authority and receipts are not repaired.

The private wrapper checks DOCKER_HOST against its workdir's nonexistent socket,
DOCKER_CONFIG against its empty private docker directory, and rejects context/TLS/
certificate/API-version overrides. Other inherited variables are not container env
unless requested with -e; the exact profile allows only its four key-only names.

This qualifies source conformity and custody through refused create only. It does
not qualify bootstrap semantic safety, secret-file delivery, execution continuity,
complete startup, runtime readiness or repository migrations. Nothing executes these
bytes and `dev.py up` remains gated.

## Reproduce the public bytes independently

Run this investigation recipe from the repository root. It downloads immutable public
primary sources into a new temporary directory, assembles a candidate there, and compares
it with the reviewed fixture. It neither writes the repository fixture nor executes its
shell/SQL. The inline Python is an auditable derivation recipe, not a runtime generator.

```bash
profile_sources=$(mktemp -d /tmp/env-profile-source.XXXXXX)
profile_base=https://raw.githubusercontent.com/supabase/cli/753520fa7202ed5f8b25883a4c0aa7e5e9ad1fc4/apps/cli/src/command-internal/db-bootstrap
curl --fail --silent --show-error "$profile_base/postgres.service.ts" -o "$profile_sources/postgres.service.ts"
for part in schema webhook supabase; do
  curl --fail --silent --show-error "$profile_base/templates/db-$part.sql.ts" -o "$profile_sources/$part.ts"
done
python3 - "$profile_sources" <<'PY'
from pathlib import Path
import hashlib
import re
import sys

source = Path(sys.argv[1])
service = (source / 'postgres.service.ts').read_text()
# Review these two source functions against the explicit assembly below.
for name, ending in [('postgresEntrypointScriptPg15', '\n}\n'),
                     ('postgresSettingsToPostgresConfig', '\n}\n')]:
    start = service.index('function ' + name + '(')
    print(service[start:service.index(ending, start) + len(ending)])

parts = []
for name in ['schema', 'webhook', 'supabase']:
    template = (source / (name + '.ts')).read_text()
    literal = template.split(' = `', 1)[1].rsplit('`;', 1)[0]
    assert '${' not in literal  # These pinned public templates have no interpolation.
    # Their only TS escapes are doubled backslashes and escaped backticks.
    assert re.search(r'\\(?![\\`])', re.sub(r'\\[\\`]', '', literal)) is None
    parts.append(re.sub(r'\\([\\`])', lambda match: match[1], literal))

script = ("\ncat <<'EOF' > /etc/postgresql.schema.sql && \\\n"
          "cat <<'EOF' >> /etc/postgresql/postgresql.conf && \\\n"
          "exec docker-entrypoint.sh postgres -D /etc/postgresql \n"
          + '\n'.join(parts)
          + "\nEOF\n\n# supabase [db.settings] configuration\n\nEOF")
raw = script.encode('utf-8')
assert len(raw) == 9642
expected = '6f995b129657d28b15a97a1c8a957a7c0015a9865880747c25ad00e3b6d7dd86'
assert hashlib.sha256(raw).hexdigest() == expected
assert raw == Path('platform/deployment/fixtures/supabase-pg17-bootstrap.txt').read_bytes()
(source / 'candidate.txt').write_bytes(raw)
print(len(raw), expected)
PY
```

This preserves literal template trailing newlines, inserts one additional newline
between each SQL template, retains the exec line's trailing space, and adds no final
newline. A mismatch stops the recipe; never replace authority with CLI-captured input.
Docker TLS activation (`DOCKER_TLS`), default-platform selection and custom HTTP headers
are also forbidden even when empty, alongside the routing overrides listed above.
