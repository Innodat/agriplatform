/**
 * FIX: Update auth hook to properly populate user_role claim in JWT
 * 
 * Issue: The previous auth hook was not properly setting user_role claim,
 * causing 403 errors when accessing finance schema tables due to RLS policies
 * expecting to claim.
 * 
 * Changes:
 * - Ensure claims object exists with coalesce
 * - Query only active roles (deleted_at IS NULL)
 * - Populate user_role with first active role
 * - Add role_ids array for future use
 * - Add department_ids placeholder for future department mapping
 */

-- Drop and recreate the auth hook function with proper claim population
-- NOTE: Multi-tenancy migration (20251222163200_multitenancy_orgs.sql) replaces this hook.
-- Keeping this file for historical consistency, but it should be a no-op.
-- If you need to re-apply a hook fix, do it in the multi-tenancy migration instead.

-- (intentionally left blank)
