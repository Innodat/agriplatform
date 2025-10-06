BEGIN;
-- 1) Ensure auth.users entries exist (use deterministic UUIDs)
INSERT INTO auth.users (id, raw_app_meta_data, raw_user_meta_data, created_at) VALUES ('11111111-1111-1111-1111-111111111111', '{}'::jsonb, '{}'::jsonb, now()), -- system
('22222222-2222-2222-2222-222222222222', '{}'::jsonb, '{}'::jsonb, now()) -- migrate
ON CONFLICT (id) DO NOTHING;

-- 3) Upsert identity.users referencing the auth.user ids
-- Upsert identity.users using id as the conflict target (updates when id exists)
WITH vals(actor_key_val, username_val, id_val) AS (
  VALUES
    ('system', 'System', '11111111-1111-1111-1111-111111111111'::uuid),
    ('migrate', 'Migrate', '22222222-2222-2222-2222-222222222222'::uuid)
)
INSERT INTO identity.users (id, actor_key, is_system, username, created_by, updated_by, created_at, updated_at)
SELECT id_val, actor_key_val, true, username_val, NULL, NULL, now(), now()
FROM vals
ON CONFLICT (id)
DO UPDATE SET
  actor_key = EXCLUDED.actor_key,
  is_system = EXCLUDED.is_system,
  username = EXCLUDED.username,
  updated_at = now()
RETURNING id;