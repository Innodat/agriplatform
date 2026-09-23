# Architecture consolidation: technology evidence

Checked 23 September 2026. This records capability fit, not a dependency upgrade or
claim that unimplemented services exist. Exact compatible versions/lockfiles are a
first-delivery prerequisite, not selected by the architecture consolidation.

- [FastAPI official features](https://fastapi.tiangolo.com/features/): Pydantic-based
  validation, OpenAPI and dependency injection support the adopted API boundary.
- [SQLAlchemy PostgreSQL dialect](https://docs.sqlalchemy.org/en/20/dialects/postgresql.html#module-sqlalchemy.dialects.postgresql.psycopg):
  explicit Psycopg dialect supports the accepted native PostgreSQL access choice.
- [Alembic autogeneration](https://alembic.sqlalchemy.org/en/latest/autogenerate.html):
  generated candidate migrations require review; matches the existing migration ADR.
- [Supabase PostgreSQL connections](https://supabase.com/docs/guides/database/connecting-to-postgres):
  native database connectivity is available; concrete connection/pool mode still must
  be verified with transaction-local scope and the selected driver before delivery.

Repository reality checks:

- `platform/builder-cli/templates/web/package.json` contains React/Vite/TypeScript,
  React Router, Tailwind, Lucide and Supabase Auth client dependencies. Existing
  ranges are seed evidence, not verified Leave lockfile selections.
- `platform/builder-cli/templates/backend/requirements.txt` contains FastAPI and
  Pydantic alongside an older Supabase access template. The accepted SQLAlchemy/
  Psycopg/Alembic direction still needs implementation and deliberate scaffold change.
- `apps/leave/` is planning-only. `services/app-directory/` exists; the planned Content,
  Notification and current-access contracts are not established merely by naming them.
- Root build/dev commands remain unsuitable as Leave verification. No dependencies
  installed, migrations run, runtime tests performed or production readiness claimed.

Previously accepted provider, UI and authentication choices remain governed by their
ADRs and UX sources; this consolidation does not introduce a new starter or vendor.
