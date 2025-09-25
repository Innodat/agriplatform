/**
 * AUTH HOOKS
 * Create an auth hook to add a custom claim to the access token jwt.
 */

-- Create the auth hook function
-- https://supabase.com/docs/guides/auth/auth-hooks#hook-custom-access-token
create or replace function identity.custom_access_token_hook(event jsonb)
returns jsonb
language plpgsql
stable
as $$
  declare
    claims jsonb;
    user_role identity.app_role;
  begin
    -- Check if the user is marked as admin in the profiles table
    select role into user_role from identity.user_roles where user_id = (event->>'user_id')::uuid;

    claims := event->'claims';

    if user_role is not null then
      -- Set the claim
      claims := jsonb_set(claims, '{user_role}', to_jsonb(user_role));
    else 
      claims := jsonb_set(claims, '{user_role}', 'null');
    end if;

    -- Update the 'claims' object in the original event
    event := jsonb_set(event, '{claims}', claims);

    -- Return the modified or original event
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