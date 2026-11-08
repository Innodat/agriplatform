# PtS · Swahili Poetry

Protected React reader and FastAPI API for the preserved collection. Current PtS
capabilities are account-scoped: an authorized reader needs no organization,
membership or employment. Read, export and stored-document access each require
their own explicit grant. Directory provides navigation; the PtS API rechecks
the exact action through Access.

The account/corpus/private-file transition is being implemented under
[E1-PTS-ADOPT](../../_bmad-output/implementation-artifacts/spec-1-15-e1-pts-account-corpus-files.md).
Production activation is separate. See the [current adoption runbook](docs/ACCOUNT_ADOPTION.md)
for the controlled transition and qualification limits. Older records in
[VERIFICATION.md](docs/VERIFICATION.md) and the original local setup describe
their historical schema and fixtures; they do not qualify this successor release.

## Development

Use Python 3.15.0, uv 0.13.1, Node 26.11.1 and npm 12.2.0, matching the selected
runtime. The Python owner is frozen in `pyproject.toml`/`uv.lock`. Frontends use
the root npm workspace and `package-lock.json`:

```bash
uv sync --frozen --project apps/pts
npm ci --workspace=apps/pts/web --include-workspace-root
npm run build --workspace=apps/pts/web
python3 tools/py/run_compose_supabase.py --check-only
apps/pts/.venv/bin/python -m apps.pts.tools.verify_archive
```

Run the owner API and frontend with only their selected process configuration:

```bash
apps/pts/.venv/bin/python -m uvicorn apps.pts.backend.main:app --port 8010 --no-access-log
npm run dev --workspace=apps/pts/web
```

These commands do not migrate or grant access. Native files additionally require
the configured dedicated HTTPS file origin and same-site frontend; HTTP development
without that ingress does not qualify cookies or PDF/download behavior.

The ignored canonical copy in `reference/poetry-library` and the original
`/mnt/c/wycliffe/PtS/PtS_Poetry_Library` remain protected source data. Never stage,
bundle or serve them as frontend assets. Obtain an authorized copy and verify
the checksum manifest before import. Do not import alternative snapshots as
additional rows or alter recorded rights and source notices.

## Configuration and ownership

`deployment/runtime.env.example` is the API's configuration catalogue. Runtime
uses `pts_account_runtime`; importer uses separate `pts_corpus_import`; only
`pts_migrator` may migrate and bind the corpus. Keep all owner, operator, Content
and provider credentials out of frontend configuration.

The PtS API needs `PTS_DATABASE_URL`, `ACCESS_URL`, `CONTENT_URL`,
`PTS_SERVICE_KEY`, `IDENTITY_URL`, `PTS_CURRENT_SESSION_SERVICE_KEY`,
`PTS_CORS_ORIGINS`, `PTS_FILE_ORIGIN` and `PTS_FILE_FRONTEND_ORIGIN`.
Access and Identity own authentication/admission and current provider-session
checks. Content owns stored ownership, readiness, immutable bytes and provider
access; its runtime policy names PtS explicitly with application resource scope.

The web UI receives only public Auth configuration, API/Directory origins and
`VITE_PTS_FILE_ORIGIN`. Existing Supabase auth owns refresh and local sign-out;
file transport never receives a refresh token. Configure the actual Auth
callbacks for the selected frontend before activation. Microsoft sign-in remains
optional through `VITE_MICROSOFT_SIGN_IN_ENABLED` and existing Auth configuration.
Set `APP_URL_PTS` on Directory to the selected reader URL.

## Verification

Run the focused API/collection/contract tests with the owner environment; tests
using doubles establish only their boundary. Browser checks use:

```bash
npm exec --workspace=apps/pts/web -- playwright install chromium
npm run test:browser --workspace=apps/pts/web
```

The ordinary browser suite uses UI doubles over disposable loopback HTTPS so
the production client's HTTPS/same-site checks remain active. Playwright ignores
certificate errors in that isolated context; this does not verify certificate
trust, cookie enforcement, current provider sessions or routed native bytes.
The separate guarded
`apps.pts.tests.integration_fixture` composes fresh real provider/Storage/owner
fixtures and has explicit phase/output requirements. Read its runbook and
custody prerequisites before using it. Never restart or reset a retained
attempt to manufacture new evidence. Root npm build/dev are not PtS verification.

Original assistant checks do not establish human review, rights clearance,
training readiness, hosted origin configuration or production activation.
