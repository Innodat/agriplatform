# platform/backend

**Status:** Placeholder — Phase 1

FastAPI application — the domain + API layer between UI and Supabase.

## Purpose
- All data CRUD goes through here (UI never touches Supabase directly for data)
- Business logic, validation, authorization, AI endpoints
- Exposes OpenAPI spec → used to generate `platform/api-client/`

## Planned structure
```
platform/backend/
  main.py               ← FastAPI app + router registry
  routers/              ← thin route handlers (one file per domain)
  services/             ← business logic (one file per domain)
  schemas/              ← Pydantic request/response schemas
  models/
    generated/          ← GENERATED Pydantic models from Supabase (do not edit)
  domain/               ← domain types, enums, constants
  auth/                 ← JWT validation, permission helpers
  workers/              ← Arq task definitions (Phase 4)
  requirements.txt
```

## Phase
Scaffolded in **Phase 1** with the first Bible reader endpoints.
