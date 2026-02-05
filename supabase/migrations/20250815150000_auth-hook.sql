/**
 * AUTH HOOKS
 * Create an auth hook to add a custom claim to the access token jwt.
 */

-- Create the auth hook function
-- https://supabase.com/docs/guides/auth/auth-hooks#hook-custom-access-token
create or replace function identity.custom_access_token_hook(
  event jsonb
) returns jsonb
language plpgsql
security definer
set search_path = public, pg_temp
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
  -- Ensure claims object exists
  claims := coalesce(event->'claims', '{}'::jsonb);

  -- Determine current org from user_metadata or first membership
  current_org_id := coalesce(
    (event->'user_metadata'->>'current_org_id')::uuid,
    (
      select om.org_id
      from identity.org_member om
      where om.user_id = (event->>'user_id')::uuid
        and om.deleted_at IS NULL
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

  if current_org_id is not null then
    select om.id, om.is_owner
      into current_member_id, is_owner
    from identity.org_member om
    where om.user_id = (event->>'user_id')::uuid
      and om.org_id = current_org_id
      and om.deleted_at IS NULL;
  end if;

  if current_member_id is not null then
    select
      array_agg(mr.role) filter (where mr.deleted_at IS NULL),
      array_agg(mr.id) filter (where mr.deleted_at IS NULL)
    into user_roles_arr, role_ids_arr
    from identity.member_role mr
    where mr.member_id = current_member_id
      and mr.deleted_at IS NULL;
  end if;

  select array_agg(om.org_id)
    into org_ids_arr
  from identity.org_member om
  where om.user_id = (event->>'user_id')::uuid
    and om.deleted_at IS NULL;

  claims := jsonb_set(claims, '{org_id}', coalesce(to_jsonb(current_org_id), 'null'::jsonb));
  claims := jsonb_set(claims, '{org_slug}', coalesce(to_jsonb(org_slug), 'null'::jsonb));
  claims := jsonb_set(claims, '{member_id}', coalesce(to_jsonb(current_member_id), 'null'::jsonb));
  claims := jsonb_set(claims, '{user_roles}', coalesce(to_jsonb(user_roles_arr), '[]'::jsonb));
  claims := jsonb_set(claims, '{role_ids}', coalesce(to_jsonb(role_ids_arr), '[]'::jsonb));
  claims := jsonb_set(claims, '{org_ids}', coalesce(to_jsonb(org_ids_arr), '[]'::jsonb));
  claims := jsonb_set(claims, '{is_org_owner}', to_jsonb(coalesce(is_owner, false)));

  claims := jsonb_set(claims, '{department_ids}', '[]'::jsonb); -- Placeholder
  -- Legacy: we no longer set single user_role claim (multi-role now lives in user_roles[])
  -- role_ids, user_roles, org context are set above.

  -- Update the 'claims' object in the original event
  event := jsonb_set(event, '{claims}', claims);

  -- Return the modified event
  return event;
end;
$$;

grant usage on schema identity to supabase_auth_admin;

grant execute
  on function identity.custom_access_token_hook
  to supabase_auth_admin;

revoke execute
  on function identity.custom_access_token_hook
  from authenticated, anon;

-- NOTE: identity.user_roles was removed. Grants/policies are now applied to org_member/member_role in
-- supabase/migrations/20251222163200_multitenancy_orgs.sql
