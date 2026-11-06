# Leave authorized entry

Generated bounded web.leave-entry.v1 owner. Follow repository AGENTS.md and accepted ADRs. Business data uses Leave API; browser Supabase is Auth only, Microsoft azure provider with SDK PKCE. No password fallback. Normal sign-in never creates membership/grants. Entry needs no employment; employee actions retain setup checks. Independent tabs own their context.

Node26.11.1/npm12.2.0/Python3.15.0/uv0.13.1. Root workspace lock and independent api/uv.lock. In api/: uv sync --frozen --group test; uv run --frozen pytest; uv run --frozen python export_openapi.py. Root: npm run api:generate --workspace @scaffold/leave-web; api:check, test:entry, test:auth, type-check, build with the same workspace.

Runtime: LEAVE_DATABASE_URL must be leave_runtime; LEAVE_ACCESS_ORIGIN, LEAVE_SERVICE_KEY, LEAVE_CURRENT_SESSION_SERVICE_KEY and LEAVE_PREFERENCES_SERVICE_KEY are private. Web VITE_LEAVE_AUTH_URL/ANON_KEY are public Auth configuration. Callback is the exact current origin/auth/callback; allowlist deliberately outside generation.

Protected setup api/tools/prepare_roles.sql; separate nonlogin leave_owner, leave_migrator and leave_runtime. Controlled api/migrate.py with LEAVE_MIGRATION_DATABASE_URL before activation through platform release tooling. No startup migration, automatic downgrade or reset. Retain immutable selection events for this increment. Packaging uses api/package_production.py and explicit selected tools.

Scaffold: bounded entry composition and neutral Auth/HTTP/migration reuse. Shared UI: platform tokens/launcher; owner-specific picker. Agent context: generated guidance. Documentation: owner commands and evidence. ADR: existing accepted decisions suffice. Local synthetic proof does not establish Entra/device or hosted VERIFY; A1/E1 stay open.
