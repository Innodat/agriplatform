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

**Architecture**: Hexagonal/Clean Architecture with Provider Abstraction
- **Domain**: Content is decoupled from business domains (finance, logistics, etc.)
- **Storage**: Multi-provider support (Azure Blob, Supabase Storage) via unified interface
- **Security**: Upload/download through signed URLs with short lifetimes; backend validates permissions
- **Versioning**: Automatic archival of previous versions when content is updated

**Database Schema (cs schema)**:
- `cs.content_source`: Storage provider configs (Azure Blob, Supabase Storage)
- `cs.content_store`: Active content metadata (external_key, mime_type, size, checksum)
- `cs.content_version`: Historical versions (for rollback/archival)

**Provider Interface**:
```typescript
export interface StorageProvider {
  generateReadUrl(params: ReadUrlParams): Promise<SignedUrlResult>;
  generateUploadUrl(params: UploadUrlParams): Promise<SignedUrlResult>;
  exists(params: ExistsParams): Promise<ExistsResult>;
  delete(params: DeleteParams): Promise<void>;
}
```

**Supported Providers**:
- **Azure Blob Storage**: Uses SAS tokens for signed URLs
- **Supabase Storage**: Uses Supabase's built-in signed URL generation

**Provider Selection**:
1. Check org settings for `content_source_id`
2. If not found, use "Default Supabase Storage"
3. Instantiate provider via registry: `getProvider(providerName, settings)`
4. Use provider for all storage operations

**Flow**:
1. **Upload**: FE → POST /functions/v1/cs-upload-content → BE returns signed upload URL → FE uploads to provider → POST /functions/v1/cs-finalize-upload
2. **Update**: FE → PUT /functions/v1/cs-update-content → BE archives current version → BE returns new upload URL → FE uploads → POST /functions/v1/cs-finalize-upload
3. **Download**: FE → GET /functions/v1/cs-generate-signed-url?id={id} → BE returns signed download URL
4. **Delete**: Provider's delete() method (not exposed via API yet)

**File Structure**:
```
supabase/functions/_shared/storage-providers/
├── types.ts                    # StorageProvider interface
├── azure-blob-provider.ts      # Azure Blob implementation
├── supabase-provider.ts        # Supabase Storage implementation
└── registry.ts                 # Provider factory
```

**Benefits**:
- **Multi-Provider Support**: Easy to switch between Azure, Supabase, or add new providers (S3, GCS, etc.)
- **Version Control**: Automatic archival of previous versions when updating content
- **Tenant Isolation**: Each org can use different storage providers
- **Type Safety**: Full TypeScript support with provider interface
- **Testability**: Easy to mock providers in tests
- **Domain Separation**: Business logic doesn't know about storage provider details
- **Security**: All access controlled through backend with JWT validation
- **Flexibility**: Easy to switch storage providers or add CDN
- **Auditability**: All content operations logged through backend

---

## Usage Notes
- Any time a schema changes in Supabase:
  1. Regenerate backend models (Zod or Pydantic).
  2. Regenerate frontend Zod from MCP or from backend OpenAPI spec.
  3. Commit both together to keep contract history in VCS.
