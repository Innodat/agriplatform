"""Exclude retired organizations from legacy Auth membership claims."""
from alembic import op

revision = 'identity_0010'
down_revision = 'identity_0009'
branch_labels = None
depends_on = None

TOKEN_HOOK_SQL = r"""
CREATE OR REPLACE FUNCTION identity.custom_access_token_hook(
  event jsonb
) returns jsonb
language plpgsql
security definer
SET search_path = pg_catalog, pg_temp
as $$
declare
  claims jsonb;
  current_org_id uuid;
  current_member_id bigint;
  user_roles_arr identity.app_role[];
  role_ids_arr bigint[];
  org_ids_arr uuid[];
  is_owner boolean;
  org_slug text;
begin
  claims := coalesce(event->'claims', '{}'::jsonb);

  -- Determine current org
  current_org_id := coalesce(
    (event->'user_metadata'->>'current_org_id')::uuid,
    (
      select om.org_id
      from identity.org_member om
      join identity.org o on o.id = om.org_id
      where om.user_id = (event->>'user_id')::uuid
        and om.deleted_at IS NULL
        and o.deleted_at IS NULL
      order by om.is_owner desc, om.created_at asc
      limit 1
    )
  );

  if current_org_id is not null then
    select o.slug
      into org_slug
    from identity.org o
    where o.id = current_org_id
      and o.deleted_at IS NULL;
  end if;

  -- Membership for current org
  if current_org_id is not null then
    select om.id, om.is_owner
      into current_member_id, is_owner
    from identity.org_member om
    join identity.org o on o.id = om.org_id
    where om.user_id = (event->>'user_id')::uuid
      and om.org_id = current_org_id
      and om.deleted_at IS NULL
      and o.deleted_at IS NULL;
  end if;

  -- Roles for membership
  if current_member_id is not null then
    select
      array_agg(mr.role) filter (where mr.deleted_at IS NULL),
      array_agg(mr.id) filter (where mr.deleted_at IS NULL)
    into user_roles_arr, role_ids_arr
    from identity.member_role mr
    where mr.member_id = current_member_id
      and mr.deleted_at IS NULL;
  end if;

  -- All org memberships
  select array_agg(om.org_id)
    into org_ids_arr
  from identity.org_member om
  join identity.org o on o.id = om.org_id
  where om.user_id = (event->>'user_id')::uuid
    and om.deleted_at IS NULL
    and o.deleted_at IS NULL;

  claims := jsonb_set(claims, '{org_id}', coalesce(to_jsonb(current_org_id), 'null'::jsonb));
  claims := jsonb_set(claims, '{org_slug}', coalesce(to_jsonb(org_slug), 'null'::jsonb));
  claims := jsonb_set(claims, '{member_id}', coalesce(to_jsonb(current_member_id), 'null'::jsonb));
  claims := jsonb_set(claims, '{user_roles}', coalesce(to_jsonb(user_roles_arr), '[]'::jsonb));
  claims := jsonb_set(claims, '{role_ids}', coalesce(to_jsonb(role_ids_arr), '[]'::jsonb));
  claims := jsonb_set(claims, '{org_ids}', coalesce(to_jsonb(org_ids_arr), '[]'::jsonb));
  claims := jsonb_set(claims, '{is_org_owner}', to_jsonb(coalesce(is_owner, false)));

  -- Update event
  event := jsonb_set(event, '{claims}', claims);
  return event;
end;
$$;
"""


def upgrade():
    # Preserve function identity, existing owner and ACL/effective permissions.
    op.get_bind().exec_driver_sql(TOKEN_HOOK_SQL, execution_options={'no_parameters': True})


def downgrade():
    raise RuntimeError('Destructive rollback is not supported; use the recovery runbook')
