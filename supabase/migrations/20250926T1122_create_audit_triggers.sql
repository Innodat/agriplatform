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

-- Finance schema
create trigger audit_finance_purchase
before insert or update on finance.purchase
for each row execute function identity.set_audit_fields();

create trigger audit_finance_receipt
before insert or update on finance.receipt
for each row execute function identity.set_audit_fields();

create trigger audit_expense_category
before insert or update on finance.expense_category
for each row execute function identity.set_audit_fields();

create trigger audit_expense_type
before insert or update on finance.expense_type
for each row execute function identity.set_audit_fields();

create trigger audit_currency
before insert or update on finance.currency
for each row execute function identity.set_audit_fields();

-- Identity schema
create trigger audit_identity_users
before insert or update on identity.users
for each row execute function identity.set_audit_fields();

create trigger audit_identity_user_roles
before insert or update on identity.user_roles
for each row execute function identity.set_audit_fields();

create trigger audit_identity_role_permissions
before insert or update on identity.role_permissions
for each row execute function identity.set_audit_fields();
