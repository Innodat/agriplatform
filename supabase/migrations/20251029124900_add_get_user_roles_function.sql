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
BEGIN
  -- Return roles for the currently authenticated user
  RETURN QUERY
  SELECT ur.role::text
  FROM identity.user_roles ur
  WHERE ur.user_id = auth.uid()
    AND ur.is_active = true;
END;
$$;

-- Grant execute permission to authenticated users
GRANT EXECUTE ON FUNCTION public.get_user_roles() TO authenticated;

COMMENT ON FUNCTION public.get_user_roles() IS 'Returns the active roles for the currently authenticated user';
