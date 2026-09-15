# Task: Create API Endpoint (FastAPI)
version: 1.1.0

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
1. Define an acceptance/contract example including success, validation, and authorization outcomes.
2. Add a failing API test through the real FastAPI route and confirm its failure.
3. Define request/response schemas in the target app/service and keep the route thin.
4. Add focused domain/service tests and implement through red-green-refactor.
5. Validate server-derived identity, NGO context, and permissions.
6. Return the platform error shape and update/verify OpenAPI contracts.
7. Run focused, contract, and relevant tenant-isolation tests; record evidence.

## Output contract
- Router: `platform/backend/routers/<domain>.py`
- Service: `platform/backend/services/<domain>.py`
- Schemas: `platform/backend/schemas/<domain>.py` (if new)
- All inputs/outputs validated with Pydantic

## Do-not
- Do not put business logic in the router
- Do not bypass Pydantic validation
- Do not access Supabase with service-role key unless explicitly required
- Do not test only a service function when route/auth/serialization behavior is part of acceptance
