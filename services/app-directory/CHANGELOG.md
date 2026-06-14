# App Directory Service — CHANGELOG

---

## 2026-06-14 — Phase 2: initial build

### Delivered
- FastAPI service scaffolded from `platform/builder-cli/templates/backend/` (vendored).
- `catalog.py`: 5-app catalog (scribeswell enabled; SE/budgeting/school/modelling disabled until live).
- `GET /api/me/apps`: JWT-optional; signed-in → all enabled apps; anonymous → empty list.
- `GET /api/me/context`: resolves org_id, member_id, roles from JWT.
- `GET /api/apps`: full catalog including disabled apps.
- Pydantic schemas: `AppEntry`, `MeContext`, `MeAppsResponse`.
- `docs/app-directory.md`: full service documentation.

### Entitlement rule (Phase 2)
Signed-in → all enabled apps. Extension point documented for Phase 3+ org/role filtering.

### Remaining TODOs
- Populate `.env` with `SUPABASE_JWT_SECRET` + production `APP_URL_*` values.
- Phase 3+: filter `/me/apps` by org entitlement / role / license.
- Phase 3+: gate `GET /apps` behind admin role.
- Phase 3+: add `POST /apps` (admin) to manage catalog dynamically.
