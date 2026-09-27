# Scribeswell Hebrew Bible reader

Read the existing Hebrew Bible collection, choose a book/chapter, and select a word
for its morphological analysis. Reading is public; optional Supabase sign-in is
for platform app-directory context. PtS collection permissions remain separate.

## Local setup

Start the shared local Supabase stack with `npx supabase start` from the repository
root. This preserves existing data; do not reset or reimport to start the reader.
The current local collection contains 39 books and 929 chapters. See
[the import audit](../docs/data-repair.md) for data verification and repair tooling.

Create `apps/scribeswell/backend/.env.local` using the names in
`backend/.env.example`: local `SUPABASE_URL=http://127.0.0.1:54321`,
`SUPABASE_SECRET_KEY` and `SUPABASE_JWT_SECRET` from your local Supabase status.
Keep privileged keys in this backend file only. Create `web/.env.local` with:

```dotenv
VITE_SUPABASE_URL=http://localhost:54321
VITE_SUPABASE_ANON_KEY=<local publishable/anon key>
VITE_APP_DIRECTORY_URL=http://localhost:8001
```

Both local configuration files are ignored by git. Browser configuration must use
`localhost` for Windows/WSL connectivity. The reader API uses the existing
Scribeswell schema and API views; no migrations run at server startup.

From the repository root:

```bash
uv venv apps/scribeswell/.local/venv
uv pip install --python apps/scribeswell/.local/venv/bin/python -r apps/scribeswell/backend/requirements.txt
apps/scribeswell/.local/venv/bin/python -m uvicorn main:app --app-dir apps/scribeswell/backend --port 8000 --no-access-log
```

In another terminal:

```bash
npm ci
npm run dev --workspace=apps/scribeswell/web
```

Open **http://localhost:5179/scribeswell/**, or choose **Apps → Scribeswell** in PtS.
With the shared configuration below, the frontend proxies `/scribeswell/api` to port 8000. The API health endpoint is
http://localhost:8000/health. The existing directory service on port 8001 supplies
the app selector; PtS's local starter includes it (see PtS's LOCAL_SETUP.md).
Reading still works if the directory is unavailable. Use Ctrl+C in each terminal
to stop the reader processes without stopping Supabase or deleting data.

## Verification

```bash
npm run build --workspace=apps/scribeswell/web
npx playwright install chromium
npm run test:browser --workspace=apps/scribeswell/web
uv pip install --python apps/scribeswell/.local/venv/bin/python pytest
apps/scribeswell/.local/venv/bin/python -m pytest apps/scribeswell/tests -q
```

The browser suite serves isolated fixtures on port 5182; it does not modify the
local Bible data. On this prepared WSL workstation, Chromium additionally uses
`LD_LIBRARY_PATH=/tmp/pts-browser-libs/usr/lib/x86_64-linux-gnu`.

## Release configuration

The local Vite proxy is development-only. A production release must route
`/scribeswell/api/bible/*` to Scribeswell's API (stripping `/scribeswell`), set the directory's Scribeswell URL to its
released frontend, and supply server-side Supabase credentials and public browser
Auth configuration for that environment. These production changes are not applied
by local setup. See [local release verification](../docs/LOCAL_READER_RELEASE.md).

The currently prepared background processes can also be managed with these
workstation-only, ignored helpers (they check process identities before stopping):

```bash
python3 apps/scribeswell/.local/stop.py
python3 apps/scribeswell/.local/start.py
```

The reader bundles Noto Serif Hebrew locally; its font licence is included at
`public/fonts/OFL-Noto-Serif-Hebrew.txt`. It makes no external font request.

## Shared sign-in with PtS

Use **http://localhost:5179/scribeswell/** for the reader. Both applications then
share the existing Supabase browser session (`pts-auth`); signing in or out in
one tab updates the other. All Bible reading and morphology remain public, and
the launchpad uses the public enabled-app catalogue when signed out. PtS access
is still checked by its API for the selected organization.

Set these additional values in `apps/scribeswell/web/.env.local`:

```dotenv
VITE_APP_BASE=/scribeswell/
VITE_PLATFORM_ORIGIN=http://localhost:5179
VITE_API_BASE_URL=http://localhost:8000
```

Use the same `VITE_SUPABASE_URL` and public key as PtS. Start both frontend
processes as well as the Bible API and directory. PtS's Vite server forwards
`/scribeswell/` to the reader on 5174, including assets and development sockets.
The reader forwards `/scribeswell/api/bible/*` to its API with the application
prefix removed. Browser visits to the old 5174 address redirect to 5179 and retain
book/chapter selection. Do not mix `localhost` and `127.0.0.1` in browser URLs.

Set `APP_URL_SCRIBESWELL=http://localhost:5179/scribeswell/` in the app-directory
service environment (or its ignored local environment file), then restart that
service. The directory already permits the configured PtS origin via its catalogue;
for other hosts, ensure CORS includes the chosen platform origin. The prepared
workstation's directory environment and reader configuration are already updated.

Production needs equivalent routing on **one trusted browser origin**: serve the
Scribeswell build at `/scribeswell/` and route `/scribeswell/api/bible/*` to its API,
stripping `/scribeswell`. Build with that base, configure the directory's canonical
URLs, and use the same Supabase project. Separate hostnames/ports do not share
browser sessions. No tokens are transferred through launchpad URLs. The Vite proxy
and legacy-port redirect are for development, not a production web server.

```bash
LD_LIBRARY_PATH=/tmp/pts-browser-libs/usr/lib/x86_64-linux-gnu node_modules/.bin/playwright test --config apps/scribeswell/web/playwright.session.config.cjs
```

This additional suite runs two frontends and a fixture API on ports 5183–5185,
covering shared authentication, public access and actual nested API forwarding.
