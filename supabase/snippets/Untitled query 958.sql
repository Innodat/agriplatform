DROP POLICY IF EXISTS "Allow update for self or admin" ON finance.receipt;
create policy "Allow update for self or admin" on finance.receipt
FOR UPDATE
USING ( TRUE )
WITH CHECK (
  org_id = identity.current_org_id()
  AND is_active = true
  and (
    ( (auth.uid())::uuid = created_by AND identity.authorize('finance.receipt.update') )
    OR identity.authorize('finance.receipt.admin')
  )
);