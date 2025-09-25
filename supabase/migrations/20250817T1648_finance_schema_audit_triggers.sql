-- Finance Schema Migration: Move tables, add supplier/status, implement centralized audit triggers
-- Migration: 20250817T1648_finance_schema_audit_triggers

-- Create finance schema and move tables
create schema if not exists finance;

-- Move tables from public to finance schema (idempotent)
do $$
begin
  if exists (select 1 from information_schema.tables where table_schema='public' and table_name='expense_category') then
    execute 'alter table public.expense_category set schema finance';
  end if;
  if exists (select 1 from information_schema.tables where table_schema='public' and table_name='expense_type') then
    execute 'alter table public.expense_type set schema finance';
  end if;
  if exists (select 1 from information_schema.tables where table_schema='public' and table_name='currency') then
    execute 'alter table public.currency set schema finance';
  end if;
  if exists (select 1 from information_schema.tables where table_schema='public' and table_name='receipt') then
    execute 'alter table public.receipt set schema finance';
  end if;
  if exists (select 1 from information_schema.tables where table_schema='public' and table_name='purchase') then
    execute 'alter table public.purchase set schema finance';
  end if;
end$$;

-- Add supplier column to receipt + index
alter table finance.receipt add column if not exists supplier text;
create index if not exists idx_finance_receipt_supplier on finance.receipt (supplier);

-- Create purchase status enum and add status column
do $$
begin
  if not exists (
    select 1 from pg_type t join pg_namespace n on n.oid=t.typnamespace
    where t.typname='purchase_status' and n.nspname='finance'
  ) then
    create type finance.purchase_status as enum ('pending','approved','rejected');
  end if;
end$$;

alter table finance.purchase add column if not exists status finance.purchase_status not null default 'pending';

-- Create centralized audit functions (schema-agnostic)
create or replace function actor_name()
returns text as $$
begin
  return coalesce(
    current_setting('app.actor_override', true),
    (current_setting('request.jwt.claims', true)::json -> 'user_metadata' ->> 'name'),
    (current_setting('request.jwt.claims', true)::json ->> 'email'),
    current_user,
    'system'
  );
end;
$$ language plpgsql;

create or replace function set_audit_fields()
returns trigger as $$
begin
  if tg_op = 'INSERT' then
    new.created_user_id := coalesce(new.created_user_id, actor_name());
    new.modified_user_id := new.created_user_id;
    new.created_timestamp := coalesce(new.created_timestamp, now());
    new.modified_timestamp := now();
  elsif tg_op = 'UPDATE' then
    new.modified_user_id := actor_name();
    new.modified_timestamp := now();
  end if;
  return new;
end;
$$ language plpgsql;

-- Attach audit triggers to finance tables
do $$
declare r record;
begin
  for r in
    select table_schema, table_name
    from information_schema.tables
    where table_schema='finance' and table_name in ('receipt','purchase','expense_type','expense_category','currency')
  loop
    execute format('drop trigger if exists trg_%I_%I_audit on %I.%I;', r.table_schema, r.table_name, r.table_schema, r.table_name);
    execute format('create trigger trg_%I_%I_audit before insert or update on %I.%I for each row execute function set_audit_fields();', r.table_schema, r.table_name, r.table_schema, r.table_name);
  end loop;
end$$;

-- Bootstrap: attach triggers to any existing table with all 4 audit columns
do $$
declare r record;
begin
  for r in
    select c.table_schema, c.table_name
    from information_schema.columns c
    where c.column_name in ('created_user_id','modified_user_id','created_timestamp','modified_timestamp')
    group by c.table_schema, c.table_name
    having count(*) = 4
  loop
    execute format('drop trigger if exists trg_%I_%I_audit on %I.%I;', r.table_schema, r.table_name, r.table_schema, r.table_name);
    execute format('create trigger trg_%I_%I_audit before insert or update on %I.%I for each row execute function set_audit_fields();', r.table_schema, r.table_name, r.table_schema, r.table_name);
  end loop;
end$$;
