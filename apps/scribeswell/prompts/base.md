# Base Rules
version: 1.0.0
source: platform/prompts@1.0.0
app: scribeswell

## Stack
React + ShadCN UI · FastAPI · Supabase · Arq workers

## Hard Rules
1. UI → FastAPI for all data CRUD/read access.
2. Supabase client only for Auth + approved Realtime.
3. Generated files are source of truth. Never hand-edit `*/generated/` or `*/schemas/generated/`.
4. Strict TypeScript. No `any`.
5. FE contracts derive from FastAPI OpenAPI/Pydantic; Supabase schema is backend persistence detail.
6. Reuse before inventing. Check local prompts/context and existing components first.
7. Files: kebab-case. Components/services: PascalCase.
8. Hebrew reader UI must preserve RTL readability and keyboard accessibility.
9. Deviations require one-line reasoning + trade-off.

## Repo Layout
```
apps/scribeswell/backend/   → FastAPI app
apps/scribeswell/docs/      → documentation
apps/scribeswell/prompts/   → prompt driven development prompts
apps/scribeswell/scripts/   → app-level management scripts, e.g. seed script
apps/scribeswell/supabase/  → migrations, seeds
apps/scribeswell/tools/     → app-level dev tooling
apps/scribeswell/web/       → ShadCN UI
```

## Context Loading
For task specifics see `prompts/registry.md`.
Load only the context files listed for the current task.
Do not dump the whole codebase.
