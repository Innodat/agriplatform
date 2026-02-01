DROP POLICY IF EXISTS "Allow read for self or admin" ON finance.receipt;
create policy "Allow read for self or admin" on finance.receipt for select using (
  org_id = identity.current_org_id()
  and (
    ( (auth.uid())::uuid = created_by and identity.authorize('finance.receipt.read') )
    or identity.authorize('finance.receipt.admin')
  )
);