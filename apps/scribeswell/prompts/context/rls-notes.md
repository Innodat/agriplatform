# Context: RLS & Auth Notes
version: 1.0.0
source: platform/prompts/tasks/rls-notes.md@1.0.0
app_overrides: false

## Multi-tenancy
- All org-scoped tables have `org_id uuid` column.
- RLS enforces `org_id = identity.current_org_id()`.
- Tables without direct `org_id` are scoped via parent join (e.g. purchase → receipt → org).

## Auth functions (Supabase)
```sql
identity.current_org_id()    -- returns org for authenticated user
identity.current_member_id() -- returns membership row id
identity.authorize('<schema>.<table>.<action>') -- permission check
```

## Permission format
`<schema>.<table>.<action>` — actions: `admin`, `read`, `insert`, `update`, `delete`
Example: `finance.receipt.read`, `bible.verse.read`

## FastAPI JWT validation
- Extract Bearer token from `Authorization` header.
- Verify with Supabase JWT secret.
- Inject `org_id` + `user_id` + `permissions` into request context.
- Never trust client-supplied `org_id` — always derive from JWT.

## Soft delete
- Finance tables use `deleted_at TIMESTAMPTZ NULL` (NULL = active).
- Read via `*_read` views that filter `WHERE deleted_at IS NULL`.
