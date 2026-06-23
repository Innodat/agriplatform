-- Add content versioning support for content store
-- Date: 2025-12-26

BEGIN;

-- Create content_version table to track previous versions when content is updated
CREATE TABLE cs.content_version (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  content_id uuid NOT NULL REFERENCES cs.content_store(id) ON DELETE CASCADE,
  version_number int NOT NULL,
  external_key text NOT NULL,
  mime_type text NOT NULL,
  size_bytes bigint,
  checksum text,
  metadata jsonb,
  replaced_at timestamptz NOT NULL DEFAULT now(),
  replaced_by uuid REFERENCES identity.users(id) ON DELETE SET NULL,
  UNIQUE(content_id, version_number)
);

COMMENT ON TABLE cs.content_version IS 'Tracks previous versions of content when updated. Enables rollback and archival features.';
COMMENT ON COLUMN cs.content_version.version_number IS 'Sequential version number starting from 1';
COMMENT ON COLUMN cs.content_version.external_key IS 'The blob/object key that was replaced';
COMMENT ON COLUMN cs.content_version.replaced_at IS 'When this version was replaced';
COMMENT ON COLUMN cs.content_version.replaced_by IS 'User who replaced this version';

-- Create indexes for performance
CREATE INDEX idx_content_version_content_id ON cs.content_version(content_id);
CREATE INDEX idx_content_version_replaced_at ON cs.content_version(replaced_at);

-- Enable RLS
ALTER TABLE cs.content_version ENABLE ROW LEVEL SECURITY;

-- Grant permissions to service_role
GRANT ALL ON TABLE cs.content_version TO service_role;

-- RLS Policy: Service role can manage all versions
CREATE POLICY "Service role can manage content versions" ON cs.content_version
  FOR ALL
  TO service_role
  USING (true)
  WITH CHECK (true);

-- Create Supabase Storage bucket for content
-- Note: This uses Supabase's storage.buckets table
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES (
  'content_kok-home_dev',
  'content_kok-home_dev',
  false, -- private bucket
  52428800, -- 50MB limit
  NULL -- allow all mime types
)
ON CONFLICT (id) DO NOTHING;

COMMENT ON TABLE cs.content_version IS 'Content versioning table - tracks historical versions when content is updated';

COMMIT;
