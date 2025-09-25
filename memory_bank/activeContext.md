# Active Context
- Module: Finance → Receipt Capturing
- UI: Modularise v0-generated page.tsx, integrate ShadCN components
- BE: Currently calling Supabase directly from frontend
- Layout: AppShell + Departments + module tabs (Overview, Today, Admin)
- Next step: Run PLAN mode → approve → ACT scaffold

## Dual-Schema Sync Checklist
(Always run this at planning stage for every module)

1. **Frontend Zod (always)**
   - Query Supabase MCP for live schema.
   - Generate/update `Zod` schema(s) for relevant table(s) and enums.
   - Apply in forms, Supabase queries, and component props.

2. **Backend Pydantic (only if using FastAPI/Python)**
   - Ensure Pydantic models match the Supabase schema.
   - Auto‑generate OpenAPI schema from FastAPI.

3. **Sync Zod ←→ Pydantic**
   - Generate/update frontend Zod from backend OpenAPI schema OR directly from Supabase MCP if backend not present.
   - Confirm enums, field names, types, nullability match exactly.
   - Resolve differences before implementation.

4. **Validation locations**
   - FE: On form submit & API responses.
   - BE (if present): On request input & service outputs.

5. **Versioning**
   - Commit schema changes in both frontend and backend repos.
   - Note changes in `progress.md` for historical tracking.

---
