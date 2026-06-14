# App Directory Service

**Service:** `services/app-directory`  
**Port (dev):** 8001  
**Architecture:** Cross-app runtime service (not a silo app — shared by all apps)  
**Status:** Phase 2 — catalog-backed, JWT-optional entitlement

---

## Purpose

The App Directory service is the single source of truth for which apps exist in the platform suite and which apps a given user can access. Every app frontend calls this service to populate its burger menu / app launcher.

This is a **runtime service** (not a shared package). Apps call it over HTTP — they do not import from it.

---

## API

```
GET /health                → liveness probe
GET /api/me/apps           → apps available to current user (JWT optional)
GET /api/me/context        → resolved identity context (org_id, member_id, roles)
GET /api/apps              → full catalog including disabled apps
```

OpenAPI docs: `http://localhost:8001/docs`

### GET /api/me/apps

**Auth:** Optional Bearer JWT (Supabase-issued)

**Phase 2 entitlement rule:**
- Anonymous (no JWT) → `{ apps: [], context: { org_id: null, member_id: null, roles: [] } }`
- Authenticated (valid JWT) → all `enabled: true` apps from catalog + resolved context

**Extension point (Phase 3+):** filter by `org_id`, role, or license entitlement.

**Response:**
```json
{
  "apps": [
    {
      "id": "scribeswell",
      "name": "Scribeswell",
      "url": "https://scribeswell.example.com",
      "icon": "book-open",
      "description": "Hebrew Bible reader with morphological analysis",
      "enabled": true
    }
  ],
  "context": {
    "org_id": "uuid-here",
    "member_id": 42,
    "roles": ["employee"]
  }
}
```

---

## App catalog

Defined in `catalog.py`. To add a new app:
1. Add an `AppEntry` to `APP_CATALOG` with `enabled=False`.
2. Add the URL env var to `config.py` + `.env.example`.
3. Set `enabled=True` when the app is live.

---

## Running locally

```bash
cd services/app-directory
cp .env.example .env          # fill in SUPABASE_JWT_SECRET
pip install -r requirements.txt
uvicorn main:app --reload --port 8001
```

---

## Structure

```
services/app-directory/
├── main.py                 # FastAPI app entry point
├── config.py               # pydantic-settings (reads .env)
├── errors.py               # {error, code?, details?} shape
├── catalog.py              # APP_CATALOG + get_enabled_apps()
├── auth/
│   └── jwt_optional.py     # OptionalUser / RequiredUser dependencies
├── routers/
│   └── apps.py             # /me/apps, /me/context, /apps
├── schemas/
│   └── app_schemas.py      # Pydantic: AppEntry, MeContext, MeAppsResponse
├── requirements.txt
├── .env.example
├── docs/                   # This file
└── CHANGELOG.md
```

---

## Contract alignment

`AppEntry` and `MeContext` are mirrored in:
- **Backend (Pydantic):** `schemas/app_schemas.py`
- **Frontend (Zod):** `platform/app-directory-client/src/schemas.ts`

Keep these in sync. If you change a field, update both.

---

## Silo note

This service lives in `services/` (not `apps/` or `platform/`). It is a **cross-app runtime service** — it has a clear API contract, can be versioned, secured, monitored, and replaced independently. Apps call it over HTTP; they do not import from it at build time.
