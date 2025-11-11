-- Create Content System (CS) schema for hexagonal content management
CREATE SCHEMA IF NOT EXISTS cs;

-- Content source table (Supabase, Azure Blob, S3, etc.)
CREATE TABLE cs.content_source (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  provider text NOT NULL CHECK (provider IN ('azure_blob')),
  name text NOT NULL,
  settings jsonb NOT NULL, -- Azure account/container/credential config
  is_active boolean NOT NULL DEFAULT true,
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
  is_active boolean NOT NULL DEFAULT true,
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

-- RLS Policies
-- content_source: Admin only
CREATE POLICY "Admin can manage content sources" ON cs.content_source
  FOR ALL USING (auth.jwt() ->> 'role' = 'admin');

-- Insert default Azure Blob source (placeholder settings)
INSERT INTO cs.content_source (provider, name, settings) VALUES (
  'azure_blob',
  'Liseli Azure Storage',
  '{
    "account_name": "liseliblob",
    "container_name": "content",
    "connection_secret": "LISELI_AZURE_BLOB_CONNECTION"
  }'
);
