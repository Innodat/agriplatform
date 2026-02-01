
create or replace function finance.debug_perm(p text)
returns boolean
language sql
as $$
  select identity.authorize(p::identity.app_permission);
$$;
