-- Finance Schema: RLS Policies with Read Views and Unified UPDATE Pattern
-- Pattern: deleted_at for soft deletes, *_read views for active records, unified UPDATE policies

-- ============================================================================
-- READ VIEWS (filter deleted_at IS NULL)
-- ============================================================================

-- Finance: receipt_read view
CREATE OR REPLACE VIEW finance.receipt_read
WITH (security_barrier, security_invoker = true)
AS
SELECT * FROM finance.receipt
WHERE deleted_at IS NULL;

-- Finance: purchase_read view
CREATE OR REPLACE VIEW finance.purchase_read
WITH (security_barrier, security_invoker = true)
AS
SELECT * FROM finance.purchase
WHERE deleted_at IS NULL;

-- Finance: expense_category_read view
CREATE OR REPLACE VIEW finance.expense_category_read
WITH (security_barrier, security_invoker = true)
AS
SELECT * FROM finance.expense_category
WHERE deleted_at IS NULL;

-- Finance: expense_type_read view
CREATE OR REPLACE VIEW finance.expense_type_read
WITH (security_barrier, security_invoker = true)
AS
SELECT * FROM finance.expense_type
WHERE deleted_at IS NULL;

-- Finance: currency_read view
CREATE OR REPLACE VIEW finance.currency_read
WITH (security_barrier, security_invoker = true)
AS
SELECT * FROM finance.currency
WHERE deleted_at IS NULL;

-- ============================================================================
-- GRANTS: SELECT on views only, INSERT/UPDATE on base tables
-- ============================================================================

-- Grant SELECT on read views to authenticated users
GRANT SELECT ON finance.receipt_read TO authenticated;
GRANT SELECT ON finance.purchase_read TO authenticated;
GRANT SELECT ON finance.expense_category_read TO authenticated;
GRANT SELECT ON finance.expense_type_read TO authenticated;
GRANT SELECT ON finance.currency_read TO authenticated;

-- Service role keeps full access to base tables (already granted in schema migration)

-- ============================================================================
-- RLS POLICIES: finance.purchase
-- ============================================================================

-- NOTE: purchases are org-scoped indirectly via finance.receipt.org_id

CREATE POLICY "Allow read for self or admin" ON finance.purchase 
FOR SELECT USING (
  EXISTS (
    SELECT 1
    FROM finance.receipt r
    WHERE r.id = finance.purchase.receipt_id
      AND r.org_id = identity.current_org_id()
  )
  AND (
    ( (auth.uid())::uuid = created_by AND identity.authorize('finance.purchase.read') )
    OR identity.authorize('finance.purchase.admin')
  )
);

CREATE POLICY "Allow insert for self or admin" ON finance.purchase 
FOR INSERT WITH CHECK (
  EXISTS (
    SELECT 1
    FROM finance.receipt r
    WHERE r.id = finance.purchase.receipt_id
      AND r.org_id = identity.current_org_id()
  )
  AND (
    ( (auth.uid())::uuid = created_by AND identity.authorize('finance.purchase.insert') )
    OR identity.authorize('finance.purchase.admin')
  )
);

CREATE POLICY "Allow update and soft delete (self or admin)" ON finance.purchase
FOR UPDATE
USING (
  -- Minimal target-set: only same-org rows are targetable
  EXISTS (
    SELECT 1
    FROM finance.receipt r
    WHERE r.id = finance.purchase.receipt_id
      AND r.org_id = identity.current_org_id()
  )
)
WITH CHECK (
  EXISTS (
    SELECT 1
    FROM finance.receipt r
    WHERE r.id = finance.purchase.receipt_id
      AND r.org_id = identity.current_org_id()
  )
  AND (
    -- Admin can do anything
    identity.authorize('finance.purchase.admin')
    -- OR creator: choose path based on the final deleted_at
    OR (
      (auth.uid())::uuid = created_by
      AND (
        -- General update path → final state must be active (deleted_at IS NULL)
        (deleted_at IS NULL AND identity.authorize('finance.purchase.update'))
        -- Soft-delete path → final state must be inactive (deleted_at IS NOT NULL)
        OR (deleted_at IS NOT NULL AND identity.authorize('finance.purchase.delete'))
      )
    )
  )
);

-- ============================================================================
-- RLS POLICIES: finance.receipt
-- ============================================================================

