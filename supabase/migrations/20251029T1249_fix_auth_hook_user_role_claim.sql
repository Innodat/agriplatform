/**
 * FIX: Update auth hook to properly populate user_role claim in JWT
 * 
 * Issue: The previous auth hook was not properly setting the user_role claim,
 * causing 403 errors when accessing finance schema tables due to RLS policies
 * expecting the claim.
 * 
 * Changes:
 * - Ensure claims object exists with coalesce
 * - Query only active roles (is_active = true)
 * - Populate user_role with first active role
 * - Add role_ids array for future use
 * - Add department_ids placeholder for future department mapping
 */

-- Drop and recreate the auth hook function with proper claim population
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

-- Ensure proper grants are in place (idempotent)
grant usage on schema identity to supabase_auth_admin;

grant execute
  on function identity.custom_access_token_hook
  to supabase_auth_admin;

revoke execute
  on function identity.custom_access_token_hook
  from authenticated, anon;
