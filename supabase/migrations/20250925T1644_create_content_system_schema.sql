-- Create Content System (CS) schema for hexagonal content management
CREATE SCHEMA IF NOT EXISTS cs;

-- Content source table (Azure Blob, future: S3, etc.)
CREATE TABLE cs.content_source (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  provider text NOT NULL CHECK (provider IN ('azure_blob')),
  name text NOT NULL,
  settings jsonb NOT NULL, -- Azure account/container/credential config
  is_active boolean NOT NULL DEFAULT true,
  created_by VARCHAR,
  created_at timestamptz DEFAULT now(),
  updated_by VARCHAR,
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
  created_by VARCHAR,
  created_at timestamptz DEFAULT now(),
  updated_by VARCHAR,
  updated_at timestamptz DEFAULT now()
);

-- Receipt-content mapping on the finance.receipt table
ALTER TABLE finance.receipt
ADD COLUMN content_id uuid
REFERENCES cs.content_store(id) ON DELETE CASCADE;

-- Indexes for performance
CREATE INDEX idx_content_store_source_id ON cs.content_store(source_id);
CREATE INDEX idx_content_store_created_by ON cs.content_store(created_by);
CREATE INDEX idx_receipt_content_receipt_id ON cs.receipt_content(receipt_id);
CREATE INDEX idx_receipt_content_content_id ON cs.receipt_content(content_id);

-- Enable RLS on all CS tables
ALTER TABLE cs.content_source ENABLE ROW LEVEL SECURITY;
ALTER TABLE cs.content_store ENABLE ROW LEVEL SECURITY;
ALTER TABLE cs.receipt_content ENABLE ROW LEVEL SECURITY;

-- RLS Policies
-- content_source: Admin only
CREATE POLICY "Admin can manage content sources" ON cs.content_source
  FOR ALL USING (auth.jwt() ->> 'role' = 'admin');

-- content_store: Users can read content linked to their receipts or if admin
CREATE POLICY "Users can read own content" ON cs.content_store
  FOR SELECT USING (
    auth.jwt() ->> 'role' = 'admin' OR
    EXISTS (
      SELECT 1 FROM cs.receipt_content rc
      JOIN public.purchase p ON p.receipt_id = rc.receipt_id
      WHERE rc.content_id = content_store.id
      AND p.user_id = auth.uid()
    )
  );

CREATE POLICY "Users can insert content for own receipts" ON cs.content_store
  FOR INSERT WITH CHECK (
    created_by = auth.uid() AND
    EXISTS (
      SELECT 1 FROM public.receipt r
      JOIN public.purchase p ON p.receipt_id = r.id
      WHERE p.user_id = auth.uid()
    )
  );

-- receipt_content: Users can manage content for their receipts
CREATE POLICY "Users can manage receipt content" ON cs.receipt_content
  FOR ALL USING (
    auth.jwt() ->> 'role' = 'admin' OR
    EXISTS (
      SELECT 1 FROM public.purchase p
      WHERE p.receipt_id = receipt_content.receipt_id
      AND p.user_id = auth.uid()
    )
  );

-- Insert default Azure Blob source (placeholder settings)
INSERT INTO cs.content_source (provider, name, settings) VALUES (
  'azure_blob',
  'Liseli Azure Storage',
  '{
    "account_name": "PLACEHOLDER",
    "container_name": "receipts",
    "connection_secret", "LISELI_AZURE_STORAGE_CONNECTION"
  }'
);

create or replace function cs.resolve_secret(secret_name text)
returns text
language sql
security definer
as $$
  select decrypted_secret
  from vault.secrets
  where name = secret_name;
$$;

-- Lock it down: only allow your backend role to call it
revoke all on function cs.resolve_secret(text) from public;
grant execute on function cs.resolve_secret(text) to service_role;
