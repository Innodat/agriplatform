# Base Rules (always loaded — keep minimal)
version: 1.0.0

## Stack
React + ShadCN UI (ui-core → ui-business → ui-app) · FastAPI · Supabase · Arq (Redis workers)

## Hard Rules
1. **UI → FastAPI for all data CRUD.** Supabase client only for Auth + Realtime.
2. **Generated files are source of truth.** Never hand-edit files in `*/generated/` or `*/schemas/generated/`.
3. **Reuse before inventing.** Check `platform/prompts/context/` and `platform/ui-*` before creating new patterns.
4. **Error shape:** `{ error: string, code?: number, details?: any }` — everywhere.
5. **Strict TypeScript.** No `any`. FE contracts derive from FastAPI OpenAPI/Pydantic; Supabase schema is backend persistence detail.
6. **Files:** kebab-case. **Components/Services:** PascalCase. **Commits:** conventional (`feat:`, `fix:`, `refactor:`, `docs:`, `chore:`).
7. **Prefer Builder CLI scaffolds** (`create-feature`, `generate-models`) over manual creation.
8. **Deviations** must include one-line reasoning + trade-off (Flexibility Clause).

## Repo Layout
```
platform/shared/     → Zod schemas, shared services, lib
platform/ui-core/    → ShadCN base wrappers
platform/ui-business/→ reusable domain components (CrudPage, ReaderLayout, …)
platform/backend/    → FastAPI app
platform/api-client/ → GENERATED typed TS client (from FastAPI OpenAPI)
platform/builder-cli/→ create-feature / generate-models / validate-patterns
apps/receipts-web/   → legacy receipts app (frozen; direct Supabase OK here)
apps/receipts-mobile/→ legacy receipts mobile (frozen)
apps/scribeswell/      → Hebrew Bible reader (clean reference app)
supabase/            → migrations, edge functions, seeds
tools/               → repo-level dev tooling
```

## Context Loading
For task specifics see `platform/prompts/registry.md`.
Load **only** the context files listed there for the current task.
Do NOT load memory_bank/ (archived). Do NOT dump the whole codebase.
