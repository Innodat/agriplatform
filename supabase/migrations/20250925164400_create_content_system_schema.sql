-- Create Content System (CS) schema for hexagonal content management
CREATE SCHEMA IF NOT EXISTS cs;

-- Content source table (Supabase, Azure Blob, S3, etc.)
CREATE TABLE cs.content_source (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  provider text NOT NULL CHECK (provider IN ('azure_blob', 'supabase_storage')),
  name text NOT NULL,
  settings jsonb NOT NULL, -- Azure account/container/credential config
  deleted_at timestamptz DEFAULT NULL,
  created_by uuid references identity.users(id) on delete set null DEFAULT auth.uid(),
  created_at timestamptz DEFAULT now(),
  updated_by uuid references identity.users(id) on delete set null,
  updated_at timestamptz DEFAULT now()
);

-- Content store table (actual content metadata)
CREATE TABLE cs.content_store (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  source_id uuid NOT NULL REFERENCES cs.content_source(id) ON DELETE RESTRICT,
  external_key text NOT NULL, -- blob path or object key
  mime_type text NOT NULL,
  size_bytes bigint,
  checksum text,
  metadata jsonb, -- EXIF, dimensions, etc.
  deleted_at timestamptz DEFAULT NULL,
  created_by uuid references identity.users(id) on delete set null DEFAULT auth.uid(),
  created_at timestamptz DEFAULT now(),
  updated_by uuid references identity.users(id) on delete set null,
  updated_at timestamptz DEFAULT now()
);

-- Receipt-content mapping on the finance.receipt table
ALTER TABLE finance.receipt
ADD COLUMN content_id uuid
REFERENCES cs.content_store(id) ON DELETE CASCADE;

-- Indexes for performance
CREATE INDEX idx_content_store_source_id ON cs.content_store(source_id);
CREATE INDEX idx_content_store_created_by ON cs.content_store(created_by);

-- Enable RLS on all CS tables
ALTER TABLE cs.content_source ENABLE ROW LEVEL SECURITY;
ALTER TABLE cs.content_store ENABLE ROW LEVEL SECURITY;


GRANT usage ON SCHEMA cs TO service_role;
GRANT all ON TABLE cs.content_source TO service_role;
GRANT all ON TABLE cs.content_store TO service_role;

-- Grants to authenticated users (RLS policies control actual access)
GRANT USAGE ON SCHEMA cs TO authenticated;
GRANT SELECT ON ALL TABLES IN SCHEMA cs TO authenticated;
ALTER DEFAULT PRIVILEGES IN SCHEMA cs
  GRANT SELECT ON TABLES TO authenticated;

-- RLS Policies
-- content_source: Admin only
CREATE POLICY "Admin can manage content sources" ON cs.content_source
  FOR ALL USING (auth.jwt() ->> 'role' = 'admin');

-- Create policy for service role (edge functions use service role client)
CREATE POLICY "Service role can manage content sources" ON cs.content_source
  FOR ALL
  TO service_role
  USING (true)
  WITH CHECK (true);

-- Insert default Azure Blob source (placeholder settings)
INSERT INTO cs.content_source (provider, name, settings) VALUES (
  'azure_blob',
  'Liseli Azure Storage',
  '{
    "account_name": "liseliblob",
    "container_name": "content-liseli-dev",
    "connection_secret": "LISELI_AZURE_BLOB_CONNECTION"
  }'::jsonb
), (
  'supabase_storage',
  'Default Supabase Storage',
  '{
    "bucket_name": "content-dev",
    "connection_secret": "SUPABASE_SERVICE_ROLE_KEY"
  }'::jsonb
) ON CONFLICT DO NOTHING;
