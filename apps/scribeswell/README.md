# Scribeswell

Public Hebrew Bible reading and study run through FastAPI. The browser uses Supabase
for shared authentication only. The API reads PostgreSQL with `scribeswell_runtime`;
the corpus operator uses the separate `scribeswell_import` role. No Data API schema
exposure or service-role key is required by either path. App Directory reads its
static catalogue and verified Auth claims; it does not query the identity schema.

For local setup, install `backend/requirements.txt` in a virtual environment. Apply
the existing Scribeswell schema to a disposable/local database, then apply
`deployment/bootstrap/001_direct_database_roles.sql` explicitly as its administrator.
Set each role's password through your local secret channel. Copy
`backend/.env.example` to an ignored local env file, supply the runtime URL, and remove
obsolete service-key variables from `.env`, `.env.local` and the shell. Start:

```bash
uvicorn main:app --app-dir apps/scribeswell/backend --port 8000
```

Remote database URLs require `sslmode=require` or `verify-full`. Runtime connections
are pooled (maximum 8, maximum 32 waiters, 5-second acquisition/connect waits), with
15-second statements, 3-second locks, and 15-second idle transactions. Database
failures return a safe 503. Health is a liveness check, not a corpus acceptance check.

The reviewed local source remains `scripts/hebrew.json`. Validate without a database:

```bash
python apps/scribeswell/scripts/seed.py --dry-run
```

For an explicitly approved import, set `SCRIBESWELL_IMPORT_DATABASE_URL` in the
operator environment and run `scripts/seed.py`; use `--verify-only` for a full audit
or `--book Gen` to resume one book. Source validation precedes writes. Each chapter's
writes and audit commit together; a failed chapter rolls back, earlier completed
chapters remain, and reruns preserve IDs. Unexpected extra rows fail the audit.

See [deployment transition and recovery](deployment/README.md) for the release gate,
and [DIRECT_DATABASE.md](DIRECT_DATABASE.md) for requirement/test evidence. No shared
UI or builder scaffold changes are needed; the owner-local adapter is not promoted
as a platform runtime library. Existing architecture decisions remain unchanged.
