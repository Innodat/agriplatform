# System Patterns

## General
- Always plan with a visual diagram first:
  - UI → ASCII layout diagram + route map
  - Backend → API/service diagram + endpoint map
- Supabase MCP is the single source of truth for schemas.
- Apply **dual‑schema validation** pattern when a separate backend is introduced.
- Use plan → approve → act gates for all changes.
- Separate shared vs feature-local modules/components/services.
- Maintain strict TypeScript; no `any`.
- ShadCN UI is the base design system for frontend.

---

## Canonical ASCII Layout Template (Frontend/UI)

+--------------------------------------------------------------------------------------+
| Topbar: Brand | Search | User | RoleSwitcher                                         |
+---------------------------+----------------------------------------------------------+
| Sidebar (Departments)     | Content Area                                             |
| - Dashboard               |  /<department>/<module>                                  |
| - Finance                 |   ├─ Tabs: [Overview] [Today] [Admin (admin only)]       |
|   └─ Receipt Capturing    |   │                                                      |
| - Logistics               |   ├─ Overview: StatsGrid + RecentTable                   |
| - HR                      |   ├─ Today: AddDialog + List                             |
| - Operations              |   └─ Admin: Filters + AdminTable                         |
+---------------------------+----------------------------------------------------------+

**Route Map (React Router)**:
/
  -> <AppShell><Dashboard /></AppShell>
/finance
  -> <AppShell><FinanceLayout /></AppShell>
/finance/receipt-capturing
  -> <FinanceLayout><ReceiptDashboard /></FinanceLayout>

---

## Canonical API Diagram Template (Backend)

[Client/UI] 
   |
   v
[Route Handler]  -->  [Request Validation Schema]  -->  [Service Layer]  -->  [DB Query]
   ^                                                                       |
   |                                                                       v
[Response Validation Schema]  <--  [Transformation]  <--  [DB Result]

---

## Dual‑Schema Sync Pattern (Frontend/Backend)

**When using Supabase only (no custom backend):**
- Generate `Zod` schemas directly from Supabase MCP.
- Use them for:
  - Form validation
  - API response parsing
  - Component prop types

**When using a separate backend in TypeScript/Node:**
- Keep `Zod` on both frontend and backend.
- Share schema definitions through a common package or repo submodule.

**When using a separate backend in Python (FastAPI):**
- Backend:
  - Use **Pydantic** models for request and response validation.
  - Expose OpenAPI schema automatically from FastAPI.
- Frontend:
  - Generate/update matching **Zod** schemas from the OpenAPI schema (using converters).
  - Keep conversion as part of the build or CI workflow so contracts stay in sync.

**Benefits:**
- Ensures frontend and backend speak the same language.
- Changes in DB schema propagate through MCP → backend models → frontend schemas without drift.
- Prevents runtime errors from mismatched payloads.

---

## Content System Pattern

**Architecture**: Hexagonal/Clean Architecture for content management
- **Domain**: Content is decoupled from business domains (finance, logistics, etc.)
- **Storage**: All media/files accessed via FastAPI Content Service; frontend never accesses storage directly
- **Security**: Upload/download through signed URLs with short lifetimes; backend validates permissions

**Database Schema (cs schema)**:
- `cs.content_source`: Storage provider configs (Azure Blob, future: S3)
- `cs.content_store`: Content metadata (external_key, mime_type, size, checksum)
- `cs.receipt_content`: Domain mapping (receipt_id → content_id with role)

**Flow**:
1. **Upload**: FE → POST /api/content/initiate → BE returns signed upload URL → FE uploads to storage → POST /api/content/{id}/finalize
2. **Download**: FE → GET /api/receipts/{id}/content → BE returns signed download URLs
3. **Delete**: FE → DELETE /api/content/{id} → BE removes from storage + database

**Benefits**:
- Domain separation: Finance doesn't know about Azure Blob details
- Security: All access controlled through backend with JWT validation
- Flexibility: Easy to switch storage providers or add CDN
- Auditability: All content operations logged through backend

---

## Usage Notes
- Any time a schema changes in Supabase:
  1. Regenerate backend models (Zod or Pydantic).
  2. Regenerate frontend Zod from MCP or from backend OpenAPI spec.
  3. Commit both together to keep contract history in VCS.
