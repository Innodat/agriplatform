# PtS on local Supabase

The local environment was prepared and tested on 2026-09-24. PtS uses this
repository's Supabase database, Auth and private Storage. The separate disposable
PostgreSQL verification containers are stopped and are not part of this setup.

## Open and sign in

1. Open **http://localhost:5179** and sign in with an account created in local Supabase.
2. To choose a password for the prepared **pts-reader@local.test** account, select
   **Forgot password?**, enter that email and send a reset link.
3. Open **http://localhost:54324**, choose the newest reset email, follow its link
   and save your new password. You can then sign in normally with email/password.

The test reader belongs to **PtS Local Testing** and has explicit read, export and
source-document permissions. It is not a platform administrator. Mail is captured
locally; links are single-use. The optional `.local/login.py` helper still issues
magic links, but normal sign-in no longer needs it.

Administrators can use **Supabase Studio → Authentication → Users** to create a
user with a password or send an invitation. An invitation opens **Set your password**.
Creating an identity does not grant collection access: membership and the three
PtS permissions are still required (see the main README). The local Auth Site URL
is `http://localhost:5179`, and public self-registration is disabled.

Microsoft sign-in is hidden by default. To enable it, configure Supabase's Azure
provider, set `VITE_MICROSOFT_SIGN_IN_ENABLED=true` and restart Vite. For a hosted
project, set the corresponding deployed Auth Site URL and allowed redirects and
configure email delivery; no hosted settings were changed here.

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

Before production, provision the intended users and organization, configure the desired sign-in providers, email delivery
and production URLs, and review source reuse restrictions. Production migration
and public deployment remain separate approval steps.


## Windows / WSL Auth connectivity

Use **http://localhost:5179** for the reader. Its local browser Auth URL must be
`http://localhost:54321`, matching `api.external_url` in `supabase/config.toml`.
On this workstation, native Windows requests to `127.0.0.1:54321` timed out while
`localhost:54321` responded; testing only inside WSL missed that difference.
The local Content service also signs document links with the localhost endpoint.
The services' internal database/Auth connections can continue using 127.0.0.1.

After changing Vite environment settings, reload the reader tab. Request a new
password reset email and use its newest link only once; previously generated links
retain their old hostname. Network failures now show connectivity guidance and
Auth fetches abort after 15 seconds so the form permits retry.

The requested **PtS** organization (description **Psalms that Sings**) is separate
from the original testing organization and holds its own imported collection.
Its production creation is recorded in `deployment/organization.json` and the
[release checklist](LOCAL_AUTH_CONNECTIVITY.md#requested-organization-and-production-release).

## Shared Scribeswell session

Open **http://localhost:5179/scribeswell/** or use Apps → Scribeswell. Both readers
use the same Supabase project and existing `pts-auth` browser session on localhost
port 5179, so sign-in/sign-out updates both tabs. Hebrew reading and morphology
remain public, with an anonymous launchpad; PtS API permissions remain mandatory.

The Scribeswell frontend must also be running on port 5174 behind PtS's development
proxy. Its prepared starter is `python3 apps/scribeswell/.local/start.py`; the Bible
API uses port 8000. Old browser visits to port 5174 redirect to the shared address.
See `apps/scribeswell/web/README.md` for reproducible configuration and production
routing requirements. No production routing or database changes have been made.
