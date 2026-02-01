-- 1) Ensure auth.users entries exist (use deterministic UUIDs)
INSERT INTO auth.users (id, raw_app_meta_data, raw_user_meta_data, created_at) VALUES ('11111111-1111-1111-1111-111111111111'::uuid, '{}'::jsonb, '{}'::jsonb, now()), -- system
('22222222-2222-2222-2222-222222222222'::uuid, '{}'::jsonb, '{}'::jsonb, now()); -- migrate

-- 2) Update identity.users (system users)
-- Note: on_auth_user_created trigger creates these automatically, so we update existing rows
UPDATE identity.users
SET 
  actor_key = 'system',
  is_system = true,
  username = 'System',
  is_platform_admin = true,
  updated_at = now()
WHERE id = '11111111-1111-1111-1111-111111111111'::uuid;

UPDATE identity.users
SET 
  actor_key = 'migrate',
  is_system = true,
  username = 'Migrate',
  is_platform_admin = true,
  updated_at = now()
WHERE id = '22222222-2222-2222-2222-222222222222'::uuid;

-- 4) Ensure a default org and membership exist for local development/testing
INSERT INTO identity.org (name, slug, created_by, updated_by)
VALUES (
  'Kok Home',
  'kok-home',
  '11111111-1111-1111-1111-111111111111'::uuid,
  '11111111-1111-1111-1111-111111111111'::uuid
);

-- Make the system user a member + owner of the default org
INSERT INTO identity.org_member (org_id, user_id, is_owner, created_by, updated_by)
VALUES (
  (select id from identity.org where slug = 'kok-home'),
  '11111111-1111-1111-1111-111111111111'::uuid,
  true,
  '11111111-1111-1111-1111-111111111111'::uuid,
  '11111111-1111-1111-1111-111111111111'::uuid
);

-- Assign admin role to the system user's membership
INSERT INTO identity.member_role (member_id, role, created_by, updated_by)
VALUES (
  (select id from identity.org_member where org_id = (select id from identity.org where slug = 'kok-home') and user_id = '11111111-1111-1111-1111-111111111111'::uuid),
  'admin'::identity.app_role,
  '11111111-1111-1111-1111-111111111111'::uuid,
  '11111111-1111-1111-1111-111111111111'::uuid
);