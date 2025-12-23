# Technical Context

## Content System

The content system is designed to handle file uploads securely and efficiently using Azure Blob Storage. It consists of the following components:

### Shared Schemas

Located in `packages/shared/schemas/zod/content-system/`, these Zod schemas define the contracts for:
- Database tables (`cs.content_store`, `cs.content_source`)
- API requests and responses (`cs-upload-content`, `cs-update-content`, `cs-finalize-upload`, `cs-generate-signed-url`)

### Supabase Edge Functions

- `cs-upload-content`: Initiates an upload by creating a `content_store` record and returning a signed SAS URL for Azure Blob Storage.
- `cs-update-content`: Updates metadata for an existing content record.
- `cs-finalize-upload`: Verifies the upload in Azure Blob Storage and marks the content as active.
- `cs-generate-signed-url`: Generates a read-only SAS URL for accessing content.

### Integration Testing

Integration tests are located in `supabase/functions/tests/integration/content-flow.test.ts`. They verify the full lifecycle of content:
1. Upload initiation
2. Blob upload to Azurite (local Azure Blob Storage emulator)
3. Metadata update
4. Finalization
5. Signed URL generation and read verification

## Environment Variables

The following environment variables are required for the content system:
- `SUPABASE_URL`: URL of the Supabase instance
- `SUPABASE_SECRET_KEY`: Service role key for admin access
- `AZURE_STORAGE_CONNECTION_STRING`: Connection string for Azure Blob Storage (or Azurite)
