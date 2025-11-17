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
  user_role identity.app_role;
  role_ids_array bigint[];
  role_ids_json jsonb;
begin
  -- Ensure claims object exists
  claims := coalesce(event->'claims', '{}'::jsonb);

  -- Query active roles for this user
  select 
    array_agg(ur.id) filter (where ur.is_active = true),
    (array_agg(ur.role) filter (where ur.is_active = true))[1]
  into 
    role_ids_array,
    user_role
  from identity.user_roles ur
  where ur.user_id = (event->>'user_id')::uuid
    and ur.is_active = true;

  -- Convert role_ids array to jsonb
  role_ids_json := coalesce(to_jsonb(role_ids_array), '[]'::jsonb);

  -- Set the claims
  if user_role is not null then
    claims := jsonb_set(claims, '{user_role}', to_jsonb(user_role));
  else 
    claims := jsonb_set(claims, '{user_role}', 'null'::jsonb);
  end if;

  claims := jsonb_set(claims, '{role_ids}', role_ids_json);
  claims := jsonb_set(claims, '{department_ids}', '[]'::jsonb); -- Placeholder

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

grant all
  on table identity.user_roles
to supabase_auth_admin;

revoke all
  on table identity.user_roles
  from authenticated, anon;

create policy "Allow auth admin to read user roles" ON identity.user_roles
as permissive for select
to supabase_auth_admin
using (true)
