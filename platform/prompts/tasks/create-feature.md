# Task: Create Full Feature (UI + API end-to-end)
version: 1.0.0

## Goal
Scaffold a complete feature: DB → FastAPI → generated client → React UI.

## Inputs
- Feature name (kebab-case, e.g. `verse-reader`, `expense-report`)
- Target app: `apps/<app-name>/`
- Entities involved (from Supabase schema)

## Context to load
See `registry.md` → load `context/error-payload.md` + `context/naming.md` + relevant pattern.
Inject: generated Zod schema for the entity + one reference feature folder.

## Steps
1. **Query Supabase MCP** for live schema of involved tables.
2. Run `generate-models` (or note it needs running) to get fresh Pydantic + Zod.
3. Scaffold API: follow `tasks/create-api.md` steps.
4. Regenerate `platform/api-client/` from FastAPI OpenAPI spec.
5. Scaffold UI: follow `tasks/create-ui.md` steps, using generated api-client.
6. Wire route in app router.
7. **Stop here** — present scaffold for review before wiring complex logic.

## Output contract
- `platform/backend/routers/<feature>.py`
- `platform/backend/services/<feature>.py`
- `apps/<app>/src/pages/<feature>/` (page + components)
- `apps/<app>/src/hooks/use-<feature>.ts`

## Do-not
- Do not skip the MCP schema query
- Do not hand-write models that should be generated
- Do not wire complex mutations before scaffold review
