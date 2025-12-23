-- Finance: purchase
-- NOTE: purchases are org-scoped indirectly via finance.receipt.org_id
DROP POLICY IF EXISTS "Allow read for self or admin" ON finance.purchase;
create policy "Allow read for self or admin" on finance.purchase for select using (
  is_active = true
  and exists (
    select 1
    from finance.receipt r
    where r.id = finance.purchase.receipt_id
      and r.org_id = identity.current_org_id()
  )
  and (
    ( (auth.uid())::uuid = created_by and identity.authorize('finance.purchase.read') )
    or identity.authorize('finance.purchase.admin')
  )
);

DROP POLICY IF EXISTS "Allow insert for self or admin" ON finance.purchase;
CREATE POLICY "Allow insert for self or admin" ON finance.purchase FOR INSERT WITH CHECK (
  exists (
    select 1
    from finance.receipt r
    where r.id = finance.purchase.receipt_id
      and r.org_id = identity.current_org_id()
  )
  and (
    ( (auth.uid())::uuid = created_by AND identity.authorize('finance.purchase.insert') )
    OR identity.authorize('finance.purchase.admin')
  )
);

DROP POLICY IF EXISTS "Allow update for self or admin" ON finance.purchase;
create policy "Allow update for self or admin" on finance.purchase
FOR UPDATE
USING (
  is_active = true
  and exists (
    select 1
    from finance.receipt r
    where r.id = finance.purchase.receipt_id
      and r.org_id = identity.current_org_id()
  )
  and (
    ( (auth.uid())::uuid = created_by AND identity.authorize('finance.purchase.update') )
    OR identity.authorize('finance.purchase.admin')
  )
)
WITH CHECK (
  exists (
    select 1
    from finance.receipt r
    where r.id = finance.purchase.receipt_id
      and r.org_id = identity.current_org_id()
  )
  and (
    ( (auth.uid())::uuid = created_by AND identity.authorize('finance.purchase.update') )
    OR identity.authorize('finance.purchase.admin')
  )
);

DROP POLICY IF EXISTS "Allow soft delete for self or admin" ON finance.purchase;
create policy "Allow soft delete for self or admin" on finance.purchase
FOR UPDATE
USING (
  is_active = true
  and exists (
    select 1
    from finance.receipt r
    where r.id = finance.purchase.receipt_id
      and r.org_id = identity.current_org_id()
  )
  and (
    ( (auth.uid())::uuid = created_by AND identity.authorize('finance.purchase.delete') )
    OR identity.authorize('finance.purchase.admin')
  )
)
WITH CHECK (
  exists (
    select 1
    from finance.receipt r
    where r.id = finance.purchase.receipt_id
      and r.org_id = identity.current_org_id()
  )
  and (
    ( (auth.uid())::uuid = created_by AND is_active = false AND identity.authorize('finance.purchase.delete') )
    OR identity.authorize('finance.purchase.admin')
  )
);

-- Finance: receipt
DROP POLICY IF EXISTS "Allow read for self or admin" ON finance.receipt;
create policy "Allow read for self or admin" on finance.receipt for select using (
  is_active = true
  and org_id = identity.current_org_id()
  and (
    ( (auth.uid())::uuid = created_by and identity.authorize('finance.receipt.read') )
    or identity.authorize('finance.receipt.admin')
  )
);

DROP POLICY IF EXISTS "Allow insert for self or admin" ON finance.receipt;
CREATE POLICY "Allow insert for self or admin" ON finance.receipt FOR INSERT WITH CHECK (
  org_id = identity.current_org_id()
  and (
    ( (auth.uid())::uuid = created_by AND identity.authorize('finance.receipt.insert') )
    OR identity.authorize('finance.receipt.admin')
  )
);

DROP POLICY IF EXISTS "Allow update for self or admin" ON finance.receipt;
create policy "Allow update for self or admin" on finance.receipt
FOR UPDATE
USING (
  is_active = true
  and org_id = identity.current_org_id()
  and (
    ( (auth.uid())::uuid = created_by AND identity.authorize('finance.receipt.update') )
    OR identity.authorize('finance.receipt.admin')
  )
)
WITH CHECK (
  org_id = identity.current_org_id()
  and (
    ( (auth.uid())::uuid = created_by AND identity.authorize('finance.receipt.update') )
    OR identity.authorize('finance.receipt.admin')
  )
);

DROP POLICY IF EXISTS "Allow soft delete for self or admin" ON finance.receipt;
create policy "Allow soft delete for self or admin" on finance.receipt
FOR UPDATE
USING (
  is_active = true
  and org_id = identity.current_org_id()
  and (
    ( (auth.uid())::uuid = created_by AND identity.authorize('finance.receipt.delete') )
    OR identity.authorize('finance.receipt.admin')
  )
)
WITH CHECK (
  org_id = identity.current_org_id()
  and (
    ( (auth.uid())::uuid = created_by AND is_active = false AND identity.authorize('finance.receipt.delete') )
    OR identity.authorize('finance.receipt.admin')
  )
);

