# PtS on local Supabase

The local environment was prepared and tested on 2026-09-24. PtS uses this
repository's Supabase database, Auth and private Storage. The separate disposable
PostgreSQL verification containers are stopped and are not part of this setup.

## Open and sign in

1. Open the local mailbox at **http://localhost:54324**.
2. Open the newest sign-in email addressed to **pts-reader@local.test** and click
   its sign-in link. It opens **http://localhost:5179**.
3. The header shows **PtS → Swahili Poetry**. This test reader belongs to the
   **PtS Local Testing** organization and has explicit read, export and document
   permissions. It is not a platform administrator.

Mail is captured locally; nothing is delivered to an external mailbox. Links are
single-use. If the link has expired or was already used, run from the repository root:

```bash
apps/pts/.local/venv/bin/python apps/pts/.local/login.py
```

Use the newest email. The Microsoft sign-in button needs a configured Entra
provider; for this local setup use the mailbox link instead. Both paths use
Supabase Auth and the same backend permission checks.

## Things to try

- The default list reports **190 of 312 records**. Choose **All catalogue records**
  for 312, **Checked transcriptions (complete)** for 33, and **Needs text review**
  for 157. Checked does not imply human verification or rights clearance.
- Search for a title, poet, place, form or dialect; combine source, genre, origin,
  dialect and text-status filters. Reset filters to return to the default list.
- Open a poem: its text comes first. Expand provenance, witnesses and source
  rights. Copy with citation, follow its direct link, and export filtered JSON/text.
- Open a stored source document from the evidence panel. Private links expire
  after five minutes; open the document again to obtain a new link.
- Narrow the browser to a phone width and use **Filters → Apply filters**.
- Open the reader in an incognito window: poems are not available until sign-in.

Supabase Studio is at **http://localhost:54323**. API documentation is at
**http://localhost:8010/docs**; protected calls require the reader's bearer token
and organization header. Studio is an administrative development tool, not the
reader's permission boundary.

## Stop and restart this prepared workstation

Run from `/home/ck/repos/innodat/agriplatform` in WSL:

```bash
# Stop PtS's five local processes; Supabase and its data remain running.
apps/pts/.local/venv/bin/python apps/pts/.local/stop.py

# Optional: stop Supabase, retaining its local database and storage volumes.
npx supabase stop

# Restart Supabase and then the reader/API processes.
npx supabase start
apps/pts/.local/venv/bin/python apps/pts/.local/start.py

# Request a fresh local sign-in email.
apps/pts/.local/venv/bin/python apps/pts/.local/login.py
```

The starter refuses occupied application ports rather than starting duplicates.
The processes are PtS API 8010, current-access API 8011, content API 8012,
app-directory 8001 and Vite reader 5179. Their logs are in `apps/pts/.local/*.log`.
Do not use `supabase db reset` or `supabase stop --no-backup` for normal restart.

`apps/pts/.local/` contains this workstation's generated launch helpers, Python
environment, local credentials and process state. It is private and git-ignored;
`web/.env.local` contains only public browser configuration. Each API receives its
own environment and restricted database role. The launcher does not run migrations.
These generated files are not distributed with a fresh checkout. Follow the main
README's explicit provisioning steps for a different workstation or database.

## Local configuration and verification

- `supabase/config.toml`: analytics disabled, Storage ceiling 128 MiB, PtS callback
  allowed. Analytics supplies the local Studio log viewer; it is not required by
  PtS database/Auth/Storage. Ordinary Docker/application logs remain available.
- Existing local Supabase data was retained. New PtS/access/content schemas use
  coordinated Alembic migrations. No cloud project was changed.
- All 312 canonical poems, 275 witnesses, 19 sources, 19 rights records and 30
  document references were compared with `library.json` in the database. The ten
  declared stored documents were uploaded privately and downloaded with matching
  SHA-256 hashes, including the 89,237,181-byte PDF.
- Repeating catalogue import returned `replayed: true`, zero insertions and zero
  conflicts. Repeating source uploads reused the ten ready document identities.
- Real Supabase sign-in, directory organization/PtS navigation, browser reading,
  checked filter and mobile rendering passed. Counts are 312/190/33/157.
- Anonymous collection/export/document access and other-organization access were
  denied. Unsigned document URLs were denied. Tampered sessions were rejected.
  A previously valid signed document URL was rejected after expiry with Supabase
  S3 `ExpiredToken` (HTTP 400).
- Local testing exposed ES256 sessions being treated as anonymous by the legacy
  directory verifier. The owning scaffold and directory copy now verify current
  sessions through configured Supabase Auth, while retaining HS256 compatibility.

Before production, provision the intended users and organization, configure Entra
and production URLs, and review source reuse restrictions. Production migration
and public deployment remain separate approval steps.
