-- 1) Ensure auth.users entries exist (use deterministic UUIDs)
INSERT INTO auth.users (id, raw_app_meta_data, raw_user_meta_data, created_at) VALUES ('11111111-1111-1111-1111-111111111111', '{}'::jsonb, '{}'::jsonb, now()), -- system
('22222222-2222-2222-2222-222222222222', '{}'::jsonb, '{}'::jsonb, now()) -- migrate
ON CONFLICT (id) DO NOTHING;

-- 3) Upsert identity.users referencing the auth.user ids
-- Upsert identity.users using id as the conflict target (updates when id exists)
WITH vals(actor_key_val, username_val, id_val, is_platform_admin_val) AS (
  VALUES
    ('system', 'System', '11111111-1111-1111-1111-111111111111'::uuid, true),
    ('migrate', 'Migrate', '22222222-2222-2222-2222-222222222222'::uuid, true)
)
INSERT INTO identity.users (id, actor_key, is_system, username, is_platform_admin, created_by, updated_by, created_at, updated_at)
SELECT id_val, actor_key_val, true, username_val, is_platform_admin_val, NULL, NULL, now(), now()
FROM vals
ON CONFLICT (id)
DO UPDATE SET
  actor_key = EXCLUDED.actor_key,
  is_system = EXCLUDED.is_system,
  username = EXCLUDED.username,
  is_platform_admin = EXCLUDED.is_platform_admin,
  updated_at = now()
RETURNING id;

-- 4) Ensure a default org and membership exist for local development/testing
INSERT INTO identity.org (name, slug, created_by, updated_by)
VALUES (
  'Kok Home',
  'kok-home',
  '11111111-1111-1111-1111-111111111111'::uuid,
  '11111111-1111-1111-1111-111111111111'::uuid
)
ON CONFLICT (slug) DO UPDATE
  SET name = EXCLUDED.name,
      updated_at = now(),
      updated_by = EXCLUDED.updated_by;

-- Make the system user a member + owner of the default org
INSERT INTO identity.org_member (org_id, user_id, is_owner, created_by, updated_by)
VALUES (
  (select id from identity.org where slug = 'kok-home'),
  '11111111-1111-1111-1111-111111111111'::uuid,
  true,
  '11111111-1111-1111-1111-111111111111'::uuid,
  '11111111-1111-1111-1111-111111111111'::uuid
)
ON CONFLICT (org_id, user_id) DO UPDATE
  SET is_owner = true,
      is_active = true,
      updated_at = now(),
      updated_by = EXCLUDED.updated_by;

-- Assign admin role to the system user's membership
INSERT INTO identity.member_role (member_id, role, is_active, created_by, updated_by)
VALUES (
  (select id from identity.org_member where org_id = (select id from identity.org where slug = 'kok-home') and user_id = '11111111-1111-1111-1111-111111111111'::uuid),
  'admin'::identity.app_role,
  true,
  '11111111-1111-1111-1111-111111111111'::uuid,
  '11111111-1111-1111-1111-111111111111'::uuid
)
ON CONFLICT (member_id, role) DO UPDATE
  SET is_active = true,
      updated_at = now(),
      updated_by = EXCLUDED.updated_by;
