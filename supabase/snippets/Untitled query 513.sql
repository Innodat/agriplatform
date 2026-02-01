-- Remove both existing UPDATE policies first
DROP POLICY IF EXISTS "Allow soft delete for self or admin" ON finance.receipt;
DROP POLICY IF EXISTS "Allow update for self or admin" ON finance.receipt;

-- Single, unified UPDATE policy
create policy "Allow update and soft delete (self or admin)" on finance.receipt
for update
using (
  -- Minimal target-set: only same-org rows are targetable
  org_id = identity.current_org_id()
)
with check (
  org_id = identity.current_org_id()
  and (
    -- Admin can do anything
    identity.authorize('finance.receipt.admin')

    -- OR creator: choose path based on the final is_active
    or (
      (auth.uid())::uuid = created_by
      and (
        -- General update path → final state must be active
        (is_active = true  and identity.authorize('finance.receipt.update'))
        -- Soft-delete path → final state must be inactive
        or (is_active = false and identity.authorize('finance.receipt.delete'))
      )
    )
  )
);