-- Finance: expense_category (org-scoped reference data)
DROP POLICY IF EXISTS "Allow read for self or admin" ON finance.expense_category;
create policy "Allow read for self or admin" on finance.expense_category for select using (
  is_active = true
  and org_id = identity.current_org_id()
  and (
    ( auth.role() = 'authenticated' and identity.authorize('finance.expense_category.read') )
    or identity.authorize('finance.expense_category.admin')
  )
);

DROP POLICY IF EXISTS "Allow insert for self or admin" ON finance.expense_category;
create policy "Allow insert for self or admin" on finance.expense_category for insert with check (
  org_id = identity.current_org_id()
  and identity.authorize('finance.expense_category.admin')
);

DROP POLICY IF EXISTS "Allow update for admin only" ON finance.expense_category;
create policy "Allow update for admin only" on finance.expense_category
FOR UPDATE USING (
  org_id = identity.current_org_id()
  and identity.authorize('finance.expense_category.admin')
  and is_active = true
) WITH CHECK (
  org_id = identity.current_org_id()
  and identity.authorize('finance.expense_category.admin')
  and is_active = true
);

DROP POLICY IF EXISTS "Allow soft delete for admin only" ON finance.expense_category;
create policy "Allow soft delete for admin only" on finance.expense_category
FOR UPDATE USING (
  org_id = identity.current_org_id()
  and identity.authorize('finance.expense_category.admin')
  and is_active = true
) WITH CHECK (
  org_id = identity.current_org_id()
  and identity.authorize('finance.expense_category.admin')
  and is_active = false
);

-- Finance: expense_type (org-scoped reference data)
DROP POLICY IF EXISTS "Allow read for self or admin" ON finance.expense_type;
create policy "Allow read for self or admin" on finance.expense_type for select using (
  is_active = true
  and org_id = identity.current_org_id()
  and (
    ( auth.role() = 'authenticated' and identity.authorize('finance.expense_type.read') )
    or identity.authorize('finance.expense_type.admin')
  )
);

DROP POLICY IF EXISTS "Allow insert for self or admin" ON finance.expense_type;
create policy "Allow insert for self or admin" on finance.expense_type for insert with check (
  org_id = identity.current_org_id()
  and identity.authorize('finance.expense_type.admin')
);

DROP POLICY IF EXISTS "Allow update for admin only" ON finance.expense_type;
create policy "Allow update for admin only" on finance.expense_type
FOR UPDATE USING (
  org_id = identity.current_org_id()
  and identity.authorize('finance.expense_type.admin')
  and is_active = true
) WITH CHECK (
  org_id = identity.current_org_id()
  and identity.authorize('finance.expense_type.admin')
  and is_active = true
);

DROP POLICY IF EXISTS "Allow soft delete for admin only" ON finance.expense_type;
create policy "Allow soft delete for admin only" on finance.expense_type
FOR UPDATE USING (
  org_id = identity.current_org_id()
  and identity.authorize('finance.expense_type.admin')
  and is_active = true
) WITH CHECK (
  org_id = identity.current_org_id()
  and identity.authorize('finance.expense_type.admin')
  and is_active = false
);

-- Finance: currency (org-scoped reference data)
DROP POLICY IF EXISTS "Allow read for self or admin" ON finance.currency;
create policy "Allow read for self or admin" on finance.currency for select using (
  is_active = true
  and org_id = identity.current_org_id()
  and (
    ( auth.role() = 'authenticated' and identity.authorize('finance.currency.read') )
    or identity.authorize('finance.currency.admin')
  )
);

DROP POLICY IF EXISTS "Allow insert for self or admin" ON finance.currency;
create policy "Allow insert for self or admin" on finance.currency for insert with check (
  org_id = identity.current_org_id()
  and identity.authorize('finance.currency.admin')
);

DROP POLICY IF EXISTS "Allow update for admin only" ON finance.currency;
create policy "Allow update for admin only" on finance.currency
FOR UPDATE USING (
  org_id = identity.current_org_id()
  and identity.authorize('finance.currency.admin')
  and is_active = true
) WITH CHECK (
  org_id = identity.current_org_id()
  and identity.authorize('finance.currency.admin')
  and is_active = true
);

DROP POLICY IF EXISTS "Allow soft delete for admin only" ON finance.currency;
create policy "Allow soft delete for admin only" on finance.currency
FOR UPDATE USING (
  org_id = identity.current_org_id()
  and identity.authorize('finance.currency.admin')
  and is_active = true
) WITH CHECK (
  org_id = identity.current_org_id()
  and identity.authorize('finance.currency.admin')
  and is_active = false
);
