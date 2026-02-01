DROP POLICY IF EXISTS "Allow soft delete for self or admin" ON finance.receipt;
create policy "Allow soft delete for self or admin" on finance.receipt
FOR UPDATE
USING ( TRUE )
WITH CHECK (
  org_id = identity.current_org_id()
  and (
    ( (auth.uid())::uuid = created_by AND is_active = false AND identity.authorize('finance.receipt.delete') )
    OR identity.authorize('finance.receipt.admin')
  )
);