CREATE POLICY "Allow read for self or admin" ON finance.receipt 
FOR SELECT USING (
  org_id = identity.current_org_id()
  AND (
    ( (auth.uid())::uuid = created_by AND identity.authorize('finance.receipt.read') )
    OR identity.authorize('finance.receipt.admin')
  )
);

CREATE POLICY "Allow insert for self or admin" ON finance.receipt 
FOR INSERT WITH CHECK (
  org_id = identity.current_org_id()
  AND (
    ( (auth.uid())::uuid = created_by AND identity.authorize('finance.receipt.insert') )
    OR identity.authorize('finance.receipt.admin')
  )
);

CREATE POLICY "Allow update and soft delete (self or admin)" ON finance.receipt
FOR UPDATE
USING (
  -- Minimal target-set: only same-org rows are targetable
  org_id = identity.current_org_id()
)
WITH CHECK (
  org_id = identity.current_org_id()
  AND (
    -- Admin can do anything
    identity.authorize('finance.receipt.admin')
    -- OR creator: choose path based on the final deleted_at
    OR (
      (auth.uid())::uuid = created_by
      AND (
        -- General update path → final state must be active (deleted_at IS NULL)
        (deleted_at IS NULL AND identity.authorize('finance.receipt.update'))
        -- Soft-delete path → final state must be inactive (deleted_at IS NOT NULL)
        OR (deleted_at IS NOT NULL AND identity.authorize('finance.receipt.delete'))
      )
    )
  )
);

-- ============================================================================
-- RLS POLICIES: finance.expense_category (org-scoped reference data)
-- ============================================================================

CREATE POLICY "Allow read for self or admin" ON finance.expense_category 
FOR SELECT USING (
  org_id = identity.current_org_id()
  AND (
    ( auth.role() = 'authenticated' AND identity.authorize('finance.expense_category.read') )
    OR identity.authorize('finance.expense_category.admin')
  )
);

CREATE POLICY "Allow insert for admin only" ON finance.expense_category 
FOR INSERT WITH CHECK (
  org_id = identity.current_org_id()
  AND identity.authorize('finance.expense_category.admin')
);

CREATE POLICY "Allow update and soft delete (admin only)" ON finance.expense_category
FOR UPDATE
USING (
  -- Minimal target-set: only same-org rows are targetable
  org_id = identity.current_org_id()
)
WITH CHECK (
  org_id = identity.current_org_id()
  AND identity.authorize('finance.expense_category.admin')
);

-- ============================================================================
-- RLS POLICIES: finance.expense_type (org-scoped reference data)
-- ============================================================================

CREATE POLICY "Allow read for self or admin" ON finance.expense_type 
FOR SELECT USING (
  org_id = identity.current_org_id()
  AND (
    ( auth.role() = 'authenticated' AND identity.authorize('finance.expense_type.read') )
    OR identity.authorize('finance.expense_type.admin')
  )
);

CREATE POLICY "Allow insert for admin only" ON finance.expense_type 
FOR INSERT WITH CHECK (
  org_id = identity.current_org_id()
  AND identity.authorize('finance.expense_type.admin')
);

CREATE POLICY "Allow update and soft delete (admin only)" ON finance.expense_type
FOR UPDATE
USING (
  -- Minimal target-set: only same-org rows are targetable
  org_id = identity.current_org_id()
)
WITH CHECK (
  org_id = identity.current_org_id()
  AND identity.authorize('finance.expense_type.admin')
);

-- ============================================================================
-- RLS POLICIES: finance.currency (org-scoped reference data)
-- ============================================================================

CREATE POLICY "Allow read for self or admin" ON finance.currency 
FOR SELECT USING (
  org_id = identity.current_org_id()
  AND (
    ( auth.role() = 'authenticated' AND identity.authorize('finance.currency.read') )
    OR identity.authorize('finance.currency.admin')
  )
);

CREATE POLICY "Allow insert for admin only" ON finance.currency 
FOR INSERT WITH CHECK (
  org_id = identity.current_org_id()
  AND identity.authorize('finance.currency.admin')
);

CREATE POLICY "Allow update and soft delete (admin only)" ON finance.currency
FOR UPDATE
USING (
  -- Minimal target-set: only same-org rows are targetable
  org_id = identity.current_org_id()
)
WITH CHECK (
  org_id = identity.current_org_id()
  AND identity.authorize('finance.currency.admin')
);
