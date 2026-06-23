-- Multi-tenancy: Organizations + Memberships + Per-org roles
-- Date: 2025-12-22

begin;

-- org-scoped unique indexes for deterministic IDs
create unique index if not exists finance_currency_org_id_id_uniq
  on finance.currency (org_id, id);

create unique index if not exists finance_expense_category_org_id_id_uniq
  on finance.expense_category (org_id, id);

create unique index if not exists finance_expense_type_org_id_id_uniq
  on finance.expense_type (org_id, id);


end;
$$;
commit;
