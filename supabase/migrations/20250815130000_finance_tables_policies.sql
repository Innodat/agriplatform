-- Finance: purchase
DROP POLICY IF EXISTS "Allow read for self or admin" ON finance.purchase;
create policy "Allow read for self or admin" on finance.purchase for select using (
  ( (auth.uid())::uuid = created_by and identity.authorize('finance.purchase.read') and is_active = true )
  or identity.authorize('finance.purchase.admin')
);
DROP POLICY IF EXISTS "Allow insert for self or admin" ON finance.purchase;
CREATE POLICY "Allow insert for self or admin" ON finance.purchase FOR INSERT WITH CHECK (
    ( (auth.uid())::uuid = created_by AND identity.authorize('finance.purchase.insert') ) 
    OR identity.authorize('finance.purchase.admin')
);
DROP POLICY IF EXISTS "Allow update for self or admin" ON finance.purchase;
create policy "Allow update for self or admin" on finance.purchase
FOR UPDATE
USING (
    is_active = true AND 
    ( (auth.uid())::uuid = created_by AND identity.authorize('finance.purchase.update') )
    OR identity.authorize('finance.purchase.admin')
)
WITH CHECK (
    ( (auth.uid())::uuid = created_by AND identity.authorize('finance.purchase.update') )
    OR identity.authorize('finance.purchase.admin')
);
DROP POLICY IF EXISTS "Allow soft delete for self or admin" ON finance.purchase;
create policy "Allow soft delete for self or admin" on finance.purchase
FOR UPDATE
USING (
    is_active = true AND 
    ( (auth.uid())::uuid = created_by AND identity.authorize('finance.purchase.delete') )
    OR identity.authorize('finance.purchase.admin')
)
WITH CHECK (
    ( (auth.uid())::uuid = created_by AND is_active = false AND identity.authorize('finance.purchase.delete') )
    OR identity.authorize('finance.purchase.admin')
);

-- Finance: receipt
DROP POLICY IF EXISTS "Allow read for self or admin" ON finance.receipt;
create policy "Allow read for self or admin" on finance.receipt for select using (
  ( (auth.uid())::uuid = created_by and identity.authorize('finance.receipt.read') and is_active = true )
  or identity.authorize('finance.receipt.admin')
);
DROP POLICY IF EXISTS "Allow insert for self or admin" ON finance.receipt;
CREATE POLICY "Allow insert for self or admin" ON finance.receipt FOR INSERT WITH CHECK (
    ( (auth.uid())::uuid = created_by AND identity.authorize('finance.receipt.insert') ) 
    OR identity.authorize('finance.receipt.admin')
);
DROP POLICY IF EXISTS "Allow update for self or admin" ON finance.receipt;
create policy "Allow update for self or admin" on finance.receipt
FOR UPDATE
USING (
    is_active = true AND 
    ( (auth.uid())::uuid = created_by AND identity.authorize('finance.receipt.update') )
    OR identity.authorize('finance.receipt.admin')
)
WITH CHECK (
    ( (auth.uid())::uuid = created_by AND identity.authorize('finance.receipt.update') )
    OR identity.authorize('finance.receipt.admin')
);
DROP POLICY IF EXISTS "Allow soft delete for self or admin" ON finance.receipt;
create policy "Allow soft delete for self or admin" on finance.receipt
FOR UPDATE
USING (
    is_active = true AND 
    ( (auth.uid())::uuid = created_by AND identity.authorize('finance.receipt.delete') )
    OR identity.authorize('finance.receipt.admin')
)
WITH CHECK (
    ( (auth.uid())::uuid = created_by AND is_active = false AND identity.authorize('finance.receipt.delete') )
    OR identity.authorize('finance.receipt.admin')
);

-- Finance: expense_category
DROP POLICY IF EXISTS "Allow read for self or admin" ON finance.expense_category;
create policy "Allow read for self or admin" on finance.expense_category for select using (
  is_active = true AND (
    ( auth.role() = 'authenticated' and identity.authorize('finance.expense_category.read') )
    or identity.authorize('finance.expense_category.admin')
  )
);
DROP POLICY IF EXISTS "Allow insert for self or admin" ON finance.expense_category;
create policy "Allow insert for self or admin" on finance.expense_category for insert with check (
  identity.authorize('finance.expense_category.admin')
);
DROP POLICY IF EXISTS "Allow update for admin only" ON finance.expense_category;
create policy "Allow update for admin only" on finance.expense_category
FOR UPDATE USING (
    identity.authorize('finance.expense_category.admin') AND is_active = true
) WITH CHECK (
    identity.authorize('finance.expense_category.admin') AND is_active = true
);
DROP POLICY IF EXISTS "Allow soft delete for admin only" ON finance.expense_category;
create policy "Allow soft delete for admin only" on finance.expense_category
FOR UPDATE USING (
    identity.authorize('finance.expense_category.admin') AND is_active = true
) WITH CHECK (
    identity.authorize('finance.expense_category.admin') AND is_active = false
);

-- Finance: expense_type
DROP POLICY IF EXISTS "Allow read for self or admin" ON finance.expense_type;
create policy "Allow read for self or admin" on finance.expense_type for select using (
  is_active = true AND (
    ( auth.role() = 'authenticated' and identity.authorize('finance.expense_type.read') )
    or identity.authorize('finance.expense_type.admin')
  )
);
DROP POLICY IF EXISTS "Allow insert for self or admin" ON finance.expense_type;
create policy "Allow insert for self or admin" on finance.expense_type for insert with check (
  identity.authorize('finance.expense_type.admin')
);
DROP POLICY IF EXISTS "Allow update for admin only" ON finance.expense_type;
create policy "Allow update for admin only" on finance.expense_type
FOR UPDATE USING (
    identity.authorize('finance.expense_type.admin') AND is_active = true
) WITH CHECK (
    identity.authorize('finance.expense_type.admin') AND is_active = true
);
DROP POLICY IF EXISTS "Allow soft delete for admin only" ON finance.expense_type;
create policy "Allow soft delete for admin only" on finance.expense_type
FOR UPDATE USING (
    identity.authorize('finance.expense_type.admin') AND is_active = true
) WITH CHECK (
    identity.authorize('finance.expense_type.admin') AND is_active = false
);

-- Finance: currency
DROP POLICY IF EXISTS "Allow read for self or admin" ON finance.currency;
create policy "Allow read for self or admin" on finance.currency for select using (
  is_active = true AND (
    ( auth.role() = 'authenticated' and identity.authorize('finance.currency.read') )
    or identity.authorize('finance.currency.admin')
  )
);
DROP POLICY IF EXISTS "Allow insert for self or admin" ON finance.currency;
create policy "Allow insert for self or admin" on finance.currency for insert with check (
  identity.authorize('finance.currency.admin')
);
DROP POLICY IF EXISTS "Allow update for admin only" ON finance.currency;
create policy "Allow update for admin only" on finance.currency
FOR UPDATE USING (
    identity.authorize('finance.currency.admin') AND is_active = true
) WITH CHECK (
    identity.authorize('finance.currency.admin') AND is_active = true
);
DROP POLICY IF EXISTS "Allow soft delete for admin only" ON finance.currency;
create policy "Allow soft delete for admin only" on finance.currency
FOR UPDATE USING (
    identity.authorize('finance.currency.admin') AND is_active = true
) WITH CHECK (
    identity.authorize('finance.currency.admin') AND is_active = false
);