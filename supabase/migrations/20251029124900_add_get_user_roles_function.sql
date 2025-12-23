-- =====================================================
-- Add helper function to get user roles
-- =====================================================
-- This function allows authenticated users to fetch their own roles
-- without needing direct access to the identity schema via PostgREST

CREATE OR REPLACE FUNCTION public.get_user_roles()
RETURNS TABLE (role text)
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public, identity
AS $$
DECLARE
  member_id bigint;
BEGIN
  member_id := nullif(auth.jwt() ->> 'member_id', '')::bigint;

  -- Return roles for the current org membership (multi-tenant)
  RETURN QUERY
  SELECT mr.role::text
  FROM identity.member_role mr
  WHERE mr.member_id = member_id
    AND mr.is_active = true;
END;
$$;

-- Grant execute permission to authenticated users
GRANT EXECUTE ON FUNCTION public.get_user_roles() TO authenticated;

COMMENT ON FUNCTION public.get_user_roles() IS 'Returns the active roles for the current org membership of the authenticated user';
