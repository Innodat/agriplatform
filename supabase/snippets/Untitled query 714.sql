create or replace function finance.debug_receipt_rls(p_id int)
returns table (
  id int,
  org_id uuid,
  is_active boolean,
  created_by uuid,
  auth_uid uuid,
  org_claim uuid,
  role_claim text,
  my_org uuid,
  can_update boolean,
  can_delete boolean,
  is_admin boolean,
  using_general_update boolean,
  with_check_general_update_if_new boolean,
  using_soft_delete boolean,
  with_check_soft_delete_if_new_inactive boolean
)
language sql
stable
as $$
  select
    r.id,
    r.org_id,
    r.is_active,
    r.created_by,
    auth.uid() as auth_uid,
    nullif(auth.jwt() ->> 'org_id','')::uuid as org_claim,
    auth.jwt() ->> 'user_role' as role_claim,
    identity.current_org_id() as my_org,
    identity.authorize('finance.receipt.update')  as can_update,
    identity.authorize('finance.receipt.delete')  as can_delete,
    identity.authorize('finance.receipt.admin')   as is_admin,

    -- USING for "general update"
    (
      r.is_active = true
      and r.org_id = identity.current_org_id()
      and (
        ((auth.uid())::uuid = r.created_by and identity.authorize('finance.receipt.update'))
        or identity.authorize('finance.receipt.admin')
      )
    ) as using_general_update,

    -- WITH CHECK for "general update" (evaluated on NEW). Since we can't see NEW here,
    -- we approximate whether it would pass ignoring is_active (general update policy
    -- doesn't constrain is_active in your version).
    (
      r.org_id = identity.current_org_id()
      and (
        ((auth.uid())::uuid = r.created_by and identity.authorize('finance.receipt.update'))
        or identity.authorize('finance.receipt.admin')
      )
    ) as with_check_general_update_if_new,

    -- USING for "soft delete"
    (
      r.is_active = true
      and r.org_id = identity.current_org_id()
      and (
        ((auth.uid())::uuid = r.created_by and identity.authorize('finance.receipt.delete'))
        or identity.authorize('finance.receipt.admin')
      )
    ) as using_soft_delete,

    -- WITH CHECK for "soft delete" if NEW.is_active=false
    (
      r.org_id = identity.current_org_id()
      and (
        ((auth.uid())::uuid = r.created_by and true and identity.authorize('finance.receipt.delete'))
        or identity.authorize('finance.receipt.admin')
      )
    ) as with_check_soft_delete_if_new_inactive
  from finance.receipt r
  where r.id = p_id
$$;
