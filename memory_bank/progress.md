# Progress Report

## Completed Tasks

- [x] Scaffold content-system shared schemas
- [x] Update package exports/build for Deno consumption
- [x] Wire Supabase functions to shared schemas
- [x] Implement integration helpers (env, storage)
- [x] Implement full content flow integration test
- [x] Update docs and memory bank per plan
- [x] Refactor content system to provider-mapping architecture
- [x] Implement content versioning for updates

## Next Steps

- [ ] Validate with deno test & summarize
- [ ] Deploy functions to Supabase
- [ ] Integrate frontend with new content system API

---

## Post-ACT Update – 2025-12-28

### Delivered
- Refactored Azure-only storage integration into provider-mapping architecture:
  - Created `StorageProvider` interface in `supabase/functions/_shared/storage-providers/types.ts`
  - Implemented `AzureBlobProvider` using SAS tokens for signed URLs
  - Implemented `SupabaseStorageProvider` using Supabase's built-in signed URL generation
  - Created provider registry/factory in `supabase/functions/_shared/storage-providers/registry.ts`
  - Removed old monolithic `cs-providers.ts` and `azure-blob.ts` files
- Added content versioning support:
  - Created migration `20251226000000_add_content_versioning.sql` with `cs.content_version` table
  - Updated `cs-update-content` handler to archive previous versions before updates
  - Versioning stores: external_key, mime_type, size_bytes, checksum, metadata, replaced_by
- Refactored all content handlers to use provider registry:
  - `cs-upload-content`: Resolves provider from org settings, falls back to default Supabase Storage
  - `cs-finalize-upload`: Uses provider for blob existence verification
  - `cs-update-content`: Archives version and generates new upload URL
- Simplified testing approach (removed _cachedSupabase complexity):
  - All handlers now accept optional `supabase` parameter (default: `supabaseAdmin`)
  - Tests provide mock clients via dependency injection
  - Removed `SKIP_SUPABASE_INIT` logic from production code
  - Test script sets dummy env vars to prevent import-time errors
- Updated unit tests:
  - All 6 unit tests passing (upload-content: 2, finalize-upload: 2, update-content: 2)
  - Added `createStorageProviderMock()` in `supabase/functions/tests/helpers/mocks.ts`
  - Updated `createAuthMock()` to include required `payload.org_id` (defaulted to "org-123")
  - Enhanced `createSupabaseMock()` to support multiple select results via `_setSelectResults()`
  - Fixed Zod error handling using property-based check instead of `instanceof` (due to multiple Zod instances)
- Updated documentation:
  - Modified `docs/tech-spec.md` section 2.4 to document provider architecture and versioning
  - Documented provider selection logic (org settings → default Supabase Storage)

### Deviations / Notes
- Zod validation errors now detected by checking for `issues` property instead of `instanceof ZodError` because schemas come from `@shared` package which may load a different Zod instance
- `orgId` is now REQUIRED in `cs-upload-content` - throws 400 error if not present in JWT claims
- Testing approach simplified: handlers accept optional `supabase`, `requireAuth`, `getProvider`, etc. parameters with sensible defaults, allowing tests to inject mocks cleanly

### Remaining TODOs
- Re-run integration/unit tests for edge functions + web once dependencies are installed/available in CI
- Apply migration `20251226000000_add_content_versioning.sql` to database
- Configure default Supabase Storage bucket for content storage
- Test provider switching between Azure Blob and Supabase Storage

---

## Post-ACT Update – 2025-12-23

### Delivered
- Implemented multi-tenancy groundwork in Supabase:
  - Added `identity.org`, `identity.org_member`, `identity.member_role`.
  - Added `org_id` to finance tables and updated RLS patterns to enforce org scoping.
  - Updated auth hook + authorization helpers to support multi-role claims.
- Fixed seed data so `supabase db reset` succeeds:
  - Reworked `supabase/seeds/010_finance.sql` to avoid cross-statement CTE references.
- Updated shared Zod schemas in `packages/shared` to reflect new schema:
  - Added org-aware fields (e.g. `org_id`) in finance schemas.
  - Added identity schemas for `org`, `org_member`, `member_role`.
  - Removed old `identity.user_roles` schema exports.
- Updated `docs/tech-spec.md` to document multi-tenancy (org tables, org-scoped RLS, and JWT claims).

### Deviations / Notes
- VS Code TypeScript diagnostics were flagging `.deno.ts` barrel exports when using explicit `.ts` suffixes; adjusted barrel exports to omit extension (matching existing non-deno TS barrel style).

### Remaining TODOs
- Decide whether to project should keep `.deno.ts` files under TS compilation, or exclude them from `packages/shared/tsconfig.json` (currently they can trigger TS5097 if `.ts` suffixes are used).
- Re-run integration/unit tests for edge functions + web once dependencies are installed/available in CI.
