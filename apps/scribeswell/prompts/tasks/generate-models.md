# Task: Generate Models / Schemas
version: 1.0.0
source: platform/prompts/tasks/generate-models.md@1.0.0
app_overrides: false

## Goal
Regenerate Zod (TS) and Pydantic (Python) models from the live Supabase schema.
Generated files are source of truth — never hand-edit them.

## Inputs
- Table(s) or schema(s) to regenerate (or "all")
- Target: `zod` | `pydantic` | `both`

## Context to load
Load `context/rls-notes.md`. Inject: current generated schema file for the table (if exists).
Query Supabase MCP for live schema before generating.

## Steps
1. Query Supabase MCP for the target table(s) — get exact types, enums, nullability.
2. Generate Zod schemas → `platform/shared/schemas/zod/<domain>/<table>.schema.ts`
   - Row / Insert / Update variants
   - Infer TypeScript types
   - Add `// GENERATED — do not edit` banner
3. Generate Pydantic models → `platform/backend/models/generated/<domain>.py`
   - Match exact field names, types, nullability from DB
   - Add `# GENERATED — do not edit` banner
4. Run `tools/py/run_schema_sync.py` to sync Zod → JSON Schema.
5. Note any breaking changes vs previous version.

## Output contract
- `platform/shared/schemas/zod/<domain>/<table>.schema.ts` (with banner)
- `platform/backend/models/generated/<domain>.py` (with banner)
- No manual edits to generated files

## Do-not
- Do not hand-write models that should be generated
- Do not edit generated files — fix the generator instead
- Do not skip the MCP schema query
