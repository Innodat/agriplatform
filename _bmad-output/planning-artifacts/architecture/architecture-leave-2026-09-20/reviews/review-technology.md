# Technology reality review

Reviewed 23 September 2026. Verdict: **suitable for architecture consolidation, with one explicit provider feasibility gate to retain**. This is not runtime verification or approval to implement. No new stack, starter, dependency pin or migration was selected.

## Finding T1 — Signed-upload target needs a supported provider path

**Delivery prerequisite; medium severity.** AD-9 inherits platform ADR-0036's fifteen-minute upload capability target, while the stack includes Supabase Storage. The standard Supabase `createSignedUploadUrl` documentation specifies a two-hour lifetime and exposes path/options rather than a caller-selected expiry. This means the ordinary API does not itself demonstrate the accepted target. [Official JavaScript reference](https://supabase.com/docs/reference/javascript/file-buckets-createsigneduploadurl), [official Python reference](https://supabase.com/docs/reference/python/storage-from-createsigneduploadurl).

The spine already defers adapter behavior before attachment delivery and does not assert tested provider support, so this does not require reopening the entire architecture. Minimal resolution: name this known mismatch in the content gate and require a supported adapter path with tested provider-enforced expiry, or a linked superseding decision if a provider-specific exception is needed. A fifteen-minute UI/upload-session timeout alone does not invalidate a longer-lived signed URL. Do not silently edit accepted ADR-0036 or claim the standard Supabase API meets fifteen minutes. Existing five-minute read configuration is a separate capability; the read API accepts an expiry parameter. [Official read reference](https://supabase.com/docs/reference/javascript/file-buckets-createsignedurl).

## Confirmed repository reality

- `platform/builder-cli/templates/web/package.json` contains the React/Vite/TypeScript seed. Its dependency ranges are existing template content, not verified Leave dependencies. The spine correctly defers compatible pins and installation evidence to the first dependent story.
- `platform/builder-cli/templates/backend/requirements.txt` contains FastAPI/Pydantic and the older Supabase client path; SQLAlchemy, Psycopg and Alembic still need deliberate implementation under accepted platform ADR-0014–0016. The spine makes the intended direction explicit without presenting the template as finished.
- `platform/builder-cli/templates/backend/errors.py` has a generated-file warning and an optional integer `code`. The spine correctly includes compatibility with that wire format in the API contract gate; no generated file was changed.
- `platform/builder-cli/README.md` labels the CLI a placeholder. `apps/leave/` is documentation only. `services/app-directory/` is the existing service; naming planned identity/access, Content and Notification contracts does not create them. The spine's planned-state wording and first-slice ownership gate are accurate.
- Content control-plane browser calls and direct signed transfer are accepted exceptions under platform ADR-0004/0005, not an unsupported second business-data path. Azure Blob/Supabase adapters are accepted choices, subject to the concrete lifetime issue above.
- The outbox/separate-process worker follows Leave ADR-0114. Basic backend OpenTelemetry and bounded asynchronous export follow the accepted operational direction. No broker, new workflow engine, monitoring vendor or browser telemetry requirement has been introduced.

## Official capability evidence checked

Opened the four sources in `technology-evidence.md`. FastAPI documents OpenAPI/Pydantic and dependency injection; SQLAlchemy documents the Psycopg PostgreSQL dialect; Alembic calls autogeneration a source of candidate migrations requiring review; Supabase documents native PostgreSQL connectivity. These support the capability choices, not package-version compatibility or deployed tenant security. [FastAPI](https://fastapi.tiangolo.com/features/), [SQLAlchemy](https://docs.sqlalchemy.org/en/20/dialects/postgresql.html#module-sqlalchemy.dialects.postgresql.psycopg), [Alembic](https://alembic.sqlalchemy.org/en/latest/autogenerate.html), [Supabase connections](https://supabase.com/docs/guides/database/connecting-to-postgres).

No package installation, runtime test, provider experiment or production access was performed. Exact versions, pool mode, transaction-scope/RLS behavior and provider enforcement remain explicit delivery evidence requirements rather than assumed guarantees.
