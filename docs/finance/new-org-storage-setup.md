# Storage Setup for New Organizations

## Overview

When a new organization is created dynamically through the application, it needs proper storage configuration. This document explains how to set up storage for new organizations.

## Background

The content system uses two storage providers:
- **Azure Blob Storage** (`azure_blob`) - Used by specific organizations (e.g., Liseli)
- **Supabase Storage** (`supabase_storage`) - Default storage for other organizations

## Existing Configuration

### Migration (`20250925164400_create_content_system_schema.sql`)

The migration creates two default content sources with **resolved bucket/container names**:

1. **Liseli Azure Storage** (`azure_blob`)
   - Container: `content-liseli-dev`
   - Account: `liseliblob`
   - Connection secret: `LISELI_AZURE_BLOB_CONNECTION`

2. **Default Supabase Storage** (`supabase_storage`)
   - Bucket: `content-dev`
   - Connection secret: `SUPABASE_SERVICE_ROLE_KEY`

## Creating New Organizations

### Step 1: Resolve Bucket/Container Name

For organizations using **Default Supabase Storage**, generate the bucket name using the pattern:
```
content-{org_slug}-{env}
```

Examples:
- `kok-home-dev` for Kok Home org in dev environment
- `newcorp-prod` for new corp org in production

### Step 2: Update Organization Settings

When creating a new organization, set the `content_source_id` in the organization's settings:

```typescript
// Example: Creating a new organization via application

const orgSlug = "new-corp"; // from request or JWT
const env = Deno.env.get("ENV") ?? "dev";

// 1. Get the default Supabase storage source
const { data: defaultSource } = await supabase
  .schema("cs")
  .from("content_source")
  .select("id")
  .eq("name", "Default Supabase Storage")
  .eq("deleted_at", null)
  .limit(1)
  .single();

// 2. Create the organization
const { data: org } = await supabase
  .schema("identity")
  .from("org")
  .insert({
    name: "New Corporation",
    slug: orgSlug,
    settings: {
      content_source_id: defaultSource.id,
      bucket_name: `content-${orgSlug}-${env}`
    },
    created_by: userId,
    updated_by: userId
  })
  .select()
  .single();
```

### Step 3: Ensure Bucket Exists (Lazy Creation)

The bucket will be created automatically when the first upload occurs via the `cs-upload-content` edge function. The handler includes:

```typescript
// In cs-upload-content/handler.ts
if (provider.ensureBucketExists) {
  try {
    await provider.ensureBucketExists({
      bucketOrContainer,
      isPublic: false,
    });
  } catch (error) {
    console.warn(`Failed to ensure bucket exists: ${error}. Continuing anyway...`);
  }
}
```

This means you don't need to explicitly create buckets - they're created on first use.

## Special Cases

### Organizations Using Azure Blob Storage

If an organization needs to use Azure Blob Storage instead of the default:

1. Create a new content source record:
```sql
INSERT INTO cs.content_source (provider, name, settings) VALUES (
  'azure_blob',
  'New Corp Azure Storage',
  '{
    "account_name": "newcorpblob",
    "container_name": "content-new-corp-dev",
    "connection_secret": "NEW_CORP_AZURE_BLOB_CONNECTION"
  }'::jsonb
);
```

2. Set `content_source_id` in organization settings to point to this new source.

### Production Environment

For production, ensure the bucket/container names use the `prod` environment:
- Development: `content-liseli-dev`, `content-dev`
- Production: `content-liseli-prod`, `content-prod`

Update the migration or create new content source records for production environments.

## Environment Variables

Ensure the following environment variables are set:

| Variable | Description | Example |
|----------|-------------|----------|
| `ENV` | Current environment | `dev`, `staging`, `prod` |
| `SUPABASE_URL` | Supabase instance URL | `https://xxx.supabase.co` |
| `SUPABASE_SERVICE_ROLE_KEY` | Service role key for Supabase Storage | `eyJ...` |
| `LISELI_AZURE_BLOB_CONNECTION` | Azure connection string | `DefaultEndpointsProtocol...` |

## Migration Considerations

When the environment changes (e.g., from dev to prod):

1. Update bucket/container names in the migration:
   ```sql
   UPDATE cs.content_source
   SET settings = jsonb_set(
     settings,
     '{container_name}',
     '"content-liseli-prod"'::jsonb
   )
   WHERE name = 'Liseli Azure Storage';
   ```

2. Create new migration for the environment change

3. Run migration: `npx supabase db push`

## Testing

To test storage for a new organization:

```typescript
// 1. Create organization with bucket name
const bucketName = `content-${orgSlug}-${env}`;

// 2. Upload a test file via cs-upload-content edge function
const uploadResponse = await fetch('/functions/v1/cs-upload-content', {
  method: 'POST',
  headers: { 'Authorization': `Bearer ${token}` },
  body: JSON.stringify({
    mime_type: 'image/jpeg',
    size_bytes: 1024,
    checksum: 'dGVzdA==',
    metadata: { test: true }
  })
});

// 3. Verify bucket was created lazily
// Check logs for: "Created bucket content-xxx-dev (public=false)"