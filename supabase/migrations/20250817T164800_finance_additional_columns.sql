-- Finance Schema Migration: Move tables, add supplier/status, implement centralized audit triggers
-- Migration: 20250817T1648_finance_schema_audit_triggers


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
    create type finance.purchase_status as enum ('pending','querying','approved','rejected');
  end if;
end$$;

alter table finance.purchase add column if not exists status finance.purchase_status not null default 'pending';

