# Task: Create API Endpoint (FastAPI)
version: 1.0.0

## Goal
Add a new FastAPI endpoint following platform backend patterns.

## Inputs
- Domain/entity name (e.g. `verse`, `receipt`)
- HTTP method + path (e.g. `GET /api/verses/{book_id}`)
- Auth requirement: public | authenticated | role-gated

## Context to load
See `registry.md` → load `context/error-payload.md` + `context/naming.md` + `context/rls-notes.md`.
Inject: the generated Pydantic model for the entity + one reference router file.

## Steps
1. Use generated Pydantic models from `platform/backend/models/generated/` — never hand-write.
2. Define request/response schemas in `platform/backend/schemas/<domain>.py`.
3. Add route in `platform/backend/routers/<domain>.py` (thin controller only).
4. Business logic goes in `platform/backend/services/<domain>.py`.
5. Validate JWT + permissions in the route (use shared auth dependency).
6. Return consistent error shape: `{ error, code?, details? }`.
7. Add to router registry in `platform/backend/main.py`.

## Output contract
- Router: `platform/backend/routers/<domain>.py`
- Service: `platform/backend/services/<domain>.py`
- Schemas: `platform/backend/schemas/<domain>.py` (if new)
- All inputs/outputs validated with Pydantic

## Do-not
- Do not put business logic in the router
- Do not bypass Pydantic validation
- Do not access Supabase with service-role key unless explicitly required
