# platform/api-client

**Status:** Placeholder — Phase 2

**GENERATED** TypeScript client for the FastAPI backend. Do not hand-edit.

## Purpose
- Typed HTTP client generated from FastAPI's OpenAPI spec
- Used by all apps to call the backend
- Replaces direct `@supabase/supabase-js` data calls in new apps

## Generation
```bash
# Run after FastAPI is running:
npx openapi-typescript http://localhost:8000/openapi.json -o src/generated/api.ts
# Or via orval for full client generation:
npx orval --config orval.config.ts
```

## Planned contents
```
src/
  generated/
    api.ts              ← GENERATED — do not edit
  client.ts             ← configured axios/fetch instance
  index.ts
```

## Phase
Generated in **Phase 2** once FastAPI skeleton (Phase 1) is complete.
