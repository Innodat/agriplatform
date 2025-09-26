create table identity.audit_log (
  id uuid primary key default gen_random_uuid(),
  table_name text not null,
  record_id uuid not null,
  operation text not null, -- 'INSERT', 'UPDATE', 'DELETE'
  actor_id uuid,
  timestamp timestamptz default now(),
  diff jsonb,              -- full row snapshot or row-level diff
  column_changes jsonb     -- per-column changes: { column: {old, new} }
);

create or replace function identity.log_audit()
returns trigger
language plpgsql
security definer
as $$
declare
  actor_id uuid := nullif(current_setting('request.jwt.claims', true)::json ->> 'sub', '');
  row_diff jsonb;
  col_changes jsonb := '{}';
  key text;
begin
  if tg_op = 'INSERT' then
    row_diff := to_jsonb(new);

  elsif tg_op = 'UPDATE' then
    row_diff := jsonb_strip_nulls(to_jsonb(new) - to_jsonb(old));

    -- Build per-column change map
    for key in select jsonb_object_keys(row_diff)
    loop
      col_changes := col_changes || jsonb_build_object(
        key,
        jsonb_build_object(
          'old', to_jsonb(old) -> key,
          'new', to_jsonb(new) -> key
        )
      );
    end loop;

  elsif tg_op = 'DELETE' then
    row_diff := to_jsonb(old);
  end if;

  insert into identity.audit_log (
    table_name,
    record_id,
    operation,
    actor_id,
    diff,
    column_changes
  ) values (
    tg_table_name,
    coalesce(new.id, old.id),
    tg_op,
    actor_id,
    row_diff,
    nullif(col_changes, '{}')
  );

  return coalesce(new, old);
end;
$$;

create trigger audit_log_finance_purchase
after insert or update or delete on finance.purchase
for each row execute function identity.log_audit();

create trigger audit_log_finance_receipt
after insert or update or delete on finance.receipt
for each row execute function identity.log_audit();

create trigger audit_log_expense_category
after insert or update or delete on finance.expense_category
for each row execute function identity.log_audit();

create trigger audit_log_expense_type
after insert or update or delete on finance.expense_type
for each row execute function identity.log_audit();

create trigger audit_log_currency
after insert or update or delete on finance.currency
for each row execute function identity.log_audit();

create trigger audit_log_identity_users
after insert or update or delete on identity.users
for each row execute function identity.log_audit();

create trigger audit_log_identity_user_roles
after insert or update or delete on identity.user_roles
for each row execute function identity.log_audit();

create trigger audit_log_identity_role_permissions
after insert or update or delete on identity.role_permissions
for each row execute function identity.log_audit();
