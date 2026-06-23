-- Create centralized audit functions (schema-agnostic)
create or replace function identity.set_audit_fields()
returns trigger
language plpgsql
security definer
as $$
declare
  actor_id uuid;
begin
  -- Try to extract the authenticated user's ID from JWT claims
  actor_id := nullif(current_setting('request.jwt.claims', true)::json ->> 'sub', '');

  if tg_op = 'INSERT' then
    new.updated_by := actor_id;
  elsif tg_op = 'UPDATE' then
    new.updated_by := actor_id;
    new.updated_at := now();
  end if;

  return new;
end;
$$;

-- Identity schema
create trigger audit_identity_users
before insert or update on identity.users
for each row execute function identity.set_audit_fields();

-- NOTE: identity.user_roles removed in multi-tenancy refactor
-- create trigger audit_identity_user_roles
-- before insert or update on identity.user_roles
-- for each row execute function identity.set_audit_fields();

create trigger audit_identity_role_permissions
before insert or update on identity.role_permissions
for each row execute function identity.set_audit_fields();
